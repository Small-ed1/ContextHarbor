from __future__ import annotations

import asyncio
import json
import re
import time
from contextvars import ContextVar
from typing import Any, cast

import httpx

from .context import build_context
from .evidence import (
    evidence_ok,
    extract_citation_tags,
    heuristic_doc_genre,
    infer_evidence_policy,
    infer_epub_intent,
    kiwix_zim_id,
    trust_tier_for,
)
from .retrieval import (
    DocRetrievalProvider,
    WebRetrievalProvider,
    KiwixRetrievalProvider,
    RetrievalResult,
)
from .rerank import rerank_results
from .tooling import (
    ToolDocSearchReq,
    ToolKiwixSearchReq,
    ToolWebSearchReq,
    tool_definitions,
    tool_doc_search,
    tool_kiwix_search,
    tool_web_search,
)
from .web_ingest import WebIngestQueue
from .web_search import web_search_with_fallback, SearchError
from ..stores import researchstore, webstore
from .. import config


MAX_SOURCE_REFINEMENTS = 3
MAX_GAP_CHECKS = 2

# Agentic deep research budgets
MAX_DEEP_TOOL_CALLS = 100

MAX_TOOL_CALLS_PER_STEP = 6
MAX_TOOL_PLANNING_STEPS = 30


_CITATION_TOKEN = re.compile(r"\[([A-Z]\d+)\]")
_NUMERIC_CITATION_TOKEN = re.compile(r"\[(\d{1,4})\]")
_REFS_HEADING = re.compile(
    r"(?im)^\s*(references|bibliography|works\s+cited)\s*:?[ \t]*$"
)


_RUN_MIN_END_AT: ContextVar[float | None] = ContextVar(
    "contextharbor_research_min_end_at", default=None
)


_DUR_FLAG = re.compile(r"^--?(\d+(?:\.\d+)?)(s|m|h|d|mo)$", re.IGNORECASE)


def _parse_time_budget_sec(val: Any) -> float | None:
    if val is None:
        return None
    if isinstance(val, (int, float)):
        sec = float(val)
        return sec if sec > 0 else None

    s = str(val or "").strip()
    if not s:
        return None

    m = _DUR_FLAG.match(s)
    if not m:
        return None

    try:
        n = float(m.group(1))
    except Exception:
        return None

    unit = str(m.group(2) or "").strip().lower()
    if n <= 0:
        return None

    mult = 1.0
    if unit == "s":
        mult = 1.0
    elif unit == "m":
        mult = 60.0
    elif unit == "h":
        mult = 3600.0
    elif unit == "d":
        mult = 86400.0
    elif unit == "mo":
        mult = 30.0 * 86400.0
    else:
        return None

    return n * mult


def _min_time_is_set() -> bool:
    return _RUN_MIN_END_AT.get() is not None


def _min_time_remaining_sec() -> float | None:
    end_at = _RUN_MIN_END_AT.get()
    if end_at is None:
        return None
    return float(end_at - time.time())


def _min_time_satisfied() -> bool:
    rem = _min_time_remaining_sec()
    return rem is None or rem <= 0


def _looks_like_stem_query(q: str) -> bool:
    s = (q or "").strip().lower()
    if not s:
        return False
    needles = (
        "superconduct",
        "physics",
        "chemistry",
        "biolog",
        "materials",
        "thermodynamics",
        "meissner",
        "bcs",
        "electron",
        "quantum",
        "band gap",
        "lattice",
        "pressure",
        "ambient pressure",
        "critical temperature",
        "tc",
    )
    return any(n in s for n in needles)


def _looks_like_empirical_stats_query(q: str) -> bool:
    s = (q or "").strip().lower()
    if not s:
        return False
    needles = (
        "ratio",
        "rate",
        "percent",
        "%",
        "how many",
        "number of",
        "deaths",
        "injuries",
        "fatalities",
        "statistics",
        "statistic",
        "per capita",
        "per 100",
        "per 1,000",
        "per 1000",
        "dataset",
        "incidence",
        "prevalence",
    )
    return any(n in s for n in needles)


async def _ollama_chat_once(
    http: httpx.AsyncClient,
    base_url: str,
    model: str,
    messages: list[dict],
    timeout: float = 60.0,
) -> str:
    payload = {"model": model, "messages": messages, "stream": False}
    r = await http.post(f"{base_url}/api/chat", json=payload, timeout=float(timeout))
    r.raise_for_status()
    return ((r.json().get("message") or {}).get("content") or "").strip()


async def _ollama_chat_message_once(
    http: httpx.AsyncClient,
    base_url: str,
    model: str,
    messages: list[dict],
    *,
    tools: list[dict[str, Any]] | None = None,
    options: dict[str, Any] | None = None,
    keep_alive: str | None = None,
    timeout: float = 60.0,
) -> dict[str, Any]:
    payload: dict[str, Any] = {"model": model, "messages": messages, "stream": False}
    if tools:
        payload["tools"] = tools
    if options is not None:
        payload["options"] = options
    if keep_alive is not None:
        payload["keep_alive"] = keep_alive
    r = await http.post(f"{base_url}/api/chat", json=payload, timeout=float(timeout))
    r.raise_for_status()
    msg_any = r.json().get("message") or {}
    return msg_any if isinstance(msg_any, dict) else {}


async def _plan_queries(
    http: httpx.AsyncClient, base_url: str, planner_model: str, query: str
) -> dict:
    prompt = (
        "Return ONLY JSON.\n"
        "{"
        '"topics":[...],'
        '"subquestions":[...],'
        '"web_queries":[...],'
        '"doc_queries":[...],'
        '"done_if":[...]\n'
        "}\n\n"
        "Guidance:\n"
        "- topics: 3-8 short topic labels that break down the question.\n"
        "- queries: keyword-focused; include disambiguators (dates/roles/locations).\n\n"
        f"User query:\n{query}\n"
    )
    out = await _ollama_chat_once(
        http,
        base_url,
        planner_model,
        [{"role": "user", "content": prompt}],
        timeout=45.0,
    )
    obj = cast(dict, _json_obj_from_text(out) or {})
    topics = obj.get("topics")
    subquestions = obj.get("subquestions")
    web_queries = obj.get("web_queries")
    doc_queries = obj.get("doc_queries")
    done_if = obj.get("done_if")
    tp = topics if isinstance(topics, list) else []
    sq = subquestions if isinstance(subquestions, list) else []
    wq = web_queries if isinstance(web_queries, list) else []
    dq = doc_queries if isinstance(doc_queries, list) else []
    di = done_if if isinstance(done_if, list) else []
    return {
        "topics": [str(x) for x in tp if str(x).strip()][:12],
        "subquestions": sq[:10],
        "web_queries": wq[:12],
        "doc_queries": dq[:12],
        "done_if": [str(x) for x in di if str(x).strip()][:10],
        "raw": out,
    }


async def _deep_research_question_profile(
    http: httpx.AsyncClient,
    base_url: str,
    model: str,
    *,
    query: str,
    plan: dict[str, Any],
) -> dict[str, Any]:
    """Classify research intent to tighten evidence constraints.

    This is used to harden the pipeline against empirical-stat hallucinations.
    """

    packet = {
        "query": query,
        "topics": plan.get("topics") or [],
        "subquestions": plan.get("subquestions") or [],
    }
    prompt = (
        "Return ONLY JSON.\n"
        "Schema:\n"
        "{\n"
        '  "question_type": "empirical_stats|general_factual|creative|other",\n'
        '  "force_evidence_policy": "strict|relaxed|default",\n'
        '  "force_epub_context_only": true|false,\n'
        '  "require_evidence": true|false,\n'
        '  "reason": "..."\n'
        "}\n\n"
        "Guidance:\n"
        "- empirical_stats: asks for counts/ratios/rates/percentages or dataset-backed claims.\n"
        "- For empirical_stats, set force_evidence_policy=strict, force_epub_context_only=true, require_evidence=true.\n"
        "- creative: story/poem/novel-type requests.\n\n"
        f"INPUT:\n{json.dumps(packet, ensure_ascii=False)}\n"
    )
    out = await _ollama_chat_once(
        http, base_url, model, [{"role": "user", "content": prompt}], timeout=25.0
    )
    obj_any = _json_obj_from_text(out) or {}
    obj = obj_any if isinstance(obj_any, dict) else {}
    qt = str(obj.get("question_type") or "").strip().lower()
    if qt not in {"empirical_stats", "general_factual", "creative", "other"}:
        qt = "general_factual"
    fep = str(obj.get("force_evidence_policy") or "").strip().lower()
    if fep not in {"strict", "relaxed", "default"}:
        fep = "default"
    return {
        "question_type": qt,
        "force_evidence_policy": fep,
        "force_epub_context_only": bool(obj.get("force_epub_context_only")),
        "require_evidence": bool(obj.get("require_evidence")),
        "reason": str(obj.get("reason") or "")[:800],
        "raw": out,
    }


async def _check_done_if(
    http: httpx.AsyncClient,
    base_url: str,
    model: str,
    *,
    query: str,
    done_if: list[str],
    supported_claims: list[dict[str, Any]],
) -> dict[str, Any]:
    criteria = [str(x).strip() for x in (done_if or []) if str(x).strip()]
    if not criteria:
        return {"done": False, "reason": "no criteria"}

    claims = [
        {
            "claim": str(c.get("claim") or "")[:600],
            "citations": c.get("citations")
            if isinstance(c.get("citations"), list)
            else [],
        }
        for c in (supported_claims or [])
        if isinstance(c, dict) and (c.get("status") == "supported")
    ]

    prompt = (
        'Return ONLY JSON: {"done": true|false, "reason": "..."}.\n\n'
        "Decide whether the research is complete for the user's question.\n\n"
        "User question:\n"
        f"{query}\n\n"
        "Completion criteria (done_if):\n- " + "\n- ".join(criteria) + "\n\n"
        "Supported claims (evidence-backed):\n" + json.dumps(claims, ensure_ascii=False)
    )

    out = await _ollama_chat_once(
        http, base_url, model, [{"role": "user", "content": prompt}], timeout=30.0
    )
    obj = _json_obj_from_text(out) or {}
    done = bool(obj.get("done")) if isinstance(obj, dict) else False
    reason = str(obj.get("reason") or "").strip() if isinstance(obj, dict) else ""
    return {"done": done, "reason": reason[:800], "raw": out}


async def _assess_sources_relevance_and_refine_queries(
    http: httpx.AsyncClient,
    base_url: str,
    model: str,
    *,
    query: str,
    sources_meta: list[dict[str, Any]],
    use_docs: bool,
    use_web: bool,
    kiwix_enabled: bool,
) -> dict[str, Any]:
    """Ask the model to judge relevance and propose refined queries.

    Returns dict with keys:
      - relevant: bool
      - reason: str
      - doc_queries: list[str]
      - web_queries: list[str]
      - kiwix_query: str | None
    """

    # Keep the prompt compact and stable.
    items = []
    for s in (sources_meta or [])[:24]:
        if not isinstance(s, dict):
            continue
        st = str(s.get("source_type") or "")
        title = str(s.get("title") or "")
        domain = str(s.get("domain") or "")
        url = str(s.get("url") or "")
        snippet = str(s.get("snippet") or "")
        items.append(
            {
                "source_type": st,
                "title": title[:180],
                "domain": domain[:120],
                "url": url[:240],
                "snippet": snippet[:260],
            }
        )

    prompt = (
        "Return ONLY JSON.\n"
        "Schema:\n"
        "{\n"
        '  "relevant": true|false,\n'
        '  "reason": "...",\n'
        '  "doc_queries": ["..."],\n'
        '  "web_queries": ["..."],\n'
        '  "kiwix_query": "..."|null\n'
        "}\n\n"
        "Task:\n"
        "1) Decide whether the provided SOURCES are relevant to the USER QUESTION.\n"
        "2) If irrelevant or insufficient, propose refined queries that are more likely to retrieve relevant sources.\n\n"
        "Guidance:\n"
        "- Keep queries short and keyword-focused (names, dates, roles, disambiguators).\n"
        "- Provide at most 4 doc_queries and 4 web_queries.\n"
        "- If a source type is disabled, still return an empty list for that field.\n"
        "- If the question is general-knowledge and only local books are available, prefer kiwix_query when enabled.\n\n"
        f"Enabled sources: docs={str(bool(use_docs)).lower()}, web={str(bool(use_web)).lower()}, kiwix={str(bool(kiwix_enabled)).lower()}\n\n"
        f"USER QUESTION:\n{query}\n\n"
        f"SOURCES (metadata + snippet):\n{json.dumps(items, ensure_ascii=False)}\n"
    )

    out = await _ollama_chat_once(
        http, base_url, model, [{"role": "user", "content": prompt}], timeout=25.0
    )
    obj = _json_obj_from_text(out) or {}
    if not isinstance(obj, dict):
        return {
            "relevant": True,
            "reason": "",
            "doc_queries": [],
            "web_queries": [],
            "kiwix_query": None,
            "raw": out,
        }

    relevant = bool(obj.get("relevant"))
    reason = str(obj.get("reason") or "").strip()[:800]

    dq_any = obj.get("doc_queries")
    wq_any = obj.get("web_queries")
    kq_any = obj.get("kiwix_query")

    dq = (
        [str(x).strip() for x in (dq_any or []) if str(x).strip()]
        if isinstance(dq_any, list)
        else []
    )
    wq = (
        [str(x).strip() for x in (wq_any or []) if str(x).strip()]
        if isinstance(wq_any, list)
        else []
    )

    kq: str | None = None
    if isinstance(kq_any, str):
        kq = kq_any.strip() or None
    elif kq_any is None:
        kq = None

    if not use_docs:
        dq = []
    if not use_web:
        wq = []
    if not kiwix_enabled:
        kq = None

    return {
        "relevant": relevant,
        "reason": reason,
        "doc_queries": dq[:4],
        "web_queries": wq[:4],
        "kiwix_query": kq,
        "raw": out,
    }


async def _gap_check_and_refine_queries(
    http: httpx.AsyncClient,
    base_url: str,
    model: str,
    *,
    query: str,
    topics: list[str],
    subquestions: list[str],
    supported_claims: list[dict[str, Any]],
    use_docs: bool,
    use_web: bool,
    kiwix_enabled: bool,
) -> dict[str, Any]:
    """Ask the model whether remaining gaps exist, and propose follow-up queries.

    Returns dict with keys:
      - done: bool
      - reason: str
      - doc_queries: list[str]
      - web_queries: list[str]
      - kiwix_query: str | None
    """

    t = [str(x).strip() for x in (topics or []) if str(x).strip()][:10]
    sq = [str(x).strip() for x in (subquestions or []) if str(x).strip()][:10]
    claims = []
    for c in (supported_claims or [])[:24]:
        if not isinstance(c, dict):
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

    prompt = (
        "Return ONLY JSON.\n"
        "Schema:\n"
        "{\n"
        '  "done": true|false,\n'
        '  "reason": "...",\n'
        '  "missing_topics": ["..."],\n'
        '  "doc_queries": ["..."],\n'
        '  "web_queries": ["..."],\n'
        '  "kiwix_query": "..."|null\n'
        "}\n\n"
        "Task:\n"
        "Decide whether the supported evidence fully answers the user question across the requested topics/subquestions. "
        "If not done, propose follow-up queries to fill the missing gaps.\n\n"
        "Guidance:\n"
        "- Base your decision ONLY on the supported_claims; do not guess.\n"
        "- Keep queries short and keyword-focused; add disambiguators.\n"
        "- Provide at most 4 doc_queries and 4 web_queries.\n\n"
        f"Enabled sources: docs={str(bool(use_docs)).lower()}, web={str(bool(use_web)).lower()}, kiwix={str(bool(kiwix_enabled)).lower()}\n\n"
        f"USER QUESTION:\n{query}\n\n"
        f"TOPICS:\n{json.dumps(t, ensure_ascii=False)}\n\n"
        f"SUBQUESTIONS:\n{json.dumps(sq, ensure_ascii=False)}\n\n"
        f"SUPPORTED_CLAIMS:\n{json.dumps(claims, ensure_ascii=False)}\n"
    )

    out = await _ollama_chat_once(
        http, base_url, model, [{"role": "user", "content": prompt}], timeout=30.0
    )
    obj = _json_obj_from_text(out) or {}
    if not isinstance(obj, dict):
        return {
            "done": True,
            "reason": "",
            "doc_queries": [],
            "web_queries": [],
            "kiwix_query": None,
            "raw": out,
        }

    done = bool(obj.get("done"))
    reason = str(obj.get("reason") or "").strip()[:800]

    dq_any = obj.get("doc_queries")
    wq_any = obj.get("web_queries")
    kq_any = obj.get("kiwix_query")

    dq = (
        [str(x).strip() for x in (dq_any or []) if str(x).strip()]
        if isinstance(dq_any, list)
        else []
    )
    wq = (
        [str(x).strip() for x in (wq_any or []) if str(x).strip()]
        if isinstance(wq_any, list)
        else []
    )

    kq: str | None = None
    if isinstance(kq_any, str):
        kq = kq_any.strip() or None
    elif kq_any is None:
        kq = None

    if not use_docs:
        dq = []
    if not use_web:
        wq = []
    if not kiwix_enabled:
        kq = None

    return {
        "done": done,
        "reason": reason,
        "doc_queries": dq[:4],
        "web_queries": wq[:4],
        "kiwix_query": kq,
        "raw": out,
    }


def _json_obj_from_text(
    s: str, max_size: int = config.config.max_json_parse_size
) -> Any:
    s = s or ""
    if not s or len(s) > max_size:
        return None

    for i, ch in enumerate(s):
        if ch == "{":
            depth = 0
            in_string = False
            escape_next = False

            for j in range(i, min(len(s), i + max_size)):
                c = s[j]
                if escape_next:
                    escape_next = False
                elif c == "\\":
                    escape_next = True
                elif c == '"':
                    in_string = not in_string
                elif not in_string:
                    if c == "{":
                        depth += 1
                    elif c == "}":
                        depth -= 1
                        if depth == 0:
                            json_str = s[i : j + 1]
                            try:
                                return json.loads(json_str)
                            except json.JSONDecodeError:
                                break
            break
    return None


def _context_by_tag(context_lines: list[str]) -> dict[str, str]:
    by: dict[str, list[str]] = {}
    for ln in context_lines or []:
        s = str(ln or "")
        if not s.startswith("["):
            continue
        rb = s.find("]")
        if rb <= 1:
            continue
        tag = s[1:rb].strip()
        if not tag:
            continue
        by.setdefault(tag, []).append(s[rb + 1 :].lstrip())
    return {k: "\n".join(v) for k, v in by.items()}


_WS_RE = re.compile(r"\s+")


def _norm_quote(s: str) -> str:
    # Normalize for robust substring checks across newlines/spacing.
    # Keep it conservative: do not drop words or reorder; just casefold + whitespace.
    t = s or ""
    t = t.replace("\u201c", '"').replace("\u201d", '"').replace("\u201e", '"')
    t = t.replace("\u2018", "'").replace("\u2019", "'")
    t = t.replace("\u2013", "-").replace("\u2014", "-")
    t = t.replace("\u2026", "...")
    t = t.casefold()
    t = _WS_RE.sub(" ", t).strip()
    return t


def _quote_in_haystack(*, quote: str, hay: str) -> bool:
    q0 = (quote or "").strip()
    if not q0:
        return False
    if q0 in (hay or ""):
        return True

    q = _norm_quote(q0)
    h = _norm_quote(hay or "")
    if len(q) < 24:
        return False

    if q in h:
        return True

    # Allow contiguous spans with ellipses: all segments must appear in-order.
    if "..." in q:
        parts = [p.strip() for p in q.split("...") if p.strip()]
        if not parts:
            return False
        pos = 0
        for p in parts:
            idx = h.find(p, pos)
            if idx < 0:
                return False
            pos = idx + len(p)
        return True

    return False


async def _verify_claims(
    http: httpx.AsyncClient,
    base_url: str,
    verifier_model: str,
    query: str,
    context_lines: list[str],
) -> dict:
    prompt = (
        "You are a verification agent.\n"
        "Given CONTEXT, produce ONLY JSON:\n"
        '{"claims":[{"claim":"...","status":"supported|unclear|refuted","citations":["D1","W2"],"evidence":[{"citation":"D1","quote":"..."}],"notes":"..."}]}\n\n'
        "Rules:\n"
        "- If not directly supported by exact text in CONTEXT, mark unclear.\n"
        "- For status=supported: include at least 1 evidence item with an EXACT quote copied from the cited CONTEXT (contiguous span; avoid ellipses).\n"
        "- citations/evidence.citation must refer to bracket tags in CONTEXT (e.g. D1/W2/K1).\n"
        "- Do not invent facts; if the corpus is fiction or irrelevant, mark unclear and explain in notes.\n\n"
        f"Question:\n{query}\n\n"
        "CONTEXT:\n" + "\n".join(context_lines)
    )
    out = await _ollama_chat_once(
        http,
        base_url,
        verifier_model,
        [{"role": "user", "content": prompt}],
        timeout=60.0,
    )
    obj = _json_obj_from_text(out) or {}
    claims_val = obj.get("claims")
    claims = claims_val if isinstance(claims_val, list) else []
    ctx = _context_by_tag(context_lines)
    cleaned = []
    for c in claims[:40]:
        if not isinstance(c, dict):
            continue
        citations = c.get("citations") if isinstance(c.get("citations"), list) else []
        evidence_val = c.get("evidence")
        evidence = evidence_val if isinstance(evidence_val, list) else []

        status = str(c.get("status") or "unclear").strip().lower()
        if status not in {"supported", "unclear", "refuted"}:
            status = "unclear"

        # Defensive: require evidence quotes to be present in context for supported claims.
        if status == "supported":
            ok = False
            for ev in evidence:
                if not isinstance(ev, dict):
                    continue
                tag = str(ev.get("citation") or "").strip()
                quote = str(ev.get("quote") or "").strip()
                if not tag or not quote:
                    continue
                hay = ctx.get(tag) or ""
                if _quote_in_haystack(quote=quote, hay=hay):
                    ok = True
                    break
            if not ok:
                status = "unclear"

        cleaned.append(
            {
                "claim": str(c.get("claim") or "")[:1800],
                "status": status,
                "citations": citations,
                "evidence": [
                    {
                        "citation": str(ev.get("citation") or "")[:16],
                        "quote": str(ev.get("quote") or "")[:500],
                    }
                    for ev in evidence[:6]
                    if isinstance(ev, dict)
                ],
                "notes": str(c.get("notes") or "")[:2000],
            }
        )
    return {"claims": cleaned, "raw": out}


