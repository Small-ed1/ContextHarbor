from __future__ import annotations

import re
from dataclasses import dataclass, field
from typing import List, Optional

from .models import Mode

URL_RE = re.compile(r"https?://\S+")


@dataclass
class VerificationResult:
    passed: bool
    errors: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)
    retry_hint: Optional[str] = None


def _count_inline_urls(text: str) -> int:
    return len(URL_RE.findall(text or ""))


def verify(ctx, output_text: str) -> VerificationResult:
    mode = ctx.decision.mode
    stops = ctx.decision.stop_conditions

    vr = VerificationResult(passed=True)

    if stops.max_words is not None:
        words = len((output_text or "").split())
        if words > stops.max_words:
            vr.passed = False
            vr.errors.append(
                f"Output too long: {words} words > max_words={stops.max_words}"
            )

    if mode in (Mode.RESEARCH, Mode.HYBRID):
        min_sources = stops.min_sources or 3

        if len(ctx.sources) < min_sources:
            vr.passed = False
            vr.errors.append(
                f"Missing sources: have {len(ctx.sources)} < min_sources={min_sources}"
            )

        acceptable = 0
        for s in ctx.sources:
            if not s.locator or not s.locator.startswith("http"):
                vr.passed = False
                vr.errors.append("Source missing valid URL")
                continue

            if s.locator.startswith("http"):
                acceptable += 1

        if acceptable < min_sources:
            if "uncertaint" not in (output_text or "").lower():
                vr.passed = False
                vr.errors.append(
                    f"Not enough valid sources: acceptable={acceptable} < min_sources={min_sources} "
                    "and output does not note uncertainty."
                )
                vr.retry_hint = "Use fewer retail/SEO sources; prefer .gov/.edu/official docs; add an uncertainty note if sources are weak."

        if _count_inline_urls(output_text) < min_sources:
            vr.warnings.append(
                "Not enough inline URLs in summary (expected at least min_sources)."
            )

    return vr
