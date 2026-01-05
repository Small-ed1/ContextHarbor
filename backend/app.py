from __future__ import annotations

import asyncio
import json
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
    np = None

import httpx
from fastapi import APIRouter, FastAPI, HTTPException, Request, File, UploadFile
from fastapi.responses import (FileResponse, HTMLResponse, JSONResponse,
                               StreamingResponse)
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

# Chat API routes
from .routes.chat import router as chat_router

# Document Q&A imports - temporarily disabled for basic server startup
# try:
#     from utils.document_processor import DocumentProcessingPipeline, DocumentMetadata
#     from utils.embedding_service import EmbeddingService, DocumentEmbeddingService, EmbeddingConfig
#     from utils.vector_store import VectorStoreManager, VectorStoreConfig
#     DOCUMENT_PROCESSING_AVAILABLE = True
# except ImportError:
DOCUMENT_PROCESSING_AVAILABLE = False

APP_TITLE = "Router Phase 1"
OLLAMA_HOST = os.environ.get("OLLAMA_HOST", "http://127.0.0.1:11434").rstrip("/")
OLLAMA_MODEL = os.environ.get("OLLAMA_MODEL", "llama3.2:1b")

app = FastAPI(title=APP_TITLE)
app.mount("/static", StaticFiles(directory="backend/static"), name="static")


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


class ResearchRequest(BaseModel):
    topic: str
    depth: str = "standard"
    project: str = "default"


MEMORIES_PATH = Path("memories.json")
chats_dir = Path("chats")
archived_dir = Path("chats/archived")
MEMORIES_PATH = Path("projects/default/memories.json")

_CONFIG_CACHE: dict[str, Any] = {}
_CONFIG_MTIME: float = 0
_CONFIG_LOCK = threading.RLock()
_CHAT_METADATA_CACHE: dict[str, dict[str, Any]] = {}
_CHAT_CACHE_LOCK = threading.RLock()


def _get_default_config() -> dict[str, Any]:
    return {
        "theme": "dark",
        "accent": "#007bff",
        "temperature": 0.7,
        "contextTokens": 8000,
        "defaultModel": "",
        "defaultTask": "chat",
        "showArchived": False,
        "autoModelSwitch": False,
        "autoModelSwitchMode": "suggest",
        "citationFormat": "inline",
        "maxToolCalls": 10,
        "researchDepth": "standard",
        "enableStreaming": True,
        "debugMode": False,
        "fontSize": "medium",
        "animations": True,
        "memoryLimit": 10,
    }


def _load_config() -> dict[str, Any]:
    global _CONFIG_CACHE, _CONFIG_MTIME
    with _CONFIG_LOCK:
        config_path = Path("router.json")
        try:
            mtime = config_path.stat().st_mtime
            if mtime > _CONFIG_MTIME:
                with open(config_path) as f:
                    _CONFIG_CACHE = json.load(f)
                _CONFIG_MTIME = mtime
            return (
                _CONFIG_CACHE.copy()
            )  # Return a copy to prevent external modifications
        except Exception:
            return _get_default_config()


def _save_config(data: dict[str, Any]):
    global _CONFIG_CACHE, _CONFIG_MTIME
    with _CONFIG_LOCK:
        config_path = Path("router.json")
        current = _load_config()
        current.update(data)
        with open(config_path, "w") as f:
            json.dump(current, f, indent=2)
        _CONFIG_MTIME = config_path.stat().st_mtime
        _CONFIG_CACHE = current  # Update cache with saved data


def _load_memories() -> list[dict[str, Any]]:
    if MEMORIES_PATH.exists():
        try:
            with open(MEMORIES_PATH) as f:
                return json.load(f)
        except Exception:
            pass
    return []


def _save_memories(memories: list[dict[str, Any]]):
    with open(MEMORIES_PATH, "w") as f:
        json.dump(memories, f, indent=2)


# Reusable HTTP client for Ollama API calls
_OLLAMA_CLIENT = None


def _get_ollama_client() -> httpx.Client:
    global _OLLAMA_CLIENT
    if _OLLAMA_CLIENT is None:
        _OLLAMA_CLIENT = httpx.Client(timeout=5.0)
    return _OLLAMA_CLIENT


def _get_ollama_models() -> list[str]:
    try:
        client = _get_ollama_client()
        response = client.get(f"{OLLAMA_HOST}/api/tags")
        if response.status_code == 200:
            data = response.json()
            return [model["name"] for model in data.get("models", [])]
    except Exception:
        pass
    return ["llama3.2:latest"]


