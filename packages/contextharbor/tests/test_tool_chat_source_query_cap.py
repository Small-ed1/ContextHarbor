import pytest

from unittest.mock import AsyncMock


@pytest.mark.asyncio
async def test_tool_chat_caps_source_query_attempts(monkeypatch):
    from contextharbor.services import tool_chat

    # Mock LLM responses: first returns 4 source-query tool calls, second ends.
    first = {
        "role": "assistant",
        "content": "",
        "tool_calls": [
            {"id": "c1", "function": {"name": "web_search", "arguments": {"q": "alpha"}}},
            {"id": "c2", "function": {"name": "web_search", "arguments": {"q": "beta"}}},
            {"id": "c3", "function": {"name": "web_search", "arguments": {"q": "gamma"}}},
            {"id": "c4", "function": {"name": "web_search", "arguments": {"q": "delta"}}},
        ],
    }
    second = {"role": "assistant", "content": "done"}

    call_llm = AsyncMock(side_effect=[first, second])
    monkeypatch.setattr(tool_chat, "_call_llm", call_llm)

    # Dummy registry + executor.
    class _Reg:
        def build_ollama_tools(self):
            return []

    exec_run = AsyncMock(
        return_value={
            "type": "tool_result",
            "id": "req_0",
            "results": [
                {"id": "c1", "name": "web_search", "ok": True, "data": {"items": [{"url": "u1"}]}, "error": None, "meta": {}},
                {"id": "c2", "name": "web_search", "ok": True, "data": {"items": [{"url": "u2"}]}, "error": None, "meta": {}},
                {"id": "c3", "name": "web_search", "ok": True, "data": {"items": [{"url": "u3"}]}, "error": None, "meta": {}},
            ],
            "error": None,
        }
    )

    class _Exec:
        def __init__(self):
            self.registry = _Reg()

        async def run_calls(self, calls, **kwargs):
            # Only 3 calls should be executed.
            assert [c.id for c in calls] == ["c1", "c2", "c3"]
            return await exec_run(calls, **kwargs)

    emitted = []

    async def emit(evt):
        emitted.append(evt)

    out = await tool_chat.chat_with_tool_contract(
        http=AsyncMock(),
        ollama_url="http://ollama",
        model="m",
        executor=_Exec(),
        tools_for_prompt=[],
        user_text="x",
        max_loops=2,
        max_source_queries=3,
        emit=emit,
    )

    assert out == "done"

    # The emitted tool_results should include the blocked call (c4).
    tool_results = [e for e in emitted if e.get("type") == "tool_results"]
    assert len(tool_results) == 1
    results = tool_results[0].get("results")
    assert isinstance(results, list)
    assert {r.get("id") for r in results} == {"c1", "c2", "c3", "c4"}
    blocked = next(r for r in results if r.get("id") == "c4")
    assert blocked.get("ok") is False
    assert blocked.get("error", {}).get("code") == "query_attempt_limit"
