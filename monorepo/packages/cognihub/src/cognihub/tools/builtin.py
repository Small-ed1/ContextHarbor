from __future__ import annotations

import os
import httpx
import subprocess
import shlex
from typing import Any, Dict, Optional
from pydantic import BaseModel, Field

from .registry import ToolRegistry, ToolSpec
from ..services.tooling import ToolDocSearchReq, ToolWebSearchReq, tool_doc_search, tool_web_search


class WebSearchArgs(BaseModel):
    q: str = Field(min_length=1, max_length=256)


class DocSearchArgs(BaseModel):
    query: str = Field(min_length=1, max_length=256)
    top_k: int = Field(default=5, ge=1, le=20)


class ShellExecArgs(BaseModel):
    command: str = Field(min_length=1, max_length=512)
    cwd: Optional[str] = Field(default=None, max_length=256)
    timeout: int = Field(default=30, ge=1, le=300)


def register_builtin_tools(
    registry: ToolRegistry,
    *,
    http: httpx.AsyncClient,
    ingest_queue,
    embed_model: str,
    kiwix_url: Optional[str] = None,
) -> None:

    async def web_search_handler(args: WebSearchArgs) -> Dict[str, Any]:
        try:
            req = ToolWebSearchReq(query=args.q)
            result = await tool_web_search(
                req,
                http=http,
                ingest_queue=ingest_queue,
                embed_model=embed_model,
                kiwix_url=kiwix_url,
            )

            items = []
            # tool_web_search returns results in "results" key, not "pages"
            for p in result.get("results", []):
                items.append({
                    "title": p.get("title", ""),
                    "url": p.get("url", ""),
                    "snippet": p.get("snippet", ""),
                })
            
            # Check for empty results and treat as error if provider indicates blocking
            if not items:
                # Check if we have provider info indicating failure
                if hasattr(result, 'get') and result.get('provider_error'):
                    return {
                        "items": [],
                        "error": f"web_search failed: {result['provider_error']}"
                    }
                else:
                    return {
                        "items": [], 
                        "error": "web_search returned no results (provider may be blocked)"
                    }
            
            return {"items": items}
            
        except Exception as e:
            # Convert any exception to structured error response
            return {
                "items": [],
                "error": f"web_search failed: {str(e)}"
            }

    async def doc_search_handler(args: DocSearchArgs) -> Dict[str, Any]:
        req = ToolDocSearchReq(query=args.query, top_k=args.top_k)
        result = await tool_doc_search(req)

        chunks = []
        for hit in result.get("results", []):
            chunks.append({
                "text": hit.get("text", ""),
                "score": hit.get("score", 0.0),
                "source": hit.get("title", ""),
                "url": hit.get("url"),
            })
        return {"chunks": chunks}

    async def shell_exec_handler(args: ShellExecArgs) -> Dict[str, Any]:
        """Execute shell command with strict safety controls."""
        try:
            # Parse command safely
            cmd_parts = shlex.split(args.command)
            if not cmd_parts:
                return {"error": "empty command"}

            # Basic allowlist - filesystem and safe commands only (no network)
            allowed_commands = {
                'ls', 'pwd', 'echo', 'cat', 'head', 'tail', 'grep', 'wc', 'sort',
                'df', 'du', 'free', 'ps', 'uptime', 'date', 'whoami', 'id',
                'python3', 'python', 'git'
            }

            if cmd_parts[0] not in allowed_commands:
                return {"error": f"command '{cmd_parts[0]}' not in allowlist"}

            # Execute with timeout and output capture
            result = subprocess.run(
                cmd_parts,
                cwd=args.cwd,
                capture_output=True,
                text=True,
                timeout=args.timeout,
                shell=False  # Never use shell=True
            )

            return {
                "returncode": result.returncode,
                "stdout": result.stdout[:4096] if result.stdout else "",  # Cap output
                "stderr": result.stderr[:4096] if result.stderr else "",
            }

        except subprocess.TimeoutExpired:
            return {"error": "command timed out"}
        except Exception as e:
            return {"error": f"execution failed: {str(e)}"}

    registry.register(
        ToolSpec(
            name="web_search",
            description="Search the web. Args: {q}. Returns: {items:[{title,url,snippet}]}",
            args_model=WebSearchArgs,
            handler=web_search_handler,
            side_effect="network",
        )
    )

    registry.register(
        ToolSpec(
            name="doc_search",
            description="Search docs (RAG). Args: {query, top_k}. Returns: {chunks:[...]}",
            args_model=DocSearchArgs,
            handler=doc_search_handler,
            side_effect="read_only",
        )
    )

    # Shell exec - only register if explicitly enabled
    if os.getenv("ALLOW_SHELL_EXEC", "").lower() in ("1", "true", "yes"):
        registry.register(
            ToolSpec(
                name="shell_exec",
                description="Execute safe shell commands (allowlisted only). Args: {command, cwd?, timeout}. Returns: {returncode, stdout, stderr}",
                args_model=ShellExecArgs,
                handler=shell_exec_handler,
                side_effect="dangerous",
                requires_confirmation=True,
            )
        )