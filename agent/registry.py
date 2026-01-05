from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict


@dataclass
class ToolRegistry:
    tools: Dict[str, Any] = field(default_factory=dict)

    def register(self, name: str, fn: Any) -> None:
        self.tools[name] = fn

    def get(self, name: str) -> Any:
        if name not in self.tools:
            raise KeyError(f"Tool not registered: {name}")
        return self.tools[name]
