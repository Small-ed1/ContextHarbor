from contextharbor.services.context import build_context
from contextharbor.services.retrieval import RetrievalResult


def test_build_context_preserves_order_when_requested():
    r1 = RetrievalResult(
        source_type="web",
        ref_id="web:1",
        chunk_id=1,
        title="t1",
        url="u1",
        domain="d1",
        score=0.1,
        text="a",
        meta={},
    )
    r2 = RetrievalResult(
        source_type="web",
        ref_id="web:2",
        chunk_id=2,
        title="t2",
        url="u2",
        domain="d2",
        score=999.0,
        text="b",
        meta={},
    )

    sources, lines = build_context([r1, r2], preserve_order=True, max_chars=10_000)
    assert sources[0]["ref_id"] == "web:1"
    assert sources[1]["ref_id"] == "web:2"


def test_build_context_still_floats_pinned_first():
    r1 = RetrievalResult(
        source_type="doc",
        ref_id="doc:1",
        chunk_id=1,
        title="t1",
        url=None,
        domain=None,
        score=0.1,
        text="a",
        meta={},
    )
    r2 = RetrievalResult(
        source_type="doc",
        ref_id="doc:2",
        chunk_id=2,
        title="t2",
        url=None,
        domain=None,
        score=0.2,
        text="b",
        meta={},
    )

    sources, _ = build_context([r1, r2], preserve_order=True, pinned_ref_ids={"doc:2"}, max_chars=10_000)
    assert sources[0]["ref_id"] == "doc:2"
