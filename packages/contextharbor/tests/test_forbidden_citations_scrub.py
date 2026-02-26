from __future__ import annotations


def test_research_strip_invalid_citation_tokens_removes_numeric_and_refs() -> None:
    from contextharbor.services import research

    txt = """Some claim [D1] and some fake [1].

References:
[1] Totally Made Up.
"""
    out = research._strip_invalid_citation_tokens(txt, allowed_tags={"D1"})

    assert "[D1]" in out
    assert "[1]" not in out
    assert "References" not in out
