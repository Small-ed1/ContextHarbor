import re
from typing import List


class IntentDecoder:
    """Decodes user intent from query to select appropriate LLM model."""

    def decode_intent(self, query: str) -> str:
        query_lower = query.lower()

        # Code-related queries
        if any(
            keyword in query_lower
            for keyword in [
                "code",
                "function",
                "class",
                "debug",
                "programming",
                "script",
                "api",
                "algorithm",
            ]
        ):
            return "codellama:7b"

        # Research or complex analysis
        if any(
            keyword in query_lower
            for keyword in [
                "research",
                "analyze",
                "explain",
                "how does",
                "why",
                "compare",
                "pros cons",
            ]
        ):
            return "llama3.1:8b"

        # Creative or open-ended
        if any(
            keyword in query_lower
            for keyword in ["create", "design", "imagine", "story", "poem", "creative"]
        ):
            return "llama3.2:latest"

        # Default to general purpose
        return "llama3.2:latest"
