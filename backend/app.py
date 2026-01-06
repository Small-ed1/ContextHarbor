from __future__ import annotations

"""Router Phase 1 Backend API

FastAPI application providing AI chat and research capabilities.
Supports multiple models, conversation management, and deep research tasks.
"""

import asyncio
import json
import logging
import os
import shutil
import threading
import uuid
from datetime import datetime
from pathlib import Path
from typing import Any

try:
    import numpy as np

    NUMPY_AVAILABLE = True
except ImportError:
    NUMPY_AVAILABLE = False
    np = None  # type: ignore

import httpx
from fastapi import (APIRouter, FastAPI, File, HTTPException, Request,
                     UploadFile)
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import (FileResponse, HTMLResponse, JSONResponse,
                               StreamingResponse)
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from starlette.middleware.base import BaseHTTPMiddleware


class StatsMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request, call_next):
        stats.increment_stat("requests")
        response = await call_next(request)
        return response


from . import stats
from .chat_manager import list_chats as list_chats_func
from .chat_manager import create_chat as create_chat_func
from .chat_manager import get_chat as get_chat_func
from .chat_manager import update_chat as update_chat_func
from .chat_manager import delete_chat as delete_chat_func
from .chat_manager import archive_chat as archive_chat_func
from .chat_manager import add_message as add_message_func
from .auth import AuthManager, auth_manager
from .memory_manager import load_memories
from .memory_manager import save_memories
from .model_manager import get_all_models
# Research functions
from .research_manager import get_research_status
from .research_manager import start_research
from .research_manager import stop_research
from .research_manager import list_research_sessions
from .research_manager import resume_research_session
from .research_manager import delete_research_session
from .research_manager import get_agent_status
from .research_manager import research_progress
from .config_manager import load_config
from .config_manager import save_config
from .rag_service import rag_service
from .routes.chat import router as chat_router

# Document Q&A imports - temporarily disabled for basic server startup
# try:
#     from utils.document_processor import DocumentProcessingPipeline, DocumentMetadata
#     from utils.embedding_service import EmbeddingService, DocumentEmbeddingService, EmbeddingConfig
#     from utils.vector_store import VectorStoreManager, VectorStoreConfig
#     DOCUMENT_PROCESSING_AVAILABLE = True
# except ImportError:
DOCUMENT_PROCESSING_AVAILABLE = False

APP_TITLE = "Router Phase 1 - Ollama Integrated"
OLLAMA_HOST = os.environ.get("OLLAMA_HOST", "http://127.0.0.1:11434").rstrip("/")
OLLAMA_MODEL = os.environ.get("OLLAMA_MODEL", "llama3.2:1b")

app = FastAPI(title=APP_TITLE)


# Startup event
@app.on_event("startup")
async def startup_event():
    logger.info("Router Phase 1 backend started")
    logger.info(f"Ollama host: {OLLAMA_HOST}")
    logger.info(f"Ollama model: {OLLAMA_MODEL}")


# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify allowed origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.mount("/static", StaticFiles(directory="backend/static"), name="static")

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class ChatRequest(BaseModel):
    message: str
    model: str | None = None
    temperature: float | None = None
    contextTokens: int | None = None
    mode: str = "chat"
    project: str = "default"
    text: str | None = None  # Alias for message
    task: str = "chat"  # Alternative to mode
    researchDepth: str = "standard"  # For research mode
    chat_id: str | None = None  # For chat history


class ResearchRequest(BaseModel):
    topic: str
    depth: str = "standard"
    project: str = "default"


@app.get("/")
def home():
    return FileResponse("backend/static/index.html")


@app.post("/api/opencode/test")
async def test_opencode_connection(request: dict[str, str]):
    """Test opencode.ai API connection"""
    try:
        api_key = request.get("apiKey")
        if not api_key:
            return {"success": False, "error": "API key required"}

        # Test with a simple request to opencode.ai
        async with httpx.AsyncClient(timeout=10.0) as client:
            headers = {"Authorization": f"Bearer {api_key}"}
            response = await client.get(
                "https://api.opencode.ai/v1/models", headers=headers
            )

            if response.status_code == 200:
                return {"success": True, "message": "Connection successful"}
            elif response.status_code == 401:
                return {"success": False, "error": "Invalid API key"}
            else:
                return {"success": False, "error": f"HTTP {response.status_code}"}

    except Exception as e:
        return {"success": False, "error": str(e)}


