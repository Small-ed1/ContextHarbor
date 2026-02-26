from __future__ import annotations
import os, re, time, json, sqlite3, hashlib
from contextlib import contextmanager
from typing import Any, Optional
from urllib.parse import urlparse
import ipaddress
import socket

import httpx
from bs4 import BeautifulSoup

try:
    from readability import Document
except Exception:
    Document = None

from . import ragstore
from .. import config

WEB_DB = os.path.abspath(os.getenv("WEB_DB", config.config.web_db))
OLLAMA_URL = os.getenv("OLLAMA_URL", "http://127.0.0.1:11434").rstrip("/")
DEFAULT_EMBED_MODEL = os.getenv("EMBED_MODEL", "nomic-embed-latest")

WEB_USE_PREFILTER = os.getenv("WEB_USE_PREFILTER", "1") == "1"
WEB_PREFILTER_LIMIT = int(os.getenv("WEB_PREFILTER_LIMIT", "1500"))

USER_AGENT = os.getenv(
    "WEB_UA",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome Safari"
)

def _is_private_ip(hostname: str) -> bool:
    try:
        ip = ipaddress.ip_address(hostname)
        return ip.is_private or ip.is_loopback or ip.is_link_local or ip.is_reserved
    except ValueError:
        pass
    
    ips_found = set()
    try:
        addr_info = socket.getaddrinfo(hostname, None, family=socket.AF_INET)
        for info in addr_info[:3]:
            ip = ipaddress.ip_address(info[4][0])
            if ip.is_private or ip.is_loopback or ip.is_link_local or ip.is_reserved:
                return True
            ips_found.add(str(ip))
    except (socket.gaierror, OSError, ValueError):
        pass
    
    if len(ips_found) > 1:
        return True
    
    return False

def _is_blocked_url(url: str) -> bool:
    parsed = urlparse(url)
    scheme = parsed.scheme.lower()
    hostname = parsed.hostname or ""

    if scheme not in ("http", "https"):
        return True

    if _is_private_ip(hostname):
        return True

    blocked_hosts = os.getenv("WEB_BLOCKED_HOSTS", "").split(",")
    blocked_hosts = [h.strip().lower() for h in blocked_hosts if h.strip()]
    if hostname.lower() in blocked_hosts:
        return True

    allowed_hosts = os.getenv("WEB_ALLOWED_HOSTS", "").split(",")
    allowed_hosts = [h.strip().lower() for h in allowed_hosts if h.strip()]
    if allowed_hosts and hostname.lower() not in allowed_hosts:
        return True

    return False

def _now() -> int:
    return int(time.time())

@contextmanager
def _conn():
    con = sqlite3.connect(WEB_DB, timeout=15, check_same_thread=False)
    con.row_factory = sqlite3.Row
    con.execute("PRAGMA journal_mode=WAL;")
    con.execute("PRAGMA synchronous=NORMAL;")
    con.execute("PRAGMA foreign_keys=ON;")
    con.execute("PRAGMA busy_timeout=8000;")
    con.execute("PRAGMA temp_store=MEMORY;")
    con.execute("PRAGMA cache_size=-20000;")
    try:
        yield con
        con.commit()
    finally:
        con.close()

