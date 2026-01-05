from __future__ import annotations

import re
from dataclasses import dataclass
from typing import Optional


@dataclass
class CitationMatch:
    index: int
    start: int
    end: int
    context_before: str
    context_after: str


@dataclass
class CitationValidationResult:
    valid: bool
    errors: list[str]
    warnings: list[str]
    citation_count: int


class CitationEngine:
    CITATION_PATTERN = re.compile(r"\[(\d+)\]")
    URL_PATTERN = re.compile(r"https?://\S+")

    def extract_inline_citations(self, text: str) -> list[CitationMatch]:
        matches = []
        for match in self.CITATION_PATTERN.finditer(text):
            index = int(match.group(1))
            matches.append(
                CitationMatch(
                    index=index,
                    start=match.start(),
                    end=match.end(),
                    context_before=text[max(0, match.start() - 50) : match.start()],
                    context_after=text[match.end() : min(len(text), match.end() + 50)],
                )
            )
        return matches

    def validate_citations(
        self,
        text: str,
        sources: list,
        citation_map: dict[str, int],
        min_required: int = 0,
    ) -> CitationValidationResult:
        errors = []
        warnings = []

        cited_indices = self.extract_inline_citations(text)

        for cm in cited_indices:
            source = None
            for s in sources:
                if citation_map.get(s.source_id) == cm.index:
                    source = s
                    break

            if not source:
                errors.append(f"Citation [{cm.index}] references non-existent source")

        if min_required > 0 and len(cited_indices) < min_required:
            errors.append(
                f"Required at least {min_required} citations, found {len(cited_indices)}"
            )

        paragraphs = text.split("\n\n")
        cited_paragraphs = sum(1 for p in paragraphs if self.CITATION_PATTERN.search(p))
        if len(paragraphs) > 2 and cited_paragraphs == 0:
            warnings.append("No citations found in answer body")

        return CitationValidationResult(
            valid=len(errors) == 0,
            errors=errors,
            warnings=warnings,
            citation_count=len(cited_indices),
        )

    def format_sources_block(self, sources: list, citation_map: dict[str, int]) -> str:
        if not sources:
            return ""

        lines = ["## Sources\n"]

        sorted_sources = sorted(
            sources, key=lambda s: citation_map.get(s.source_id, 999)
        )

        for source in sorted_sources:
            idx = citation_map.get(source.source_id, 0)
            if idx == 0:
                continue

            lines.append(f"[{idx}] {source.title}")

            if source.source_type.value == "web":
                lines.append(f"    URL: {source.locator}")
            elif source.source_type.value == "file":
                lines.append(f"    File: {source.locator}")
            elif source.source_type.value == "kiwix":
                lines.append(f"    Kiwix: {source.locator}")
            elif source.source_type.value == "command_output":
                lines.append(f"    Command: {source.locator}")
            elif source.source_type.value == "rag":
                lines.append(f"    RAG Index: {source.locator}")
            elif source.source_type.value == "artifact":
                lines.append(f"    Artifact: {source.locator}")

            if source.snippet:
                preview = (
                    source.snippet[:200] + "..."
                    if len(source.snippet) > 200
                    else source.snippet
                )
                lines.append(f"    Preview: {preview}")

            lines.append("")

        return "\n".join(lines)

    def format_tools_used_block(self, tool_calls: list) -> str:
        if not tool_calls:
            return ""

        counts: dict[str, int] = {}
        for tc in tool_calls:
            counts[tc.name] = counts.get(tc.name, 0) + 1

        lines = ["## Tools Used\n"]
        for tool, count in sorted(counts.items()):
            lines.append(f"- {tool} ×{count}")

        return "\n".join(lines)

    def format_artifacts_block(self, artifacts: list) -> str:
        if not artifacts:
            return ""

        lines = ["## Artifacts\n"]
        for artifact in artifacts:
            lines.append(f"- {artifact.path}")
            if artifact.description:
                lines.append(f"    {artifact.description}")
        lines.append("")

        return "\n".join(lines)

    def format_pipeline_summary(self, step_results: list) -> str:
        if not step_results:
            return ""

        lines = ["## Pipeline Execution\n"]
        for result in step_results:
            status = "✓" if result.ok else "✗"
            lines.append(f"{status} {result.step_name}: {result.notes}")
            if result.tool_calls:
                lines.append(
                    f"    Tools: {', '.join(tc.name for tc in result.tool_calls)}"
                )
            if result.sources_added:
                lines.append(f"    Sources: {len(result.sources_added)} added")
        lines.append("")

        return "\n".join(lines)

    def format_step_history(self, step_history: list) -> str:
        if not step_history:
            return ""

        lines = ["## Execution Steps\n"]
        for step in step_history:
            status = "✓" if step.get("ok") else "✗"
            lines.append(f"{status} {step.get('step_name')} ({step.get('step_type')})")
        lines.append("")

        return "\n".join(lines)

    def inject_citations_into_text(
        self,
        text: str,
        sources: list,
        citation_map: dict[str, int],
        citation_hints: Optional[dict[str, str]] = None,
    ) -> str:
        result = text
        for source in sources:
            idx = citation_map.get(source.source_id)
            if idx is None:
                continue

            if citation_hints and source.source_id in citation_hints:
                hint = citation_hints[source.source_id]
                pattern = f"({re.escape(hint)})"
                replacement = f"\\1 [{idx}]"
                result = re.sub(pattern, replacement, result, count=1)

        return result

    def extract_urls_from_text(self, text: str) -> list[str]:
        return self.URL_PATTERN.findall(text)

    def check_url_coverage(
        self, text: str, sources: list, citation_map: dict[str, int]
    ) -> tuple[int, int]:
        urls_in_text = self.extract_urls_from_text(text)
        cited_sources = set()

        for source in sources:
            idx = citation_map.get(source.source_id)
            if (
                idx
                and self.CITATION_PATTERN.search(text)
                and any(str(idx) in line for line in text.split("\n"))
            ):
                cited_sources.add(source.source_id)

        return len(urls_in_text), len(cited_sources)
