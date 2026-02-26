from __future__ import annotations

from contextharbor.services.context import build_context
from contextharbor.services.retrieval import RetrievalResult


def test_build_context_truncates_first_oversize_source_instead_of_returning_empty() -> None:
    big = "x" * 5000
    r1 = RetrievalResult(
        source_type="kiwix",
        ref_id="kiwix:1",
        chunk_id=1,
        title="t",
        url="u",
        domain="d",
        score=1.0,
        text=big,
        meta={},
    )

    sources, lines = build_context([r1], max_chars=800, preserve_order=True)

    assert sources
    assert lines
    assert len(lines[0]) <= 800


def test_build_context_skips_oversize_middle_source_and_keeps_later_small_source() -> None:
    small1 = RetrievalResult(
        source_type="web",
        ref_id="web:1",
        chunk_id=1,
        title="t1",
        url="u1",
        domain="d1",
        score=1.0,
        text="a" * 200,
        meta={},
    )
    big = RetrievalResult(
        source_type="kiwix",
        ref_id="kiwix:2",
        chunk_id=2,
        title="t2",
        url="u2",
        domain="d2",
        score=0.9,
        text="b" * 5000,
        meta={},
    )
    small2 = RetrievalResult(
        source_type="web",
        ref_id="web:3",
        chunk_id=3,
        title="t3",
        url="u3",
        domain="d3",
        score=0.8,
        text="c" * 200,
        meta={},
    )

    sources, _ = build_context([small1, big, small2], max_chars=700, preserve_order=True)
    ref_ids = [s["ref_id"] for s in sources]

    assert "web:1" in ref_ids
    assert "web:3" in ref_ids
