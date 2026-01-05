from __future__ import annotations

import os
import re
import shlex
import shutil
import subprocess
import tempfile
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple, Union

import httpx
import yaml

from ..models import Source, SourceType, ToolResult


def _handle_file_error(path: str, error: Exception) -> ToolResult:
    error_type = type(error).__name__
    if isinstance(error, PermissionError):
        return ToolResult(
            ok=False,
            error=f"Permission denied: Cannot access '{path}'. Check file permissions.",
        )
    elif isinstance(error, FileNotFoundError):
        return ToolResult(ok=False, error=f"File not found: {path}")
    elif isinstance(error, IsADirectoryError):
        return ToolResult(ok=False, error=f"Path is a directory, not a path: {path}")
    elif isinstance(error, UnicodeDecodeError):
        return ToolResult(
            ok=False, error=f"File encoding error: {path} contains non-text data"
        )
    else:
        return ToolResult(
            ok=False, error=f"Unexpected error accessing '{path}': {str(error)}"
        )


def _check_project_path(
    path: str | Path, allowed_root: str = "projects"
) -> Path | ToolResult:
    """Validate that a path is within the allowed project directory and protect against symlink attacks."""
    project_root = Path(allowed_root).resolve().absolute()

    if isinstance(path, str):
        path_str = path
    else:
        path_str = str(path)

    if ".." in path_str or path_str.startswith("/"):
        return ToolResult(
            ok=False,
            error=f"Access denied: path contains absolute or parent directory references",
        )

    try:
        full_path = (project_root / path).resolve().absolute()

        if not str(full_path).startswith(str(project_root)):
            return ToolResult(
                ok=False, error=f"Access denied: path outside {allowed_root} directory"
            )

        if full_path != full_path.resolve():
            return ToolResult(
                ok=False,
                error=f"Access denied: path contains symlinks pointing outside allowed directory",
            )

        return full_path
    except (ValueError, RuntimeError) as e:
        return ToolResult(ok=False, error=f"Access denied: invalid path specification")


class BaseTool(ABC):
    """Base class for all tools"""

    def __init__(self, name: str, description: str):
        self.name = name
        self.description = description

    @abstractmethod
    def execute(self, **kwargs) -> ToolResult:
        """Execute the tool with given parameters"""
        pass

    def get_schema(self) -> Dict[str, Any]:
        """Return JSON schema for tool parameters"""
        return {
            "name": self.name,
            "description": self.description,
            "parameters": {"type": "object", "properties": {}, "required": []},
        }


class FileReadTool(BaseTool):
    """Tool for reading files within project directories"""

    def __init__(self):
        super().__init__(
            "read_file", "Read the contents of a file within the project directory"
        )

    def execute(self, **kwargs) -> ToolResult:
        path = kwargs.get("path", "")
        max_lines = kwargs.get("max_lines", 100)
        try:
            path_check = _check_project_path(path)
            if isinstance(path_check, ToolResult):
                return path_check

            if not path_check.exists():
                return ToolResult(ok=False, error=f"File not found: {path}")

            with open(path_check, "r", encoding="utf-8", errors="ignore") as f:
                lines = f.readlines()[:max_lines]
                content = "".join(lines)

                if len(lines) == max_lines and f.readline():
                    content += f"\n... (truncated after {max_lines} lines)"

            return ToolResult(ok=True, data=content)

        except Exception as e:
            return _handle_file_error(path, e)

    def get_schema(self) -> Dict[str, Any]:
        schema = super().get_schema()
        schema["parameters"]["properties"] = {
            "path": {
                "type": "string",
                "description": "Relative path to file within project directory",
            },
            "max_lines": {
                "type": "integer",
                "description": "Maximum number of lines to read",
                "default": 2000,
            },
        }
        schema["parameters"]["required"] = ["path"]
        return schema


class DirectoryListTool(BaseTool):
    """Tool for listing directory contents"""

    def __init__(self):
        super().__init__("list_dir", "List contents of a directory within the project")

    def execute(self, path: str = ".", **kwargs) -> ToolResult:
        try:
            # Security: validate and restrict path
            path_check = _check_project_path(path)
            if isinstance(path_check, ToolResult):
                return path_check

            if not path_check.is_dir():
                return ToolResult(ok=False, error=f"Not a directory: {path}")

            items = []
            for item in sorted(path_check.iterdir()):
                if item.is_file():
                    items.append(f"FILE: {item.name}")
                else:
                    items.append(f"DIR:  {item.name}")

            return ToolResult(ok=True, data={"items": "\n".join(items)})

        except Exception as e:
            return _handle_file_error(path, e)

    def get_schema(self) -> Dict[str, Any]:
        schema = super().get_schema()
        schema["parameters"]["properties"] = {
            "path": {
                "type": "string",
                "description": "Relative path to directory within project (default: current)",
                "default": ".",
            }
        }
        return schema


