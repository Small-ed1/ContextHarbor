from __future__ import annotations

import json
import os
import re
from typing import Any, Optional

from ollama import Client

from .toolcore import ToolRegistry


PLAN_SYSTEM = """You are a tool planner.

Return ONLY JSON in this schema:
{
  "use_tools": true|false,
  "reason": "short reason",
  "calls": [
    {"name": "tool_name", "arguments": { ... }, "purpose": "why"}
  ]
}

Rules:
- Use tools when the question asks for real-world facts, current status, or winners.
- If the user asks a who/what/when/where/which question, prefer web_search.
- Keep calls minimal and relevant to the user question.
- If no tool is required, set use_tools=false and calls=[].
"""

INTERPRET_SYSTEM = """You interpret user questions.

Return ONLY JSON in this schema:
{
  "intent": "short paraphrase",
  "question": "what the user is asking",
  "needs_tools": true|false,
  "key_terms": ["term1", "term2"]
}

Rules:
- needs_tools should be true for real-world facts, winners, or lookup requests.
- Keep intent and question short and concrete.
- Do not add extra constraints or criteria that are not present in the user message.
"""

ANSWER_SYSTEM = """You are a helpful assistant.

Tools are disabled for this reply.
If you are missing facts, say so and explain what is missing.
"""

SYNTH_SYSTEM = """You are a synthesis assistant.

Use ONLY the tool results provided to answer the user.
If a claim is not supported by tool data, say you do not know.
Cite sources with [T1], [T2], etc based on the tool result tags.
"""

SUMMARY_SYSTEM = """You summarize tool results.

Return a short, structured summary of the evidence.
Focus on facts directly supported by the tool output.
"""

SUFFICIENCY_SYSTEM = """You check if tool evidence is sufficient.

Return ONLY JSON in this schema:
{
  "sufficient": true|false,
  "reason": "short reason",
  "calls": [
    {"name": "tool_name", "arguments": { ... }, "purpose": "why"}
  ]
}

Rules:
- If sufficient, set calls=[].
- If insufficient, propose minimal follow-up tool calls.
"""

_WORDS = re.compile(r"[a-z0-9]{2,}")

TOOL_HINTS = (
    "http://",
    "https://",
    "search",
    "lookup",
    "find",
    "latest",
    "current",
    "news",
    "price",
    "citation",
    "source",
    "wikipedia",
    "wiki",
    "statistics",
    "data",
    "who is",
    "who's",
    "what is",
    "when was",
    "where is",
    "calculate",
    "compute",
    "convert",
    "time",
    "date",
)

QUESTION_WORDS = {
    "who",
    "what",
    "when",
    "where",
    "which",
    "latest",
    "current",
    "today",
    "now",
    "winner",
    "champion",
}

MAX_TOOL_CALLS = int(os.getenv("TOOL_MAX_CALLS", "4"))
MAX_TOOL_RESULT_CHARS = int(os.getenv("TOOL_RESULT_MAX_CHARS", "3500"))
SEARCH_TOP_K = int(os.getenv("TOOL_SEARCH_TOP_K", "5"))
SEARCH_MIN_SCORE = int(os.getenv("TOOL_SEARCH_MIN_SCORE", "1"))
MAX_TOOL_ROUNDS = int(os.getenv("TOOL_MAX_ROUNDS", "3"))


def _extract_first_json_obj(text: str) -> Optional[dict[str, Any]]:
    """Robustly find the first {...} JSON object in a string and parse it."""

    s = text.strip()
    if not s:
        return None

    search_start = 0
    while True:
        start = s.find("{", search_start)
        if start < 0:
            return None

        depth = 0
        in_str = False
        esc = False
        for i in range(start, len(s)):
            ch = s[i]
            if in_str:
                if esc:
                    esc = False
                elif ch == "\\":
                    esc = True
                elif ch == '"':
                    in_str = False
                continue

            if ch == '"':
                in_str = True
                continue
            if ch == "{":
                depth += 1
            elif ch == "}":
                depth -= 1
                if depth == 0:
                    blob = s[start : i + 1]
                    try:
                        return json.loads(blob)
                    except json.JSONDecodeError:
                        search_start = start + 1
                        break
        else:
            return None