@app.get("/api/settings")
def get_settings():
    return load_config()


@app.post("/api/settings")
def save_settings(data: dict):
    save_config(data)
    return {"status": "ok"}


@app.get("/api/memories")
def get_memories():
    return load_memories()


@app.post("/api/memories")
def add_memory(data: dict):
    memories = load_memories()
    key = data.get("key", "")
    value = data.get("value", "")
    if key and value:
        memories = [m for m in memories if m.get("key") != key]
        memories.append({"key": key, "value": value})
        save_memories(memories)
    return {"status": "ok"}


@app.delete("/api/memories/{key}")
def delete_memory(key: str):
    memories = load_memories()
    memories = [m for m in memories if m.get("key") != key]
    save_memories(memories)
    return {"status": "ok"}


@app.get("/api/models")
def get_models():
    logger.info("Fetching available models")
    try:
        all_models = get_all_models()
        model_names = [model["name"] for model in all_models]
        default_model = "llama3.2:latest"

        # Prefer opencode models if available
        for model in all_models:
            if model["provider"] == "opencode":
                default_model = model["name"]
                break

        logger.info(f"Found {len(model_names)} models, default: {default_model}")
        return {
            "items": model_names,
            "default": default_model,
            "providers": all_models,  # Include provider info for UI
        }
    except Exception as e:
        logger.error(f"Error fetching models: {e}")
        return {"items": ["llama3.2:latest"], "default": "llama3.2:latest"}


@app.get("/api/chats")
def list_chats(limit: int = 50, offset: int = 0):
    show_archived = load_config().get("showArchived", False)
    return list_chats_func(show_archived, limit, offset)


