from __future__ import annotations

import re
from dataclasses import dataclass
from functools import lru_cache
from typing import Dict, List, Optional, Tuple


@dataclass
class MockTool:
    name: str
    description: str

from .defaults import DEFAULTS
from .models import Mode, RouteDecision, StopConditions, ToolBudget

# Configurable tool list
AVAILABLE_TOOLS = [
    "read_file",
    "list_dir",
    "write_file",
    "edit_file",
    "web_search",
    "kiwix_query",
    "fetch_url",
    "rag_search",
    "github_search",
    "github_fetch",
    "run_command",
    "duckduckgo_search",
    "iterative_research",
]

_OVERRIDE_RE = re.compile(r"\bmode\s*=\s*(WRITE|EDIT|RESEARCH|HYBRID)\b", re.IGNORECASE)
_RESEARCH_MODE_RE = re.compile(
    r"\bresearch\s*mode\s*=\s*(QUICK|STANDARD|DEEP)\b", re.IGNORECASE
)

WRITE_KEYWORDS = (
    "write",
    "compose",
    "create",
    "generate",
    "make a",
    "chapter",
    "scene",
)
EDIT_KEYWORDS = (
    "edit",
    "revise",
    "proofread",
    "polish",
    "tighten",
    "rewrite",
    "fix grammar",
    "improve this",
)
RESEARCH_KEYWORDS = (
    "find",
    "sources",
    "citations",
    "evidence",
    "look up",
    "research",
    "verify",
    "compare",
    "what's the latest",
    "stats",
    "data",
    "wikipedia",
    "what does",
)
HYBRID_KEYWORDS = (
    "summarize",
    "explain",
    "overview",
    "outline",
    "report",
    "teach me",
    "walk me through",
)
FACT_SEEKING_HINTS = (
    "according to",
    "study",
    "paper",
    "dataset",
    "official",
    "documentation",
    "release notes",
)


_KNOWLEDGE_PATTERNS = frozenset(("what", "how", "explain", "tell me about", "search"))
_RESEARCH_PATTERNS = frozenset(
    ("research", "find sources", "citations", "evidence", "latest")
)
_FILE_PATTERNS = frozenset(("read", "check", "examine", "look at", "analyze"))
_WEB_PATTERNS = frozenset(("news", "current", "recent", "trending", "update"))
_GITHUB_PATTERNS = frozenset(
    (
        "github",
        "repository",
        "repo",
        "git",
        "commit",
        "pull request",
        "issue",
        "code search",
    )
)


@dataclass(frozen=True)
class RouterConfig:
    default_mode: Mode = Mode.HYBRID
    low_conf_threshold: float = 0.55


def _extract_override(text: str) -> Optional[Mode]:
    m = _OVERRIDE_RE.search(text or "")
    if not m:
        return None
    return Mode(m.group(1).upper())


def _score(text: str) -> Tuple[Mode, float, List[str]]:
    t = text.lower() if text else ""
    signals: List[str] = []

    # Check keywords and build signals
    keyword_matches = {
        "write": any(k in t for k in WRITE_KEYWORDS),
        "edit": any(k in t for k in EDIT_KEYWORDS),
        "research": any(k in t for k in RESEARCH_KEYWORDS),
        "hybrid": any(k in t for k in HYBRID_KEYWORDS),
        "facty": any(k in t for k in FACT_SEEKING_HINTS),
    }

    for kw, found in keyword_matches.items():
        if found:
            signals.append(f"kw:{kw}" if kw != "facty" else "hint:fact-seeking")

    write, edit, research, hybrid, facty = keyword_matches.values()

    # Decision logic - ordered by precedence
    if edit and not (write or research):
        return Mode.EDIT, 0.85, signals
    if edit and write and not research:
        return Mode.EDIT, 0.80, signals + ["tie:edit>write"]
    if research and not (write or edit):
        return Mode.RESEARCH, 0.80 if facty else 0.72, signals
    if write and research:
        return Mode.HYBRID, 0.70 if facty else 0.62, signals
    if hybrid and (research or facty):
        return Mode.HYBRID, 0.68, signals
    if write and hybrid and not research:
        return Mode.HYBRID, 0.66, signals + ["combo:write+hybrid"]
    if write:
        return Mode.WRITE, 0.65, signals
    if hybrid:
        return Mode.HYBRID, 0.60, signals
    if research or facty:
        return Mode.RESEARCH, 0.58, signals

    return Mode.HYBRID, 0.45, signals + ["kw:none-strong"]


