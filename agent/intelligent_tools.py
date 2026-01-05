from __future__ import annotations

import json
import re
from dataclasses import dataclass
from typing import Any, Dict, List, Tuple

from .models import Mode
from .tools.base import BaseTool


@dataclass
class ToolMatch:
    """Represents a tool match with confidence score and reasoning"""

    tool_name: str
    confidence: float
    reasoning: str
    priority: int = 0


class IntelligentToolSelector:
    """Intelligent tool selection using semantic analysis and pattern matching"""

    def __init__(self, tools: List[BaseTool]):
        self.tools = {tool.name: tool for tool in tools}
        self.tool_patterns = self._build_tool_patterns()
        self.context_keywords = self._build_context_keywords()

    def _build_tool_patterns(self) -> Dict[str, List[Dict[str, Any]]]:
        """Build semantic patterns for each tool"""
        return {
            "read_file": [
                {
                    "patterns": [
                        "read",
                        "open",
                        "view",
                        "examine",
                        "check",
                        "look at",
                        "what's in",
                    ],
                    "keywords": ["file", "code", "document"],
                    "weight": 0.8,
                },
                {
                    "patterns": ["show me", "display", "content of"],
                    "keywords": ["file", "code"],
                    "weight": 0.7,
                },
            ],
            "list_dir": [
                {
                    "patterns": [
                        "list",
                        "show",
                        "what's in",
                        "directory",
                        "folder",
                        "ls",
                        "dir",
                    ],
                    "keywords": ["files", "contents", "structure"],
                    "weight": 0.8,
                },
                {
                    "patterns": ["explore", "browse", "navigate"],
                    "keywords": ["directory", "folder"],
                    "weight": 0.6,
                },
            ],
            "write_file": [
                {
                    "patterns": [
                        "write",
                        "create",
                        "make",
                        "generate",
                        "save",
                        "output",
                    ],
                    "keywords": ["file", "document", "code"],
                    "weight": 0.8,
                },
                {
                    "patterns": ["store", "save to", "export to"],
                    "keywords": ["file"],
                    "weight": 0.7,
                },
            ],
            "edit_file": [
                {
                    "patterns": [
                        "edit",
                        "modify",
                        "change",
                        "update",
                        "fix",
                        "improve",
                    ],
                    "keywords": ["file", "code", "document"],
                    "weight": 0.8,
                },
                {
                    "patterns": ["replace", "change", "update", "fix"],
                    "keywords": ["in file", "in code"],
                    "weight": 0.7,
                },
            ],
            "web_search": [
                {
                    "patterns": [
                        "search",
                        "find",
                        "look up",
                        "google",
                        "research",
                        "what is",
                        "who is",
                    ],
                    "keywords": ["online", "web", "internet"],
                    "weight": 0.8,
                },
                {
                    "patterns": ["latest", "current", "news", "recent"],
                    "keywords": ["information", "data"],
                    "weight": 0.7,
                },
            ],
            "kiwix_query": [
                {
                    "patterns": [
                        "wikipedia",
                        "encyclopedia",
                        "reference",
                        "lookup",
                        "define",
                    ],
                    "keywords": ["offline", "knowledge"],
                    "weight": 0.8,
                },
                {
                    "patterns": ["what is", "who is", "explain", "tell me about"],
                    "keywords": [],
                    "weight": 0.6,
                },
            ],
            "github_search": [
                {
                    "patterns": [
                        "github",
                        "repository",
                        "repo",
                        "code search",
                        "open source",
                    ],
                    "keywords": ["code", "project"],
                    "weight": 0.8,
                },
                {
                    "patterns": ["find code", "search repos", "git"],
                    "keywords": ["code", "project"],
                    "weight": 0.7,
                },
            ],
            "fetch_url": [
                {
                    "patterns": ["fetch", "download", "get", "grab", "retrieve"],
                    "keywords": ["url", "website", "page"],
                    "weight": 0.8,
                },
                {
                    "patterns": ["access", "visit", "load"],
                    "keywords": ["url", "website"],
                    "weight": 0.6,
                },
            ],
            "run_command": [
                {
                    "patterns": [
                        "run",
                        "execute",
                        "command",
                        "shell",
                        "terminal",
                        "bash",
                    ],
                    "keywords": ["system", "os"],
                    "weight": 0.8,
                },
                {
                    "patterns": ["install", "build", "compile", "test"],
                    "keywords": ["command"],
                    "weight": 0.7,
                },
            ],
            "rag_search": [
                {
                    "patterns": ["search", "find", "lookup", "context"],
                    "keywords": ["local", "documents", "knowledge base"],
                    "weight": 0.8,
                },
                {
                    "patterns": ["semantic search", "vector search"],
                    "keywords": ["similarity", "meaning"],
                    "weight": 0.9,
                },
            ],
            "duckduckgo_search": [
                {
                    "patterns": ["search", "find", "lookup", "duckduckgo"],
                    "keywords": ["web", "online", "internet"],
                    "weight": 0.8,
                },
                {
                    "patterns": ["research", "investigate", "explore online"],
                    "keywords": ["sources", "information"],
                    "weight": 0.7,
                },
            ],
            "iterative_research": [
                {
                    "patterns": ["deep research", "iterative", "comprehensive research"],
                    "keywords": ["analysis", "thorough", "detailed"],
                    "weight": 0.9,
                },
                {
                    "patterns": ["research with llm", "ai research", "smart research"],
                    "keywords": ["intelligent", "automated", "refined"],
                    "weight": 0.8,
                },
            ],
        }

    def _build_context_keywords(self) -> Dict[Mode, List[str]]:
        """Build context-specific keyword sets"""
        return {
            Mode.RESEARCH: [
                "find",
                "search",
                "research",
                "investigate",
                "verify",
                "evidence",
                "sources",
                "data",
                "statistics",
                "cite",
                "reference",
            ],
            Mode.WRITE: [
                "write",
                "create",
                "generate",
                "compose",
                "draft",
                "make",
                "produce",
                "author",
                "content",
                "text",
            ],
            Mode.EDIT: [
                "edit",
                "revise",
                "improve",
                "modify",
                "update",
                "fix",
                "correct",
                "refine",
                "polish",
                "enhance",
            ],
            Mode.HYBRID: [
                "explain",
                "analyze",
                "summarize",
                "overview",
                "help me understand",
                "break down",
                "compare",
                "evaluate",
            ],
        }

    def _analyze_text_pattern(self, text: str, tool_name: str) -> Tuple[float, str]:
        """Analyze text for patterns matching a specific tool"""
        if tool_name not in self.tool_patterns:
            return 0.0, "Tool not recognized"

        text_lower = text.lower()
        total_score = 0.0
        reasoning_parts = []

        for pattern_set in self.tool_patterns[tool_name]:
            pattern_score = 0.0
            pattern_matches = []
            keyword_matches = []

            # Check pattern matches
            for pattern in pattern_set["patterns"]:
                if pattern in text_lower:
                    pattern_matches.append(pattern)
                    pattern_score += 1.0

            # Check keyword matches
            for keyword in pattern_set["keywords"]:
                if keyword in text_lower:
                    keyword_matches.append(keyword)
                    pattern_score += 0.5

            # Apply weight
            weighted_score = (
                pattern_score / len(pattern_set["patterns"])
            ) * pattern_set["weight"]
            total_score += weighted_score

            if pattern_matches or keyword_matches:
                reasoning_parts.append(
                    f"Matches: {pattern_matches + keyword_matches} (score: {weighted_score:.2f})"
                )

        return (
            min(total_score, 1.0),
            "; ".join(reasoning_parts) if reasoning_parts else "No matches",
        )

    def _analyze_mode_context(self, text: str, mode: Mode) -> Dict[str, float]:
        """Analyze text for mode-specific context"""
        if mode not in self.context_keywords:
            return {}

        text_lower = text.lower()
        mode_score = {}

        for tool_name in self.tools.keys():
            tool_score = 0.0
            for keyword in self.context_keywords[mode]:
                if keyword in text_lower:
                    tool_score += 0.1

            # Bonus if tool aligns with mode
            if mode == Mode.RESEARCH and tool_name in [
                "web_search",
                "kiwix_query",
                "github_search",
                "fetch_url",
            ]:
                tool_score += 0.3
            elif mode == Mode.WRITE and tool_name in [
                "write_file",
                "edit_file",
                "read_file",
            ]:
                tool_score += 0.3
            elif mode == Mode.EDIT and tool_name in [
                "edit_file",
                "read_file",
                "list_dir",
            ]:
                tool_score += 0.3
            elif mode == Mode.HYBRID:  # General purpose
                tool_score += 0.1

            mode_score[tool_name] = min(tool_score, 0.5)  # Cap mode bonus

        return mode_score

    def _analyze_semantic_structure(self, text: str) -> Dict[str, float]:
        """Analyze semantic structure for implicit tool needs"""
        scores = {}
        text_lower = text.lower()

        # File operation indicators
        if any(
            word in text_lower
            for word in ["file", "code", "document", "script", "program"]
        ):
            if any(word in text_lower for word in ["read", "open", "view", "examine"]):
                scores["read_file"] = 0.4
            if any(
                word in text_lower for word in ["write", "create", "make", "generate"]
            ):
                scores["write_file"] = 0.4
            if any(
                word in text_lower for word in ["edit", "modify", "change", "update"]
            ):
                scores["edit_file"] = 0.4
            if any(
                word in text_lower for word in ["list", "show", "directory", "folder"]
            ):
                scores["list_dir"] = 0.4

        # Web operation indicators
        if any(
            word in text_lower for word in ["search", "find", "look up", "research"]
        ):
            scores["web_search"] = 0.3
            scores["kiwix_query"] = 0.2

        # URL indicators
        if re.search(r"https?://\S+", text_lower):
            scores["fetch_url"] = 0.8
            scores["web_search"] = 0.1

        # GitHub indicators
        if any(word in text_lower for word in ["github", "repo", "repository", "git"]):
            scores["github_search"] = 0.6

        # Command indicators
        if any(
            word in text_lower
            for word in ["run", "execute", "command", "install", "build"]
        ):
            scores["run_command"] = 0.5

        return scores

    def _prioritize_tools(
        self, matches: List[ToolMatch], mode: Mode
    ) -> List[ToolMatch]:
        """Prioritize tools based on confidence and mode"""
        # Sort by confidence, then priority
        matches.sort(key=lambda x: (x.confidence, x.priority), reverse=True)

        # Apply mode-specific prioritization
        if mode == Mode.RESEARCH:
            # Prioritize research tools
            research_tools = [
                "web_search",
                "kiwix_query",
                "github_search",
                "fetch_url",
                "rag_search",
            ]
            for match in matches:
                if match.tool_name in research_tools:
                    match.priority += 2
        elif mode == Mode.WRITE:
            # Prioritize file tools
            file_tools = ["read_file", "write_file", "edit_file", "list_dir"]
            for match in matches:
                if match.tool_name in file_tools:
                    match.priority += 2
        elif mode == Mode.EDIT:
            # Prioritize file operation tools
            edit_tools = ["read_file", "edit_file", "list_dir"]
            for match in matches:
                if match.tool_name in edit_tools:
                    match.priority += 2

        # Resort with priorities
        matches.sort(
            key=lambda x: (x.confidence + x.priority * 0.1, x.priority), reverse=True
        )
        return matches

    def select_tools(self, objective: str, mode: Mode, max_tools: int = 5) -> List[str]:
        """Select appropriate tools for the given objective"""
        if not self.tools:
            return []

        matches = []

        for tool_name in self.tools.keys():
            # Pattern-based analysis
            pattern_score, reasoning = self._analyze_text_pattern(objective, tool_name)

            # Mode context analysis
            mode_context_scores = self._analyze_mode_context(objective, mode)
            mode_score = mode_context_scores.get(tool_name, 0.0)

            # Semantic structure analysis
            semantic_scores = self._analyze_semantic_structure(objective)
            semantic_score = semantic_scores.get(tool_name, 0.0)

            # Calculate total score
            total_score = pattern_score + mode_score + semantic_score

            if total_score > 0.1:  # Threshold for relevance
                match = ToolMatch(
                    tool_name=tool_name,
                    confidence=min(total_score, 1.0),
                    reasoning=f"Pattern: {reasoning}; Mode bonus: {mode_score:.2f}; Semantic: {semantic_score:.2f}",
                )
                matches.append(match)

        # Prioritize and limit tools
        prioritized = self._prioritize_tools(matches, mode)
        selected_tools = [match.tool_name for match in prioritized[:max_tools]]

        # Always include some baseline tools for certain modes
        if mode == Mode.RESEARCH and not any(
            t in selected_tools for t in ["web_search", "kiwix_query"]
        ):
            selected_tools.insert(0, "web_search")

        return selected_tools

    def get_tool_reasoning(self, objective: str, mode: Mode) -> Dict[str, str]:
        """Get reasoning for tool selection"""
        reasoning = {}

        for tool_name in self.tools.keys():
            pattern_score, pattern_reasoning = self._analyze_text_pattern(
                objective, tool_name
            )
            if pattern_score > 0.1:
                reasoning[tool_name] = pattern_reasoning

        return reasoning
