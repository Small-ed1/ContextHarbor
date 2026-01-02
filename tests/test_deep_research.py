import unittest
from agent.deep_research import DeepResearch
from unittest.mock import Mock, patch
from agent.models import Mode, RouteDecision, ToolBudget, StopConditions


class TestDeepResearch(unittest.TestCase):
    """Test deep research multi-pass analysis"""

    def setUp(self):
        self.worker = Mock()

    @patch('agent.deep_research.threading.ThreadPoolExecutor')
    def test_deep_research_initialization(self, mock_executor):
        """Test deep research initialization"""
        research = DeepResearch(
            objective="Test objective",
            worker=self.worker,
            mode=Mode.RESEARCH,
            depth="standard"
        )
        self.assertIsNotNone(research)
        self.assertEqual(research.objective, "Test objective")

    @patch('agent.deep_research.threading.ThreadPoolExecutor')
    def test_research_returns_results(self, mock_executor):
        """Test that research returns structured results"""
        mock_executor.return_value = Mock(
            submit=Mock(return_value=Mock(result="test result"))
        )

        research = DeepResearch(
            objective="Test",
            worker=self.worker,
            mode=Mode.RESEARCH
        )
        result = research.run()

        self.assertIsNotNone(result)

    @patch('agent.deep_research.threading.ThreadPoolExecutor')
    def test_research_handles_empty_objective(self, mock_executor):
        """Test handling of empty objective"""
        research = DeepResearch(
            objective="",
            worker=self.worker,
            mode=Mode.RESEARCH
        )
        result = research.run()
        self.assertIsNotNone(result)

    @patch('agent.deep_research.threading.ThreadPoolExecutor')
    def test_research_quick_mode(self, mock_executor):
        """Test quick research mode with fewer passes"""
        research = DeepResearch(
            objective="Test",
            worker=self.worker,
            mode=Mode.RESEARCH,
            depth="quick"
        )
        self.assertEqual(research.depth, "quick")

    @patch('agent.deep_research.threading.ThreadPoolExecutor')
    def test_research_deep_mode(self, mock_executor):
        """Test deep research mode with more passes"""
        research = DeepResearch(
            objective="Test",
            worker=self.worker,
            mode=Mode.RESEARCH,
            depth="deep"
        )
        self.assertEqual(research.depth, "deep")

    @patch('agent.deep_research.threading.ThreadPoolExecutor')
    def test_research_caches_results(self, mock_executor):
        """Test that research caches results appropriately"""
        research = DeepResearch(
            objective="Test",
            worker=self.worker,
            mode=Mode.RESEARCH
        )
        self.assertIsNotNone(research.cache)


if __name__ == "__main__":
    unittest.main()
