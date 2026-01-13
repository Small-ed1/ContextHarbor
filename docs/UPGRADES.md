# UI and Model Selection Upgrades

## 1. Hover Tooltips

All buttons now have elegant hover tooltips using CSS pseudo-elements.

### Implementation
- **CSS**: Added `[data-tip]` styling with `::after` and `::before` pseudo-elements
- **JS**: Added `hydrateTooltips()` function that converts `title` attributes to `data-tip` attributes
- **Auto-initialization**: Called in `init()` so all buttons have tooltips on load

### Features
- Styled tooltips matching app theme
- Automatic conversion of existing `title` attributes
- Applies to dynamically created buttons (like Copy)
- Z-index 9999 for visibility above other elements

### Usage
All buttons with `title` attribute automatically get styled tooltips:
```html
<button title="Settings">⚙</button>
<button title="Clear chat">🧹</button>
```

## 2. Auto Model Decider

Tiny LLM (or heuristic fallback) picks the best model for each query.

### Components

#### Frontend
- **Auto Toggle**: Checkbox in header controls (`autoModelToggle`)
- **decideModel()**: Async function calling `/api/decide_model`
- **Auto-selection**: Updates model select dropdown and saves state
- **Status hint**: Shows selected model in status bar

#### Backend
- **`/api/decide_model`**: New endpoint for model selection
- **Task classification**: `_guess_task()` categorizes queries (coding/writing/general)
- **Decider model**: Uses `DECIDER_MODEL` env var or smallest installed model
- **Fallback logic**: Heuristics when LLM decider unavailable

### How It Works

1. User types query with Auto enabled
2. Frontend calls `/api/decide_model` with query and RAG status
3. Backend:
   - Fetches installed models from Ollama
   - Classifies task type (coding/writing/general)
   - Asks decider LLM to pick best model
   - Falls back to heuristic if needed
4. Frontend updates model dropdown and continues to chat

### Heuristic Fallback
When LLM decider unavailable:
- **Coding** or **long** (>700 chars) → Largest model
- **Writing/general** → Medium model

### Optional: Pull Fast Decider Model
For faster model selection, pull a tiny model:
```bash
ollama pull llama3.2:1b
export DECIDER_MODEL="llama3.2:1b"
```

### Testing
```bash
# Test endpoint directly
curl -X POST http://localhost:8000/api/decide_model \
  -H "Content-Type: application/json" \
  -d '{"query":"fix stack trace","rag_enabled":false}'
```

### UI Changes
- Added "Auto" checkbox next to model selector
- Model dropdown updates automatically when Auto is on
- Status bar shows "Auto model: {selected_model}"

### Configuration
Environment variables:
- `DECIDER_MODEL` - Model used for selection (optional)
- Defaults to smallest installed model if not set

## Current Status

✅ Tooltips implemented and working
✅ Auto model decider endpoint implemented
✅ Frontend integration complete
✅ Fallback logic for reliability
✅ Both servers running and tested

## Usage

### Enable Auto Model Selection
1. Check "Auto" checkbox in header
2. Type query and send
3. Model automatically selects based on query type

### Hover Any Button
1. Hover over any button in the UI
2. See styled tooltip with description

### Manual Mode
Uncheck "Auto" to manually select models as before.
