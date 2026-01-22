import os

DEFAULT_HOST = "http://127.0.0.1:11434"
DEFAULT_MODEL = "qwen3:14b"


def ollama_host() -> str:
    return os.environ.get("OLLAMA_HOST", DEFAULT_HOST)


def ollama_model() -> str:
    return os.environ.get("OLLAMA_MODEL", DEFAULT_MODEL)
