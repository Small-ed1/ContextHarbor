"""
Ollama Client for Local LLM Integration
Provides comprehensive interface to Ollama with model management and health monitoring.
"""

import asyncio
import json
import logging
import time
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, AsyncGenerator, Dict, List, Optional, Union

import aiohttp


@dataclass
class OllamaConfig:
    """Configuration for Ollama integration."""

    base_url: str = "http://localhost:11434"
    default_model: str = "llama3.2:3b"
    large_model: str = "llama3.1:8b"
    small_model: str = "llama3.2:1b"
    temperature: float = 0.7
    max_tokens: int = 4096
    context_window: int = 32768
    timeout: int = 300
    max_retries: int = 3
    retry_delay: float = 1.0


@dataclass
class GenerationRequest:
    """Request structure for LLM generation."""

    prompt: str
    system_prompt: Optional[str] = None
    context: Optional[List[Dict[str, str]]] = None
    temperature: Optional[float] = None
    max_tokens: Optional[int] = None
    stream: bool = False
    model: Optional[str] = None


@dataclass
class GenerationResponse:
    """Response structure from LLM."""

    text: str
    usage: Dict[str, int]
    model: str
    finish_reason: str
    generated_at: datetime
    total_time: float = 0.0


@dataclass
class ModelInfo:
    """Information about an Ollama model."""

    name: str
    size: int
    size_vram: int
    digest: str
    details: Dict[str, Any]
    modified_at: datetime


