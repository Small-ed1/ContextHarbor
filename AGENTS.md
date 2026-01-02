# AGENTS.md

Guidelines for agentic coding assistants working on Router Phase 1.

## Build, Lint, and Test Commands

### Environment Setup
```bash
python -m venv .venv && source .venv/bin/activate && pip install -r requirements.txt
```

### Syntax Checking
```bash
make fmt                       # Verify syntax with compileall
python -m compileall agent     # Direct command
```

### Testing
```bash
make test                     # Quick test run (pytest)
python -m pytest tests/ -v     # All tests with output
python -m pytest tests/test_router.py -v                # Specific file
python -m pytest tests/test_router.py::TestRouter::test_override -v  # Single test
python -m pytest tests/ -k "test_router" -v             # Pattern match
```

## Code Style

### Imports
```python
from __future__ import annotations
import os
from pathlib import Path
from typing import List, Optional, Any

from pydantic import BaseModel, Field

from .models import Mode
from .router import route
```
Order: stdlib → third-party → relative (`.` prefix). No wildcard imports.

### Type Hints
- Modern syntax preferred: `str | None`, `list[str]`, `dict[str, str]`
- All function parameters/returns must have type hints
- Use `Any`, `Dict`, `List`, `Optional`, `Tuple` from `typing`

### Naming
- Files: `snake_case.py`
- Classes: `PascalCase`
- Functions/methods: `snake_case`
- Constants: `UPPER_SNAKE_CASE`
- Private: prefix `_` (e.g., `_score()`)

### Dataclasses
```python
@dataclass
class RunContext:
    objective: str           # required first
    decision: RouteDecision
    project: str = "default"  # defaults after
    messages: List[Message] = field(default_factory=list)
```
Use `@dataclass(frozen=True)` for immutable configs.

### Pydantic Models
```python
class RouteDecision(BaseModel):
    mode: Mode
    confidence: float = 0.0
    signals: List[str] = Field(default_factory=list)
```
Validate with `.model_validate()`, export with `.model_dump()`.

### Error Handling
- Custom exceptions inherit from `RuntimeError`
- Use descriptive messages: `raise BudgetExceeded(f"{cur}/{lim}")`
- Use `raise_for_status()` on HTTP responses
- Never expose secrets in error messages

### Code Organization
- Constants/compiled regex at module level before functions
- Helper functions before public functions
- Keep functions focused (~50 lines max)

### Testing
- Use `unittest` framework in `tests/` directory
- Files: `test_*.py`, functions: `test_*` (no args)
- Import directly: `from agent.router import route`

### Patterns
- `datetime.now(timezone.utc)` for UTC timestamps
- `Path` objects: `p.read_text()`, `p.write_text()`
- `json.dumps(obj, indent=2, ensure_ascii=False)` for JSON
- `os.environ.get()` with defaults for env vars

## Architecture

### Core Components
- **Router** (`agent/router.py`): Mode selection (WRITE/EDIT/RESEARCH/HYBRID)
- **Controller** (`agent/controller.py`): Tool execution coordination
- **Workers** (`agent/worker_*.py`): AI model interactions
- **Tools** (`agent/tools.py`): 13 tools (file ops, search, GitHub, etc.)
- **Pipeline** (`agent/pipeline.py`): Multi-step execution (10 step types)
- **Citation** (`agent/citation.py`): Source tracking and citation formatting

### Data Flow
Query → Router (mode) → Controller (pipeline/worker) → Tools → Synthesize → Output

### Interfaces
```bash
./run_webui.sh    # FastAPI web UI (port 8000)
./chat            # Console chat
./agt "query"     # CLI agent
```

### Tool Development
1. Inherit from `BaseTool`, implement `execute(**kwargs) -> ToolResult`
2. Return `ToolResult(ok, data, sources=[], artifacts=[])`
3. Register in `Controller.__init__()`

### GitHub Tools
- `github_search`: Search repos, code, issues, PRs
- `github_fetch`: Get file contents from repositories

## Security
- All file ops sandboxed to `projects/` directory
- No secrets/API keys in code or error messages
- Tool timeouts and resource constraints enforced
