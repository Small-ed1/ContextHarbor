import unittest
from unittest.mock import Mock, patch

from agent.context import RunContext
from agent.models import (Mode, RouteDecision, StepType, StopConditions,
                          ToolBudget)
from agent.pipeline import Pipeline, execute_pipeline


class TestPipeline(unittest.TestCase):
    def setUp(self):
        self.decision = RouteDecision(
            mode=Mode.RESEARCH,
            confidence=0.8,
            tool_budget=ToolBudget(),
            stop_conditions=StopConditions(),
        )
        self.ctx = RunContext(objective="Test objective", decision=self.decision)
        self.controller = Mock()

    def test_pipeline_building(self):
        from agent.steps import (FinalizeStep, GatherStep, PlanStep,
                                 SynthesizeStep, UnderstandStep, VerifyStep)

        pipeline = Pipeline(self.ctx, self.controller)

        self.assertEqual(len(pipeline.steps), 6)  # RESEARCH pipeline has 6 steps

    def test_default_pipelines(self):
        from agent.pipeline import DEFAULT_PIPELINE

        self.assertIn("WRITE", DEFAULT_PIPELINE)
        self.assertIn("EDIT", DEFAULT_PIPELINE)
        self.assertIn("RESEARCH", DEFAULT_PIPELINE)
        self.assertIn("HYBRID", DEFAULT_PIPELINE)

        # Check RESEARCH pipeline steps
        research_steps = DEFAULT_PIPELINE["RESEARCH"]
        self.assertIn(StepType.UNDERSTAND, research_steps)
        self.assertIn(StepType.PLAN, research_steps)
        self.assertIn(StepType.GATHER, research_steps)
        self.assertIn(StepType.VERIFY, research_steps)
        self.assertIn(StepType.SYNTHESIZE, research_steps)
        self.assertIn(StepType.FINALIZE, research_steps)

    def test_step_override(self):
        from agent.steps import UnderstandStep

        override_steps = [StepType.UNDERSTAND]
        self.ctx.steps_override = override_steps

        pipeline = Pipeline(self.ctx, self.controller)

        # Should only have the overridden steps
        self.assertEqual(len(pipeline.steps), 1)

    @patch("agent.pipeline._import_steps")
    def test_execute_pipeline_function(self, mock_import):
        result = execute_pipeline(self.ctx, self.controller)

        self.assertIsInstance(result, RunContext)
        mock_import.assert_called_once()


if __name__ == "__main__":
    unittest.main()
