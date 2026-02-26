from __future__ import annotations

import re
from typing import Any


VALID_EVIDENCE_POLICIES = {"strict", "relaxed"}
VALID_DOC_GENRES = {"unknown", "fiction", "nonfiction", "reference"}


_CITATION_TAG = re.compile(r"\[([A-Z]\d+)\]")
_KIWIX_ZIM = re.compile(r"/content/([^/]+)/")


def infer_evidence_policy(query: str, *, default_policy: str = "strict") -> str:
    """Infer evidence policy for a query.

    - strict: evidence/citation gate is enforced
    - relaxed: citations can come from any retrieved source
    """

    d = (default_policy or "strict").strip().lower()
    if d not in VALID_EVIDENCE_POLICIES:
        d = "strict"

    q = (query or "").strip().lower()
    if not q:
        return d

    # Explicitly non-empirical / literary requests: allow fiction as first-class sources.
    creative_needles = (
        "write a story",
        "fanfic",
        "fanfiction",
        "roleplay",
        "plot",
        "character",
        "chapter",
        "scene",
        "poem",
        "lyrics",
        "summarize the novel",
        "book summary",
    )
    if any(n in q for n in creative_needles):
        return "relaxed"

    # Evidence-demanding prompts: fail closed.
    strict_needles = (
        "demonstrably",
        "has been demonstrated",
        "studies show",
        "study shows",
        "meta-analysis",
        "systematic review",
        "randomized",
        "clinical trial",
        "statistically",
        "data show",
        "evidence",
        "where has it failed",
        "failure modes",
        "failure rate",
    )
    if any(n in q for n in strict_needles):
        return "strict"

    return d


def user_requested_references(query: str) -> bool:
    """Best-effort detector for user requests for references/citations.

    Used to decide whether to allow a References/Sources section in chat output and
    whether to include EPUBs by default.
    """

    q = (query or "").strip().lower()
    if not q:
        return False

    # Common non-citation uses of "sources" (causes/origins), not bibliographic requests.
    non_citation_phrases = (
        "sources of error",
        "source of error",
        "sources of bias",
        "source of bias",
        "sources of noise",
        "source of noise",
        "sources of uncertainty",
        "source of uncertainty",
        "sources of variation",
        "source of variation",
    )
    if any(p in q for p in non_citation_phrases):
        return False

    # Strong explicit asks.
    strong_needles = (
        "works cited",
        "bibliography",
        "reference list",
        "list of references",
        "cite your sources",
        "cite sources",
        "provide sources",
        "list sources",
        "show sources",
        "include sources",
        "add sources",
        "provide references",
        "include references",
        "include citations",
        "add references",
        "add citations",
        "with references",
        "with citations",
        "with sources",
    )
    if any(n in q for n in strong_needles):
        return True

    # Weaker: "references"/"sources" without an imperative can be ambiguous.
    # Only count it when it looks like a request.
    weak_markers = ("references", "citations")
    if any(w in q for w in weak_markers):
        verbs = ("list", "include", "provide", "give", "show", "add", "cite")
        if any(v + " " in q for v in verbs):
            return True

    return False


def infer_epub_intent(query: str) -> str:
    """Infer whether EPUBs should be included for retrieval.

    Returns one of: "fiction", "reference", "none".
    """

    q = (query or "").strip().lower()
    if not q:
        return "none"

    fiction_needles = (
        "fanfic",
        "fanfiction",
        "roleplay",
        "plot",
        "character",
        "chapter",
        "scene",
        "novel",
        "short story",
        "fiction",
        "summarize the novel",
        "book summary",
        "quote from",
        "excerpt",
    )
    if any(n in q for n in fiction_needles):
        return "fiction"

    if user_requested_references(q):
        return "reference"

    return "none"


def kiwix_zim_id(url: str | None, path: str | None) -> str | None:
    s = (url or path or "").strip()
    if not s:
        return None
    m = _KIWIX_ZIM.search(s)
    if not m:
        return None
    zim = (m.group(1) or "").strip()
    return zim or None