def _get_all_models() -> list[dict[str, str]]:
    """Get all available models including opencode.ai"""
    models = []

    # Add Ollama models
    ollama_models = _get_ollama_models()
    for model in ollama_models:
        models.append({"name": model, "provider": "ollama", "type": "local"})

    # Add opencode.ai models
    opencode_key = os.environ.get("OPENCODE_API_KEY")
    if opencode_key:
        try:
            # Try to fetch available models from opencode.ai
            with httpx.Client(timeout=5.0) as client:
                headers = {"Authorization": f"Bearer {opencode_key}"}
                response = client.get(
                    "https://api.opencode.ai/v1/models", headers=headers
                )
                if response.status_code == 200:
                    data = response.json()
                    for model in data.get("data", []):
                        models.append(
                            {"name": model["id"], "provider": "opencode", "type": "api"}
                        )
        except Exception:
            # Fallback to default opencode models
            models.extend(
                [
                    {"name": "opencode-gpt4", "provider": "opencode", "type": "api"},
                    {"name": "opencode-claude", "provider": "opencode", "type": "api"},
                ]
            )
    else:
        # Add placeholder models to show opencode option
        models.append({"name": "opencode-gpt4", "provider": "opencode", "type": "api"})

    return models


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
    return _load_config()


@app.post("/api/settings")
def save_settings(data: dict):
    _save_config(data)
    return {"status": "ok"}


@app.get("/api/memories")
def get_memories():
    return _load_memories()


@app.post("/api/memories")
def add_memory(data: dict):
    memories = _load_memories()
    key = data.get("key", "")
    value = data.get("value", "")
    if key and value:
        memories = [m for m in memories if m.get("key") != key]
        memories.append({"key": key, "value": value})
        _save_memories(memories)
    return {"status": "ok"}


@app.delete("/api/memories/{key}")
def delete_memory(key: str):
    memories = _load_memories()
    memories = [m for m in memories if m.get("key") != key]
    _save_memories(memories)
    return {"status": "ok"}


@app.get("/api/models")
def get_models():
    try:
        all_models = _get_all_models()
        model_names = [model["name"] for model in all_models]
        default_model = "llama3.2:latest"

        # Prefer opencode models if available
        for model in all_models:
            if model["provider"] == "opencode":
                default_model = model["name"]
                break

        return {
            "items": model_names,
            "default": default_model,
            "providers": all_models,  # Include provider info for UI
        }
    except Exception as e:
        print(f"Error fetching models: {e}")
        return {"items": ["llama3.2:latest"], "default": "llama3.2:latest"}


@app.get("/api/chats")
def list_chats():
    with _CHAT_CACHE_LOCK:
        chats = []
        show_archived = _load_config().get("showArchived", False)
        dirs = [chats_dir] + ([archived_dir] if show_archived else [])

        for d in dirs:
            for f in d.glob("*.json"):
                chat_id = f.stem
                cache_key = f"{chat_id}:{f.stat().st_mtime}"

                # Check if cached data is still valid
                if cache_key in _CHAT_METADATA_CACHE and _CHAT_METADATA_CACHE[
                    cache_key
                ].get("archived") == (str(d) == str(archived_dir)):
                    chats.append(_CHAT_METADATA_CACHE[cache_key]["metadata"])
                    continue

                # Load and cache the chat metadata
                try:
                    with open(f) as file:
                        data = json.load(file)
                        chat_metadata = {
                            "id": chat_id,
                            "title": data.get("title", "Untitled"),
                            "created_at": data.get("created_at"),
                            "summary": data.get("summary", ""),
                            "archived": str(d) == str(archived_dir),
                        }
                        chats.append(chat_metadata)
                        _CHAT_METADATA_CACHE[cache_key] = {
                            "metadata": chat_metadata,
                            "archived": chat_metadata["archived"],
                        }
                except:
                    # Clean up cache entry for corrupted files
                    _CHAT_METADATA_CACHE.pop(cache_key, None)
                    pass

        return chats


@app.post("/api/chats")
def create_chat():
    chat_id = str(uuid.uuid4())
    chat_path = chats_dir / f"{chat_id}.json"
    data = {
        "id": chat_id,
        "title": "New Chat",
        "created_at": datetime.now().isoformat(),
        "messages": [],
    }
    with open(chat_path, "w") as f:
        json.dump(data, f, indent=2)
    return {"id": chat_id}


@app.get("/api/chats/{chat_id}")
def get_chat(chat_id: str):
    chat_path = chats_dir / f"{chat_id}.json"
    if not chat_path.exists():
        chat_path = archived_dir / f"{chat_id}.json"
    if chat_path.exists():
        with open(chat_path) as f:
            return json.load(f)
    return {"error": "Chat not found"}


@app.put("/api/chats/{chat_id}")
def update_chat(chat_id: str, data: dict):
    chat_path = chats_dir / f"{chat_id}.json"
    if not chat_path.exists():
        chat_path = archived_dir / f"{chat_id}.json"
    if chat_path.exists():
        current = json.load(open(chat_path))
        current.update(data)
        with open(chat_path, "w") as f:
            json.dump(current, f, indent=2)
        return {"status": "ok"}
    return {"error": "Chat not found"}


@app.delete("/api/chats/{chat_id}")
def delete_chat(chat_id: str):
    chat_path = chats_dir / f"{chat_id}.json"
    if chat_path.exists():
        chat_path.unlink()
        return {"status": "ok"}
    return {"error": "Chat not found"}


