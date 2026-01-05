from __future__ import annotations

import json
from functools import lru_cache
from pathlib import Path
from typing import Any, Dict, List, Union

from .budget import BudgetExceeded
from .context import Message, RunContext
from .models import ToolResult
from .pipeline import execute_pipeline
from .registry import ToolRegistry
from .router import route
from .tools import get_all_tools
from .worker_ollama import OllamaWorker

_TOOLS = None


def _get_tools():
    global _TOOLS
    if _TOOLS is None:
        _TOOLS = get_all_tools()
    return _TOOLS


@lru_cache(maxsize=8)
def _load_permissions_cached():
    config_path = Path("router.json")
    if config_path.exists():
        try:
            with open(config_path) as f:
                config = json.load(f)
                return config.get("permissions", {})
        except Exception:
            pass
    return {}


class Controller:
    def __init__(self, worker: Any):
        self.worker = worker
        self.tool_registry = ToolRegistry()
        self._permissions: Dict[str, Any] | None = None

        for tool in _get_tools():
            self.tool_registry.register(tool.name, tool)

    def _get_permissions(self) -> Dict[str, Any]:
        if self._permissions is None:
            self._permissions = _load_permissions_cached()
        return self._permissions or {}

    def execute_tool(self, tool_name: str, **kwargs) -> ToolResult:
        """Execute a tool by name with given parameters"""
        try:
            # Check permissions
            permissions = self._get_permissions()
            if tool_name in permissions.get("disabled_tools", []):
                return ToolResult(
                    ok=False, error=f"Tool '{tool_name}' is disabled by configuration"
                )

            # Get tool from registry
            tool = self.tool_registry.get(tool_name)

            # Execute tool
            result = tool.execute(**kwargs)

            # Validate result type
            if not isinstance(result, ToolResult):
                return ToolResult(
                    ok=False, error=f"Tool '{tool_name}' returned invalid result type"
                )

            return result

        except KeyError:
            return ToolResult(
                ok=False,
                error=f"Tool '{tool_name}' not found. Available tools: {list(self.tool_registry.tools.keys())}",
            )
        except Exception as e:
            return ToolResult(
                ok=False, error=f"Error executing tool '{tool_name}': {str(e)}"
            )

    def run(self, objective: str, project: str = "default") -> str:
        """Main entry point for running an objective through the agent system"""
        try:
            # Route the objective to determine mode and tools
            decision = route(objective)

            # Create run context
            context = RunContext(
                objective=objective,
                decision=decision,
                project=project,
                messages=[Message(role="user", content=objective)],
            )

            # Execute pipeline
            result_ctx = execute_pipeline(context, self)

            # Extract result from context
            if hasattr(result_ctx, "final_answer") and result_ctx.final_answer:
                return result_ctx.final_answer
            else:
                return "Pipeline completed successfully"

        except BudgetExceeded as e:
            return f"Error: Budget exceeded - {e}"
        except Exception as e:
            return f"Error: {str(e)}"
