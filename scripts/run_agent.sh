#!/usr/bin/env bash
set -euo pipefail

# Activate virtual environment
source venv/bin/activate

export OLLAMA_HOST="${OLLAMA_HOST:-http://localhost:11434}"
export OLLAMA_MODEL="${OLLAMA_MODEL:-qwen3}"
export OLLAMA_SUPERVISOR="${OLLAMA_SUPERVISOR:-}"

# optional: web search backend
# export SEARXNG_URL="${SEARXNG_URL:-http://localhost:8080/search}"

python3 scripts/ollama_tool_agent.py