async def _synthesize(
    http: httpx.AsyncClient,
    base_url: str,
    synth_model: str,
    query: str,
    mode: str,
    context_lines: list[str],
    verified_claims: list[dict],
    *,
    embed_model: str,
    ingest_queue: WebIngestQueue | None,
    kiwix_url: str | None,
) -> str:
    vc = json.dumps(verified_claims, ensure_ascii=False)

    m = (mode or "deep").strip().lower()

    if m.startswith("deep"):
        fmt = (
            "## Executive Summary\n"
            "- 7-12 bullets (high-signal), each with citations\n\n"
            "## Concepts And Definitions\n"
            "- Define key terms and explain the mental model\n\n"
            "## Detailed Analysis\n"
            "- Use short subsections (### ...)\n"
            "- Explain mechanisms, causal chains, and tradeoffs\n"
            "- Include concrete examples and edge cases\n\n"
            "## Practical Guidance\n"
            "- A step-by-step checklist or playbook\n\n"
            "## Failure Modes And How To Validate\n"
            "- Common ways this goes wrong; tests/experiments to confirm\n\n"
            "## Uncertainties / Gaps\n"
            "- Anything unclear, missing, conflicting, or likely wrong\n"
        )
    else:
        fmt = (
            "## Executive Summary\n"
            "- 5-9 bullets, each with citations\n\n"
            "## Detailed Analysis\n"
            "- Use short subsections (### ...)\n"
            "- Prefer concrete, checkable statements\n\n"
            "## Practical Takeaways\n"
            "- Actionable checklist\n\n"
            "## Uncertainties / Gaps\n"
            "- Anything unclear, missing, conflicting, or likely wrong\n"
        )

    prompt = (
        "Write a research report in Markdown.\n"
        "The report must be self-contained and written for a reader who will not ask follow-ups.\n\n"
        "Output format:\n" + fmt + "\nRules:\n"
        "- Only assert claims marked supported.\n"
        "- Every factual bullet/sentence must end with at least one citation tag like [D1], [W2], [K1].\n"
        "- Use ONLY citation tags that appear in CONTEXT.\n"
        "- Use evidence quotes in Verified claims to stay grounded (do not paraphrase beyond what the quote supports).\n"
        "- Do NOT include a Sources section; it will be added automatically.\n\n"
        f"Question:\n{query}\n\n"
        f"Verified claims JSON:\n{vc}\n\n"
        "CONTEXT:\n" + "\n".join(context_lines)
    )
    # Research mode synthesis is tool-free: all sources are explicit in trace.
    return await _ollama_chat_once(
        http=http,
        base_url=base_url,
        model=synth_model,
        messages=[{"role": "user", "content": prompt}],
        timeout=90.0,
    )


async def _synthesize_from_context(
    http: httpx.AsyncClient,
    base_url: str,
    model: str,
    *,
    query: str,
    topics: list[str],
    context_lines: list[str],
    deep: bool,
) -> str:
    t = [str(x).strip() for x in (topics or []) if str(x).strip()][:10]
    topics_line = ("Topics: " + ", ".join(t)) if t else ""

    fmt = (
        (
            "## Executive Summary\n"
            "- 7-12 bullets, each with citations\n\n"
            "## Concepts And Definitions\n"
            "- Define key terms\n\n"
            "## Detailed Analysis\n"
            "- Use short subsections (### ...)\n\n"
            "## Practical Guidance\n"
            "- Checklist\n\n"
            "## Uncertainties / Gaps\n"
            "- What is missing/unclear\n"
        )
        if deep
        else (
            "## Executive Summary\n"
            "- 5-9 bullets, each with citations\n\n"
            "## Detailed Analysis\n"
            "- Short subsections (### ...)\n\n"
            "## Practical Takeaways\n"
            "- Checklist\n\n"
            "## Uncertainties / Gaps\n"
            "- What is missing/unclear\n"
        )
    )

    prompt = (
        "Write a research answer in Markdown using ONLY the provided CONTEXT.\n\n"
        "Output format:\n" + fmt + "\nRules:\n"
        "- Do NOT use any knowledge not present in CONTEXT.\n"
        "- Every factual bullet/sentence must end with at least one citation tag like [D1], [W2], [K1].\n"
        "- Use ONLY citation tags that appear in CONTEXT.\n"
        "- If the CONTEXT does not contain the answer, say you don't know.\n"
        "- Do NOT include a Sources section; it will be added automatically.\n\n"
        f"Question:\n{query}\n\n"
        + (topics_line + "\n\n" if topics_line else "")
        + "CONTEXT:\n"
        + "\n".join(context_lines)
    )

    return await _ollama_chat_once(
        http=http,
        base_url=base_url,
        model=model,
        messages=[{"role": "user", "content": prompt}],
        timeout=90.0,
    )


def _format_sources_section(sources_meta: list[dict[str, Any]]) -> str:
    lines: list[str] = []
    seen: set[str] = set()

    for s in sources_meta or []:
        if not isinstance(s, dict):
            continue

        tag = str(s.get("citation") or "").strip()
        if not tag or tag in seen:
            continue
        seen.add(tag)

        stype = str(s.get("source_type") or "").strip().lower()
        title = str(
            s.get("title") or s.get("domain") or s.get("url") or "source"
        ).strip()
        url = str(s.get("url") or "").strip()

        if stype == "doc":
            meta_any = s.get("meta")
            meta = meta_any if isinstance(meta_any, dict) else {}
            src = str(meta.get("source") or "").strip()
            path = str(meta.get("path") or "").strip()
            chunk_id = s.get("chunk_id")
            bits: list[str] = []
            if src:
                bits.append(f"source:{src}")
            if path:
                bits.append(f"path:{path}")
            if isinstance(chunk_id, int) and chunk_id:
                bits.append(f"chunk:{chunk_id}")
            suffix = f" ({', '.join(bits)})" if bits else ""
            lines.append(f"- [{tag}] {title}{suffix}")
            continue

        if url:
            lines.append(f"- [{tag}] {title} — {url}")
        else:
            lines.append(f"- [{tag}] {title}")

    if not lines:
        return ""
    return "## Sources\n" + "\n".join(lines)


def _normalize_evidence_policy(val: Any, *, default_policy: str) -> str:
    s = str(val or "").strip().lower()
    if s in {"strict", "relaxed"}:
        return s
    d = str(default_policy or "strict").strip().lower()
    return d if d in {"strict", "relaxed"} else "strict"


def _normalize_strict_fail_behavior(val: Any, *, default_behavior: str) -> str:
    s = str(val or "").strip().lower()
    if s in {"refuse", "speculative"}:
        return s
    d = str(default_behavior or "refuse").strip().lower()
    return d if d in {"refuse", "speculative"} else "refuse"


def _source_kind_and_id(res: RetrievalResult) -> tuple[str, str | None, str | None]:
    """Return (source_kind, source_id, kiwix_zim).

    source_kind is a stable, semantically meaningful type used by the evidence gate.
    """

    st = (res.source_type or "").strip().lower()
    meta = res.meta if isinstance(res.meta, dict) else {}

    if st == "web":
        sid = (res.domain or "").strip() or None
        return ("web", sid, None)

    if st == "kiwix":
        zim = kiwix_zim_id(res.url, str(meta.get("path") or "") or None)
        return ("kiwix_zim", zim, zim)

    # Docs (uploads/notes/epub)
    src = str(meta.get("source") or "").strip().lower()
    grp = str(meta.get("group_name") or "").strip().lower()
    tags_any = meta.get("tags")
    tags = (
        [str(x).strip().lower() for x in tags_any] if isinstance(tags_any, list) else []
    )
    tagset = {t for t in tags if t}

    if src == "epub" or grp == "epub" or "epub" in tagset:
        title = str(meta.get("title") or "").strip()
        author = str(meta.get("author") or "").strip()
        pth = str(meta.get("path") or "").strip()
        sid = (
            (f"{title} - {author}".strip(" -") if (title or author) else "")
            or pth
            or (res.title or "")
        )
        sid = sid.strip()[:260] if sid else None
        return ("epub", sid, None)

    if src == "kiwix" or grp == "kiwix" or "kiwix" in tagset:
        zim = kiwix_zim_id(res.url, str(meta.get("path") or "") or None)
        return ("kiwix_zim", zim, zim)

    # Treat remaining local docs as user-provided uploads by default.
    fn = str(meta.get("filename") or "").strip() or (res.title or "")
    sid = fn.strip()[:260] if fn else None
    return ("uploaded_doc", sid, None)


def _sources_meta_from_hits(
    hits: list[RetrievalResult],
    *,
    pinned_ref_ids: set[str],
    excluded_ref_ids: set[str],
    limit: int = 40,
) -> list[dict[str, Any]]:
    out: list[dict[str, Any]] = []
    seen: set[str] = set()
    for res in hits[: max(0, int(limit))]:
        ref = str(res.ref_id or "").strip()
        if not ref or ref in seen:
            continue
        seen.add(ref)
        out.append(
            {
                "source_type": res.source_type,
                "ref_id": ref,
                "chunk_id": int(res.chunk_id),
                "title": res.title,
                "url": res.url,
                "domain": res.domain,
                "score": float(res.score or 0.0),
                "snippet": (res.text or "")[:240],
                "meta": res.meta if isinstance(res.meta, dict) else {},
                "pinned": bool(ref in pinned_ref_ids),
                "excluded": bool(ref in excluded_ref_ids),
            }
        )
    return out


async def _classify_epub_genre_llm(
    http: httpx.AsyncClient,
    base_url: str,
    model: str,
    *,
    title: str,
    author: str,
    excerpt: str,
) -> dict[str, Any]:
    prompt = (
        'Return ONLY JSON: {"doc_genre":"fiction|nonfiction|reference|unknown","confidence":0.0,"reason":"..."}.\n\n'
        "Classify whether the following book excerpt is from fiction, nonfiction, a reference work, or unknown. "
        "Be conservative: if uncertain, return unknown.\n\n"
        f"Title: {title[:200]}\n"
        f"Author: {author[:200]}\n\n"
        "Excerpt (first page-ish):\n" + (excerpt or "")[:600]
    )

    out = await _ollama_chat_once(
        http, base_url, model, [{"role": "user", "content": prompt}], timeout=25.0
    )
    obj_any = _json_obj_from_text(out) or {}
    obj = obj_any if isinstance(obj_any, dict) else {}

    g = str(obj.get("doc_genre") or obj.get("genre") or "unknown").strip().lower()
    if g not in {"unknown", "fiction", "nonfiction", "reference"}:
        g = "unknown"
    conf_any: object = obj.get("confidence")
    conf = 0.0
    if isinstance(conf_any, float):
        conf = conf_any
    elif isinstance(conf_any, int):
        conf = float(conf_any)
    elif isinstance(conf_any, str) and conf_any.strip():
        try:
            conf = float(conf_any.strip())
        except Exception:
            conf = 0.0
    if conf < 0.0:
        conf = 0.0
    if conf > 1.0:
        conf = 1.0

    reason = str(obj.get("reason") or "").strip()[:400]
    return {"doc_genre": g, "confidence": conf, "reason": reason, "raw": out}


async def _annotate_provenance_and_partition_hits(
    http: httpx.AsyncClient,
    base_url: str,
    model: str,
    *,
    hits: list[RetrievalResult],
    policy: str,
    strict_allowlist: list[str],
    kiwix_zim_allowlist: list[str],
    epub_default_genre: str,
    epub_nonfiction_is_evidence: bool,
    epub_reference_is_evidence: bool,
    epub_fiction_is_evidence: bool,
    trust_tiers: dict[str, float],
    force_epub_context_only: bool = False,
) -> tuple[list[RetrievalResult], list[RetrievalResult], dict[str, Any]]:
    p = (policy or "strict").strip().lower()

    # Classify EPUBs per doc_id (or per source_id fallback).
    epub_genre_by_doc: dict[str, dict[str, Any]] = {}
    for res in hits:
        kind, sid, _zim = _source_kind_and_id(res)
        if kind != "epub":
            continue
        meta = res.meta if isinstance(res.meta, dict) else {}
        key = str(meta.get("doc_id") or "").strip() or (sid or "")
        if not key or key in epub_genre_by_doc:
            continue

        title = str(meta.get("title") or res.title or "").strip()
        author = str(meta.get("author") or "").strip()
        path = str(meta.get("path") or "").strip()
        tags_any = meta.get("tags")
        tags = (
            [str(x).strip().lower() for x in tags_any]
            if isinstance(tags_any, list)
            else []
        )

        g, why = heuristic_doc_genre(
            title=title,
            author=author,
            path=path,
            tags=tags,
            default_genre=epub_default_genre,
        )
        epub_genre_by_doc[key] = {
            "doc_genre": g,
            "why": why,
            "confidence": 1.0 if g != "unknown" else 0.0,
        }

    if p == "strict":
        for res in hits:
            kind, sid, _zim = _source_kind_and_id(res)
            if kind != "epub":
                continue
            meta = res.meta if isinstance(res.meta, dict) else {}
            key = str(meta.get("doc_id") or "").strip() or (sid or "")
            if not key:
                continue
            cur = epub_genre_by_doc.get(key) or {}
            if str(cur.get("doc_genre") or "unknown").strip().lower() != "unknown":
                continue

            title = str(meta.get("title") or res.title or "").strip()
            author = str(meta.get("author") or "").strip()
            excerpt = (res.text or "").strip()
            if not excerpt:
                continue

            try:
                classified = await _classify_epub_genre_llm(
                    http,
                    base_url,
                    model,
                    title=title,
                    author=author,
                    excerpt=excerpt[:600],
                )
            except Exception:
                continue

            g2 = str(classified.get("doc_genre") or "unknown").strip().lower()
            conf_any: object = classified.get("confidence")
            conf2 = 0.0
            if isinstance(conf_any, float):
                conf2 = conf_any
            elif isinstance(conf_any, int):
                conf2 = float(conf_any)
            elif isinstance(conf_any, str) and conf_any.strip():
                try:
                    conf2 = float(conf_any.strip())
                except Exception:
                    conf2 = 0.0
            if g2 in {"nonfiction", "reference", "fiction"} and conf2 >= 0.55:
                epub_genre_by_doc[key] = {
                    "doc_genre": g2,
                    "why": "llm",
                    "confidence": conf2,
                }

    stats: dict[str, Any] = {
        "policy": p,
        "total": len(hits),
        "evidence": 0,
        "excluded": 0,
        "by_kind": {},
        "by_reason": {},
        "epub_by_genre": {},
    }

    evidence_hits: list[RetrievalResult] = []
    context_hits: list[RetrievalResult] = []

    for res in hits:
        kind, sid, zim = _source_kind_and_id(res)
        meta = res.meta if isinstance(res.meta, dict) else {}
        tags_any = meta.get("tags")
        tags = (
            [str(x).strip().lower() for x in tags_any]
            if isinstance(tags_any, list)
            else []
        )
        doc_genre = "unknown"
        if kind == "epub":
            key = str(meta.get("doc_id") or "").strip() or (sid or "")
            doc_genre = (
                str((epub_genre_by_doc.get(key) or {}).get("doc_genre") or "unknown")
                .strip()
                .lower()
            )
        ok, reason = evidence_ok(
            policy=p,
            kind=kind,
            doc_genre=doc_genre,
            kiwix_zim=zim,
            strict_allowlist=strict_allowlist,
            kiwix_zim_allowlist=kiwix_zim_allowlist,
            epub_nonfiction_is_evidence=epub_nonfiction_is_evidence,
            epub_reference_is_evidence=epub_reference_is_evidence,
            epub_fiction_is_evidence=epub_fiction_is_evidence,
        )

        if p == "strict" and kind == "epub" and bool(force_epub_context_only):
            ok = False
            reason = "epub_context_only_empirical"

        trust = trust_tier_for(kind, doc_genre=doc_genre, trust_tiers=trust_tiers)

        prov = {
            "evidence_policy": p,
            "source_kind": kind,
            "source_id": sid,
            "trust_tier": trust,
            "doc_genre": doc_genre,
            "evidence_ok": bool(ok),
            "evidence_reason": reason,
        }
        if zim:
            prov["kiwix_zim"] = zim
        if kind == "epub":
            key = str(meta.get("doc_id") or "").strip() or (sid or "")
            gmeta = epub_genre_by_doc.get(key) or {}
            if gmeta:
                prov["genre_why"] = gmeta.get("why")
                prov["genre_confidence"] = gmeta.get("confidence")

        # Attach provenance for downstream prompts/trace.
        if isinstance(res.meta, dict):
            res.meta["provenance"] = prov
            # Keep doc_genre accessible without spelunking.
            if kind == "epub":
                res.meta["doc_genre"] = doc_genre
                if tags and "epub" not in tags:
                    tags.append("epub")
                    res.meta["tags"] = tags

        stats["by_kind"][kind] = int(stats["by_kind"].get(kind, 0)) + 1
        stats["by_reason"][reason] = int(stats["by_reason"].get(reason, 0)) + 1
        if kind == "epub":
            stats["epub_by_genre"][doc_genre] = (
                int(stats["epub_by_genre"].get(doc_genre, 0)) + 1
            )

        if ok:
            evidence_hits.append(res)
            stats["evidence"] += 1
        else:
            context_hits.append(res)
            stats["excluded"] += 1

    # Order evidence hits by trust_tier then similarity score.
    def _e_key(r: RetrievalResult) -> tuple[float, float]:
        m = r.meta if isinstance(r.meta, dict) else {}
        prov_any = m.get("provenance")
        prov2 = prov_any if isinstance(prov_any, dict) else {}
        tt = float(prov2.get("trust_tier") or 0.0)
        return (tt, float(r.score or 0.0))

    evidence_hits.sort(key=lambda r: _e_key(r), reverse=True)
    return (evidence_hits, context_hits, stats)


async def _citation_audit_rewrite(
    http: httpx.AsyncClient,
    base_url: str,
    model: str,
    *,
    query: str,
    report_md: str,
    allowed_tags: list[str],
    supported_claims: list[dict[str, Any]],
) -> str:
    prompt = (
        "You are a citation auditor. Rewrite the REPORT to comply with the rules.\n\n"
        "Rules:\n"
        "- Do not add new claims; only use the Supported claims JSON.\n"
        "- If a sentence uses strong evidence language (e.g., 'shown', 'demonstrated', 'meta-analysis', 'studies'), it MUST include at least one allowed citation tag.\n"
        "- If you cannot cite it, downgrade language (might/could) or remove the sentence.\n"
        "- Use ONLY citation tags from ALLOWED_TAGS.\n"
        "- Preserve Markdown headings; do NOT add a Sources section.\n\n"
        f"Question:\n{query}\n\n"
        f"ALLOWED_TAGS:\n{json.dumps(allowed_tags, ensure_ascii=False)}\n\n"
        f"Supported claims JSON:\n{json.dumps(supported_claims, ensure_ascii=False)}\n\n"
        "REPORT:\n" + (report_md or "")
    )

    out = await _ollama_chat_once(
        http=http,
        base_url=base_url,
        model=model,
        messages=[{"role": "user", "content": prompt}],
        timeout=45.0,
    )
    return (out or "").strip()


def _strip_invalid_citation_tokens(text: str, *, allowed_tags: set[str]) -> str:
    def _repl(m: re.Match[str]) -> str:
        tag = str(m.group(1) or "").strip()
        return m.group(0) if tag in allowed_tags else ""

    out = _CITATION_TOKEN.sub(_repl, text or "")
    # Also remove numeric citation tokens like [1] which are never valid in this system.
    out = _NUMERIC_CITATION_TOKEN.sub("", out)
    # Drop trailing reference blocks if present.
    lines = out.splitlines()
    for i, ln in enumerate(lines):
        if _REFS_HEADING.match(ln or ""):
            out = "\n".join(lines[:i]).rstrip()
            break
    out = re.sub(r"[ \t]{2,}", " ", out)
    return out.strip()


_EMPIRICAL_CITATION_NEEDLES = (
    "according to",
    "statistics",
    "statistic",
    "ratio",
    "rate",
    "percent",
    "%",
    "meta-analysis",
    "systematic review",
    "study shows",
    "studies show",
    "who",
    "world health organization",
    "nhtsa",
    "national highway traffic safety administration",
    "cdc",
    "eurostat",
    "oecd",
)


def _has_uncited_empirical_claims(text: str) -> bool:
    for ln in (text or "").splitlines():
        raw = ln.strip()
        if not raw:
            continue
        if extract_citation_tags(raw):
            continue
        low = raw.lower()
        if re.search(r"\d", low):
            return True
        if any(n in low for n in _EMPIRICAL_CITATION_NEEDLES):
            return True
    return False


async def _rewrite_for_citation_contract(
    http: httpx.AsyncClient,
    base_url: str,
    model: str,
    *,
    query: str,
    text: str,
    allowed_tags: list[str],
    invalid_tags: list[str],
    question_type: str,
) -> str:
    rules = (
        "Citation Contract:\n"
        "- Use ONLY citation tags in ALLOWED_TAGS.\n"
        "- Remove any tag in INVALID_TAGS.\n"
        "- Every factual bullet/sentence must end with at least one allowed citation tag like [D1], [W2], [K1].\n"
        "- Do NOT add new sources or a Sources section.\n"
        "- Do NOT add new claims.\n"
        "- If you cannot support a statement with allowed citations, remove it or clearly mark it as unknown.\n"
    )
    if allowed_tags:
        rules += "- Output must include at least one citation tag from ALLOWED_TAGS (unless the only answer is that you don't know).\n"
    if (question_type or "").strip().lower() == "empirical_stats":
        rules += "- For empirical/statistical questions: any line that contains numbers or empirical/dataset phrasing must have an allowed citation on the same line; otherwise remove it.\n"

    prompt = (
        "Rewrite TEXT to comply with the Citation Contract.\n\n"
        + rules
        + "\nQuestion:\n"
        + (query or "")
        + "\n\nALLOWED_TAGS:\n"
        + json.dumps(
            [str(t) for t in allowed_tags if str(t).strip()], ensure_ascii=False
        )
        + "\n\nINVALID_TAGS:\n"
        + json.dumps(
            [str(t) for t in invalid_tags if str(t).strip()], ensure_ascii=False
        )
        + "\n\nTEXT:\n"
        + (text or "")
    )
    out = await _ollama_chat_once(
        http, base_url, model, [{"role": "user", "content": prompt}], timeout=75.0
    )
    return (out or "").strip()


async def _synthesize_speculative_no_evidence(
    http: httpx.AsyncClient,
    base_url: str,
    model: str,
    *,
    query: str,
    context_items: list[dict[str, Any]],
) -> str:
    prompt = (
        "You are answering with NO evidence-eligible sources. The provided snippets are context-only and may include fiction or unreliable material.\n\n"
        "Rules:\n"
        "- Label the answer as speculative.\n"
        "- Do NOT claim that anything is 'shown', 'demonstrated', or backed by studies.\n"
        "- Use hedging language (might/could/possibly).\n"
        "- Do NOT include citations.\n\n"
        "Format:\n"
        "## Speculative Answer (No Reliable Evidence Enabled)\n"
        "(2-6 paragraphs)\n\n"
        "## What Evidence Would Be Needed\n"
        "- 4-8 bullets\n\n"
        f"Question:\n{query}\n\n"
        f"Context-only snippets (not evidence):\n{json.dumps(context_items, ensure_ascii=False)}\n"
    )

    out = await _ollama_chat_once(
        http=http,
        base_url=base_url,
        model=model,
        messages=[{"role": "user", "content": prompt}],
        timeout=60.0,
    )
    return (out or "").strip()


