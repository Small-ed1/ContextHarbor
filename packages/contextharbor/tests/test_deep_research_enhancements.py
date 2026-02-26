from __future__ import annotations

import sqlite3
from pathlib import Path

import httpx
import pytest

from contextharbor.services.context import build_context
from contextharbor.services.retrieval import RetrievalResult
from contextharbor.services.web_ingest import WebIngestQueue
from contextharbor.stores import researchstore


def test_build_context_respects_pinned_and_excluded() -> None:
    r1 = RetrievalResult(
        source_type="doc",
        ref_id="doc:1",
        chunk_id=1,
        title="Doc One",
        url=None,
        domain=None,
        score=0.9,
        text="doc text",
        meta={},
    )
    r2 = RetrievalResult(
        source_type="web",
        ref_id="web:2",
        chunk_id=2,
        title="Web Two",
        url="https://example.com/two",
        domain="example.com",
        score=0.8,
        text="web text",
        meta={},
    )
    r3 = RetrievalResult(
        source_type="web",
        ref_id="web:3",
        chunk_id=3,
        title="Web Three",
        url="https://example.com/three",
        domain="example.com",
        score=0.7,
        text="web text 3",
        meta={},
    )

    sources, lines = build_context(
        [r1, r2, r3],
        per_source_cap=1,
        pinned_ref_ids={"web:3"},
        excluded_ref_ids={"doc:1"},
    )

    # Excluded doc is not present.
    assert all(s.get("ref_id") != "doc:1" for s in sources)

    # Pinned web item is included even if per-source cap is reached.
    ref_ids = [s.get("ref_id") for s in sources]
    assert "web:3" in ref_ids

    # Pinned item is prioritized.
    assert sources[0].get("ref_id") == "web:3"
    assert sources[0].get("pinned") is True

    # Context lines include citation tags.
    assert any(ln.startswith("[W") for ln in lines)


