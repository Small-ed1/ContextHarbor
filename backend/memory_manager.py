import json
from pathlib import Path
from typing import Any

MEMORIES_PATH = Path("projects/default/memories.json")


def load_memories() -> list[dict[str, Any]]:
    """Load memories from the JSON file."""
    if MEMORIES_PATH.exists():
        try:
            with open(MEMORIES_PATH) as f:
                return json.load(f)
        except Exception:
            pass
    return []


def save_memories(memories: list[dict[str, Any]]):
    """Save memories to the JSON file."""
    with open(MEMORIES_PATH, "w") as f:
        json.dump(memories, f, indent=2)
