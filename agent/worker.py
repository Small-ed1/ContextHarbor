from __future__ import annotations

import re
from typing import Dict, List

from .models import Mode

_MODE_PREFIX = re.compile(r"^\s*mode=[A-Z]+\s+", re.I)


def _clean_objective(s: str) -> str:
    s = _MODE_PREFIX.sub("", s).strip()
    return s


class DummyWorker:
    def __call__(self, ctx):
        return self.run(ctx)

    def run(self, ctx) -> str:
        objective = _clean_objective(ctx.objective)
        mode = ctx.decision.mode

        sys = "You are a helpful assistant. Answer clearly and concisely."

        msgs = [
            {"role": "system", "content": sys},
            {"role": "user", "content": objective},
        ]

        return f"[DUMMY - {mode.value} mode] Would process: {objective[:100]}..."
