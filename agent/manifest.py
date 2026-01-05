from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path


@dataclass
class ProjectManifest:
    root: Path
    project: str = "default"

    @property
    def bible_dir(self) -> Path:
        return self.root / "bible"

    @property
    def drafts_dir(self) -> Path:
        return self.root / "drafts"

    @property
    def research_dir(self) -> Path:
        return self.root / "research"


def load_manifest(project: str = "default") -> ProjectManifest:
    root = Path("projects") / project
    root.mkdir(parents=True, exist_ok=True)

    (root / "bible").mkdir(exist_ok=True)
    (root / "drafts").mkdir(exist_ok=True)
    (root / "research").mkdir(exist_ok=True)
    (root / "rag").mkdir(exist_ok=True)
    (root / "runs").mkdir(exist_ok=True)

    return ProjectManifest(root=root, project=project)
