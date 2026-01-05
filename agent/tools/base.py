from __future__ import annotations

from abc import ABC, abstractmethod
from pathlib import Path
from typing import Any, Dict, List, Optional

from ..models import ToolResult


def _handle_file_error(path: str, error: Exception) -> ToolResult:
    """Handle file-related errors with descriptive messages"""
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
    """Validate that a path is within allowed project directory and protect against symlink attacks"""
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
