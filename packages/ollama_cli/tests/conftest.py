from __future__ import annotations

import sys
from pathlib import Path


def pytest_configure() -> None:
    # Keep tests runnable without requiring an editable install.
    repo_root = Path(__file__).resolve().parents[3]
    oc_src = repo_root / "packages" / "ollama_cli" / "src"
    ch_src = repo_root / "packages" / "contextharbor" / "src"
    for p in (str(oc_src), str(ch_src)):
        if p not in sys.path:
            sys.path.insert(0, p)
