import json
import threading
from pathlib import Path
from typing import Any

_CONFIG_CACHE: dict[str, Any] = {}
_CONFIG_MTIME: float = 0
_CONFIG_LOCK = threading.RLock()


def get_default_config() -> dict[str, Any]:
    """Return the default configuration settings."""
    return {
        "theme": "dark",
        "accent": "#007bff",
        "temperature": 0.7,
        "contextTokens": 8000,
        "defaultModel": "",
        "defaultTask": "chat",
        "showArchived": False,
        "autoModelSwitch": False,
        "autoModelSwitchMode": "suggest",
        "citationFormat": "inline",
        "maxToolCalls": 10,
        "researchDepth": "standard",
        "enableStreaming": True,
        "debugMode": False,
        "fontSize": "medium",
        "animations": True,
        "memoryLimit": 10,
    }


def load_config() -> dict[str, Any]:
    """Load configuration from file with caching."""
    global _CONFIG_CACHE, _CONFIG_MTIME
    with _CONFIG_LOCK:
        config_path = Path("router.json")
        try:
            mtime = config_path.stat().st_mtime
            if mtime > _CONFIG_MTIME:
                with open(config_path) as f:
                    _CONFIG_CACHE = json.load(f)
                _CONFIG_MTIME = mtime
            return (
                _CONFIG_CACHE.copy()
            )  # Return a copy to prevent external modifications
        except Exception:
            return get_default_config()


def save_config(data: dict[str, Any]):
    """Save configuration to file and update cache."""
    global _CONFIG_CACHE, _CONFIG_MTIME
    with _CONFIG_LOCK:
        config_path = Path("router.json")
        current = load_config()
        current.update(data)
        with open(config_path, "w") as f:
            json.dump(current, f, indent=2)
        _CONFIG_MTIME = config_path.stat().st_mtime
        _CONFIG_CACHE = current  # Update cache with saved data