def _fallback_tool_calls_from_hints(
    *,
    query: str,
    plan: dict[str, Any],
    hints: dict[str, Any],
    allowed_tools: list[str],
    doc_top_k: int,
    web_top_k: int,
    pages_per_round: int,
    cap: int,
) -> list[dict[str, Any]]:
    allow = {str(x).strip() for x in (allowed_tools or []) if str(x).strip()}

    def _dedupe(items: list[Any]) -> list[str]:
        out: list[str] = []
        seen: set[str] = set()
        for raw in items:
            s = str(raw or "").strip()
            if not s:
                continue
            k = s.lower()
            if k in seen:
                continue
            seen.add(k)
            out.append(s)
        return out

    doc_q: list[str] = []
    if "doc_search" in allow:
        h_doc_any = hints.get("doc_queries")
        h_doc = h_doc_any if isinstance(h_doc_any, list) else []
        p_doc_any = plan.get("doc_queries")
        p_doc = p_doc_any if isinstance(p_doc_any, list) else []
        p_sub_any = plan.get("subquestions")
        p_sub = p_sub_any if isinstance(p_sub_any, list) else []
        doc_q = _dedupe([*h_doc, *p_doc, *p_sub, query])

    web_q: list[str] = []
    if "web_search" in allow:
        h_web_any = hints.get("web_queries")
        h_web = h_web_any if isinstance(h_web_any, list) else []
        p_web_any = plan.get("web_queries")
        p_web = p_web_any if isinstance(p_web_any, list) else []
        p_sub_any = plan.get("subquestions")
        p_sub = p_sub_any if isinstance(p_sub_any, list) else []
        web_q = _dedupe([*h_web, *p_web, *p_sub, query])

    kiwix_q = str(hints.get("kiwix_query") or query).strip() or query

    # Rotating cursors (stored in hints) so repeated fallbacks don't always hit the same query.
    doc_i = int(hints.get("_fallback_doc_i") or 0)
    web_i = int(hints.get("_fallback_web_i") or 0)
    hints["_fallback_doc_i"] = doc_i + 1
    hints["_fallback_web_i"] = web_i + 1

    def _mk_call(name: str, args: dict[str, Any], *, idx: int) -> dict[str, Any]:
        return {"id": f"auto_tool_{idx}", "function": {"name": name, "arguments": args}}

    calls: list[dict[str, Any]] = []
    idx = 1
    if "kiwix_search" in allow and kiwix_q:
        calls.append(_mk_call("kiwix_search", {"query": kiwix_q, "top_k": 5}, idx=idx))
        idx += 1
    if "doc_search" in allow and doc_q:
        q0 = doc_q[doc_i % len(doc_q)]
        calls.append(
            _mk_call("doc_search", {"query": q0, "top_k": int(doc_top_k)}, idx=idx)
        )
        idx += 1
    if "web_search" in allow and web_q:
        q1 = web_q[web_i % len(web_q)]
        calls.append(
            _mk_call(
                "web_search",
                {
                    "query": q1,
                    "top_k": int(web_top_k),
                    "pages": max(1, min(int(pages_per_round), 3)),
                },
                idx=idx,
            )
        )

    return calls[: max(0, int(cap))]


async def _run_deep_research_agentic(
    *,
    http: httpx.AsyncClient,
    base_url: str,
    ingest_queue: WebIngestQueue,
    kiwix_url: str | None,
    run_id: str,
    query: str,
    plan: dict[str, Any],
    use_docs: bool,
    use_web: bool,
    pages_per_round: int,
    web_top_k: int,
    doc_top_k: int,
    domain_whitelist: list[str] | None,
    embed_model: str,
    planner_model: str,
    verifier_model: str,
    synth_model: str,
    settings: dict[str, Any],
    steps: list[dict[str, Any]],
    evidence_policy: str,
    strict_fail_behavior: str,
    strict_allowlist: list[str],
    kiwix_zim_allowlist: list[str],
    epub_default_genre: str,
    epub_nonfiction_is_evidence: bool,
    epub_reference_is_evidence: bool,
    epub_fiction_is_evidence: bool,
    trust_tiers: dict[str, float],
    genre_classifier_model: str,
    audit_model: str,
) -> dict[str, Any]:
    started_at = time.time()

    tool_schemas = _research_tools_for_prompt(
        use_docs=use_docs, use_web=use_web, kiwix_url=kiwix_url
    )
    allowed_tools = []
    for t in tool_schemas:
        fn = t.get("function") if isinstance(t, dict) else None
        if isinstance(fn, dict) and isinstance(fn.get("name"), str):
            allowed_tools.append(str(fn.get("name")))

    max_tool_calls = int(settings.get("max_tool_calls") or MAX_DEEP_TOOL_CALLS)
    # Hard cap: deep agentic loop must not exceed MAX_DEEP_TOOL_CALLS.
    max_tool_calls = max(1, min(max_tool_calls, MAX_DEEP_TOOL_CALLS))
    max_steps = int(settings.get("max_tool_steps") or MAX_TOOL_PLANNING_STEPS)
    max_steps = max(3, min(max_steps, 80))
    per_step_cap = int(
        settings.get("max_tool_calls_per_step") or MAX_TOOL_CALLS_PER_STEP
    )
    per_step_cap = max(1, min(per_step_cap, 12))

    question_type = "general_factual"
    force_epub_context_only = False
    require_evidence = False
    try:
        prof = await _deep_research_question_profile(
            http,
            base_url,
            verifier_model,
            query=query,
            plan=plan,
        )
        qt = str(prof.get("question_type") or "").strip().lower()
        if qt in {"empirical_stats", "general_factual", "creative", "other"}:
            question_type = qt
        force_epub_context_only = bool(prof.get("force_epub_context_only"))
        require_evidence = bool(prof.get("require_evidence"))
        researchstore.add_trace(
            run_id,
            "question_profile",
            {
                "question_type": question_type,
                "force_evidence_policy": prof.get("force_evidence_policy"),
                "force_epub_context_only": force_epub_context_only,
                "require_evidence": require_evidence,
                "reason": prof.get("reason"),
            },
        )
        steps.append(
            {
                "type": "question_profile",
                "question_type": question_type,
                "reason": prof.get("reason"),
            }
        )
    except Exception as e:
        researchstore.add_trace(run_id, "question_profile_error", {"error": str(e)})

    # Heuristic backstop: ensure empirical stats questions are treated as strict.
    if question_type != "creative" and _looks_like_empirical_stats_query(query):
        if question_type != "empirical_stats":
            researchstore.add_trace(
                run_id,
                "question_profile_override",
                {"from": question_type, "to": "empirical_stats", "reason": "heuristic"},
            )
        question_type = "empirical_stats"

    # Harden defaults for empirical-statistical questions.
    if question_type == "empirical_stats":
        evidence_policy = "strict"
        strict_fail_behavior = "refuse"
        force_epub_context_only = True
        require_evidence = True

    pool: dict[str, RetrievalResult] = {}
    seen_sigs: set[str] = set()
    tool_calls_used = 0
    supported_claims: list[dict[str, Any]] = []
    verify: dict[str, Any] = {"claims": []}

    hints: dict[str, Any] = {
        "doc_queries": plan.get("doc_queries") or [],
        "web_queries": plan.get("web_queries") or [],
        "kiwix_query": query,
    }

    sources_meta: list[dict[str, Any]] = []
    sources_meta_store: list[dict[str, Any]] = []
    context_lines: list[str] = []

    for step_no in range(1, max_steps + 1):
        budget_remaining = max(0, int(max_tool_calls) - int(tool_calls_used))
        min_rem = _min_time_remaining_sec()
        researchstore.add_trace(
            run_id,
            "agent_step_begin",
            {
                "step": step_no,
                "tool_calls_used": tool_calls_used,
                "tool_budget": max_tool_calls,
                "min_time_remaining_sec": round(max(0.0, float(min_rem)), 2)
                if min_rem is not None
                else None,
            },
        )
        if _min_time_is_set() and _min_time_satisfied():
            researchstore.add_trace(
                run_id,
                "time_budget_met",
                {"step": step_no, "elapsed_s": round(time.time() - started_at, 2)},
            )
            break
        if budget_remaining <= 0 or not allowed_tools:
            break

        # User steering flags.
        flags = researchstore.get_source_flags_by_ref_id(run_id)
        pinned_ref_ids = {
            ref for ref, f in flags.items() if isinstance(f, dict) and f.get("pinned")
        }
        excluded_ref_ids = {
            ref for ref, f in flags.items() if isinstance(f, dict) and f.get("excluded")
        }

        # Model call: choose tools to call.
        msg = await _deep_agentic_tool_plan(
            http,
            base_url,
            planner_model,
            query=query,
            plan=plan,
            evidence_policy=evidence_policy,
            budget_remaining=budget_remaining,
            allowed_tools=allowed_tools,
            hints=hints,
            supported_claims=supported_claims,
            tool_schemas=tool_schemas,
        )
        researchstore.add_trace(
            run_id,
            "agent_tool_plan",
            {
                "step": step_no,
                "content": str(msg.get("content") or "")[:800],
                "has_tool_calls": bool(msg.get("tool_calls")),
            },
        )

        tool_calls_raw = _normalize_tool_calls_from_message(msg)
        if not tool_calls_raw:
            if (not _min_time_is_set()) or _min_time_satisfied():
                # Model signaled it wants to stop retrieving.
                break

            tool_calls_raw = _fallback_tool_calls_from_hints(
                query=query,
                plan=plan,
                hints=hints,
                allowed_tools=allowed_tools,
                doc_top_k=doc_top_k,
                web_top_k=web_top_k,
                pages_per_round=pages_per_round,
                cap=min(per_step_cap, budget_remaining),
            )
            researchstore.add_trace(
                run_id,
                "agent_tool_plan_fallback",
                {
                    "step": step_no,
                    "calls": [
                        str((c.get("function") or {}).get("name") or "")
                        for c in tool_calls_raw
                    ],
                },
            )
            if not tool_calls_raw:
                break

        tool_calls_raw = tool_calls_raw[: min(per_step_cap, budget_remaining)]

        exec_results: list[dict[str, Any]] = []
        new_candidates: list[RetrievalResult] = []

        for idx, tc in enumerate(tool_calls_raw, start=1):
            name, args, call_id = _parse_tool_call(tc, index=idx)
            if not name or name not in allowed_tools:
                exec_results.append(
                    {
                        "tool_call_id": call_id,
                        "tool": name,
                        "ok": False,
                        "error": "tool_not_allowed",
                    }
                )
                continue

            sig = name + ":" + json.dumps(args, sort_keys=True, ensure_ascii=False)
            if sig in seen_sigs:
                exec_results.append(
                    {
                        "tool_call_id": call_id,
                        "tool": name,
                        "ok": False,
                        "error": "duplicate_call",
                    }
                )
                continue
            seen_sigs.add(sig)

            if tool_calls_used >= max_tool_calls:
                exec_results.append(
                    {
                        "tool_call_id": call_id,
                        "tool": name,
                        "ok": False,
                        "error": "tool_budget_exhausted",
                    }
                )
                break

            tool_calls_used += 1
            t0 = time.time()
            try:
                ran = await _execute_research_tool(
                    name=name,
                    args=args,
                    http=http,
                    ingest_queue=ingest_queue,
                    embed_model=embed_model,
                    kiwix_url=kiwix_url,
                    domain_whitelist=domain_whitelist,
                    pages_per_round=pages_per_round,
                    web_top_k=web_top_k,
                    doc_top_k=doc_top_k,
                    allow_epub=bool(settings.get("allow_epub")),
                )
            except Exception as e:
                ran = {"tool": name, "ok": False, "error": f"{type(e).__name__}: {e}"}

            dur_ms = int((time.time() - t0) * 1000)
            ran["tool_call_id"] = call_id
            ran["duration_ms"] = dur_ms
            exec_results.append(ran)

            if ran.get("ok") is True and isinstance(ran.get("result"), dict):
                new_candidates.extend(_hits_from_tool_result(name, ran["result"]))

        researchstore.add_trace(
            run_id,
            "agent_tool_results",
            {
                "step": step_no,
                "tool_calls_used": tool_calls_used,
                "results": [
                    {
                        "tool": r.get("tool"),
                        "ok": bool(r.get("ok")),
                        "error": r.get("error"),
                        "duration_ms": r.get("duration_ms"),
                    }
                    for r in exec_results
                ],
            },
        )

        # Model call: relevance gate on NEW candidates.
        budget_remaining = max(0, int(max_tool_calls) - int(tool_calls_used))
        rel = await _deep_agentic_relevance_check(
            http,
            base_url,
            verifier_model,
            query=query,
            plan=plan,
            new_candidates=new_candidates,
            evidence_policy=evidence_policy,
            budget_remaining=budget_remaining,
        )
        researchstore.add_trace(
            run_id,
            "agent_relevance",
            {
                "step": step_no,
                "done": bool(rel.get("done")),
                "reason": rel.get("reason"),
                "missing": rel.get("missing"),
            },
        )

        keep_ids = set(
            [str(x) for x in (rel.get("keep_ref_ids") or []) if str(x).strip()]
        )
        if not keep_ids:
            # Conservative fallback: keep top-scoring candidates so we can make progress.
            ranked = sorted(
                new_candidates, key=lambda r: float(r.score or 0.0), reverse=True
            )
            keep_ids = {r.ref_id for r in ranked[: min(8, len(ranked))] if r.ref_id}

        for r in new_candidates:
            if not r.ref_id or r.ref_id in excluded_ref_ids:
                continue
            if r.ref_id not in keep_ids:
                continue
            prev = pool.get(r.ref_id)
            if prev is None or float(r.score or 0.0) > float(prev.score or 0.0):
                pool[r.ref_id] = r

        # Evidence gate (Stage 2): mark which sources can be cited.
        (
            evidence_hits,
            _ctx_only,
            gate_stats,
        ) = await _annotate_provenance_and_partition_hits(
            http,
            base_url,
            genre_classifier_model,
            hits=list(pool.values()),
            policy=evidence_policy,
            strict_allowlist=strict_allowlist,
            kiwix_zim_allowlist=kiwix_zim_allowlist,
            epub_default_genre=epub_default_genre,
            epub_nonfiction_is_evidence=epub_nonfiction_is_evidence,
            epub_reference_is_evidence=epub_reference_is_evidence,
            epub_fiction_is_evidence=epub_fiction_is_evidence,
            trust_tiers=trust_tiers,
            force_epub_context_only=force_epub_context_only,
        )
        researchstore.add_trace(
            run_id, "evidence_gate", {"step": step_no, **gate_stats}
        )

        # Persist sources list for UI steering.
        sources_meta_store = _sources_meta_from_hits(
            list(pool.values()),
            pinned_ref_ids=pinned_ref_ids,
            excluded_ref_ids=excluded_ref_ids,
            limit=80,
        )
        researchstore.upsert_sources(run_id, sources_meta_store)

        max_chars = 20000
        per_source_cap = 8
        sources_meta, context_lines = build_context(
            evidence_hits,
            max_chars=max_chars,
            per_source_cap=per_source_cap,
            pinned_ref_ids=pinned_ref_ids,
            excluded_ref_ids=excluded_ref_ids,
            preserve_order=True,
        )
        researchstore.add_trace(
            run_id,
            "evidence_context",
            {
                "step": step_no,
                "sources": len(sources_meta),
                "lines": len(context_lines),
            },
        )

        # Strict fail-closed: no evidence to cite.
        if evidence_policy == "strict" and not context_lines:
            by_kind = gate_stats.get("by_kind") if isinstance(gate_stats, dict) else {}
            epub_by_genre = (
                gate_stats.get("epub_by_genre") if isinstance(gate_stats, dict) else {}
            )
            researchstore.add_trace(
                run_id,
                "guardrail",
                {
                    "reason": "no_evidence_sources",
                    "step": step_no,
                    "by_kind": by_kind,
                    "epub_by_genre": epub_by_genre,
                    "strict_fail_behavior": strict_fail_behavior,
                },
            )

            # If other evidence sources are enabled, keep trying.
            if budget_remaining > 0 and (use_web or bool(kiwix_url)):
                continue

            if strict_fail_behavior == "speculative":
                ctx_items: list[dict[str, Any]] = []
                for s in sources_meta_store or []:
                    if not isinstance(s, dict):
                        continue
                    ctx_items.append(
                        {
                            "title": s.get("title"),
                            "snippet": s.get("snippet"),
                            "meta": s.get("meta"),
                        }
                    )
                    if len(ctx_items) >= 12:
                        break
                msg2 = await _synthesize_speculative_no_evidence(
                    http,
                    base_url,
                    synth_model,
                    query=query,
                    context_items=ctx_items,
                )
            else:
                if require_evidence:
                    msg2 = (
                        "## Cannot Answer (No Evidence-Eligible Data)\n\n"
                        "This question requires empirical, dataset-backed evidence (e.g., counts/ratios/statistics), "
                        "but no evidence-eligible sources were available under strict mode.\n\n"
                        f"Retrieved kinds: {json.dumps(by_kind, ensure_ascii=False)}\n"
                        f"EPUB genres: {json.dumps(epub_by_genre, ensure_ascii=False)}\n\n"
                        "To answer this safely:\n"
                        "- Enable web search or configure offline Wikipedia (Kiwix), then re-run.\n"
                        "- Or upload/ingest an authoritative crash/injury dataset or report.\n"
                    )
                else:
                    msg2 = (
                        "No evidence found in enabled sources (evidence_policy=strict).\n\n"
                        "This run retrieved content, but it was excluded from evidence by policy (for example: EPUB fiction/unknown).\n\n"
                        f"Retrieved kinds: {json.dumps(by_kind, ensure_ascii=False)}\n"
                        f"EPUB genres: {json.dumps(epub_by_genre, ensure_ascii=False)}\n\n"
                        "Fixes:\n"
                        "- Configure offline Wikipedia (Kiwix) and set `KIWIX_URL`, then re-run.\n"
                        "- Or re-run with web enabled: `/research --web ...` or `/deep --web ...`.\n"
                        "- Or ingest/upload nonfiction/reference documents, or tag EPUBs as nonfiction/reference for evidence use."
                    )

            researchstore.set_run_done(run_id, msg2)
            return {
                "ok": True,
                "run_id": run_id,
                "answer": msg2,
                "sources": sources_meta_store,
                "steps": steps,
            }

        # Model call: verify supported claims.
        verify = await _verify_claims(
            http, base_url, verifier_model, query, context_lines
        )
        researchstore.clear_claims(run_id)
        researchstore.add_claims(run_id, verify["claims"])
        researchstore.add_trace(
            run_id, "verify", {"step": step_no, "claims": len(verify["claims"])}
        )
        supported_claims = [
            c
            for c in (verify.get("claims") or [])
            if isinstance(c, dict)
            and str(c.get("status") or "").strip().lower() == "supported"
        ]

        # Model call: gap check.
        gap = await _gap_check_and_refine_queries(
            http,
            base_url,
            verifier_model,
            query=query,
            topics=plan.get("topics") or [],
            subquestions=plan.get("subquestions") or [],
            supported_claims=supported_claims,
            use_docs=use_docs,
            use_web=use_web,
            kiwix_enabled=bool(kiwix_url),
        )
        researchstore.add_trace(
            run_id,
            "gap",
            {"step": step_no, "done": gap.get("done"), "reason": gap.get("reason")},
        )
        steps.append(
            {
                "type": "gap",
                "step": step_no,
                "done": bool(gap.get("done")),
                "reason": str(gap.get("reason") or "")[:800],
            }
        )

        # Update hints for next planning step.
        hints["doc_queries"] = gap.get("doc_queries") or hints.get("doc_queries")
        hints["web_queries"] = gap.get("web_queries") or hints.get("web_queries")
        if gap.get("kiwix_query"):
            hints["kiwix_query"] = gap.get("kiwix_query")

        done_if = plan.get("done_if") or []
        if done_if:
            done_check = await _check_done_if(
                http,
                base_url,
                verifier_model,
                query=query,
                done_if=done_if,
                supported_claims=supported_claims,
            )
            researchstore.add_trace(run_id, "done_if", done_check)
            if bool(done_check.get("done")) and (
                (not _min_time_is_set()) or _min_time_satisfied()
            ):
                break

        if (not _min_time_is_set()) or _min_time_satisfied():
            if bool(rel.get("done")) and len(supported_claims) >= 4:
                break
            if bool(gap.get("done")) and len(supported_claims) >= 6:
                break

    # Parse/analyze/breakdown further
    claims_any = verify.get("claims") if isinstance(verify, dict) else None
    verified_claims = (
        cast(list[dict[str, Any]], claims_any) if isinstance(claims_any, list) else []
    )
    parsed = await _deep_agentic_parse(
        http, base_url, verifier_model, query=query, verified_claims=verified_claims
    )
    researchstore.add_trace(
        run_id,
        "agent_parse",
        {
            "facts": len(parsed.get("facts") or []),
            "open": len(parsed.get("open_questions") or []),
        },
    )

    analysis = await _deep_agentic_analyze(
        http,
        base_url,
        verifier_model,
        query=query,
        plan=plan,
        parsed=parsed,
    )
    researchstore.add_trace(
        run_id,
        "agent_analyze",
        {
            "need_more": bool(analysis.get("need_more_research")),
            "missing": analysis.get("missing"),
        },
    )

    allowed_tools2 = allowed_tools
    missing_any = analysis.get("missing") if isinstance(analysis, dict) else None
    missing = cast(list[str], missing_any) if isinstance(missing_any, list) else []
    breakdown = await _deep_agentic_breakdown_further(
        http,
        base_url,
        planner_model,
        query=query,
        missing=missing,
        allowed_tools=allowed_tools2,
    )
    researchstore.add_trace(
        run_id,
        "agent_breakdown",
        {
            "doc": len(breakdown.get("doc_queries") or []),
            "web": len(breakdown.get("web_queries") or []),
            "kiwix": breakdown.get("kiwix_query"),
        },
    )

    # Optional extra tool pass if analysis says we're missing evidence.
    if bool(analysis.get("need_more_research")) and tool_calls_used < max_tool_calls:
        hints["doc_queries"] = breakdown.get("doc_queries") or hints.get("doc_queries")
        hints["web_queries"] = breakdown.get("web_queries") or hints.get("web_queries")
        if breakdown.get("kiwix_query"):
            hints["kiwix_query"] = breakdown.get("kiwix_query")

        # Run a small number of additional planning steps.
        extra_steps = min(3, max_steps)
        for _ in range(extra_steps):
            budget_remaining = max(0, int(max_tool_calls) - int(tool_calls_used))
            if budget_remaining <= 0:
                break
            msg = await _deep_agentic_tool_plan(
                http,
                base_url,
                planner_model,
                query=query,
                plan=plan,
                evidence_policy=evidence_policy,
                budget_remaining=budget_remaining,
                allowed_tools=allowed_tools,
                hints=hints,
                supported_claims=supported_claims,
                tool_schemas=tool_schemas,
            )
            tool_calls_raw = _normalize_tool_calls_from_message(msg)
            if not tool_calls_raw:
                break
            tool_calls_raw = tool_calls_raw[: min(per_step_cap, budget_remaining)]
            new_candidates = []
            for idx, tc in enumerate(tool_calls_raw, start=1):
                name, args, call_id = _parse_tool_call(tc, index=idx)
                if not name or name not in allowed_tools:
                    continue
                sig = name + ":" + json.dumps(args, sort_keys=True, ensure_ascii=False)
                if sig in seen_sigs:
                    continue
                seen_sigs.add(sig)
                if tool_calls_used >= max_tool_calls:
                    break
                tool_calls_used += 1
                try:
                    ran = await _execute_research_tool(
                        name=name,
                        args=args,
                        http=http,
                        ingest_queue=ingest_queue,
                        embed_model=embed_model,
                        kiwix_url=kiwix_url,
                        domain_whitelist=domain_whitelist,
                        pages_per_round=pages_per_round,
                        web_top_k=web_top_k,
                        doc_top_k=doc_top_k,
                        allow_epub=bool(settings.get("allow_epub")),
                    )
                except Exception:
                    continue
                if ran.get("ok") is True and isinstance(ran.get("result"), dict):
                    new_candidates.extend(_hits_from_tool_result(name, ran["result"]))

            for r in new_candidates:
                if r.ref_id and r.ref_id not in pool:
                    pool[r.ref_id] = r

        # Recompute evidence context + claims after extra tools.
        (
            evidence_hits,
            _ctx_only,
            gate_stats,
        ) = await _annotate_provenance_and_partition_hits(
            http,
            base_url,
            genre_classifier_model,
            hits=list(pool.values()),
            policy=evidence_policy,
            strict_allowlist=strict_allowlist,
            kiwix_zim_allowlist=kiwix_zim_allowlist,
            epub_default_genre=epub_default_genre,
            epub_nonfiction_is_evidence=epub_nonfiction_is_evidence,
            epub_reference_is_evidence=epub_reference_is_evidence,
            epub_fiction_is_evidence=epub_fiction_is_evidence,
            trust_tiers=trust_tiers,
            force_epub_context_only=force_epub_context_only,
        )
        flags = researchstore.get_source_flags_by_ref_id(run_id)
        pinned_ref_ids = {
            ref for ref, f in flags.items() if isinstance(f, dict) and f.get("pinned")
        }
        excluded_ref_ids = {
            ref for ref, f in flags.items() if isinstance(f, dict) and f.get("excluded")
        }
        sources_meta, context_lines = build_context(
            evidence_hits,
            max_chars=20000,
            per_source_cap=8,
            pinned_ref_ids=pinned_ref_ids,
            excluded_ref_ids=excluded_ref_ids,
            preserve_order=True,
        )
        if context_lines:
            verify = await _verify_claims(
                http, base_url, verifier_model, query, context_lines
            )
            researchstore.clear_claims(run_id)
            researchstore.add_claims(run_id, verify["claims"])
            supported_claims = [
                c
                for c in (verify.get("claims") or [])
                if isinstance(c, dict)
                and str(c.get("status") or "").strip().lower() == "supported"
            ]

    # Construct response -> analyze -> edit -> format -> finalize
    allowed_tags = [
        str(s.get("citation") or "").strip()
        for s in (sources_meta or [])
        if isinstance(s, dict) and str(s.get("citation") or "").strip()
    ]
    allowed_set = set(allowed_tags)

    # For empirical/statistical questions, refuse if we could not verify any supported claims.
    if require_evidence and not supported_claims:
        msg = (
            "## Cannot Answer (Insufficient Supported Evidence)\n\n"
            "I retrieved sources, but none of the key empirical claims could be verified as supported from evidence-eligible chunks.\n\n"
            "Try enabling web/Kiwix or uploading an authoritative dataset/report, then re-run.\n"
        )
        sources_section = _format_sources_section(sources_meta)
        if sources_section:
            msg = (msg.rstrip() + "\n\n" + sources_section).strip()
        researchstore.set_run_done(run_id, msg)
        researchstore.add_trace(
            run_id,
            "done",
            {"reason": "no_supported_claims", "question_type": question_type},
        )
        return {
            "ok": True,
            "run_id": run_id,
            "answer": msg,
            "sources": sources_meta_store,
            "steps": steps,
        }

    claims_any = verify.get("claims") if isinstance(verify, dict) else None
    verified_claims = (
        cast(list[dict[str, Any]], claims_any) if isinstance(claims_any, list) else []
    )
    draft = await _deep_agentic_construct_response(
        http,
        base_url,
        synth_model,
        query=query,
        context_lines=context_lines,
        verified_claims=verified_claims,
        deep=True,
    )
    researchstore.add_trace(run_id, "agent_draft", {"len": len(draft)})

    resp_analysis = await _deep_agentic_analyze_response(
        http,
        base_url,
        verifier_model,
        query=query,
        draft_md=draft,
        allowed_tags=allowed_tags,
    )
    researchstore.add_trace(
        run_id,
        "agent_response_analysis",
        {
            "rewrite_needed": bool(resp_analysis.get("rewrite_needed")),
            "issues": len(resp_analysis.get("issues") or []),
        },
    )

    issues_any = (
        resp_analysis.get("issues") if isinstance(resp_analysis, dict) else None
    )
    issues = (
        cast(list[dict[str, Any]], issues_any) if isinstance(issues_any, list) else []
    )
    edited = await _deep_agentic_edit(
        http,
        base_url,
        synth_model,
        query=query,
        draft_md=draft,
        issues=issues,
        allowed_tags=allowed_tags,
    )
    researchstore.add_trace(run_id, "agent_edit", {"len": len(edited)})

    formatted = await _deep_agentic_format(
        http,
        base_url,
        synth_model,
        draft_md=edited,
        deep=True,
    )
    researchstore.add_trace(run_id, "agent_format", {"len": len(formatted)})

    finalized = await _deep_agentic_finalize(
        http,
        base_url,
        synth_model,
        draft_md=formatted,
        allowed_tags=allowed_tags,
    )
    researchstore.add_trace(run_id, "agent_finalize", {"len": len(finalized)})

    # Optional: citation audit rewrite for evidence-language.
    if evidence_policy == "strict" and finalized and allowed_tags and supported_claims:
        try:
            audited = await _citation_audit_rewrite(
                http,
                base_url,
                audit_model,
                query=query,
                report_md=finalized,
                allowed_tags=allowed_tags,
                supported_claims=supported_claims,
            )
            used = extract_citation_tags(audited)
            invalid = sorted([t for t in used if t not in allowed_set])
            if audited and not invalid:
                finalized = audited
                researchstore.add_trace(run_id, "citation_audit", {"ok": True})
        except Exception as e:
            researchstore.add_trace(run_id, "citation_audit_error", {"error": str(e)})

    # Citation Contract (hard):
    # - forbid unknown citation tags
    # - for empirical stats also forbid uncited numbers
    # - in strict mode (non-creative), require at least one allowed citation tag
    if finalized and allowed_tags:
        used0 = extract_citation_tags(finalized)
        invalid0 = sorted([t for t in used0 if t not in allowed_set])
        uncited0 = (
            question_type == "empirical_stats"
        ) and _has_uncited_empirical_claims(finalized)
        missing0 = (
            evidence_policy == "strict" and question_type != "creative" and not used0
        )
        if invalid0 or uncited0 or missing0:
            researchstore.add_trace(
                run_id,
                "citation_contract",
                {
                    "ok": False,
                    "missing_citations": bool(missing0),
                    "invalid_tags": invalid0[:20],
                    "uncited_numbers": bool(uncited0),
                },
            )

            fixed = finalized
            fixed_invalid_total = 0
            for attempt in (1, 2):
                try:
                    fixed = await _rewrite_for_citation_contract(
                        http,
                        base_url,
                        audit_model,
                        query=query,
                        text=fixed,
                        allowed_tags=allowed_tags,
                        invalid_tags=sorted(
                            [
                                t
                                for t in extract_citation_tags(fixed)
                                if t not in allowed_set
                            ]
                        )[:40],
                        question_type=question_type,
                    )
                except Exception as e:
                    researchstore.add_trace(
                        run_id,
                        "citation_contract_error",
                        {"attempt": attempt, "error": str(e)},
                    )
                    break

                invalid1 = sorted(
                    [t for t in extract_citation_tags(fixed) if t not in allowed_set]
                )
                if invalid1:
                    fixed_invalid_total += len(invalid1)
                    fixed = _strip_invalid_citation_tokens(
                        fixed, allowed_tags=allowed_set
                    )

                used1 = extract_citation_tags(fixed)
                uncited1 = (
                    question_type == "empirical_stats"
                ) and _has_uncited_empirical_claims(fixed)
                missing1 = (
                    evidence_policy == "strict"
                    and question_type != "creative"
                    and not used1
                )
                if not invalid1 and not uncited1 and not missing1:
                    break

            if (question_type == "empirical_stats") and _has_uncited_empirical_claims(
                fixed
            ):
                fixed = (
                    "## Cannot Answer (Citation Contract Failed)\n\n"
                    "I could not produce a citation-grounded statistical answer from the available evidence chunks.\n\n"
                    "To answer this safely:\n"
                    "- Enable web search or configure offline Wikipedia (Kiwix), then re-run.\n"
                    "- Or upload/ingest an authoritative dataset or report.\n"
                )
                researchstore.add_trace(
                    run_id, "citation_contract", {"ok": False, "fail_closed": True}
                )
            elif (
                evidence_policy == "strict"
                and question_type != "creative"
                and not extract_citation_tags(fixed)
            ):
                fixed = (
                    "## Cannot Answer (Citation Contract Failed)\n\n"
                    "I could not produce an answer that complies with the citation contract using the available sources.\n\n"
                    "To fix this:\n"
                    "- Try a different synthesis/audit model (some models ignore citation formatting).\n"
                    "- Or broaden evidence with web/Kiwix enabled.\n"
                )
                researchstore.add_trace(
                    run_id,
                    "citation_contract",
                    {"ok": False, "fail_closed": True, "reason": "missing_citations"},
                )
            else:
                researchstore.add_trace(
                    run_id,
                    "citation_contract",
                    {"ok": True, "fixed_invalid": int(fixed_invalid_total)},
                )

            finalized = fixed

    sources_section = _format_sources_section(sources_meta)
    final = finalized
    if sources_section:
        lower = "\n" + final.lower()
        if "\n## sources" not in lower and "\nsources\n" not in lower:
            final = final.rstrip() + "\n\n" + sources_section

    researchstore.set_run_done(run_id, final)
    researchstore.add_trace(
        run_id,
        "done",
        {
            "elapsed_s": round(time.time() - started_at, 2),
            "tool_calls": tool_calls_used,
        },
    )
    return {
        "ok": True,
        "run_id": run_id,
        "answer": final,
        "sources": sources_meta_store,
        "steps": steps,
    }


