# AGENTS.md

Purpose
- Guide agentic coding assistants working in this repo.
- Favor small, focused changes that match existing patterns.
- Keep tooling lightweight and avoid new dependencies unless necessary.

Repo Summary
- Python package: `ollama_tools`
- Entry point script: `run.py`
- Tool registry and core types: `ollama_tools/toolcore.py`
- Tools live in `ollama_tools/tools/`

Key Files
- `ollama_tools/agent.py` handles the tool loop and prompt assembly.
- `ollama_tools/config.py` centralizes environment defaults.
- `ollama_tools/tools/basic.py` shows the simplest ToolSpec patterns.
- `ollama_tools/tools/internet.py` is the only network module.

Environment
- Python >= 3.11
- Local venv in `.venv/`
- Main dependencies: `ollama`, `pydantic`, `requests`, `ddgs`, `beautifulsoup4`
- Optional dev dependency: `ruff`

Runtime Configuration
- `OLLAMA_MODEL` sets the model; default is `qwen3:14b`.
- `OLLAMA_HOST` sets the Ollama host; default is `http://127.0.0.1:11434`.
- `TOOL_INTERPRET_MODEL` overrides the interpreter model.
- `TOOL_PLANNER_MODEL` overrides the planner model.
- `TOOL_SUMMARY_MODEL` overrides the summary model.
- `TOOL_SUFFICIENCY_MODEL` overrides the sufficiency model.
- `TOOL_ANSWER_MODEL` overrides the final answer model.
- `WEB_SEARCH_TIMEOUT` controls DDG search timeout (seconds).
- `WEB_FETCH_TIMEOUT` controls fetch timeouts (seconds).
- `WEB_MAX_REDIRECTS` caps redirect chains.
- `WEB_ALLOWED_HOSTS` allows only specific hosts (comma-separated).
- `WEB_BLOCKED_HOSTS` blocks specific hosts (comma-separated).
- `TOOL_MAX_CALLS` caps tool calls per query.
- `TOOL_MAX_ROUNDS` caps tool loop rounds.
- `TOOL_RESULT_MAX_CHARS` clamps tool output size.
- `TOOL_SEARCH_TOP_K` keeps top-k search results.
- `TOOL_SEARCH_MIN_SCORE` filters low-relevance search hits.
- `TOOL_TRACE=1` enables tool loop debug output.

Cursor/Copilot Rules
- No `.cursor/rules/`, `.cursorrules`, or `.github/copilot-instructions.md` found.

Build, Lint, Test Commands
- Create venv (Windows): `python -m venv .venv`
- Activate venv (Windows): `\.venv\Scripts\Activate.ps1`
- Activate venv (Linux/macOS): `source .venv/bin/activate`
- Install package: `pip install -e .`
- Install dev deps: `pip install -e .[dev]`
- Run the agent (Windows): `./run.ps1`
- Run the agent (cross-platform): `python run.py`
- Lint: `ruff check .`
- Lint with fixes: `ruff check . --fix`
- Formatting: no formatter configured; keep manual formatting consistent
- Tests: no test suite in repo right now
- If tests are added (pytest assumed): `pytest`
- Single test (pytest): `pytest tests/test_file.py::test_case`
- Single test by name (pytest): `pytest -k "name_substring"`

Code Style Guidelines

Imports
- Use standard library imports first, then third-party, then local imports.
- Prefer absolute imports within package (e.g., `from ollama_tools.toolcore import ToolRegistry`).
- Keep import groups separated by a blank line.

Formatting
- 4-space indent, no tabs.
- `ruff` line length is 100; wrap long lines accordingly.
- Use f-strings for formatting.
- Keep blank lines between logical sections and top-level definitions.
- Prefer explicit intermediate variables over deeply nested expressions.
- Keep docstrings brief and only for non-obvious logic.

Typing and Annotations
- Use `from __future__ import annotations` in modules with forward refs.
- Add type hints on public functions and methods.
- Prefer `dict[str, Any]` and `list[str]` instead of `Dict`/`List`.
- Use `|` union types (Python 3.11+) instead of `Optional` when clear.

Naming Conventions
- Modules and functions: `snake_case`.
- Classes and dataclasses: `PascalCase`.
- Constants: `UPPER_SNAKE_CASE`.
- Tool specs are defined as module-level constants (e.g., `WEB_SEARCH`).

Tool Definitions
- Each tool has a `BaseModel` args schema and a handler function.
- Create a `ToolSpec` constant with `name`, `description`, `args_schema`, `handler`.
- Register tools in `register_*_tools()` in the relevant module.
- Keep descriptions concise and user-facing.

Error Handling
- Validate inputs in Pydantic models or early in handlers.
- Raise `ValueError` for user input errors in tool handlers.
- Let `ToolRegistry.call()` catch exceptions and return `{"ok": False, "error": ...}`.
- When adding network calls, use timeouts and surface clear errors.
- Prefer explicit error messages that can be shown to end users.
- Avoid silent failures; either return a structured error or raise.

Logging and Debugging
- Use the `Agent.trace` flag and `_dbg()` helper for debug output.
- Avoid noisy print statements in libraries; keep user-facing prints in `run.py`.
- If debugging a tool, log only small, safe snippets of data.

Behavioral Patterns
- Keep `Agent.chat()` focused on orchestration (plan -> tools -> synth).
- Only modify system prompt text in `ollama_tools/agent.py` when necessary.
- Preserve JSON planning and sufficiency schemas and extraction logic.
- Maintain conversation history as a list of `{role, content}` dicts.
- Tool calls should return quickly; cap calls and fall back gracefully.

Working With Tools
- Tools should be deterministic and side-effect light unless explicitly needed.
- Avoid hidden I/O; keep network work in `internet.py`.
- Use clear, stable return shapes (lists of dicts, dicts with consistent keys).
- Keep output sizes bounded; respect `max_chars` and add ellipses when truncating.
- Validate URLs with `_is_http_url` and reject non-http schemes.
- Reuse shared helpers like `_clean_text` and `_extract_readable_text`.

Networking and I/O
- Set explicit timeouts on all network calls.
- Use the shared `UA` user agent string for outbound HTTP requests.
- Parse HTML with `BeautifulSoup` and remove script/style content before extracting text.
- Clamp fetched content with `max_chars` to avoid oversized responses.
- Reject non-HTTP URLs early with a clear error message.

Adding New Tools Checklist
- Define `Args` model in `ollama_tools/tools/<module>.py`.
- Implement handler with type hints and concise error messages.
- Create a `ToolSpec` constant.
- Register it in `register_*_tools()`.
- Update `run.py` if new tool module must be registered.

Testing Guidance (When Tests Exist)
- Prefer `pytest` and keep tests in `tests/`.
- Name files `test_*.py` and test functions `test_*`.
- Keep unit tests fast; mock network calls.
- Favor deterministic fixtures and stable response payloads.

Documentation
- Update `README.md` for user-facing behavior changes.
- Mention new tools and environment variables.

Packaging
- Project metadata is in `pyproject.toml`.
- Keep dependencies minimal and version constraints consistent.
- Avoid adding new extras unless there is a clear dev need.

Do/Do Not
- Do keep changes small and aligned with current style.
- Do reuse existing helpers like `_is_http_url` and `_clean_text`.
- Do not add large frameworks or unnecessary abstractions.
- Do not change tool-call JSON schema without updating parser logic.
- Do not add hidden filesystem access or shell execution tools.
