"""Deep research pipeline.

This module provides a small, self-contained research flow that:
- plans a handful of search queries
- gathers sources via SearxNG (web_search)
- opens and extracts text from top sources
- synthesizes a cited report with an Ollama model

It is designed to be used from both the interactive shell and a CLI subcommand.
"""

import json
import re
import sys
import time
from dataclasses import dataclass
from typing import Any, Dict, List, Optional, Tuple
from urllib.parse import quote, unquote

from .client import OllamaClient
from .config import DEFAULT_SEARXNG_URL
from .tools.kiwix_tools import KiwixTools
from .tools.web_tools import WebTools


MAX_SOURCE_QUERY_ATTEMPTS = 3


_CODE_BLOCK = re.compile(r"```(?:json)?\s*(.*?)\s*```", re.DOTALL)


def normalize_query(q: str) -> str:
    q = (q or "").strip()
    q = re.sub(r"\s+", " ", q)
    q = q.rstrip(".!?;:,")
    return q


def _progress(msg: str) -> None:
    print(msg, file=sys.stderr, flush=True)


def _query_tokens(q: str) -> List[str]:
    tokens: List[str] = []
    seen = set()
    for t in re.findall(r"[A-Za-z0-9]+", (q or "").lower()):
        if len(t) < 3:
            continue
        if t in seen:
            continue
        seen.add(t)
        tokens.append(t)
    return tokens


def _keyword_overlap_score(tokens: List[str], title: str, snippet: str) -> int:
    if not tokens:
        return 0
    hay = f"{title} {snippet}".lower()
    score = 0
    for t in tokens:
        if t in hay:
            score += 1
    # Weight title matches a bit higher.
    title_l = (title or "").lower()
    for t in tokens:
        if t in title_l:
            score += 1
    return score


def _shrink_opened_doc(doc: Dict[str, Any], max_chars: int) -> Dict[str, Any]:
    out = dict(doc)
    content = out.get("content")
    if isinstance(content, str) and max_chars > 0 and len(content) > max_chars:
        out["content"] = content[:max_chars]
        out["truncated"] = True
        out["size"] = len(out["content"])
    return out


def _sources_digest(
    *,
    query: str,
    sources: List[Dict[str, Any]],
    opened: List[Dict[str, Any]],
    reason: str,
) -> str:
    lines: List[str] = []
    lines.append(
        "Synthesis failed (timeout/context/model error). Showing retrieved sources instead."
    )
    lines.append(reason)
    lines.append("")
    lines.append(f"Query: {query}")
    lines.append("")

    opened_urls: set[str] = set()
    for d in opened:
        u = d.get("url")
        if isinstance(u, str) and u:
            opened_urls.add(u)

    shown = 0
    for s in sources:
        url = s.get("url", "")
        if not isinstance(url, str) or not url:
            continue
        if opened_urls and url not in opened_urls:
            continue
        title = s.get("title", "")
        if not isinstance(title, str):
            title = str(title or "")
        snippet = s.get("snippet", "")
        if not isinstance(snippet, str):
            snippet = str(snippet or "")
        shown += 1
        lines.append(f"{shown}. {title} - {url}")
        if snippet:
            lines.append(f"   {snippet[:256]}")

    if shown == 0:
        lines.append("No sources opened.")

    return "\n".join(lines)


@dataclass
class ResearchPreset:
    """Budgets and knobs for research."""

    name: str
    max_planned_queries: int
    results_per_query: int
    max_sources_open: int
    max_source_chars: int
    recency_days: int


PRESETS: Dict[str, ResearchPreset] = {
    "quick": ResearchPreset(
        name="quick",
        max_planned_queries=2,
        results_per_query=6,
        max_sources_open=5,
        max_source_chars=6000,
        recency_days=365,
    ),
    "standard": ResearchPreset(
        name="standard",
        max_planned_queries=4,
        results_per_query=10,
        max_sources_open=10,
        max_source_chars=9000,
        recency_days=365,
    ),
    "deep": ResearchPreset(
        name="deep",
        max_planned_queries=7,
        results_per_query=15,
        max_sources_open=16,
        max_source_chars=12000,
        recency_days=365,
    ),
}


