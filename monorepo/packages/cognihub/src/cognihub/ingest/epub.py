from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any, Optional

from bs4 import BeautifulSoup
from ebooklib import epub, ITEM_DOCUMENT  # type: ignore

from .. import config
from ..stores import ragstore


@dataclass(frozen=True)
class EpubInfo:
    path: str
    title: str
    authors: list[str]


def _default_library_dir() -> Path:
    return Path(config.config.ebooks_dir)


def _extract_text_from_html(html: str) -> str:
    soup = BeautifulSoup(html or "", "lxml")
    for tag in soup(["script", "style", "noscript", "svg", "header", "footer", "nav", "aside"]):
        try:
            tag.decompose()
        except Exception:
            pass
    text = soup.get_text("\n")
    lines = [ln.strip() for ln in text.splitlines() if ln.strip()]
    return "\n".join(lines)


def _read_epub(epub_path: Path) -> tuple[EpubInfo, str]:
    book = epub.read_epub(str(epub_path))

    title = ""
    authors: list[str] = []

    try:
        meta_title = book.get_metadata("DC", "title")
        if meta_title and isinstance(meta_title, list) and meta_title[0]:
            title = str(meta_title[0][0] or "").strip()
    except Exception:
        pass

    try:
        meta_auth = book.get_metadata("DC", "creator")
        if meta_auth and isinstance(meta_auth, list):
            for item in meta_auth:
                if not item:
                    continue
                a = str(item[0] or "").strip()
                if a:
                    authors.append(a)
    except Exception:
        pass

    parts: list[str] = []
    for item in book.get_items_of_type(ITEM_DOCUMENT):
        try:
            raw = item.get_content()
            html = raw.decode("utf-8", errors="ignore") if isinstance(raw, (bytes, bytearray)) else str(raw)
            txt = _extract_text_from_html(html)
            if txt:
                parts.append(txt)
        except Exception:
            continue

    text = "\n\n".join(parts).strip()

    rel = str(epub_path)
    try:
        rel = str(epub_path.relative_to(_default_library_dir()))
    except Exception:
        pass

    info = EpubInfo(
        path=rel,
        title=title or epub_path.stem,
        authors=authors,
    )
    return info, text


def list_epubs(*, query: Optional[str] = None, limit: int = 25, library_dir: Optional[str] = None) -> list[dict[str, Any]]:
    root = Path(library_dir) if library_dir else _default_library_dir()
    q = (query or "").strip().lower()
    limit = max(1, min(int(limit), 200))

    out: list[dict[str, Any]] = []
    if not root.exists() or not root.is_dir():
        return out

    for p in root.rglob("*.epub"):
        if len(out) >= limit:
            break
        try:
            rel = str(p.relative_to(root))
        except Exception:
            rel = str(p)

        if q and q not in rel.lower():
            continue

        out.append({"path": rel})
    return out


async def ingest_epub(
    *,
    path: str,
    embed_model: str | None = None,
    library_dir: Optional[str] = None,
) -> dict[str, Any]:
    root = Path(library_dir) if library_dir else _default_library_dir()
    p = Path(path)
    if not p.is_absolute():
        p = root / p
    p = p.expanduser().resolve()

    if not p.exists() or not p.is_file():
        return {"ok": False, "error": f"epub not found: {p}"}

    info, text = _read_epub(p)
    if not text:
        return {"ok": False, "error": "no extractable text"}

    filename = f"epub:{info.title}"
    if info.authors:
        filename = f"epub:{info.title} - {', '.join(info.authors)}"

    doc_id = await ragstore.add_document(filename, text, embed_model=embed_model)
    try:
        ragstore.update_document(doc_id, group_name="epub", filename=filename)
    except Exception:
        pass

    return {
        "ok": True,
        "doc_id": doc_id,
        "title": info.title,
        "authors": info.authors,
        "path": info.path,
    }


async def ingest_epubs_by_query(
    *,
    query: str,
    limit: int = 3,
    embed_model: str | None = None,
    library_dir: Optional[str] = None,
) -> dict[str, Any]:
    q = (query or "").strip()
    if not q:
        return {"ok": False, "error": "query cannot be empty"}

    matches = list_epubs(query=q, limit=limit, library_dir=library_dir)
    results: list[dict[str, Any]] = []
    for m in matches:
        r = await ingest_epub(path=str(m.get("path") or ""), embed_model=embed_model, library_dir=library_dir)
        results.append(r)
    return {"ok": True, "results": results, "count": len(results)}