class KiwixQueryTool(BaseTool):
    """Tool for querying Kiwix offline knowledge base"""

    _CATALOG_CACHE: Optional[List[Dict[str, str]]] = None
    _CATALOG_CACHE_TIME: float = 0

    def __init__(self, host: str | None = None):
        super().__init__(
            "kiwix_query",
            "Search offline knowledge base (Wikipedia, Stack Overflow, etc.)",
        )
        import os

        default_host = os.environ.get("KIWIX_HOST", "http://localhost:8080")
        self.host = (host or default_host).rstrip("/")
        self.catalog_url = f"{self.host}/catalog/v2/entries"

    def _get_catalog(self) -> List[Dict[str, str]]:
        """Fetch and parse the Kiwix catalog (OPDS format)."""
        now = Path(".").stat().st_mtime
        if (
            KiwixQueryTool._CATALOG_CACHE is not None
            and (now - KiwixQueryTool._CATALOG_CACHE_TIME) < 300
        ):
            return KiwixQueryTool._CATALOG_CACHE

        try:
            with httpx.Client(timeout=10.0) as client:
                response = client.get(self.catalog_url)
                response.raise_for_status()
                content = response.text

            entries = []
            entry_pattern = re.compile(r"<entry>(.*?)</entry>", re.DOTALL)
            title_pattern = re.compile(r"<title>(.*?)</title>")
            name_pattern = re.compile(r"<name>(.*?)</name>")
            summary_pattern = re.compile(r"<summary>(.*?)</summary>")
            url_pattern = re.compile(r'<link[^>]+type="text/html"[^>]+href="([^"]+)"')

            for entry_match in entry_pattern.finditer(content):
                entry_text = entry_match.group(1)
                title = title_pattern.search(entry_text)
                name = name_pattern.search(entry_text)
                summary = summary_pattern.search(entry_text)
                url = url_pattern.search(entry_text)

                if name:
                    entries.append(
                        {
                            "title": title.group(1).strip() if title else name.group(1),
                            "name": name.group(1).strip(),
                            "summary": summary.group(1).strip() if summary else "",
                            "url": url.group(1).strip()
                            if url
                            else f"/content/{name.group(1).strip()}",
                        }
                    )

            KiwixQueryTool._CATALOG_CACHE = entries
            KiwixQueryTool._CATALOG_CACHE_TIME = now
            return entries

        except Exception as e:
            print(f"Error fetching Kiwix catalog: {e}")
            return []

    def _get_zim_content_path(self, zim_name: str) -> str | None:
        """Get the content base URL for a ZIM file."""
        catalog = self._get_catalog()
        zim_entry = next((e for e in catalog if e["name"] == zim_name), None)
        if not zim_entry:
            return None
        content_path = zim_entry["url"]
        if not content_path.startswith("http"):
            return f"{self.host}{content_path}"
        return content_path

    def _get_zim_content_name(self, zim_name_prefix: str) -> str | None:
        """Get the full content name for Kiwix API (e.g., 'wikipedia_en_all_nopic_2025-08')."""
        catalog = self._get_catalog()
        for entry in catalog:
            if entry["name"] == zim_name_prefix:
                url = entry["url"]
                if url.startswith("/content/"):
                    return url.replace("/content/", "")
        return None

    def _suggest_titles(
        self, zim_name: str, query: str, max_results: int = 10
    ) -> List[Dict[str, str]]:
        """Use Kiwix /suggest endpoint to get title suggestions."""
        try:
            with httpx.Client(timeout=10.0) as client:
                response = client.get(
                    f"{self.host}/suggest",
                    params={"content": zim_name, "term": query, "count": max_results},
                )
                response.raise_for_status()
                suggestions = response.json()

            results = []
            for item in suggestions:
                if item.get("kind") == "path" and item.get("path"):
                    results.append(
                        {
                            "title": item.get("value", item.get("path")),
                            "path": item.get("path"),
                            "source": "suggest",
                        }
                    )
            return results
        except Exception as e:
            print(f"Kiwix suggest error: {e}")
            return []

    def _full_text_search(
        self, zim_name: str, query: str, max_results: int = 5
    ) -> List[Dict[str, Union[str, int]]]:
        """Use Kiwix /search endpoint for full-text search."""
        try:
            with httpx.Client(timeout=15.0) as client:
                response = client.get(
                    f"{self.host}/search",
                    params={
                        "books.name": zim_name,
                        "pattern": query,
                        "format": "xml",
                        "pageLength": max_results,
                    },
                )
                response.raise_for_status()
                content = response.text

            results = []
            title_pattern = re.compile(r"<title>(.*?)</title>")
            link_pattern = re.compile(r"<link>(.*?)</link>")
            desc_pattern = re.compile(r"<description>(.*?)</description>", re.DOTALL)
            item_pattern = re.compile(r"<item>(.*?)</item>", re.DOTALL)
            word_count_pattern = re.compile(r"<wordCount>(\d+)</wordCount>")

            for item_match in item_pattern.finditer(content):
                item_text = item_match.group(1)
                title = title_pattern.search(item_text)
                link = link_pattern.search(item_text)
                desc = desc_pattern.search(item_text)
                word_count = word_count_pattern.search(item_text)

                if title and link:
                    snippet = ""
                    if desc:
                        clean = re.sub(r"<[^>]+>", "", desc.group(1)).strip()
                        snippet = clean[:400] + "..." if len(clean) > 400 else clean

                    results.append(
                        {
                            "title": title.group(1),
                            "url": link.group(1),
                            "snippet": snippet,
                            "word_count": int(word_count.group(1)) if word_count else 0,
                            "source": "search",
                        }
                    )

            return results
        except Exception as e:
            print(f"Kiwix search error: {e}")
            return []

    def _fetch_article_content(
        self, content_base: str, article_path: str
    ) -> Dict[str, str] | None:
        """Fetch and parse article content from ZIM file."""
        try:
            with httpx.Client(timeout=10.0) as client:
                response = client.get(
                    f"{content_base}/A/{article_path}", follow_redirects=True
                )
                if response.status_code != 200:
                    return None

                content = response.text
                if "mw-parser-output" not in content:
                    return None

                title_match = re.search(
                    r'<span class="mw-page-title-main">(.*?)</span>', content
                )
                title = title_match.group(1) if title_match else article_path

                paragraphs = re.findall(r"<p>(.*?)</p>", content, re.DOTALL)
                snippet = ""
                for p in paragraphs[:5]:
                    clean = re.sub(r"<[^>]+>", "", p).strip()
                    if len(clean) > 80:
                        snippet = clean[:400] + "..." if len(clean) > 400 else clean
                        break

                return {
                    "title": title,
                    "snippet": snippet,
                    "url": f"{content_base}/A/{article_path}",
                }
        except Exception:
            return None

    def _search_content(
        self, zim_name: str, query: str, max_results: int = 5
    ) -> List[Dict[str, str]]:
        """Search within a specific ZIM file using suggest then search endpoints."""
        results: List[Dict[str, str]] = []

        content_name = self._get_zim_content_name(zim_name)
        if not content_name:
            return results

        content_base = self._get_zim_content_path(zim_name)
        if not content_base:
            return results

        suggestions = self._suggest_titles(content_name, query, max_results)

        for sugg in suggestions[:max_results]:
            article = self._fetch_article_content(content_base, sugg["path"])
            if article and article.get("snippet"):
                article["source"] = "suggest"
                results.append(article)

        if len(results) < max_results:
            search_results = self._full_text_search(
                content_name, query, max_results - len(results)
            )
            for sr in search_results:
                if not any(r["url"] == sr["url"] for r in results):
                    results.append(sr)

        return results[:max_results]

    def _generate_article_titles(self, query: str) -> List[str]:
        """Generate potential Wikipedia article titles from a query."""
        titles = []
        query_clean = re.sub(r"[^\w\s]", " ", query)
        words = query_clean.split()
        filtered_words = [w for w in words if len(w) > 2]

        titles.append(query.replace(" ", "_"))

        if len(filtered_words) >= 2:
            titles.append("_".join(filtered_words[:3]).capitalize())

        for word in filtered_words[:3]:
            titles.append(word.capitalize())

        wiki_terms = [
            "shadow_library",
            "Digital_library",
            "File_sharing",
            "Copyright",
            "Open_access",
        ]
        for term in wiki_terms:
            if any(t in query.lower() for t in term.lower().split("_")):
                titles.append(term)

        common_topics = {
            "programming": [
                "Python_(programming_language)",
                "Programming_language",
                "Computer_programming",
            ],
            "python": ["Python_(programming_language)"],
            "docker": ["Docker"],
            "database": ["Database", "SQL"],
            "web": ["World_Wide_Web", "Web_server"],
            "linux": ["Linux"],
            "archive": ["Archive", "Digital_preservation"],
            "library": ["Library", "Digital_library"],
            "search": ["Web_search_engine"],
        }

        for key, topics in common_topics.items():
            if key in query.lower():
                titles.extend(topics)

        return list(dict.fromkeys(titles))

    def execute(self, **kwargs) -> ToolResult:
        query = kwargs.get("query", "")
        max_results = kwargs.get("max_results", 5)
        zim_name = kwargs.get("zim_name", None)

        if not query:
            return ToolResult(ok=False, error="Query is required")

        try:
            catalog = self._get_catalog()

            if not catalog:
                return ToolResult(ok=True, data=[], sources=[])

            all_results = []
            all_sources: list[Source] = []

            if zim_name:
                all_results = self._search_content(zim_name, query, max_results)
            else:
                priority_zims = [e for e in catalog if "wikipedia" in e["name"].lower()]
                other_zims = [
                    e for e in catalog if "wikipedia" not in e["name"].lower()
                ]

                for zim in priority_zims[:2]:
                    results = self._search_content(
                        zim["name"], query, max(1, max_results // 2)
                    )
                    all_results.extend(results)

                if len(all_results) < max_results:
                    for zim in other_zims[:3]:
                        if len(all_results) >= max_results:
                            break
                        results = self._search_content(zim["name"], query, 1)
                        all_results.extend(results)

            for item in all_results[:max_results]:
                source = Source(
                    source_id=Source.generate_id(
                        "kiwix_query", item.get("url", ""), item.get("title", "")
                    ),
                    tool="kiwix_query",
                    source_type=SourceType.KIWIX,
                    title=item.get("title", ""),
                    locator=item.get("url", ""),
                    snippet=item.get("snippet", "")[:500],
                    confidence=0.9,
                )
                all_sources.append(source)

            if all_results:
                return ToolResult(
                    ok=True, data=all_results[:max_results], sources=all_sources
                )

            return ToolResult(ok=True, data=[], sources=[])

        except Exception as e:
            return ToolResult(ok=False, error=f"Kiwix query failed: {str(e)}")

    def get_schema(self) -> Dict[str, Any]:
        schema = super().get_schema()
        schema["parameters"]["properties"] = {
            "query": {
                "type": "string",
                "description": "Search query for the knowledge base",
            },
            "max_results": {
                "type": "integer",
                "description": "Maximum number of results to return",
                "default": 5,
            },
            "zim_name": {
                "type": "string",
                "description": "Specific ZIM file to search (optional, searches all if not specified)",
            },
        }
        schema["parameters"]["required"] = ["query"]
        return schema


class WebSearchTool(BaseTool):
    """Tool for performing web searches"""

    def __init__(self):
        super().__init__(
            "web_search", "Perform a web search and return relevant results"
        )

    def execute(self, **kwargs) -> ToolResult:
        query = kwargs.get("query", "")
        max_results = kwargs.get("max_results", 5)
        try:
            import ddgs

            results = []
            all_sources: list[Source] = []
            with ddgs.DDGS() as ddgs_client:
                for r in ddgs_client.text(query, max_results=max_results):
                    url = r.get("href", "")
                    title = r.get("title", "")
                    snippet = r.get("body", "")[:300]
                    results.append({"title": title, "url": url, "snippet": snippet})
                    all_sources.append(
                        Source(
                            source_id=Source.generate_id("web_search", url, title),
                            tool="web_search",
                            source_type=SourceType.WEB,
                            title=title,
                            locator=url,
                            snippet=snippet[:500],
                            confidence=0.7,
                        )
                    )

            return ToolResult(ok=True, data=results, sources=all_sources)

        except httpx.TimeoutException:
            return ToolResult(
                ok=False,
                error="Web search timed out. The search service may be slow or unavailable.",
            )
        except httpx.ConnectError:
            return ToolResult(
                ok=False,
                error="Cannot connect to search service. Check your internet connection.",
            )
        except Exception as e:
            return ToolResult(ok=False, error=f"Web search failed: {str(e)}")

    def get_schema(self) -> Dict[str, Any]:
        schema = super().get_schema()
        schema["parameters"]["properties"] = {
            "query": {"type": "string", "description": "Web search query"},
            "max_results": {
                "type": "integer",
                "description": "Maximum number of results to return",
                "default": 5,
            },
        }
        schema["parameters"]["required"] = ["query"]
        return schema


class UrlFetchTool(BaseTool):
    """Tool for fetching content from URLs"""

    def __init__(self):
        super().__init__("fetch_url", "Fetch and extract content from a URL")

    def execute(self, **kwargs) -> ToolResult:
        url = kwargs.get("url", "")
        max_length = kwargs.get("max_length", 2000)
        try:
            if not url.startswith(("http://", "https://")):
                return ToolResult(ok=False, error="Invalid URL scheme")

            from trafilatura.core import extract
            from trafilatura.downloads import fetch_url

            downloaded = fetch_url(url)
            text = extract(downloaded)
            if not text:
                return ToolResult(ok=False, error="No extractable text found")

            if len(text) > max_length:
                text = text[:max_length] + "..."

            source = Source(
                source_id=Source.generate_id(
                    "fetch_url", url, url.split("/")[-1] or url
                ),
                tool="fetch_url",
                source_type=SourceType.WEB,
                title=url.split("/")[-1][:50] or "Fetched URL",
                locator=url,
                snippet=text[:500],
                confidence=0.8,
            )

            return ToolResult(ok=True, data=text, sources=[source])

        except Exception as e:
            return ToolResult(ok=False, error=f"URL fetch failed: {str(e)}")

    def get_schema(self) -> Dict[str, Any]:
        schema = super().get_schema()
        schema["parameters"]["properties"] = {
            "url": {"type": "string", "description": "URL to fetch content from"},
            "max_length": {
                "type": "integer",
                "description": "Maximum content length to return",
                "default": 2000,
            },
        }
        schema["parameters"]["required"] = ["url"]
        return schema


class RagSearchTool(BaseTool):
    """Tool for searching local RAG index"""

    def __init__(self):
        super().__init__("rag_search", "Search local project knowledge base (RAG)")

    def execute(self, **kwargs) -> ToolResult:
        query = kwargs.get("query", "")
        max_results = kwargs.get("max_results", 3)
        try:
            from ..manifest import load_manifest
            from ..rag import search

            manifest = load_manifest("default")  # Could make this configurable
            results = search(manifest, query, k=max_results)

            formatted_results = [
                {
                    "source": chunk.source,
                    "ref": chunk.ref,
                    "content": chunk.text[:500],  # Truncate for brevity
                    "chunk_id": chunk.chunk_id,
                }
                for chunk in results
            ]

            return ToolResult(ok=True, data=formatted_results)

        except Exception as e:
            return ToolResult(ok=False, error=f"RAG search failed: {str(e)}")

    def get_schema(self) -> Dict[str, Any]:
        schema = super().get_schema()
        schema["parameters"]["properties"] = {
            "query": {
                "type": "string",
                "description": "Search query for local knowledge base",
            },
            "max_results": {
                "type": "integer",
                "description": "Maximum number of results to return",
                "default": 3,
            },
        }
        schema["parameters"]["required"] = ["query"]
        return schema


class TerminalTool(BaseTool):
    """Tool for executing safe terminal commands"""

    def __init__(self):
        super().__init__(
            "run_command",
            "Execute safe shell commands on the system (sudo removed for security)",
        )

    def execute(self, **kwargs) -> ToolResult:
        command = kwargs.get("command", "")
        timeout = kwargs.get("timeout", 30)

        if not command:
            return ToolResult(ok=False, error="No command provided")

        import re

        command_norm = command.lower().strip()

        destructive_patterns = [
            r"\brm\s+(-rf?|--recursive|--force)\s+[/\\]",
            r"\bdd\s+if=/dev/zero",
            r"\b(mkfs|fdisk|format|formatfs)\b",
            r"\bchmod\s+777\b",
            r"\bshutdown\b.*\b(now|0|\d+)\b",
            r"\breboot\b",
            r"\b(passwd|usermod|userdel|groupmod)\b.*\b(root|admin)\b",
            r"\bsystemctl\s+(stop|disable|mask|kill)\b",
        ]

        for pattern in destructive_patterns:
            if re.search(pattern, command_norm):
                return ToolResult(
                    ok=False, error=f"Command contains blocked operation: {pattern}"
                )

        network_commands = [
            r"\b(ssh|scp|sftp|ftp|telnet|nc|ncat|netcat)\b",
            r"\bcurl\s+",
            r"\bwget\s+",
        ]
        for pattern in network_commands:
            if re.search(pattern, command_norm):
                return ToolResult(ok=False, error="Network commands are not allowed")

        dangerous_chars = [
            ";",
            "`",
            "$(",
            "${",
            "&&",
            "||",
            "|&",
            ">",
            ">>",
            "<",
            "|",
            "&",
        ]
        for char in dangerous_chars:
            if char in command:
                return ToolResult(
                    ok=False, error=f"Character '{char}' not allowed in commands"
                )

        encoding_patterns = [
            r"\\x[0-9a-fA-F]{2}",
            r"\$\(echo.*\|.*\)",
            r"`.*`",
            r"\\0[0-9]{3}",
        ]
        for pattern in encoding_patterns:
            if re.search(pattern, command):
                return ToolResult(ok=False, error="Command encoding not allowed")

        allowed_commands = {
            "ls",
            "cat",
            "head",
            "tail",
            "grep",
            "find",
            "wc",
            "sort",
            "uniq",
            "cut",
            "awk",
            "sed",
            "date",
            "whoami",
            "pwd",
            "cd",
            "echo",
            "printf",
            "mkdir",
            "touch",
            "cp",
            "mv",
            "du",
            "df",
            "ps",
            "top",
            "htop",
            "uname",
            "which",
            "whereis",
            "type",
            "man",
            "help",
        }

        cmd_parts = shlex.split(command)
        if not cmd_parts:
            return ToolResult(ok=False, error="Invalid command syntax")

        base_cmd = cmd_parts[0].lower()
        if base_cmd not in allowed_commands:
            return ToolResult(
                ok=False, error=f"Command '{base_cmd}' is not in the allowed list"
            )

        if base_cmd in ["rm", "mv", "cp"]:
            for arg in cmd_parts[1:]:
                if "../" in arg or arg.startswith("/") or "\\" in arg:
                    return ToolResult(
                        ok=False,
                        error="File operations cannot use absolute paths or directory traversal",
                    )

        try:
            result = subprocess.run(
                cmd_parts, capture_output=True, text=True, timeout=timeout, check=False
            )

            output = result.stdout.strip()
            error = result.stderr.strip()

            return ToolResult(
                ok=result.returncode == 0,
                data={
                    "stdout": output,
                    "stderr": error,
                    "returncode": result.returncode,
                },
            )

        except subprocess.TimeoutExpired:
            return ToolResult(
                ok=False, error=f"Command timed out after {timeout} seconds"
            )
        except Exception as e:
            return ToolResult(ok=False, error=f"Command execution failed: {str(e)}")

    def get_schema(self) -> Dict[str, Any]:
        schema = super().get_schema()
        schema["parameters"]["properties"] = {
            "command": {"type": "string", "description": "Shell command to execute"},
            "timeout": {
                "type": "integer",
                "description": "Command timeout in seconds",
                "default": 30,
            },
        }
        schema["parameters"]["required"] = ["command"]
        return schema


class SystemdTool(BaseTool):
    """Tool for managing systemd services"""

    def __init__(self):
        super().__init__(
            "systemd_control", "Control systemd services (start, stop, restart, status)"
        )

    def execute(self, **kwargs) -> ToolResult:
        action = kwargs.get("action", "")
        service = kwargs.get("service", "")

        if not action or not service:
            return ToolResult(ok=False, error="Both action and service are required")

        valid_actions = ["start", "stop", "restart", "status", "enable", "disable"]
        if action not in valid_actions:
            return ToolResult(
                ok=False,
                error=f"Invalid action. Must be one of: {', '.join(valid_actions)}",
            )

        try:
            if action == "status":
                cmd = f"systemctl status {service}"
            else:
                cmd = f"sudo systemctl {action} {service}"

            result = subprocess.run(
                shlex.split(cmd), capture_output=True, text=True, timeout=10
            )

            return ToolResult(
                ok=result.returncode == 0,
                data={
                    "stdout": result.stdout.strip(),
                    "stderr": result.stderr.strip(),
                    "returncode": result.returncode,
                },
            )

        except subprocess.TimeoutExpired:
            return ToolResult(ok=False, error="Systemd command timed out")
        except Exception as e:
            return ToolResult(ok=False, error=f"Systemd operation failed: {str(e)}")

    def get_schema(self) -> Dict[str, Any]:
        schema = super().get_schema()
        schema["parameters"]["properties"] = {
            "action": {
                "type": "string",
                "enum": ["start", "stop", "restart", "status", "enable", "disable"],
                "description": "Systemd action to perform",
            },
            "service": {"type": "string", "description": "Name of the systemd service"},
        }
        schema["parameters"]["required"] = ["action", "service"]
        return schema


class PackageTool(BaseTool):
    """Tool for package management (apt/pacman/etc)"""

    def __init__(self):
        super().__init__(
            "package_manage", "Manage system packages (install, remove, update, search)"
        )

    def execute(self, **kwargs) -> ToolResult:
        action = kwargs.get("action", "")
        package = kwargs.get("package", "")

        if not action:
            return ToolResult(ok=False, error="Action is required")

        try:
            # Detect package manager
            if self._has_command("apt"):
                pm = "apt"
                if action == "install":
                    cmd = f"sudo apt update && sudo apt install -y {package}"
                elif action == "remove":
                    cmd = f"sudo apt remove -y {package}"
                elif action == "update":
                    cmd = "sudo apt update && sudo apt upgrade -y"
                elif action == "search":
                    cmd = f"apt search {package}"
                else:
                    return ToolResult(
                        ok=False, error=f"Unsupported action for apt: {action}"
                    )

            elif self._has_command("pacman"):
                pm = "pacman"
                if action == "install":
                    cmd = f"sudo pacman -S --noconfirm {package}"
                elif action == "remove":
                    cmd = f"sudo pacman -R --noconfirm {package}"
                elif action == "update":
                    cmd = "sudo pacman -Syu --noconfirm"
                elif action == "search":
                    cmd = f"pacman -Ss {package}"
                else:
                    return ToolResult(
                        ok=False, error=f"Unsupported action for pacman: {action}"
                    )
            else:
                return ToolResult(ok=False, error="No supported package manager found")

            result = subprocess.run(
                cmd,
                shell=True,
                capture_output=True,
                text=True,
                timeout=300,  # 5 minutes for package operations
            )

            return ToolResult(
                ok=result.returncode == 0,
                data={
                    "stdout": result.stdout.strip(),
                    "stderr": result.stderr.strip(),
                    "returncode": result.returncode,
                },
            )

        except subprocess.TimeoutExpired:
            return ToolResult(ok=False, error="Package operation timed out")
        except Exception as e:
            return ToolResult(ok=False, error=f"Package operation failed: {str(e)}")

    def _has_command(self, cmd: str) -> bool:
        """Check if a command exists"""
        return shutil.which(cmd) is not None

    def get_schema(self) -> Dict[str, Any]:
        schema = super().get_schema()
        schema["parameters"]["properties"] = {
            "action": {
                "type": "string",
                "enum": ["install", "remove", "update", "search"],
                "description": "Package management action",
            },
            "package": {
                "type": "string",
                "description": "Package name (not required for update)",
            },
        }
        schema["parameters"]["required"] = ["action"]
        return schema


class SkillTool(BaseTool):
    """Tool for loading reusable skill instructions from SKILL.md files"""

    def __init__(self):
        super().__init__(
            "load_skill",
            "Load and return content of a SKILL.md file for dynamic instruction injection",
        )

    def execute(self, **kwargs) -> ToolResult:
        name = kwargs.get("name", "")
        try:
            # Security: restrict to .router/skills/ directory with proper path validation
            if not name or ".." in name or "/" in name or "\\" in name:
                return ToolResult(
                    ok=False,
                    error="Invalid skill name: must not contain path traversal characters",
                )

            skills_dir = Path(".router/skills").resolve()
            skill_dir = skills_dir / name
            skill_md_path = None

            if skill_dir.is_dir():
                skill_md_path = skill_dir / "SKILL.md"
            else:
                skill_md_path = skills_dir / f"{name}.md"

            skill_md_path = skill_md_path.resolve()

            # Verify the resolved path is still within the skills directory
            if not str(skill_md_path).startswith(str(skills_dir)):
                return ToolResult(
                    ok=False,
                    error="Access denied: skill path outside allowed directory",
                )

            if not skill_md_path.exists():
                return ToolResult(ok=False, error=f"Skill '{name}' not found")

            content = skill_md_path.read_text(encoding="utf-8")

            # Parse frontmatter if present
            match = re.match(r"^---\s*\n(.*?)\n---\s*\n(.*)$", content, re.DOTALL)
            if match:
                frontmatter, body = match.groups()
                try:
                    metadata = yaml.safe_load(frontmatter)
                    if not isinstance(metadata, dict):
                        metadata = {}
                except yaml.YAMLError:
                    metadata = {}
                body = body.strip()
            else:
                body = content

            # Add resource hints if skill is a directory
            if skill_dir.is_dir():
                resources = []
                for folder, label in [
                    ("scripts", "Scripts"),
                    ("references", "References"),
                    ("assets", "Assets"),
                ]:
                    folder_path = skill_dir / folder
                    if folder_path.exists():
                        files = list(folder_path.glob("*"))
                        if files:
                            resources.append(
                                f"{label}: {', '.join(f.name for f in files)}"
                            )

                if resources:
                    body += f"\n\n**Available resources in {skill_dir}:**\n"
                    body += "\n".join(f"- {r}" for r in resources)

            return ToolResult(ok=True, data=body)

        except Exception as e:
            return ToolResult(ok=False, error=f"Error listing skills: {str(e)}")

    def get_schema(self) -> Dict[str, Any]:
        return super().get_schema()


class FileEditTool(BaseTool):
    """Tool for editing files by replacing text content"""

    def __init__(self):
        super().__init__("edit_file", "Edit files by replacing specific text content")

    def execute(
        self, path: str = "", old_str: str = "", new_str: str = "", **kwargs
    ) -> ToolResult:
        """Edit a file by replacing old_str with new_str"""
        if not path:
            return ToolResult(ok=False, error="File path is required")

        if not old_str:
            return ToolResult(ok=False, error="Old text to replace is required")

        if not new_str:
            return ToolResult(ok=False, error="New replacement text is required")

        try:
            # Validate path is within project directory
            path_check = _check_project_path(path)
            if isinstance(path_check, ToolResult):
                return path_check

            if not path_check.exists():
                return ToolResult(ok=False, error=f"File not found: {path}")

            # Read file content
            with open(path_check, "r", encoding="utf-8") as f:
                content = f.read()

            # Check if old_str exists
            if old_str not in content:
                return ToolResult(
                    ok=False, error=f"Text not found in file: {old_str[:50]}..."
                )

            # Replace text
            new_content = content.replace(old_str, new_str)

            # Write back to file
            with open(path_check, "w", encoding="utf-8") as f:
                f.write(new_content)

            return ToolResult(ok=True, data=f"Successfully replaced text in {path}")

        except Exception as e:
            return _handle_file_error(path, e)

    def get_schema(self) -> Dict[str, Any]:
        schema = super().get_schema()
        schema["parameters"]["properties"] = {
            "path": {
                "type": "string",
                "description": "Relative path to file within project directory",
            },
            "old_str": {
                "type": "string",
                "description": "Text to search for and replace",
            },
            "new_str": {"type": "string", "description": "Replacement text"},
        }
        schema["parameters"]["required"] = ["path", "old_str", "new_str"]
        return schema


class ListSkillsTool(BaseTool):
    """Tool for listing available skills with descriptions"""

    def __init__(self):
        super().__init__(
            "list_skills", "List all available skills with their descriptions"
        )

    def execute(self, **kwargs) -> ToolResult:
        try:
            skills_dir = Path(".router/skills").resolve()
            skills = []

            for item in skills_dir.iterdir():
                name = item.name
                if item.is_dir():
                    skill_md = item / "SKILL.md"
                    if skill_md.exists():
                        content = skill_md.read_text(encoding="utf-8")
                        match = re.match(
                            r"^---\s*\n(.*?)\n---\s*\n(.*)$", content, re.DOTALL
                        )
                        if match:
                            frontmatter, _ = match.groups()
                            try:
                                metadata = yaml.safe_load(frontmatter)
                                if (
                                    isinstance(metadata, dict)
                                    and "name" in metadata
                                    and "description" in metadata
                                ):
                                    skills.append(
                                        f"- {metadata['name']}: {metadata['description']}"
                                    )
                                else:
                                    skills.append(f"- {name}: Skill file")
                            except yaml.YAMLError:
                                skills.append(f"- {name}: Skill file")
                        else:
                            skills.append(f"- {name}: Skill file")
                elif item.is_file() and item.suffix == ".md":
                    name = item.stem
                    skills.append(f"- {name}: Skill file")

            if not skills:
                return ToolResult(ok=True, data="(no skills available)")

            return ToolResult(ok=True, data="\n".join(skills))

        except Exception as e:
            return ToolResult(ok=False, error=f"Error listing skills: {str(e)}")

    def get_schema(self) -> Dict[str, Any]:
        return super().get_schema()


class GitHubSearchTool(BaseTool):
    """Tool for searching GitHub repositories and code"""

    def __init__(self, token: str | None = None):
        super().__init__(
            "github_search", "Search GitHub for repositories, code, and issues"
        )
        self.token = token or os.environ.get("GITHUB_TOKEN")
        self.api_base = "https://api.github.com"
        self.headers = {"Accept": "application/vnd.github.v3+json"}
        if self.token:
            self.headers["Authorization"] = f"token {self.token}"

    def _search_repos(self, query: str, max_results: int = 5) -> list[dict]:
        """Search GitHub repositories."""
        url = f"{self.api_base}/search/repositories"
        params = {"q": query, "per_page": max_results, "sort": "stars"}
        try:
            with httpx.Client(timeout=15.0) as client:
                response = client.get(url, params=params, headers=self.headers)
                response.raise_for_status()
                data = response.json()
                return data.get("items", [])[:max_results]
        except Exception as e:
            print(f"GitHub repo search error: {e}")
            return []

    def _search_code(self, query: str, max_results: int = 5) -> list[dict]:
        """Search GitHub code."""
        url = f"{self.api_base}/search/code"
        params = {"q": query, "per_page": max_results}
        try:
            with httpx.Client(timeout=15.0) as client:
                response = client.get(url, params=params, headers=self.headers)
                response.raise_for_status()
                data = response.json()
                return data.get("items", [])[:max_results]
        except Exception as e:
            print(f"GitHub code search error: {e}")
            return []

    def _search_issues(self, query: str, max_results: int = 5) -> list[dict]:
        """Search GitHub issues and PRs."""
        url = f"{self.api_base}/search/issues"
        params = {"q": query, "per_page": max_results}
        try:
            with httpx.Client(timeout=15.0) as client:
                response = client.get(url, params=params, headers=self.headers)
                response.raise_for_status()
                data = response.json()
                return data.get("items", [])[:max_results]
        except Exception as e:
            print(f"GitHub issues search error: {e}")
            return []

    def execute(self, **kwargs) -> ToolResult:
        query = kwargs.get("query", "")
        search_type = kwargs.get("type", "repositories")
        max_results = kwargs.get("max_results", 5)

        if not query:
            return ToolResult(ok=False, error="Query is required")

        try:
            if search_type == "repositories":
                results = self._search_repos(query, max_results)
            elif search_type == "code":
                results = self._search_code(query, max_results)
            elif search_type == "issues":
                results = self._search_issues(query, max_results)
            else:
                results = self._search_repos(query, max_results)

            sources = []
            for item in results:
                if search_type == "repositories":
                    url = item.get("html_url", "")
                    title = item.get("full_name", "")
                    snippet = item.get("description", "") or ""
                    sources.append(
                        Source(
                            source_id=Source.generate_id("github_search", url, title),
                            tool="github_search",
                            source_type=SourceType.WEB,
                            title=title,
                            locator=url,
                            snippet=snippet[:500],
                            confidence=0.8,
                        )
                    )
                elif search_type == "code":
                    url = item.get("html_url", "")
                    title = f"{item.get('repository', {}).get('full_name', '')}/{item.get('path', '')}"
                    snippet = item.get("name", "")
                    sources.append(
                        Source(
                            source_id=Source.generate_id("github_search", url, title),
                            tool="github_search",
                            source_type=SourceType.WEB,
                            title=title,
                            locator=url,
                            snippet=snippet[:500],
                            confidence=0.7,
                        )
                    )
                elif search_type == "issues":
                    url = item.get("html_url", "")
                    title = item.get("title", "")
                    snippet = f"State: {item.get('state', '')}"
                    sources.append(
                        Source(
                            source_id=Source.generate_id("github_search", url, title),
                            tool="github_search",
                            source_type=SourceType.WEB,
                            title=title,
                            locator=url,
                            snippet=snippet[:500],
                            confidence=0.7,
                        )
                    )

            return ToolResult(ok=True, data=results, sources=sources)

        except Exception as e:
            return ToolResult(ok=False, error=f"GitHub search failed: {str(e)}")

    def get_schema(self) -> Dict[str, Any]:
        schema = super().get_schema()
        schema["parameters"]["properties"] = {
            "query": {"type": "string", "description": "Search query for GitHub"},
            "type": {
                "type": "string",
                "enum": ["repositories", "code", "issues"],
                "description": "Type of search",
                "default": "repositories",
            },
            "max_results": {
                "type": "integer",
                "description": "Maximum results to return",
                "default": 5,
            },
        }
        schema["parameters"]["required"] = ["query"]
        return schema


class GitHubFetchTool(BaseTool):
    """Tool for fetching file contents from GitHub repositories"""

    def __init__(self, token: str | None = None):
        super().__init__("github_fetch", "Fetch file contents from GitHub repositories")
        self.token = token or os.environ.get("GITHUB_TOKEN")
        self.api_base = "https://api.github.com"
        self.headers = {"Accept": "application/vnd.github.v3+json"}
        if self.token:
            self.headers["Authorization"] = f"token {self.token}"

    def _get_repo_info(self, owner: str, repo: str) -> dict | None:
        """Get repository information."""
        url = f"{self.api_base}/repos/{owner}/{repo}"
        try:
            with httpx.Client(timeout=10.0) as client:
                response = client.get(url, headers=self.headers)
                if response.status_code == 200:
                    return response.json()
        except Exception:
            pass
        return None

    def _get_file_content(
        self, owner: str, repo: str, path: str, ref: str = "main"
    ) -> dict | None:
        """Get file content from repository."""
        url = f"{self.api_base}/repos/{owner}/{repo}/contents/{path}"
        params = {"ref": ref}
        try:
            with httpx.Client(timeout=10.0) as client:
                response = client.get(url, params=params, headers=self.headers)
                if response.status_code == 200:
                    data = response.json()
                    import base64

                    if data.get("encoding") == "base64":
                        content = base64.b64decode(data["content"]).decode(
                            "utf-8", errors="ignore"
                        )
                        return {"content": content, "sha": data.get("sha")}
        except Exception:
            pass
        return None

    def _get_directory(
        self, owner: str, repo: str, path: str = "", ref: str = "main"
    ) -> list[dict]:
        """List directory contents."""
        url = f"{self.api_base}/repos/{owner}/{repo}/contents/{path}"
        params = {"ref": ref}
        try:
            with httpx.Client(timeout=10.0) as client:
                response = client.get(url, params=params, headers=self.headers)
                if response.status_code == 200:
                    return response.json()
        except Exception:
            pass
        return []

    def execute(self, **kwargs) -> ToolResult:
        repo = kwargs.get("repo", "")
        path = kwargs.get("path", "")
        ref = kwargs.get("ref", "main")

        if not repo:
            return ToolResult(
                ok=False, error="Repository is required (format: owner/repo)"
            )

        parts = repo.split("/")
        if len(parts) != 2:
            return ToolResult(
                ok=False, error="Invalid repository format (use owner/repo)"
            )

        owner, repo_name = parts

        try:
            if path.endswith("/") or not path:
                contents = self._get_directory(owner, repo_name, path.strip("/"), ref)
                sources = [
                    Source(
                        source_id=Source.generate_id(
                            "github_fetch",
                            f"{repo}#{item.get('path', '')}",
                            item.get("name", ""),
                        ),
                        tool="github_fetch",
                        source_type=SourceType.WEB,
                        title=f"{repo}/{item.get('path', item.get('name', ''))}",
                        locator=f"https://github.com/{repo}/blob/{ref}/{item.get('path', item.get('name', ''))}",
                        snippet=f"Type: {item.get('type', 'file')}",
                        confidence=0.8,
                    )
                    for item in (contents if isinstance(contents, list) else [])
                ]
                return ToolResult(
                    ok=True,
                    data={"type": "directory", "contents": contents},
                    sources=sources,
                )
            else:
                file_data = self._get_file_content(owner, repo_name, path, ref)
                if file_data:
                    source = Source(
                        source_id=Source.generate_id(
                            "github_fetch", f"{repo}#{path}", path.split("/")[-1]
                        ),
                        tool="github_fetch",
                        source_type=SourceType.WEB,
                        title=f"{repo}/{path}",
                        locator=f"https://github.com/{repo}/blob/{ref}/{path}",
                        snippet=file_data["content"][:500],
                        confidence=0.9,
                    )
                    return ToolResult(
                        ok=True,
                        data={
                            "type": "file",
                            "content": file_data["content"],
                            "sha": file_data.get("sha"),
                        },
                        sources=[source],
                    )
                else:
                    return ToolResult(ok=False, error=f"File not found: {path}")

        except Exception as e:
            return ToolResult(ok=False, error=f"GitHub fetch failed: {str(e)}")

    def get_schema(self) -> Dict[str, Any]:
        schema = super().get_schema()
        schema["parameters"]["properties"] = {
            "repo": {
                "type": "string",
                "description": "Repository (format: owner/repo)",
            },
            "path": {
                "type": "string",
                "description": "File or directory path",
                "default": "",
            },
            "ref": {
                "type": "string",
                "description": "Branch, tag, or commit",
                "default": "main",
            },
        }
        schema["parameters"]["required"] = ["repo"]
        return schema
