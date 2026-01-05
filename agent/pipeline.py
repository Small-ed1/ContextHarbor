from __future__ import annotations

from typing import TYPE_CHECKING, Optional

from agent.context import RunContext
from agent.models import StepType
from agent.steps.base import BaseStep

if TYPE_CHECKING:
    from agent.controller import Controller


STEP_CLASSES: dict[StepType, type[BaseStep] | None] = {
    StepType.UNDERSTAND: None,
    StepType.PLAN: None,
    StepType.GATHER: None,
    StepType.VERIFY: None,
    StepType.SYNTHESIZE: None,
    StepType.FINALIZE: None,
    StepType.OUTLINE: None,
    StepType.DRAFT: None,
    StepType.ANSWER: None,
    StepType.EXECUTE: None,
}


def _register_step(step_type: StepType, step_class: type):
    STEP_CLASSES[step_type] = step_class


def _import_steps():
    from agent.steps import (AnswerStep, DraftStep, ExecuteStep, FinalizeStep,
                             GatherStep, OutlineStep, PlanStep, SynthesizeStep,
                             UnderstandStep, VerifyStep)

    _register_step(StepType.UNDERSTAND, UnderstandStep)
    _register_step(StepType.PLAN, PlanStep)
    _register_step(StepType.GATHER, GatherStep)
    _register_step(StepType.VERIFY, VerifyStep)
    _register_step(StepType.SYNTHESIZE, SynthesizeStep)
    _register_step(StepType.FINALIZE, FinalizeStep)
    _register_step(StepType.OUTLINE, OutlineStep)
    _register_step(StepType.DRAFT, DraftStep)
    _register_step(StepType.ANSWER, AnswerStep)
    _register_step(StepType.EXECUTE, ExecuteStep)


DEFAULT_PIPELINE: dict[str, list[StepType]] = {
    "WRITE": [StepType.UNDERSTAND, StepType.OUTLINE, StepType.DRAFT, StepType.FINALIZE],
    "EDIT": [StepType.UNDERSTAND, StepType.PLAN, StepType.DRAFT, StepType.FINALIZE],
    "RESEARCH": [
        StepType.UNDERSTAND,
        StepType.PLAN,
        StepType.GATHER,
        StepType.VERIFY,
        StepType.SYNTHESIZE,
        StepType.FINALIZE,
    ],
    "HYBRID": [
        StepType.UNDERSTAND,
        StepType.PLAN,
        StepType.GATHER,
        StepType.SYNTHESIZE,
        StepType.FINALIZE,
    ],
}


class Pipeline:
    def __init__(self, ctx: RunContext, controller: Optional["Controller"] = None):
        self.ctx = ctx
        self.controller = controller
        self.steps: list = []
        self._build_pipeline()

    def _build_pipeline(self):
        _import_steps()
        mode = self.ctx.decision.mode.value

        if self.ctx.steps_override:
            step_types = self.ctx.steps_override
        else:
            step_types = DEFAULT_PIPELINE.get(mode, [])

        for step_type in step_types:
            step_class = STEP_CLASSES.get(step_type)
            if step_class:
                self.steps.append(step_class(self.ctx, self.controller))

    def execute(self) -> RunContext:
        for step in self.steps:
            self.ctx.current_step = step.name

            result = step.execute()
            self.ctx.add_step_result(result)

            if not result.ok and step.critical:
                self.ctx.final_answer = self._format_error(result)
                return self.ctx

        finalize_class = STEP_CLASSES.get(StepType.FINALIZE)
        if finalize_class:
            finalize_step = finalize_class(self.ctx, self.controller)
            finalize_result = finalize_step.execute()
            self.ctx.add_step_result(finalize_result)

        return self.ctx

    def _format_error(self, result) -> str:
        return f"Pipeline halted at step '{result.step_name}': {result.notes}"


def execute_pipeline(
    ctx: RunContext, controller: Optional["Controller"] = None
) -> RunContext:
    pipeline = Pipeline(ctx, controller)
    return pipeline.execute()