def init_db():
    with _conn() as con:
        con.execute("""
        CREATE TABLE IF NOT EXISTS web_pages (
          id INTEGER PRIMARY KEY AUTOINCREMENT,
          url TEXT NOT NULL UNIQUE,
          domain TEXT,
          title TEXT,
          fetched_at INTEGER NOT NULL,
          published_at INTEGER,
          content_hash TEXT,
          text TEXT NOT NULL,
          embed_model TEXT,
          embed_dim INTEGER
        );
        """)
        con.execute("CREATE INDEX IF NOT EXISTS idx_web_pages_domain ON web_pages(domain);")
        con.execute("CREATE INDEX IF NOT EXISTS idx_web_pages_fetched ON web_pages(fetched_at);")

        con.execute("""
        CREATE TABLE IF NOT EXISTS web_chunks (
          id INTEGER PRIMARY KEY AUTOINCREMENT,
          page_id INTEGER NOT NULL,
          chunk_index INTEGER NOT NULL,
          text TEXT NOT NULL,
          embedding BLOB NOT NULL,
          FOREIGN KEY(page_id) REFERENCES web_pages(id) ON DELETE CASCADE
        );
        """)
        con.execute("CREATE INDEX IF NOT EXISTS idx_web_chunks_page ON web_chunks(page_id, chunk_index);")

        # FTS prefilter to avoid full-scans during retrieval.
        con.execute(
            """
        CREATE VIRTUAL TABLE IF NOT EXISTS web_chunks_fts
        USING fts5(
          chunk_id UNINDEXED,
          page_id UNINDEXED,
          text,
          tokenize='unicode61'
        );
        """
        )
        con.execute("DROP TRIGGER IF EXISTS web_chunks_ai;")
        con.execute("DROP TRIGGER IF EXISTS web_chunks_ad;")
        con.execute("DROP TRIGGER IF EXISTS web_chunks_au;")

        con.execute(
            """
        CREATE TRIGGER IF NOT EXISTS web_chunks_ai
        AFTER INSERT ON web_chunks
        BEGIN
          INSERT INTO web_chunks_fts(rowid, chunk_id, page_id, text)
          VALUES (new.id, new.id, new.page_id, new.text);
        END;
        """
        )
        con.execute(
            """
        CREATE TRIGGER IF NOT EXISTS web_chunks_ad
        AFTER DELETE ON web_chunks
        BEGIN
          DELETE FROM web_chunks_fts WHERE rowid = old.id;
        END;
        """
        )
        con.execute(
            """
        CREATE TRIGGER IF NOT EXISTS web_chunks_au
        AFTER UPDATE OF text, page_id ON web_chunks
        BEGIN
          UPDATE web_chunks_fts
             SET chunk_id=new.id,
                 page_id=new.page_id,
                 text=new.text
           WHERE rowid=new.id;
        END;
        """
        )

        con.execute(
            """
        INSERT INTO web_chunks_fts(rowid, chunk_id, page_id, text)
        SELECT wc.id, wc.id, wc.page_id, wc.text
          FROM web_chunks wc
         WHERE wc.id NOT IN (SELECT rowid FROM web_chunks_fts);
        """
        )

        cols = {r["name"] for r in con.execute("PRAGMA table_info(web_pages);").fetchall()}
        if "embed_model" not in cols:
            con.execute("ALTER TABLE web_pages ADD COLUMN embed_model TEXT;")
        if "embed_dim" not in cols:
            con.execute("ALTER TABLE web_pages ADD COLUMN embed_dim INTEGER;")

def _domain(url: str) -> str:
    try:
        return (urlparse(url).netloc or "").lower()
    except Exception:
        return ""

def _hash(s: str) -> str:
    return hashlib.sha256((s or "").encode("utf-8", errors="ignore")).hexdigest()

def _clean_text(text: str) -> str:
    t = re.sub(r"\s+", " ", (text or "").strip())
    return t

def _extract_readable(html: str, url: str) -> tuple[str, str]:
    html = html or ""
    if Document is not None:
        try:
            doc = Document(html)
            title = (doc.short_title() or "").strip()
            content_html = doc.summary(html_partial=True) or ""
            soup = BeautifulSoup(content_html, "lxml")
            text = soup.get_text("\n")
            text = "\n".join([ln.strip() for ln in text.splitlines() if ln.strip()])
            return title[:300], text
        except Exception:
            pass

    soup = BeautifulSoup(html, "lxml")
    for tag in soup(["script", "style", "noscript", "svg", "header", "footer", "nav", "aside"]):
        try:
            tag.decompose()
        except Exception:
            pass
    title = ""
    if soup.title and soup.title.string:
        title = soup.title.string.strip()
    text = soup.get_text("\n")
    text = "\n".join([ln.strip() for ln in text.splitlines() if ln.strip()])
    return title[:300], text

def _chunk_text(text: str, target_chars: int = 900, overlap: int = 120) -> list[str]:
    paras = [p.strip() for p in (text or "").split("\n") if p.strip()]
    chunks: list[str] = []
    cur: list[str] = []
    cur_len = 0

    def flush():
        nonlocal cur, cur_len
        if cur:
            chunks.append("\n".join(cur).strip())
        cur, cur_len = [], 0

    for p in paras:
        if cur_len + len(p) + 1 > target_chars and cur_len > 200:
            flush()
        cur.append(p)
        cur_len += len(p) + 1

    flush()

    if overlap > 0 and len(chunks) > 1:
        out = [chunks[0]]
        for i in range(1, len(chunks)):
            prev = out[-1]
            tail = prev[-overlap:] if len(prev) > overlap else prev
            out.append((tail + "\n" + chunks[i]).strip())
        return out
    return chunks


