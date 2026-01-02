from __future__ import annotations
from typing import Dict, Any

from .base import BaseTool, ToolResult, _check_project_path, _handle_file_error


class FileReadTool(BaseTool):
    """Tool for reading files within project directories"""

    def __init__(self):
        super().__init__(
            "read_file",
            "Read the contents of a file within the project directory"
        )

    def execute(self, **kwargs) -> ToolResult:
        path = kwargs.get('path', '')
        max_lines = kwargs.get('max_lines', 100)
        try:
            path_check = _check_project_path(path)
            if isinstance(path_check, ToolResult):
                return path_check

            if not path_check.exists():
                return ToolResult(
                    ok=False,
                    error=f"File not found: {path}"
                )

            with open(path_check, 'r', encoding='utf-8', errors='ignore') as f:
                lines = f.readlines()[:max_lines]
                content = ''.join(lines)

                if len(lines) == max_lines and f.readline():
                    content += f"\n... (truncated after {max_lines} lines)"

            return ToolResult(
                ok=True,
                data=content
            )

        except Exception as e:
            return _handle_file_error(path, e)

    def get_schema(self) -> Dict[str, Any]:
        schema = super().get_schema()
        schema["parameters"]["properties"] = {
            "path": {
                "type": "string",
                "description": "Relative path to file within project directory"
            },
            "max_lines": {
                "type": "integer",
                "description": "Maximum number of lines to read",
                "default": 2000
            }
        }
        schema["parameters"]["required"] = ["path"]
        return schema


class DirectoryListTool(BaseTool):
    """Tool for listing directory contents"""

    def __init__(self):
        super().__init__(
            "list_dir",
            "List contents of a directory within the project"
        )

    def execute(self, path: str = ".", **kwargs) -> ToolResult:
        try:
            path_check = _check_project_path(path)
            if isinstance(path_check, ToolResult):
                return path_check

            if not path_check.is_dir():
                return ToolResult(
                    ok=False,
                    error=f"Not a directory: {path}"
                )

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
                "default": "."
            }
        }
        return schema


class FileEditTool(BaseTool):
    """Tool for editing files by replacing text content"""

    def __init__(self):
        super().__init__(
            "edit_file",
            "Edit files by replacing specific text content"
        )

    def execute(self, path: str = "", old_str: str = "", new_str: str = "", **kwargs) -> ToolResult:
        """Edit a file by replacing old_str with new_str"""
        if not path:
            return ToolResult(ok=False, error="File path is required")

        if not old_str:
            return ToolResult(ok=False, error="Old text to replace is required")

        if not new_str:
            return ToolResult(ok=False, error="New replacement text is required")

        try:
            path_check = _check_project_path(path)
            if isinstance(path_check, ToolResult):
                return path_check

            if not path_check.exists():
                return ToolResult(
                    ok=False,
                    error=f"File not found: {path}"
                )

            with open(path_check, 'r', encoding='utf-8') as f:
                content = f.read()

            if old_str not in content:
                return ToolResult(
                    ok=False,
                    error=f"Text not found in file: {old_str[:50]}..."
                )

            new_content = content.replace(old_str, new_str)

            with open(path_check, 'w', encoding='utf-8') as f:
                f.write(new_content)

            return ToolResult(
                ok=True,
                data=f"Successfully replaced text in {path}"
            )

        except Exception as e:
            return _handle_file_error(path, e)

    def get_schema(self) -> Dict[str, Any]:
        schema = super().get_schema()
        schema["parameters"]["properties"] = {
            "path": {
                "type": "string",
                "description": "Relative path to file within project directory"
            },
            "old_str": {
                "type": "string",
                "description": "Text to search for and replace"
            },
            "new_str": {
                "type": "string",
                "description": "Replacement text"
            }
        }
        schema["parameters"]["required"] = ["path", "old_str", "new_str"]
        return schema
