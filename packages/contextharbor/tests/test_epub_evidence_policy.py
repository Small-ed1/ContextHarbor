from __future__ import annotations

import httpx
import pytest

from contextharbor.services import evidence


def test_evidence_ok_epub_disabled_by_default() -> None:
    # Regardless of strict/relaxed, EPUB should not be evidence unless explicitly enabled.
    for policy in ("strict", "relaxed"):
        ok, reason = evidence.evidence_ok(
            policy=policy,
            kind="epub",
            doc_genre="nonfiction",
            kiwix_zim=None,
            strict_allowlist=["kiwix_zim", "web", "uploaded_doc"],
            kiwix_zim_allowlist=[],
            epub_nonfiction_is_evidence=False,
            epub_reference_is_evidence=False,
            epub_fiction_is_evidence=False,
        )
        assert ok is False
        assert "epub" in reason


@pytest.mark.asyncio
async def test_execute_research_tool_injects_exclude_epub(monkeypatch: pytest.MonkeyPatch) -> None:
    from contextharbor.services import research

    seen = {}

    async def fake_tool_doc_search(req):
        seen["exclude_group_names"] = list(req.exclude_group_names or [])
        return {"query": req.query, "results": []}

    monkeypatch.setattr(research, "tool_doc_search", fake_tool_doc_search)

    async with httpx.AsyncClient() as http:
        out = await research._execute_research_tool(
            name="doc_search",
            args={"query": "q", "top_k": 3},
            http=http,
            ingest_queue=object(),
            embed_model="m",
            kiwix_url=None,
            doc_top_k=6,
            web_top_k=6,
            pages_per_round=3,
            domain_whitelist=None,
            allow_epub=False,
        )

    assert out.get("query") == "q"
    assert "epub" in {x.lower() for x in (seen.get("exclude_group_names") or [])}


@pytest.mark.asyncio
async def test_execute_research_tool_allows_epub_when_enabled(monkeypatch: pytest.MonkeyPatch) -> None:
    from contextharbor.services import research

    seen = {}

    async def fake_tool_doc_search(req):
        seen["exclude_group_names"] = req.exclude_group_names
        return {"query": req.query, "results": []}

    monkeypatch.setattr(research, "tool_doc_search", fake_tool_doc_search)

    async with httpx.AsyncClient() as http:
        await research._execute_research_tool(
            name="doc_search",
            args={"query": "q", "top_k": 3},
            http=http,
            ingest_queue=object(),
            embed_model="m",
            kiwix_url=None,
            doc_top_k=6,
            web_top_k=6,
            pages_per_round=3,
            domain_whitelist=None,
            allow_epub=True,
        )

    assert seen.get("exclude_group_names") in (None, [])
