from __future__ import annotations

import json
import re
from functools import lru_cache
from typing import Any, Generator

import httpx

from .config import OLLAMA_HOST, OLLAMA_MODEL
from .models import Mode

TOOL_CALL_PATTERN = re.compile(r"TOOL_CALL:\s*(\{.*?\})", re.DOTALL)
TOOL_CALL_ALT_PATTERN = re.compile(r"TOOL_CALL:\s*(\w+):\s*(\{.*?\})", re.DOTALL)
TOOL_CALL_MULTIPLE_PATTERN = re.compile(r"TOOL_CALL:\s*(\{.*?\})", re.DOTALL)

_TOOL_INFO_KEYWORDS = frozenset(
    (
        "find",
        "search",
        "lookup",
        "check",
        "read",
        "list",
        "what",
        "how",
        "when",
        "where",
        "who",
        "analyze",
    )
)

_CLIENTS: dict[str, httpx.Client] = {}


def _get_client(host: str) -> httpx.Client:
    if host not in _CLIENTS:
        _CLIENTS[host] = httpx.Client(timeout=120.0)
    return _CLIENTS[host]


def _cleanup_client(host: str) -> None:
    """Close and remove HTTP client for a specific host."""
    if host in _CLIENTS:
        try:
            _CLIENTS[host].close()
        except Exception:
            pass  # Ignore cleanup errors
        finally:
            del _CLIENTS[host]


def _cleanup_all_clients() -> None:
    """Close all HTTP clients and clear the cache."""
    for host in list(_CLIENTS.keys()):
        _cleanup_client(host)


def _get_client_with_limit(host: str, max_clients: int = 10) -> httpx.Client:
    """Get client with automatic cleanup when too many clients are cached."""
    if len(_CLIENTS) >= max_clients:
        # Remove the oldest client (simple LRU)
        oldest_host = next(iter(_CLIENTS))
        _cleanup_client(oldest_host)

    return _get_client(host)


