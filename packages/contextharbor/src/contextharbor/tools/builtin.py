from __future__ import annotations

import asyncio
import os
import httpx
import subprocess
import shlex
from pathlib import Path
from typing import Any, Dict, Optional
from pydantic import BaseModel, Field

from .registry import ToolRegistry, ToolSpec
from .exceptions import ToolError
from ..services.tooling import (
    ToolDocSearchReq,
    ToolWebSearchReq,
    tool_doc_search,
    tool_web_search,
)
from .. import config as ch_config
from ..services.evidence import infer_epub_intent


class WebSearchArgs(BaseModel):
    q: str = Field(min_length=1, max_length=256)


class DocSearchArgs(BaseModel):
    query: str = Field(min_length=1, max_length=256)
    # Keep tool output bounded so it fits comfortably in the tool-message cap.
    top_k: int = Field(default=5, ge=1, le=8)


class LibrarySearchArgs(BaseModel):
    query: str = Field(min_length=1, max_length=256)
    limit: int = Field(default=10, ge=1, le=50)


class LocalFileReadArgs(BaseModel):
    path: str = Field(min_length=1, max_length=1024)


class KiwixSearchArgs(BaseModel):
    query: str = Field(min_length=1, max_length=256)
    top_k: int = Field(default=8, ge=1, le=25)


class ShellExecArgs(BaseModel):
    command: str = Field(min_length=1, max_length=512)
    cwd: Optional[str] = Field(default=None, max_length=1024)
    timeout: int = Field(default=30, ge=1, le=300)


class WebSearchOut(BaseModel):
    items: list[dict[str, Any]]


class DocSearchOut(BaseModel):
    class Chunk(BaseModel):
        text: str
        score: float = 0.0

        # Document identity / metadata (present when available)
        doc_id: int | None = None
        chunk_id: int | None = None
        chunk_index: int | None = None
        section: str | None = None

        source: str | None = None
        title: str | None = None
        author: str | None = None
        path: str | None = None
        filename: str | None = None

    chunks: list[Chunk]


class LibrarySearchOut(BaseModel):
    class Item(BaseModel):
        id: int
        title: str | None = None
        author: str | None = None
        path: str | None = None
        source: str | None = None
        filename: str | None = None
        chunk_count: int | None = None

    items: list[Item]


class LocalFileReadOut(BaseModel):
    path: str
    truncated: bool
    content: str


class ShellExecOut(BaseModel):
    returncode: int
    stdout: str
    stderr: str


class KiwixSearchOut(BaseModel):
    class Item(BaseModel):
        title: str
        url: str
        path: str
        snippet: str | None = None

    items: list[Item]


