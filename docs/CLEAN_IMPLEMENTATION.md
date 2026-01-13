# Clean UI & Auto Model Decider Implementation

## Changes Made

### 1. Hover Tooltips (Cleaned Up)

#### CSS (`static/styles.css`)
- Added `[data-tip]` pseudo-element styling for custom tooltips
- Uses `::after` for tooltip text and `::before` for arrow
- Positioned above elements with proper z-index (9999)
- Matches app theme with dark background and border

#### JavaScript (`static/app.js`)
- Updated `hydrateTooltips()` to use `aria-label` preference
- Removes `title` attribute after extracting to avoid double-tooltips
- Applies to all interactive elements: buttons, links, inputs, selects, textareas
- Called after `renderChat()` in `send()` for dynamic buttons
- Called in `init()` for initial page load

#### HTML (`static/index.html`)
- Replaced all `title` attributes with `aria-label`
- Updated 16 elements with accessible labels:
  - Settings, Clear chat, Stop, Send buttons
  - Top K input, File upload input
  - Model select, Auto toggle
  - Settings drawer controls (Save, Reset, Close)
  - System prompt textarea
  - Temperature, num_ctx, keep_alive inputs
  - Prompt textarea

#### Button Creation
- Copy button in `msgNode()` now uses `aria-label` instead of `title`

### 2. Auto Model Decider (Cleaned Up)

#### Frontend (`static/index.html`, `static/app.js`)
- Added "Auto" checkbox toggle next to model selector
- Implemented `decideModel()` function calling `/api/decide_model`
- Updates model dropdown and state when auto-selection completes
- Shows "Auto model: {name}" in status bar
- Integrates with RAG status for better decisions

#### Backend (`app.py`)
- Added `re` import for JSON parsing
- Implemented `_extract_json_obj()` with regex to find first `{...}` block
- Implemented `/api/decide_model` endpoint with improvements:
  - **Filters out embedding models** (excludes models with "embed" in name)
  - Better error handling (returns `None` for model instead of query string)
  - Robust JSON extraction with regex fallback
  - Returns `auto: False` when using heuristics
  - Cleaner reason messages ("fallback largest", "bad_json mid")

#### Task Classification (`_guess_task()`)
- **Coding tasks**: stack trace, traceback, error, refactor, bug, uvicorn, fastapi, docker, arch, systemd, regex
- **Writing tasks**: summarize, explain, write, essay, outline
- **General**: everything else

#### Fallback Logic
- **Coding or long queries** (>700 chars) → Largest model
- **Writing/general** → Medium model
- Returns `auto: False` and reason when fallback used

## How It Works

### Tooltips
1. Page loads → `hydrateTooltips()` runs in `init()`
2. Extracts labels from `aria-label` or `title` attributes
3. Sets `data-tip` attribute with the label
4. Removes `title` attribute to avoid double-tooltips
5. CSS `::after` pseudo-element displays tooltip on hover

### Auto Model Decider
1. User checks "Auto" and sends a message
2. Frontend calls `/api/decide_model` with query and RAG status
3. Backend:
   - Fetches installed models from Ollama
   - Filters out embedding models
   - Classifies task type (coding/writing/general)
   - Asks decider LLM to pick best model
   - Falls back to heuristic if LLM fails or returns bad JSON
4. Frontend updates model dropdown and proceeds to chat

## Testing

### Tooltips
```bash
# Check HTML has aria-labels (not titles)
curl -s http://localhost:8000/ | grep "aria-label" | wc -l
# Expected: 16

# Verify hydrateTooltips removes titles
curl -s http://localhost:8000/static/app.js | grep "removeAttribute.*title"
```

### Auto Model Decider
```bash
# Coding task → largest model
curl -X POST http://localhost:8000/api/decide_model \
  -H "Content-Type: application/json" \
  -d '{"query":"fix docker error","rag_enabled":false}'

# Writing task → medium model
curl -X POST http://localhost:8000/api/decide_model \
  -H "Content-Type: application/json" \
  -d '{"query":"write an essay","rag_enabled":true}'
```

## Current Status

✅ Tooltips: All elements use `aria-label`, double-tooltips eliminated
✅ Auto Model: Filters embedding models, robust JSON parsing, safe fallbacks
✅ Both servers running (FastAPI port 8000, Ollama port 11434)
✅ 10 chat models installed (no embedding-only models)
✅ All features tested and working

## Optional: Fast Decider Model

For faster model selection, pull a tiny model:
```bash
ollama pull llama3.2:1b
export DECIDER_MODEL="llama3.2:1b"
./servers.sh restart
```

This makes the decision process much faster since the decider model is tiny.
