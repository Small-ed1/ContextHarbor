from __future__ import annotations

import os
from pathlib import Path


def _prompt(question: str, default: str | None = None) -> str:
    if default:
        q = f"{question} [{default}]: "
    else:
        q = f"{question}: "
    ans = input(q).strip()
    return ans or (default or "")


def _prompt_bool(question: str, default: bool = False) -> bool:
    d = "Y/n" if default else "y/N"
    ans = input(f"{question} ({d}): ").strip().lower()
    if not ans:
        return default
    return ans in {"y", "yes", "true", "1"}


def _expand(p: str) -> str:
    return os.path.expanduser(p.strip())


def main() -> int:
    print("CogniHub setup wizard")
    print("- Writes monorepo/.env (gitignored)")
    print("- You can edit it later")
    print("")

    ollama_url = _prompt("Ollama URL", "http://127.0.0.1:11434").rstrip("/")
    embed_model = _prompt("Embedding model", "nomic-embed-text")
    chat_model = _prompt("Default chat model", "llama3.1")

    use_kiwix = _prompt_bool("Use Kiwix offline ZIMs?", default=False)
    kiwix_url = ""
    kiwix_zim_dir = ""
    if use_kiwix:
        kiwix_url = _prompt("Kiwix URL", "http://127.0.0.1:8081").rstrip("/")
        kiwix_zim_dir = _expand(_prompt("ZIM directory", "~/zims"))

    use_epubs = _prompt_bool("Use EPUB ingestion?", default=False)
    ebooks_dir = ""
    if use_epubs:
        ebooks_dir = _expand(_prompt("Ebooks directory (or Calibre library root)", "~/Ebooks"))

    use_web_search = _prompt_bool("Enable web search (SearxNG)?", default=False)
    searxng_url = ""
    search_provider = ""
    if use_web_search:
        searxng_url = _prompt("SearxNG URL", "http://localhost:8080/search").strip()
        search_provider = _prompt("Search provider order", "searxng").strip()

    allow_shell = _prompt_bool("Enable shell tool (dangerous)?", default=False)

    lines: list[str] = []
    lines.append(f"OLLAMA_URL={ollama_url}")
    lines.append(f"EMBED_MODEL={embed_model}")
    lines.append(f"DEFAULT_CHAT_MODEL={chat_model}")

    if use_kiwix:
        lines.append(f"KIWIX_URL={kiwix_url}")
        lines.append(f"KIWIX_ZIM_DIR={kiwix_zim_dir}")

    if use_epubs:
        lines.append(f"EBOOKS_DIR={ebooks_dir}")

    if use_web_search:
        lines.append(f"SEARXNG_URL={searxng_url}")
        lines.append(f"COGNIHUB_SEARCH_PROVIDER={search_provider}")

    if allow_shell:
        lines.append("ALLOW_SHELL_EXEC=1")

    out = Path(__file__).resolve().parents[1] / ".env"
    out.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print("")
    print(f"Wrote: {out}")
    print("")
    print("Run with:")
    print("  cd monorepo")
    print("  set -a; source .env; set +a")
    print("  uvicorn cognihub.app:app --reload --host 127.0.0.1 --port 8000")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