def _agentic_tools_for_prompt(
    *, use_docs: bool, use_web: bool, kiwix_url: str | None
) -> list[dict[str, Any]]:
    allowed: set[str] = set()
    if use_docs:
        allowed.add("doc_search")
    if use_web:
        allowed.add("web_search")
    if kiwix_url:
        allowed.add("kiwix_search")
    return [
        t
        for t in tool_definitions()
        if str(((t.get("function") or {}).get("name") or "")).strip() in allowed
    ]


def _safe_tool_args(raw: Any) -> dict[str, Any]:
    if isinstance(raw, dict):
        return raw
    if isinstance(raw, str) and raw.strip():
        try:
            val = json.loads(raw)
        except Exception:
            return {}
        return val if isinstance(val, dict) else {}
    return {}


def _extract_tool_calls_from_msg(msg: dict[str, Any]) -> list[dict[str, Any]]:
    tc_any = msg.get("tool_calls")
    if isinstance(tc_any, list):
        return [c for c in tc_any if isinstance(c, dict)]

    # Fallback: some models print JSON in content.
    content = str(msg.get("content") or "")
    obj_any = _json_obj_from_text(content)
    if isinstance(obj_any, dict):
        tc = obj_any.get("tool_calls")
        if isinstance(tc, list):
            return [c for c in tc if isinstance(c, dict)]
    return []


def _parse_tool_call(
    call: dict[str, Any], *, index: int
) -> tuple[str, dict[str, Any], str]:
    call_id = str(call.get("id") or call.get("tool_call_id") or f"tool_call_{index}")
    fn_any = call.get("function")
    fn = fn_any if isinstance(fn_any, dict) else {}
    name = str(fn.get("name") or call.get("name") or "").strip()
    raw_args = fn.get("arguments") if fn else call.get("arguments")
    args = _safe_tool_args(raw_args)
    return (name, args, call_id)


async def _execute_research_tool(
    *,
    name: str,
    args: dict[str, Any],
    http: httpx.AsyncClient,
    ingest_queue: WebIngestQueue,
    embed_model: str,
    kiwix_url: str | None,
    doc_top_k: int,
    web_top_k: int,
    pages_per_round: int,
    domain_whitelist: list[str] | None,
    allow_epub: bool,
) -> dict[str, Any]:
    n = (name or "").strip()
    if n == "doc_search":
        req = ToolDocSearchReq.model_validate(args)
        req.top_k = max(1, min(int(req.top_k), int(doc_top_k)))
        if not bool(allow_epub):
            cur = [
                str(x).strip()
                for x in (req.exclude_group_names or [])
                if str(x).strip()
            ]
            if "epub" not in {c.lower() for c in cur}:
                cur.append("epub")
            req.exclude_group_names = cur
        return await tool_doc_search(req)

    if n == "web_search":
        req = ToolWebSearchReq.model_validate(args)
        req.top_k = max(1, min(int(req.top_k), int(web_top_k)))
        req.pages = max(1, min(int(req.pages), int(pages_per_round)))
        if domain_whitelist is not None:
            req.domain_whitelist = domain_whitelist
        return await tool_web_search(
            req,
            http=http,
            ingest_queue=ingest_queue,
            embed_model=embed_model,
            kiwix_url=kiwix_url,
        )

    if n == "kiwix_search":
        req = ToolKiwixSearchReq.model_validate(args)
        req.top_k = max(1, min(int(req.top_k), 10))
        return await tool_kiwix_search(
            req, kiwix_url=kiwix_url, embed_model=embed_model
        )

    raise ValueError(f"unknown tool: {n}")


def _tags_from_doc_hit(hit: dict[str, Any]) -> list[str]:
    raw_tags = hit.get("tags")
    if isinstance(raw_tags, list):
        return [str(x).strip().lower() for x in raw_tags if str(x).strip()]

    raw = hit.get("tags_json")
    if isinstance(raw, str) and raw.strip():
        try:
            val = json.loads(raw)
            if isinstance(val, list):
                return [str(x).strip().lower() for x in val if str(x).strip()]
        except Exception:
            return []
    return []


def _hits_from_tool_result(
    tool_name: str, payload: dict[str, Any]
) -> list[RetrievalResult]:
    out: list[RetrievalResult] = []
    t = (tool_name or "").strip()

    if t == "doc_search":
        hits_any = payload.get("results")
        hits = hits_any if isinstance(hits_any, list) else []
        for h in hits[:80]:
            if not isinstance(h, dict):
                continue
            try:
                chunk_id = int(h.get("chunk_id") or 0)
            except Exception:
                continue
            if chunk_id <= 0:
                continue

            text = str(h.get("text") or "")
            if not text.strip():
                continue

            title = str(h.get("title") or h.get("filename") or "doc").strip() or "doc"
            section = str(h.get("section") or "").strip()
            display = f"{title} — {section}" if section else title

            meta = {
                "doc_id": h.get("doc_id"),
                "chunk_index": h.get("chunk_index"),
                "doc_weight": h.get("doc_weight", 1.0),
                "group_name": h.get("group_name"),
                "filename": h.get("filename"),
                "title": h.get("title"),
                "author": h.get("author"),
                "path": h.get("path"),
                "source": h.get("source"),
                "section": h.get("section"),
                "tags": _tags_from_doc_hit(h),
            }

            try:
                score = float(h.get("score") or 0.0)
            except Exception:
                score = 0.0

            out.append(
                RetrievalResult(
                    source_type="doc",
                    ref_id=f"doc:{chunk_id}",
                    chunk_id=chunk_id,
                    title=display,
                    url=None,
                    domain=None,
                    score=score,
                    text=text,
                    meta=meta,
                )
            )
        return out

    if t == "web_search":
        hits_any = payload.get("results")
        hits = hits_any if isinstance(hits_any, list) else []
        for h in hits[:120]:
            if not isinstance(h, dict):
                continue
            if str(h.get("source_type") or "").strip().lower() != "web":
                continue
            try:
                chunk_id = int(h.get("chunk_id") or 0)
            except Exception:
                continue
            if chunk_id <= 0:
                continue
            text = str(h.get("text") or "")
            if not text.strip():
                continue
            try:
                score = float(h.get("score") or 0.0)
            except Exception:
                score = 0.0
            out.append(
                RetrievalResult(
                    source_type="web",
                    ref_id=f"web:{chunk_id}",
                    chunk_id=chunk_id,
                    title=str(
                        h.get("title") or h.get("domain") or h.get("url") or "web"
                    )[:260],
                    url=str(h.get("url") or "")[:2048] or None,
                    domain=str(h.get("domain") or "")[:260] or None,
                    score=score,
                    text=text,
                    meta={
                        "page_id": h.get("page_id"),
                        "chunk_index": h.get("chunk_index"),
                    },
                )
            )
        return out

    if t == "kiwix_search":
        hits_any = payload.get("results")
        hits = hits_any if isinstance(hits_any, list) else []
        for h in hits[:60]:
            if not isinstance(h, dict):
                continue
            st = str(h.get("source_type") or "").strip().lower()
            if st != "kiwix":
                continue
            try:
                chunk_id = int(h.get("chunk_id") or 0)
            except Exception:
                continue
            if chunk_id <= 0:
                continue
            text = str(h.get("text") or "")
            if not text.strip():
                continue
            try:
                score = float(h.get("score") or 0.0)
            except Exception:
                score = 0.0
            meta_any = h.get("meta")
            meta = meta_any if isinstance(meta_any, dict) else {}
            out.append(
                RetrievalResult(
                    source_type="kiwix",
                    ref_id=str(h.get("ref_id") or f"kiwix:{chunk_id}"),
                    chunk_id=chunk_id,
                    title=str(h.get("title") or "kiwix")[:260],
                    url=str(h.get("url") or "")[:2048] or None,
                    domain=str(h.get("domain") or "")[:260] or None,
                    score=score,
                    text=text,
                    meta=meta,
                )
            )
        return out

    return out


async def _agentic_parse_supported_claims(
    http: httpx.AsyncClient,
    base_url: str,
    model: str,
    *,
    query: str,
    subquestions: list[str],
    supported_claims: list[dict[str, Any]],
) -> dict[str, Any]:
    prompt = (
        "Return ONLY JSON.\n"
        'Schema: {"facts":[{"fact":"...","citations":["D1"],"notes":"..."}],"by_subquestion":{"...":[0]}}\n\n'
        "Task: Convert Supported claims into short factual notes with citations.\n\n"
        f"Question:\n{query}\n\n"
        f"Subquestions:\n{json.dumps(subquestions, ensure_ascii=False)}\n\n"
        f"Supported claims JSON:\n{json.dumps(supported_claims, ensure_ascii=False)}\n"
    )
    out = await _ollama_chat_once(
        http, base_url, model, [{"role": "user", "content": prompt}], timeout=45.0
    )
    obj_any = _json_obj_from_text(out) or {}
    return obj_any if isinstance(obj_any, dict) else {}


async def _agentic_analyze_coverage(
    http: httpx.AsyncClient,
    base_url: str,
    model: str,
    *,
    query: str,
    topics: list[str],
    subquestions: list[str],
    facts_json: dict[str, Any],
) -> dict[str, Any]:
    prompt = (
        "Return ONLY JSON.\n"
        'Schema: {"need_more_tools":true|false,"missing":["..."],"reason":"..."}.\n\n'
        "Task: Decide if the evidence-backed facts are sufficient to answer the user question.\n"
        "Be strict about missing or unsupported parts.\n\n"
        f"Question:\n{query}\n\n"
        f"Topics:\n{json.dumps(topics, ensure_ascii=False)}\n\n"
        f"Subquestions:\n{json.dumps(subquestions, ensure_ascii=False)}\n\n"
        f"Facts JSON:\n{json.dumps(facts_json, ensure_ascii=False)}\n"
    )
    out = await _ollama_chat_once(
        http, base_url, model, [{"role": "user", "content": prompt}], timeout=35.0
    )
    obj_any = _json_obj_from_text(out) or {}
    return obj_any if isinstance(obj_any, dict) else {}


async def _agentic_break_down_further(
    http: httpx.AsyncClient,
    base_url: str,
    model: str,
    *,
    query: str,
    missing: list[str],
    enabled_tools: list[str],
    tool_budget_remaining: int,
) -> dict[str, Any]:
    prompt = (
        "Return ONLY JSON.\n"
        'Schema: {"tool_calls":[{"name":"doc_search|web_search|kiwix_search","arguments":{...}}],"notes":"..."}.\n\n'
        "Task: Turn missing items into concrete tool calls. Keep queries short and specific.\n"
        "Do not exceed tool_budget_remaining tool calls.\n\n"
        f"Question:\n{query}\n\n"
        f"Missing:\n{json.dumps(missing, ensure_ascii=False)}\n\n"
        f"Enabled tools:\n{json.dumps(enabled_tools, ensure_ascii=False)}\n\n"
        f"tool_budget_remaining: {tool_budget_remaining}\n"
    )
    out = await _ollama_chat_once(
        http, base_url, model, [{"role": "user", "content": prompt}], timeout=40.0
    )
    obj_any = _json_obj_from_text(out) or {}
    return obj_any if isinstance(obj_any, dict) else {}


async def _agentic_critique_response(
    http: httpx.AsyncClient,
    base_url: str,
    model: str,
    *,
    query: str,
    draft_md: str,
    allowed_tags: list[str],
) -> dict[str, Any]:
    prompt = (
        "Return ONLY JSON.\n"
        'Schema: {"issues":[{"type":"missing_citation|unsupported|overstated|format","detail":"..."}],"rewrite_needed":true|false}.\n\n'
        "Task: Critique the DRAFT for unsupported claims, missing citations, and overstated language.\n"
        "Citations must use ONLY tags in allowed_tags.\n\n"
        f"Question:\n{query}\n\n"
        f"allowed_tags:\n{json.dumps(allowed_tags, ensure_ascii=False)}\n\n"
        "DRAFT:\n" + (draft_md or "")
    )
    out = await _ollama_chat_once(
        http, base_url, model, [{"role": "user", "content": prompt}], timeout=40.0
    )
    obj_any = _json_obj_from_text(out) or {}
    return obj_any if isinstance(obj_any, dict) else {}


async def _agentic_rewrite(
    http: httpx.AsyncClient,
    base_url: str,
    model: str,
    *,
    query: str,
    text: str,
    instruction: str,
    allowed_tags: list[str],
) -> str:
    prompt = (
        instruction.strip()
        + "\n\nRules:\n- Use ONLY citations in allowed_tags.\n- Do NOT add a Sources section.\n\n"
        + f"Question:\n{query}\n\n"
        + f"allowed_tags:\n{json.dumps(allowed_tags, ensure_ascii=False)}\n\n"
        + "TEXT:\n"
        + (text or "")
    )
    out = await _ollama_chat_once(
        http, base_url, model, [{"role": "user", "content": prompt}], timeout=60.0
    )
    return (out or "").strip()


