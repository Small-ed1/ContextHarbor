import unittest
from unittest.mock import Mock

from agent.context import RunContext
from agent.models import (Mode, RouteDecision, StepType, StopConditions,
                          ToolBudget)
from agent.steps import (AnswerStep, DraftStep, ExecuteStep, FinalizeStep,
                         GatherStep, OutlineStep, PlanStep, SynthesizeStep,
                         UnderstandStep, VerifyStep)


class TestStepClasses(unittest.TestCase):
    def setUp(self):
        self.decision = RouteDecision(
            mode=Mode.RESEARCH,
            confidence=0.8,
            tool_budget=ToolBudget(),
            stop_conditions=StopConditions(min_sources=3),
        )
        self.ctx = RunContext(
            objective="Find information about climate change", decision=self.decision
        )
        self.controller = Mock()

    def test_understand_step(self):
        step = UnderstandStep(self.ctx, self.controller)
        result = step.execute()

        self.assertTrue(result.ok)
        self.assertEqual(result.step_name, "understand")
        self.assertEqual(result.step_type, StepType.UNDERSTAND)
        self.assertIn("User wants:", result.notes)

    def test_plan_step(self):
        step = PlanStep(self.ctx, self.controller)
        result = step.execute()

        self.assertTrue(result.ok)
        self.assertEqual(result.step_name, "plan")
        self.assertIn("Plan for RESEARCH mode:", result.notes)
        self.assertIn("kiwix_query", result.notes)

    def test_gather_step(self):
        # Mock the tool usage
        mock_result = Mock()
        mock_result.ok = True
        mock_result.sources_added = ["source1", "source2"]

        step = GatherStep(self.ctx, self.controller)
        step._use_tool = Mock(return_value=mock_result)

        result = step.execute()

        self.assertTrue(result.ok)
        self.assertEqual(result.step_name, "gather")
        self.assertEqual(result.step_type, StepType.GATHER)

    def test_verify_step(self):
        # Add some sources and tool calls
        from agent.models import Source, SourceType

        self.ctx.sources = [
            Source("id1", "test", SourceType.WEB, "Title1", "url1", "snippet1"),
            Source("id2", "test", SourceType.WEB, "Title2", "url2", "snippet2"),
            Source("id3", "test", SourceType.WEB, "Title3", "url3", "snippet3"),
        ]
        # Add a tool call
        from agent.models import ToolCall

        mock_result = Mock()
        mock_result.ok = True
        self.ctx.tool_calls = [
            ToolCall(
                name="kiwix_query", parameters={"query": "test"}, result=mock_result
            )
        ]

        step = VerifyStep(self.ctx, self.controller)
        result = step.execute()

        self.assertTrue(result.ok)
        self.assertEqual(result.step_name, "verify")
        self.assertIn("Verification passed", result.notes)

    def test_verify_step_insufficient_sources(self):
        # No sources added
        step = VerifyStep(self.ctx, self.controller)
        result = step.execute()

        self.assertFalse(result.ok)
        self.assertIn("Only 0 sources", result.notes)

    def test_synthesize_step(self):
        # Add some sources
        from agent.models import Source, SourceType

        self.ctx.sources = [
            Source("id1", "test", SourceType.WEB, "Title", "url", "snippet")
        ]

        step = SynthesizeStep(self.ctx, self.controller)
        result = step.execute()

        self.assertTrue(result.ok)
        self.assertEqual(result.step_name, "synthesize")
        self.assertIsNotNone(self.ctx.final_answer)
        self.assertIn("Based on 1 source(s):", self.ctx.final_answer)

    def test_finalize_step(self):
        # Set up final answer
        self.ctx.final_answer = "Test answer"

        step = FinalizeStep(self.ctx, self.controller)
        result = step.execute()

        self.assertTrue(result.ok)
        self.assertEqual(result.step_name, "finalize")
        self.assertTrue(self.ctx.verified)

    def test_outline_step(self):
        step = OutlineStep(self.ctx, self.controller)
        result = step.execute()

        self.assertTrue(result.ok)
        self.assertEqual(result.step_name, "outline")
        self.assertIn("Outline for:", result.notes)
        self.assertIn("Introduction", result.notes)

    def test_draft_step(self):
        step = DraftStep(self.ctx, self.controller)
        result = step.execute()

        self.assertTrue(result.ok)
        self.assertEqual(result.step_name, "draft")
        self.assertIsNotNone(self.ctx.final_answer)
        self.assertIn("Draft of:", self.ctx.final_answer)

    def test_answer_step(self):
        step = AnswerStep(self.ctx, self.controller)
        result = step.execute()

        self.assertTrue(result.ok)
        self.assertEqual(result.step_name, "answer")
        self.assertIsNotNone(self.ctx.final_answer)
        self.assertIn("Answer:", self.ctx.final_answer)

    def test_execute_step(self):
        step = ExecuteStep(self.ctx, self.controller)
        result = step.execute()

        self.assertTrue(result.ok)
        self.assertEqual(result.step_name, "execute")
        self.assertIn("Execution step", result.notes)


class TestStepProperties(unittest.TestCase):
    def test_step_properties(self):
        self.assertEqual(UnderstandStep.name, "understand")
        self.assertEqual(UnderstandStep.step_type, StepType.UNDERSTAND)
        self.assertFalse(UnderstandStep.critical)

        self.assertEqual(GatherStep.name, "gather")
        self.assertEqual(GatherStep.step_type, StepType.GATHER)
        self.assertTrue(GatherStep.critical)

        self.assertEqual(FinalizeStep.name, "finalize")
        self.assertEqual(FinalizeStep.step_type, StepType.FINALIZE)
        self.assertTrue(FinalizeStep.critical)


if __name__ == "__main__":
    unittest.main()
