try:
    from ollama import Client
except ModuleNotFoundError:
    print(
        "Missing dependency: ollama.\n"
        "Create a venv and install dependencies:\n"
        "  python -m venv .venv\n"
        "  .venv\\Scripts\\Activate.ps1\n"
        "  pip install -e modules/router_phase1-tool\n"
    )
    raise SystemExit(1)

from ollama_tools.agent import Agent
from ollama_tools.config import ollama_host, ollama_model
from ollama_tools.tools.basic import register_basic_tools
from ollama_tools.tools.internet import register_internet_tools


def _list_models(host: str) -> list[str]:
    client = Client(host=host)
    response = client.list()
    if isinstance(response, dict):
        entries = response.get("models", [])
    elif hasattr(response, "models"):
        entries = list(getattr(response, "models") or [])
    elif isinstance(response, list):
        entries = response
    else:
        entries = []

    models: list[str] = []
    for entry in entries:
        name = None
        if isinstance(entry, dict):
            name = entry.get("name") or entry.get("model")
        elif hasattr(entry, "model"):
            name = getattr(entry, "model")
        if isinstance(name, str):
            models.append(name)
    return models


def _ensure_model_available(model: str, host: str) -> bool:
    try:
        models = _list_models(host)
    except Exception as exc:
        print(f"Error: failed to reach Ollama at {host}: {exc}")
        return False

    if model in models:
        return True

    if models:
        available = ", ".join(models)
        print(f"Error: model '{model}' is not downloaded. Available: {available}")
    else:
        print(f"Error: model '{model}' is not downloaded and no models are available.")
    return False


def main() -> None:
    model = ollama_model()
    host = ollama_host()

    if not _ensure_model_available(model, host):
        return

    agent = Agent(model=model, host=host)

    register_basic_tools(agent.tools)
    register_internet_tools(agent.tools)

    print(f"Ollama Tool Agent ({model}) (type 'exit' to quit)\n")

    while True:
        try:
            q = input("> ").strip()
            if not q:
                continue
            if q.lower() in {"exit", "quit", "q"}:
                break
            print(agent.chat(q))
            print()
        except KeyboardInterrupt:
            print("\n^C")
            break
        except Exception as exc:
            print(f"Error: {exc}")
            print()


if __name__ == "__main__":
    main()