async def _run_deep_research_agentic_alt(
    *,
    http: httpx.AsyncClient,
    base_url: str,
    ingest_queue: WebIngestQueue,
    kiwix_url: str | None,
    run_id: str,
    query: str,
    plan: dict[str, Any],
    use_docs: bool,
    use_web: bool,
    rounds: int,
    pages_per_round: int,
    web_top_k: int,
    doc_top_k: int,
    domain_whitelist: list[str] | None,
    embed_model: str,
    planner_model: str,
    verifier_model: str,
    synth_model: str,
    settings: dict[str, Any],
    steps: list[dict[str, Any]],
    evidence_policy: str,
    strict_fail_behavior: str,
    strict_allowlist: list[str],
    kiwix_zim_allowlist: list[str],
    epub_default_genre: str,
    epub_nonfiction_is_evidence: bool,
    epub_reference_is_evidence: bool,
    epub_fiction_is_evidence: bool,
    trust_tiers: dict[str, float],
    genre_classifier_model: str,
    audit_model: str,
) -> dict[str, Any]:
    max_tool_calls = int(settings.get("max_tool_calls") or MAX_DEEP_TOOL_CALLS)
    max_tool_calls = max(1, min(max_tool_calls, 200))
    max_tool_calls_per_step = int(settings.get("max_tool_calls_per_step") or 6)
    max_tool_calls_per_step = max(1, min(max_tool_calls_per_step, 12))

    # Heuristic: allow more planning iterations than legacy rounds.
    max_steps = int(settings.get("agent_steps") or max(6, min(30, int(rounds) * 6)))

    enabled_tools = _agentic_tools_for_prompt(
        use_docs=use_docs, use_web=use_web, kiwix_url=kiwix_url
    )
    enabled_tool_names = [
        str(((t.get("function") or {}).get("name") or "")).strip()
        for t in enabled_tools
    ]
    enabled_tool_names = [n for n in enabled_tool_names if n]
    enabled_tool_set = set(enabled_tool_names)

    pool: dict[str, RetrievalResult] = {}
    tool_calls_used = 0
    seen_tool_sigs: set[str] = set()

    topics = plan.get("topics") or []
    subquestions = plan.get("subquestions") or []
    done_if = plan.get("done_if") or []

    last_assess: dict[str, Any] = {}
    last_gap: dict[str, Any] = {}
    last_verify: dict[str, Any] = {"claims": []}

    # Main tool loop: each step is a separate model call.
    for step_no in range(1, max_steps + 1):
        remaining = max(0, max_tool_calls - tool_calls_used)
        if remaining <= 0:
            break
        if not enabled_tool_names:
            break

        # Step: tool-plan model call
        tool_plan_prompt = (
            "You are a deep research tool planner. Use tool calls to gather evidence for the user's question.\n\n"
            "Rules:\n"
            "- Prefer evidence-eligible sources in strict mode (kiwix/wiki, web, uploaded docs).\n"
            "- If a tool is not enabled, do not call it.\n"
            "- Call at most 6 tools per step.\n"
            "- If you think we have enough evidence, do not call tools and instead say DONE in content.\n\n"
            f"Enabled tools: {', '.join(enabled_tool_names)}\n"
            f"Evidence policy: {evidence_policy}\n"
            f"Tool budget remaining: {remaining}\n"
        )

        supported_claims = [
            c
            for c in (last_verify.get("claims") or [])
            if isinstance(c, dict)
            and str(c.get("status") or "").strip().lower() == "supported"
        ]

        user_state = {
            "query": query,
            "topics": topics,
            "subquestions": subquestions,
            "done_if": done_if,
            "supported_claims": [
                {
                    "claim": str(c.get("claim") or "")[:600],
                    "citations": c.get("citations")
                    if isinstance(c.get("citations"), list)
                    else [],
                    "evidence": c.get("evidence")
                    if isinstance(c.get("evidence"), list)
                    else [],
                }
                for c in supported_claims[:12]
            ],
            "last_assess": {
                k: last_assess.get(k)
                for k in (
                    "relevant",
                    "reason",
                    "doc_queries",
                    "web_queries",
                    "kiwix_query",
                )
            },
            "last_gap": {
                k: last_gap.get(k)
                for k in (
                    "done",
                    "reason",
                    "missing_topics",
                    "doc_queries",
                    "web_queries",
                    "kiwix_query",
                )
            },
            "tool_budget_remaining": remaining,
        }

        msg = await _ollama_chat_message_once(
            http=http,
            base_url=base_url,
            model=planner_model,
            messages=[
                {"role": "system", "content": tool_plan_prompt},
                {"role": "user", "content": json.dumps(user_state, ensure_ascii=False)},
            ],
            tools=enabled_tools,
            timeout=45.0,
        )
        tool_calls = _extract_tool_calls_from_msg(msg)
        researchstore.add_trace(
            run_id,
            "agent_tool_plan",
            {
                "step": step_no,
                "tool_calls": len(tool_calls),
                "content": str(msg.get("content") or "")[:400],
            },
        )

        if not tool_calls:
            # If model explicitly says done, stop; otherwise stop to avoid spinning.
            content = str(msg.get("content") or "").strip().lower()
            if content.startswith("done") or content.startswith("enough"):
                break
            break

        # Execute tools (non-model step)
        ran = 0
        step_tool_results: list[dict[str, Any]] = []
        for idx, call in enumerate(tool_calls[:max_tool_calls_per_step], start=1):
            if tool_calls_used >= max_tool_calls:
                break
            name, args, call_id = _parse_tool_call_alt(call, idx)
            if not name or name not in enabled_tool_set:
                step_tool_results.append(
                    {
                        "ok": False,
                        "tool": name,
                        "call_id": call_id,
                        "error": "tool_not_enabled",
                    }
                )
                continue

            sig = name + ":" + json.dumps(args, sort_keys=True, ensure_ascii=False)
            if sig in seen_tool_sigs:
                step_tool_results.append(
                    {
                        "ok": False,
                        "tool": name,
                        "call_id": call_id,
                        "error": "duplicate",
                    }
                )
                continue
            seen_tool_sigs.add(sig)

            started = time.time()
            try:
                result = await _execute_research_tool_alt(
                    name=name,
                    args=args,
                    http=http,
                    ingest_queue=ingest_queue,
                    embed_model=embed_model,
                    kiwix_url=kiwix_url,
                    doc_top_k=doc_top_k,
                    web_top_k=web_top_k,
                    pages_per_round=pages_per_round,
                    domain_whitelist=domain_whitelist,
                    allow_epub=bool(settings.get("allow_epub")),
                )
                took_ms = int((time.time() - started) * 1000)
                step_tool_results.append(
                    {
                        "ok": True,
                        "tool": name,
                        "call_id": call_id,
                        "took_ms": took_ms,
                        "result": {"keys": list(result.keys())},
                    }
                )
                # Merge hits
                payload_any = result.get("result") if isinstance(result, dict) else None
                payload = payload_any if isinstance(payload_any, dict) else {}
                for hit in _hits_from_tool_result_alt(name, payload):
                    prev = pool.get(hit.ref_id)
                    if prev is None or float(hit.score or 0.0) > float(
                        prev.score or 0.0
                    ):
                        pool[hit.ref_id] = hit
            except Exception as e:
                took_ms = int((time.time() - started) * 1000)
                step_tool_results.append(
                    {
                        "ok": False,
                        "tool": name,
                        "call_id": call_id,
                        "took_ms": took_ms,
                        "error": str(e)[:400],
                    }
                )

            tool_calls_used += 1
            ran += 1

        researchstore.add_trace(
            run_id,
            "agent_tools_ran",
            {
                "step": step_no,
                "ran": ran,
                "tool_calls_used": tool_calls_used,
                "results": step_tool_results,
            },
        )

        # Apply evidence gate + build evidence-only context
        flags = researchstore.get_source_flags_by_ref_id(run_id)
        pinned_ref_ids = {
            ref for ref, f in flags.items() if isinstance(f, dict) and f.get("pinned")
        }
        excluded_ref_ids = {
            ref for ref, f in flags.items() if isinstance(f, dict) and f.get("excluded")
        }

        all_hits = list(pool.values())
        (
            evidence_hits,
            _context_only_hits,
            gate_stats,
        ) = await _annotate_provenance_and_partition_hits(
            http=http,
            base_url=base_url,
            model=genre_classifier_model,
            hits=all_hits,
            policy=evidence_policy,
            strict_allowlist=strict_allowlist,
            kiwix_zim_allowlist=kiwix_zim_allowlist,
            epub_default_genre=epub_default_genre,
            epub_nonfiction_is_evidence=epub_nonfiction_is_evidence,
            epub_reference_is_evidence=epub_reference_is_evidence,
            epub_fiction_is_evidence=epub_fiction_is_evidence,
            trust_tiers=trust_tiers,
        )
        researchstore.add_trace(
            run_id, "evidence_gate", {"step": step_no, **gate_stats}
        )

        sources_meta_store = _sources_meta_from_hits(
            all_hits,
            pinned_ref_ids=pinned_ref_ids,
            excluded_ref_ids=excluded_ref_ids,
            limit=80,
        )
        researchstore.upsert_sources(run_id, sources_meta_store)

        max_chars = 20000
        per_source_cap = 8
        sources_meta, context_lines = build_context(
            evidence_hits,
            max_chars=max_chars,
            per_source_cap=per_source_cap,
            pinned_ref_ids=pinned_ref_ids,
            excluded_ref_ids=excluded_ref_ids,
            preserve_order=True,
        )
        researchstore.add_trace(
            run_id,
            "evidence_context",
            {
                "step": step_no,
                "sources": len(sources_meta),
                "lines": len(context_lines),
            },
        )

        # Strict-mode guardrail: if we have no evidence context, keep trying if possible.
        if evidence_policy == "strict" and not context_lines:
            if (
                step_no < max_steps
                and tool_calls_used < max_tool_calls
                and (use_web or bool(kiwix_url))
            ):
                continue
            # fall through to end; final strict gate handled later

        # Step: relevance assessment model call
        try:
            last_assess = await _assess_sources_relevance_and_refine_queries(
                http,
                base_url,
                planner_model,
                query=query,
                sources_meta=sources_meta_store,
                use_docs=use_docs,
                use_web=use_web,
                kiwix_enabled=bool(kiwix_url),
            )
            researchstore.add_trace(
                run_id,
                "assess",
                {
                    "step": step_no,
                    "relevant": last_assess.get("relevant"),
                    "reason": last_assess.get("reason"),
                },
            )
            steps.append(
                {
                    "type": "assess",
                    "step": step_no,
                    "relevant": bool(last_assess.get("relevant")),
                    "reason": str(last_assess.get("reason") or "")[:800],
                }
            )
        except Exception as e:
            last_assess = {}
            researchstore.add_trace(
                run_id, "assess_error", {"step": step_no, "error": str(e)}
            )

        # Step: verify claims model call
        last_verify = await _verify_claims(
            http, base_url, verifier_model, query, context_lines
        )
        researchstore.clear_claims(run_id)
        researchstore.add_claims(run_id, last_verify.get("claims") or [])
        researchstore.add_trace(
            run_id,
            "verify",
            {"step": step_no, "claims": len(last_verify.get("claims") or [])},
        )

        supported_claims = [
            c
            for c in (last_verify.get("claims") or [])
            if isinstance(c, dict) and c.get("status") == "supported"
        ]

        # Step: gap check model call
        try:
            last_gap = await _gap_check_and_refine_queries(
                http,
                base_url,
                verifier_model,
                query=query,
                topics=topics if isinstance(topics, list) else [],
                subquestions=subquestions if isinstance(subquestions, list) else [],
                supported_claims=supported_claims,
                use_docs=use_docs,
                use_web=use_web,
                kiwix_enabled=bool(kiwix_url),
            )
            researchstore.add_trace(
                run_id,
                "gap",
                {
                    "step": step_no,
                    "done": last_gap.get("done"),
                    "reason": last_gap.get("reason"),
                },
            )
            steps.append(
                {
                    "type": "gap",
                    "step": step_no,
                    "done": bool(last_gap.get("done")),
                    "reason": str(last_gap.get("reason") or "")[:800],
                }
            )
        except Exception as e:
            last_gap = {}
            researchstore.add_trace(
                run_id, "gap_error", {"step": step_no, "error": str(e)}
            )

        # Step: done_if model call
        if done_if:
            try:
                done_check = await _check_done_if(
                    http,
                    base_url,
                    verifier_model,
                    query=query,
                    done_if=[str(x) for x in done_if if str(x).strip()],
                    supported_claims=supported_claims,
                )
                researchstore.add_trace(
                    run_id,
                    "done_if",
                    {
                        "step": step_no,
                        "done": done_check.get("done"),
                        "reason": done_check.get("reason"),
                    },
                )
                if bool(done_check.get("done")):
                    break
            except Exception as e:
                researchstore.add_trace(
                    run_id, "done_if_error", {"step": step_no, "error": str(e)}
                )

        # Termination heuristic
        if bool(last_gap.get("done")) and len(supported_claims) >= 6:
            break

    # Final context build from the best evidence we have
    flags = researchstore.get_source_flags_by_ref_id(run_id)
    pinned_ref_ids = {
        ref for ref, f in flags.items() if isinstance(f, dict) and f.get("pinned")
    }
    excluded_ref_ids = {
        ref for ref, f in flags.items() if isinstance(f, dict) and f.get("excluded")
    }

    all_hits = list(pool.values())
    (
        evidence_hits,
        _context_only_hits,
        gate_stats,
    ) = await _annotate_provenance_and_partition_hits(
        http=http,
        base_url=base_url,
        model=genre_classifier_model,
        hits=all_hits,
        policy=evidence_policy,
        strict_allowlist=strict_allowlist,
        kiwix_zim_allowlist=kiwix_zim_allowlist,
        epub_default_genre=epub_default_genre,
        epub_nonfiction_is_evidence=epub_nonfiction_is_evidence,
        epub_reference_is_evidence=epub_reference_is_evidence,
        epub_fiction_is_evidence=epub_fiction_is_evidence,
        trust_tiers=trust_tiers,
    )
    researchstore.add_trace(run_id, "evidence_gate_final", gate_stats)

    sources_meta_store = _sources_meta_from_hits(
        all_hits,
        pinned_ref_ids=pinned_ref_ids,
        excluded_ref_ids=excluded_ref_ids,
        limit=100,
    )
    researchstore.upsert_sources(run_id, sources_meta_store)

    max_chars = 20000
    per_source_cap = 8
    sources_meta, context_lines = build_context(
        evidence_hits,
        max_chars=max_chars,
        per_source_cap=per_source_cap,
        pinned_ref_ids=pinned_ref_ids,
        excluded_ref_ids=excluded_ref_ids,
        preserve_order=True,
    )

    # Hard evidence gate: strict mode refuses when no evidence-eligible sources exist.
    if evidence_policy == "strict" and not context_lines:
        by_kind = gate_stats.get("by_kind") if isinstance(gate_stats, dict) else {}
        epub_by_genre = (
            gate_stats.get("epub_by_genre") if isinstance(gate_stats, dict) else {}
        )
        researchstore.add_trace(
            run_id,
            "guardrail",
            {
                "reason": "no_evidence_sources",
                "by_kind": by_kind,
                "epub_by_genre": epub_by_genre,
            },
        )
        if strict_fail_behavior == "speculative":
            ctx_items: list[dict[str, Any]] = []
            for s in sources_meta_store:
                if not isinstance(s, dict):
                    continue
                ctx_items.append({"title": s.get("title"), "snippet": s.get("snippet")})
                if len(ctx_items) >= 12:
                    break
            answer = await _synthesize_speculative_no_evidence(
                http, base_url, synth_model, query=query, context_items=ctx_items
            )
        else:
            answer = (
                "No evidence found in enabled sources (evidence_policy=strict).\n\n"
                f"Retrieved kinds: {json.dumps(by_kind, ensure_ascii=False)}\n"
                f"EPUB genres: {json.dumps(epub_by_genre, ensure_ascii=False)}\n\n"
                "Fixes:\n"
                "- Configure offline Wikipedia (Kiwix) and set `KIWIX_URL`, then re-run.\n"
                "- Or re-run with web enabled: `/research --web ...` or `/deep --web ...`.\n"
                "- Or ingest/upload nonfiction/reference documents."
            )

        researchstore.set_run_done(run_id, answer)
        return {
            "ok": True,
            "run_id": run_id,
            "answer": answer,
            "sources": sources_meta_store,
            "steps": steps,
        }

    # Parse/analyze/break down further (each as its own model call)
    supported_claims = [
        c
        for c in (last_verify.get("claims") or [])
        if isinstance(c, dict)
        and str(c.get("status") or "").strip().lower() == "supported"
    ]

    facts_json = await _agentic_parse_supported_claims(
        http,
        base_url,
        verifier_model,
        query=query,
        subquestions=[str(x) for x in (subquestions or []) if str(x).strip()],
        supported_claims=supported_claims,
    )
    researchstore.add_trace(
        run_id,
        "agent_parse",
        {
            "facts": len(facts_json.get("facts") or [])
            if isinstance(facts_json, dict)
            else 0
        },
    )

    coverage = await _agentic_analyze_coverage(
        http,
        base_url,
        verifier_model,
        query=query,
        topics=[str(x) for x in (topics or []) if str(x).strip()],
        subquestions=[str(x) for x in (subquestions or []) if str(x).strip()],
        facts_json=facts_json if isinstance(facts_json, dict) else {},
    )
    researchstore.add_trace(run_id, "agent_analyze", coverage)

    # Make more tool calls if necessary (model call -> execute)
    need_more_tools = bool(coverage.get("need_more_tools"))
    missing_val = coverage.get("missing")
    missing_any = missing_val if isinstance(missing_val, list) else []
    tool_budget_remaining = max(0, max_tool_calls - tool_calls_used)
    if need_more_tools and tool_budget_remaining > 0 and enabled_tool_names:
        breakdown = await _agentic_break_down_further(
            http,
            base_url,
            planner_model,
            query=query,
            missing=[str(x) for x in missing_any if str(x).strip()][:12],
            enabled_tools=enabled_tool_names,
            tool_budget_remaining=tool_budget_remaining,
        )
        tc_any0 = breakdown.get("tool_calls") if isinstance(breakdown, dict) else None
        tc_list0 = tc_any0 if isinstance(tc_any0, list) else []
        researchstore.add_trace(
            run_id,
            "agent_breakdown",
            {"missing": len(missing_any), "tool_calls": len(tc_list0)},
        )

        tc_any = breakdown.get("tool_calls")
        tc_list = tc_any if isinstance(tc_any, list) else []
        for i, tc in enumerate(tc_list[: min(tool_budget_remaining, 12)], start=1):
            if tool_calls_used >= max_tool_calls:
                break
            if not isinstance(tc, dict):
                continue
            nm = str(tc.get("name") or "").strip()
            if nm not in enabled_tool_set:
                continue
            args_any = tc.get("arguments")
            args = args_any if isinstance(args_any, dict) else {}
            sig = nm + ":" + json.dumps(args, sort_keys=True, ensure_ascii=False)
            if sig in seen_tool_sigs:
                continue
            seen_tool_sigs.add(sig)
            try:
                result = await _execute_research_tool_alt(
                    name=nm,
                    args=args,
                    http=http,
                    ingest_queue=ingest_queue,
                    embed_model=embed_model,
                    kiwix_url=kiwix_url,
                    doc_top_k=doc_top_k,
                    web_top_k=web_top_k,
                    pages_per_round=pages_per_round,
                    domain_whitelist=domain_whitelist,
                    allow_epub=bool(settings.get("allow_epub")),
                )
                payload_any = result.get("result") if isinstance(result, dict) else None
                payload = payload_any if isinstance(payload_any, dict) else {}
                for hit in _hits_from_tool_result_alt(nm, payload):
                    prev = pool.get(hit.ref_id)
                    if prev is None or float(hit.score or 0.0) > float(
                        prev.score or 0.0
                    ):
                        pool[hit.ref_id] = hit
            except Exception:
                pass
            tool_calls_used += 1

        # Rebuild context + re-verify (separate model call)
        all_hits = list(pool.values())
        (
            evidence_hits,
            _context_only_hits,
            _,
        ) = await _annotate_provenance_and_partition_hits(
            http=http,
            base_url=base_url,
            model=genre_classifier_model,
            hits=all_hits,
            policy=evidence_policy,
            strict_allowlist=strict_allowlist,
            kiwix_zim_allowlist=kiwix_zim_allowlist,
            epub_default_genre=epub_default_genre,
            epub_nonfiction_is_evidence=epub_nonfiction_is_evidence,
            epub_reference_is_evidence=epub_reference_is_evidence,
            epub_fiction_is_evidence=epub_fiction_is_evidence,
            trust_tiers=trust_tiers,
        )
        sources_meta, context_lines = build_context(
            evidence_hits,
            max_chars=max_chars,
            per_source_cap=per_source_cap,
            pinned_ref_ids=pinned_ref_ids,
            excluded_ref_ids=excluded_ref_ids,
            preserve_order=True,
        )
        last_verify = await _verify_claims(
            http, base_url, verifier_model, query, context_lines
        )
        researchstore.clear_claims(run_id)
        researchstore.add_claims(run_id, last_verify.get("claims") or [])
        researchstore.add_trace(
            run_id,
            "verify",
            {"step": "post_breakdown", "claims": len(last_verify.get("claims") or [])},
        )

    # Construct response (model call)
    final = await _synthesize(
        http,
        base_url,
        synth_model,
        query,
        mode="deep",
        context_lines=context_lines,
        verified_claims=last_verify.get("claims") or [],
        embed_model=embed_model,
        ingest_queue=ingest_queue,
        kiwix_url=kiwix_url,
    )

    allowed_tags = [
        str(s.get("citation") or "").strip()
        for s in sources_meta
        if str(s.get("citation") or "").strip()
    ]
    allowed_set = set(allowed_tags)

    # Analyze response (model call)
    critique = await _agentic_critique_response(
        http,
        base_url,
        verifier_model,
        query=query,
        draft_md=final,
        allowed_tags=allowed_tags,
    )
    researchstore.add_trace(run_id, "agent_response_analyze", critique)

    # Edit response (model call)
    issues = critique.get("issues") if isinstance(critique.get("issues"), list) else []
    if bool(critique.get("rewrite_needed")) and issues:
        final = await _agentic_rewrite(
            http,
            base_url,
            synth_model,
            query=query,
            text=final,
            instruction="Rewrite the answer to fix the listed issues. Remove unsupported claims and add missing citations.",
            allowed_tags=allowed_tags,
        )

    # Format response (model call)
    final = await _agentic_rewrite(
        http,
        base_url,
        synth_model,
        query=query,
        text=final,
        instruction="Format the answer cleanly in Markdown with consistent headings and short paragraphs/bullets.",
        allowed_tags=allowed_tags,
    )

    # Finalize response (model call)
    final = await _agentic_rewrite(
        http,
        base_url,
        synth_model,
        query=query,
        text=final,
        instruction="Final pass: make it concise, high-signal, and strictly grounded. Ensure every factual sentence has a citation.",
        allowed_tags=allowed_tags,
    )

    # Citation audit rewrite pass (strict) to fail closed.
    if evidence_policy == "strict" and allowed_tags:
        supported_only = [
            c
            for c in (last_verify.get("claims") or [])
            if isinstance(c, dict)
            and str(c.get("status") or "").strip().lower() == "supported"
        ]
        if supported_only:
            audited = await _citation_audit_rewrite(
                http,
                base_url,
                audit_model,
                query=query,
                report_md=final,
                allowed_tags=allowed_tags,
                supported_claims=supported_only,
            )
            used = extract_citation_tags(audited)
            invalid = [t for t in used if t not in allowed_set]
            if audited and not invalid:
                final = audited

    sources_section = _format_sources_section(sources_meta)
    if sources_section:
        lower = "\n" + final.lower()
        if "\n## sources" not in lower and "\nsources\n" not in lower:
            final = final.rstrip() + "\n\n" + sources_section

    researchstore.set_run_done(run_id, final)
    researchstore.add_trace(
        run_id, "done", {"len": len(final), "tool_calls_used": tool_calls_used}
    )

    return {
        "ok": True,
        "run_id": run_id,
        "answer": final,
        "sources": sources_meta_store,
        "steps": steps,
    }


