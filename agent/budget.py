from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict


class BudgetExceeded(RuntimeError):
    pass


@dataclass
class BudgetManager:
    limits: Dict[str, int]
    max_total: int | None = None
    used: Dict[str, int] = field(default_factory=dict)

    def remaining(self, tool_name: str) -> int:
        lim = self.limits.get(tool_name, 0)
        return max(0, lim - self.used.get(tool_name, 0))

    def total_used(self) -> int:
        return sum(self.used.values())

    def consume(self, tool_name: str, n: int = 1) -> None:
        if n <= 0:
            return
        lim = self.limits.get(tool_name, 0)
        cur = self.used.get(tool_name, 0)
        remaining = lim - cur
        if n > remaining:
            raise BudgetExceeded(
                f"Tool budget exceeded for '{tool_name}': attempted to consume {n}, "
                f"but only {remaining} remaining (budget: {lim}, used: {cur})"
            )
        self.used[tool_name] = cur + n
        if self.max_total is not None and self.total_used() > self.max_total:
            raise BudgetExceeded(
                f"Total tool budget exceeded: {self.total_used()}/{self.max_total} calls"
            )
