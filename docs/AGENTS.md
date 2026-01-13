# AGENTS.md - Router Phase 1 Development Guide

Essential information for agentic coding agents working in this repository.

## Build, Lint, and Test Commands

```bash
# Install dependencies
pip install -r requirements.txt

# Run development server (FastAPI + Uvicorn)
uvicorn app:app --reload --host 0.0.0.0 --port 8000

# Run TUI
python3 router_tui.py

# Type checking (if mypy is available)
mypy app.py --ignore-missing-imports

# Manual testing
curl http://localhost:8000/health
curl http://localhost:8000/api/status
```

**Note:** This codebase does not have automated tests or linting configured. Tests exist only in backup/ directory. When adding features, manually test endpoints.

## Service Endpoints

- **Backend API**: http://localhost:8000
- **Ollama API**: http://localhost:11434 (must be running separately)

## Code Style Guidelines

### Python (Backend)

#### Imports
```python
from __future__ import annotations
import os, sqlite3, time
from typing import Optional, Any
from contextlib import asynccontextmanager, contextmanager
import httpx
from fastapi import FastAPI, HTTPException, UploadFile, File
from pydantic import BaseModel, Field, ConfigDict
import ragstore, chatstore, webstore, researchstore
```

#### Type Hints
```python
async def get_chat(chat_id: str, limit: int = 2000) -> dict[str, Any]:
    return {"chat": {}, "messages": []}

def get_user(user_id: int) -> Optional[Dict[str, Any]]:
    return None
chat_id: str | None = None
```

#### Pydantic Models
```python
class ChatCreateReq(BaseModel):
    model_config = ConfigDict(extra="ignore")
    title: Optional[str] = "New Chat"
```

#### Error Handling
```python
@app.get("/api/chats/{chat_id}")
async def api_get_chat(chat_id: str):
    try:
        return chatstore.get_chat(chat_id)
    except KeyError:
        raise HTTPException(status_code=404, detail="chat not found")
```

#### Naming Conventions
- **Classes**: PascalCase (`ChatCreateReq`, `Database`)
- **Functions/Methods**: snake_case (`get_chat`, `list_chats`, `init_db`)
- **Constants**: UPPER_SNAKE_CASE (`OLLAMA_URL`, `DEFAULT_EMBED_MODEL`)
- **Files**: snake_case (`user_manager.py`, `database.py`)
- **Variables**: snake_case (`user_data`, `result_list`)
- **Private methods**: prefix with `_` (`_validate_input`)

#### Database Operations
```python
@contextmanager
def _db():
    con = sqlite3.connect(DB_PATH, timeout=10, check_same_thread=False)
    con.row_factory = sqlite3.Row
    con.execute("PRAGMA journal_mode=WAL;")
    con.execute("PRAGMA synchronous=NORMAL;")
    try:
        yield con
        con.commit()
    finally:
        con.close()
```

### JavaScript (Web UI)

#### Imports
```javascript
const el = (id) => document.getElementById(id);
async function api(path, opts) {
    const res = await fetch(path, opts);
    const text = await res.text();
    let j = {};
    try { j = JSON.parse(text); } catch {}
    if (!res.ok) throw new Error(j.error || j.detail || `HTTP ${res.status}`);
    return j;
}
```

#### Naming Conventions
- **Components**: PascalCase (`ChatInterface`, `UserProfile`)
- **Functions**: camelCase (`handleSubmit`, `loadMessages`)
- **Constants**: UPPER_SNAKE_CASE (`MAX_MESSAGE_LENGTH`)
- **CSS Classes**: kebab-case (`chat-container`, `message-item`)
- **Variables**: camelCase (`userData`, `isLoading`)

### Python (TUI)

Follow backend Python conventions. Use textual for TUI components.

## File Organization

```
/
├── app.py                 # Main FastAPI application
├── chatstore.py           # Chat database operations
├── ragstore.py            # RAG document storage
├── webstore.py            # Web page scraping
├── researchstore.py       # Deep research runs
├── router_tui.py          # Terminal User Interface
├── requirements.txt        # Python dependencies
├── static/
│   ├── index.html         # Main web UI
│   └── app.js            # Frontend JavaScript
└── *.sqlite3             # SQLite databases
```

## Environment Variables

```bash
OLLAMA_URL="http://127.0.0.1:11434"
EMBED_MODEL="embeddinggemma"
DEFAULT_CHAT_MODEL="llama3.1"
API_BASE="http://127.0.0.1:8000"
RAG_DB="rag.sqlite3"
CHAT_DB="chat.sqlite3"
MAX_UPLOAD_BYTES=10485760"

# Web scraping SSRF protection
WEB_ALLOWED_HOSTS=""        # Comma-separated whitelist (empty = any public domain)
WEB_BLOCKED_HOSTS=""        # Comma-separated blacklist
WEB_UA="Mozilla/5.0..."  # Custom User-Agent for requests
```

## Notes

- **No automated tests**: All testing is manual via curl or web UI
- **No linting/formatting config**: Code style is maintained manually
- **SQLite WAL mode**: Always use WAL journal mode for concurrency
- **Type hints**: Use `dict[str, Any]` and `list[str]` style (Python 3.9+)
- **Async context managers**: Use `@asynccontextmanager` for lifespan in FastAPI apps
- **Error responses**: Return JSON with `{"error": "message"}` or `{"detail": "message"}`