def _research_tools_for_prompt(
    *, use_docs: bool, use_web: bool, kiwix_url: str | None
) -> list[dict[str, Any]]:
    tools = tool_definitions()
    allowed: set[str] = set()
    if bool(use_docs):
        allowed.add("doc_search")
    if bool(use_web):
        allowed.add("web_search")
    if bool(kiwix_url):
        allowed.add("kiwix_search")
    out: list[dict[str, Any]] = []
    for t in tools:
        fn = (t or {}).get("function") if isinstance(t, dict) else None
        name = (fn or {}).get("name") if isinstance(fn, dict) else None
        if isinstance(name, str) and name in allowed:
            out.append(t)
    return out


def _normalize_tool_calls_from_message(msg: dict[str, Any]) -> list[dict[str, Any]]:
    """Return tool calls as list of dicts.

    Prefer native Ollama tool_calls; fallback to JSON emitted in content.
    """

    raw = msg.get("tool_calls")
    if isinstance(raw, list) and raw:
        return [tc for tc in raw if isinstance(tc, dict)]

    content = str(msg.get("content") or "").strip()
    if not content:
        return []

    obj = _json_obj_from_text(content) or {}
    if isinstance(obj, dict):
        tc = obj.get("tool_calls")
        if isinstance(tc, list):
            return [x for x in tc if isinstance(x, dict)]
        # Accept a single tool call object.
        if isinstance(obj.get("name"), str) and isinstance(
            obj.get("arguments"), (dict, str)
        ):
            return [
                {
                    "id": "tool_call_1",
                    "function": {
                        "name": obj.get("name"),
                        "arguments": obj.get("arguments"),
                    },
                }
            ]

    return []


def _parse_tool_call_alt(
    tc: dict[str, Any], idx: int
) -> tuple[str, dict[str, Any], str]:
    call_id = str(tc.get("id") or tc.get("tool_call_id") or f"tool_call_{idx}")

    fn_any = tc.get("function") or {}
    fn = fn_any if isinstance(fn_any, dict) else {}
    name = fn.get("name") or tc.get("name") or ""
    name = str(name or "").strip()

    raw_args = fn.get("arguments") if "arguments" in fn else tc.get("arguments")
    if isinstance(raw_args, dict):
        args = raw_args
    elif isinstance(raw_args, str) and raw_args.strip():
        try:
            parsed = json.loads(raw_args)
            args = parsed if isinstance(parsed, dict) else {}
        except Exception:
            args = {}
    else:
        args = {}

    return (name, args, call_id)


async def _execute_research_tool_alt(
    *,
    name: str,
    args: dict[str, Any],
    http: httpx.AsyncClient,
    ingest_queue: WebIngestQueue,
    embed_model: str,
    kiwix_url: str | None,
    domain_whitelist: list[str] | None,
    pages_per_round: int,
    web_top_k: int,
    doc_top_k: int,
    allow_epub: bool,
) -> dict[str, Any]:
    tool = (name or "").strip()
    if tool == "doc_search":
        req = ToolDocSearchReq.model_validate(args)
        req.top_k = max(1, min(int(req.top_k), int(doc_top_k)))
        if not bool(allow_epub):
            cur = [
                str(x).strip()
                for x in (req.exclude_group_names or [])
                if str(x).strip()
            ]
            if "epub" not in {c.lower() for c in cur}:
                cur.append("epub")
            req.exclude_group_names = cur
        return {"tool": tool, "ok": True, "result": await tool_doc_search(req)}
    if tool == "web_search":
        req = ToolWebSearchReq.model_validate(args)
        req.top_k = max(1, min(int(req.top_k), int(web_top_k)))
        req.pages = max(1, min(int(req.pages), int(pages_per_round)))
        # Always honor the request-level domain whitelist.
        if domain_whitelist:
            req.domain_whitelist = domain_whitelist
        return {
            "tool": tool,
            "ok": True,
            "result": await tool_web_search(
                req,
                http=http,
                ingest_queue=ingest_queue,
                embed_model=embed_model,
                kiwix_url=kiwix_url,
            ),
        }
    if tool == "kiwix_search":
        req = ToolKiwixSearchReq.model_validate(args)
        req.top_k = max(1, min(int(req.top_k), 10))
        return {
            "tool": tool,
            "ok": True,
            "result": await tool_kiwix_search(
                req, kiwix_url=kiwix_url, embed_model=embed_model
            ),
        }
    return {"tool": tool, "ok": False, "error": f"unknown tool: {tool}"}


def _parse_tags_json(raw: Any) -> list[str]:
    if not isinstance(raw, str) or not raw.strip():
        return []
    try:
        val = json.loads(raw)
    except Exception:
        return []
    if not isinstance(val, list):
        return []
    out: list[str] = []
    seen: set[str] = set()
    for x in val:
        t = str(x).strip().lower()
        if not t or t in seen:
            continue
        seen.add(t)
        out.append(t)
    return out


def _hits_from_tool_result_alt(
    tool: str, result: dict[str, Any]
) -> list[RetrievalResult]:
    tool = (tool or "").strip()
    out: list[RetrievalResult] = []

    if tool == "doc_search":
        rows = result.get("results")
        hits = rows if isinstance(rows, list) else []
        for h in hits[:50]:
            if not isinstance(h, dict):
                continue
            chunk_raw = h.get("chunk_id")
            if chunk_raw is None:
                continue
            try:
                chunk_id = int(str(chunk_raw))
            except Exception:
                continue
            text = str(h.get("text") or "")
            if not text.strip():
                continue
            title = h.get("title") or h.get("filename")
            section = h.get("section")
            display = str(title or "doc").strip()
            if section:
                display = f"{display} — {str(section).strip()}"
            tags = _parse_tags_json(h.get("tags_json"))

            out.append(
                RetrievalResult(
                    source_type="doc",
                    ref_id=f"doc:{chunk_id}",
                    chunk_id=chunk_id,
                    title=display,
                    url=None,
                    domain=None,
                    score=float(h.get("score") or 0.0),
                    text=text,
                    meta={
                        "doc_id": h.get("doc_id"),
                        "chunk_index": h.get("chunk_index"),
                        "doc_weight": h.get("doc_weight", 1.0),
                        "group_name": h.get("group_name"),
                        "filename": h.get("filename"),
                        "title": h.get("title"),
                        "author": h.get("author"),
                        "path": h.get("path"),
                        "source": h.get("source"),
                        "section": h.get("section"),
                        "tags": tags,
                    },
                )
            )
        return out

    if tool == "web_search":
        rows = result.get("results")
        hits = rows if isinstance(rows, list) else []
        for h in hits[:80]:
            if not isinstance(h, dict):
                continue
            if str(h.get("source_type") or "").strip().lower() != "web":
                continue
            chunk_raw = h.get("chunk_id")
            if chunk_raw is None:
                continue
            try:
                chunk_id = int(str(chunk_raw))
            except Exception:
                continue
            text = str(h.get("text") or "")
            if not text.strip():
                continue
            url = str(h.get("url") or "").strip() or None
            domain = str(h.get("domain") or "").strip() or None
            title = str(h.get("title") or domain or url or "web").strip()
            out.append(
                RetrievalResult(
                    source_type="web",
                    ref_id=f"web:{chunk_id}",
                    chunk_id=chunk_id,
                    title=title,
                    url=url,
                    domain=domain,
                    score=float(h.get("score") or 0.0),
                    text=text,
                    meta={
                        "page_id": h.get("page_id"),
                        "chunk_index": h.get("chunk_index"),
                    },
                )
            )
        return out

    if tool == "kiwix_search":
        rows = result.get("results")
        hits = rows if isinstance(rows, list) else []
        for h in hits[:40]:
            if not isinstance(h, dict):
                continue
            # tool_kiwix_search returns RetrievalResult dicts.
            try:
                meta_any = h.get("meta")
                meta: dict[str, Any] = meta_any if isinstance(meta_any, dict) else {}
                rr = RetrievalResult(
                    source_type=str(h.get("source_type") or "kiwix"),
                    ref_id=str(h.get("ref_id") or ""),
                    chunk_id=int(str(h.get("chunk_id") or 0)),
                    title=h.get("title"),
                    url=h.get("url"),
                    domain=h.get("domain"),
                    score=float(h.get("score") or 0.0),
                    text=str(h.get("text") or ""),
                    meta=meta,
                )
            except Exception:
                continue
            if not rr.ref_id or not rr.text.strip():
                continue
            # Cap page text to keep contexts bounded.
            if len(rr.text) > 24_000:
                rr.text = rr.text[:24_000]
            out.append(rr)
        return out

    return out


async def _deep_agentic_tool_plan(
    http: httpx.AsyncClient,
    base_url: str,
    model: str,
    *,
    query: str,
    plan: dict[str, Any],
    evidence_policy: str,
    budget_remaining: int,
    allowed_tools: list[str],
    hints: dict[str, Any],
    supported_claims: list[dict[str, Any]],
    tool_schemas: list[dict[str, Any]],
) -> dict[str, Any]:
    system = (
        "You are a deep research tool planner. Your job is to gather evidence by calling tools. "
        "Do NOT answer the question yet. "
        "Call one or more tools to retrieve relevant passages. "
        "If min_time_remaining_sec is provided and > 0, keep gathering (do not signal done yet). "
        'Once min_time_remaining_sec reaches 0, stop retrieving: return NO tool calls and set content to JSON: {"done":true,"reason":"..."}. '
        "If no min_time_remaining_sec is provided, you may stop when you have enough evidence by returning NO tool calls with that same JSON. "
        "Prefer focused queries. Avoid repeating identical tool calls."
    )

    min_rem = _min_time_remaining_sec()
    packet = {
        "query": query,
        "plan": {
            "topics": plan.get("topics") or [],
            "subquestions": plan.get("subquestions") or [],
            "done_if": plan.get("done_if") or [],
        },
        "min_time_remaining_sec": round(max(0.0, float(min_rem)), 2)
        if min_rem is not None
        else None,
        "min_time_satisfied": _min_time_satisfied() if min_rem is not None else None,
        "evidence_policy": evidence_policy,
        "budget_remaining": int(budget_remaining),
        "allowed_tools": allowed_tools,
        "hints": hints,
        "supported_claims": [
            {
                "claim": str(c.get("claim") or "")[:500],
                "citations": c.get("citations")
                if isinstance(c.get("citations"), list)
                else [],
            }
            for c in (supported_claims or [])
            if isinstance(c, dict)
            and str(c.get("status") or "").strip().lower() == "supported"
        ][:18],
        "rules": [
            "Use doc_search for local documents.",
            "For factual questions: start with kiwix_search when available (primary offline factual source).",
            "Do NOT use EPUB/book passages as factual evidence about the real world unless the user explicitly asks to cite books.",
            "If calling doc_search for factual research, default exclude_group_names=['epub'] unless the user explicitly requests books.",
            "Use web_search only if web is enabled.",
            "If min_time_remaining_sec is not null and > 0, DO NOT set done=true; use the time to broaden coverage and triangulate.",
            "Keep tool_calls <= {max_calls}.".format(max_calls=MAX_TOOL_CALLS_PER_STEP),
        ],
    }

    msg = await _ollama_chat_message_once(
        http=http,
        base_url=base_url,
        model=model,
        messages=[
            {"role": "system", "content": system},
            {"role": "user", "content": json.dumps(packet, ensure_ascii=False)},
        ],
        tools=tool_schemas,
        timeout=60.0,
    )
    return msg


async def _deep_agentic_relevance_check(
    http: httpx.AsyncClient,
    base_url: str,
    model: str,
    *,
    query: str,
    plan: dict[str, Any],
    new_candidates: list[RetrievalResult],
    evidence_policy: str,
    budget_remaining: int,
) -> dict[str, Any]:
    items: list[dict[str, Any]] = []
    for r in new_candidates[:30]:
        items.append(
            {
                "ref_id": r.ref_id,
                "source_type": r.source_type,
                "title": (r.title or "")[:180],
                "url": (r.url or "")[:240],
                "domain": (r.domain or "")[:120],
                "score": float(r.score or 0.0),
                "snippet": (r.text or "")[:320],
                "meta": {
                    "source": (r.meta or {}).get("source"),
                    "path": (r.meta or {}).get("path"),
                    "tags": (r.meta or {}).get("tags"),
                },
            }
        )

    prompt = (
        "Return ONLY JSON.\n"
        "Schema:\n"
        "{\n"
        '  "keep_ref_ids": ["..."],\n'
        '  "drop_ref_ids": ["..."],\n'
        '  "missing": ["..."],\n'
        '  "done": true|false,\n'
        '  "reason": "..."\n'
        "}\n\n"
        "Task:\n"
        "- Decide which NEW candidates are relevant to the question and should be kept.\n"
        "- If evidence is still missing, list what is missing in 'missing'.\n"
        "- Set done=true only if you believe we have enough to answer.\n\n"
        f"Evidence policy: {evidence_policy}\n"
        f"Tool budget remaining: {int(budget_remaining)}\n\n"
        f"QUESTION:\n{query}\n\n"
        f"SUBQUESTIONS:\n{json.dumps(plan.get('subquestions') or [], ensure_ascii=False)}\n\n"
        f"NEW_CANDIDATES:\n{json.dumps(items, ensure_ascii=False)}\n"
    )

    out = await _ollama_chat_once(
        http,
        base_url,
        model,
        [{"role": "user", "content": prompt}],
        timeout=45.0,
    )
    obj_any = _json_obj_from_text(out) or {}
    obj = obj_any if isinstance(obj_any, dict) else {}

    keep_raw = obj.get("keep_ref_ids")
    drop_raw = obj.get("drop_ref_ids")
    keep = (
        [str(x).strip() for x in keep_raw if str(x).strip()]
        if isinstance(keep_raw, list)
        else []
    )
    drop = (
        [str(x).strip() for x in drop_raw if str(x).strip()]
        if isinstance(drop_raw, list)
        else []
    )
    missing_raw = obj.get("missing")
    missing = (
        [str(x).strip() for x in missing_raw if str(x).strip()]
        if isinstance(missing_raw, list)
        else []
    )
    done = bool(obj.get("done"))
    reason = str(obj.get("reason") or "").strip()[:800]
    return {
        "keep_ref_ids": keep[:40],
        "drop_ref_ids": drop[:40],
        "missing": missing[:20],
        "done": done,
        "reason": reason,
        "raw": out,
    }


async def _deep_agentic_parse(
    http: httpx.AsyncClient,
    base_url: str,
    model: str,
    *,
    query: str,
    verified_claims: list[dict[str, Any]],
) -> dict[str, Any]:
    prompt = (
        "Return ONLY JSON.\n"
        'Schema: {"facts":[{"fact":"...","citations":["D1"],"notes":"..."}],"open_questions":["..."]}.\n\n'
        "Task: Turn Supported claims into concise, checkable facts with their citations.\n\n"
        f"Question:\n{query}\n\n"
        f"Verified claims JSON:\n{json.dumps(verified_claims, ensure_ascii=False)}\n"
    )
    out = await _ollama_chat_once(
        http, base_url, model, [{"role": "user", "content": prompt}], timeout=45.0
    )
    obj_any = _json_obj_from_text(out) or {}
    obj = obj_any if isinstance(obj_any, dict) else {}
    facts_any = obj.get("facts")
    facts = facts_any if isinstance(facts_any, list) else []
    open_any = obj.get("open_questions")
    open_q = open_any if isinstance(open_any, list) else []
    return {
        "facts": facts[:60],
        "open_questions": [str(x)[:240] for x in open_q if str(x).strip()][:25],
        "raw": out,
    }


async def _deep_agentic_analyze(
    http: httpx.AsyncClient,
    base_url: str,
    model: str,
    *,
    query: str,
    plan: dict[str, Any],
    parsed: dict[str, Any],
) -> dict[str, Any]:
    prompt = (
        "Return ONLY JSON.\n"
        'Schema: {"need_more_research":true|false,"missing":["..."],"why":"..."}.\n\n'
        "Decide whether the current facts are sufficient to answer the question across subquestions.\n\n"
        f"Question:\n{query}\n\n"
        f"Subquestions:\n{json.dumps(plan.get('subquestions') or [], ensure_ascii=False)}\n\n"
        f"Facts:\n{json.dumps(parsed.get('facts') or [], ensure_ascii=False)}\n"
    )
    out = await _ollama_chat_once(
        http, base_url, model, [{"role": "user", "content": prompt}], timeout=35.0
    )
    obj_any = _json_obj_from_text(out) or {}
    obj = obj_any if isinstance(obj_any, dict) else {}
    need_more = bool(obj.get("need_more_research"))
    missing_any = obj.get("missing")
    missing = (
        [str(x).strip() for x in missing_any if str(x).strip()]
        if isinstance(missing_any, list)
        else []
    )
    why = str(obj.get("why") or "").strip()[:800]
    return {
        "need_more_research": need_more,
        "missing": missing[:20],
        "why": why,
        "raw": out,
    }


async def _deep_agentic_breakdown_further(
    http: httpx.AsyncClient,
    base_url: str,
    model: str,
    *,
    query: str,
    missing: list[str],
    allowed_tools: list[str],
) -> dict[str, Any]:
    prompt = (
        "Return ONLY JSON.\n"
        'Schema: {"doc_queries":["..."],"web_queries":["..."],"kiwix_query":"..."|null}.\n\n'
        "Turn missing info into focused retrieval queries for the enabled tools.\n\n"
        f"Question:\n{query}\n\n"
        f"Missing:\n{json.dumps(missing or [], ensure_ascii=False)}\n\n"
        f"Allowed tools:\n{json.dumps(allowed_tools, ensure_ascii=False)}\n"
    )
    out = await _ollama_chat_once(
        http, base_url, model, [{"role": "user", "content": prompt}], timeout=35.0
    )
    obj_any = _json_obj_from_text(out) or {}
    obj = obj_any if isinstance(obj_any, dict) else {}
    dq_any = obj.get("doc_queries")
    wq_any = obj.get("web_queries")
    kq_any = obj.get("kiwix_query")
    dq = (
        [str(x).strip() for x in dq_any if str(x).strip()]
        if isinstance(dq_any, list)
        else []
    )
    wq = (
        [str(x).strip() for x in wq_any if str(x).strip()]
        if isinstance(wq_any, list)
        else []
    )
    kq = (
        str(kq_any).strip() if isinstance(kq_any, str) and str(kq_any).strip() else None
    )
    return {"doc_queries": dq[:6], "web_queries": wq[:6], "kiwix_query": kq, "raw": out}


async def _deep_agentic_construct_response(
    http: httpx.AsyncClient,
    base_url: str,
    model: str,
    *,
    query: str,
    context_lines: list[str],
    verified_claims: list[dict[str, Any]],
    deep: bool,
) -> str:
    fmt = (
        (
            "## Executive Summary\n"
            "- 7-12 bullets, each with citations\n\n"
            "## Detailed Analysis\n"
            "- Use short subsections (### ...)\n\n"
            "## Practical Guidance\n"
            "- Checklist\n\n"
            "## Uncertainties / Gaps\n"
            "- What is missing/unclear\n"
        )
        if deep
        else (
            "## Answer\n"
            "(2-6 short paragraphs)\n\n"
            "## Key Points\n"
            "- 5-9 bullets, each with citations\n\n"
            "## Uncertainties / Gaps\n"
            "- What is missing/unclear\n"
        )
    )

    prompt = (
        "Write the best possible answer in Markdown using ONLY the provided CONTEXT and Verified claims JSON.\n\n"
        "Rules:\n"
        "- Only assert claims marked supported.\n"
        "- Every factual sentence/bullet must end with at least one citation tag like [D1], [W2], [K1].\n"
        "- Do NOT include a Sources section; it will be added automatically.\n\n"
        "Output format:\n" + fmt + "\n\n"
        f"Question:\n{query}\n\n"
        f"Verified claims JSON:\n{json.dumps(verified_claims, ensure_ascii=False)}\n\n"
        "CONTEXT:\n" + "\n".join(context_lines)
    )

    out = await _ollama_chat_once(
        http, base_url, model, [{"role": "user", "content": prompt}], timeout=120.0
    )
    return (out or "").strip()


async def _deep_agentic_analyze_response(
    http: httpx.AsyncClient,
    base_url: str,
    model: str,
    *,
    query: str,
    draft_md: str,
    allowed_tags: list[str],
) -> dict[str, Any]:
    prompt = (
        "Return ONLY JSON.\n"
        'Schema: {"issues":[{"type":"missing_citation|overclaim|format","detail":"..."}],"rewrite_needed":true|false}.\n\n'
        "Analyze the DRAFT for problems: missing citations, overconfident language, or format issues.\n\n"
        f"Question:\n{query}\n\n"
        f"Allowed citation tags:\n{json.dumps(allowed_tags, ensure_ascii=False)}\n\n"
        "DRAFT:\n" + (draft_md or "")
    )
    out = await _ollama_chat_once(
        http, base_url, model, [{"role": "user", "content": prompt}], timeout=45.0
    )
    obj_any = _json_obj_from_text(out) or {}
    obj = obj_any if isinstance(obj_any, dict) else {}
    issues_any = obj.get("issues")
    issues = issues_any if isinstance(issues_any, list) else []
    rewrite_needed = bool(obj.get("rewrite_needed"))
    return {"issues": issues[:30], "rewrite_needed": rewrite_needed, "raw": out}


async def _deep_agentic_edit(
    http: httpx.AsyncClient,
    base_url: str,
    model: str,
    *,
    query: str,
    draft_md: str,
    issues: list[dict[str, Any]],
    allowed_tags: list[str],
) -> str:
    prompt = (
        "Rewrite the DRAFT to address the ISSUES.\n\n"
        "Rules:\n"
        "- Use ONLY allowed citation tags.\n"
        "- Do NOT add new claims.\n"
        "- Do NOT add a Sources section.\n\n"
        f"Question:\n{query}\n\n"
        f"Allowed tags:\n{json.dumps(allowed_tags, ensure_ascii=False)}\n\n"
        f"ISSUES:\n{json.dumps(issues, ensure_ascii=False)}\n\n"
        "DRAFT:\n" + (draft_md or "")
    )
    out = await _ollama_chat_once(
        http, base_url, model, [{"role": "user", "content": prompt}], timeout=90.0
    )
    return (out or "").strip()


