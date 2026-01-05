from __future__ import annotations

from .models import Mode, StopConditions, ToolBudget

DEFAULTS = {
    Mode.WRITE: {
        "tool_budget": ToolBudget(
            limits={"web_search": 0, "fetch_url": 0, "rag_search": 3}, time_limit_s=60
        ),
        "stop_conditions": StopConditions(max_words=900, max_tool_calls_total=6),
    },
    Mode.EDIT: {
        "tool_budget": ToolBudget(
            limits={"web_search": 0, "fetch_url": 0, "rag_search": 2}, time_limit_s=60
        ),
        "stop_conditions": StopConditions(max_words=900, max_tool_calls_total=4),
    },
    Mode.RESEARCH: {
        "tool_budget": ToolBudget(
            limits={"web_search": 5, "fetch_url": 5, "rag_search": 0}, time_limit_s=120
        ),
        "stop_conditions": StopConditions(
            min_sources=3, max_words=650, max_tool_calls_total=12
        ),
    },
    Mode.HYBRID: {
        "tool_budget": ToolBudget(
            limits={"web_search": 3, "fetch_url": 3, "rag_search": 3}, time_limit_s=120
        ),
        "stop_conditions": StopConditions(
            min_sources=3, max_words=900, max_tool_calls_total=12
        ),
    },
}
