import unittest

from agent.models import ToolResult
from agent.tools import BaseTool
from agent.worker_ollama import OllamaWorker


class MockTool(BaseTool):
    def __init__(self):
        super().__init__("mock_tool", "Mock tool for testing")

    def execute(self, **kwargs) -> ToolResult:
        return ToolResult(ok=True, data="mocked")


class TestOllamaWorker(unittest.TestCase):
    """Test OllamaWorker functionality"""

    def test_worker_initialization(self):
        """Test worker initializes with correct defaults"""
        worker = OllamaWorker()
        self.assertIsNotNone(worker.model)
        self.assertIsNotNone(worker.host)
        self.assertIsInstance(worker.tools, list)
        self.assertTrue(worker.streaming)

    def test_worker_initialization_with_custom_params(self):
        """Test worker initialization with custom parameters"""
        worker = OllamaWorker(
            model="custom_model",
            host="http://custom-host:11434",
            streaming=False,
            temperature=0.5,
        )
        self.assertEqual(worker.model, "custom_model")
        self.assertEqual(worker.host, "http://custom-host:11434")
        self.assertFalse(worker.streaming)
        self.assertEqual(worker.temperature, 0.5)

    def test_tool_lookup_population(self):
        """Test that tools are populated in lookup dict"""
        tool = MockTool()
        worker = OllamaWorker(tools=[tool])
        self.assertIn("mock_tool", worker._tool_lookup)

    def test_clean_json_string_trailing_comma(self):
        """Test JSON cleaning removes trailing commas"""
        worker = OllamaWorker()
        cleaned = worker._clean_json_string('{"key": "value",}')
        self.assertEqual(cleaned, '{"key": "value"}')
        cleaned = worker._clean_json_string('{"key": ["a",]}')
        self.assertEqual(cleaned, '{"key": ["a"]}')

    def test_clean_json_string_quotes(self):
        """Test JSON cleaning fixes single quotes"""
        worker = OllamaWorker()
        cleaned = worker._clean_json_string("{'key': 'value'}")
        self.assertEqual(cleaned, '{"key": "value"}')

    def test_clean_json_string_code_blocks(self):
        """Test JSON cleaning removes code block markers"""
        worker = OllamaWorker()
        cleaned = worker._clean_json_string('```json\n{"key": "value"}\n```')
        self.assertIn('{"key": "value"}', cleaned)

    def test_extract_single_tool_call_alt_format(self):
        """Test extracting tool call in alternative format"""
        worker = OllamaWorker()
        response = 'TOOL_CALL: read_file: {"path": "test.py"}'
        calls = worker._extract_tool_calls(response)
        self.assertEqual(len(calls), 1)
        self.assertEqual(calls[0]["name"], "read_file")

    def test_extract_multiple_tool_calls(self):
        """Test extracting multiple tool calls in alt format"""
        worker = OllamaWorker()
        response = """TOOL_CALL: read_file: {"path": "a.py"}
TOOL_CALL: write_file: {"path": "b.py", "content": "test"}
"""
        calls = worker._extract_tool_calls(response)
        self.assertEqual(len(calls), 2)
        self.assertEqual(calls[0]["name"], "read_file")
        self.assertEqual(calls[1]["name"], "write_file")

    def test_extract_no_tool_calls(self):
        """Test extracting tool calls from text without any"""
        worker = OllamaWorker()
        response = "This is just a regular response without tool calls"
        calls = worker._extract_tool_calls(response)
        self.assertEqual(len(calls), 0)

    def test_extract_tool_call_with_invalid_json(self):
        """Test handling invalid JSON gracefully"""
        worker = OllamaWorker()
        response = "TOOL_CALL: {invalid json}"
        calls = worker._extract_tool_calls(response)
        self.assertEqual(len(calls), 0)

    def test_extract_tool_call_with_malformed_params(self):
        """Test extracting tool calls with malformed parameters"""
        worker = OllamaWorker()
        response = 'TOOL_CALL: {"name": "test_tool"}'
        calls = worker._extract_tool_calls(response)
        self.assertEqual(len(calls), 1)
        self.assertEqual(calls[0]["name"], "test_tool")
        self.assertIn("parameters", calls[0])


if __name__ == "__main__":
    unittest.main()
