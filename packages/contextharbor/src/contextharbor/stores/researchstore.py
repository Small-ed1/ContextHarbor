from __future__ import annotations
import os, sqlite3, time, uuid, json
from pathlib import Path
import threading
from contextlib import contextmanager
from typing import Any, Optional

from .. import config

def _db_path() -> str:
    raw = (os.getenv("RESEARCH_DB") or str(config.config.research_db) or "").strip()
    if not raw:
        # Defensive fallback.
        raw = "~/.contextharbor/data/research.sqlite3"
    p = os.path.abspath(os.path.expanduser(raw))
    Path(os.path.dirname(p)).mkdir(parents=True, exist_ok=True)
    return p


_inited_path: str | None = None
_init_lock = threading.Lock()


def _connect(path: str) -> sqlite3.Connection:
    con = sqlite3.connect(path, timeout=15, check_same_thread=False)
    con.row_factory = sqlite3.Row
    con.execute("PRAGMA journal_mode=WAL;")
    con.execute("PRAGMA synchronous=NORMAL;")
    con.execute("PRAGMA foreign_keys=ON;")
    con.execute("PRAGMA busy_timeout=8000;")
    return con


def _ensure_init() -> None:
    global _inited_path
    p = _db_path()
    if _inited_path == p:
        return
    with _init_lock:
        p2 = _db_path()
        if _inited_path == p2:
            return

        con = _connect(p2)
        try:
            con.execute(
                """
            CREATE TABLE IF NOT EXISTS research_runs (
              id TEXT PRIMARY KEY,
              chat_id TEXT,
              query TEXT NOT NULL,
              mode TEXT NOT NULL,
              created_at INTEGER NOT NULL,
              status TEXT NOT NULL,
              settings_json TEXT,
              final_answer TEXT,
              error TEXT
            );
            """
            )
            con.execute("CREATE INDEX IF NOT EXISTS idx_runs_chat ON research_runs(chat_id, created_at);")
            con.execute("CREATE INDEX IF NOT EXISTS idx_runs_status ON research_runs(status, created_at);")

            con.execute(
                """
            CREATE TABLE IF NOT EXISTS research_trace (
              id INTEGER PRIMARY KEY AUTOINCREMENT,
              run_id TEXT NOT NULL,
              step TEXT NOT NULL,
              created_at INTEGER NOT NULL,
              payload_json TEXT,
              FOREIGN KEY(run_id) REFERENCES research_runs(id) ON DELETE CASCADE
            );
            """
            )
            con.execute("CREATE INDEX IF NOT EXISTS idx_trace_run ON research_trace(run_id, id);")

            con.execute(
                """
            CREATE TABLE IF NOT EXISTS research_sources (
              id INTEGER PRIMARY KEY AUTOINCREMENT,
              run_id TEXT NOT NULL,
              source_type TEXT NOT NULL,
              ref_id TEXT NOT NULL,
              title TEXT,
              url TEXT,
              domain TEXT,
              score REAL,
              snippet TEXT,
              pinned INTEGER NOT NULL DEFAULT 0,
              excluded INTEGER NOT NULL DEFAULT 0,
              meta_json TEXT,
              FOREIGN KEY(run_id) REFERENCES research_runs(id) ON DELETE CASCADE
            );
            """
            )
            con.execute("CREATE INDEX IF NOT EXISTS idx_sources_run ON research_sources(run_id, id);")
            con.execute("CREATE INDEX IF NOT EXISTS idx_sources_pin ON research_sources(run_id, pinned, excluded);")

            con.execute(
                """
            CREATE TABLE IF NOT EXISTS research_claims (
              id INTEGER PRIMARY KEY AUTOINCREMENT,
              run_id TEXT NOT NULL,
              claim TEXT NOT NULL,
              status TEXT NOT NULL,
              citations_json TEXT,
              notes TEXT,
              FOREIGN KEY(run_id) REFERENCES research_runs(id) ON DELETE CASCADE
            );
            """
            )
            con.execute("CREATE INDEX IF NOT EXISTS idx_claims_run ON research_claims(run_id, id);")

            con.commit()
        finally:
            con.close()

        _inited_path = p2

def _now() -> int:
    return int(time.time())

@contextmanager
def _conn():
    _ensure_init()
    con = _connect(_db_path())
    try:
        yield con
        con.commit()
    finally:
        con.close()

def init_db():
    _ensure_init()

def create_run(chat_id: Optional[str], query: str, mode: str, settings: dict[str, Any]) -> str:
    run_id = str(uuid.uuid4())
    with _conn() as con:
        con.execute("""
          INSERT INTO research_runs(id,chat_id,query,mode,created_at,status,settings_json)
          VALUES(?,?,?,?,?,'running',?)
        """, (run_id, chat_id, query, mode, _now(), json.dumps(settings, ensure_ascii=False)))
    return run_id