class OllamaClient:
    """Advanced Ollama client with model management, health monitoring, and error handling."""

    def __init__(self, config: OllamaConfig):
        self.config = config
        self.session: Optional[aiohttp.ClientSession] = None
        self.logger = logging.getLogger(__name__)
        self.available_models: Dict[str, ModelInfo] = {}
        self.model_performance: Dict[str, List[float]] = {}  # Response times

    async def __aenter__(self):
        timeout = aiohttp.ClientTimeout(total=self.config.timeout)
        self.session = aiohttp.ClientSession(timeout=timeout)
        await self._load_available_models()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.session:
            await self.session.close()

    async def generate(self, request: GenerationRequest) -> GenerationResponse:
        """Generate text using Ollama with comprehensive error handling."""

        model = request.model or self.config.default_model
        start_time = time.time()

        # Prepare payload
        payload = {
            "model": model,
            "prompt": request.prompt,
            "stream": request.stream,
            "options": {
                "temperature": request.temperature or self.config.temperature,
                "num_predict": request.max_tokens or self.config.max_tokens,
                "num_ctx": self.config.context_window,
            },
        }

        if request.system_prompt:
            payload["system"] = request.system_prompt

        # Retry logic
        for attempt in range(self.config.max_retries):
            try:
                assert self.session is not None, "Session not initialized"
                async with self.session.post(
                    f"{self.config.base_url}/api/generate", json=payload
                ) as response:
                    if response.status != 200:
                        error_text = await response.text()
                        if attempt == self.config.max_retries - 1:
                            raise OllamaError(
                                f"API error {response.status}: {error_text}"
                            )
                        await asyncio.sleep(self.config.retry_delay * (2**attempt))
                        continue

                    if request.stream:
                        result = await self._handle_stream_response(response)
                    else:
                        result = await self._handle_single_response(response)

                    # Track performance
                    response_time = time.time() - start_time
                    self._track_performance(model, response_time)
                    result.total_time = response_time

                    return result

            except aiohttp.ClientError as e:
                if attempt == self.config.max_retries - 1:
                    raise OllamaConnectionError(
                        f"Failed to connect to Ollama after {self.config.max_retries} attempts: {e}"
                    )
                await asyncio.sleep(self.config.retry_delay * (2**attempt))

        raise OllamaError("All retry attempts failed")

    async def _handle_stream_response(
        self, response: aiohttp.ClientResponse
    ) -> GenerationResponse:
        """Handle streaming response from Ollama."""
        full_text = ""
        usage = {"prompt_tokens": 0, "completion_tokens": 0, "total_tokens": 0}

        async for line_bytes in response.content:
            line = line_bytes.decode("utf-8").strip()
            if not line:
                continue

            try:
                data = json.loads(line)

                if "response" in data:
                    full_text += data["response"]
                    # In a real implementation, you'd yield tokens here for streaming

                if data.get("done", False):
                    usage = {
                        "prompt_tokens": data.get("prompt_eval_count", 0),
                        "completion_tokens": data.get("eval_count", 0),
                        "total_tokens": data.get("prompt_eval_count", 0)
                        + data.get("eval_count", 0),
                    }
                    break

            except json.JSONDecodeError:
                continue

        return GenerationResponse(
            text=full_text,
            usage=usage,
            model=self.config.default_model,
            finish_reason="stop",
            generated_at=datetime.now(),
        )

    async def _handle_single_response(
        self, response: aiohttp.ClientResponse
    ) -> GenerationResponse:
        """Handle single response from Ollama."""
        data = await response.json()

        return GenerationResponse(
            text=data.get("response", ""),
            usage={
                "prompt_tokens": data.get("prompt_eval_count", 0),
                "completion_tokens": data.get("eval_count", 0),
                "total_tokens": data.get("prompt_eval_count", 0)
                + data.get("eval_count", 0),
            },
            model=self.config.default_model,
            finish_reason="stop",
            generated_at=datetime.now(),
        )

    async def _load_available_models(self):
        """Load information about available Ollama models."""
        try:
            assert self.session is not None, "Session not initialized"
            async with self.session.get(f"{self.config.base_url}/api/tags") as response:
                if response.status == 200:
                    data = await response.json()
                    for model_data in data.get("models", []):
                        model_info = ModelInfo(
                            name=model_data["name"],
                            size=model_data.get("size", 0),
                            size_vram=model_data.get("size_vram", 0),
                            digest=model_data.get("digest", ""),
                            details=model_data.get("details", {}),
                            modified_at=datetime.fromisoformat(
                                model_data.get(
                                    "modified_at", datetime.now().isoformat()
                                )
                            ),
                        )
                        self.available_models[model_info.name] = model_info
                else:
                    self.logger.warning(
                        f"Failed to load models: HTTP {response.status}"
                    )
        except Exception as e:
            self.logger.error(f"Error loading available models: {e}")

    def get_optimal_model(self, task_complexity: str, available_memory_mb: int) -> str:
        """Select the optimal model based on task complexity and available memory."""

        # Model memory requirements (approximate)
        model_memory = {
            "llama3.2:1b": 2 * 1024,  # 2GB
            "llama3.2:3b": 6 * 1024,  # 6GB
            "llama3.1:8b": 16 * 1024,  # 16GB
        }

        # Select model based on complexity and memory
        if (
            task_complexity == "simple"
            and available_memory_mb > model_memory["llama3.2:1b"]
        ):
            return self.config.small_model
        elif (
            task_complexity == "moderate"
            and available_memory_mb > model_memory["llama3.2:3b"]
        ):
            return self.config.default_model
        elif (
            task_complexity == "complex"
            and available_memory_mb > model_memory["llama3.1:8b"]
        ):
            return self.config.large_model
        else:
            # Fallback to smallest available model
            return self.config.small_model

    def _track_performance(self, model: str, response_time: float):
        """Track model performance metrics."""
        if model not in self.model_performance:
            self.model_performance[model] = []

        self.model_performance[model].append(response_time)

        # Keep only last 100 measurements
        if len(self.model_performance[model]) > 100:
            self.model_performance[model].pop(0)

    def get_performance_stats(self, model: str) -> Dict[str, float]:
        """Get performance statistics for a model."""
        if model not in self.model_performance:
            return {}

        times = self.model_performance[model]
        if not times:
            return {}

        return {
            "avg_response_time": sum(times) / len(times),
            "min_response_time": min(times),
            "max_response_time": max(times),
            "sample_count": len(times),
        }

    async def check_health(self) -> bool:
        """Check if Ollama service is healthy."""
        try:
            assert self.session is not None, "Session not initialized"
            async with self.session.get(f"{self.config.base_url}/api/tags") as response:
                return response.status == 200
        except Exception:
            return False

    async def list_models(self) -> List[str]:
        """List available Ollama models."""
        await self._load_available_models()  # Refresh
        return list(self.available_models.keys())

    async def get_model_info(self, model_name: str) -> Optional[ModelInfo]:
        """Get detailed information about a specific model."""
        await self._load_available_models()  # Refresh
        return self.available_models.get(model_name)

    async def unload_model(self, model: str) -> bool:
        """Unload a model from memory to free up RAM."""
        try:
            assert self.session is not None, "Session not initialized"
            async with self.session.post(
                f"{self.config.base_url}/api/generate",
                json={"model": model, "keep_alive": 0},
            ) as response:
                return response.status == 200
        except Exception as e:
            self.logger.error(f"Error unloading model {model}: {e}")
            return False


class OllamaError(Exception):
    """Base exception for Ollama-related errors."""

    pass


class OllamaConnectionError(OllamaError):
    """Exception for connection-related errors."""

    pass
