from __future__ import annotations

import sqlite3

import pytest


@pytest.mark.asyncio
async def test_kiwix_retrieval_falls_back_without_embeddings(monkeypatch: pytest.MonkeyPatch) -> None:
    from contextharbor.services import retrieval

    async def fake_search(base_url: str, query: str, top_k: int = 5):
        return [
            {
                "title": "Example",
                "path": "/content/wikipedia_en_all_maxi_2024-01/A/Biodiversity",
                "url": f"{base_url}/content/wikipedia_en_all_maxi_2024-01/A/Biodiversity",
                "snippet": "biodiversity ...",
            }
        ]

    async def fake_fetch_page(base_url: str, path: str):
        return {
            "url": f"{base_url}{path}",
            "path": path,
            "zim": "wikipedia_en_all_maxi_2024-01",
            "text": "Biodiversity increases when habitat is restored over time.",
        }

    async def boom_embed(*args, **kwargs):
        raise RuntimeError("embeddings down")

    monkeypatch.setattr(retrieval.kiwix, "search", fake_search)
    monkeypatch.setattr(retrieval.kiwix, "fetch_page", fake_fetch_page)
    monkeypatch.setattr(retrieval.ragstore, "embed_texts", boom_embed)

    provider = retrieval.KiwixRetrievalProvider("http://kiwix")
    hits = await provider.retrieve("biodiversity habitat restoration", top_k=3, embed_model="m", pages=1)

    assert hits
    assert hits[0].source_type == "kiwix"
    assert hits[0].meta.get("score_mode") == "keyword"


@pytest.mark.asyncio
async def test_webstore_retrieve_falls_back_to_fts(tmp_path, monkeypatch: pytest.MonkeyPatch) -> None:
    db = tmp_path / "web.sqlite3"
    monkeypatch.setenv("WEB_DB", str(db))

    # Import after env var so module-level WEB_DB picks it up.
    # (Reload defensively in case another test imported webstore already.)
    import importlib
    from contextharbor.stores import webstore as _webstore
    webstore = importlib.reload(_webstore)

    webstore.init_db()
    with sqlite3.connect(str(db)) as con:
        con.execute(
            "INSERT INTO web_pages(url,domain,title,fetched_at,published_at,content_hash,text,embed_model,embed_dim) VALUES(?,?,?,?,NULL,?,?,?,?)",
            (
                "https://example.com/a",
                "example.com",
                "A",
                1,
                "h",
                "Biodiversity increases with habitat restoration.",
                "n/a",
                0,
            ),
        )
        page_id = int(con.execute("SELECT id FROM web_pages WHERE url='https://example.com/a'").fetchone()[0])
        con.execute(
            "INSERT INTO web_chunks(page_id,chunk_index,text,embedding) VALUES(?,?,?,?)",
            (page_id, 0, "Biodiversity increases with habitat restoration.", b""),
        )
        con.commit()

    async def boom_embed(*args, **kwargs):
        raise RuntimeError("embeddings down")

    monkeypatch.setattr(webstore.ragstore, "embed_texts", boom_embed)

    hits = await webstore.retrieve("biodiversity restoration", top_k=3)
    assert hits
    assert hits[0].get("source_type") == "web"
    assert hits[0].get("url") == "https://example.com/a"
