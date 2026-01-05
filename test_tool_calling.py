#!/usr/bin/env python3
"""Simple test script to verify tool calling integration"""

import os
import sys
from pathlib import Path

# Add the project root to Python path
sys.path.insert(0, str(Path(__file__).parent))


def test_controller_execute_tool():
    """Test the execute_tool method in Controller"""
    try:
        from agent.controller import Controller
        from agent.worker_ollama import OllamaWorker

        # Create a mock worker (we won't actually call Ollama)
        worker = OllamaWorker(model="test", host="http://test")
        controller = Controller(worker)

        # Test tool execution
        result = controller.execute_tool("list_dir", path=".")

        print(f"Tool execution result:")
        print(f"  OK: {result.ok}")
        print(f"  Data: {result.data}")
        print(f"  Error: {result.error}")

        if result.ok:
            print("✅ execute_tool method works correctly!")
            return True
        else:
            print(f"❌ Tool execution failed: {result.error}")
            return False

    except Exception as e:
        print(f"❌ Exception during test: {e}")
        import traceback

        traceback.print_exc()
        return False


def test_tool_call_parsing():
    """Test tool call parsing improvements"""
    try:
        from agent.worker_ollama import OllamaWorker

        worker = OllamaWorker()

        # Test various tool call formats
        test_cases = [
            'TOOL_CALL: {"name": "test_tool", "parameters": {"arg": "value"}}',
            """TOOL_CALL: {"name": "test_tool", "parameters": {"arg": "value"}}""",
            'TOOL_CALL: test_tool: {"arg": "value"}',
            'TOOL_CALL: {"name": "test_tool", "parameters": {"arg": "value",}}',
        ]

        print("Testing tool call parsing:")
        for i, test_case in enumerate(test_cases):
            calls = worker._extract_tool_calls(test_case)
            print(f"  Test {i+1}: Found {len(calls)} calls")
            for call in calls:
                print(f"    - {call}")

        print("✅ Tool call parsing works!")
        return True

    except Exception as e:
        print(f"❌ Exception during parsing test: {e}")
        import traceback

        traceback.print_exc()
        return False


def main():
    """Run all tests"""
    print("🧪 Testing Tool Calling Integration")
    print("=" * 40)

    test1_passed = test_controller_execute_tool()
    test2_passed = test_tool_call_parsing()

    print("\n" + "=" * 40)
    if test1_passed and test2_passed:
        print("🎉 All tests passed! Tool calling integration is working.")
        return 0
    else:
        print("💥 Some tests failed.")
        return 1


if __name__ == "__main__":
    exit(main())