def test_researchstore_upsert_preserves_flags(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    db = tmp_path / "research.sqlite3"
    monkeypatch.setenv("RESEARCH_DB", str(db))

    # Re-import module-level DB path by reloading store.
    import importlib
    import contextharbor.stores.researchstore as rs

    importlib.reload(rs)
    rs.init_db()

    run_id = rs.create_run(chat_id=None, query="q", mode="deep", settings={})
    rs.add_sources(
        run_id,
        [
            {
                "source_type": "web",
                "ref_id": "web:123",
                "chunk_id": 123,
                "title": "t",
                "url": "https://example.com",
                "domain": "example.com",
                "score": 1.0,
                "snippet": "s",
                "meta": {},
                "citation": "W1",
                "pinned": True,
                "excluded": False,
            }
        ],
    )

    # Upsert same ref_id without flags should preserve pinned/excluded.
    rs.upsert_sources(
        run_id,
        [
            {
                "source_type": "web",
                "ref_id": "web:123",
                "chunk_id": 123,
                "title": "t2",
                "url": "https://example.com/2",
                "domain": "example.com",
                "score": 0.5,
                "snippet": "s2",
                "meta": {},
                "citation": "W1",
            }
        ],
    )

    src = rs.get_sources(run_id)
    assert len(src) == 1
    assert src[0]["ref_id"] == "web:123"
    assert bool(src[0]["pinned"]) is True
    assert bool(src[0]["excluded"]) is False


def test_webstore_fts_is_populated(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    db = tmp_path / "web.sqlite3"

    # Ensure webstore uses our temp DB.
    monkeypatch.setenv("WEB_DB", str(db))

    import importlib
    import contextharbor.stores.webstore as ws

    importlib.reload(ws)
    ws.init_db()

    con = sqlite3.connect(str(db))
    try:
        con.execute(
            "INSERT INTO web_pages(url,domain,title,fetched_at,published_at,content_hash,text,embed_model,embed_dim) VALUES(?,?,?,?,NULL,?,?,?,?)",
            (
                "https://example.com",
                "example.com",
                "Example",
                1,
                "h",
                "page text",
                "m",
                3,
            ),
        )
        page_id = int(
            con.execute(
                "SELECT id FROM web_pages WHERE url=?", ("https://example.com",)
            ).fetchone()[0]
        )

        con.execute(
            "INSERT INTO web_chunks(page_id, chunk_index, text, embedding) VALUES(?,?,?,?)",
            (page_id, 0, "chunk text for fts", b"x"),
        )
        chunk_id = int(
            con.execute(
                "SELECT id FROM web_chunks WHERE page_id=?", (page_id,)
            ).fetchone()[0]
        )

        row = con.execute(
            "SELECT text FROM web_chunks_fts WHERE rowid=?", (chunk_id,)
        ).fetchone()
        assert row is not None
        assert "chunk text" in str(row[0])
    finally:
        con.close()


@pytest.mark.asyncio
async def test_run_research_honors_done_if(monkeypatch: pytest.MonkeyPatch) -> None:
    from contextharbor.services import research as rs

    async def fake_plan(*_a, **_k):
        return {
            "subquestions": [],
            "web_queries": [],
            "doc_queries": ["dq"],
            "done_if": ["enough"],
            "raw": "",
        }

    async def fake_profile(*_a, **_k):
        return {
            "question_type": "general_factual",
            "force_evidence_policy": "default",
            "force_epub_context_only": False,
            "require_evidence": False,
            "reason": "",
            "raw": "",
        }

    async def fake_deep_tool_plan(*_a, **_k):
        # Return a single doc_search tool call.
        return {
            "role": "assistant",
            "content": "",
            "tool_calls": [
                {
                    "id": "tool_call_1",
                    "function": {
                        "name": "doc_search",
                        "arguments": {"query": "dq", "top_k": 1},
                    },
                }
            ],
        }

    async def fake_execute_tool(*, name: str, args: dict, **_k):
        assert name == "doc_search"
        # Minimal shape matching tool_doc_search output.
        hit = {
            "chunk_id": 42,
            "doc_id": 1,
            "chunk_index": 0,
            "filename": "x.txt",
            "title": "Doc",
            "section": "",
            "score": 1.0,
            "text": "Some grounded text.",
            # Treat as user-provided doc so strict evidence policy allows it.
            "source": "upload",
            "path": "x.txt",
            "tags_json": "[]",
        }
        return {
            "tool": name,
            "ok": True,
            "result": {"query": args.get("query"), "results": [hit]},
        }

    async def fake_relevance(*_a, **_k):
        return {
            "keep_ref_ids": ["doc:42"],
            "drop_ref_ids": [],
            "missing": [],
            "done": False,
            "reason": "ok",
        }

    async def fake_gap(*_a, **_k):
        return {
            "done": True,
            "reason": "ok",
            "doc_queries": [],
            "web_queries": [],
            "kiwix_query": None,
        }

    async def fake_verify(*_a, **_k):
        return {
            "claims": [
                {"claim": "c", "status": "supported", "citations": ["D1"], "notes": ""}
            ],
            "raw": "",
        }

    async def fake_construct(*_a, **_k):
        return "answer [D1]"

    async def fake_analyze_response(*_a, **_k):
        return {"issues": [], "rewrite_needed": False, "raw": ""}

    async def fake_edit(*_a, **_k):
        return "answer [D1]"

    async def fake_format(*_a, **_k):
        return "answer [D1]"

    async def fake_finalize(*_a, **_k):
        return "answer [D1]"

    async def fake_parse(*_a, **_k):
        return {"facts": [], "open_questions": [], "raw": ""}

    async def fake_analyze(*_a, **_k):
        return {"need_more_research": False, "missing": [], "why": "", "raw": ""}

    async def fake_breakdown(*_a, **_k):
        return {"doc_queries": [], "web_queries": [], "kiwix_query": None, "raw": ""}

    async def fake_citation_audit(*_a, **_k):
        return "answer [D1]"

    async def fake_done_if(*_a, **_k):
        return {"done": True, "reason": "ok"}

    monkeypatch.setattr(rs, "_plan_queries", fake_plan)
    monkeypatch.setattr(rs, "_deep_research_question_profile", fake_profile)
    monkeypatch.setattr(rs, "_deep_agentic_tool_plan", fake_deep_tool_plan)
    monkeypatch.setattr(rs, "_deep_agentic_relevance_check", fake_relevance)
    monkeypatch.setattr(rs, "_execute_research_tool", fake_execute_tool)
    monkeypatch.setattr(rs, "_verify_claims", fake_verify)
    monkeypatch.setattr(rs, "_gap_check_and_refine_queries", fake_gap)
    monkeypatch.setattr(rs, "_deep_agentic_parse", fake_parse)
    monkeypatch.setattr(rs, "_deep_agentic_analyze", fake_analyze)
    monkeypatch.setattr(rs, "_deep_agentic_breakdown_further", fake_breakdown)
    monkeypatch.setattr(rs, "_deep_agentic_construct_response", fake_construct)
    monkeypatch.setattr(rs, "_deep_agentic_analyze_response", fake_analyze_response)
    monkeypatch.setattr(rs, "_deep_agentic_edit", fake_edit)
    monkeypatch.setattr(rs, "_deep_agentic_format", fake_format)
    monkeypatch.setattr(rs, "_deep_agentic_finalize", fake_finalize)
    monkeypatch.setattr(rs, "_citation_audit_rewrite", fake_citation_audit)
    monkeypatch.setattr(rs, "_check_done_if", fake_done_if)

    async with httpx.AsyncClient() as http:
        out = await rs.run_research(
            http=http,
            base_url="http://127.0.0.1:11434",
            ingest_queue=WebIngestQueue(concurrency=1),
            kiwix_url=None,
            chat_id=None,
            query="q",
            mode="deep",
            use_docs=True,
            use_web=False,
            rounds=3,
            pages_per_round=1,
            web_top_k=1,
            doc_top_k=1,
            domain_whitelist=None,
            embed_model="nomic-embed-text",
            planner_model="m",
            verifier_model="m",
            synth_model="m",
            settings={},
        )

    ans = str(out.get("answer") or "")
    assert ans.startswith("answer")
    assert "## Sources" in ans
    assert out.get("run_id")

    # Confirm the done_if trace exists.
    trace = researchstore.get_trace(out["run_id"], limit=500, offset=0)
    assert any(t.get("step") == "done_if" for t in trace)
