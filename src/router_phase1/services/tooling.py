from __future__ import annotations

import asyncio
import json
import os
from dataclasses import dataclass
from typing import Any

import httpx
from pydantic import BaseModel, ConfigDict

from ..stores import ragstore, webstore
from .. import config
from .retrieval import KiwixRetrievalProvider
from .web_ingest import WebIngestQueue
from .web_search import ddg_search


DEFAULT_MAX_TOOL_ROUNDS = 3
MAX_WEB_PAGES = 12


def _ollama_chat_timeout() -> float | None:
    """Return timeout seconds for Ollama /api/chat calls.

    Model loads can take minutes; default to no timeout unless explicitly set.
    """
    raw = os.getenv("OLLAMA_CHAT_TIMEOUT_SEC", "0").strip()
    try:
        sec = float(raw)
    except ValueError:
        sec = 0.0
    return None if sec <= 0 else sec


class ToolDocSearchReq(BaseModel):
    model_config = ConfigDict(extra="ignore")
    query: str
    top_k: int = 6
    doc_ids: list[int] | None = None
    embed_model: str | None = None
    use_mmr: bool | None = None
    mmr_lambda: float = 0.75


class ToolWebSearchReq(BaseModel):
    model_config = ConfigDict(extra="ignore")
    query: str
    top_k: int = 6
    pages: int = 5
    domain_whitelist: list[str] | None = None
    embed_model: str | None = None
    force: bool = False


class ToolKiwixSearchReq(BaseModel):
    model_config = ConfigDict(extra="ignore")
    query: str
    top_k: int = 6


@dataclass
class ToolLoopResult:
    content: str
    messages: list[dict[str, Any]]
    used_tools: bool


def tool_definitions() -> list[dict[str, Any]]:
    return [
        {
            "type": "function",
            "function": {
                "name": "doc_search",
                "description": "Search uploaded documents for relevant passages.",
                "parameters": ToolDocSearchReq.model_json_schema(),
            },
        },
        {
            "type": "function",
            "function": {
                "name": "web_search",
                "description": "Search the web and return relevant passages.",
                "parameters": ToolWebSearchReq.model_json_schema(),
            },
        },
        {
            "type": "function",
            "function": {
                "name": "kiwix_search",
                "description": "Search offline Kiwix content if configured.",
                "parameters": ToolKiwixSearchReq.model_json_schema(),
            },
        },
    ]


def _clamp_int(val: int, low: int, high: int) -> int:
    return max(low, min(high, int(val)))


def _parse_tool_args(raw: Any) -> dict[str, Any]:
    if isinstance(raw, dict):
        return raw
    if isinstance(raw, str):
        try:
            parsed = json.loads(raw)
            if isinstance(parsed, dict):
                return parsed
        except json.JSONDecodeError:
            return {}
    return {}


async def tool_doc_search(req: ToolDocSearchReq) -> dict[str, Any]:
    query = (req.query or "").strip()
    if not query:
        raise ValueError("query required")
    hits = await ragstore.retrieve(
        query,
        top_k=req.top_k,
        doc_ids=req.doc_ids,
        embed_model=req.embed_model,
        use_mmr=req.use_mmr,
        mmr_lambda=req.mmr_lambda,
    )
    return {"query": query, "results": hits}