_word = re.compile(r"[A-Za-z0-9_]{2,}")


def _fts_safe_query(q: str) -> str:
    toks = _word.findall((q or "").lower())
    return " OR ".join(toks[:24])


def _prefilter_chunk_ids(
    con: sqlite3.Connection,
    query: str,
    domain_whitelist: list[str],
    limit: int,
) -> list[int]:
    q = (query or "").strip()
    if not q:
        return []
    limit = max(1, min(int(limit), 5000))

    wl = [d.lower().strip() for d in (domain_whitelist or []) if d and d.strip()]
    params: list[Any] = []
    where: list[str] = []

    # MATCH must be in the WHERE clause.
    where.append("web_chunks_fts MATCH ?")
    params.append(q)

    if wl:
        qmarks = ",".join(["?"] * len(wl))
        where.append(f"wp.domain IN ({qmarks})")
        params.extend(wl)

    where_sql = "WHERE " + " AND ".join(where)

    sql = f"""
      SELECT wc.id AS chunk_id
        FROM web_chunks_fts
        JOIN web_chunks wc ON wc.id = web_chunks_fts.rowid
        JOIN web_pages wp ON wp.id = wc.page_id
       {where_sql}
       LIMIT ?;
    """

    try:
        rows = con.execute(sql, [*params, int(limit)]).fetchall()
        return [int(r[0]) for r in rows]
    except sqlite3.OperationalError:
        safe = _fts_safe_query(q)
        if not safe:
            return []
        params2 = list(params)
        params2[0] = safe
        rows = con.execute(sql, [*params2, int(limit)]).fetchall()
        return [int(r[0]) for r in rows]

async def _fetch_url(url: str, timeout: float = 12.0) -> tuple[int, str]:
    headers = {"User-Agent": USER_AGENT, "Accept": "text/html,application/xhtml+xml"}
    async with httpx.AsyncClient(timeout=timeout, follow_redirects=True, headers=headers) as client:
        r = await client.get(url)
        return int(r.status_code), (r.text or "")

def _looks_like_html(text: str) -> bool:
    t = (text or "").lower()
    return "<html" in t or "<body" in t or "</p>" in t or "<div" in t

async def upsert_page_from_url(url: str, force: bool = False, max_chars: int = 600_000) -> dict[str, Any]:
    url = (url or "").strip()
    if not url:
        raise ValueError("url required")

    if _is_blocked_url(url):
        raise ValueError(f"URL blocked: {url}")

    dom = _domain(url)
    now = _now()

    with _conn() as con:
        row = con.execute("SELECT * FROM web_pages WHERE url=?", (url,)).fetchone()
        if row and not force:
            return dict(row)

    code, html = await _fetch_url(url)
    if code < 200 or code >= 300:
        raise ValueError(f"fetch failed: HTTP {code}")

    if not _looks_like_html(html):
        raise ValueError("not html")

    title, text = _extract_readable(html, url)
    text = text.strip()
    if not text:
        raise ValueError("no readable text")

    if len(text) > max_chars:
        text = text[:max_chars]

    embed_model = DEFAULT_EMBED_MODEL
    h = _hash(title + "\n" + text)

    chunks = _chunk_text(text)
    if not chunks:
        raise ValueError("chunking produced no chunks")

    try:
        embs = await ragstore.embed_texts(chunks, model=embed_model)
        embed_dim = len(embs[0]) if embs else 0
    except Exception:
        # Degraded mode: keep page text + FTS available even if embeddings are down.
        embs = [[] for _ in chunks]
        embed_dim = 0

    with _conn() as con:
        row = con.execute("SELECT id, content_hash FROM web_pages WHERE url=?", (url,)).fetchone()
        if row:
            if (row["content_hash"] or "") == h:
                con.execute("UPDATE web_pages SET fetched_at=? WHERE id=?", (now, row["id"]))
                out = con.execute("SELECT * FROM web_pages WHERE id=?", (row["id"],)).fetchone()
                return dict(out)

            con.execute("""
              UPDATE web_pages
                 SET title=?, domain=?, fetched_at=?, content_hash=?, text=?, embed_model=?, embed_dim=?
               WHERE id=?
            """, (title, dom, now, h, text, embed_model, embed_dim, row["id"]))
            page_id = int(row["id"])
            con.execute("DELETE FROM web_chunks WHERE page_id=?", (page_id,))
        else:
            cur = con.execute("""
              INSERT INTO web_pages(url,domain,title,fetched_at,published_at,content_hash,text,embed_model,embed_dim)
              VALUES(?,?,?,?,NULL,?,?,?,?)
            """, (url, dom, title, now, h, text, embed_model, embed_dim))
            lastrowid = cur.lastrowid
            if lastrowid is None:
                raise RuntimeError("failed to create web page row")
            page_id = int(lastrowid)
    with _conn() as con:
        for idx, (ch, emb) in enumerate(zip(chunks, embs), start=0):
            blob = ragstore.embedding_to_blob(emb)
            con.execute("""
              INSERT INTO web_chunks(page_id, chunk_index, text, embedding)
              VALUES(?,?,?,?)
            """, (page_id, idx, ch, blob))

        out = con.execute("SELECT * FROM web_pages WHERE id=?", (page_id,)).fetchone()
        return dict(out)