def set_run_done(run_id: str, final_answer: str):
    with _conn() as con:
        con.execute("UPDATE research_runs SET status='done', final_answer=? WHERE id=?", (final_answer, run_id))

def set_run_error(run_id: str, error: str):
    with _conn() as con:
        con.execute("UPDATE research_runs SET status='error', error=? WHERE id=?", (error, run_id))

def add_trace(run_id: str, step: str, payload: Any = None):
    with _conn() as con:
        con.execute("""
          INSERT INTO research_trace(run_id,step,created_at,payload_json)
          VALUES(?,?,?,?)
        """, (run_id, step, _now(), None if payload is None else json.dumps(payload, ensure_ascii=False)))

def add_sources(run_id: str, sources: list[dict[str, Any]]):
    with _conn() as con:
        for s in sources:
            pinned = 1 if bool(s.get("pinned")) else 0
            excluded = 1 if bool(s.get("excluded")) else 0
            con.execute("""
              INSERT INTO research_sources(run_id,source_type,ref_id,title,url,domain,score,snippet,pinned,excluded,meta_json)
              VALUES(?,?,?,?,?,?,?,?,?,?,?)
            """, (
                run_id,
                s.get("source_type") or "",
                str(s.get("ref_id") or ""),
                s.get("title"),
                s.get("url"),
                s.get("domain"),
                float(s.get("score") or 0.0),
                (s.get("snippet") or "")[:600],
                pinned,
                excluded,
                json.dumps(s.get("meta") or {}, ensure_ascii=False),
            ))


def get_source_flags_by_ref_id(run_id: str) -> dict[str, dict[str, bool]]:
    with _conn() as con:
        rows = con.execute(
            "SELECT ref_id, pinned, excluded FROM research_sources WHERE run_id=?",
            (run_id,),
        ).fetchall()
        out: dict[str, dict[str, bool]] = {}
        for r in rows:
            ref = str(r[0] or "").strip()
            if not ref:
                continue
            out[ref] = {
                "pinned": bool(int(r[1] or 0)),
                "excluded": bool(int(r[2] or 0)),
            }
        return out

def set_source_flag(run_id: str, source_id: int, pinned: Optional[bool] = None, excluded: Optional[bool] = None):
    sets = []
    params: list[Any] = []
    if pinned is not None:
        sets.append("pinned=?"); params.append(1 if pinned else 0)
    if excluded is not None:
        sets.append("excluded=?"); params.append(1 if excluded else 0)
    if not sets:
        return
    params.extend([run_id, int(source_id)])
    sql = "UPDATE research_sources SET " + ", ".join(sets) + " WHERE run_id=? AND id=?"
    with _conn() as con:
        con.execute(sql, params)

def clear_sources(run_id: str):
    with _conn() as con:
        con.execute("DELETE FROM research_sources WHERE run_id=?", (run_id,))


def upsert_sources(run_id: str, sources: list[dict[str, Any]]):
    """Upsert sources by stable ref_id, preserving pinned/excluded flags."""

    cleaned = [s for s in (sources or []) if isinstance(s, dict) and str(s.get("ref_id") or "").strip()]
    new_ref_ids = {str(s.get("ref_id") or "").strip() for s in cleaned}

    with _conn() as con:
        existing_rows = con.execute(
            "SELECT id, ref_id, pinned, excluded FROM research_sources WHERE run_id=?",
            (run_id,),
        ).fetchall()
        existing: dict[str, dict[str, Any]] = {}
        for r in existing_rows:
            ref = str(r[1] or "").strip()
            if not ref:
                continue
            existing[ref] = {
                "id": int(r[0]),
                "pinned": bool(int(r[2] or 0)),
                "excluded": bool(int(r[3] or 0)),
            }

        # Remove stale sources.
        if existing and new_ref_ids:
            stale = [ref for ref in existing.keys() if ref not in new_ref_ids]
            if stale:
                qmarks = ",".join(["?"] * len(stale))
                con.execute(
                    f"DELETE FROM research_sources WHERE run_id=? AND ref_id IN ({qmarks})",
                    [run_id, *stale],
                )
        elif existing and not new_ref_ids:
            con.execute("DELETE FROM research_sources WHERE run_id=?", (run_id,))

        for s in cleaned:
            ref_id = str(s.get("ref_id") or "").strip()
            if not ref_id:
                continue

            # Preserve pinned/excluded unless explicitly provided.
            prev = existing.get(ref_id) or {}
            pinned = bool(s.get("pinned")) if "pinned" in s else bool(prev.get("pinned"))
            excluded = bool(s.get("excluded")) if "excluded" in s else bool(prev.get("excluded"))

            title = s.get("title")
            url = s.get("url")
            domain = s.get("domain")
            score = float(s.get("score") or 0.0)
            snippet = (s.get("snippet") or "")[:600]
            meta_json = json.dumps(s.get("meta") or {}, ensure_ascii=False)
            source_type = s.get("source_type") or ""

            if prev.get("id"):
                con.execute(
                    """
                    UPDATE research_sources
                       SET source_type=?, title=?, url=?, domain=?, score=?, snippet=?,
                           pinned=?, excluded=?, meta_json=?
                     WHERE run_id=? AND id=?
                    """,
                    (
                        source_type,
                        title,
                        url,
                        domain,
                        score,
                        snippet,
                        1 if pinned else 0,
                        1 if excluded else 0,
                        meta_json,
                        run_id,
                        int(prev["id"]),
                    ),
                )
            else:
                con.execute(
                    """
                    INSERT INTO research_sources(run_id,source_type,ref_id,title,url,domain,score,snippet,pinned,excluded,meta_json)
                    VALUES(?,?,?,?,?,?,?,?,?,?,?)
                    """,
                    (
                        run_id,
                        source_type,
                        ref_id,
                        title,
                        url,
                        domain,
                        score,
                        snippet,
                        1 if pinned else 0,
                        1 if excluded else 0,
                        meta_json,
                    ),
                )