def _extract_message_content(resp: Any) -> str:
    message = resp.get("message") if hasattr(resp, "get") else getattr(resp, "message", None)
    content: str | None = None
    tool_calls = None
    if isinstance(message, dict):
        content = message.get("content")
        tool_calls = message.get("tool_calls")
    elif message is not None:
        if hasattr(message, "get"):
            content = message.get("content")
            tool_calls = message.get("tool_calls")
        else:
            content = getattr(message, "content", None)
            tool_calls = getattr(message, "tool_calls", None)

    out = content if isinstance(content, str) else ""
    if out.strip():
        return out

    if not tool_calls:
        return ""

    first_call = tool_calls[0] if isinstance(tool_calls, (list, tuple)) else None
    function = None
    if isinstance(first_call, dict):
        function = first_call.get("function")
    elif first_call is not None:
        if hasattr(first_call, "get"):
            function = first_call.get("function")
        else:
            function = getattr(first_call, "function", None)

    tool_name = None
    tool_args: dict[str, Any] = {}
    if isinstance(function, dict):
        tool_name = function.get("name")
        args = function.get("arguments")
    elif function is not None:
        if hasattr(function, "get"):
            tool_name = function.get("name")
            args = function.get("arguments")
        else:
            tool_name = getattr(function, "name", None)
            args = getattr(function, "arguments", None)
    else:
        args = None

    if isinstance(args, dict):
        tool_args = args
    elif args is not None:
        try:
            tool_args = dict(args)
        except Exception:
            tool_args = {}

    if isinstance(tool_name, str) and tool_name:
        return json.dumps({"type": "tool_call", "name": tool_name, "arguments": tool_args})

    return ""


def _word_tokens(text: str) -> list[str]:
    return _WORDS.findall((text or "").lower())


def _overlap_ratio(a: list[str], b: list[str]) -> float:
    if not a or not b:
        return 0.0
    aset = set(a)
    bset = set(b)
    return len(aset & bset) / max(1, len(bset))


def _should_consider_tools(text: str) -> bool:
    t = (text or "").lower()
    if any(hint in t for hint in TOOL_HINTS):
        return True
    tokens = _word_tokens(t)
    if len(tokens) < 3:
        return False
    if "?" in t:
        if any(word in QUESTION_WORDS for word in tokens):
            return True
    if tokens and tokens[0] in QUESTION_WORDS:
        return True
    return False


def _score_overlap(tokens: set[str], text: str) -> int:
    if not tokens:
        return 0
    words = set(_word_tokens(text))
    return len(tokens & words)


def _truncate(text: str, limit: int) -> str:
    if len(text) <= limit:
        return text
    return text[:limit].rstrip() + "..."


