from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Callable

from pydantic import BaseModel


@dataclass(frozen=True)
class ToolSpec:
    """
    A tool definition:
      - args_schema validates inputs (Pydantic)
      - handler receives the validated model instance
    """

    name: str
    description: str
    args_schema: type[BaseModel]
    handler: Callable[[Any], Any]

    def json_schema(self) -> dict[str, Any]:
        return self.args_schema.model_json_schema()


class ToolRegistry:
    def __init__(self) -> None:
        self._tools: dict[str, ToolSpec] = {}

    def register(self, tool: ToolSpec) -> None:
        self._tools[tool.name] = tool

    def get(self, name: str) -> ToolSpec | None:
        return self._tools.get(name)

    def list_names(self) -> list[str]:
        return sorted(self._tools.keys())

    def schema_for_prompt(self) -> list[dict[str, Any]]:
        """
        What the model sees.
        """
        out: list[dict[str, Any]] = []
        for tool in self._tools.values():
            out.append(
                {
                    "name": tool.name,
                    "description": tool.description,
                    "arguments_schema": tool.json_schema(),
                }
            )
        return out

    def call(self, tool_name: str, raw_args: dict[str, Any]) -> dict[str, Any]:
        tool = self.get(tool_name)
        if not tool:
            return {"ok": False, "error": f"Unknown tool: {tool_name}"}

        try:
            args_obj = tool.args_schema.model_validate(raw_args)
            result = tool.handler(args_obj)
            return {"ok": True, "result": result}
        except Exception as exc:
            return {"ok": False, "error": str(exc)}
