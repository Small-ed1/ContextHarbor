import unittest
from agent.intelligent_tools import IntelligentTools
from agent.models import Mode
from agent.tools import BaseTool


class MockTool(BaseTool):
    def __init__(self, name="mock"):
        super().__init__(name, "Mock tool")

    def execute(self, **kwargs):
        pass


class TestIntelligentTools(unittest.TestCase):
    """Test intelligent tool selection system"""

    def setUp(self):
        self.intelligent = IntelligentTools()

    def test_get_recommended_tools_write_mode(self):
        """Test tool recommendations for WRITE mode"""
        tools = [MockTool("write_file"), MockTool("read_file")]
        result = self.intelligent.get_recommended_tools(
            "Create a new file",
            Mode.WRITE,
            available_tools=tools
        )
        self.assertIsInstance(result, list)
        self.assertIn("write_file", result)

    def test_get_recommended_tools_research_mode(self):
        """Test tool recommendations for RESEARCH mode"""
        tools = [MockTool("web_search"), MockTool("read_file")]
        result = self.intelligent.get_recommended_tools(
            "Search for information online",
            Mode.RESEARCH,
            available_tools=tools
        )
        self.assertIn("web_search", result)

    def test_keyword_matching(self):
        """Test keyword-based tool matching"""
        tools = [MockTool("grep"), MockTool("find"), MockTool("search")]
        result = self.intelligent.get_recommended_tools(
            "Find all occurrences of error",
            Mode.RESEARCH,
            available_tools=tools
        )
        self.assertTrue(any("find" in t or "grep" in t or "search" in t for t in result))

    def test_empty_objective(self):
        """Test handling empty objective"""
        result = self.intelligent.get_recommended_tools(
            "",
            Mode.WRITE,
            available_tools=[]
        )
        self.assertIsInstance(result, list)

    def test_mode_context_influences_recommendations(self):
        """Test that mode influences tool selection"""
        tools = [MockTool("web_search"), MockTool("write_file")]
        write_result = self.intelligent.get_recommended_tools(
            "test",
            Mode.WRITE,
            available_tools=tools
        )
        research_result = self.intelligent.get_recommended_tools(
            "test",
            Mode.RESEARCH,
            available_tools=tools
        )
        self.assertNotEqual(write_result, research_result)

    def test_no_tools_available(self):
        """Test handling when no tools are available"""
        result = self.intelligent.get_recommended_tools(
            "test query",
            Mode.WRITE,
            available_tools=[]
        )
        self.assertEqual(len(result), 0)


if __name__ == "__main__":
    unittest.main()