class Agent:
    def __init__(self, model: str = "qwen3:14b", host: str = "http://127.0.0.1:11434") -> None:
        self.model = model
        self.client = Client(host=host)
        self.tools = ToolRegistry()

        self.interpret_model = os.getenv("TOOL_INTERPRET_MODEL", self.model)
        self.planner_model = os.getenv("TOOL_PLANNER_MODEL", self.model)
        self.summary_model = os.getenv("TOOL_SUMMARY_MODEL", self.model)
        self.sufficiency_model = os.getenv("TOOL_SUFFICIENCY_MODEL", self.model)
        self.answer_model = os.getenv("TOOL_ANSWER_MODEL", self.model)

        self.history: list[dict[str, str]] = []
        self.trace = os.getenv("TOOL_TRACE", "0") == "1"

    def _dbg(self, *msg: Any) -> None:
        if self.trace:
            print("[TRACE]", *msg)

    def _chat_once(
        self,
        messages: list[dict[str, str]],
        temperature: float = 0.2,
        model: Optional[str] = None,
    ) -> str:
        resp = self.client.chat(
            model=model or self.model,
            messages=messages,
            options={"temperature": temperature},
        )
        return _extract_message_content(resp)

    def _recent_context(self, limit: int = 6) -> str:
        msgs = [m for m in self.history[:-1] if m.get("role") in {"user", "assistant"}]
        if not msgs:
            return ""
        lines = [f"{m['role']}: {m['content']}" for m in msgs[-limit:]]
        return "\n".join(lines).strip()

    def _interpret_user(self, user_text: str) -> dict[str, Any]:
        context = self._recent_context()
        prompt = f"User question: {user_text}"
        if context:
            prompt = f"Context:\n{context}\n\n{prompt}"
        out = self._chat_once(
            [{"role": "system", "content": INTERPRET_SYSTEM}, {"role": "user", "content": prompt}],
            temperature=0.0,
            model=self.interpret_model,
        )
        self._dbg("INTERPRET_OUT:", out)
        obj = _extract_first_json_obj(out)
        if not obj:
            return {
                "intent": user_text,
                "question": user_text,
                "needs_tools": _should_consider_tools(user_text),
                "key_terms": _word_tokens(user_text)[:6],
            }

        if "needs_tools" not in obj:
            obj["needs_tools"] = _should_consider_tools(user_text)
        if "intent" not in obj:
            obj["intent"] = user_text
        if "question" not in obj:
            obj["question"] = user_text
        if "key_terms" not in obj or not isinstance(obj["key_terms"], list):
            obj["key_terms"] = _word_tokens(user_text)[:6]

        question = obj.get("question") or ""
        q_tokens = _word_tokens(question)
        u_tokens = _word_tokens(user_text)
        if q_tokens and (len(question) > len(user_text) * 2 + 40 or _overlap_ratio(u_tokens, q_tokens) < 0.5):
            obj["question"] = user_text

        intent = obj.get("intent") or ""
        if intent and len(intent) > len(user_text) * 2 + 40:
            obj["intent"] = user_text
        return obj

    def _plan_tools(
        self,
        user_text: str,
        interpretation: Optional[dict[str, Any]] = None,
    ) -> Optional[dict[str, Any]]:
        tool_blob = json.dumps(self.tools.schema_for_prompt(), indent=2)
        sys = PLAN_SYSTEM + "\n\nAvailable tools:\n" + tool_blob
        context = self._recent_context()
        user_block = f"Question: {user_text}"
        if interpretation:
            user_block = (
                f"Interpretation: {json.dumps(interpretation, ensure_ascii=False)}\n" + user_block
            )
        if context:
            user_block = f"Context:\n{context}\n\n{user_block}"
        out = self._chat_once(
            [{"role": "system", "content": sys}, {"role": "user", "content": user_block}],
            temperature=0.0,
            model=self.planner_model,
        )
        self._dbg("PLAN_OUT:", out)
        obj = _extract_first_json_obj(out)
        if not obj:
            return None

        if obj.get("type") == "tool_call" or obj.get("name"):
            name = obj.get("name") or obj.get("type")
            args = obj.get("arguments") if isinstance(obj.get("arguments"), dict) else obj.get("args")
            if not isinstance(args, dict):
                args = {}
            if name:
                return {"use_tools": True, "reason": "tool_call", "calls": [{"name": name, "arguments": args}]}

        return obj

    def _fallback_plan(self, user_text: str) -> Optional[dict[str, Any]]:
        if self.tools.get("web_search"):
            return {
                "use_tools": True,
                "reason": "heuristic_web_search",
                "calls": [
                    {
                        "name": "web_search",
                        "arguments": {"query": user_text, "max_results": SEARCH_TOP_K},
                        "purpose": "Find current factual info",
                    }
                ],
            }
        return None

    def _answer_without_tools(self, user_text: str, reason: str | None = None) -> str:
        context = self._recent_context()
        prompt = f"Question: {user_text}"
        if reason:
            prompt = f"Reason: {reason}\n" + prompt
        if context:
            prompt = f"Context:\n{context}\n\n{prompt}"
        return self._chat_once(
            [{"role": "system", "content": ANSWER_SYSTEM}, {"role": "user", "content": prompt}],
            temperature=0.2,
            model=self.answer_model,
        )

    def _filter_search_results(self, results: list[dict[str, Any]], query: str) -> list[dict[str, Any]]:
        tokens = set(_word_tokens(query))
        seen = set()
        scored = []
        for r in results:
            url = (r.get("url") or "").strip().lower()
            if url and url in seen:
                continue
            text = f"{r.get('title', '')} {r.get('snippet', '')}"
            score = _score_overlap(tokens, text)
            if url:
                seen.add(url)
            scored.append((score, r))

        scored.sort(key=lambda x: x[0], reverse=True)
        kept = [r for score, r in scored if score >= SEARCH_MIN_SCORE]
        if not kept:
            kept = [r for _, r in scored]
        return kept[:SEARCH_TOP_K]

    def _normalize_tool_result(self, tool_name: str, result: Any, query: str) -> Any:
        if tool_name in {"web_search", "site_search"} and isinstance(result, list):
            return self._filter_search_results(result, query)
        if isinstance(result, dict):
            out = dict(result)
            if "text" in out and isinstance(out["text"], str):
                out["text"] = _truncate(out["text"], MAX_TOOL_RESULT_CHARS)
            if "html" in out and isinstance(out["html"], str):
                out["html"] = _truncate(out["html"], MAX_TOOL_RESULT_CHARS)
            if "extract" in out and isinstance(out["extract"], str):
                out["extract"] = _truncate(out["extract"], MAX_TOOL_RESULT_CHARS)
            return out
        if isinstance(result, str):
            return _truncate(result, MAX_TOOL_RESULT_CHARS)
        return result

    def _run_tool_calls(self, calls: list[dict[str, Any]], query: str) -> list[dict[str, Any]]:
        tool_results = []
        for idx, call in enumerate(calls[:MAX_TOOL_CALLS], start=1):
            name = (call.get("name") or "").strip()
            args = call.get("arguments") or {}
            if not isinstance(args, dict):
                args = {}
            if not name or not self.tools.get(name):
                tool_results.append(
                    {
                        "id": f"T{idx}",
                        "tool": name or "unknown",
                        "args": args,
                        "ok": False,
                        "error": f"Unknown tool: {name}",
                    }
                )
                continue

            self._dbg("TOOL_CALL:", name, args)
            result = self.tools.call(name, args)
            self._dbg("TOOL_RESULT:", result)
            if result.get("ok") is True:
                normalized = self._normalize_tool_result(name, result.get("result"), query)
                tool_results.append(
                    {
                        "id": f"T{idx}",
                        "tool": name,
                        "args": args,
                        "ok": True,
                        "result": normalized,
                    }
                )
            else:
                tool_results.append(
                    {
                        "id": f"T{idx}",
                        "tool": name,
                        "args": args,
                        "ok": False,
                        "error": result.get("error") or "tool failed",
                    }
                )
        return tool_results

    def _format_tool_results(self, tool_results: list[dict[str, Any]]) -> str:
        lines = []
        for tr in tool_results:
            tag = tr.get("id")
            tool = tr.get("tool")
            lines.append(f"[{tag}] tool={tool}")
            if tr.get("ok"):
                payload = tr.get("result")
                lines.append(json.dumps(payload, ensure_ascii=False, indent=2))
            else:
                lines.append(f"error: {tr.get('error')}")
            lines.append("")
        return "\n".join(lines).strip()

    def _summarize_results(self, user_text: str, tool_results: list[dict[str, Any]]) -> str:
        tool_block = self._format_tool_results(tool_results)
        prompt = f"Question: {user_text}\n\nTool results:\n{tool_block}\n"
        return self._chat_once(
            [{"role": "system", "content": SUMMARY_SYSTEM}, {"role": "user", "content": prompt}],
            temperature=0.2,
            model=self.summary_model,
        )

    def _check_sufficiency(
        self,
        user_text: str,
        summary: str,
        tool_results: list[dict[str, Any]],
    ) -> dict[str, Any]:
        tool_blob = json.dumps(self.tools.schema_for_prompt(), indent=2)
        tool_block = self._format_tool_results(tool_results)
        prompt = (
            f"Question: {user_text}\n\nSummary:\n{summary}\n\nTool results:\n{tool_block}\n\n"
            "If more evidence is required, propose follow-up tool calls."
        )
        out = self._chat_once(
            [{"role": "system", "content": SUFFICIENCY_SYSTEM + "\n\nAvailable tools:\n" + tool_blob},
             {"role": "user", "content": prompt}],
            temperature=0.0,
            model=self.sufficiency_model,
        )
        self._dbg("SUFFICIENCY_OUT:", out)
        obj = _extract_first_json_obj(out)
        if not obj:
            return {"sufficient": True, "reason": "no_parse", "calls": []}
        if "sufficient" not in obj:
            obj["sufficient"] = True
        if "calls" not in obj or not isinstance(obj["calls"], list):
            obj["calls"] = []
        return obj

    def _synthesize(
        self,
        user_text: str,
        plan: dict[str, Any],
        tool_results: list[dict[str, Any]],
        interpretation: Optional[dict[str, Any]] = None,
        summaries: Optional[list[str]] = None,
    ) -> str:
        context = self._recent_context()
        tool_block = self._format_tool_results(tool_results)
        user_block = f"Question: {user_text}"
        if interpretation:
            user_block = (
                f"Interpretation: {json.dumps(interpretation, ensure_ascii=False)}\n" + user_block
            )
        if context:
            user_block = f"Context:\n{context}\n\n{user_block}"
        summary_block = ""
        if summaries:
            summary_text = "\n".join(summaries).strip()
            if summary_text:
                summary_block = f"Summaries:\n{summary_text}\n\n"
        prompt = f"{summary_block}{user_block}\n\nTool results:\n{tool_block}\n"
        if plan.get("reason"):
            prompt = f"Planner reason: {plan['reason']}\n\n" + prompt
        return self._chat_once(
            [{"role": "system", "content": SYNTH_SYSTEM}, {"role": "user", "content": prompt}],
            temperature=0.2,
            model=self.answer_model,
        )

    def chat(self, user_text: str) -> str:
        self.history.append({"role": "user", "content": user_text})

        try:
            interpretation = self._interpret_user(user_text)
            self._dbg("INTERPRETATION:", interpretation)

            needs_tools = bool(interpretation.get("needs_tools")) or _should_consider_tools(user_text)
            if not needs_tools:
                out = self._answer_without_tools(user_text)
                self.history.append({"role": "assistant", "content": out})
                return out

            plan = self._plan_tools(user_text, interpretation) or {}
            use_tools = bool(plan.get("use_tools"))
            calls = plan.get("calls") if isinstance(plan.get("calls"), list) else []

            if not use_tools or not calls:
                fallback = self._fallback_plan(user_text)
                if fallback:
                    plan = fallback
                    use_tools = True
                    calls = plan.get("calls") if isinstance(plan.get("calls"), list) else []

            if not use_tools or not calls:
                out = self._answer_without_tools(user_text, plan.get("reason"))
                self.history.append({"role": "assistant", "content": out})
                return out

            aggregated_results: list[dict[str, Any]] = []
            summaries: list[str] = []
            plan_reason = plan.get("reason")
            current_calls = calls

            for round_idx in range(MAX_TOOL_ROUNDS):
                if not current_calls:
                    break
                self._dbg("TOOL_ROUND:", round_idx + 1)
                tool_results = self._run_tool_calls(current_calls, user_text)
                aggregated_results.extend(tool_results)

                summary = self._summarize_results(user_text, tool_results)
                summaries.append(summary)
                self._dbg("SUMMARY_OUT:", summary)

                sufficiency = self._check_sufficiency(user_text, summary, aggregated_results)
                if sufficiency.get("sufficient"):
                    if sufficiency.get("reason") and not plan_reason:
                        plan_reason = sufficiency.get("reason")
                    break

                current_calls = (
                    sufficiency.get("calls") if isinstance(sufficiency.get("calls"), list) else []
                )
                if not current_calls:
                    break

            if not aggregated_results:
                out = self._answer_without_tools(user_text, plan_reason)
                self.history.append({"role": "assistant", "content": out})
                return out

            synth_plan = {"reason": plan_reason or ""}
            out = self._synthesize(user_text, synth_plan, aggregated_results, interpretation, summaries)
            self.history.append({"role": "assistant", "content": out})
            return out
        except Exception as exc:
            err = f"Agent failure: {exc}"
            self.history.append({"role": "assistant", "content": err})
            return err