def _recommend_tools(user_text: str, mode: Mode) -> List[str]:
    """Recommend tools using intelligent selection"""
    try:
        from .intelligent_tools import IntelligentToolSelector
        from .tool_learning import get_learning_system

        # Get all available tools
        available_tools = [MockTool(name=tool_name, description=f"Mock {tool_name} tool") for tool_name in AVAILABLE_TOOLS]

        # Use intelligent selector
        selector = IntelligentToolSelector(available_tools)  # type: ignore
        intelligent_selection = selector.select_tools(user_text, mode, max_tools=6)

        # Get learning system recommendations
        learning_system = get_learning_system()
        learning_recommendations = learning_system.get_tool_recommendations(
            user_text, str(mode)
        )

        # Combine and rank tools
        tool_scores: Dict[str, float] = {}
        for i, tool in enumerate(intelligent_selection):
            tool_scores[tool] = float(10 - i)  # Base score from intelligent selection

        for tool, score in learning_recommendations.items():
            if tool in tool_scores:
                tool_scores[tool] += score * 3  # Weight learning data
            else:
                tool_scores[tool] = score * 3

        # Sort by score and return top tools
        sorted_tools = sorted(tool_scores.items(), key=lambda x: x[1], reverse=True)
        final_tools = [tool for tool, score in sorted_tools[:8]]

        return final_tools

    except ImportError:
        # Fallback to keyword-based selection if intelligent tools not available
        return _recommend_tools_fallback(user_text, mode)


def _recommend_tools_fallback(user_text: str, mode: Mode) -> List[str]:
    """Fallback keyword-based tool recommendation"""
    t = user_text.lower() if user_text else ""
    tools: List[str] = []

    if any(p in t for p in _KNOWLEDGE_PATTERNS):
        tools.extend(("kiwix_query", "rag_search"))

    if any(p in t for p in _RESEARCH_PATTERNS):
        tools.extend(("kiwix_query", "web_search", "fetch_url"))

    if any(p in t for p in _FILE_PATTERNS):
        tools.extend(("read_file", "list_dir"))

    if any(p in t for p in _WEB_PATTERNS):
        tools.append("web_search")

    if mode == Mode.RESEARCH:
        tools = [
            "kiwix_query",
            "web_search",
            "fetch_url",
            "duckduckgo_search",
            "iterative_research",
        ]
    elif mode == Mode.HYBRID:
        tools = ["kiwix_query", "web_search", "rag_search", "read_file", "list_dir"]
    elif mode == Mode.WRITE:
        tools = [t for t in tools if t in ("read_file", "list_dir", "rag_search")]
    elif mode == Mode.EDIT:
        tools = [
            t
            for t in tools
            if t in ("read_file", "list_dir", "rag_search", "kiwix_query")
        ]

    return list(dict.fromkeys(tools))  # Preserve order while removing duplicates


def _recommend_steps(mode: Mode) -> List[str]:
    mode_str = mode.value if hasattr(mode, "value") else str(mode)
    step_maps = {
        "WRITE": ["understand", "outline", "draft", "finalize"],
        "EDIT": ["understand", "plan", "draft", "finalize"],
        "RESEARCH": [
            "understand",
            "plan",
            "gather",
            "verify",
            "synthesize",
            "finalize",
        ],
        "HYBRID": ["understand", "plan", "gather", "synthesize", "finalize"],
    }
    return step_maps.get(mode_str, ["understand", "finalize"])


@lru_cache(maxsize=128)
def _route_cached(text_hash: int, text: str, config_tuple: Tuple) -> RouteDecision:
    config = RouterConfig(*config_tuple) if config_tuple else RouterConfig()
    return _route_impl(text, config)


def _route_impl(user_text: str, config: RouterConfig) -> RouteDecision:
    override = _extract_override(user_text)
    if override is not None:
        d = DEFAULTS[override]
        recommended_tools = _recommend_tools(user_text, override)
        recommended_steps = _recommend_steps(override)
        return RouteDecision(
            mode=override,
            confidence=1.0,
            warning=None,
            tool_budget=ToolBudget.model_validate(d["tool_budget"]),
            stop_conditions=StopConditions.model_validate(d["stop_conditions"]),
            signals=["override:mode"],
            override_used=True,
            recommended_tools=recommended_tools,
            recommended_steps=recommended_steps,
        )

    mode, conf, signals = _score(user_text)
    recommended_tools = _recommend_tools(user_text, mode)
    recommended_steps = _recommend_steps(mode)

    warning = None
    if conf < config.low_conf_threshold:
        warning = f"Mode confidence low ({conf:.2f}); defaulted to {config.default_mode.value}"
        mode = config.default_mode
        signals.append("fallback:default-mode")

    d = DEFAULTS[mode]
    return RouteDecision(
        mode=mode,
        confidence=conf,
        warning=warning,
        tool_budget=ToolBudget.model_validate(d["tool_budget"]),
        stop_conditions=StopConditions.model_validate(d["stop_conditions"]),
        signals=signals,
        override_used=False,
        recommended_tools=recommended_tools,
        recommended_steps=recommended_steps,
    )


def route(user_text: str, config: RouterConfig = RouterConfig()) -> RouteDecision:
    config_tuple = (
        (config.default_mode.value, config.low_conf_threshold)
        if config != RouterConfig()
        else None
    )
    return _route_cached(hash(user_text), user_text, config_tuple)
