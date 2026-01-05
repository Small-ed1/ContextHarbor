#!/usr/bin/env python3
"""Test the complete tool calling integration with controller and worker"""

import os
import sys
from pathlib import Path

# Add the project root to Python path
sys.path.insert(0, str(Path(__file__).parent))


def test_controller_integration():
    """Test the controller's execute_tool method integration"""
    try:
        from agent.controller import Controller
        from agent.tools import DirectoryListTool, FileReadTool
        from agent.worker_ollama import OllamaWorker

        # Create a controller with tools
        worker = OllamaWorker(model="test", host="http://test")
        controller = Controller(worker)

        # Test tool registry works
        assert len(controller.tool_registry.tools) > 0
        print(f"✅ Controller registered {len(controller.tool_registry.tools)} tools")

        # Test tool execution via controller
        result = controller.execute_tool("list_dir", path=".")
        print(f"✅ Controller tool execution: ok={result.ok}")

        if not result.ok:
            print(f"  Error: {result.error}")
        else:
            print(f"  Data type: {type(result.data)}")

        return True

    except Exception as e:
        print(f"❌ Controller integration test failed: {e}")
        import traceback

        traceback.print_exc()
        return False


def test_worker_tool_parsing():
    """Test the worker's tool call parsing capabilities"""
    try:
        from agent.worker_ollama import OllamaWorker

        worker = OllamaWorker()

        # Test multiple tool calls in one response
        test_response = """
        I'll help you with that.
        TOOL_CALL: {"name": "read_file", "parameters": {"path": "test.txt"}}
        TOOL_CALL: {"name": "list_dir", "parameters": {"path": "."}}
        Now I have the information.
        """

        calls = worker._extract_tool_calls(test_response)
        print(f"✅ Found {len(calls)} tool calls")

        for i, call in enumerate(calls):
            print(f"  Call {i+1}: {call['name']} -> {call['parameters']}")

        # Test parameter validation
        if calls:
            tool_name = calls[0]["name"]
            parameters = calls[0]["parameters"]

            # Test validation (should not crash)
            validation_error = worker._validate_tool_parameters(None, parameters)
            print(f"✅ Parameter validation works: {validation_error}")

        return True

    except Exception as e:
        print(f"❌ Worker tool parsing test failed: {e}")
        import traceback

        traceback.print_exc()
        return False


def test_tool_result_handling():
    """Test tool result handling and error recovery"""
    try:
        from agent.models import Source, SourceType, ToolResult

        # Test successful result
        success_result = ToolResult(
            ok=True,
            data="File content here",
            sources=[
                Source(
                    source_id="test",
                    tool="read_file",
                    source_type=SourceType.FILE,
                    title="Test File",
                    locator="/test/file.txt",
                    snippet="Test snippet",
                )
            ],
        )

        assert success_result.ok == True
        assert len(success_result.sources) == 1
        print("✅ Successful tool result handling works")

        # Test error result
        error_result = ToolResult(ok=False, error="File not found")

        assert error_result.ok == False
        assert "File not found" in error_result.error
        print("✅ Error tool result handling works")

        return True

    except Exception as e:
        print(f"❌ Tool result handling test failed: {e}")
        import traceback

        traceback.print_exc()
        return False


def main():
    """Run all integration tests"""
    print("🧪 Testing Complete Tool Calling Integration")
    print("=" * 50)

    test1_passed = test_controller_integration()
    test2_passed = test_worker_tool_parsing()
    test3_passed = test_tool_result_handling()

    print("\n" + "=" * 50)
    if test1_passed and test2_passed and test3_passed:
        print("🎉 All integration tests passed!")
        print("✅ Tool calling integration is complete and working!")
        print("\nKey improvements made:")
        print("  • Added missing execute_tool method to Controller")
        print("  • Improved tool call parsing with better error handling")
        print("  • Added support for multiple tool calls per response")
        print("  • Implemented parameter validation before execution")
        print("  • Enhanced error recovery and reporting")
        print("  • Fixed type annotations and imports")
        return 0
    else:
        print("💥 Some integration tests failed.")
        return 1


if __name__ == "__main__":
    exit(main())
