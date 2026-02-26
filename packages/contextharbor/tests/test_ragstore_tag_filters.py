import pytest


@pytest.mark.asyncio
async def test_ragstore_retrieve_include_exclude_tags(monkeypatch):
    from contextharbor.stores import ragstore

    async def fake_embed_texts(texts, model=None):
        return [[1.0, 0.0] for _ in texts]

    monkeypatch.setattr(ragstore, "embed_texts", fake_embed_texts)

    class _Row(dict):
        def keys(self):
            return super().keys()

    def fake_load_candidates(con, doc_ids, chunk_ids):
        return [
            _Row({
                "id": 1,
                "doc_id": 10,
                "chunk_index": 0,
                "text": "a",
                "emb": ragstore._pack([1.0, 0.0]),
                "norm": 1.0,
                "filename": "doc1",
                "weight": 1.0,
                "group_name": "epub",
                "source": "epub",
                "tags_json": '["fiction","novel"]',
            }),
            _Row({
                "id": 2,
                "doc_id": 11,
                "chunk_index": 0,
                "text": "b",
                "emb": ragstore._pack([1.0, 0.0]),
                "norm": 1.0,
                "filename": "doc2",
                "weight": 1.0,
                "group_name": "epub",
                "source": "epub",
                "tags_json": '["textbook","physics"]',
            }),
        ]

    monkeypatch.setattr(ragstore, "_load_candidates", fake_load_candidates)
    monkeypatch.setattr(ragstore, "_prefilter_chunk_ids", lambda con, query, doc_ids, limit: [1, 2])
    monkeypatch.setattr(ragstore, "USE_PREFILTER", True)

    hits = await ragstore.retrieve(
        "q",
        top_k=10,
        doc_ids=[10, 11],
        include_tags=["physics"],
        exclude_tags=["fiction"],
    )
    assert [h["chunk_id"] for h in hits] == [2]