@app.post("/api/chats/{chat_id}/archive")
def archive_chat(chat_id: str):
    chat_path = chats_dir / f"{chat_id}.json"
    if chat_path.exists():
        archived_path = archived_dir / f"{chat_id}.json"
        chat_path.rename(archived_path)
        return {"status": "archived"}
    return {"error": "Chat not found"}


# Document Q&A API endpoints
documents_dir = Path("data/documents")
documents_dir.mkdir(parents=True, exist_ok=True)

# Temporarily disabled for basic server startup
# @app.get("/api/documents")
# def list_documents():
#     ...

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


@app.post("/api/research/start")
async def start_research(req: ResearchRequest):
    try:
        from utils.research_session_manager import research_session_manager

        task_id = await research_session_manager.start_research(req.topic, req.depth)

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
        from utils.research_session_manager import research_session_manager

        status = await research_session_manager.get_status(task_id)
        if status is None:
            return {"error": "Research session not found", "status": "not_found"}

        return status
    except Exception as e:
        return {"task_id": task_id, "status": "error", "progress": 0, "error": str(e)}


@app.post("/api/research/{task_id}/stop")
async def stop_research(task_id: str):
    try:
        from utils.research_session_manager import research_session_manager

        result = await research_session_manager.stop_research(task_id)
        return result
    except Exception as e:
        return {"task_id": task_id, "status": "error", "error": str(e)}


@app.get("/api/research/sessions")
async def list_research_sessions():
    """List all saved research sessions."""
    try:
        from utils.research_session_manager import research_session_manager

        sessions = research_session_manager.list_saved_sessions()
        return {"sessions": list(sessions.values())}
    except Exception as e:
        return {"error": f"Failed to list sessions: {str(e)}"}


@app.post("/api/research/{task_id}/resume")
async def resume_research_session(task_id: str):
    """Resume a saved research session."""
    try:
        from utils.research_session_manager import research_session_manager

        session = await research_session_manager.resume_session(task_id)
        if session:
            return {"task_id": task_id, "status": "resumed", "message": "Research session resumed"}
        else:
            return {"error": "Failed to resume session"}
    except Exception as e:
        return {"task_id": task_id, "status": "error", "error": str(e)}


@app.delete("/api/research/{task_id}")
async def delete_research_session(task_id: str):
    """Delete a saved research session."""
    try:
        from utils.research_session_manager import research_session_manager

        research_session_manager.delete_session(task_id)
        return {"task_id": task_id, "status": "deleted"}
    except Exception as e:
        return {"task_id": task_id, "status": "error", "error": str(e)}


@app.get("/api/agents/status")
def get_agent_status():
    """Get current status of all agents in active research sessions."""
    try:
        import logging
        from utils.research_session_manager import research_session_manager

        all_agents = []

        # Get agents from all active sessions
        for session in research_session_manager.sessions.values():
            if session.multi_agent_system:
                try:
                    # Get system status which includes agent information
                    status = session.multi_agent_system.get_system_status()
                    # Extract agent information
                    agents_info = []
                    for agent_id, agent in session.multi_agent_system.agents.items():
                        agents_info.append({
                            "id": agent.id,
                            "role": agent.config.role.value,
                            "model": agent.config.model,
                            "status": agent.state.value,
                            "current_task": agent.current_task.type if agent.current_task else None,
                            "performance_metrics": agent.performance_metrics,
                            "last_active": agent.last_active.isoformat() if agent.last_active else None,
                        })
                    all_agents.extend(agents_info)
                except Exception as e:
                    logging.error(f"Error getting agent status for session {session.task_id}: {e}")

        return {"agents": all_agents}
    except Exception as e:
        return {"error": f"Failed to get agent status: {str(e)}"}


@app.get("/api/research/{task_id}/progress")
async def research_progress(task_id: str):
    """Stream real-time research progress using Server-Sent Events."""
    try:
        from utils.research_session_manager import research_session_manager

        async def generate():
            try:
                queue = await research_session_manager.subscribe_progress(task_id)

                while True:
                    try:
                        # Wait for progress update
                        update = await asyncio.wait_for(queue.get(), timeout=30.0)

                        # Format as SSE
                        data = json.dumps(update)
                        yield f"data: {data}\n\n"

                        # Check if research is complete
                        if update.get("status") == "completed":
                            break

                    except asyncio.TimeoutError:
                        # Send heartbeat
                        yield "data: {\"type\": \"heartbeat\"}\n\n"
                        continue

            except Exception as e:
                error_data = json.dumps({"error": str(e), "status": "error"})
                yield f"data: {error_data}\n\n"

        return StreamingResponse(
            generate(),
            media_type="text/event-stream",
            headers={
                "Cache-Control": "no-cache",
                "Connection": "keep-alive",
                "Access-Control-Allow-Origin": "*",
                "Access-Control-Allow-Headers": "Cache-Control",
            }
        )

    except Exception as e:
        return {"error": f"Failed to subscribe to progress: {str(e)}"}


@app.get("/api/health")
def health():
    return {"status": "ok"}


# Include routers
app.include_router(chat_router, prefix="/api")