async def tool_web_search(
    req: ToolWebSearchReq,
    *,
    http: httpx.AsyncClient,
    ingest_queue: WebIngestQueue | None,
    embed_model: str,
    kiwix_url: str | None,
) -> dict[str, Any]:
    query = (req.query or "").strip()
    if not query:
        raise ValueError("query required")
    pages = _clamp_int(req.pages, 1, MAX_WEB_PAGES)
    errors: list[dict[str, Any]] = []
    kiwix_results: list[dict[str, Any]] = []
    if kiwix_url:
        try:
            provider = KiwixRetrievalProvider(kiwix_url)
            kiwix_results = [r.__dict__ for r in await provider.retrieve(query, top_k=req.top_k, embed_model=req.embed_model)]
        except Exception as exc:
            errors.append({"stage": "kiwix", "error": str(exc)})

    try:
        urls = await ddg_search(http, query, n=pages)
    except Exception as exc:
        urls = []
        errors.append({"stage": "search", "error": str(exc)})

    fetched = []
    queued: list[str] = []
    if urls:
        sync_cap = len(urls) if req.force else 2
        sync_targets = urls[:sync_cap]
        queued = urls[sync_cap:]
        tasks = [webstore.upsert_page_from_url(u, force=bool(req.force)) for u in sync_targets]
        results = await asyncio.gather(*tasks, return_exceptions=True)
        for url, result in zip(sync_targets, results):
            if isinstance(result, BaseException):
                errors.append({"url": url, "error": str(result)})
                continue
            if not isinstance(result, dict):
                errors.append({"url": url, "error": "unexpected response"})
                continue
            fetched.append(
                {
                    "url": result.get("url") or url,
                    "title": result.get("title"),
                    "domain": result.get("domain"),
                    "page_id": result.get("id"),
                }
            )
        if ingest_queue is not None:
            for url in queued:
                await ingest_queue.enqueue(url)

    hits = await webstore.retrieve(
        query,
        top_k=req.top_k,
        domain_whitelist=req.domain_whitelist,
        embed_model=req.embed_model or embed_model,
    )
    combined = kiwix_results + hits
    return {
        "query": query,
        "urls": urls,
        "fetched": fetched,
        "queued": queued,
        "errors": errors,
        "kiwix_results": kiwix_results,
        "results": combined,
    }


async def tool_kiwix_search(
    req: ToolKiwixSearchReq,
    *,
    kiwix_url: str | None,
    embed_model: str,
) -> dict[str, Any]:
    if not kiwix_url:
        return {"results": [], "error": "KIWIX_URL not set"}
    query = (req.query or "").strip()
    if not query:
        raise ValueError("query required")
    provider = KiwixRetrievalProvider(kiwix_url)
    results = await provider.retrieve(query, top_k=req.top_k, embed_model=embed_model)
    return {"results": [r.__dict__ for r in results]}


async def _execute_tool_call(
    name: str,
    args: dict[str, Any],
    *,
    http: httpx.AsyncClient,
    ingest_queue: WebIngestQueue | None,
    embed_model: str,
    kiwix_url: str | None,
) -> dict[str, Any]:
    if name == "doc_search":
        req = ToolDocSearchReq.model_validate(args)
        return await tool_doc_search(req)
    if name == "web_search":
        req = ToolWebSearchReq.model_validate(args)
        return await tool_web_search(
            req,
            http=http,
            ingest_queue=ingest_queue,
            embed_model=embed_model,
            kiwix_url=kiwix_url,
        )
    if name == "kiwix_search":
        req = ToolKiwixSearchReq.model_validate(args)
        return await tool_kiwix_search(req, kiwix_url=kiwix_url, embed_model=embed_model)
    raise ValueError(f"Unknown tool: {name}")


def _extract_tool_calls(message: Any) -> list[dict[str, Any]]:
    if isinstance(message, dict):
        tool_calls = message.get("tool_calls")
    else:
        tool_calls = getattr(message, "tool_calls", None)
    if not tool_calls:
        return []
    if isinstance(tool_calls, list):
        return tool_calls
    return []


def _parse_tool_call(call: dict[str, Any], index: int) -> tuple[str, dict[str, Any], str]:
    call_id = call.get("id") or call.get("tool_call_id") or f"tool_call_{index}"
    function = call.get("function") or {}
    name = function.get("name") or call.get("name") or ""
    raw_args = function.get("arguments") if function else call.get("arguments")
    args = _parse_tool_args(raw_args)
    return name, args, call_id


