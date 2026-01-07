"""
Iterative Research Tool
Research functionality with LLM-driven query refinement and iterative analysis.
Adapted from ollama_search_tool for integration into the agent system.
"""

import asyncio
import logging
import time
from typing import Any, Dict, List, Optional, Tuple, cast

from ..ollama_client import GenerationRequest, OllamaClient, OllamaConfig
from ..tools.agent_tools import BaseTool, ToolResult
from ..tools.duckduckgo_search import (DuckDuckGoSearchTool,
                                       get_duckduckgo_search_tool)
from .web_scraper import ScrapingConfig, SearchQuery, WebScraper

try:
    from ...utils.memory_manager import MemoryManager
except ImportError:
    MemoryManager = None
    MemoryManager = None

logger = logging.getLogger(__name__)


class IterativeResearchTool:
    """Tool for performing iterative web research with LLM refinement."""

    def __init__(
        self,
        ollama_client: OllamaClient,
        web_scraper: WebScraper,
        memory_manager: Any,
        duckduckgo_tool: Optional[DuckDuckGoSearchTool] = None,
    ):
        """Initialize the iterative research tool.

        Args:
            ollama_client: Ollama client for LLM interactions
            web_scraper: Web scraper for content extraction
            memory_manager: Memory manager for resource monitoring
            duckduckgo_tool: DuckDuckGo search tool (optional, will create if None)
        """
        self.ollama_client = ollama_client
        self.web_scraper = web_scraper
        self.memory_manager = memory_manager
        self.duckduckgo_tool = duckduckgo_tool or get_duckduckgo_search_tool()

    async def research_topic(
        self,
        query: str,
        model: str = "llama3.2:3b",
        max_iterations: int = 3,
        search_limit: int = 5,
        ollama_timeout: int = 60,
        deep_research: bool = False,
    ) -> str:
        """Perform iterative web research with LLM analysis and refinement.

        Args:
            query: Initial research query
            model: Ollama model to use
            max_iterations: Maximum number of research iterations
            search_limit: Number of search results per query
            ollama_timeout: Timeout for Ollama requests
            deep_research: Enable deep research mode with more iterations

        Returns:
            Comprehensive research analysis

        Raises:
            Exception: If research fails
        """
        try:
            logger.info(
                f"Starting iterative research on '{query}' using model '{model}'"
            )

            current_query = query
            context_parts: List[str] = []
            analysis = ""
            max_iters = 10 if deep_research else max_iterations
            iteration = 0
            start_time = time.time()
            time_limit = 1800 if deep_research else None  # 30 minutes for deep research

            while iteration < max_iters and (
                time_limit is None or time.time() - start_time < time_limit
            ):
                logger.info(f"Research iteration {iteration + 1}/{max_iters}")

                # Step 1: Break down query with LLM (first iteration only)
                if iteration == 0 and current_query == query:
                    logger.info("Breaking down initial query with LLM")
                    breakdown_queries = await self._break_down_query(
                        query, model, ollama_timeout
                    )
                    if not breakdown_queries:
                        breakdown_queries = [query]
                else:
                    breakdown_queries = [current_query]

                # Step 2: Search for each query
                all_search_results = []
                for sq in breakdown_queries:
                    logger.info(f"Searching for: '{sq}'")
                    try:
                        results = self.duckduckgo_tool.search(sq, limit=search_limit)
                        all_search_results.extend(results)
                    except Exception as e:
                        logger.warning(f"Search failed for '{sq}': {e}")
                        continue

                # Remove duplicates
                seen_urls = set()
                search_results = []
                for title, url in all_search_results:
                    if url not in seen_urls:
                        search_results.append((title, url))
                        seen_urls.add(url)

                search_results = search_results[: search_limit * len(breakdown_queries)]

                if not search_results:
                    logger.warning("No search results found")
                    if iteration == 0:
                        return "No search results found for the given query."
                    else:
                        break

                # Step 3: Fetch and extract content
                logger.info(f"Fetching content from {len(search_results)} sources")
                new_context_parts: List[str] = []

                for title, url in search_results:
                    try:
                        # Use web scraper to fetch content
                        content = await self._fetch_content(url)
                        if content.strip():
                            source_num = len(context_parts) + len(new_context_parts) + 1
                            new_context_parts.append(
                                f"SOURCE {source_num}: {title}\n{content}"
                            )
                            logger.debug(f"Successfully fetched content from {url}")
                        else:
                            logger.warning(f"No content extracted from {url}")
                    except Exception as e:
                        logger.warning(f"Failed to fetch content from {url}: {e}")
                        continue

                if not new_context_parts and iteration == 0:
                    logger.warning("No content could be fetched")
                    return "Unable to fetch content from search results."

                context_parts.extend(new_context_parts)

                # Step 4: Analyze with LLM
                context = "\n\n".join(context_parts)
                logger.info("Analyzing content with LLM")

                analysis = await self._analyze_with_llm(
                    query, context, model, ollama_timeout, iteration, analysis
                )

                if not analysis.strip():
                    logger.warning("LLM returned empty analysis")
                    if iteration == 0:
                        return "The language model did not provide an analysis."
                    else:
                        break

                # Check if LLM needs more information
                if "NEED_MORE_INFO" in analysis:
                    lines = analysis.split("\n")
                    if lines and "NEED_MORE_INFO" in lines[-1]:
                        current_query = lines[-1].replace("NEED_MORE_INFO", "").strip()
                        if not current_query:
                            current_query = query
                        logger.info(
                            f"LLM requested more info with query: '{current_query}'"
                        )
                        iteration += 1
                        continue
                    else:
                        break
                else:
                    break

            logger.info("Iterative research completed")
            # Clean up NEED_MORE_INFO if present
            if "NEED_MORE_INFO" in analysis:
                analysis = analysis.split("NEED_MORE_INFO")[0].strip()

            return analysis

        except Exception as e:
            logger.error(f"Research failed: {e}")
            raise

    async def _break_down_query(
        self, query: str, model: str, timeout: int
    ) -> List[str]:
        """Use LLM to break down research query into focused search queries."""
        breakdown_prompt = (
            f"Given this research query: '{query}'\n\n"
            "Please break it down into 2-4 specific, focused search queries that would help gather comprehensive information. "
            "Format your response as:\n"
            "Query 1: [specific query]\n"
            "Query 2: [specific query]\n"
            "etc.\n\n"
            "Make sure the queries are search-engine friendly and targeted."
        )

        try:
            request = GenerationRequest(
                prompt=breakdown_prompt,
                model=model,
                max_tokens=500,
                temperature=0.7,
            )

            response = await self.ollama_client.generate(request)
            breakdown_response = response.text

            # Parse queries
            import re

            query_matches = re.findall(
                r"Query \d+:\s*(.+)", breakdown_response, re.IGNORECASE
            )
            if query_matches:
                return [q.strip() for q in query_matches[:4]]
            else:
                logger.warning("Failed to parse LLM breakdown response")
                return []

        except Exception as e:
            logger.error(f"Query breakdown failed: {e}")
            return []

    async def _fetch_content(self, url: str) -> str:
        """Fetch and extract text content from a URL."""
        import requests  # type: ignore
        from bs4 import BeautifulSoup

        try:
            headers = {
                "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
            }
            response = requests.get(url, timeout=10, headers=headers)
            response.raise_for_status()

            soup = BeautifulSoup(response.content, "html.parser")

            # Remove unwanted elements
            for script in soup(["script", "style"]):
                script.decompose()

            # Get text content
            text = soup.get_text(separator=" ", strip=True)

            # Limit content length
            max_length = 5000
            if len(text) > max_length:
                text = text[:max_length] + "..."

            return text

        except Exception as e:
            logger.warning(f"Content fetch failed for {url}: {e}")
            return ""

    async def _analyze_with_llm(
        self,
        original_query: str,
        context: str,
        model: str,
        timeout: int,
        iteration: int,
        previous_analysis: str = "",
    ) -> str:
        """Analyze research context with LLM."""
        mode_instruction = "deep research" if iteration > 2 else "standard research"
        prompt = (
            f"You are an AI research assistant in {mode_instruction} mode. Using the following web search results, please analyze and summarize the information related to: "
            f"{original_query}\n\nContext from web search:\n{context}\n\n"
            "Please provide a comprehensive analysis that addresses the query based on the information found. "
            "Compare different sources, validate information, and highlight key findings. "
            "If you need more information to provide a complete and accurate answer, end your response with 'NEED_MORE_INFO' followed by a refined search query on the same line."
        )

        if iteration > 0 and previous_analysis:
            prompt += f"\n\nPrevious analysis:\n{previous_analysis}\n\nPlease refine or expand your analysis based on the new information."

        try:
            request = GenerationRequest(
                prompt=prompt,
                model=model,
                max_tokens=2000,
                temperature=0.7,
            )

            response = await self.ollama_client.generate(request)
            return response.text

        except Exception as e:
            logger.error(f"LLM analysis failed: {e}")
            return ""