class OllamaWorker:
    _tool_cache: dict[str, Any] = {}

    def __init__(
        self,
        model: str | None = None,
        host: str | None = None,
        tools: list[Any] | None = None,
        streaming: bool = True,
        temperature: float = 0.7,
        num_ctx: int = 8000,
    ):
        self.model = model or OLLAMA_MODEL
        self.host = (host or OLLAMA_HOST).rstrip("/")
        self.tools = tools or []
        self.streaming = streaming
        self.temperature = temperature
        self.num_ctx = num_ctx
        self._tool_lookup: dict[str, Any] = {}

        for tool in self.tools:
            self._tool_lookup[tool.name] = tool

    def _chat(
        self, model: str, messages: list[dict[str, str]], stream: bool = False
    ) -> str:
        prompt = messages[-1]["content"]
        payload = {
            "model": model,
            "prompt": prompt,
            "stream": stream,
            "options": {"temperature": self.temperature, "num_ctx": self.num_ctx},
        }
        client = _get_client_with_limit(self.host)

        # Retry logic for network errors
        max_retries = 3
        for attempt in range(max_retries):
            try:
                if stream:
                    response = client.post(f"{self.host}/api/generate", json=payload)
                    response.raise_for_status()
                    full_response = ""
                    for line_num, line in enumerate(response.iter_lines(), 1):
                        if line:
                            try:
                                data = json.loads(line)
                                if "response" in data:
                                    full_response += data["response"]
                                elif "error" in data:
                                    # Handle error responses from Ollama
                                    raise RuntimeError(f"Ollama API error: {data['error']}")
                            except json.JSONDecodeError as e:
                                # Log the problematic line for debugging
                                print(
                                    f"Warning: JSON decode error on line {line_num}: {line[:100]}..."
                                )
                                continue
                            except Exception as e:
                                # Re-raise non-JSON errors
                                raise
                    return full_response.strip()
                else:
                    r = client.post(f"{self.host}/api/generate", json=payload)
                    r.raise_for_status()
                    data = r.json()
                    return data.get("response", "").strip()
            except Exception as e:
                if attempt == max_retries - 1:
                    # Last attempt failed
                    raise RuntimeError(f"Ollama request failed after {max_retries} attempts: {str(e)}")
                # Wait before retry (exponential backoff)
                import time
                time.sleep(1 * (2 ** attempt))
        # This should never be reached
        raise RuntimeError("All retry attempts failed")

    def _chat_stream(
        self, model: str, messages: list[dict[str, str]]
    ) -> Generator[str, None, None]:
        prompt = messages[-1]["content"]
        payload = {
            "model": model,
            "prompt": prompt,
            "stream": True,
            "options": {"temperature": self.temperature, "num_ctx": self.num_ctx},
        }
        client = _get_client_with_limit(self.host)
        response = client.post(f"{self.host}/api/generate", json=payload)
        response.raise_for_status()
        for line_num, line in enumerate(response.iter_lines(), 1):
            if line:
                try:
                    data = json.loads(line)
                    if "response" in data:
                        yield data["response"]
                    elif "error" in data:
                        # Handle error responses from Ollama
                        yield f"\n[Error: {data['error']}]"
                        break
                except json.JSONDecodeError as e:
                    # Log the problematic line for debugging but continue streaming
                    print(
                        f"Warning: JSON decode error on line {line_num}: {line[:100]}..."
                    )
                    continue
                except Exception as e:
                    # Re-raise non-JSON errors
                    yield f"\n[Streaming error: {str(e)}]"
                    break

    def _extract_tool_call(self, response: str) -> dict | None:
        """Extract a single tool call from response (legacy compatibility)"""
        calls = self._extract_tool_calls(response)
        return calls[0] if calls else None

    def _extract_tool_calls(self, response: str) -> list[dict]:
        """Extract all tool calls from response"""
        calls = []

        # Try primary format first: TOOL_CALL: {"name": "...", "parameters": {...}}
        matches = TOOL_CALL_MULTIPLE_PATTERN.finditer(response)
        for match in matches:
            try:
                json_str = match.group(1).strip()
                # Fix common JSON issues
                json_str = self._clean_json_string(json_str)

                data = json.loads(json_str)
                if "name" in data and "parameters" in data:
                    calls.append(data)
                elif data and isinstance(data, dict):
                    # Try to infer structure
                    if "name" not in data:
                        # If no name but has parameters, assume unknown tool
                        calls.append({"name": "unknown", "parameters": data})
                    else:
                        # If name but no parameters, add empty parameters
                        if "parameters" not in data:
                            data["parameters"] = {}
                        calls.append(data)
            except json.JSONDecodeError as e:
                # Try alternative format parsing
                continue

        # Try alternative format: TOOL_CALL: tool_name: {parameters}
        alt_matches = TOOL_CALL_ALT_PATTERN.finditer(response)
        for match in alt_matches:
            tool_name = match.group(1)
            params_str = match.group(2)
            try:
                params_str = self._clean_json_string(params_str)
                params = json.loads(params_str)
                calls.append({"name": tool_name, "parameters": params})
            except json.JSONDecodeError:
                continue

        return calls

    def _clean_json_string(self, json_str: str) -> str:
        """Clean common JSON formatting issues"""
        # Remove trailing commas
        json_str = re.sub(r",\s*}", "}", json_str)
        json_str = re.sub(r",\s*]", "]", json_str)

        # Fix quotes
        json_str = re.sub(r"'([^']*)'", r'"\1"', json_str)

        # Remove any non-JSON wrapper characters
        json_str = json_str.strip()
        if json_str.startswith("```"):
            json_str = json_str[3:]
        if json_str.endswith("```"):
            json_str = json_str[:-3]
        json_str = json_str.strip("`").strip()

        return json_str

    def _execute_tool_call(self, tool_call: dict, ctx) -> str | None:
        """Execute a single tool call with error handling"""
        tool_name = tool_call.get("name")
        parameters = tool_call.get("parameters", {})

        if not tool_name:
            return "Error: Tool call missing 'name' field"

        # Validate tool name
        if tool_name == "unknown":
            return f"Error: Unknown tool call with parameters: {parameters}"

        # Get tool
        tool = self._tool_lookup.get(tool_name)
        if not tool:
            available_tools = list(self._tool_lookup.keys())
            return f"Error: Tool '{tool_name}' not found. Available tools: {available_tools}"

        # Validate parameters against tool schema
        validation_error = self._validate_tool_parameters(tool, parameters)
        if validation_error:
            return f"Error: {validation_error}"

        try:
            result = tool.execute(**parameters)

            if result.ok:
                # Format successful result
                result_text = f"Tool '{tool_name}' executed successfully"
                if result.data is not None:
                    result_text += f": {result.data}"

                # Include sources if any
                if result.sources:
                    result_text += f"\nSources found: {len(result.sources)}"

                return result_text
            else:
                return f"Tool '{tool_name}' failed: {result.error}"

        except Exception as e:
            return f"Tool '{tool_name}' crashed: {str(e)}"

    def _validate_tool_parameters(self, tool, parameters: dict) -> str | None:
        """Validate tool parameters against its schema"""
        try:
            schema = tool.get_schema()
            params_schema = schema.get("parameters", {})
            required = params_schema.get("required", [])
            properties = params_schema.get("properties", {})

            # Check required parameters
            for param in required:
                if param not in parameters:
                    return (
                        f"Missing required parameter '{param}' for tool '{tool.name}'"
                    )

            # Check parameter types (basic validation)
            for param_name, param_value in parameters.items():
                if param_name in properties:
                    expected_type = properties[param_name].get("type")
                    if expected_type and not self._check_type(
                        param_value, expected_type
                    ):
                        return f"Parameter '{param_name}' should be {expected_type}, got {type(param_value).__name__}"

            return None

        except Exception:
            # If validation fails, don't block execution
            return None

    def _check_type(self, value: Any, expected_type: str) -> bool:
        """Basic type checking for parameters"""
        type_mapping = {
            "string": str,
            "integer": int,
            "number": (int, float),
            "boolean": bool,
            "array": list,
            "object": dict,
        }

        expected_python_type = type_mapping.get(expected_type)
        if expected_python_type is not None:
            return isinstance(value, expected_python_type)  # type: ignore

        return True

    def _should_include_tools(self, objective: str, mode: Mode) -> bool:
        if mode == Mode.RESEARCH:
            return True
        query_lower = objective.lower() if objective else ""
        return any(keyword in query_lower for keyword in _TOOL_INFO_KEYWORDS)

    def _format_tool_for_prompt(self, tool) -> str:
        schema = tool.get_schema()
        params = schema.get("parameters", {})
        props = params.get("properties", {})
        required = params.get("required", [])

        lines = [f"- {tool.name}: {tool.description}"]
        if props:
            for param_name, param_info in props.items():
                param_type = param_info.get("type", "any")
                desc = param_info.get("description", "")
                default = param_info.get("default")
                required_mark = " (required)" if param_name in required else ""
                default_str = f" (default: {default})" if default is not None else ""
                lines.append(
                    f"    - {param_name}: {param_type}{required_mark}{default_str}"
                )
                if desc:
                    lines.append(f"      {desc}")
        return "\n".join(lines)

    @lru_cache(maxsize=32)
    def _build_system_prompt(self, objective: str, mode: Mode, has_tools: bool) -> str:
        tool_descriptions = ""
        if has_tools and self._should_include_tools(objective, mode):
            tool_descriptions = "\n\nAvailable tools:\n" + "\n".join(
                [self._format_tool_for_prompt(tool) for tool in self.tools]
            )
            tool_descriptions += (
                "\n\nTo use a tool, respond with: "
                'TOOL_CALL: {"name": "tool_name", "parameters": {"param_name": "param_value"}}'
                "\nYou can make multiple tool calls in one response, each on a new line starting with TOOL_CALL:"
            )

        mode_prompts = {
            Mode.RESEARCH: f"You are in RESEARCH mode. Use provided sources. Cite with [1], [2].{tool_descriptions}",
            Mode.HYBRID: f"You are in HYBRID mode. Balance research and writing.{tool_descriptions}",
            Mode.EDIT: f"You are in EDIT mode. Produce revised text only.{tool_descriptions}",
            Mode.WRITE: f"You are in WRITE mode. Write clearly.{tool_descriptions}",
        }
        return mode_prompts.get(mode, mode_prompts[Mode.WRITE])

    def run(self, ctx) -> str:
        mode = ctx.decision.mode
        base: list[dict[str, str]] = [
            {"role": x.role, "content": x.content} for x in ctx.messages
        ]

        sys_prompt = self._build_system_prompt(ctx.objective, mode, bool(self.tools))
        messages = base + [
            {"role": "system", "content": sys_prompt},
            {"role": "user", "content": ctx.objective},
        ]
        response = self._chat(self.model, messages, stream=self.streaming)

        # Handle multiple tool calls
        tool_calls = self._extract_tool_calls(response)
        if tool_calls:
            messages.append({"role": "assistant", "content": response})

            # Execute each tool call
            tool_results = []
            for i, tool_call in enumerate(tool_calls):
                tool_result = self._execute_tool_call(tool_call, ctx)
                if tool_result:
                    tool_results.append(f"Tool call {i+1}: {tool_result}")

            if tool_results:
                # Send all results back to LLM
                combined_results = "\n".join(tool_results)
                messages.append(
                    {
                        "role": "system",
                        "content": f"Tool execution results:\n{combined_results}",
                    }
                )
                response = self._chat(self.model, messages, stream=self.streaming)

        return response

    def run_with_sources(self, ctx, system_prompt: str) -> str:
        messages = [{"role": "system", "content": system_prompt}]

        if ctx.sources:
            sources_info = "Sources gathered:\n"
            for source in ctx.sources:
                idx = ctx.citation_map.get(source.source_id, 0)
                if idx:
                    sources_info += (
                        f"[{idx}] {source.title}: {source.snippet[:200]}...\n"
                    )
            messages.append(
                {"role": "user", "content": f"{ctx.objective}\n\n{sources_info}"}
            )

            messages.append(
                {
                    "role": "system",
                    "content": "Generate a comprehensive answer citing sources inline with [n] notation.",
                }
            )

        response = self._chat(self.model, messages, stream=self.streaming)
        return response

    def cleanup(self) -> None:
        """Clean up resources used by this worker."""
        _cleanup_client(self.host)

    def run_stream(self, ctx) -> Generator[str, None, None]:
        mode = ctx.decision.mode
        base: list[dict[str, str]] = [
            {"role": x.role, "content": x.content} for x in ctx.messages
        ]

        sys_prompt = self._build_system_prompt(ctx.objective, mode, bool(self.tools))
        messages = base + [
            {"role": "system", "content": sys_prompt},
            {"role": "user", "content": ctx.objective},
        ]

        for chunk in self._chat_stream(self.model, messages):
            yield chunk
