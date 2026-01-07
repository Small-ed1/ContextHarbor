from __future__ import annotations

from ..research.iterative_research import IterativeResearchToolClass
from .agent_tools import (BaseTool, DirectoryListTool, FileEditTool,
                          FileReadTool, GitHubFetchTool, GitHubSearchTool,
                          KiwixQueryTool, ListSkillsTool, PackageTool,
                          RagSearchTool, SkillTool, SystemdTool, TerminalTool,
                          ToolResult, UrlFetchTool, WebSearchTool,
                          _check_project_path, _handle_file_error)
from .duckduckgo_search import DuckDuckGoSearchTool


def get_all_tools():
    """Get all available tools"""
    return [
        FileReadTool(),
        DirectoryListTool(),
        KiwixQueryTool(),
        WebSearchTool(),
        UrlFetchTool(),
        RagSearchTool(),
        TerminalTool(),
        SystemdTool(),
        PackageTool(),
        FileEditTool(),
        SkillTool(),
        ListSkillsTool(),
        GitHubSearchTool(),
        GitHubFetchTool(),
        DuckDuckGoSearchTool(),
        IterativeResearchToolClass(),
    ]


__all__ = [
    "BaseTool",
    "FileReadTool",
    "DirectoryListTool",
    "KiwixQueryTool",
    "WebSearchTool",
    "UrlFetchTool",
    "RagSearchTool",
    "ToolResult",
    "TerminalTool",
    "SystemdTool",
    "PackageTool",
    "FileEditTool",
    "SkillTool",
    "ListSkillsTool",
    "GitHubSearchTool",
    "GitHubFetchTool",
    "DuckDuckGoSearchTool",
    "IterativeResearchToolClass",
    "_handle_file_error",
    "_check_project_path",
    "get_all_tools",
]
