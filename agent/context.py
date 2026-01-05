from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional

from .models import RouteDecision, Source, StepResult, StepType, ToolCall


@dataclass
class Message:
    role: str
    content: str
    meta: Dict[str, Any] = field(default_factory=dict)


@dataclass
class RunContext:
    objective: str
    decision: RouteDecision

    project: str = "default"
    manifest: Any = None
    created_at: str = field(
        default_factory=lambda: datetime.now(timezone.utc).isoformat()
    )
    run_dir: Optional[Path] = None

    messages: List[Message] = field(default_factory=list)

    extras: Dict[str, Any] = field(default_factory=dict)

    attempt: int = 0
    max_retries: int = 2

    step_results: List[StepResult] = field(default_factory=list)
    tool_calls: List[ToolCall] = field(default_factory=list)

    sources: List[Source] = field(default_factory=list)
    citation_map: Dict[str, int] = field(default_factory=dict)
    next_citation_index: int = 1

    global_budget_used: int = 0
    per_tool_used: Dict[str, int] = field(default_factory=dict)

    artifacts: List[Any] = field(default_factory=list)

    final_answer: str = ""
    verified: bool = False

    steps_override: Optional[List[StepType]] = None
    current_step: Optional[str] = None
    step_history: List[Dict] = field(default_factory=list)

    def add_source(self, source: Source) -> int:
        source_id = source.source_id

        if source_id in self.citation_map:
            return self.citation_map[source_id]

        citation_index = self.next_citation_index
        self.next_citation_index += 1

        self.sources.append(source)
        self.citation_map[source_id] = citation_index

        return citation_index

    def get_citation(self, source_id: str) -> Optional[int]:
        return self.citation_map.get(source_id)

    def get_source_by_citation(self, index: int) -> Optional[Source]:
        for source in self.sources:
            if self.citation_map.get(source.source_id) == index:
                return source
        return None

    def can_use_tool(self, tool_name: str, step_budget: Optional[int] = None) -> bool:
        if self.global_budget_used >= (
            self.decision.stop_conditions.max_tool_calls_total or 12
        ):
            return False

        tool_limit = self.decision.tool_budget.limits.get(tool_name, float("inf"))
        used = self.per_tool_used.get(tool_name, 0)
        if used >= tool_limit:
            return False

        if step_budget is not None:
            step_used = sum(
                1 for tc in self.tool_calls if tc.step_name == self.current_step
            )
            if step_used >= step_budget:
                return False

        return True

    def record_tool_use(self, tool_name: str, step_name: str):
        self.global_budget_used += 1
        self.per_tool_used[tool_name] = self.per_tool_used.get(tool_name, 0) + 1

    def add_step_result(self, result: StepResult):
        self.step_results.append(result)
        self.step_history.append(
            {
                "step_name": result.step_name,
                "step_type": result.step_type.value,
                "ok": result.ok,
                "notes": result.notes,
                "tool_calls_count": len(result.tool_calls),
                "sources_added": len(result.sources_added),
                "timestamp": datetime.now(timezone.utc).isoformat(),
            }
        )
