from __future__ import annotations


def test_user_requested_references_detects_explicit_asks() -> None:
    from contextharbor.services.evidence import user_requested_references

    assert user_requested_references("Provide a bibliography.") is True
    assert user_requested_references("Add a works cited section.") is True
    assert user_requested_references("Please cite your sources.") is True

    # Ambiguous cases should stay conservative.
    assert user_requested_references("Show sources of error in this system.") is False


def test_infer_epub_intent_routes_fiction_and_reference() -> None:
    from contextharbor.services.evidence import infer_epub_intent

    assert infer_epub_intent("Summarize the novel Dune.") == "fiction"
    assert infer_epub_intent("Quote from chapter 3.") == "fiction"
    assert infer_epub_intent("Give me references for this claim.") == "reference"
    assert infer_epub_intent("What is a mutex?") == "none"


def test_chat_citation_scrubber_is_code_fence_aware() -> None:
    from contextharbor.services.chat import _strip_forbidden_citations

    txt = """Here is some code:

```python
# References:
arr = [1, 2, 3]
print(arr[1])
```

References:
[1] Totally made up.
"""

    out = _strip_forbidden_citations(txt, allow_reference_section=False)
    assert "# References:" in out  # keep code
    assert "Totally made up" not in out  # strip tail


def test_chat_citation_scrubber_allows_reference_section_when_requested() -> None:
    from contextharbor.services.chat import (
        _strip_forbidden_citations,
        _has_forbidden_citations,
    )

    txt = """Claim.

References:
[1] A thing.
"""

    assert _has_forbidden_citations(txt, allow_reference_section=False) is True
    assert _has_forbidden_citations(txt, allow_reference_section=True) is False

    out = _strip_forbidden_citations(txt, allow_reference_section=True)
    assert "References" in out


def test_chat_citation_scrubber_does_not_flag_numeric_tokens_alone() -> None:
    from contextharbor.services.chat import _has_forbidden_citations

    assert (
        _has_forbidden_citations("Use arr[1]", allow_reference_section=False) is False
    )
    assert (
        _has_forbidden_citations("A claim [1]", allow_reference_section=False) is False
    )