async def run_tool_calling_loop(
    *,
    http: httpx.AsyncClient,
    ollama_url: str,
    model: str,
    messages: list[dict[str, Any]],
    options: dict[str, Any] | None,
    keep_alive: str | None,
    embed_model: str,
    ingest_queue: WebIngestQueue | None,
    kiwix_url: str | None,
    max_rounds: int = DEFAULT_MAX_TOOL_ROUNDS,
    emit: Any = None,
) -> ToolLoopResult:
    tools = tool_definitions()
    working = list(messages)
    used_tools = False

    timeout = _ollama_chat_timeout()

    for round_idx in range(max_rounds):
        payload: dict[str, Any] = {
            "model": model,
            "messages": working,
            "stream": False,
            "tools": tools,
        }
        if options is not None:
            payload["options"] = options
        if keep_alive is not None:
            payload["keep_alive"] = keep_alive

        if emit:
            if round_idx == 0:
                await emit({"type": "status", "stage": "pulling_from_disk"})
            else:
                await emit({"type": "status", "stage": "constructing_response"})

        resp = await http.post(f"{ollama_url}/api/chat", json=payload, timeout=timeout)
        resp.raise_for_status()
        message = (resp.json().get("message") or {})
        content = (message.get("content") or "").strip()
        tool_calls = _extract_tool_calls(message)
        if not tool_calls:
            if emit:
                await emit({"type": "status", "stage": "constructing_response"})
            return ToolLoopResult(content=content, messages=working, used_tools=used_tools)

        used_tools = True

        if emit:
            await emit({"type": "status", "stage": "calling_tools"})
        assistant_msg = {
            "role": "assistant",
            "content": content,
            "tool_calls": tool_calls,
        }
        working.append(assistant_msg)

        for idx, call in enumerate(tool_calls, start=1):
            if not isinstance(call, dict):
                continue
            name, args, call_id = _parse_tool_call(call, idx)
            try:
                if emit and name:
                    await emit({"type": "tool", "name": name})
                result = await _execute_tool_call(
                    name,
                    args,
                    http=http,
                    ingest_queue=ingest_queue,
                    embed_model=embed_model,
                    kiwix_url=kiwix_url,
                )
                payload = {"ok": True, "tool": name, "result": result}
            except Exception as exc:
                payload = {"ok": False, "tool": name, "error": str(exc)}
            working.append(
                {
                    "role": "tool",
                    "content": json.dumps(payload, ensure_ascii=False),
                    "tool_call_id": call_id,
                    "name": name,
                }
            )

    fallback_payload: dict[str, Any] = {"model": model, "messages": working, "stream": False}
    if options is not None:
        fallback_payload["options"] = options
    if keep_alive is not None:
        fallback_payload["keep_alive"] = keep_alive

    if emit:
        await emit({"type": "status", "stage": "constructing_response"})
    resp = await http.post(f"{ollama_url}/api/chat", json=fallback_payload, timeout=timeout)
    resp.raise_for_status()
    message = (resp.json().get("message") or {})
    content = (message.get("content") or "").strip()
    return ToolLoopResult(content=content, messages=working, used_tools=used_tools)


async def chat_with_tools(
    *,
    http: httpx.AsyncClient,
    ollama_url: str,
    model: str,
    messages: list[dict[str, Any]],
    options: dict[str, Any] | None = None,
    keep_alive: str | None = None,
    embed_model: str | None = None,
    ingest_queue: WebIngestQueue | None = None,
    kiwix_url: str | None = None,
    emit: Any = None,
) -> str:
    embed = embed_model or config.config.default_embed_model
    result = await run_tool_calling_loop(
        http=http,
        ollama_url=ollama_url,
        model=model,
        messages=messages,
        options=options,
        keep_alive=keep_alive,
        embed_model=embed,
        ingest_queue=ingest_queue,
        kiwix_url=kiwix_url,
        emit=emit,
    )
    return result.content