def list_pages(limit: int = 50, offset: int = 0, domain: Optional[str] = None) -> list[dict[str, Any]]:
    limit = max(1, min(int(limit), 200))
    offset = max(0, int(offset))
    dom = (domain or "").strip().lower()
    with _conn() as con:
        if dom:
            rows = con.execute("""
              SELECT id,url,domain,title,fetched_at,published_at,content_hash
                FROM web_pages
               WHERE domain=?
               ORDER BY fetched_at DESC, id DESC
               LIMIT ? OFFSET ?
            """, (dom, limit, offset)).fetchall()
        else:
            rows = con.execute("""
              SELECT id,url,domain,title,fetched_at,published_at,content_hash
                FROM web_pages
               ORDER BY fetched_at DESC, id DESC
               LIMIT ? OFFSET ?
            """, (limit, offset)).fetchall()
        return [dict(r) for r in rows]

def get_chunk(chunk_id: int) -> dict[str, Any]:
    with _conn() as con:
        row = con.execute("""
          SELECT wc.id AS chunk_id, wc.page_id, wc.chunk_index, wc.text,
                 wp.url, wp.domain, wp.title, wp.fetched_at
            FROM web_chunks wc
            JOIN web_pages wp ON wp.id = wc.page_id
           WHERE wc.id=?
        """, (int(chunk_id),)).fetchone()
        if not row:
            raise KeyError("chunk not found")
        return dict(row)

def get_neighbors(chunk_id: int, span: int = 1) -> dict[str, Any]:
    span = max(1, min(int(span), 8))
    with _conn() as con:
        row = con.execute("SELECT page_id, chunk_index FROM web_chunks WHERE id=?", (int(chunk_id),)).fetchone()
        if not row:
            raise KeyError("chunk not found")
        page_id = int(row["page_id"])
        idx = int(row["chunk_index"])

        lo = max(0, idx - span)
        hi = idx + span

        rows = con.execute("""
          SELECT id AS chunk_id, chunk_index, text
            FROM web_chunks
           WHERE page_id=? AND chunk_index BETWEEN ? AND ?
           ORDER BY chunk_index ASC
        """, (page_id, lo, hi)).fetchall()

        meta = con.execute("SELECT url,domain,title,fetched_at FROM web_pages WHERE id=?", (page_id,)).fetchone()
        return {
            "page_id": page_id,
            "url": meta["url"] if meta else None,
            "domain": meta["domain"] if meta else None,
            "title": meta["title"] if meta else None,
            "fetched_at": meta["fetched_at"] if meta else None,
            "anchor_chunk_id": int(chunk_id),
            "chunks": [dict(r) for r in rows],
        }