# Tool class for agent integration
class IterativeResearchToolClass(BaseTool):
    """Tool for performing iterative web research with LLM refinement."""

    def __init__(self):
        super().__init__(
            "iterative_research",
            "Perform iterative web research with LLM-driven query refinement and analysis",
        )
        self._tool_instance = None

    async def _get_tool_instance(self):
        """Lazy initialization of the research tool."""
        if self._tool_instance is None:
            self._tool_instance = await get_iterative_research_tool()
        return self._tool_instance

    def execute(self, **kwargs) -> ToolResult:
        """Execute iterative research synchronously (for tool interface)."""
        # For now, we'll need to make this synchronous or handle differently
        # Since the agent system expects sync execute, we'll implement a simplified version
        import asyncio

        query = kwargs.get("query", "")
        if not query:
            return ToolResult(ok=False, error="Query is required")

        try:
            # Run async research in a new event loop
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)

            tool = loop.run_until_complete(self._get_tool_instance())
            result = loop.run_until_complete(
                tool.research_topic(
                    query=query,
                    max_iterations=kwargs.get("max_iterations", 2),
                    search_limit=kwargs.get("search_limit", 3),
                )
            )

            return ToolResult(ok=True, data=result)

        except Exception as e:
            return ToolResult(ok=False, error=f"Research failed: {str(e)}")

    def get_schema(self) -> Dict[str, Any]:
        """Return JSON schema for tool parameters."""
        schema = super().get_schema()
        schema["parameters"]["properties"] = {
            "query": {
                "type": "string",
                "description": "Research query to investigate",
            },
            "max_iterations": {
                "type": "integer",
                "description": "Maximum number of research iterations",
                "default": 2,
                "minimum": 1,
                "maximum": 5,
            },
            "search_limit": {
                "type": "integer",
                "description": "Number of search results per query",
                "default": 3,
                "minimum": 1,
                "maximum": 10,
            },
        }
        schema["parameters"]["required"] = ["query"]
        return schema


# Global instance management
_iterative_research_tool = None


async def get_iterative_research_tool(
    ollama_config: Optional[OllamaConfig] = None,
    scraping_config: Optional[ScrapingConfig] = None,
    memory_manager: Optional[Any] = None,
) -> IterativeResearchTool:
    """Get or create the global iterative research tool instance."""
    global _iterative_research_tool

    if _iterative_research_tool is None:
        if ollama_config is None:
            ollama_config = OllamaConfig()
        if scraping_config is None:
            scraping_config = ScrapingConfig()
        mm = memory_manager
        if mm is None:
            try:
                from ...utils.memory_manager import MemoryManager

                mm = MemoryManager()
            except ImportError:
                mm = None

        ollama_client = OllamaClient(ollama_config)
        web_scraper = WebScraper(scraping_config, mm)  # type: ignore

        _iterative_research_tool = IterativeResearchTool(
            ollama_client, web_scraper, mm  # type: ignore
        )

    return _iterative_research_tool