def heuristic_doc_genre(
    *,
    title: str | None,
    author: str | None,
    path: str | None,
    tags: list[str] | None,
    default_genre: str = "unknown",
) -> tuple[str, str]:
    """Fast doc-genre heuristic.

    Returns (doc_genre, reason).
    """

    d = (default_genre or "unknown").strip().lower()
    if d not in VALID_DOC_GENRES:
        d = "unknown"

    tagset = {str(t).strip().lower() for t in (tags or []) if str(t).strip()}
    if tagset:
        fiction_tags = {
            "fiction",
            "novel",
            "sci-fi",
            "scifi",
            "fantasy",
            "romance",
            "mystery",
            "thriller",
            "short stories",
            "literature",
        }
        reference_tags = {
            "reference",
            "encyclopedia",
            "dictionary",
            "handbook",
            "manual",
            "specification",
            "standard",
        }
        nonfiction_tags = {
            "nonfiction",
            "non-fiction",
            "textbook",
            "course",
            "monograph",
            "biography",
            "history",
            "science",
            "medicine",
            "engineering",
        }

        if tagset.intersection(reference_tags):
            return ("reference", "tag")
        if tagset.intersection(nonfiction_tags):
            return ("nonfiction", "tag")
        if tagset.intersection(fiction_tags):
            return ("fiction", "tag")

    p = (path or "").strip().lower()
    if p:
        if any(x in p for x in ("/fiction/", "\\fiction\\", " fiction ")):
            return ("fiction", "path")
        if any(
            x in p
            for x in ("/nonfiction/", "\\nonfiction\\", "non-fiction", " nonfiction ")
        ):
            return ("nonfiction", "path")
        if any(
            x in p
            for x in ("/reference/", "\\reference\\", " encyclopedia ", " dictionary ")
        ):
            return ("reference", "path")

    t = (title or "").strip().lower()
    a = (author or "").strip().lower()
    hay = (t + " " + a).strip()
    if hay:
        # Very light signals; keep conservative.
        if "encyclopedia" in hay or "dictionary" in hay or "handbook" in hay:
            return ("reference", "title")
        if "a novel" in hay or "(novel" in hay:
            return ("fiction", "title")

    return (d, "default")


def trust_tier_for(
    kind: str, *, doc_genre: str, trust_tiers: dict[str, float] | None
) -> float:
    tiers = trust_tiers or {}
    k = (kind or "").strip().lower()
    g = (doc_genre or "unknown").strip().lower()
    if g not in VALID_DOC_GENRES:
        g = "unknown"

    if k == "epub":
        key = f"epub_{g}"
        if key in tiers:
            return float(tiers.get(key) or 0.0)
    if k in tiers:
        return float(tiers.get(k) or 0.0)
    return 0.0


def evidence_ok(
    *,
    policy: str,
    kind: str,
    doc_genre: str,
    kiwix_zim: str | None,
    strict_allowlist: list[str] | None,
    kiwix_zim_allowlist: list[str] | None,
    epub_nonfiction_is_evidence: bool,
    epub_reference_is_evidence: bool,
    epub_fiction_is_evidence: bool,
) -> tuple[bool, str]:
    p = (policy or "strict").strip().lower()

    k = (kind or "").strip().lower()
    g = (doc_genre or "unknown").strip().lower()
    if g not in VALID_DOC_GENRES:
        g = "unknown"

    allow = [str(x).strip().lower() for x in (strict_allowlist or []) if str(x).strip()]

    # EPUBs are NOT evidence-eligible by default.
    # They can be enabled per-genre when you explicitly want to cite the book itself.
    if k == "epub":
        if g == "reference" and bool(epub_reference_is_evidence):
            return (True, "epub_reference")
        if g == "nonfiction" and bool(epub_nonfiction_is_evidence):
            return (True, "epub_nonfiction")
        if g == "fiction" and bool(epub_fiction_is_evidence):
            return (True, "epub_fiction_allowed")
        return (False, f"epub_{g}_not_evidence")

    # If relaxed, allow non-EPUB sources through the gate.
    if p != "strict":
        return (True, "policy_relaxed")

    if allow and k not in set(allow):
        return (False, "kind_not_allowlisted")

    if k == "kiwix_zim":
        z_allow = [
            str(x).strip().lower()
            for x in (kiwix_zim_allowlist or [])
            if str(x).strip()
        ]
        if not z_allow:
            return (True, "kiwix_ok")
        if not kiwix_zim:
            return (False, "kiwix_zim_unknown")
        z = str(kiwix_zim).strip().lower()
        if any(a in z for a in z_allow):
            return (True, "kiwix_allowlisted")
        return (False, "kiwix_not_allowlisted")

    return (True, "allowlisted")


def extract_citation_tags(text: str) -> set[str]:
    return {m.group(1) for m in _CITATION_TAG.finditer(text or "") if m.group(1)}