async def retrieve(query: str, top_k: int = 6, domain_whitelist: Optional[list[str]] = None, embed_model: Optional[str] = None) -> list[dict[str, Any]]:
    q = (query or "").strip()
    if not q:
        return []
    top_k = max(1, min(int(top_k), 30))
    wl = [d.lower().strip() for d in (domain_whitelist or []) if d and d.strip()]

    embed_model = embed_model or DEFAULT_EMBED_MODEL
    try:
        qemb = (await ragstore.embed_texts([q], model=embed_model))[0]
        qvec = ragstore.embedding_to_array(qemb)
    except Exception:
        # Embeddings unavailable: fall back to FTS ranking.
        with _conn() as con:
            wl2 = list(wl)
            params: list[Any] = [q]
            where: list[str] = ["web_chunks_fts MATCH ?"]
            if wl2:
                qmarks = ",".join(["?"] * len(wl2))
                where.append(f"wp.domain IN ({qmarks})")
                params.extend(wl2)
            where_sql = "WHERE " + " AND ".join(where)
            sql = f"""
              SELECT wc.id AS chunk_id, wc.page_id, wc.chunk_index, wc.text,
                     wp.url, wp.domain, wp.title,
                     bm25(web_chunks_fts) AS rank
                FROM web_chunks_fts
                JOIN web_chunks wc ON wc.id = web_chunks_fts.rowid
                JOIN web_pages wp ON wp.id = wc.page_id
               {where_sql}
               ORDER BY rank ASC
               LIMIT ?;
            """
            try:
                rows = con.execute(sql, [*params, int(top_k)]).fetchall()
            except sqlite3.OperationalError:
                safe = _fts_safe_query(q)
                if not safe:
                    return []
                params[0] = safe
                rows = con.execute(sql, [*params, int(top_k)]).fetchall()

        hits2: list[dict[str, Any]] = []
        for r in rows:
            rank = float(r[7] if "rank" in r.keys() else 0.0)
            # Smaller bm25 is better; convert to descending score.
            rr = max(0.0, rank)
            score = 1.0 / (1.0 + rr)
            hits2.append({
                "source_type": "web",
                "chunk_id": int(r[0]),
                "page_id": int(r[1]),
                "chunk_index": int(r[2]),
                "text": r[3],
                "url": r[4],
                "domain": r[5],
                "title": r[6],
                "score": float(score),
            })
        return hits2

    hits: list[dict[str, Any]] = []
    with _conn() as con:
        chunk_ids: list[int] | None = None
        if WEB_USE_PREFILTER:
            try:
                chunk_ids = _prefilter_chunk_ids(con, q, wl, WEB_PREFILTER_LIMIT)
            except Exception:
                chunk_ids = None

        if chunk_ids is not None:
            if not chunk_ids:
                return []
            qs = ",".join(["?"] * len(chunk_ids))
            rows = con.execute(
                f"""
              SELECT wc.id AS chunk_id, wc.page_id, wc.chunk_index, wc.text, wc.embedding,
                     wp.url, wp.domain, wp.title
                FROM web_chunks wc
                JOIN web_pages wp ON wp.id = wc.page_id
               WHERE wc.id IN ({qs})
                """,
                tuple(chunk_ids),
            ).fetchall()
        else:
            if wl:
                placeholders = ",".join("?" for _ in wl)
                rows = con.execute(
                    f"""
                  SELECT wc.id AS chunk_id, wc.page_id, wc.chunk_index, wc.text, wc.embedding,
                         wp.url, wp.domain, wp.title
                    FROM web_chunks wc
                    JOIN web_pages wp ON wp.id = wc.page_id
                   WHERE wp.domain IN ({placeholders})
                    """,
                    tuple(wl),
                ).fetchall()
            else:
                rows = con.execute(
                    """
                  SELECT wc.id AS chunk_id, wc.page_id, wc.chunk_index, wc.text, wc.embedding,
                         wp.url, wp.domain, wp.title
                    FROM web_chunks wc
                    JOIN web_pages wp ON wp.id = wc.page_id
                    """
                ).fetchall()

    for r in rows:
        emb = ragstore.embedding_blob_to_array(r["embedding"])
        score = ragstore.cosine(qvec, emb)
        hits.append({
            "source_type": "web",
            "chunk_id": int(r["chunk_id"]),
            "page_id": int(r["page_id"]),
            "chunk_index": int(r["chunk_index"]),
            "url": r["url"],
            "domain": r["domain"],
            "title": r["title"],
            "text": r["text"],
            "score": float(score),
        })

    hits.sort(key=lambda x: x["score"], reverse=True)
    return hits[:top_k]
