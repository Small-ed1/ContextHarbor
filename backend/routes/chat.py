import json
import uuid
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List

import httpx
from fastapi import APIRouter, HTTPException
from fastapi.responses import StreamingResponse
from pydantic import BaseModel

from agent.controller import Controller
from agent.tools import get_all_tools
from agent.worker_ollama import OllamaWorker

router = APIRouter()


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


OLLAMA_HOST = "http://127.0.0.1:11434"


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
            ollama_config = OllamaConfig()
            multi_agent_system = MultiAgentSystem(memory_manager, ollama_config)
            orchestrator = ResearchOrchestrator(
                multi_agent_system, None, memory_manager
            )

            # Initialize the multi-agent system and start memory monitoring
            await multi_agent_system.initialize_system(num_workers=2)
            await memory_manager.start_monitoring()

            # Create and execute research plan
            plan_id = await orchestrator.create_research_plan(
                title=f"Research: {req.message}",
                description=f"Research query: {req.message}",
                time_budget_hours=1.0,  # Shorter for chat-based research
            )

            # Execute synchronously for now (could be async)
            success = await orchestrator.execute_research_plan(plan_id)

            if success:
                status = await orchestrator.get_research_status(plan_id)
                progress = status.get("progress", {})
                findings_count = progress.get("findings_count", 0)
                return {
                    "response": f"Research completed successfully. Found {findings_count} key findings across {len(status.get('topics', []))} topics.",
                    "research_id": plan_id,
                    "findings_count": findings_count,
                }
            else:
                return {"response": "Research failed to complete successfully."}

        # Regular chat mode
        # Try to import OpenCodeWorker (may fail if dependencies missing)
        try:
            from agent.worker_opencode import OpenCodeWorker
        except ImportError:
            OpenCodeWorker = None

        # Select worker based on model
        if req.model and "opencode" in req.model:
            if OpenCodeWorker:
                worker = OpenCodeWorker()
            else:
                raise HTTPException(
                    status_code=400, detail="OpenCode worker not available"
                )
        else:
            worker = OllamaWorker()

        controller = Controller(worker)
        result = controller.run(req.message, req.project)
        return {"response": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/health")
def health():
    return {"status": "ok"}