async def _deep_agentic_format(
    http: httpx.AsyncClient,
    base_url: str,
    model: str,
    *,
    draft_md: str,
    deep: bool,
) -> str:
    fmt = (
        (
            "Ensure the output uses these headings: Executive Summary, Concepts And Definitions, Detailed Analysis, Practical Guidance, Uncertainties / Gaps."
        )
        if deep
        else (
            "Ensure the output uses these headings: Answer, Key Points, Uncertainties / Gaps."
        )
    )
    prompt = (
        "Reformat the text to match the required Markdown structure. Do NOT change meaning. Do NOT add a Sources section.\n\n"
        + fmt
        + "\n\nTEXT:\n"
        + (draft_md or "")
    )
    out = await _ollama_chat_once(
        http, base_url, model, [{"role": "user", "content": prompt}], timeout=60.0
    )
    return (out or "").strip()


async def _deep_agentic_finalize(
    http: httpx.AsyncClient,
    base_url: str,
    model: str,
    *,
    draft_md: str,
    allowed_tags: list[str],
) -> str:
    prompt = (
        "Final pass: improve clarity and tighten wording without removing citations.\n\n"
        "Rules:\n"
        "- Keep all factual claims cited.\n"
        "- Use ONLY allowed citation tags.\n"
        "- Do NOT add a Sources section.\n\n"
        f"Allowed tags:\n{json.dumps(allowed_tags, ensure_ascii=False)}\n\n"
        "TEXT:\n" + (draft_md or "")
    )
    out = await _ollama_chat_once(
        http, base_url, model, [{"role": "user", "content": prompt}], timeout=60.0
    )
    return (out or "").strip()


