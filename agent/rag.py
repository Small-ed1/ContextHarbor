from __future__ import annotations

import json
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable, Optional

WORD = re.compile(r"[a-z0-9]+")


@dataclass
class Chunk:
    source: str
    ref: str
    chunk_id: str
    text: str


def _tokens(s: str) -> set[str]:
    return set(WORD.findall((s or "").lower()))


def _load_json(p: Path) -> list[dict]:
    if not p.exists():
        return []
    try:
        return json.loads(p.read_text(errors="ignore"))
    except Exception:
        return []


def build_index(manifest, max_chars: int = 1200) -> list[Chunk]:
    chunks: list[Chunk] = []

    def chunk_file(kind: str, fp: Path):
        t = fp.read_text(errors="ignore").strip()
        if not t:
            return
        for i in range(0, len(t), max_chars):
            c = t[i : i + max_chars]
            chunks.append(
                Chunk(
                    source=kind,
                    ref=fp.name,
                    chunk_id=f"{fp.stem}:{i//max_chars}",
                    text=c,
                )
            )

    bible_dir = (
        manifest.bible_dir
        if hasattr(manifest, "bible_dir")
        else Path("projects/default/bible")
    )
    drafts_dir = (
        manifest.drafts_dir
        if hasattr(manifest, "drafts_dir")
        else Path("projects/default/drafts")
    )
    research_dir = (
        manifest.research_dir
        if hasattr(manifest, "research_dir")
        else Path("projects/default/research")
    )

    for fp in sorted(bible_dir.glob("*.md")):
        chunk_file("bible", fp)
    for fp in sorted(drafts_dir.glob("*.md")):
        chunk_file("draft", fp)

    ex_path = research_dir / "extracts.json"
    for row in _load_json(ex_path):
        url = row.get("url") or "unknown"
        cid = row.get("chunk_id") or "chunk"
        txt = row.get("text") or ""
        if txt.strip():
            chunks.append(Chunk(source="extract", ref=url, chunk_id=cid, text=txt))

    return chunks


def save_index(manifest, chunks: list[Chunk]) -> Path:
    out_dir = (
        manifest.root / "rag"
        if hasattr(manifest, "root")
        else Path("projects/default/rag")
    )
    out_dir.mkdir(parents=True, exist_ok=True)
    p = out_dir / "index.json"
    p.write_text(json.dumps([c.__dict__ for c in chunks], indent=2, ensure_ascii=False))
    return p


def load_index(manifest) -> list[Chunk]:
    rag_dir = (
        manifest.root / "rag"
        if hasattr(manifest, "root")
        else Path("projects/default/rag")
    )
    p = rag_dir / "index.json"
    if not p.exists():
        return []
    data = json.loads(p.read_text(errors="ignore"))
    return [Chunk(**d) for d in data]


def search(manifest, query: str, k: int = 6) -> list[Chunk]:
    chunks = load_index(manifest)
    if not chunks:
        return []
    q = _tokens(query)
    scored: list[tuple[int, Chunk]] = []
    for c in chunks:
        t = _tokens(c.text)
        score = len(q & t)
        if score:
            scored.append((score, c))
    scored.sort(key=lambda x: x[0], reverse=True)
    return [c for _, c in scored[:k]]
