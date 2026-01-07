"""
DuckDuckGo Search Tool
Web search functionality using DuckDuckGo search engine.
Adapted from ollama_search_tool for integration into the agent system.
"""

import logging
from typing import List, Optional, Tuple

try:
    from ddgs import DDGS
except ImportError:
    DDGS = None  # type: ignore

logger = logging.getLogger(__name__)


def is_safe_url(url: str) -> bool:
    """Check if URL is safe and suitable for scraping."""
    try:
        from urllib.parse import urlparse

        parsed = urlparse(url)

        # Basic validation
        if not parsed.scheme or not parsed.netloc:
            return False

        if parsed.scheme not in ["http", "https"]:
            return False

        # Skip common non-content domains
        skip_domains = [
            "google",
            "facebook",
            "twitter",
            "instagram",
            "youtube",
            "amazon",
            "ebay",
            "pinterest",
            "linkedin",
        ]
        if any(domain in parsed.netloc for domain in skip_domains):
            return False

        # Skip file extensions that aren't HTML
        skip_extensions = [
            ".pdf",
            ".doc",
            ".docx",
            ".xls",
            ".xlsx",
            ".ppt",
            ".pptx",
            ".zip",
            ".rar",
            ".7z",
            ".tar",
            ".gz",
        ]
        if any(url.lower().endswith(ext) for ext in skip_extensions):
            return False

        return True

    except Exception:
        return False


class DuckDuckGoSearchTool:
    """Web search tool using DuckDuckGo."""

    def __init__(self, timeout: int = 10):
        """Initialize the search tool.

        Args:
            timeout: Search timeout in seconds
        """
        self.name = "duckduckgo_search"
        self.description = "Search the web using DuckDuckGo"
        self.timeout = timeout
        if DDGS is None:
            raise ImportError(
                "duckduckgo-search package is required for DuckDuckGo search"
            )

    def search(
        self, query: str, limit: int = 5, timeout: Optional[int] = None
    ) -> List[Tuple[str, str]]:
        """Search the web using DuckDuckGo.

        Args:
            query: Search query string
            limit: Maximum number of results to return
            timeout: Search timeout in seconds (uses instance default if None)

        Returns:
            List of (title, url) tuples

        Raises:
            ImportError: If duckduckgo-search is not installed
            Exception: If search fails
        """
        if timeout is None:
            timeout = self.timeout

        try:
            logger.info(f"Searching DuckDuckGo for '{query}' with limit {limit}")

            if DDGS is None:
                raise ImportError("duckduckgo-search package not available")

            ddgs = DDGS()
            results = list(ddgs.text(query, max_results=limit))

            if not results:
                logger.warning(f"No search results found for query: {query}")
                return []

            # Validate and filter results
            valid_results = []
            for result in results:
                title = result.get("title", "").strip()
                url = result.get("href", "").strip()

                if title and url and is_safe_url(url):
                    valid_results.append((title, url))
                else:
                    logger.debug(
                        f"Skipping invalid result: title='{title}', url='{url}'"
                    )

            logger.info(f"Found {len(valid_results)} valid search results")
            return valid_results[:limit]

        except Exception as e:
            logger.error(f"DuckDuckGo search failed: {e}")
            raise


# Global instance for easy access
_duckduckgo_search_tool = None


def get_duckduckgo_search_tool() -> DuckDuckGoSearchTool:
    """Get or create the global DuckDuckGo search tool instance."""
    global _duckduckgo_search_tool
    if _duckduckgo_search_tool is None:
        _duckduckgo_search_tool = DuckDuckGoSearchTool()
    return _duckduckgo_search_tool
