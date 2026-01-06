import os
from typing import Any

import httpx

OLLAMA_HOST = os.environ.get("OLLAMA_HOST", "http://127.0.0.1:11434").rstrip("/")

# Reusable HTTP client for Ollama API calls
_OLLAMA_CLIENT = None


def get_ollama_client() -> httpx.Client:
    """Get a reusable HTTP client for Ollama API calls."""
    global _OLLAMA_CLIENT
    if _OLLAMA_CLIENT is None:
        _OLLAMA_CLIENT = httpx.Client(timeout=5.0)
    return _OLLAMA_CLIENT


def get_ollama_models() -> list[str]:
    """Fetch available models from Ollama."""
    try:
        client = get_ollama_client()
        response = client.get(f"{OLLAMA_HOST}/api/tags")
        if response.status_code == 200:
            data = response.json()
            return [model["name"] for model in data.get("models", [])]
    except Exception:
        pass
    return ["llama3.2:latest"]


def get_all_models() -> list[dict[str, str]]:
    """Get all available models from Ollama and OpenCode."""
    """Get all available models including opencode.ai"""
    models = []

    # Add Ollama models
    ollama_models = get_ollama_models()
    for model in ollama_models:
        models.append({"name": model, "provider": "ollama", "type": "local"})

    # Add opencode.ai models
    opencode_key = os.environ.get("OPENCODE_API_KEY")
    if opencode_key:
        try:
            # Try to fetch available models from opencode.ai
            with httpx.Client(timeout=5.0) as client:
                headers = {"Authorization": f"Bearer {opencode_key}"}
                response = client.get(
                    "https://api.opencode.ai/v1/models", headers=headers
                )
                if response.status_code == 200:
                    data = response.json()
                    for model in data.get("data", []):
                        models.append(
                            {"name": model["id"], "provider": "opencode", "type": "api"}
                        )
        except Exception:
            # Fallback to default opencode models
            models.extend(
                [
                    {"name": "opencode-gpt4", "provider": "opencode", "type": "api"},
                    {"name": "opencode-claude", "provider": "opencode", "type": "api"},
                ]
            )
    else:
        # Add placeholder models to show opencode option
        models.append({"name": "opencode-gpt4", "provider": "opencode", "type": "api"})

    return models
