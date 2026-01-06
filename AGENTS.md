# AGENTS.md - Router Phase 1 Development Guide

Essential information for agentic coding agents working in this repository.

## Build, Lint, and Test Commands

### Backend (Python + FastAPI)
```bash
# Install dependencies (Arch Linux: pip install --break-system-packages -r requirements.txt)
pip install --break-system-packages -r requirements.txt

# Development server
uvicorn backend.app:app --reload --host 0.0.0.0 --port 8000

# Web UI server (separate)
uvicorn webui.app:app --reload --host 0.0.0.0 --port 3000

# Run all tests
python -m pytest tests/ -v

# Run single test file
python -m pytest tests/test_database.py -v

# Run tests with coverage
python -m pytest tests/ --cov=backend --cov-report=html

# Type checking
mypy backend/ --ignore-missing-imports

# Code formatting
black backend/ && isort backend/

# Lint all Python files
ruff check backend/ webui/ agent/ utils/

# Fix auto-fixable lint issues
ruff check backend/ webui/ agent/ utils/ --fix
```

### Service Endpoints
- **Backend API**: http://localhost:8000
- **Web UI**: http://localhost:3000
- **Ollama API**: http://localhost:11434

### Post-Edit Workflow
After making any code changes, run:
```bash
# Quick restart (recommended)
./restart_servers.sh all

# Health check
curl http://localhost:8000/api/v1/health
```

## Code Style Guidelines

### Python (Backend)

#### Imports
```python
# Standard library imports
import json
import sqlite3
from typing import List, Dict, Any, Optional

# Third-party imports
import httpx
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

# Local imports
from .database import Database
from .auth import AuthManager
```

#### Type Hints
```python
# Use explicit typing for all function parameters and return values
async def get_user(user_id: int) -> Optional[Dict[str, Any]]:
    # Function implementation
    pass

# Use Union types for multiple possible types
def process_data(data: Union[str, bytes]) -> str:
    pass

# Use generics for collections
def search_items(query: str) -> List[Dict[str, str]]:
    pass
```

#### Error Handling
```python
async def api_endpoint(request: UserRequest):
    try:
        if not request.name:
            raise HTTPException(status_code=400, detail="Name required")
        result = await process_user_request(request)
        return {"status": "success", "data": result}
    except HTTPException:
        raise  # Re-raise FastAPI exceptions
    except sqlite3.IntegrityError as e:
        raise HTTPException(status_code=400, detail="Database constraint violation")
    except Exception as e:
        # Log unexpected errors
        logger.error(f"Unexpected error: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")
```

#### Naming Conventions
- **Classes**: PascalCase (`UserManager`, `Database`)
- **Functions/Methods**: snake_case (`get_user`, `process_data`)
- **Constants**: UPPER_SNAKE_CASE (`DEFAULT_TIMEOUT`, `MAX_RETRIES`)
- **Files**: snake_case (`user_manager.py`, `database.py`)
- **Variables**: snake_case (`user_data`, `result_list`)
- **Private methods**: prefix with `_` (`_validate_input`)
- **Database tables**: snake_case (`users`, `chat_messages`)

#### Async/Await Patterns
```python
# Always use async for I/O operations
async def fetch_user_data(user_id: int) -> Dict[str, Any]:
    async with httpx.AsyncClient() as client:
        response = await client.get(f"/api/users/{user_id}")
        return response.json()

# Use ThreadPoolExecutor for CPU-bound operations
async def process_embedding(text: str) -> List[float]:
    loop = asyncio.get_event_loop()
    return await loop.run_in_executor(executor, embedding_model.encode, text)
```

#### Database Operations
```python
# Always use context managers for database connections
def get_user(user_id: int) -> Optional[Dict[str, Any]]:
    with sqlite3.connect(db.db_path) as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM users WHERE id = ?", (user_id,))
        row = cursor.fetchone()
        return dict(row) if row else None

# Use parameterized queries to prevent SQL injection
def create_user(username: str, password_hash: str) -> int:
    with sqlite3.connect(db.db_path) as conn:
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO users (username, password_hash)
            VALUES (?, ?)
        """, (username, password_hash))
        conn.commit()
        return cursor.lastrowid
```

### JavaScript (Web UI)

#### Imports
```javascript
// Standard modules first
import { useState, useEffect } from 'react';

// Third-party libraries
import axios from 'axios';

// Local imports (relative paths)
import { apiClient } from './api';
import ChatMessage from './ChatMessage';
```

#### Component Patterns
```javascript
function ChatInterface({ userId }) {
    const [messages, setMessages] = useState([]);
    const [loading, setLoading] = useState(false);

    useEffect(() => {
        loadMessages();
    }, [userId]);

    const loadMessages = async () => {
        try {
            setLoading(true);
            const data = await apiClient.get(`/chats/${userId}/messages`);
            setMessages(data.messages);
        } catch (error) {
            console.error('Failed to load messages:', error);
        } finally {
            setLoading(false);
        }
    };

    return (
        <div className="chat-container">
            {messages.map(msg => (
                <ChatMessage key={msg.id} message={msg} />
            ))}
        </div>
    );
}
```

#### Error Handling
```javascript
const handleApiCall = async () => {
    try {
        const response = await fetch('/api/data', {
            headers: { 'Authorization': `Bearer ${token}` }
        });
        if (!response.ok) {
            throw new Error(`HTTP ${response.status}`);
        }
        const data = await response.json();
        setData(data);
    } catch (error) {
        console.error('API call failed:', error);
        setError(error.message);
    }
};
```

#### Naming Conventions
- **Components**: PascalCase (`ChatInterface`, `UserProfile`)
- **Functions**: camelCase (`handleSubmit`, `loadMessages`)
- **Constants**: UPPER_SNAKE_CASE (`MAX_MESSAGE_LENGTH`)
- **CSS Classes**: kebab-case (`chat-container`, `message-item`)
- **Variables**: camelCase (`userData`, `isLoading`)

### General Guidelines

#### File Organization
```
backend/
├── app.py              # Main FastAPI application
├── database.py         # Database schema and connections
├── auth.py            # Authentication and authorization
├── config.py          # Configuration management
├── rag_service.py     # RAG operations
├── chat_manager.py    # Chat CRUD operations
└── routes/            # Additional route handlers

webui/
├── app.py             # Web UI FastAPI application
└── static/            # CSS/JS assets

agent/
├── router.py          # Main agent logic
├── research/          # Research agents
├── tools/             # Tool implementations
└── config.py          # Agent configuration

tests/
├── test_database.py   # Database tests
├── test_auth.py       # Authentication tests
└── test_*.py          # Other test files
```

#### Security Best Practices
- **Input Validation**: Always validate and sanitize user inputs
- **Authentication**: Use JWT tokens with proper expiration
- **SQL Injection Prevention**: Use parameterized queries
- **XSS Prevention**: Sanitize HTML content in responses
- **CORS**: Configure appropriate CORS policies
- **Secrets**: Never commit secrets; use environment variables

#### Performance Considerations
- **Database Indexing**: Add indexes on frequently queried columns
- **Connection Pooling**: Reuse database connections
- **Async Operations**: Use async/await for I/O operations
- **Memory Management**: Monitor memory usage, especially with embeddings
- **Caching**: Cache expensive operations when appropriate

This guide ensures consistency across the codebase and helps agents produce high-quality, maintainable code.