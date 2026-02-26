import pytest


@pytest.mark.asyncio
async def test_ragstore_retrieve_excludes_group(monkeypatch):
    from contextharbor.stores import ragstore

    # Fake embed + candidate loading to keep the test isolated.
    async def fake_embed_texts(texts, model=None):
        # Deterministic small vector
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
                "filename": "epub:Novel",
                "weight": 1.0,
                "group_name": "epub",
                "source": "epub",
            }),
            _Row({
                "id": 2,
                "doc_id": 11,
                "chunk_index": 0,
                "text": "b",
                "emb": ragstore._pack([1.0, 0.0]),
                "norm": 1.0,
                "filename": "upload.txt",
                "weight": 1.0,
                "group_name": None,
                "source": None,
            }),
        ]

    monkeypatch.setattr(ragstore, "_load_candidates", fake_load_candidates)
    monkeypatch.setattr(ragstore, "_prefilter_chunk_ids", lambda con, query, doc_ids, limit: [1, 2])

    # Ensure we don't hit sqlite in the safety check.
    monkeypatch.setattr(ragstore, "USE_PREFILTER", True)

    hits = await ragstore.retrieve(
        "q",
        top_k=10,
        doc_ids=[10, 11],
        exclude_group_names=["epub"],
    )
    assert [h["chunk_id"] for h in hits] == [2]
