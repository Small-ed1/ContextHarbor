#!/usr/bin/env python3
"""Simple test to verify tool calling integration without external dependencies"""

import os
import sys
from pathlib import Path

# Add the project root to Python path
sys.path.insert(0, str(Path(__file__).parent))


def test_imports():
    """Test that all key modules can be imported"""
    try:
        # Test basic imports
        from agent.models import Source, SourceType, ToolResult
        from agent.tools.base import BaseTool

        print("✅ Basic imports successful")

        # Test tool result creation
        result = ToolResult(ok=True, data="test")
        assert result.ok == True
        assert result.data == "test"
        print("✅ ToolResult creation works")

        # Test source creation
        source = Source(
            source_id="test",
            tool="test_tool",
            source_type=SourceType.FILE,
            title="Test File",
            locator="/test/path",
            snippet="Test content",
        )
        assert source.source_id == "test"
        print("✅ Source creation works")

        return True

    except Exception as e:
        print(f"❌ Import test failed: {e}")
        import traceback

        traceback.print_exc()
        return False


def test_tool_schema():
    """Test tool schema generation"""
    try:
        from agent.models import ToolResult
        from agent.tools.base import BaseTool

        class TestTool(BaseTool):
            def __init__(self):
                super().__init__("test_tool", "A test tool")

            def execute(self, **kwargs) -> ToolResult:
                return ToolResult(ok=True, data=f"Test executed with {kwargs}")

            def get_schema(self):
                schema = super().get_schema()
                schema["parameters"]["properties"] = {
                    "test_param": {"type": "string", "description": "A test parameter"}
                }
                schema["parameters"]["required"] = ["test_param"]
                return schema

        tool = TestTool()
        schema = tool.get_schema()

        assert schema["name"] == "test_tool"
        assert schema["description"] == "A test tool"
        assert "test_param" in schema["parameters"]["properties"]
        assert "test_param" in schema["parameters"]["required"]

        print("✅ Tool schema generation works")
        return True

    except Exception as e:
        print(f"❌ Tool schema test failed: {e}")
        import traceback

        traceback.print_exc()
        return False


def main():
    """Run all tests"""
    print("🧪 Testing Tool Calling Components")
    print("=" * 40)

    test1_passed = test_imports()
    test2_passed = test_tool_schema()

    print("\n" + "=" * 40)
    if test1_passed and test2_passed:
        print(
            "🎉 Component tests passed! Tool calling integration components are working."
        )
        return 0
    else:
        print("💥 Some component tests failed.")
        return 1


if __name__ == "__main__":
    exit(main())
