import unittest

from agent.models import ToolResult
from agent.registry import ToolRegistry
from agent.tools import BaseTool


class MockTool(BaseTool):
    """Mock tool for testing"""

    def __init__(self, name="mock_tool"):
        super().__init__(name, "Mock tool for testing")

    def execute(self, **kwargs) -> ToolResult:
        return ToolResult(ok=True, data="mock result")


class TestToolRegistry(unittest.TestCase):
    """Test tool registry management"""

    def test_register_tool(self):
        """Test registering a new tool"""
        registry = ToolRegistry()
        tool = MockTool()
        registry.register("mock_tool", tool)

        self.assertIn("mock_tool", registry.tools)
        self.assertEqual(registry.tools["mock_tool"], tool)

    def test_get_tool(self):
        """Test retrieving a registered tool"""
        registry = ToolRegistry()
        tool = MockTool()
        registry.register("mock_tool", tool)

        retrieved = registry.get("mock_tool")
        self.assertEqual(retrieved, tool)
        self.assertEqual(retrieved.name, "mock_tool")

    def test_get_nonexistent_tool(self):
        """Test retrieving a non-existent tool raises KeyError"""
        registry = ToolRegistry()
        registry.register("tool1", MockTool("tool1"))

        with self.assertRaises(KeyError) as cm:
            registry.get("nonexistent_tool")
        self.assertIn("not registered", str(cm.exception))

    def test_list_tools(self):
        """Test listing all registered tools"""
        registry = ToolRegistry()
        registry.register("tool1", MockTool("tool1"))
        registry.register("tool2", MockTool("tool2"))
        registry.register("tool3", MockTool("tool3"))

        tool_names = list(registry.tools.keys())
        self.assertEqual(len(tool_names), 3)
        self.assertIn("tool1", tool_names)
        self.assertIn("tool2", tool_names)
        self.assertIn("tool3", tool_names)

    def test_overwrite_tool(self):
        """Test overwriting an existing tool registration"""
        registry = ToolRegistry()
        tool1 = MockTool("original")
        tool2 = MockTool("new")
        registry.register("tool", tool1)

        self.assertEqual(registry.get("tool").name, "original")

        registry.register("tool", tool2)
        self.assertEqual(registry.get("tool").name, "new")

    def test_tool_count(self):
        """Test counting registered tools"""
        registry = ToolRegistry()

        self.assertEqual(len(registry.tools), 0)

        for i in range(5):
            registry.register(f"tool_{i}", MockTool(f"tool_{i}"))

        self.assertEqual(len(registry.tools), 5)

    def test_has_tool(self):
        """Test checking if a tool is registered"""
        registry = ToolRegistry()
        registry.register("tool1", MockTool("tool1"))

        self.assertIn("tool1", registry.tools)
        self.assertNotIn("tool2", registry.tools)

    def test_multiple_registries(self):
        """Test that multiple registries are independent"""
        reg1 = ToolRegistry()
        reg2 = ToolRegistry()

        tool1 = MockTool("tool1")
        tool2 = MockTool("tool2")

        reg1.register("tool", tool1)
        reg2.register("tool", tool2)

        self.assertEqual(reg1.get("tool"), tool1)
        self.assertEqual(reg2.get("tool"), tool2)
        self.assertNotEqual(reg1.get("tool"), reg2.get("tool"))


if __name__ == "__main__":
    unittest.main()
