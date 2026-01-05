from __future__ import annotations

from typing import Optional

from agent.context import RunContext
from agent.models import StepResult, StepType, ToolResult
from agent.steps.base import BaseStep


class UnderstandStep(BaseStep):
    name = "understand"
    step_type = StepType.UNDERSTAND
    critical = False

    def execute(self) -> StepResult:
        objective = self.ctx.objective

        intent_summary = f"User wants: {objective}"

        if "what does" in objective.lower() or "what is" in objective.lower():
            intent_summary += "\nIntent: Factual information seeking"

        return StepResult(
            step_name=self.name, step_type=self.step_type, ok=True, notes=intent_summary
        )


class PlanStep(BaseStep):
    name = "plan"
    step_type = StepType.PLAN
    critical = False
    step_budget = 3

    def execute(self) -> StepResult:
        objective = self.ctx.objective
        decision = self.ctx.decision

        tools_needed = []
        if decision.mode.value in ("RESEARCH", "HYBRID"):
            tools_needed = ["kiwix_query", "web_search"]
        elif decision.mode.value == "WRITE":
            tools_needed = ["read_file", "list_dir"]
        elif decision.mode.value == "EDIT":
            tools_needed = ["read_file"]

        plan = f"Plan for {decision.mode.value} mode:\n"
        plan += f"- Tools to use: {', '.join(tools_needed) or 'none'}\n"
        plan += (
            f"- Estimated sources needed: {decision.stop_conditions.min_sources or 3}\n"
        )
        plan += (
            f"- Max tool calls: {decision.stop_conditions.max_tool_calls_total or 12}"
        )

        return StepResult(
            step_name=self.name, step_type=self.step_type, ok=True, notes=plan
        )


class GatherStep(BaseStep):
    name = "gather"
    step_type = StepType.GATHER
    critical = True
    step_budget = 10

    def execute(self) -> StepResult:
        objective = self.ctx.objective
        decision = self.ctx.decision

        total_sources = len(self.ctx.sources)
        max_iterations = min(
            5,
            (decision.stop_conditions.max_tool_calls_total or 12)
            - self.ctx.global_budget_used,
        )

        for i in range(max_iterations):
            stop, reason = self._check_stop_condition()
            if stop:
                break

            if decision.mode.value in ("RESEARCH", "HYBRID"):
                result = self._use_tool("kiwix_query", query=objective, max_results=3)
                if result.ok and result.sources_added:
                    continue

                result = self._use_tool("web_search", query=objective, max_results=2)
            elif decision.mode.value == "WRITE":
                result = self._use_tool("rag_search", query=objective, max_results=3)
            else:
                break

        final_sources = len(self.ctx.sources) - total_sources
        return StepResult(
            step_name=self.name,
            step_type=self.step_type,
            ok=True,
            notes=f"Gathered {final_sources} sources in {max_iterations} iteration(s)",
            sources_added=[s.source_id for s in self.ctx.sources[total_sources:]],
        )


class VerifyStep(BaseStep):
    name = "verify"
    step_type = StepType.VERIFY
    critical = False

    def execute(self) -> StepResult:
        decision = self.ctx.decision
        issues = []
        sources_count = len(self.ctx.sources)
        min_sources = decision.stop_conditions.min_sources or 0

        if min_sources > 0 and sources_count < min_sources:
            issues.append(f"Only {sources_count} sources, need at least {min_sources}")

        if not self.ctx.tool_calls:
            issues.append("No tool calls recorded")

        valid = len(issues) == 0
        return StepResult(
            step_name=self.name,
            step_type=self.step_type,
            ok=valid,
            notes=f"Verification {'passed' if valid else 'issues: ' + '; '.join(issues)}",
        )


class SynthesizeStep(BaseStep):
    name = "synthesize"
    step_type = StepType.SYNTHESIZE
    critical = True

    def execute(self) -> StepResult:
        objective = self.ctx.objective
        sources_count = len(self.ctx.sources)

        if sources_count == 0:
            answer = f"Answer to: {objective}\n\nI wasn't able to find any sources to answer this question."
        else:
            answer = (
                f"Answer to: {objective}\n\nBased on {sources_count} source(s):\n\n"
            )
            answer += "[This is a placeholder - LLM would generate actual answer with citations here]"

        self.ctx.final_answer = answer
        return StepResult(
            step_name=self.name,
            step_type=self.step_type,
            ok=True,
            notes=f"Synthesized answer with {sources_count} sources",
        )


class FinalizeStep(BaseStep):
    name = "finalize"
    step_type = StepType.FINALIZE
    critical = True

    def __init__(self, ctx: RunContext, controller: Optional[object] = None):
        super().__init__(ctx, controller)
        self.step_budget = 5

    def execute(self) -> StepResult:
        from agent.citation import CitationEngine

        engine = CitationEngine()

        if not self.ctx.final_answer:
            self.ctx.final_answer = "No answer generated."

        tools_block = engine.format_tools_used_block(self.ctx.tool_calls)
        sources_block = engine.format_sources_block(
            self.ctx.sources, self.ctx.citation_map
        )
        pipeline_block = engine.format_step_history(self.ctx.step_history)

        full_output = self.ctx.final_answer
        if tools_block:
            full_output += "\n\n" + tools_block
        if sources_block:
            full_output += "\n\n" + sources_block
        if pipeline_block:
            full_output += "\n\n" + pipeline_block

        self.ctx.final_answer = full_output
        self.ctx.verified = True

        return StepResult(
            step_name=self.name,
            step_type=self.step_type,
            ok=True,
            notes="Finalized output with citations",
        )


class OutlineStep(BaseStep):
    name = "outline"
    step_type = StepType.OUTLINE
    critical = False

    def execute(self) -> StepResult:
        outline = f"Outline for: {self.ctx.objective}\n\n"
        outline += "1. Introduction\n2. Main Points\n3. Conclusion"

        return StepResult(
            step_name=self.name, step_type=self.step_type, ok=True, notes=outline
        )


class DraftStep(BaseStep):
    name = "draft"
    step_type = StepType.DRAFT
    critical = True

    def execute(self) -> StepResult:
        self.ctx.final_answer = (
            f"Draft of: {self.ctx.objective}\n\n[Placeholder for actual draft]"
        )
        return StepResult(
            step_name=self.name,
            step_type=self.step_type,
            ok=True,
            notes="Draft created",
        )


class AnswerStep(BaseStep):
    name = "answer"
    step_type = StepType.ANSWER
    critical = True

    def execute(self) -> StepResult:
        self.ctx.final_answer = f"Answer: {self.ctx.objective}\n\n[Placeholder - would use LLM to generate answer]"
        return StepResult(
            step_name=self.name,
            step_type=self.step_type,
            ok=True,
            notes="Answer generated",
        )


class ExecuteStep(BaseStep):
    name = "execute"
    step_type = StepType.EXECUTE
    critical = True
    step_budget = 5

    def execute(self) -> StepResult:
        return StepResult(
            step_name=self.name,
            step_type=self.step_type,
            ok=True,
            notes="Execution step - for DEV/OPS mode",
        )
