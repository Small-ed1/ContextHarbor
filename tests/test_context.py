import unittest

from agent.context import Message, RunContext
from agent.models import (Mode, RouteDecision, Source, SourceType, StepResult,
                          StepType, StopConditions, ToolBudget, ToolCall)


class TestRunContext(unittest.TestCase):
    """Test RunContext state management and citation tracking"""

    def _create_decision(self, mode=Mode.WRITE, confidence=0.8):
        """Helper to create valid RouteDecision"""
        return RouteDecision(
            mode=mode,
            confidence=confidence,
            signals=[],
            tool_budget=ToolBudget(),
            stop_conditions=StopConditions(),
        )

    def test_basic_creation(self):
        """Test basic RunContext creation"""
        decision = self._create_decision(Mode.WRITE, 0.8)
        decision.signals = ["file creation"]
        ctx = RunContext(objective="Create a file", decision=decision)
        self.assertEqual(ctx.objective, "Create a file")
        self.assertEqual(ctx.decision.mode, Mode.WRITE)
        self.assertEqual(ctx.project, "default")

    def test_message_management(self):
        """Test adding and managing messages"""
        decision = self._create_decision()
        ctx = RunContext(objective="test", decision=decision)
        self.assertEqual(len(ctx.messages), 0)

        msg1 = Message(role="user", content="Hello")
        msg2 = Message(role="assistant", content="Hi there")
        ctx.messages.extend([msg1, msg2])

        self.assertEqual(len(ctx.messages), 2)
        self.assertEqual(ctx.messages[0].role, "user")
        self.assertEqual(ctx.messages[1].content, "Hi there")

    def test_source_addition(self):
        """Test adding sources and getting citation indices"""
        decision = self._create_decision(Mode.RESEARCH, 0.9)
        ctx = RunContext(objective="Research test", decision=decision)

        source1 = Source(
            source_id="src1",
            tool="web_search",
            source_type=SourceType.WEB,
            title="Test Source 1",
            locator="http://example.com/1",
            snippet="Content 1",
            confidence=0.8,
        )
        source2 = Source(
            source_id="src2",
            tool="kiwix_query",
            source_type=SourceType.KIWIX,
            title="Test Source 2",
            locator="http://example.com/2",
            snippet="Content 2",
            confidence=0.9,
        )

        idx1 = ctx.add_source(source1)
        idx2 = ctx.add_source(source2)

        self.assertEqual(idx1, 1)
        self.assertEqual(idx2, 2)
        self.assertEqual(len(ctx.sources), 2)

        duplicate_idx = ctx.add_source(source1)
        self.assertEqual(duplicate_idx, 1)
        self.assertEqual(len(ctx.sources), 2)

    def test_citation_retrieval(self):
        """Test retrieving citations by source ID and index"""
        decision = self._create_decision(Mode.RESEARCH, 0.9)
        ctx = RunContext(objective="test", decision=decision)

        source = Source(
            source_id="test_source",
            tool="web_search",
            source_type=SourceType.WEB,
            title="Test",
            locator="http://test.com",
            snippet="Test content",
            confidence=0.7,
        )

        idx = ctx.add_source(source)
        self.assertEqual(idx, 1)

        retrieved_idx = ctx.get_citation("test_source")
        self.assertEqual(retrieved_idx, 1)

        missing_idx = ctx.get_citation("nonexistent")
        self.assertIsNone(missing_idx)

        retrieved_source = ctx.get_source_by_citation(1)
        self.assertIsNotNone(retrieved_source)
        self.assertEqual(retrieved_source.title, "Test")

    def test_tool_usage_tracking(self):
        """Test tracking tool usage and budget"""
        tool_budget = ToolBudget(limits={"read_file": 5, "write_file": 3})
        stop_conditions = StopConditions(max_tool_calls_total=10)
        decision = RouteDecision(
            mode=Mode.WRITE,
            confidence=0.7,
            tool_budget=tool_budget,
            stop_conditions=stop_conditions,
        )
        ctx = RunContext(objective="test", decision=decision)

        self.assertTrue(ctx.can_use_tool("read_file"))

        ctx.record_tool_use("read_file", "step1")
        ctx.record_tool_use("read_file", "step1")
        ctx.record_tool_use("write_file", "step2")

        self.assertEqual(ctx.global_budget_used, 3)
        self.assertEqual(ctx.per_tool_used["read_file"], 2)
        self.assertEqual(ctx.per_tool_used["write_file"], 1)

    def test_tool_budget_enforcement(self):
        """Test that tool budgets are enforced"""
        tool_budget = ToolBudget(limits={"test_tool": 2})
        decision = RouteDecision(
            mode=Mode.WRITE,
            confidence=0.7,
            tool_budget=tool_budget,
            stop_conditions=StopConditions(),
        )
        ctx = RunContext(objective="test", decision=decision)

        self.assertTrue(ctx.can_use_tool("test_tool"))
        ctx.record_tool_use("test_tool", "step1")
        ctx.record_tool_use("test_tool", "step1")
        self.assertFalse(ctx.can_use_tool("test_tool"))

    def test_total_budget_enforcement(self):
        """Test that total tool call budget is enforced"""
        stop_conditions = StopConditions(max_tool_calls_total=3)
        decision = RouteDecision(
            mode=Mode.WRITE,
            confidence=0.7,
            tool_budget=ToolBudget(),
            stop_conditions=stop_conditions,
        )
        ctx = RunContext(objective="test", decision=decision)

        self.assertTrue(ctx.can_use_tool("any_tool"))
        ctx.record_tool_use("tool1", "step1")
        ctx.record_tool_use("tool2", "step2")
        ctx.record_tool_use("tool3", "step3")
        self.assertFalse(ctx.can_use_tool("any_tool"))

    def test_step_budget_enforcement(self):
        """Test step-level budget enforcement"""
        decision = self._create_decision()
        ctx = RunContext(objective="test", decision=decision)
        ctx.current_step = "gather"

        call1 = ToolCall(
            name="test_tool", parameters={}, step_name="gather", result=None
        )
        call2 = ToolCall(
            name="test_tool", parameters={}, step_name="gather", result=None
        )

        ctx.tool_calls.extend([call1, call2])

        self.assertTrue(ctx.can_use_tool("new_tool", step_budget=3))
        call3 = ToolCall(
            name="new_tool", parameters={}, step_name="gather", result=None
        )
        ctx.tool_calls.append(call3)
        self.assertFalse(ctx.can_use_tool("another_tool", step_budget=3))

    def test_step_result_recording(self):
        """Test recording step results"""
        decision = self._create_decision()
        ctx = RunContext(objective="test", decision=decision)

        step_result = StepResult(
            step_name="test_step",
            step_type=StepType.GATHER,
            ok=True,
            notes="Test notes",
            tool_calls=[],
            sources_added=[],
        )

        ctx.add_step_result(step_result)

        self.assertEqual(len(ctx.step_results), 1)
        self.assertEqual(len(ctx.step_history), 1)
        self.assertEqual(ctx.step_results[0].step_name, "test_step")

        history_entry = ctx.step_history[0]
        self.assertEqual(history_entry["step_name"], "test_step")
        self.assertEqual(history_entry["ok"], True)
        self.assertIn("timestamp", history_entry)

    def test_extras_dict(self):
        """Test extras dictionary for custom data"""
        decision = self._create_decision()
        ctx = RunContext(objective="test", decision=decision)

        ctx.extras["custom_key"] = "custom_value"
        ctx.extras["metadata"] = {"key": "value"}

        self.assertEqual(ctx.extras["custom_key"], "custom_value")
        self.assertEqual(ctx.extras["metadata"]["key"], "value")

    def test_retry_tracking(self):
        """Test attempt and max_retries tracking"""
        decision = self._create_decision()
        ctx = RunContext(objective="test", decision=decision)

        self.assertEqual(ctx.attempt, 0)
        self.assertEqual(ctx.max_retries, 2)

        ctx.attempt = 1
        self.assertEqual(ctx.attempt, 1)
        self.assertTrue(ctx.attempt <= ctx.max_retries)

    def test_artifacts_tracking(self):
        """Test tracking artifacts"""
        decision = self._create_decision()
        ctx = RunContext(objective="test", decision=decision)

        self.assertEqual(len(ctx.artifacts), 0)

        ctx.artifacts.append({"type": "file", "path": "/tmp/test.txt"})
        ctx.artifacts.append({"type": "chart", "data": "..."})

        self.assertEqual(len(ctx.artifacts), 2)
        self.assertEqual(ctx.artifacts[0]["type"], "file")

    def test_final_answer_and_verification(self):
        """Test final answer and verification status"""
        decision = self._create_decision(Mode.RESEARCH)
        ctx = RunContext(objective="test", decision=decision)

        self.assertEqual(ctx.final_answer, "")
        self.assertFalse(ctx.verified)

        ctx.final_answer = "The answer is 42"
        ctx.verified = True

        self.assertEqual(ctx.final_answer, "The answer is 42")
        self.assertTrue(ctx.verified)


if __name__ == "__main__":
    unittest.main()
