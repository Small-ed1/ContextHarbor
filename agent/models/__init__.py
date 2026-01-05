from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field


class Mode(str, Enum):
    WRITE = "WRITE"
    EDIT = "EDIT"
    RESEARCH = "RESEARCH"
    HYBRID = "HYBRID"


class StepType(Enum):
    UNDERSTAND = "understand"
    PLAN = "plan"
    GATHER = "gather"
    VERIFY = "verify"
    SYNTHESIZE = "synthesize"
    FINALIZE = "finalize"
    OUTLINE = "outline"
    DRAFT = "draft"
    ANSWER = "answer"
    EXECUTE = "execute"


class SourceType(Enum):
    WEB = "web"
    FILE = "file"
    KIWIX = "kiwix"
    RAG = "rag"
    COMMAND = "command_output"
    ARTIFACT = "artifact"


class ArtifactType(Enum):
    FILE = "file"
    PATCH = "patch"
    DIFF = "diff"
    CODE = "code"
    TEXT = "text"


class ToolBudget(BaseModel):
    limits: Dict[str, int] = Field(default_factory=dict)
    time_limit_s: Optional[int] = None


class StopConditions(BaseModel):
    min_sources: Optional[int] = None
    max_words: Optional[int] = None
    max_tool_calls_total: Optional[int] = None
    extras: Dict[str, Any] = Field(default_factory=dict)


class RouteDecision(BaseModel):
    mode: Mode
    confidence: float = 0.0
    warning: Optional[str] = None
    tool_budget: ToolBudget
    stop_conditions: StopConditions
    signals: List[str] = Field(default_factory=list)
    override_used: bool = False
    recommended_tools: List[str] = Field(default_factory=list)
    recommended_steps: List[str] = Field(default_factory=list)
    depth: str = "standard"


@dataclass(frozen=True)
class Source:
    source_id: str
    tool: str
    source_type: SourceType
    title: str
    locator: str
    snippet: str
    retrieved_at: datetime = field(default_factory=lambda: datetime.now())
    confidence: float = 1.0
    artifact_path: str | None = None

    @staticmethod
    def normalize_url(url: str) -> str:
        from urllib.parse import urlparse

        parsed = urlparse(url)
        normalized = parsed._replace(query="", fragment="")
        return normalized.geturl()

    @staticmethod
    def generate_id(tool: str, locator: str, title: str) -> str:
        import hashlib

        normalized = Source.normalize_url(locator)
        content = f"{tool}:{normalized}:{title}"
        return hashlib.md5(content.encode()).hexdigest()[:16]


@dataclass
class Artifact:
    artifact_id: str
    artifact_type: ArtifactType
    path: str
    content: str | None = None
    description: str = ""
    created_at: datetime = field(default_factory=lambda: datetime.now())


@dataclass
class ToolResult:
    ok: bool
    data: Any = None
    sources: List[Source] = field(default_factory=list)
    artifacts: List[Artifact] = field(default_factory=list)
    error: str | None = None
    logs: List[str] = field(default_factory=list)


@dataclass
class ToolCall:
    name: str
    parameters: Dict
    result: Optional[ToolResult] = None
    timestamp: datetime = field(default_factory=lambda: datetime.now())
    step_name: str = ""
    tool_result_id: Optional[str] = None


@dataclass
class StepResult:
    step_name: str
    step_type: StepType
    ok: bool
    notes: str = ""
    tool_calls: List[ToolCall] = field(default_factory=list)
    sources_added: List[str] = field(default_factory=list)
    citations_added: List[int] = field(default_factory=list)
    artifacts_created: List[str] = field(default_factory=list)


@dataclass
class StepConfig:
    step_type: StepType
    enabled: bool = True
    max_iterations: int = 5
    budget: int = 5
    stop_condition: str = "budget"


@dataclass
class BudgetConfig:
    global_max: int = 12
    per_tool: Dict[str, int] = field(default_factory=dict)
    per_step: Dict[str, int] = field(default_factory=dict)

    @staticmethod
    def default_for_mode(mode) -> BudgetConfig:
        mode_str = str(mode).upper() if mode else ""

        if mode_str == "CHAT":
            return BudgetConfig(global_max=5, per_tool={"web_search": 2})
        elif mode_str == "WRITE":
            return BudgetConfig(global_max=8, per_tool={"read_file": 3, "edit_file": 2})
        elif mode_str == "EDIT":
            return BudgetConfig(global_max=6, per_tool={"read_file": 2, "edit_file": 2})
        elif mode_str == "HYBRID":
            return BudgetConfig(
                global_max=12,
                per_tool={"web_search": 3, "kiwix_query": 3, "fetch_url": 2},
            )
        elif mode_str == "RESEARCH":
            return BudgetConfig(
                global_max=15,
                per_tool={"web_search": 5, "kiwix_query": 5, "fetch_url": 3},
            )
        else:
            return BudgetConfig()


@dataclass
class Citation:
    index: int
    source_id: str
    context: str = ""
    inline_text: str = ""


@dataclass
class CitationValidationResult:
    valid: bool
    errors: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)
    citation_count: int = 0