def clear_claims(run_id: str):
    with _conn() as con:
        con.execute("DELETE FROM research_claims WHERE run_id=?", (run_id,))

def add_claims(run_id: str, claims: list[dict[str, Any]]):
    with _conn() as con:
        for c in claims:
            con.execute("""
              INSERT INTO research_claims(run_id,claim,status,citations_json,notes)
              VALUES(?,?,?,?,?)
            """, (
                run_id,
                (c.get("claim") or "")[:1800],
                c.get("status") or "unclear",
                json.dumps(c.get("citations") or [], ensure_ascii=False),
                (c.get("notes") or "")[:2000],
            ))

def get_run(run_id: str) -> dict[str, Any]:
    with _conn() as con:
        row = con.execute("SELECT * FROM research_runs WHERE id=?", (run_id,)).fetchone()
        if not row:
            raise KeyError("run not found")
        out = dict(row)
        try:
            out["settings"] = json.loads(out.get("settings_json") or "{}")
        except Exception:
            out["settings"] = {}
        return out

def list_runs(chat_id: Optional[str] = None, limit: int = 50, offset: int = 0) -> list[dict[str, Any]]:
    limit = max(1, min(int(limit), 200))
    offset = max(0, int(offset))
    with _conn() as con:
        if chat_id:
            rows = con.execute("""
              SELECT id,chat_id,query,mode,created_at,status
                FROM research_runs
               WHERE chat_id=?
               ORDER BY created_at DESC
               LIMIT ? OFFSET ?
            """, (chat_id, limit, offset)).fetchall()
        else:
            rows = con.execute("""
              SELECT id,chat_id,query,mode,created_at,status
                FROM research_runs
               ORDER BY created_at DESC
               LIMIT ? OFFSET ?
            """, (limit, offset)).fetchall()
        return [dict(r) for r in rows]

def get_trace(run_id: str, limit: int = 200, offset: int = 0) -> list[dict[str, Any]]:
    limit = max(1, min(int(limit), 500))
    offset = max(0, int(offset))
    with _conn() as con:
        rows = con.execute("""
          SELECT id,step,created_at,payload_json
            FROM research_trace
           WHERE run_id=?
           ORDER BY id ASC
           LIMIT ? OFFSET ?
        """, (run_id, limit, offset)).fetchall()
        out = []
        for r in rows:
            d = dict(r)
            try:
                d["payload"] = json.loads(d["payload_json"] or "null")
            except Exception:
                d["payload"] = None
            out.append(d)
        return out

def get_sources(run_id: str) -> list[dict[str, Any]]:
    with _conn() as con:
        rows = con.execute("""
          SELECT id,source_type,ref_id,title,url,domain,score,snippet,pinned,excluded,meta_json
            FROM research_sources
           WHERE run_id=?
           ORDER BY pinned DESC, excluded ASC, score DESC, id ASC
        """, (run_id,)).fetchall()
        out = []
        for r in rows:
            d = dict(r)
            try:
                d["meta"] = json.loads(d.get("meta_json") or "{}")
            except Exception:
                d["meta"] = {}
            out.append(d)
        return out

def get_claims(run_id: str) -> list[dict[str, Any]]:
    with _conn() as con:
        rows = con.execute("""
          SELECT id,claim,status,citations_json,notes
            FROM research_claims
           WHERE run_id=?
           ORDER BY id ASC
        """, (run_id,)).fetchall()
        out = []
        for r in rows:
            d = dict(r)
            try:
                d["citations"] = json.loads(d.get("citations_json") or "[]")
            except Exception:
                d["citations"] = []
            out.append(d)
        return out
