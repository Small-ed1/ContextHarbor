import asyncio
import json
import logging
import os
import re
import uuid
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List

import httpx
from fastapi import APIRouter, HTTPException
from fastapi.responses import StreamingResponse
from pydantic import BaseModel, validator

from agent.controller import Controller
from agent.tools import get_all_tools
from agent.worker_ollama import OllamaWorker

from .. import stats

router = APIRouter()

logger = logging.getLogger(__name__)

OLLAMA_HOST = os.environ.get("OLLAMA_HOST", "http://127.0.0.1:11434").rstrip("/")


async def stream_ollama_chat(payload: Dict[str, Any]):
    """Stream chat responses from Ollama"""
    payload["stream"] = True
    try:
        async with httpx.AsyncClient(timeout=60.0) as client:
            async with client.stream(
                "POST", f"{OLLAMA_HOST}/api/chat", json=payload
            ) as response:
                response.raise_for_status()
                async for line in response.aiter_lines():
                    if line.strip():
                        try:
                            data = json.loads(line)
                            if "message" in data and "content" in data["message"]:
                                yield f"data: {json.dumps({'content': data['message']['content']})}\n\n"
                            elif data.get("done", False):
                                yield f"data: {json.dumps({'done': True})}\n\n"
                                break
                        except json.JSONDecodeError:
                            continue
    except Exception as e:
        yield f"data: {json.dumps({'error': str(e)})}\n\n"


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
    history: List[Dict[str, str]] = []  # Conversation history
    stream: bool = False  # Enable streaming responses

    @validator("message")
    def validate_message(cls, v):
        if not v.strip():
            raise ValueError("Message cannot be empty")
        # Basic sanitization: remove excessive whitespace, limit length
        import re

        v = re.sub(r"\s+", " ", v.strip())
        if len(v) > 10000:
            raise ValueError("Message too long (max 10000 characters)")
        return v

    @validator("temperature")
    def temperature_range(cls, v):
        if v is not None and not (0.0 <= v <= 2.0):
            raise ValueError("Temperature must be between 0.0 and 2.0")
        return v


@router.get("/models")
def get_models():
    """Get available Ollama models"""
    try:
        response = httpx.get(f"{OLLAMA_HOST}/api/tags", timeout=10)
        data = response.json()
        models = data.get("models", [])

        # Add placeholder models to show opencode option
        models.append({"name": "opencode-gpt4", "provider": "opencode", "type": "api"})

        return models
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch models: {str(e)}")


@router.post("/chat")
async def api_chat(req: ChatRequest):
    """Process chat messages and research queries.

    Supports both regular chat mode using Ollama models and research mode
    with multi-agent systems for comprehensive analysis.
    """
    stats.increment_stat("chats")
    logger.info(
        f"Chat request: mode={req.mode}, model={req.model}, message_length={len(req.message)}"
    )
    try:
        # Handle research mode
        if req.mode == "research" or req.task == "research":
            # Import research components
            from agent.ollama_client import OllamaConfig
            from agent.research.multi_agent_system import MultiAgentSystem
            from agent.research.research_orchestrator import \
                ResearchOrchestrator
            from utils.memory_manager import MemoryManager

            # Initialize components
            memory_manager = MemoryManager()
            ollama_config = OllamaConfig(default_model=req.model or "llama3.2:latest")
            multi_agent_system = MultiAgentSystem(memory_manager, ollama_config)
            orchestrator = ResearchOrchestrator(
                multi_agent_system, None, memory_manager
            )

            # Initialize the multi-agent system and start memory monitoring
            await multi_agent_system.initialize_system(num_workers=2)
            await memory_manager.start_monitoring()

            # Create and execute research plan
            logger.info(f"Starting research for query: {req.message}")
            plan_id = await orchestrator.create_research_plan(
                title=f"Research: {req.message}",
                description=f"Research query: {req.message}",
                time_budget_hours=1.0,  # Shorter for chat-based research
            )

            # Execute synchronously for now (could be async)
            success = await orchestrator.execute_research_plan(plan_id)
            logger.info(f"Research plan {plan_id} execution success: {success}")

            if success:
                status = await orchestrator.get_research_status(plan_id)
                progress = status.get("progress", {})
                findings_count = progress.get("findings_count", 0)
                return {
                    "response": (
                        f"Research completed successfully. Found {findings_count} key "
                        f"findings across {len(status.get('topics', []))} topics."
                    ),
                    "research_id": plan_id,
                    "findings_count": findings_count,
                }
            else:
                return {"response": "Research failed to complete successfully."}

        # Regular chat mode - use Ollama directly for simple chat
        # Try to import OpenCodeWorker (may fail if dependencies missing)
        OpenCodeWorker = None  # type: ignore
        try:
            from agent.worker_opencode import OpenCodeWorker  # type: ignore
        except ImportError:
            pass

        # Select worker based on model
        if req.model and "opencode" in req.model:
            if OpenCodeWorker:
                worker = OpenCodeWorker()
                logger.info(f"Processing chat with OpenCode model {req.model}")
                controller = Controller(worker)
                loop = asyncio.get_event_loop()
                result = await loop.run_in_executor(
                    None, controller.run, req.message, req.project
                )
            else:
                raise HTTPException(
                    status_code=400, detail="OpenCode worker not available"
                )
        else:
            # Direct Ollama chat for better control and simpler responses
            import httpx

            model = req.model or "llama3.2:latest"
            temperature = req.temperature or 0.7
            logger.info(f"Processing direct chat with Ollama model {model}")

            # Prepare messages for chat API
            messages = []
            if req.history:
                messages.extend(req.history)
            messages.append({"role": "user", "content": req.message})

            payload = {
                "model": model,
                "messages": messages,
                "stream": False,
                "options": {
                    "temperature": temperature,
                    "num_ctx": req.contextTokens or 8000,
                },
            }

            try:
                if req.stream:
                    # Streaming response
                    return StreamingResponse(
                        stream_ollama_chat(payload), media_type="text/plain"
                    )
                else:
                    # Regular response
                    async with httpx.AsyncClient(timeout=60.0) as client:
                        response = await client.post(
                            f"{OLLAMA_HOST}/api/chat", json=payload
                        )
                        response.raise_for_status()
                        data = response.json()
                        result = data.get("message", {}).get(
                            "content", "No response from model"
                        )
            except Exception as e:
                logger.error(f"Ollama chat error: {e}")
                raise HTTPException(status_code=500, detail=f"Ollama error: {str(e)}")

        logger.info(f"Chat response generated, length: {len(result)}")
        return {
            "response": result,
            "model": req.model or "llama3.2:latest",
            "temperature": req.temperature or 0.7,
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/health")
async def health():
    """Health check endpoint"""
    try:
        # Check Ollama connectivity
        async with httpx.AsyncClient(timeout=5.0) as client:
            response = await client.get(f"{OLLAMA_HOST}/api/tags")
            if response.status_code == 200:
                ollama_status = "connected"
                data = response.json()
                model_count = len(data.get("models", []))
            else:
                ollama_status = "error"
                model_count = 0
    except Exception:
        ollama_status = "disconnected"
        model_count = 0

    return {
        "status": "ok",
        "ollama": ollama_status,
        "available_models": model_count,
        "timestamp": datetime.now().isoformat(),
    }
