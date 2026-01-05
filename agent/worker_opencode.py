from __future__ import annotations

import json
import os
import re
from functools import lru_cache
from typing import Any, Dict, Generator, List

import httpx

from .intelligent_tools import IntelligentToolSelector
from .models import Mode, ToolResult
from .tools.base import BaseTool


class OpenCodeWorker:
    """Worker for opencode.ai API integration with intelligent tool selection"""

    _tool_cache: dict[str, Any] = {}

    def __init__(
        self,
        model: str = "opencode-default",
        api_key: str | None = None,
        tools: list[BaseTool] | None = None,
        temperature: float = 0.7,
        max_tokens: int = 8000,
    ):
        self.model = model
        self.api_key = api_key or os.environ.get("OPENCODE_API_KEY", "")
        self.tools = tools or []
        self.temperature = temperature
        self.max_tokens = max_tokens
        self._tool_lookup: dict[str, BaseTool] = {}
        self.base_url = "https://api.opencode.ai/v1"

        for tool in self.tools:
            self._tool_lookup[tool.name] = tool

    def _get_client(self) -> httpx.Client:
        """Create HTTP client for opencode.ai API"""
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }
        return httpx.Client(base_url=self.base_url, headers=headers, timeout=120.0)

    def _analyze_request_for_tools(self, objective: str, mode: Mode) -> List[str]:
        """Intelligently analyze request to determine needed tools"""
        selector = IntelligentToolSelector(self.tools)
        return selector.select_tools(objective, mode)

    def _format_tools_for_api(
        self, selected_tools: List[BaseTool]
    ) -> List[Dict[str, Any]]:
        """Format tools for opencode.ai API"""
        tools = []
        for tool in selected_tools:
            schema = tool.get_schema()
            tools.append(
                {
                    "name": tool.name,
                    "description": tool.description,
                    "parameters": schema.get("parameters", {}),
                }
            )
        return tools

    def _execute_tool_call(self, tool_name: str, parameters: Dict[str, Any]) -> str:
        """Execute a tool call and return the result"""
        tool = self._tool_lookup.get(tool_name)
        if not tool:
            return f"Error: Tool '{tool_name}' not found"

        try:
            result = tool.execute(**parameters)
            if result.ok:
                if isinstance(result.data, str):
                    return result.data
                elif isinstance(result.data, dict):
                    return json.dumps(result.data, indent=2)
                else:
                    return str(result.data)
            else:
                return f"Error: {result.error}"
        except Exception as e:
            return f"Error executing tool '{tool_name}': {str(e)}"

    def _build_system_prompt(
        self, objective: str, mode: Mode, tools_available: List[BaseTool]
    ) -> str:
        """Build system prompt with mode-specific instructions"""
        base_instructions = f"""You are Router Phase 1, an advanced AI assistant with tool capabilities. 
Current mode: {mode.value}
Objective: {objective}

Available tools:
{self._format_tools_for_prompt(tools_available)}

When you need to use a tool, format your response with:
TOOL_CALL: {{"name": "tool_name", "parameters": {{"param": "value"}}}}

Mode-specific guidelines:
- RESEARCH: Focus on gathering information, citing sources, and verifying facts
- WRITE: Create content, generate text, compose documents
- EDIT: Revise, improve, refine existing content
- HYBRID: Balance research, writing, and analysis

Always be helpful, accurate, and use tools when they can improve your response."""

        return base_instructions

    def _format_tools_for_prompt(self, tools: List[BaseTool]) -> str:
        """Format tools for human-readable prompt"""
        if not tools:
            return "No tools available."

        tool_descriptions = []
        for tool in tools:
            schema = tool.get_schema()
            params = schema.get("parameters", {}).get("properties", {})
            required = schema.get("parameters", {}).get("required", [])

            desc = f"- {tool.name}: {tool.description}"
            if params:
                param_list = []
                for param_name, param_info in params.items():
                    param_type = param_info.get("type", "any")
                    req_mark = " (required)" if param_name in required else ""
                    param_desc = param_info.get("description", "")
                    param_list.append(
                        f"  • {param_name}: {param_type}{req_mark} - {param_desc}"
                    )
                desc += "\n" + "\n".join(param_list)

            tool_descriptions.append(desc)

        return "\n".join(tool_descriptions)

    def _extract_and_execute_tools(self, response: str) -> str:
        """Extract tool calls from response and execute them"""
        tool_pattern = re.compile(r"TOOL_CALL:\s*(\{.*?\})", re.DOTALL)

        processed_response = response

        for match in tool_pattern.finditer(response):
            try:
                tool_call = json.loads(match.group(1))
                tool_name = tool_call.get("name")
                parameters = tool_call.get("parameters", {})

                if tool_name in self._tool_lookup:
                    tool_result = self._execute_tool_call(tool_name, parameters)
                    # Replace tool call with result
                    tool_call_text = match.group(0)
                    processed_response = processed_response.replace(
                        tool_call_text, f"[Tool: {tool_name}]\n{tool_result}"
                    )
            except (json.JSONDecodeError, Exception) as e:
                # Keep original if parsing fails
                continue

        return processed_response

    def chat(self, objective: str, mode: Mode = Mode.HYBRID) -> str:
        """Process a chat message with intelligent tool selection"""
        try:
            client = self._get_client()

            # Select tools intelligently
            selected_tool_names = self._analyze_request_for_tools(objective, mode)
            selected_tools = [
                self._tool_lookup[name]
                for name in selected_tool_names
                if name in self._tool_lookup
            ]

            system_prompt = self._build_system_prompt(objective, mode, selected_tools)

            messages = [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": objective},
            ]

            payload = {
                "model": self.model,
                "messages": messages,
                "temperature": self.temperature,
                "max_tokens": self.max_tokens,
                "tools": self._format_tools_for_api(selected_tools)
                if selected_tools
                else None,
            }

            response = client.post("/chat/completions", json=payload)
            response.raise_for_status()

            data = response.json()
            content = data["choices"][0]["message"]["content"]

            # Check for tool calls in the response
            if "tool_calls" in data["choices"][0]["message"]:
                # Handle tool calls via API
                tool_calls = data["choices"][0]["message"]["tool_calls"]
                tool_results = []

                for tool_call in tool_calls:
                    tool_name = tool_call["function"]["name"]
                    try:
                        parameters = json.loads(tool_call["function"]["arguments"])
                        result = self._execute_tool_call(tool_name, parameters)
                        tool_results.append(
                            {"tool_call_id": tool_call["id"], "result": result}
                        )
                    except Exception as e:
                        tool_results.append(
                            {
                                "tool_call_id": tool_call["id"],
                                "result": f"Error: {str(e)}",
                            }
                        )

                # Send tool results back to API
                messages.append(data["choices"][0]["message"])
                for tool_result in tool_results:
                    messages.append(
                        {
                            "role": "tool",
                            "tool_call_id": tool_result["tool_call_id"],
                            "content": tool_result["result"],
                        }
                    )

                # Get final response
                final_payload = {
                    "model": self.model,
                    "messages": messages,
                    "temperature": self.temperature,
                    "max_tokens": self.max_tokens,
                }

                final_response = client.post("/chat/completions", json=final_payload)
                final_response.raise_for_status()
                final_data = final_response.json()

                return final_data["choices"][0]["message"]["content"]
            else:
                # Handle tool calls in text format
                return self._extract_and_execute_tools(content)

        except httpx.HTTPStatusError as e:
            if e.response.status_code == 401:
                return "Error: Invalid opencode.ai API key. Please check your configuration."
            elif e.response.status_code == 429:
                return "Error: Rate limit exceeded. Please try again later."
            else:
                return f"Error: {e.response.status_code} - {e.response.text}"
        except Exception as e:
            return f"Error: {str(e)}"

    def chat_stream(
        self, objective: str, mode: Mode = Mode.HYBRID
    ) -> Generator[str, None, None]:
        """Stream chat responses with tool support"""
        try:
            client = self._get_client()

            # Select tools intelligently
            selected_tool_names = self._analyze_request_for_tools(objective, mode)
            selected_tools = [
                self._tool_lookup[name]
                for name in selected_tool_names
                if name in self._tool_lookup
            ]

            system_prompt = self._build_system_prompt(objective, mode, selected_tools)

            messages = [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": objective},
            ]

            payload = {
                "model": self.model,
                "messages": messages,
                "temperature": self.temperature,
                "max_tokens": self.max_tokens,
                "stream": True,
                "tools": self._format_tools_for_api(selected_tools)
                if selected_tools
                else None,
            }

            with client.stream("POST", "/chat/completions", json=payload) as response:
                response.raise_for_status()

                full_content = ""
                for line in response.iter_lines():
                    if line:
                        try:
                            line_text = (
                                line.decode() if isinstance(line, bytes) else line
                            )
                            data = json.loads(line_text.replace("data: ", ""))
                            if data.get("choices"):
                                delta = data["choices"][0].get("delta", {})
                                if "content" in delta:
                                    chunk = delta["content"]
                                    full_content += chunk
                                    yield chunk
                        except json.JSONDecodeError:
                            continue

            # Process tool calls after streaming
            if selected_tools:
                processed_content = self._extract_and_execute_tools(full_content)
                # If tools were executed, yield the additional content
                if processed_content != full_content:
                    yield "\n\n" + processed_content[len(full_content) :]

        except Exception as e:
            yield f"\n[Error: {str(e)}]"

    def run(self, ctx) -> str:
        """Run with context object for compatibility"""
        return self.chat(ctx.objective, ctx.decision.mode)

    def cleanup(self) -> None:
        """Cleanup resources"""
        pass
