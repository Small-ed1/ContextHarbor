# ollama_tools (Qwen + Internet tools)

Minimal tool-calling agent for Ollama with live web tools. This repo intentionally excludes Kiwix.

## Features
- Tool planning step to decide if tools are needed
- Tool calling with strict JSON tool-call format
- Relevance filtering for search results (token overlap + top-k)
- Grounded answers with [T1]/[T2] citations from tool outputs
- Iterative tool loop with evidence summaries and sufficiency checks
- Web safety guardrails (blocked/allowed hosts, redirect cap, timeouts)
- Internet tools:
  - web search (DuckDuckGo)
  - site-specific search
  - fetch + readable text extraction
  - Wikipedia summary

## Setup (Windows)

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -e .
.\run.ps1
```

## Setup (Linux/macOS)

```bash
python -m venv .venv
source .venv/bin/activate
pip install -e .
OLLAMA_MODEL=qwen3:14b python run.py
```

## Environment variables

- `OLLAMA_MODEL` (default: `qwen3:14b`)
- `OLLAMA_HOST` (default: `http://127.0.0.1:11434`)
- `TOOL_INTERPRET_MODEL` (default: `OLLAMA_MODEL`)
- `TOOL_PLANNER_MODEL` (default: `OLLAMA_MODEL`)
- `TOOL_SUMMARY_MODEL` (default: `OLLAMA_MODEL`)
- `TOOL_SUFFICIENCY_MODEL` (default: `OLLAMA_MODEL`)
- `TOOL_ANSWER_MODEL` (default: `OLLAMA_MODEL`)
- `TOOL_MAX_CALLS` (default: `4`)
- `TOOL_RESULT_MAX_CHARS` (default: `3500`)
- `TOOL_SEARCH_TOP_K` (default: `5`)
- `TOOL_SEARCH_MIN_SCORE` (default: `1`)
- `TOOL_MAX_ROUNDS` (default: `3`)
- `WEB_SEARCH_TIMEOUT` (default: `15`)
- `WEB_FETCH_TIMEOUT` (default: `15`)
- `WEB_MAX_REDIRECTS` (default: `5`)
- `WEB_ALLOWED_HOSTS` (default: allow any public host)
- `WEB_BLOCKED_HOSTS` (default: none)
- On startup the CLI checks installed models; if the selected model is missing, install it with `ollama pull qwen3:14b` or set `OLLAMA_MODEL` to an installed model like `phi3:mini`.

## Basic tool loop

1. Interpret the user question.
2. Decide if tools are needed and which ones.
3. Execute tool calls and summarize the evidence.
4. Check if the evidence is sufficient; if not, request more tools.
5. Answer with citations from tool outputs.

## Example prompts

Internet:
- "Search the web: world's strongest man 2017 wikipedia"
- "Search only on wikipedia.org: world's strongest man 2017"
- "Fetch this URL and summarize it: https://en.wikipedia.org/wiki/2017_World%27s_Strongest_Man"