async def _run_research_classic(
    *,
    http: httpx.AsyncClient,
    base_url: str,
    ingest_queue: WebIngestQueue,
    kiwix_url: str | None,
    run_id: str,
    query: str,
    plan: dict[str, Any],
    use_docs: bool,
    use_web: bool,
    pages_per_round: int,
    web_top_k: int,
    doc_top_k: int,
    domain_whitelist: list[str] | None,
    embed_model: str,
    synth_model: str,
    settings: dict[str, Any],
    steps: list[dict[str, Any]],
    evidence_policy: str,
    strict_fail_behavior: str,
    strict_allowlist: list[str],
    kiwix_zim_allowlist: list[str],
    epub_default_genre: str,
    epub_nonfiction_is_evidence: bool,
    epub_reference_is_evidence: bool,
    epub_fiction_is_evidence: bool,
    trust_tiers: dict[str, float],
    genre_classifier_model: str,
) -> dict[str, Any]:
    pages_per_round = max(
        1, min(int(pages_per_round), config.config.max_pages_per_round)
    )

    doc_provider = DocRetrievalProvider()
    web_provider = WebRetrievalProvider()
    kiwix_provider = KiwixRetrievalProvider(kiwix_url)

    all_doc_hits: list = []
    all_web_hits: list = []
    all_kiwix_hits: list = []
    seen_urls: set[str] = set()

    round_step: dict[str, Any] = {"type": "round", "round": 1}

    if use_docs:
        # Default safety: do not pull from the general EPUB library unless explicitly enabled.
        allow_epub = bool(settings.get("allow_epub"))
        exclude_groups = None if allow_epub else ["epub"]

        exclude_tags = None
        if allow_epub and _looks_like_stem_query(query):
            exclude_tags = ["fiction"]

        include_tags = settings.get("doc_include_tags")
        if not isinstance(include_tags, list):
            include_tags = None
        ex2 = settings.get("doc_exclude_tags")
        if isinstance(ex2, list):
            exclude_tags = list(set((exclude_tags or []) + [str(x) for x in ex2]))

        doc_queries = plan.get("doc_queries") or plan.get("subquestions") or [query]
        doc_queries = [str(x) for x in doc_queries if str(x).strip()][
            : config.config.max_doc_queries
        ]
        doc_round_hits = []
        for dq in doc_queries:
            doc_round_hits.extend(
                await doc_provider.retrieve(
                    dq,
                    top_k=int(doc_top_k),
                    embed_model=embed_model,
                    use_mmr=False,
                    mmr_lambda=0.75,
                    exclude_group_names=exclude_groups,
                    include_tags=include_tags,
                    exclude_tags=exclude_tags,
                )
            )

        uniq = {int(h.chunk_id): h for h in doc_round_hits}
        doc_round_hits = list(uniq.values())
        doc_round_hits.sort(key=lambda x: x.score, reverse=True)
        all_doc_hits.extend(doc_round_hits[: int(doc_top_k)])

        researchstore.add_trace(
            run_id,
            "docs_retrieve",
            {"queries": doc_queries, "hits": len(doc_round_hits)},
        )
        round_step["docs"] = {"queries": len(doc_queries), "hits": len(doc_round_hits)}

    if use_web:
        web_queries = plan.get("web_queries") or plan.get("subquestions") or [query]
        web_queries = [str(x) for x in web_queries if str(x).strip()][
            : config.config.max_web_queries
        ]

        urls = []
        urls_per_query = (
            max(1, pages_per_round // len(web_queries))
            if web_queries
            else pages_per_round
        )
        if not config.config.search_enabled:
            err = "web search disabled by config"
            researchstore.add_trace(
                run_id, "web_search_error", {"query": "*", "error": err}
            )
            round_step["web"] = {"queries": len(web_queries), "urls": 0, "error": err}
        else:
            search_tasks = [
                web_search_with_fallback(http, wq, n=urls_per_query)
                for wq in web_queries
            ]
            search_results = await asyncio.gather(*search_tasks, return_exceptions=True)

            for wq, result in zip(web_queries, search_results):
                if isinstance(result, BaseException):
                    researchstore.add_trace(
                        run_id, "web_search_error", {"query": wq, "error": str(result)}
                    )
                else:
                    found_urls, _provider = result
                    if isinstance(found_urls, list) and found_urls:
                        urls.extend(found_urls)

        cleaned_urls = []
        for u in urls:
            if u in seen_urls:
                continue
            seen_urls.add(u)
            cleaned_urls.append(u)
            if len(cleaned_urls) >= pages_per_round:
                break

        researchstore.add_trace(
            run_id, "web_search", {"queries": web_queries, "urls": cleaned_urls}
        )
        if "web" not in round_step:
            round_step["web"] = {"queries": len(web_queries), "urls": len(cleaned_urls)}

        for u in cleaned_urls:
            await ingest_queue.enqueue(u)
            try:
                page = await webstore.upsert_page_from_url(u, force=False)
                researchstore.add_trace(
                    run_id,
                    "web_upsert",
                    {"url": u, "page_id": page.get("id"), "title": page.get("title")},
                )
            except Exception as e:
                researchstore.add_trace(
                    run_id, "web_upsert_error", {"url": u, "error": str(e)}
                )

        web_round_hits = []
        for wq in web_queries:
            try:
                web_round_hits.extend(
                    await web_provider.retrieve(
                        wq,
                        top_k=int(web_top_k),
                        domain_whitelist=domain_whitelist,
                        embed_model=embed_model,
                    )
                )
            except Exception as e:
                researchstore.add_trace(
                    run_id, "web_retrieve_error", {"query": wq, "error": str(e)}
                )

        web_uniq = {int(h.chunk_id): h for h in web_round_hits}
        web_round_hits = list(web_uniq.values())
        web_round_hits.sort(key=lambda x: x.score, reverse=True)
        all_web_hits.extend(web_round_hits[: int(web_top_k)])
        researchstore.add_trace(run_id, "web_retrieve", {"hits": len(web_round_hits)})
        if isinstance(round_step.get("web"), dict):
            round_step["web"]["hits"] = len(web_round_hits)

    kiwix_hits = []
    if kiwix_url:
        try:
            kiwix_hits = await kiwix_provider.retrieve(
                query, top_k=3, embed_model=embed_model
            )
        except Exception:
            kiwix_hits = []
    all_kiwix_hits.extend(kiwix_hits)

    doc_uniq = {int(h.chunk_id): h for h in all_doc_hits}
    web_uniq = {int(h.chunk_id): h for h in all_web_hits}
    kiwix_uniq = {int(h.chunk_id): h for h in all_kiwix_hits}

    doc_hits = sorted(doc_uniq.values(), key=lambda x: x.score, reverse=True)[
        : int(doc_top_k)
    ]
    web_hits = sorted(web_uniq.values(), key=lambda x: x.score, reverse=True)[
        : int(web_top_k)
    ]
    kiwix_hits = sorted(kiwix_uniq.values(), key=lambda x: x.score, reverse=True)[:3]

    combined_hits = [*doc_hits, *web_hits, *kiwix_hits]

    (
        evidence_hits,
        _context_only_hits,
        gate_stats,
    ) = await _annotate_provenance_and_partition_hits(
        http=http,
        base_url=base_url,
        model=genre_classifier_model,
        hits=combined_hits,
        policy=evidence_policy,
        strict_allowlist=strict_allowlist,
        kiwix_zim_allowlist=kiwix_zim_allowlist,
        epub_default_genre=epub_default_genre,
        epub_nonfiction_is_evidence=epub_nonfiction_is_evidence,
        epub_reference_is_evidence=epub_reference_is_evidence,
        epub_fiction_is_evidence=epub_fiction_is_evidence,
        trust_tiers=trust_tiers,
    )
    researchstore.add_trace(run_id, "evidence_gate", {"round": 1, **gate_stats})

    sources_meta_store = _sources_meta_from_hits(
        combined_hits, pinned_ref_ids=set(), excluded_ref_ids=set(), limit=40
    )
    researchstore.upsert_sources(run_id, sources_meta_store)

    sources_meta, context_lines = build_context(
        evidence_hits,
        max_chars=12000,
        per_source_cap=6,
        pinned_ref_ids=set(),
        excluded_ref_ids=set(),
        preserve_order=True,
    )
    researchstore.add_trace(
        run_id,
        "evidence_context",
        {"round": 1, "sources": len(sources_meta), "lines": len(context_lines)},
    )

    if evidence_policy == "strict" and not context_lines:
        by_kind = gate_stats.get("by_kind") if isinstance(gate_stats, dict) else {}
        epub_by_genre = (
            gate_stats.get("epub_by_genre") if isinstance(gate_stats, dict) else {}
        )
        researchstore.add_trace(
            run_id,
            "guardrail",
            {
                "reason": "no_evidence_sources",
                "round": 1,
                "by_kind": by_kind,
                "epub_by_genre": epub_by_genre,
                "strict_fail_behavior": strict_fail_behavior,
            },
        )

        if strict_fail_behavior == "speculative":
            ctx_items: list[dict[str, Any]] = []
            for s in sources_meta_store or []:
                if not isinstance(s, dict):
                    continue
                meta_any = s.get("meta")
                meta = meta_any if isinstance(meta_any, dict) else {}
                prov_any = meta.get("provenance")
                prov = prov_any if isinstance(prov_any, dict) else {}
                if bool(prov.get("evidence_ok")):
                    continue
                ctx_items.append(
                    {
                        "title": s.get("title"),
                        "source_kind": prov.get("source_kind"),
                        "doc_genre": prov.get("doc_genre"),
                        "source_id": prov.get("source_id"),
                        "snippet": s.get("snippet"),
                    }
                )
                if len(ctx_items) >= 12:
                    break

            msg = await _synthesize_speculative_no_evidence(
                http,
                base_url,
                synth_model,
                query=query,
                context_items=ctx_items,
            )
            if not msg:
                msg = (
                    "## Speculative Answer (No Reliable Evidence Enabled)\n\n"
                    "No evidence-eligible sources were found in strict mode.\n\n"
                    "Fixes:\n"
                    "- Configure offline Wikipedia (Kiwix) and set `KIWIX_URL`, then re-run.\n"
                    "- Or re-run with web enabled: `/research --web ...` or `/deep --web ...`.\n"
                    "- Or ingest/upload nonfiction/reference documents."
                )
        else:
            msg = (
                "No evidence found in enabled sources (evidence_policy=strict).\n\n"
                "This run retrieved content, but it was excluded from evidence by policy (for example: EPUB fiction/unknown).\n\n"
                f"Retrieved kinds: {json.dumps(by_kind, ensure_ascii=False)}\n"
                f"EPUB genres: {json.dumps(epub_by_genre, ensure_ascii=False)}\n\n"
                "Fixes:\n"
                "- Configure offline Wikipedia (Kiwix) and set `KIWIX_URL`, then re-run.\n"
                "- Or re-run with web enabled: `/research --web ...` or `/deep --web ...`.\n"
                "- Or ingest/upload nonfiction/reference documents, or tag EPUBs as nonfiction/reference for evidence use."
            )

        researchstore.set_run_done(run_id, msg)
        return {
            "ok": True,
            "run_id": run_id,
            "answer": msg,
            "sources": sources_meta_store,
            "steps": steps,
        }

    final = await _synthesize_from_context(
        http,
        base_url,
        synth_model,
        query=query,
        topics=plan.get("topics") or [],
        context_lines=context_lines,
        deep=False,
    )

    # Classic mode still needs strong citation enforcement in practice.
    # Some models ignore the synthesis prompt's citation rules; fix via a bounded rewrite.
    allowed_tags = [
        str(s.get("citation") or "").strip()
        for s in (sources_meta or [])
        if isinstance(s, dict) and str(s.get("citation") or "").strip()
    ]
    allowed_set = set(allowed_tags)
    if final and allowed_tags:
        used0 = extract_citation_tags(final)
        invalid0 = sorted([t for t in used0 if t not in allowed_set])
        question_type = (
            "empirical_stats"
            if _looks_like_empirical_stats_query(query)
            else "general_factual"
        )
        uncited0 = (
            question_type == "empirical_stats"
        ) and _has_uncited_empirical_claims(final)
        missing0 = not used0

        if missing0 or invalid0 or uncited0:
            researchstore.add_trace(
                run_id,
                "citation_contract_classic",
                {
                    "ok": False,
                    "missing_citations": bool(missing0),
                    "invalid_tags": invalid0[:20],
                    "uncited_numbers": bool(uncited0),
                },
            )
            fixed = final
            fixed_invalid_total = 0
            # Use the synthesis model for this rewrite; tiny classifier models are unreliable
            # for citation-contract editing.
            rewrite_model = synth_model
            for attempt in (1, 2):
                try:
                    fixed = await _rewrite_for_citation_contract(
                        http,
                        base_url,
                        rewrite_model,
                        query=query,
                        text=fixed,
                        allowed_tags=allowed_tags,
                        invalid_tags=sorted(
                            [
                                t
                                for t in extract_citation_tags(fixed)
                                if t not in allowed_set
                            ]
                        )[:40],
                        question_type=question_type,
                    )
                except Exception as e:
                    researchstore.add_trace(
                        run_id,
                        "citation_contract_classic_error",
                        {"attempt": attempt, "error": str(e)},
                    )
                    break

                invalid1 = sorted(
                    [t for t in extract_citation_tags(fixed) if t not in allowed_set]
                )
                if invalid1:
                    fixed_invalid_total += len(invalid1)
                    fixed = _strip_invalid_citation_tokens(
                        fixed, allowed_tags=allowed_set
                    )

                used1 = extract_citation_tags(fixed)
                uncited1 = (
                    question_type == "empirical_stats"
                ) and _has_uncited_empirical_claims(fixed)
                if used1 and not uncited1:
                    break

            # Fail closed for empirical/statistical answers that still contain uncited numbers.
            if (question_type == "empirical_stats") and _has_uncited_empirical_claims(
                fixed
            ):
                fixed = (
                    "## Cannot Answer (Citation Contract Failed)\n\n"
                    "I could not produce a citation-grounded statistical answer from the available evidence chunks.\n\n"
                    "To answer this safely:\n"
                    "- Re-run with web enabled or configure offline Wikipedia (Kiwix).\n"
                    "- Or ingest/upload an authoritative dataset or report.\n"
                )
                researchstore.add_trace(
                    run_id,
                    "citation_contract_classic",
                    {"ok": False, "fail_closed": True},
                )
            # Strict mode: if we still can't get any citations, fail closed (or go speculative).
            elif evidence_policy == "strict" and not extract_citation_tags(fixed):
                if strict_fail_behavior == "speculative":
                    ctx_items: list[dict[str, Any]] = []
                    for s in sources_meta_store or []:
                        if not isinstance(s, dict):
                            continue
                        ctx_items.append(
                            {
                                "title": s.get("title"),
                                "snippet": s.get("snippet"),
                                "meta": s.get("meta"),
                            }
                        )
                        if len(ctx_items) >= 12:
                            break
                    fixed = await _synthesize_speculative_no_evidence(
                        http,
                        base_url,
                        synth_model,
                        query=query,
                        context_items=ctx_items,
                    )
                else:
                    fixed = (
                        "## Cannot Answer (Citation Contract Failed)\n\n"
                        "I could not produce an answer that complies with the citation contract using the available sources.\n\n"
                        "To fix this:\n"
                        "- Try a different synthesis model (some models ignore citation formatting).\n"
                        "- Or re-run with web/Kiwix enabled to broaden evidence.\n"
                    )
                researchstore.add_trace(
                    run_id,
                    "citation_contract_classic",
                    {"ok": False, "fail_closed": True, "reason": "missing_citations"},
                )
            else:
                researchstore.add_trace(
                    run_id,
                    "citation_contract_classic",
                    {
                        "ok": bool(extract_citation_tags(fixed)),
                        "fixed_invalid": int(fixed_invalid_total),
                    },
                )

            final = fixed

    sources_section = _format_sources_section(sources_meta)
    if sources_section:
        lower = "\n" + (final or "").lower()
        if "\n## sources" not in lower and "\nsources\n" not in lower:
            final = (final or "").rstrip() + "\n\n" + sources_section

    researchstore.set_run_done(run_id, final)
    researchstore.add_trace(run_id, "done", {"len": len(final)})
    steps.append(round_step)
    return {
        "ok": True,
        "run_id": run_id,
        "answer": final,
        "sources": sources_meta,
        "steps": steps,
    }


async def run_research(
    *,
    http: httpx.AsyncClient,
    base_url: str,
    ingest_queue: WebIngestQueue,
    kiwix_url: str | None,
    chat_id: str | None,
    query: str,
    mode: str,
    use_docs: bool,
    use_web: bool,
    rounds: int,
    pages_per_round: int,
    web_top_k: int,
    doc_top_k: int,
    domain_whitelist: list[str] | None,
    embed_model: str,
    planner_model: str,
    verifier_model: str,
    synth_model: str,
    settings: dict[str, Any],
    run_id: str | None = None,
) -> dict[str, Any]:
    if not run_id:
        m0 = (mode or "").strip().lower() or "deep"
        if m0 == "research":
            m0 = "deep"
        mode = m0
        run_id = researchstore.create_run(chat_id, query, mode, settings)
    researchstore.add_trace(run_id, "start", {"query": query, "settings": settings})

    steps: list[dict[str, Any]] = []

    def _looks_like_general_knowledge_question(q: str) -> bool:
        s = (q or "").strip().lower()
        if not s:
            return False
        starters = (
            "what is ",
            "who is ",
            "when did ",
            "when was ",
            "where is ",
            "define ",
            "explain ",
            "history of ",
            "overview of ",
        )
        return s.startswith(starters) or s.endswith("?")

    # Optional minimum wall-clock duration.
    # When set, the agentic deep loop keeps retrieving until the minimum is met,
    # then it stops tool calls and performs final synthesis.
    min_sec = _parse_time_budget_sec(
        settings.get("time_budget_sec") or settings.get("time_budget")
    )
    min_token = None
    if min_sec:
        min_end_at = time.time() + float(min_sec)
        min_token = _RUN_MIN_END_AT.set(min_end_at)
        researchstore.add_trace(
            run_id,
            "time_budget",
            {
                "time_budget_sec": float(min_sec),
                "min_end_at": min_end_at,
                "semantics": "minimum_then_wrap_up",
            },
        )

    try:
        plan = await _plan_queries(http, base_url, planner_model, query)
        researchstore.add_trace(run_id, "plan", plan)
        steps.append(
            {
                "type": "plan",
                "topics": plan.get("topics") or [],
                "subquestions": plan.get("subquestions") or [],
                "web_queries": plan.get("web_queries") or [],
                "doc_queries": plan.get("doc_queries") or [],
                "done_if": plan.get("done_if") or [],
            }
        )

        m = (mode or "deep").strip().lower()
        if m == "research":
            m = "deep"
        deep_mode = m.startswith("deep")

        # Stage 0: intent + evidence policy
        policy_override = settings.get("evidence_policy")
        evidence_policy = _normalize_evidence_policy(
            policy_override,
            default_policy=config.config.default_evidence_policy,
        )
        if not (isinstance(policy_override, str) and policy_override.strip()):
            evidence_policy = infer_evidence_policy(
                query, default_policy=evidence_policy
            )

        strict_fail_behavior = _normalize_strict_fail_behavior(
            settings.get("strict_fail_behavior"),
            default_behavior=config.config.strict_fail_behavior,
        )

        strict_allowlist = list(config.config.evidence_allowlist_strict or [])
        kiwix_zim_allowlist = list(config.config.kiwix_evidence_zim_allowlist or [])
        epub_default_genre = str(config.config.epub_default_genre or "unknown")
        epub_nonfiction_is_evidence = bool(
            getattr(config.config, "epub_nonfiction_is_evidence", False)
        )
        epub_reference_is_evidence = bool(
            getattr(config.config, "epub_reference_is_evidence", False)
        )
        epub_fiction_is_evidence = bool(config.config.epub_fiction_is_evidence)
        trust_tiers = dict(config.config.trust_tiers or {})
        genre_classifier_model = str(
            settings.get("genre_classifier_model") or verifier_model
        )
        audit_model = str(settings.get("citation_audit_model") or verifier_model)

        epub_intent = infer_epub_intent(query)
        if epub_intent in {"fiction", "reference"}:
            # If the user is explicitly asking for book content or a references-style answer,
            # include EPUBs in retrieval by default.
            if "allow_epub" not in settings:
                settings["allow_epub"] = True

            # Make EPUBs evidence-eligible for the relevant intent.
            # (This only affects whether EPUB hits can be cited/used as evidence.)
            if epub_intent == "fiction":
                epub_fiction_is_evidence = True
            else:
                epub_reference_is_evidence = True
                epub_nonfiction_is_evidence = True

        researchstore.add_trace(
            run_id,
            "evidence_policy",
            {
                "policy": evidence_policy,
                "strict_fail_behavior": strict_fail_behavior,
                "strict_allowlist": strict_allowlist,
                "kiwix_zim_allowlist": kiwix_zim_allowlist,
                "epub_default_genre": epub_default_genre,
                "epub_nonfiction_is_evidence": epub_nonfiction_is_evidence,
                "epub_reference_is_evidence": epub_reference_is_evidence,
                "epub_fiction_is_evidence": epub_fiction_is_evidence,
                "genre_classifier_model": genre_classifier_model,
                "audit_model": audit_model,
            },
        )

        # Deep mode uses the agentic pipeline (tool loop + multi-step post-processing).
        if deep_mode:
            researchstore.add_trace(
                run_id, "agentic_deep_research_used", {"enabled": True}
            )
            return await _run_deep_research_agentic(
                http=http,
                base_url=base_url,
                ingest_queue=ingest_queue,
                kiwix_url=kiwix_url,
                run_id=run_id,
                query=query,
                plan=plan,
                use_docs=use_docs,
                use_web=use_web,
                pages_per_round=pages_per_round,
                web_top_k=web_top_k,
                doc_top_k=doc_top_k,
                domain_whitelist=domain_whitelist,
                embed_model=embed_model,
                planner_model=planner_model,
                verifier_model=verifier_model,
                synth_model=synth_model,
                settings=settings,
                steps=steps,
                evidence_policy=evidence_policy,
                strict_fail_behavior=strict_fail_behavior,
                strict_allowlist=strict_allowlist,
                kiwix_zim_allowlist=kiwix_zim_allowlist,
                epub_default_genre=epub_default_genre,
                epub_nonfiction_is_evidence=epub_nonfiction_is_evidence,
                epub_reference_is_evidence=epub_reference_is_evidence,
                epub_fiction_is_evidence=epub_fiction_is_evidence,
                trust_tiers=trust_tiers,
                genre_classifier_model=genre_classifier_model,
                audit_model=audit_model,
            )

        return await _run_research_classic(
            http=http,
            base_url=base_url,
            ingest_queue=ingest_queue,
            kiwix_url=kiwix_url,
            run_id=run_id,
            query=query,
            plan=plan,
            use_docs=use_docs,
            use_web=use_web,
            pages_per_round=pages_per_round,
            web_top_k=web_top_k,
            doc_top_k=doc_top_k,
            domain_whitelist=domain_whitelist,
            embed_model=embed_model,
            synth_model=synth_model,
            settings=settings,
            steps=steps,
            evidence_policy=evidence_policy,
            strict_fail_behavior=strict_fail_behavior,
            strict_allowlist=strict_allowlist,
            kiwix_zim_allowlist=kiwix_zim_allowlist,
            epub_default_genre=epub_default_genre,
            epub_nonfiction_is_evidence=epub_nonfiction_is_evidence,
            epub_reference_is_evidence=epub_reference_is_evidence,
            epub_fiction_is_evidence=epub_fiction_is_evidence,
            trust_tiers=trust_tiers,
            genre_classifier_model=genre_classifier_model,
        )

        """LEGACY CLASSIC PIPELINE

        The implementation below was the pre-deep "classic" pipeline.
        It is intentionally unreachable: classic mode now delegates to `_run_research_classic()`.

        pages_per_round = max(1, min(int(pages_per_round), config.config.max_pages_per_round))

        if not deep_mode:
            rounds = 1

        all_doc_hits: list = []
        all_web_hits: list = []
        all_kiwix_hits: list = []
        seen_urls: set[str] = set()
        sources_meta: list[dict[str, Any]] = []
        context_lines: list[str] = []
        verify: dict[str, Any] = {"claims": []}

        doc_provider = DocRetrievalProvider()
        web_provider = WebRetrievalProvider()
        kiwix_provider = KiwixRetrievalProvider(kiwix_url)

        # These can be refined across rounds when sources are irrelevant.
        doc_queries_override: list[str] | None = None
        web_queries_override: list[str] | None = None
        kiwix_query_override: str | None = None
        refinements_used = 0
        gap_checks_used = 0

        for rno in range(1, rounds + 1):
            researchstore.add_trace(run_id, "round_begin", {"round": rno})
            round_step: dict[str, Any] = {"type": "round", "round": rno}

            if use_docs:
                # Default safety: do not pull from the general EPUB library for research runs
                # unless explicitly enabled (EPUBs often contain fiction / narrative material).
                allow_epub = bool(settings.get("allow_epub"))
                exclude_groups = None if allow_epub else ["epub"]
                exclude_tags = None
                # If EPUBs are enabled, still allow users to exclude fiction via tags.
                if allow_epub and _looks_like_stem_query(query):
                    exclude_tags = ["fiction"]

                # Optional explicit tag filters.
                include_tags = settings.get("doc_include_tags")
                if not isinstance(include_tags, list):
                    include_tags = None
                ex2 = settings.get("doc_exclude_tags")
                if isinstance(ex2, list):
                    exclude_tags = list(set((exclude_tags or []) + [str(x) for x in ex2]))

                doc_queries = doc_queries_override or plan.get("doc_queries") or plan.get("subquestions") or [query]
                doc_queries = [str(x) for x in doc_queries if str(x).strip()][: config.config.max_doc_queries]
                doc_round_hits = []
                for dq in doc_queries:
                    doc_round_hits.extend(
                        await doc_provider.retrieve(
                            dq,
                            top_k=int(doc_top_k),
                            embed_model=embed_model,
                            use_mmr=False,
                            mmr_lambda=0.75,
                            exclude_group_names=exclude_groups,
                            include_tags=include_tags,
                            exclude_tags=exclude_tags,
                        )
                    )
                uniq = {int(h.chunk_id): h for h in doc_round_hits}
                doc_round_hits = list(uniq.values())
                doc_round_hits.sort(key=lambda x: x.score, reverse=True)
                all_doc_hits.extend(doc_round_hits[: int(doc_top_k)])

                researchstore.add_trace(run_id, "docs_retrieve", {"queries": doc_queries, "hits": len(doc_round_hits)})
                round_step["docs"] = {"queries": len(doc_queries), "hits": len(doc_round_hits)}

            if use_web:
                web_queries = web_queries_override or plan.get("web_queries") or plan.get("subquestions") or [query]
                web_queries = [str(x) for x in web_queries if str(x).strip()][: config.config.max_web_queries]

                urls = []
                urls_per_query = max(1, pages_per_round // len(web_queries)) if web_queries else pages_per_round
                if not config.config.search_enabled:
                    err = "web search disabled by config"
                    researchstore.add_trace(run_id, "web_search_error", {"query": "*", "error": err})
                    round_step["web"] = {"queries": len(web_queries), "urls": 0, "error": err}
                else:
                    search_tasks = [web_search_with_fallback(http, wq, n=urls_per_query) for wq in web_queries]
                    search_results = await asyncio.gather(*search_tasks, return_exceptions=True)

                    for wq, result in zip(web_queries, search_results):
                        if isinstance(result, BaseException):
                            researchstore.add_trace(run_id, "web_search_error", {"query": wq, "error": str(result)})
                        else:
                            found_urls, _provider = result
                            if isinstance(found_urls, list) and found_urls:
                                urls.extend(found_urls)

                cleaned_urls = []
                for u in urls:
                    if u in seen_urls:
                        continue
                    seen_urls.add(u)
                    cleaned_urls.append(u)
                    if len(cleaned_urls) >= pages_per_round:
                        break

                researchstore.add_trace(run_id, "web_search", {"queries": web_queries, "urls": cleaned_urls})
                if "web" not in round_step:
                    round_step["web"] = {"queries": len(web_queries), "urls": len(cleaned_urls)}

                for u in cleaned_urls:
                    await ingest_queue.enqueue(u)
                    try:
                        page = await webstore.upsert_page_from_url(u, force=False)
                        researchstore.add_trace(run_id, "web_upsert", {"url": u, "page_id": page.get("id"), "title": page.get("title")})
                    except Exception as e:
                        researchstore.add_trace(run_id, "web_upsert_error", {"url": u, "error": str(e)})

                web_round_hits = []
                for wq in web_queries:
                    try:
                        web_round_hits.extend(
                            await web_provider.retrieve(
                                wq,
                                top_k=int(web_top_k),
                                domain_whitelist=domain_whitelist,
                                embed_model=embed_model,
                            )
                        )
                    except Exception as e:
                        researchstore.add_trace(run_id, "web_retrieve_error", {"query": wq, "error": str(e)})

                web_uniq = {int(h.chunk_id): h for h in web_round_hits}
                web_round_hits = list(web_uniq.values())
                web_round_hits.sort(key=lambda x: x.score, reverse=True)
                all_web_hits.extend(web_round_hits[: int(web_top_k)])
                researchstore.add_trace(run_id, "web_retrieve", {"hits": len(web_round_hits)})
                if isinstance(round_step.get("web"), dict):
                    round_step["web"]["hits"] = len(web_round_hits)

            kiwix_hits = []
            if kiwix_url:
                try:
                    kq = (kiwix_query_override or query)
                    kiwix_hits = await kiwix_provider.retrieve(kq, top_k=3, embed_model=embed_model)
                except Exception:
                    kiwix_hits = []
            all_kiwix_hits.extend(kiwix_hits)

            doc_uniq = {int(h.chunk_id): h for h in all_doc_hits}
            web_uniq = {int(h.chunk_id): h for h in all_web_hits}
            kiwix_uniq = {int(h.chunk_id): h for h in all_kiwix_hits}

            doc_hits = sorted(doc_uniq.values(), key=lambda x: x.score, reverse=True)[: int(doc_top_k)]
            web_hits = sorted(web_uniq.values(), key=lambda x: x.score, reverse=True)[: int(web_top_k)]
            kiwix_hits = sorted(kiwix_uniq.values(), key=lambda x: x.score, reverse=True)[:3]

            combined_hits = [*doc_hits, *web_hits, *kiwix_hits]

            if deep_mode and combined_hits:
                # Optional rerank for better precision (best-effort).
                rr_model = str(settings.get("rerank_model") or verifier_model)
                keep_n = int(settings.get("rerank_keep_n") or 24)
                keep_n = max(4, min(keep_n, len(combined_hits)))
                try:
                    combined_hits = await rerank_results(
                        http=http,
                        ollama_url=base_url,
                        model=rr_model,
                        query=query,
                        results=combined_hits,
                        keep_n=keep_n,
                    )
                    researchstore.add_trace(run_id, "rerank", {"model": rr_model, "keep_n": keep_n})
                except Exception as e:
                    researchstore.add_trace(run_id, "rerank_error", {"error": str(e)})

            # Apply user steering flags (pinned/excluded) from prior rounds.
            flags = researchstore.get_source_flags_by_ref_id(run_id)
            pinned_ref_ids = {ref for ref, f in flags.items() if isinstance(f, dict) and f.get("pinned")}
            excluded_ref_ids = {ref for ref, f in flags.items() if isinstance(f, dict) and f.get("excluded")}

            max_chars = 20000 if deep_mode else 12000
            per_source_cap = 8 if deep_mode else 6

            # Stage 1: retrieval (already done) + provenance
            # Stage 2: evidence gate (filter what is allowed to be cited)
            evidence_hits, _context_only_hits, gate_stats = await _annotate_provenance_and_partition_hits(
                http=http,
                base_url=base_url,
                model=genre_classifier_model,
                hits=combined_hits,
                policy=evidence_policy,
                strict_allowlist=strict_allowlist,
                kiwix_zim_allowlist=kiwix_zim_allowlist,
                epub_default_genre=epub_default_genre,
                epub_nonfiction_is_evidence=epub_nonfiction_is_evidence,
                epub_reference_is_evidence=epub_reference_is_evidence,
                epub_fiction_is_evidence=epub_fiction_is_evidence,
                trust_tiers=trust_tiers,
            )
            researchstore.add_trace(run_id, "evidence_gate", {"round": rno, **gate_stats})

            # Persist a lightweight sources list for UI steering/debugging.
            sources_meta_store = _sources_meta_from_hits(
                combined_hits,
                pinned_ref_ids=pinned_ref_ids,
                excluded_ref_ids=excluded_ref_ids,
                limit=60 if deep_mode else 40,
            )
            researchstore.upsert_sources(run_id, sources_meta_store)

            # Build the evidence-only context used for verification + synthesis.
            sources_meta, context_lines = build_context(
                evidence_hits,
                max_chars=max_chars,
                per_source_cap=per_source_cap,
                pinned_ref_ids=pinned_ref_ids,
                excluded_ref_ids=excluded_ref_ids,
                preserve_order=True,
            )
            researchstore.add_trace(
                run_id,
                "evidence_context",
                {"round": rno, "sources": len(sources_meta), "lines": len(context_lines)},
            )

            if deep_mode:
                # If sources look irrelevant, let the model refine queries and retry (bounded).
                try:
                    assess = await _assess_sources_relevance_and_refine_queries(
                        http,
                        base_url,
                        planner_model,
                        query=query,
                        sources_meta=sources_meta_store,
                        use_docs=use_docs,
                        use_web=use_web,
                        kiwix_enabled=bool(kiwix_url),
                    )
                    researchstore.add_trace(
                        run_id,
                        "assess",
                        {"round": rno, "relevant": assess.get("relevant"), "reason": assess.get("reason")},
                    )
                    steps.append(
                        {
                            "type": "assess",
                            "round": rno,
                            "relevant": bool(assess.get("relevant")),
                            "reason": str(assess.get("reason") or "")[:800],
                        }
                    )
                    if (
                        (not bool(assess.get("relevant")))
                        and rno < rounds
                        and refinements_used < MAX_SOURCE_REFINEMENTS
                    ):
                        dq_any = assess.get("doc_queries")
                        wq_any = assess.get("web_queries")
                        dq_list: list[Any] = dq_any if isinstance(dq_any, list) else []
                        wq_list: list[Any] = wq_any if isinstance(wq_any, list) else []
                        kq = assess.get("kiwix_query")

                        doc_queries_override = [str(x) for x in dq_list if str(x).strip()] if use_docs else None
                        web_queries_override = [str(x) for x in wq_list if str(x).strip()] if use_web else None
                        kiwix_query_override = str(kq).strip() if isinstance(kq, str) and str(kq).strip() else None
                        refinements_used += 1

                        researchstore.add_trace(
                            run_id,
                            "refine",
                            {
                                "round": rno,
                                "refinements_used": refinements_used,
                                "doc_queries": doc_queries_override or [],
                                "web_queries": web_queries_override or [],
                                "kiwix_query": kiwix_query_override,
                            },
                        )
                        # Skip verification on clearly-irrelevant sources; try again next round.
                        continue
                except Exception as e:
                    researchstore.add_trace(run_id, "assess_error", {"round": rno, "error": str(e)})

            # Hard evidence gate: in strict mode, refuse to produce an evidence-backed answer
            # when no evidence-eligible sources are available.
            if evidence_policy == "strict" and not context_lines:
                by_kind = gate_stats.get("by_kind") if isinstance(gate_stats, dict) else {}
                epub_by_genre = gate_stats.get("epub_by_genre") if isinstance(gate_stats, dict) else {}
                researchstore.add_trace(
                    run_id,
                    "guardrail",
                    {
                        "reason": "no_evidence_sources",
                        "round": rno,
                        "by_kind": by_kind,
                        "epub_by_genre": epub_by_genre,
                        "strict_fail_behavior": strict_fail_behavior,
                    },
                )

                # If other evidence sources are enabled, allow the loop to continue (bounded) in case
                # later rounds produce evidence-eligible hits.
                if deep_mode and rno < rounds and refinements_used < MAX_SOURCE_REFINEMENTS and (use_web or bool(kiwix_url)):
                    continue

                if strict_fail_behavior == "speculative":
                    ctx_items: list[dict[str, Any]] = []
                    for s in sources_meta_store or []:
                        if not isinstance(s, dict):
                            continue
                        meta_any = s.get("meta")
                        meta = meta_any if isinstance(meta_any, dict) else {}
                        prov_any = meta.get("provenance")
                        prov = prov_any if isinstance(prov_any, dict) else {}
                        if bool(prov.get("evidence_ok")):
                            continue
                        ctx_items.append(
                            {
                                "title": s.get("title"),
                                "source_kind": prov.get("source_kind"),
                                "doc_genre": prov.get("doc_genre"),
                                "source_id": prov.get("source_id"),
                                "snippet": s.get("snippet"),
                            }
                        )
                        if len(ctx_items) >= 12:
                            break

                    msg = await _synthesize_speculative_no_evidence(
                        http,
                        base_url,
                        synth_model,
                        query=query,
                        context_items=ctx_items,
                    )
                    if not msg:
                        msg = (
                            "## Speculative Answer (No Reliable Evidence Enabled)\n\n"
                            "No evidence-eligible sources were found in strict mode.\n\n"
                            "Fixes:\n"
                            "- Configure offline Wikipedia (Kiwix) and set `KIWIX_URL`, then re-run.\n"
                            "- Or re-run with web enabled: `/research --web ...` or `/deep --web ...`.\n"
                            "- Or ingest/upload nonfiction/reference documents."
                        )
                else:
                    msg = (
                        "No evidence found in enabled sources (evidence_policy=strict).\n\n"
                        "This run retrieved content, but it was excluded from evidence by policy (for example: EPUB fiction/unknown).\n\n"
                        f"Retrieved kinds: {json.dumps(by_kind, ensure_ascii=False)}\n"
                        f"EPUB genres: {json.dumps(epub_by_genre, ensure_ascii=False)}\n\n"
                        "Fixes:\n"
                        "- Configure offline Wikipedia (Kiwix) and set `KIWIX_URL`, then re-run.\n"
                        "- Or re-run with web enabled: `/research --web ...` or `/deep --web ...`.\n"
                        "- Or ingest/upload nonfiction/reference documents, or tag EPUBs as nonfiction/reference for evidence use."
                    )

                researchstore.set_run_done(run_id, msg)
                return {
                    "ok": True,
                    "run_id": run_id,
                    "answer": msg,
                    "sources": sources_meta_store,
                    "steps": steps,
                }

            if not deep_mode:
                break

            verify = await _verify_claims(http, base_url, verifier_model, query, context_lines)
            researchstore.clear_claims(run_id)
            researchstore.add_claims(run_id, verify["claims"])
            researchstore.add_trace(run_id, "verify", {"claims": len(verify["claims"])})

            supported_claims = [c for c in (verify.get("claims") or []) if isinstance(c, dict) and c.get("status") == "supported"]

            # Gap check: ensure we actually covered the planned topics.
            if rno < rounds and refinements_used < MAX_SOURCE_REFINEMENTS and gap_checks_used < MAX_GAP_CHECKS:
                try:
                    gap = await _gap_check_and_refine_queries(
                        http,
                        base_url,
                        verifier_model,
                        query=query,
                        topics=plan.get("topics") or [],
                        subquestions=plan.get("subquestions") or [],
                        supported_claims=supported_claims,
                        use_docs=use_docs,
                        use_web=use_web,
                        kiwix_enabled=bool(kiwix_url),
                    )
                    gap_checks_used += 1
                    researchstore.add_trace(run_id, "gap", {"round": rno, "done": gap.get("done"), "reason": gap.get("reason")})
                    steps.append({"type": "gap", "round": rno, "done": bool(gap.get("done")), "reason": str(gap.get("reason") or "")[:800]})
                    if not bool(gap.get("done")):
                        dq_any = gap.get("doc_queries")
                        wq_any = gap.get("web_queries")
                        dq_list: list[Any] = dq_any if isinstance(dq_any, list) else []
                        wq_list: list[Any] = wq_any if isinstance(wq_any, list) else []
                        kq = gap.get("kiwix_query")

                        doc_queries_override = [str(x) for x in dq_list if str(x).strip()] if use_docs else None
                        web_queries_override = [str(x) for x in wq_list if str(x).strip()] if use_web else None
                        kiwix_query_override = str(kq).strip() if isinstance(kq, str) and str(kq).strip() else None
                        refinements_used += 1

                        researchstore.add_trace(
                            run_id,
                            "gap_refine",
                            {
                                "round": rno,
                                "refinements_used": refinements_used,
                                "doc_queries": doc_queries_override or [],
                                "web_queries": web_queries_override or [],
                                "kiwix_query": kiwix_query_override,
                            },
                        )
                        continue
                except Exception as e:
                    researchstore.add_trace(run_id, "gap_error", {"round": rno, "error": str(e)})

            supported = sum(1 for c in verify["claims"] if (c.get("status") == "supported"))
            unclear = sum(1 for c in verify["claims"] if (c.get("status") != "supported"))
            researchstore.add_trace(run_id, "round_end", {"round": rno, "supported": supported, "other": unclear})

            round_step["verify"] = {"claims": len(verify["claims"]), "supported": supported, "other": unclear}
            steps.append(round_step)

            done_if = plan.get("done_if") or []
            if done_if:
                try:
                    done_check = await _check_done_if(
                        http,
                        base_url,
                        verifier_model,
                        query=query,
                        done_if=done_if,
                        supported_claims=supported_claims,
                    )
                    researchstore.add_trace(run_id, "done_if", done_check)
                    if bool(done_check.get("done")):
                        break
                except Exception as e:
                    researchstore.add_trace(run_id, "done_if_error", {"error": str(e)})

            if supported >= 6:
                break

        if deep_mode:
            final = await _synthesize(
                http,
                base_url,
                synth_model,
                query,
                mode,
                context_lines,
                verify["claims"],
                embed_model=embed_model,
                ingest_queue=ingest_queue,
                kiwix_url=kiwix_url,
            )
        else:
            final = await _synthesize_from_context(
                http,
                base_url,
                synth_model,
                query=query,
                topics=plan.get("topics") or [],
                context_lines=context_lines,
                deep=False,
            )

        # Stage 3: citation audit (strict mode). Fail closed by rewriting.
        if evidence_policy == "strict" and deep_mode and sources_meta:
            allowed_tags = [str(s.get("citation") or "").strip() for s in sources_meta if str(s.get("citation") or "").strip()]
            allowed_set = set(allowed_tags)
            supported_claims = [
                c
                for c in (verify.get("claims") or [])
                if isinstance(c, dict) and str(c.get("status") or "").strip().lower() == "supported"
            ]
            needs_audit = any(
                k in (final or "").lower()
                for k in (
                    "meta-analysis",
                    "systematic review",
                    "studies show",
                    "study shows",
                    "has been demonstrated",
                    "demonstrated",
                    "shown",
                    "randomized",
                    "statistically",
                )
            )
            if needs_audit and allowed_tags and supported_claims:
                try:
                    audited = await _citation_audit_rewrite(
                        http,
                        base_url,
                        audit_model,
                        query=query,
                        report_md=final,
                        allowed_tags=allowed_tags,
                        supported_claims=supported_claims,
                    )
                    used = extract_citation_tags(audited)
                    invalid = sorted([t for t in used if t not in allowed_set])
                    if audited and not invalid:
                        final = audited
                        researchstore.add_trace(run_id, "citation_audit", {"ok": True})
                    else:
                        researchstore.add_trace(run_id, "citation_audit", {"ok": False, "invalid_tags": invalid[:20]})
                except Exception as e:
                    researchstore.add_trace(run_id, "citation_audit_error", {"error": str(e)})

        sources_section = _format_sources_section(sources_meta)
        if sources_section:
            lower = "\n" + final.lower()
            if "\n## sources" not in lower and "\nsources\n" not in lower:
                final = final.rstrip() + "\n\n" + sources_section

        researchstore.set_run_done(run_id, final)
        researchstore.add_trace(run_id, "done", {"len": len(final)})
        return {
            "ok": True,
            "run_id": run_id,
            "answer": final,
            "sources": sources_meta,
            "steps": steps,
        }

        """
    except Exception as e:
        researchstore.set_run_error(run_id, str(e))
        researchstore.add_trace(run_id, "error", {"error": str(e)})
        raise
    finally:
        if min_token is not None:
            _RUN_MIN_END_AT.reset(min_token)