def register_builtin_tools(
    registry: ToolRegistry,
    *,
    http: httpx.AsyncClient,
    ingest_queue,
    embed_model: str,
    kiwix_url: Optional[str] = None,
) -> None:

    cfg = ch_config.config
    enabled = set(cfg.enabled_tools or [])

    def _cap_text(s: Any, limit: int = 900) -> str:
        out = str(s or "")
        if len(out) <= limit:
            return out
        return out[:limit] + "...(truncated)"

    async def web_search_handler(args: WebSearchArgs) -> Dict[str, Any]:
        if not cfg.search_enabled:
            raise ToolError("web search is disabled by config", code="search_disabled")

        req = ToolWebSearchReq(query=args.q)
        result = await tool_web_search(
            req,
            http=http,
            ingest_queue=ingest_queue,
            embed_model=embed_model,
            kiwix_url=kiwix_url,
        )

        items = []
        for p in result.get("results", []):
            items.append(
                {
                    "title": p.get("title", ""),
                    "url": p.get("url", ""),
                    "snippet": p.get("snippet", ""),
                }
            )

        if not items:
            provider_error = (
                result.get("provider_error") if isinstance(result, dict) else None
            )
            if provider_error:
                raise ToolError(
                    f"web search failed: {provider_error}", code="search_failed"
                )
            raise ToolError("web search returned no results", code="search_failed")

        return {"items": items}

    async def doc_search_handler(args: DocSearchArgs) -> Dict[str, Any]:
        epub_intent = infer_epub_intent(args.query)
        exclude_group_names = ["epub"] if epub_intent == "none" else None
        exclude_tags = ["fiction"] if epub_intent == "reference" else None
        req = ToolDocSearchReq(
            query=args.query,
            top_k=min(int(args.top_k), 8),
            exclude_group_names=exclude_group_names,
            exclude_tags=exclude_tags,
        )
        result = await tool_doc_search(req)

        chunks = []
        for hit in result.get("results", []):
            chunks.append(
                {
                    "text": _cap_text(hit.get("text", "")),
                    "score": float(hit.get("score", 0.0) or 0.0),
                    "doc_id": hit.get("doc_id"),
                    "chunk_id": hit.get("chunk_id"),
                    "chunk_index": hit.get("chunk_index"),
                    "section": hit.get("section"),
                    "source": hit.get("source"),
                    "title": hit.get("title"),
                    "author": hit.get("author"),
                    "path": hit.get("path"),
                    "filename": hit.get("filename"),
                }
            )
        return {"chunks": chunks}

    async def library_search_handler(args: LibrarySearchArgs) -> Dict[str, Any]:
        from ..stores import ragstore

        q = (args.query or "").strip()
        if not q:
            return {"items": []}

        docs = ragstore.search_documents(q, limit=int(args.limit))
        items = []
        for d in docs:
            items.append(
                {
                    "id": int(d.get("id") or 0),
                    "title": d.get("title"),
                    "author": d.get("author"),
                    "path": d.get("path"),
                    "source": d.get("source"),
                    "filename": d.get("filename"),
                    "chunk_count": d.get("chunk_count"),
                }
            )
        return {"items": items}

    async def kiwix_search_handler(args: KiwixSearchArgs) -> Dict[str, Any]:
        from ..services import kiwix

        base_url = (kiwix_url or "").strip()
        if not base_url:
            raise ToolError("KIWIX_URL not set", code="not_configured")

        q = (args.query or "").strip()
        if not q:
            raise ToolError("query required", code="invalid_arguments")

        hits = await kiwix.search(base_url, q, top_k=int(args.top_k))
        items = []
        for h in hits:
            if not isinstance(h, dict):
                continue
            title = str(h.get("title") or "").strip()
            url = str(h.get("url") or "").strip()
            path = str(h.get("path") or "").strip()
            if not (title and url and path):
                continue
            items.append(
                {"title": title, "url": url, "path": path, "snippet": h.get("snippet")}
            )
        return {"items": items}

    def _is_within_roots(p: Path, roots: list[str]) -> bool:
        try:
            rp = p.resolve()
        except Exception:
            return False
        for root in roots:
            try:
                rr = Path(os.path.expanduser(root)).resolve()
            except Exception:
                continue
            try:
                rp.relative_to(rr)
                return True
            except Exception:
                continue
        return False

    async def local_file_read_handler(args: LocalFileReadArgs) -> Dict[str, Any]:
        raw_path = args.path.strip()
        if not raw_path:
            raise ToolError("path is required", code="invalid_args")

        p = Path(os.path.expanduser(raw_path))
        roots = cfg.local_file_roots or []
        if not roots:
            raise ToolError(
                "local_file_read has no configured roots", code="not_configured"
            )

        if not _is_within_roots(p, roots):
            raise ToolError(
                "path is outside allowed roots",
                code="path_out_of_scope",
                details={"path": raw_path},
            )

        max_bytes = int(cfg.local_file_max_bytes or 200000)
        try:
            b = p.read_bytes()
        except FileNotFoundError:
            raise ToolError(
                "file not found", code="not_found", details={"path": str(p)}
            )
        except Exception as exc:
            raise ToolError(
                f"failed to read file: {exc}",
                code="read_failed",
                details={"path": str(p)},
            )

        truncated = False
        if len(b) > max_bytes:
            b = b[:max_bytes]
            truncated = True

        try:
            content = b.decode("utf-8")
        except Exception:
            content = b.decode("utf-8", errors="replace")

        return {"path": str(p), "truncated": truncated, "content": content}

    async def shell_exec_handler(args: ShellExecArgs) -> Dict[str, Any]:
        """Execute shell command with strict safety controls."""
        try:
            # Parse command safely
            cmd_parts = shlex.split(args.command)
            if not cmd_parts:
                raise ToolError("empty command", code="invalid_args")

            allowed = set(cfg.shell_exec_allow or [])
            if not allowed:
                raise ToolError("shell_exec allowlist is empty", code="not_configured")
            if cmd_parts[0] not in allowed:
                raise ToolError(
                    "command not in allowlist",
                    code="not_allowed",
                    details={"cmd": cmd_parts[0]},
                )

            # Execute with timeout and output capture
            result = subprocess.run(
                cmd_parts,
                cwd=args.cwd,
                capture_output=True,
                text=True,
                timeout=args.timeout,
                shell=False,  # Never use shell=True
            )

            return {
                "returncode": int(result.returncode),
                "stdout": (result.stdout or "")[:4096],
                "stderr": (result.stderr or "")[:4096],
            }

        except subprocess.TimeoutExpired:
            raise ToolError("command timed out", code="timeout")
        except ToolError:
            raise
        except Exception as e:
            raise ToolError(f"execution failed: {e}", code="execution_failed")

    if "web_search" in enabled:
        registry.register(
            ToolSpec(
                name="web_search",
                description="Search the web for relevant pages.",
                args_model=WebSearchArgs,
                output_model=WebSearchOut,
                error_codes=["search_disabled", "search_failed"],
                handler=web_search_handler,
                side_effect="network",
            )
        )

    if "doc_search" in enabled:
        registry.register(
            ToolSpec(
                name="doc_search",
                description=(
                    "Search locally-ingested documents for relevant passages. "
                    "Returns chunks with text plus doc metadata when available (title/author/path/doc_id)."
                ),
                args_model=DocSearchArgs,
                output_model=DocSearchOut,
                error_codes=["invalid_arguments"],
                handler=doc_search_handler,
                side_effect="read_only",
            )
        )

    if "library_search" in enabled:
        registry.register(
            ToolSpec(
                name="library_search",
                description=(
                    "Search the ingested document library by title/author/path/filename and return matching documents. "
                    "Use this when you need an exact path or author without guessing."
                ),
                args_model=LibrarySearchArgs,
                output_model=LibrarySearchOut,
                error_codes=["invalid_arguments"],
                handler=library_search_handler,
                side_effect="read_only",
            )
        )

    if "kiwix_search" in enabled:
        registry.register(
            ToolSpec(
                name="kiwix_search",
                description=(
                    "Search offline ZIM content via kiwix-serve (configured by kiwix_url) and return matching pages. "
                    "Use this when the user asks about ZIM content."
                ),
                args_model=KiwixSearchArgs,
                output_model=KiwixSearchOut,
                error_codes=["not_configured", "invalid_arguments"],
                handler=kiwix_search_handler,
                side_effect="network",
            )
        )

    if "local_file_read" in enabled:
        registry.register(
            ToolSpec(
                name="local_file_read",
                description="Read a local file (requires explicit user-provided path; root-scoped; size-bounded).",
                args_model=LocalFileReadArgs,
                output_model=LocalFileReadOut,
                error_codes=[
                    "not_configured",
                    "path_out_of_scope",
                    "not_found",
                    "read_failed",
                ],
                handler=local_file_read_handler,
                side_effect="read_only",
            )
        )

    # Shell exec - only register if explicitly enabled via tools.toml
    if "shell_exec" in enabled and cfg.shell_exec_enabled:
        registry.register(
            ToolSpec(
                name="shell_exec",
                description="Execute safe shell commands (allowlisted only). Args: {command, cwd?, timeout}. Returns: {returncode, stdout, stderr}",
                args_model=ShellExecArgs,
                output_model=ShellExecOut,
                error_codes=[
                    "not_configured",
                    "not_allowed",
                    "timeout",
                    "execution_failed",
                ],
                handler=shell_exec_handler,
                side_effect="dangerous",
                requires_confirmation=bool(cfg.shell_exec_requires_confirmation),
            )
        )