def _safe_json_from_text(text: str) -> Optional[Dict[str, Any]]:
    """Best-effort JSON extraction from raw model output."""
    s = (text or "").strip()
    if not s:
        return None

    # Direct parse
    try:
        data = json.loads(s)
        return data if isinstance(data, dict) else None
    except Exception:
        pass

    # Code block parse
    for m in _CODE_BLOCK.finditer(s):
        try:
            data = json.loads(m.group(1))
            return data if isinstance(data, dict) else None
        except Exception:
            continue

    return None


def _chat_once(
    client: OllamaClient,
    model: str,
    messages: List[Dict[str, Any]],
    options: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    """Run a single non-streaming chat call and return the response dict."""
    # OllamaClient.chat returns an iterator; for non-stream it yields exactly one object.
    out: Dict[str, Any] = {}
    for chunk in client.chat(messages, model, stream=False, options=options):
        out = chunk
    return out


def _content_from_chat_response(resp: Dict[str, Any]) -> str:
    msg = resp.get("message", {}) or {}
    return msg.get("content") or ""


def plan_research(
    client: OllamaClient,
    model: str,
    query: str,
    preset: ResearchPreset,
) -> Dict[str, Any]:
    """Stage 1: plan topics + search queries + subquestions (one model call)."""
    system = (
        "You are a research planner. Output ONLY valid JSON. "
        "Return an object with keys: topics (array of strings), search_queries (array of strings), subquestions (array of strings). "
        "Keep topics short and specific. Keep search_queries concise and keyword-focused."
    )
    user = {
        "query": query,
        "max_topics": 8,
        "max_search_queries": preset.max_planned_queries,
        "notes": (
            "Break the question into topics, then propose search queries with disambiguators (dates/roles/locations). "
            "Prefer authoritative sources."
        ),
    }
    resp = _chat_once(
        client,
        model,
        [
            {"role": "system", "content": system},
            {"role": "user", "content": json.dumps(user, ensure_ascii=False)},
        ],
        options={"temperature": 0.2},
    )
    data = _safe_json_from_text(_content_from_chat_response(resp)) or {}

    raw_topics = data.get("topics", [])
    raw_queries = data.get("search_queries", [])
    raw_subq = data.get("subquestions", [])

    topics: List[str] = []
    if isinstance(raw_topics, list):
        for t in raw_topics:
            if isinstance(t, str):
                tt = normalize_query(t)
                if tt and tt not in topics:
                    topics.append(tt)

    queries: List[str] = []
    if isinstance(raw_queries, list):
        for q in raw_queries:
            if isinstance(q, str):
                qq = normalize_query(q)
                if qq and qq not in queries:
                    queries.append(qq)

    subquestions: List[str] = []
    if isinstance(raw_subq, list):
        for sq in raw_subq:
            if isinstance(sq, str):
                ss = normalize_query(sq)
                if ss and ss not in subquestions:
                    subquestions.append(ss)

    if not queries:
        queries = [query]

    return {
        "topics": topics[:8],
        "search_queries": queries[: preset.max_planned_queries],
        "subquestions": subquestions[: max(0, preset.max_planned_queries * 2)],
    }


def plan_queries(
    client: OllamaClient,
    model: str,
    query: str,
    preset: ResearchPreset,
) -> Tuple[List[str], List[str]]:
    """Backward-compatible wrapper for older callers.

    Returns (search_queries, subquestions).
    """

    plan = plan_research(client, model, query, preset)
    raw_queries = plan.get("search_queries") or []
    raw_subq = plan.get("subquestions") or []

    queries = [str(x) for x in raw_queries if isinstance(x, str) and str(x).strip()]
    subquestions = [str(x) for x in raw_subq if isinstance(x, str) and str(x).strip()]
    return (queries, subquestions)


def assess_relevance_and_refine_queries(
    *,
    client: OllamaClient,
    model: str,
    user_query: str,
    planned_queries: List[str],
    sources: List[Dict[str, Any]],
    max_queries: int,
) -> Dict[str, Any]:
    """Ask the model to judge relevance and suggest better search queries."""

    items: List[Dict[str, Any]] = []
    for s in (sources or [])[:24]:
        url = s.get("url")
        if not isinstance(url, str) or not url:
            continue
        items.append(
            {
                "title": str(s.get("title") or "")[:200],
                "url": url[:260],
                "snippet": str(s.get("snippet") or "")[:260],
                "backend": str(s.get("backend") or "")[:40],
            }
        )

    system = (
        "You are a retrieval critic. Output ONLY valid JSON. "
        "Your job is to decide whether the SOURCES are relevant to the USER QUESTION, "
        "and if not, propose refined search queries."
    )
    user = {
        "user_question": user_query,
        "planned_queries": planned_queries,
        "sources": items,
        "max_refined_queries": max_queries,
        "output_schema": {
            "relevant": "boolean",
            "reason": "string",
            "refined_queries": "array of strings",
        },
        "rules": [
            "If sources are off-topic, set relevant=false.",
            "If relevant=true but evidence seems weak, keep refined_queries empty.",
            "Refined queries must be short and keyword-focused; include disambiguators when needed.",
            "Return at most max_refined_queries.",
        ],
    }
    resp = _chat_once(
        client,
        model,
        [
            {"role": "system", "content": system},
            {"role": "user", "content": json.dumps(user, ensure_ascii=False)},
        ],
        options={"temperature": 0.2},
    )
    data = _safe_json_from_text(_content_from_chat_response(resp)) or {}

    relevant = bool(data.get("relevant"))
    reason = str(data.get("reason") or "")[:800]
    refined: List[str] = []
    raw_refined = data.get("refined_queries")
    if isinstance(raw_refined, list):
        for q in raw_refined:
            if not isinstance(q, str):
                continue
            qq = normalize_query(q)
            if qq and qq not in refined:
                refined.append(qq)

    return {
        "relevant": relevant,
        "reason": reason,
        "refined_queries": refined[:max_queries],
    }


def verify_claims_from_opened_sources(
    *,
    client: OllamaClient,
    model: str,
    user_query: str,
    sources: List[Dict[str, Any]],
    opened: List[Dict[str, Any]],
    max_claims: int = 30,
    max_content_chars: int = 2500,
) -> Dict[str, Any]:
    """Optional deep step: extract supported claims with evidence quotes."""

    docs: List[Dict[str, Any]] = []
    for i, (s, d) in enumerate(zip(sources, opened), start=1):
        content = d.get("content")
        if not isinstance(content, str):
            content = ""
        docs.append(
            {
                "id": i,
                "title": str(s.get("title") or "")[:200],
                "url": str(s.get("url") or "")[:260],
                "snippet": str(s.get("snippet") or "")[:260],
                "content": content[:max_content_chars],
            }
        )

    system = (
        "You are a verifier. Output ONLY valid JSON. "
        "Use ONLY the provided documents. Do not guess. "
        "Citations must be integers that refer to document ids."
    )
    user = {
        "question": user_query,
        "documents": docs,
        "max_claims": max_claims,
        "schema": {
            "claims": [
                {
                    "claim": "string",
                    "status": "supported|unclear|refuted",
                    "citations": [1],
                    "evidence": [{"citation": 1, "quote": "exact quote"}],
                    "notes": "string",
                }
            ]
        },
        "rules": [
            "For status=supported, include at least one evidence quote that is an exact substring of a cited document's content.",
            "If you cannot find exact support, mark unclear.",
        ],
    }

    resp = _chat_once(
        client,
        model,
        [
            {"role": "system", "content": system},
            {"role": "user", "content": json.dumps(user, ensure_ascii=False)},
        ],
        options={"temperature": 0.1},
    )
    data = _safe_json_from_text(_content_from_chat_response(resp)) or {}
    claims = data.get("claims")
    if not isinstance(claims, list):
        claims = []
    return {"claims": claims[:max_claims]}


def gap_check_and_refine_queries(
    *,
    client: OllamaClient,
    model: str,
    user_query: str,
    topics: List[str],
    subquestions: List[str],
    verified_claims: List[Dict[str, Any]],
    max_refined_queries: int,
) -> Dict[str, Any]:
    """Deep-only: decide if we covered topics; propose refined search queries."""

    t = [
        normalize_query(x)
        for x in (topics or [])
        if isinstance(x, str) and normalize_query(x)
    ][:10]
    sq = [
        normalize_query(x)
        for x in (subquestions or [])
        if isinstance(x, str) and normalize_query(x)
    ][:10]

    claims: List[Dict[str, Any]] = []
    for c in (verified_claims or [])[:24]:
        if not isinstance(c, dict):
            continue
        if str(c.get("status") or "").strip().lower() != "supported":
            continue
        claims.append(
            {
                "claim": str(c.get("claim") or "")[:500],
                "citations": c.get("citations")
                if isinstance(c.get("citations"), list)
                else [],
                "evidence": c.get("evidence")
                if isinstance(c.get("evidence"), list)
                else [],
            }
        )

    system = (
        "You are a research gap checker. Output ONLY valid JSON. "
        "Decide if supported claims cover the topics/subquestions; if not, propose refined search queries."
    )
    user = {
        "question": user_query,
        "topics": t,
        "subquestions": sq,
        "supported_claims": claims,
        "max_refined_queries": max_refined_queries,
        "schema": {"done": "boolean", "reason": "string", "refined_queries": ["..."]},
        "rules": [
            "Base your decision ONLY on supported_claims.",
            "If not done, propose refined_queries that are short and keyword-focused; add disambiguators.",
            "Return at most max_refined_queries refined_queries.",
        ],
    }

    resp = _chat_once(
        client,
        model,
        [
            {"role": "system", "content": system},
            {"role": "user", "content": json.dumps(user, ensure_ascii=False)},
        ],
        options={"temperature": 0.1},
    )
    data = _safe_json_from_text(_content_from_chat_response(resp)) or {}
    done = bool(data.get("done"))
    reason = str(data.get("reason") or "")[:800]

    refined: List[str] = []
    raw = data.get("refined_queries")
    if isinstance(raw, list):
        for q in raw:
            if not isinstance(q, str):
                continue
            qq = normalize_query(q)
            if qq and qq not in refined:
                refined.append(qq)

    return {
        "done": done,
        "reason": reason,
        "refined_queries": refined[:max_refined_queries],
    }


def run_deep_research(
    *,
    client: OllamaClient,
    model: str,
    query: str,
    preset_name: str = "standard",
    seed_urls: Optional[List[str]] = None,
    searxng_url: Optional[str] = None,
    kiwix_url: Optional[str] = None,
) -> str:
    """Run a bounded deep research pass and return a cited report."""
    raw_query = query
    query = normalize_query(query)
    if not query:
        query = (raw_query or "").strip()

    preset = PRESETS.get(preset_name, PRESETS["standard"])
    web = WebTools(searxng_url=searxng_url or DEFAULT_SEARXNG_URL)

    kiwix: Optional[KiwixTools] = None
    offline_zims: List[str] = []
    if kiwix_url:
        kt = KiwixTools(kiwix_url=kiwix_url)
        if kt.ping():
            kiwix = kt

    started_at = time.time()
    plan = plan_research(client, model, query, preset)
    topics = plan.get("topics") or []
    planned_queries = plan.get("search_queries") or []
    subquestions = plan.get("subquestions") or []

    max_attempts = MAX_SOURCE_QUERY_ATTEMPTS if preset.name == "deep" else 1

    for attempt in range(1, max_attempts + 1):
        q_tokens = _query_tokens(query)

        # Pick offline books (ZIM ids) to search.
        offline_zims = []
        if kiwix and not seed_urls:
            max_offline_zims = (
                2 if preset.name == "quick" else (4 if preset.name == "standard" else 6)
            )

            terms: List[str] = []
            terms.append(query)
            terms.extend(planned_queries)
            for token in re.findall(r"[A-Za-z0-9]{4,}", query.lower()):
                if token not in terms:
                    terms.append(token)
            terms.insert(0, "wikipedia")

            scores: Dict[str, int] = {}
            for t in terms[:8]:
                try:
                    books = kiwix.catalog_search_books(t, count=12)
                except Exception:
                    continue
                for b in books:
                    zim_id = str(b.get("zim_id") or "").strip()
                    if not zim_id:
                        continue
                    title = str(b.get("title") or "").lower()
                    inc = 1
                    if "wikipedia" in zim_id.lower() or "wikipedia" in title:
                        inc += 3
                    if t.lower() in title:
                        inc += 2
                    scores[zim_id] = scores.get(zim_id, 0) + inc

            offline_zims = [
                z for z, _ in sorted(scores.items(), key=lambda kv: (-kv[1], kv[0]))
            ][:max_offline_zims]

        _progress(
            f"Source query attempt {attempt}/{max_attempts}: "
            + ", ".join(planned_queries[: min(3, len(planned_queries))])
        )

        urls: List[str] = []
        sources: List[Dict[str, Any]] = []

        if kiwix and not seed_urls:
            for q in planned_queries:
                try:
                    rows = kiwix.search_rss(
                        q, zim=None, count=preset.results_per_query, start=0
                    )
                except Exception:
                    rows = []

                for row in rows:
                    zim = str(row.get("zim") or "").strip()
                    path = str(row.get("path") or "").strip()
                    title = str(row.get("title") or "").strip()
                    snippet = str(row.get("snippet") or "").strip()
                    if not zim or not path or not title:
                        continue

                    safe_path = quote(path.lstrip("/"), safe="/-._~")
                    u = f"{kiwix.kiwix_url}/content/{zim}/{safe_path}"
                    if u not in urls:
                        urls.append(u)
                        sources.append(
                            {
                                "title": title,
                                "url": u,
                                "snippet": snippet,
                                "backend": "kiwix",
                                "zim": zim,
                                "path": path,
                            }
                        )
                    if len(urls) >= preset.max_sources_open:
                        break
                if len(urls) >= preset.max_sources_open:
                    break

            if not urls and offline_zims:
                per_zim = max(
                    2, min(6, preset.results_per_query // max(1, len(offline_zims)))
                )
                for q in planned_queries:
                    for zim in offline_zims:
                        try:
                            offline = kiwix.search_xml(q, zim, count=per_zim, start=0)
                        except Exception:
                            offline = []
                        for r in offline:
                            if not r.url:
                                continue
                            safe_path = quote(r.url.lstrip("/"), safe="/-._~")
                            u = f"{kiwix.kiwix_url}/content/{zim}/{safe_path}"
                            if u not in urls:
                                urls.append(u)
                                sources.append(
                                    {
                                        "title": r.title,
                                        "url": u,
                                        "snippet": r.snippet,
                                        "backend": "kiwix",
                                        "zim": zim,
                                        "path": r.url,
                                    }
                                )
                        if len(urls) >= preset.max_sources_open:
                            break
                    if len(urls) >= preset.max_sources_open:
                        break

        if seed_urls:
            for u in seed_urls:
                u = (u or "").strip()
                if u and u not in urls:
                    urls.append(u)
                    sources.append(
                        {"title": u, "url": u, "snippet": "", "backend": "seed"}
                    )
        else:
            if len(urls) < preset.max_sources_open:
                for q in planned_queries:
                    results = web.search(
                        q,
                        count=preset.results_per_query,
                        recency_days=preset.recency_days,
                    )
                    for r in results:
                        if r.url and r.url not in urls:
                            urls.append(r.url)
                            sources.append(
                                {
                                    "title": r.title,
                                    "url": r.url,
                                    "snippet": r.snippet,
                                    "backend": "web",
                                }
                            )
                    if len(urls) >= preset.max_sources_open:
                        break

        if sources:
            offline_sources = [s for s in sources if s.get("backend") == "kiwix"]
            web_sources = [s for s in sources if s.get("backend") != "kiwix"]

            def _score(s: Dict[str, Any]) -> int:
                return _keyword_overlap_score(
                    q_tokens,
                    str(s.get("title") or ""),
                    str(s.get("snippet") or ""),
                )

            offline_sources.sort(key=lambda s: (-_score(s), str(s.get("title") or "")))
            web_sources.sort(key=lambda s: (-_score(s), str(s.get("title") or "")))
            sources = offline_sources + web_sources
            urls = [str(s.get("url") or "") for s in sources if s.get("url")]

        opened: List[Dict[str, Any]] = []
        for u in urls[: preset.max_sources_open]:
            if kiwix and u.startswith(f"{kiwix.kiwix_url}/content/"):
                try:
                    rest = u.split(f"{kiwix.kiwix_url}/content/", 1)[1]
                    parts = rest.split("/", 1)
                    if len(parts) == 2:
                        zim = parts[0]
                        path = unquote(parts[1])
                        raw = kiwix.open_raw(
                            zim, path, max_chars=preset.max_source_chars
                        )
                        opened.append(raw)
                        continue
                except Exception:
                    pass

            try:
                opened_doc = web.open_url(
                    u, mode="auto", max_chars=preset.max_source_chars
                )
            except Exception:
                continue
            opened.append(opened_doc)

        if not opened:
            if attempt < max_attempts:
                continue
            raise RuntimeError(
                "No sources could be fetched/opened. "
                "If using web search, verify your SearxNG instance and SEARXNG_URL. "
                "Alternatively, provide seed URLs."
            )

        source_by_url: Dict[str, Dict[str, Any]] = {}
        for s in sources:
            src_url = s.get("url")
            if isinstance(src_url, str) and src_url and src_url not in source_by_url:
                source_by_url[src_url] = s

        opened_sources: List[Dict[str, Any]] = []
        opened_ordered: List[Dict[str, Any]] = []
        for d in opened:
            opened_url = d.get("url")
            if not isinstance(opened_url, str) or not opened_url:
                continue
            opened_ordered.append(d)
            opened_sources.append(
                source_by_url.get(
                    opened_url, {"title": opened_url, "url": opened_url, "snippet": ""}
                )
            )
        opened = opened_ordered

        if preset.name == "deep":
            assess = assess_relevance_and_refine_queries(
                client=client,
                model=model,
                user_query=query,
                planned_queries=planned_queries,
                sources=opened_sources,
                max_queries=preset.max_planned_queries,
            )
            if not bool(assess.get("relevant")) and attempt < max_attempts:
                refined = assess.get("refined_queries") or []
                if isinstance(refined, list):
                    refined_list = [
                        normalize_query(str(x)) for x in refined if str(x).strip()
                    ]
                else:
                    refined_list = []

                if refined_list:
                    planned_queries = refined_list[: preset.max_planned_queries]
                else:
                    planned_queries = [query]
                _progress(
                    f"Sources look off-topic; refining queries: {assess.get('reason', '')}"
                )
                continue

        offline_opened = sum(1 for s in opened_sources if s.get("backend") == "kiwix")
        web_opened = sum(1 for s in opened_sources if s.get("backend") != "kiwix")
        if offline_opened and not web_opened:
            _progress(
                f"Found {offline_opened} offline sources (Kiwix). Synthesizing..."
            )
        elif offline_opened:
            _progress(
                f"Found {offline_opened} offline sources (Kiwix) and {web_opened} web sources. Synthesizing..."
            )
        else:
            _progress(f"Found {len(opened_sources)} sources. Synthesizing...")

        # Build report prompt
        packet = {
            "query": query,
            "topics": topics,
            "subquestions": subquestions,
            "planned_queries": planned_queries,
            "sources": opened_sources,
            "opened": opened,
            "elapsed_s": round(time.time() - started_at, 2),
            "instructions": {
                "citation_style": "Use inline bracket citations like [1], [2] referencing the numbered Sources list you include at the end.",
                "be_explicit_about_uncertainty": True,
                "prefer_primary_sources": True,
            },
        }

        if preset.name == "deep":
            verified = verify_claims_from_opened_sources(
                client=client,
                model=model,
                user_query=query,
                sources=opened_sources,
                opened=opened,
            )
            verified_claims = verified.get("claims") or []
            packet["verified_claims"] = verified_claims

            gap = gap_check_and_refine_queries(
                client=client,
                model=model,
                user_query=query,
                topics=topics,
                subquestions=subquestions,
                verified_claims=verified_claims
                if isinstance(verified_claims, list)
                else [],
                max_refined_queries=preset.max_planned_queries,
            )
            if not bool(gap.get("done")) and attempt < max_attempts:
                refined = gap.get("refined_queries") or []
                if isinstance(refined, list) and refined:
                    planned_queries = [
                        normalize_query(str(x)) for x in refined if str(x).strip()
                    ][: preset.max_planned_queries]
                else:
                    planned_queries = [query]
                _progress(f"Gap check suggests more research: {gap.get('reason', '')}")
                continue

        if preset.name == "deep":
            system = (
                "You are a deep research assistant. Write a thorough, high-signal report with citations. "
                "Use ONLY the provided sources (do not rely on prior knowledge). "
                "Only assert claims that are supported by the provided verified_claims. "
                "Every factual claim must have an inline numeric citation like [1] that matches the numbered Sources list at the end. "
                "Do not use any other citation labels (no [A1], [W3], etc). "
                "If the sources do not support a claim, say you don't know. "
                "Format:\n"
                "## Executive Summary\n- 7-12 bullets\n\n"
                "## Concepts And Definitions\n\n"
                "## Detailed Analysis\n(use short subsections)\n\n"
                "## Practical Guidance\n(checklist)\n\n"
                "## Uncertainties / Gaps\n"
                "End with a 'Sources' section listing numbered sources with title and URL."
            )
        else:
            system = (
                "You are a research assistant. Write a concise answer with citations. "
                "Use ONLY the provided sources (do not rely on prior knowledge). "
                "Every factual claim must have an inline numeric citation like [1] that matches the numbered Sources list at the end. "
                "If the sources do not support a claim, say you don't know. "
                "Format:\n"
                "## Answer\n(2-6 short paragraphs)\n\n"
                "## Key Points\n- 5-9 bullets\n\n"
                "## Uncertainties / Gaps\n"
                "End with a 'Sources' section listing numbered sources with title and URL."
            )

        def _synthesize(pkt: Dict[str, Any], temperature: float) -> str:
            msgs = [
                {"role": "system", "content": system},
                {"role": "user", "content": json.dumps(pkt, ensure_ascii=False)},
            ]
            resp = _chat_once(client, model, msgs, options={"temperature": temperature})
            text = _content_from_chat_response(resp).strip()
            if not text:
                raise RuntimeError("empty model response")
            return text

        try:
            return _synthesize(packet, temperature=0.3)
        except Exception as e1:
            _progress(
                f"Synthesis failed: {type(e1).__name__}: {e1}. Retrying with smaller context..."
            )

            retry_max_sources_open = min(4, max(2, len(opened_sources) // 2))
            retry_max_source_chars = min(3000, preset.max_source_chars)

            ranked: List[Tuple[int, int, Dict[str, Any], Dict[str, Any]]] = []
            for i, (s, d) in enumerate(zip(opened_sources, opened)):
                score = _keyword_overlap_score(
                    q_tokens, str(s.get("title") or ""), str(s.get("snippet") or "")
                )
                ranked.append((score, -i, s, d))
            ranked.sort(key=lambda t: (-t[0], -t[1]))

            small_sources: List[Dict[str, Any]] = []
            small_opened: List[Dict[str, Any]] = []
            for _, _, s, d in ranked[:retry_max_sources_open]:
                small_sources.append(s)
                small_opened.append(
                    _shrink_opened_doc(d, max_chars=retry_max_source_chars)
                )

            packet_small = dict(packet)
            packet_small["opened"] = small_opened
            packet_small["sources"] = small_sources
            q_obj = packet_small.get("query")
            q_str = q_obj if isinstance(q_obj, str) else ""
            packet_small["query"] = normalize_query(q_str)

            try:
                return _synthesize(packet_small, temperature=0.2)
            except Exception as e2:
                _progress(
                    f"Synthesis failed again: {type(e2).__name__}: {e2}. Showing sources list."
                )
                reason = (
                    f"Primary error: {type(e1).__name__}: {e1} | "
                    f"Retry error: {type(e2).__name__}: {e2}"
                )
                return _sources_digest(
                    query=query, sources=opened_sources, opened=opened, reason=reason
                )

    raise RuntimeError("research loop ended unexpectedly")