@app.get("/api/chats/search")
def search_chats(q: str = "", limit: int = 50):
    """Search chats by content using FTS."""
    if not q:
        return list_chats_func(False, limit, 0)

    # Search messages FTS
    import sqlite3
    from .database import db
    with sqlite3.connect(db.db_path) as conn:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT DISTINCT c.id, c.name, c.created_at, c.updated_at
            FROM chats c
            JOIN messages m ON c.id = m.chat_id
            WHERE m.rowid IN (
                SELECT rowid FROM messages_fts WHERE messages_fts MATCH ?
            )
            ORDER BY c.updated_at DESC
            LIMIT ?
        """, (q, limit))

        chats = []
        for row in cursor.fetchall():
            chat_id, name, created_at, updated_at = row
            chats.append({
                "id": chat_id,
                "title": name,
                "created_at": created_at,
                "summary": "",
                "archived": False,
            })

        return chats


@app.post("/api/chats")
def create_chat():
    chat_id = create_chat_func()
    return {"id": chat_id}


@app.get("/api/chats/{chat_id}")
def get_chat(chat_id: str):
    result = get_chat_func(chat_id)
    if "error" in result:
        raise HTTPException(status_code=404, detail=result["error"])
    return result


@app.put("/api/chats/{chat_id}")
def update_chat(chat_id: str, data: dict):
    result = update_chat_func(chat_id, data)
    if "error" in result:
        raise HTTPException(status_code=404, detail=result["error"])
    return result


@app.delete("/api/chats/{chat_id}")
def delete_chat(chat_id: str):
    result = delete_chat_func(chat_id)
    if "error" in result:
        raise HTTPException(status_code=404, detail=result["error"])
    return result


@app.post("/api/chats/{chat_id}/archive")
def archive_chat(chat_id: str):
    result = archive_chat_func(chat_id)
    if "error" in result:
        raise HTTPException(status_code=404, detail=result["error"])
    return result


@app.post("/api/chats/{chat_id}/messages")
async def add_message(chat_id: str, message: dict):
    """Add a message to a chat."""
    role = message.get("role")
    content = message.get("content")
    if not role or not content:
        raise HTTPException(status_code=400, detail="Role and content required")

    # Estimate token count (simple word count)
    token_count = len(content.split())

    success = add_message_func(chat_id, role, content, token_count)
    if not success:
        raise HTTPException(status_code=500, detail="Failed to add message")
    return {"status": "ok"}

@app.post("/api/chat")
async def chat(req: ChatRequest):
    """Process a chat message with Ollama."""
    try:
        # Get chat history
        messages: list[dict[str, Any]] = []
        if hasattr(req, 'chat_id') and req.chat_id:
            chat_data = get_chat_func(req.chat_id)
            if "messages" in chat_data and isinstance(chat_data["messages"], list):
                messages = chat_data["messages"]

        # Add current message
        messages.append({"role": "user", "content": req.message})

        # Call Ollama
        async with httpx.AsyncClient(timeout=60.0) as client:
            response = await client.post(
                f"{OLLAMA_HOST}/api/chat",
                json={
                    "model": req.model or OLLAMA_MODEL,
                    "messages": messages,
                    "stream": False
                }
            )

            if response.status_code == 200:
                data = response.json()
                ai_message = data["message"]["content"]

                # Add AI response to chat if chat_id provided
                if hasattr(req, 'chat_id') and req.chat_id:
                    add_message_func(req.chat_id, "assistant", ai_message, len(ai_message.split()))

                return {
                    "response": ai_message,
                    "model": req.model or OLLAMA_MODEL
                }
            else:
                return {"error": f"Ollama error: {response.text}"}

    except Exception as e:
        return {"error": f"Chat failed: {str(e)}"}


# Document Q&A API endpoints
documents_dir = Path("data/documents")
documents_dir.mkdir(parents=True, exist_ok=True)

# Documents API for document QA functionality
@app.get("/api/documents")
def get_documents():
    """Get list of uploaded documents for document QA"""
    # Mock endpoint - return sample documents
    return {
        "documents": [
            {
                "id": "doc1",
                "filename": "research_paper.pdf",
                "title": "Advances in Machine Learning",
                "type": "pdf",
                "size": 2457600,
                "uploadedAt": "2024-01-15T10:30:00Z",
                "status": "processed",
                "chunkCount": 45,
            },
            {
                "id": "doc2",
                "filename": "user_manual.docx",
                "title": "System User Manual",
                "type": "docx",
                "size": 512000,
                "uploadedAt": "2024-01-14T15:20:00Z",
                "status": "processed",
                "chunkCount": 23,
            },
            {
                "id": "doc3",
                "filename": "notes.txt",
                "title": "Meeting Notes",
                "type": "txt",
                "size": 16384,
                "uploadedAt": "2024-01-13T09:15:00Z",
                "status": "processed",
                "chunkCount": 8,
            },
        ]
    }

# @app.get("/api/vector-store/health")
# def vector_store_health():
#     ...


@app.post("/api/suggest_model")
def suggest_model(data: dict):
    text = data.get("text", "").lower()
    if "code" in text or "programming" in text or "python" in text:
        return {"model": "codellama"}
    elif "research" in text or "analyze" in text or "deep" in text:
        return {"model": "llama3.1:8b"}
    else:
        return {"model": "llama3.2:latest"}


# Research endpoints
@app.post("/api/research/start")
async def start_research_endpoint(req: ResearchRequest):
    stats.increment_stat("research")
    try:
        task_id = await start_research(req.topic, req.depth)
        return {
            "task_id": task_id,
            "status": "started",
            "message": f"Research started on topic: {req.topic}",
        }
    except Exception as e:
        return {"error": f"Failed to start research: {str(e)}", "status": "error"}


@app.get("/api/research/{task_id}/status")
async def research_status(task_id: str):
    try:
        status = await get_research_status(task_id)
        return status
    except Exception as e:
        return {"task_id": task_id, "status": "error", "progress": 0, "error": str(e)}


@app.post("/api/research/{task_id}/stop")
async def stop_research_endpoint(task_id: str):
    try:
        result = await stop_research(task_id)
        return result
    except Exception as e:
        return {"task_id": task_id, "status": "error", "error": str(e)}


@app.get("/api/research/sessions")
async def list_research_sessions_endpoint():
    """List all saved research sessions."""
    try:
        return await list_research_sessions()
    except Exception as e:
        return {"sessions": [], "error": str(e)}


@app.post("/api/research/{task_id}/resume")
async def resume_research_session_endpoint(task_id: str):
    """Resume a saved research session."""
    try:
        result = await resume_research_session(task_id)
        return result
    except Exception as e:
        return {"task_id": task_id, "status": "error", "error": str(e)}


@app.delete("/api/research/{task_id}")
async def delete_research_session_endpoint(task_id: str):
    """Delete a saved research session."""
    try:
        result = delete_research_session(task_id)
        return result
    except Exception as e:
        return {"task_id": task_id, "status": "error", "error": str(e)}


@app.get("/api/agents/status")
def get_agent_status_endpoint():
    """Get current status of all agents in active research sessions."""
    try:
        return get_agent_status()
    except Exception as e:
        return {
            "status": "error",
            "active_sessions": 0,
            "agents": [],
            "error": str(e)
        }


@app.get("/api/research/{task_id}/progress")
async def research_progress_endpoint(task_id: str):
    """Stream real-time research progress using Server-Sent Events."""
    try:

        async def generate():
            async for item in research_progress(task_id):
                yield item

        return StreamingResponse(
            generate(),
            media_type="text/event-stream",
            headers={
                "Cache-Control": "no-cache",
                "Connection": "keep-alive",
                "Access-Control-Allow-Origin": "*",
                "Access-Control-Allow-Headers": "Cache-Control",
            },
        )

    except Exception as e:
        return {"error": f"Failed to subscribe to progress: {str(e)}"}


# Authentication endpoints
class LoginRequest(BaseModel):
    username: str
    password: str

class RegisterRequest(BaseModel):
    username: str
    password: str

class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"

@app.post("/api/auth/register", response_model=TokenResponse)
async def register(request: RegisterRequest):
    user_id = auth_manager.create_user(request.username, request.password)
    if not user_id:
        raise HTTPException(status_code=400, detail="Username already exists")

    user = auth_manager.authenticate_user(request.username, request.password)
    if not user:
        raise HTTPException(status_code=500, detail="Registration failed")

    access_token = auth_manager.create_access_token({"sub": user["username"], "user_id": user["id"]})
    return TokenResponse(access_token=access_token)

@app.post("/api/auth/login", response_model=TokenResponse)
async def login(request: LoginRequest):
    user = auth_manager.authenticate_user(request.username, request.password)
    if not user:
        raise HTTPException(status_code=401, detail="Invalid credentials")

    access_token = auth_manager.create_access_token({"sub": user["username"], "user_id": user["id"]})
    return TokenResponse(access_token=access_token)

@app.get("/api/auth/me")
async def get_current_user(request: Request):
    # Simple auth check - in production use proper JWT
    auth_header = request.headers.get("Authorization")
    if not auth_header or not auth_header.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Token required")

    token = auth_header.split(" ")[1]
    user = auth_manager.verify_token(token)
    if not user:
        raise HTTPException(status_code=401, detail="Invalid token")

    return user

@app.get("/api/v1/health")
def health():
    return {"status": "ok", "version": "1.0", "uptime": "unknown"}


@app.get("/api/v1/stats")
def get_stats():
    return stats.get_stats()


# RAG endpoints
@app.get("/api/rag/knowledge")
async def get_knowledge():
    return rag_service.export_knowledge()

@app.post("/api/rag/knowledge")
async def add_knowledge(data: dict):
    content = data.get("content")
    source = data.get("source", "")
    if not content:
        raise HTTPException(status_code=400, detail="Content required")
    knowledge_id = await rag_service.add_knowledge(content, source)
    return {"id": knowledge_id}

@app.post("/api/rag/maintenance")
async def run_maintenance():
    # Placeholder for maintenance
    return {"status": "maintenance completed"}


# Include routers
app.include_router(chat_router, prefix="/api/v1")
