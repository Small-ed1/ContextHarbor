from __future__ import annotations

from abc import ABC, abstractmethod
from typing import TYPE_CHECKING, Optional

from agent.context import RunContext
from agent.models import StepResult, StepType, ToolResult

if TYPE_CHECKING:
    from agent.controller import Controller


class BaseStep(ABC):
    name: str
    step_type: StepType
    critical: bool = False
    repeatable: bool = False

    def __init__(self, ctx: RunContext, controller: Optional["Controller"] = None):
        self.ctx = ctx
        self.controller = controller
        self.step_budget: int = 5

    @abstractmethod
    def execute(self) -> StepResult:
        pass

    def _use_tool(self, tool_name: str, **kwargs) -> StepResult:
        if not self.ctx.can_use_tool(tool_name, self.step_budget):
            return StepResult(
                step_name=self.name,
                step_type=self.step_type,
                ok=False,
                notes=f"Budget exceeded for {tool_name}",
            )

        if not self.controller:
            return StepResult(
                step_name=self.name,
                step_type=self.step_type,
                ok=False,
                notes="No controller available",
            )

        try:
            # Type ignore for dynamic method access
            result = self.controller.execute_tool(tool_name, **kwargs)  # type: ignore

            from agent.models import ToolCall

            tc = ToolCall(
                name=tool_name, parameters=kwargs, result=result, step_name=self.name
            )
            self.ctx.tool_calls.append(tc)

            sources_added = []
            for source in result.sources:
                citation_idx = self.ctx.add_source(source)
                sources_added.append(source.source_id)

            self.ctx.record_tool_use(tool_name, self.name)

            return StepResult(
                step_name=self.name,
                step_type=self.step_type,
                ok=result.ok,
                notes=f"Tool {tool_name} executed",
                tool_calls=[tc],
                sources_added=sources_added,
            )

        except Exception as e:
            return StepResult(
                step_name=self.name,
                step_type=self.step_type,
                ok=False,
                notes=f"Tool {tool_name} failed: {str(e)}",
            )

    def _check_stop_condition(self) -> tuple[bool, str]:
        max_calls = self.ctx.decision.stop_conditions.max_tool_calls_total or 12
        if self.ctx.global_budget_used >= max_calls:
            return True, "budget_exhausted"

        min_sources = self.ctx.decision.stop_conditions.min_sources or 0
        if min_sources > 0 and len(self.ctx.sources) >= min_sources:
            return True, "min_sources_reached"

        return False, ""
