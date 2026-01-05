from __future__ import annotations

import hashlib
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from enum import Enum
from typing import Any, Dict, List, Optional

from agent.models import Mode


class ResearchMode(Enum):
    QUICK = "quick"  # Single pass, basic research
    STANDARD = "standard"  # Two passes, moderate depth
    DEEP = "deep"  # Multi-pass, comprehensive analysis


class DeepResearchEngine:
    """Advanced research engine with multi-pass analysis"""

    def __init__(self, model_router=None, cache_enabled=True, max_workers=3):
        self.model_router = model_router
        self.cache_enabled = cache_enabled
        self.max_workers = max_workers
        self._cache = {}  # Simple in-memory cache
        self._executor = ThreadPoolExecutor(max_workers=max_workers)

    def execute_research(self, query: str, mode: str = "standard") -> Dict[str, Any]:
        """Execute multi-pass research based on complexity"""

        # Convert string mode to enum
        try:
            research_mode = ResearchMode(mode.lower())
        except ValueError:
            research_mode = ResearchMode.STANDARD

        # Step 1: Initial analysis and planning
        analysis = self._analyze_query_complexity(query)

        # Step 2: Select research strategy based on mode and complexity
        strategy = self._select_research_strategy(query, research_mode, analysis)

        # Step 3: Execute research passes
        results = self._execute_research_passes(query, strategy)

        # Step 4: Synthesize and validate findings
        synthesis = self._synthesize_findings(results, query)

        return {
            "query": query,
            "mode": research_mode.value,
            "complexity_analysis": analysis,
            "strategy": strategy,
            "raw_results": results,
            "synthesis": synthesis,
            "execution_time": time.time(),
            "sources_used": self._count_sources(results),
        }

    def _analyze_query_complexity(self, query: str) -> Dict[str, Any]:
        """Analyze query complexity using simple heuristics"""

        complexity_indicators = {
            "technical_terms": [
                "algorithm",
                "quantum",
                "neural",
                "machine learning",
                "blockchain",
                "cryptography",
            ],
            "research_depth": [
                "comprehensive",
                "detailed",
                "thorough",
                "extensive",
                "in-depth",
            ],
            "multi_disciplinary": [
                "intersection",
                "relationship",
                "comparison",
                "vs",
                "versus",
            ],
            "current_events": ["recent", "latest", "current", "breaking", "news"],
            "controversial": ["debate", "controversy", "dispute", "criticism"],
        }

        scores = {}
        for category, keywords in complexity_indicators.items():
            matches = sum(1 for keyword in keywords if keyword.lower() in query.lower())
            scores[category] = min(matches * 2, 10)  # Cap at 10

        total_score = sum(scores.values())
        complexity_level = (
            "low" if total_score < 5 else "medium" if total_score < 15 else "high"
        )

        return {
            "scores": scores,
            "total_score": total_score,
            "complexity_level": complexity_level,
            "estimated_passes": 1
            if complexity_level == "low"
            else 2
            if complexity_level == "medium"
            else 4,
        }

    def _select_research_strategy(
        self, query: str, mode: ResearchMode, analysis: Dict
    ) -> Dict[str, Any]:
        """Select research strategy based on mode and analysis"""

        base_strategies = {
            ResearchMode.QUICK: {
                "passes": 1,
                "time_limit": 60,
                "sources": ["kiwix"],
                "depth": "surface",
            },
            ResearchMode.STANDARD: {
                "passes": 2,
                "time_limit": 300,
                "sources": ["kiwix", "web"],
                "depth": "moderate",
            },
            ResearchMode.DEEP: {
                "passes": 4,
                "time_limit": 1800,
                "sources": ["kiwix", "web", "academic"],
                "depth": "comprehensive",
            },
        }

        strategy = base_strategies[mode].copy()

        # Adjust based on complexity analysis
        if analysis["complexity_level"] == "high" and mode != ResearchMode.DEEP:
            strategy["passes"] += 1
            strategy["time_limit"] += 300

        # Adjust sources based on query type
        if (
            "technical" in analysis["scores"]
            and analysis["scores"]["technical_terms"] > 3
        ):
            strategy["sources"].append("code_repositories")

        return strategy

    def _execute_research_passes(
        self, query: str, strategy: Dict
    ) -> List[Dict[str, Any]]:
        """Execute multiple research passes"""

        results = []

        for pass_num in range(strategy["passes"]):
            pass_result = self._execute_single_pass(query, pass_num, strategy)
            results.append(pass_result)

            # Check if we have sufficient information
            if self._is_information_sufficient(results, strategy):
                break

        return results

    def _get_cache_key(self, tool_name: str, query: str) -> str:
        """Generate cache key for tool results"""
        return hashlib.md5(f"{tool_name}:{query}".encode()).hexdigest()

    def _execute_single_pass(
        self, query: str, pass_num: int, strategy: Dict
    ) -> Dict[str, Any]:
        """Execute a single research pass with parallel tool execution"""

        # Refine query for this pass
        refined_query = self._refine_query_for_pass(query, pass_num, strategy)

        # Select appropriate tools
        tools_to_use = self._select_tools_for_pass(strategy, pass_num)

        # Execute tools in parallel
        pass_results = []
        futures = {}

        for tool_name in tools_to_use:
            cache_key = self._get_cache_key(tool_name, refined_query)

            # Check cache first
            if self.cache_enabled and cache_key in self._cache:
                cached_result = self._cache[cache_key]
                pass_results.append(
                    {
                        "tool": tool_name,
                        "query": refined_query,
                        "result": cached_result,
                        "success": cached_result.get("success", False),
                        "cached": True,
                    }
                )
                continue

            # Submit to thread pool
            future = self._executor.submit(
                self._execute_research_tool_safe, tool_name, refined_query, cache_key
            )
            futures[future] = tool_name

        # Collect results
        for future in as_completed(futures):
            tool_name = futures[future]
            try:
                result_data = future.result()
                pass_results.append(result_data)
            except Exception as e:
                pass_results.append(
                    {
                        "tool": tool_name,
                        "query": refined_query,
                        "error": str(e),
                        "success": False,
                    }
                )

        return {
            "pass_number": pass_num,
            "refined_query": refined_query,
            "tools_used": tools_to_use,
            "results": pass_results,
            "timestamp": time.time(),
        }

    def _refine_query_for_pass(
        self, original_query: str, pass_num: int, strategy: Dict
    ) -> str:
        """Refine the query for each research pass"""

        if pass_num == 0:
            return original_query  # First pass uses original query

        # Subsequent passes focus on gaps or deeper analysis
        refinements = [
            f"{original_query} detailed analysis",
            f"{original_query} recent developments",
            f"{original_query} expert opinions",
            f"{original_query} comprehensive review",
        ]

        return refinements[min(pass_num - 1, len(refinements) - 1)]

    def _select_tools_for_pass(self, strategy: Dict, pass_num: int) -> List[str]:
        """Select appropriate tools for each pass"""

        base_tools = []
        sources = strategy.get("sources", ["kiwix"])

        if "kiwix" in sources:
            base_tools.append("kiwix_query")

        if "web" in sources and pass_num > 0:  # Web search after initial Kiwix pass
            base_tools.append("web_search")

        if pass_num > 1:  # Deeper passes
            base_tools.append("fetch_url")

        return base_tools[:3]  # Limit to 3 tools per pass

    def _execute_research_tool_safe(
        self, tool_name: str, query: str, cache_key: str
    ) -> Dict[str, Any]:
        """Execute research tool with error handling and caching"""
        try:
            result = self._execute_research_tool(tool_name, query)

            # Cache successful results
            if self.cache_enabled and result.get("success"):
                self._cache[cache_key] = result

            return {
                "tool": tool_name,
                "query": query,
                "result": result,
                "success": result.get("success", False),
                "cached": False,
            }
        except Exception as e:
            return {
                "tool": tool_name,
                "query": query,
                "error": str(e),
                "success": False,
                "cached": False,
            }

    def _execute_research_tool(self, tool_name: str, query: str) -> Dict[str, Any]:
        """Execute a research tool using the controller's tool registry"""

        try:
            from agent.controller import Controller
            from agent.worker import DummyWorker

            # Create a controller to access tool registry
            controller = Controller(DummyWorker())
            result = controller.execute_tool(tool_name, query=query)

            if result.success:
                # Convert ToolResult to the expected format
                data = result.data
                sources = []

                # Extract sources from different tool types
                if tool_name == "web_search" and isinstance(data, list):
                    sources = [item.get("url", "") for item in data if item.get("url")]
                elif tool_name == "kiwix_query" and isinstance(data, list):
                    sources = [f"kiwix:{item.get('title', '')}" for item in data]
                elif tool_name == "fetch_url":
                    sources = [query]  # The URL itself is the source
                else:
                    sources = ["local_search"]

                return {
                    "success": True,
                    "data": str(data)[:1000],  # Limit data size
                    "sources": sources[:5],  # Limit sources
                    "confidence": 0.9,
                }
            else:
                return {
                    "success": False,
                    "data": f"Tool failed: {result.error}",
                    "sources": [],
                    "confidence": 0.0,
                }

        except Exception as e:
            return {
                "success": False,
                "data": f"Tool execution error: {str(e)}",
                "sources": [],
                "confidence": 0.0,
            }

    def _is_information_sufficient(self, results: List[Dict], strategy: Dict) -> bool:
        """Determine if we have sufficient information to stop research"""

        total_successful_results = 0
        total_sources = 0
        high_quality_sources = 0

        for pass_result in results:
            for tool_result in pass_result.get("results", []):
                if tool_result.get("success"):
                    total_successful_results += 1
                    result_data = tool_result.get("result", {})
                    sources = result_data.get("sources", [])
                    total_sources += len(sources)

                    # Count high-quality sources (web URLs, academic sources)
                    for source in sources:
                        if any(
                            indicator in source.lower()
                            for indicator in ["http", "academic", "edu", "gov"]
                        ):
                            high_quality_sources += 1

        # Early termination conditions
        min_passes = strategy.get("passes", 2) // 2  # At least half the planned passes
        current_pass = len(results)

        # Stop if we have good coverage or are running too long
        sufficient_sources = total_sources >= 8 or high_quality_sources >= 3
        sufficient_results = total_successful_results >= 6
        time_pressure = current_pass >= min_passes and (
            sufficient_sources or sufficient_results
        )

        return time_pressure or current_pass >= strategy.get("passes", 2)

    def _synthesize_findings(
        self, results: List[Dict], original_query: str
    ) -> Dict[str, Any]:
        """Synthesize findings from all research passes"""

        all_sources = []
        successful_results = []

        for pass_result in results:
            for tool_result in pass_result.get("results", []):
                if tool_result.get("success"):
                    successful_results.append(tool_result)
                    all_sources.extend(tool_result.get("result", {}).get("sources", []))

        # Remove duplicates
        unique_sources = list(set(all_sources))

        return {
            "total_passes": len(results),
            "successful_results": len(successful_results),
            "unique_sources": len(unique_sources),
            "sources_list": unique_sources[:10],  # Limit for brevity
            "confidence_score": min(len(successful_results) * 0.2, 1.0),
            "summary": f"Found {len(unique_sources)} unique sources across {len(successful_results)} successful research operations",
        }

    def _count_sources(self, results: List[Dict]) -> int:
        """Count total unique sources across all results"""
        all_sources = set()
        for pass_result in results:
            for tool_result in pass_result.get("results", []):
                sources = tool_result.get("result", {}).get("sources", [])
                all_sources.update(sources)
        return len(all_sources)

    def cleanup(self):
        """Clean up resources"""
        if hasattr(self, "_executor"):
            self._executor.shutdown(wait=True)
