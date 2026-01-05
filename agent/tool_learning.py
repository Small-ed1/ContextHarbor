from __future__ import annotations

import json
import time
from collections import Counter, defaultdict
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any, Dict, List, Tuple


@dataclass
class ToolUsageRecord:
    """Record of tool usage"""

    tool_name: str
    objective: str
    mode: str
    success: bool
    execution_time: float
    timestamp: float
    user_feedback: int = 0  # -1, 0, 1 for negative, neutral, positive
    context_keywords: List[str] | None = None

    def __post_init__(self):
        if self.context_keywords is None:
            self.context_keywords = []


class ToolLearningSystem:
    """Learning system for improving tool selection based on usage patterns"""

    def __init__(self, data_path: str = "projects/default/tool_learning.json"):
        self.data_path = Path(data_path)
        self.usage_history: List[ToolUsageRecord] = []
        self.tool_scores: Dict[str, float] = defaultdict(float)
        self.context_patterns: Dict[str, Dict[str, float]] = defaultdict(
            lambda: defaultdict(float)
        )
        self.mode_preferences: Dict[str, Dict[str, float]] = defaultdict(
            lambda: defaultdict(float)
        )
        self._load_data()

    def _load_data(self):
        """Load learning data from file"""
        if self.data_path.exists():
            try:
                with open(self.data_path, "r") as f:
                    data = json.load(f)

                # Load usage history
                for record_data in data.get("usage_history", []):
                    record = ToolUsageRecord(**record_data)
                    self.usage_history.append(record)

                # Load computed scores
                self.tool_scores.update(data.get("tool_scores", {}))

                # Load context patterns
                for tool, patterns in data.get("context_patterns", {}).items():
                    for keyword, score in patterns.items():
                        self.context_patterns[tool][keyword] = float(score)

                # Load mode preferences
                for mode, tools in data.get("mode_preferences", {}).items():
                    self.mode_preferences[mode].update(tools)

            except Exception as e:
                print(f"Error loading tool learning data: {e}")

    def _save_data(self):
        """Save learning data to file"""
        try:
            self.data_path.parent.mkdir(parents=True, exist_ok=True)

            data = {
                "usage_history": [
                    asdict(record) for record in self.usage_history[-1000:]
                ],  # Keep last 1000 records
                "tool_scores": dict(self.tool_scores),
                "context_patterns": {
                    tool: dict(patterns)
                    for tool, patterns in self.context_patterns.items()
                },
                "mode_preferences": {
                    mode: dict(tools) for mode, tools in self.mode_preferences.items()
                },
                "last_updated": time.time(),
            }

            with open(self.data_path, "w") as f:
                json.dump(data, f, indent=2)

        except Exception as e:
            print(f"Error saving tool learning data: {e}")

    def record_usage(
        self,
        tool_name: str,
        objective: str,
        mode: str,
        success: bool,
        execution_time: float,
        context_keywords: List[str] | None = None,
    ) -> None:
        """Record tool usage for learning"""
        record = ToolUsageRecord(
            tool_name=tool_name,
            objective=objective,
            mode=mode,
            success=success,
            execution_time=execution_time,
            timestamp=time.time(),
            context_keywords=context_keywords or [],
        )

        self.usage_history.append(record)
        self._update_scores(tool_name, record)

        # Periodically save
        if len(self.usage_history) % 10 == 0:
            self._save_data()

    def _update_scores(self, tool_name: str, record: ToolUsageRecord) -> None:
        """Update internal scores based on usage record"""
        # Base score update
        score_change = 0.1 if record.success else -0.2
        self.tool_scores[tool_name] += score_change

        # Time-based adjustment (faster is better)
        if record.success and record.execution_time < 5.0:
            self.tool_scores[tool_name] += 0.05

        # Context pattern learning
        for keyword in record.context_keywords or []:
            current_value = self.context_patterns[tool_name].get(keyword, 0)
            self.context_patterns[tool_name][keyword] = current_value + (
                1 if record.success else -0.5
            )

        # Mode preference learning
        current_mode_value = self.mode_preferences[record.mode].get(tool_name, 0)
        self.mode_preferences[record.mode][tool_name] = (
            current_mode_value + score_change
        )

        # User feedback adjustment
        self.tool_scores[tool_name] += record.user_feedback * 0.2

        # Keep scores bounded
        self.tool_scores[tool_name] = max(-1.0, min(1.0, self.tool_scores[tool_name]))

    def add_user_feedback(self, tool_name: str, feedback: int) -> None:
        """Add user feedback for recent tool usage"""
        # Find most recent usage of this tool
        for record in reversed(self.usage_history):
            if record.tool_name == tool_name:
                record.user_feedback = feedback
                self._update_scores(tool_name, record)
                self._save_data()
                break

    def get_tool_recommendations(
        self, objective: str, mode: str, context_keywords: List[str] | None = None
    ) -> Dict[str, float]:
        """Get tool recommendations based on learning data"""
        if not self.usage_history:
            return {}

        recommendations = {}
        objective_lower = objective.lower()
        context_keywords = context_keywords or []

        for tool_name in self.tool_scores.keys():
            score = 0.0

            # Base learned score
            score += self.tool_scores[tool_name] * 0.3

            # Mode preference
            score += self.mode_preferences[mode].get(tool_name, 0) * 0.3

            # Context pattern matching
            context_score = 0.0
            for keyword in context_keywords:
                context_score += self.context_patterns[tool_name].get(keyword, 0)
            recommendations[tool_name] = score + (context_score * 0.2)

            # Objective similarity (simple keyword matching)
            if any(word in objective_lower for word in tool_name.split("_")):
                recommendations[tool_name] += 0.2

        return recommendations

    def get_tool_usage_stats(self, tool_name: str | None = None) -> Dict[str, Any]:
        """Get usage statistics for a tool or all tools"""
        if tool_name:
            tool_records = [r for r in self.usage_history if r.tool_name == tool_name]
            if not tool_records:
                return {}

            success_rate = sum(1 for r in tool_records if r.success) / len(tool_records)
            avg_time = sum(r.execution_time for r in tool_records) / len(tool_records)
            total_usage = len(tool_records)

            return {
                "tool_name": tool_name,
                "total_usage": total_usage,
                "success_rate": success_rate,
                "average_execution_time": avg_time,
                "current_score": self.tool_scores.get(tool_name, 0),
                "last_used": max((r.timestamp for r in tool_records), default=0)
                if tool_records
                else None,
            }
        else:
            return {
                tool_name: self.get_tool_usage_stats(tool_name)
                for tool_name in set(r.tool_name for r in self.usage_history)
            }

    def get_improvement_suggestions(self) -> List[str]:
        """Get suggestions for tool improvement based on usage patterns"""
        suggestions = []

        # Find tools with low success rates
        for tool_name in set(r.tool_name for r in self.usage_history):
            tool_records = [r for r in self.usage_history if r.tool_name == tool_name]
            if len(tool_records) >= 5:  # Only consider tools with sufficient data
                success_rate = sum(1 for r in tool_records if r.success) / len(
                    tool_records
                )

                if success_rate < 0.5:
                    suggestions.append(
                        f"Tool '{tool_name}' has low success rate ({success_rate:.0%}). Consider improving error handling or updating tool selection criteria."
                    )

                avg_time = sum(r.execution_time for r in tool_records) / len(
                    tool_records
                )
                if avg_time > 10.0:
                    suggestions.append(
                        f"Tool '{tool_name}' is slow (avg {avg_time:.1f}s). Consider optimization or caching."
                    )

        # Find underutilized tools
        if self.usage_history:
            all_tool_names = set(r.tool_name for r in self.usage_history)
            recent_tools = set(
                r.tool_name for r in self.usage_history[-100:]
            )  # Last 100 uses

            for tool_name in all_tool_names:
                if tool_name not in recent_tools:
                    suggestions.append(
                        f"Tool '{tool_name}' hasn't been used recently. Consider if it's still relevant or needs promotion."
                    )

        return suggestions


# Global learning system instance
_learning_system: ToolLearningSystem | None = None


def get_learning_system() -> ToolLearningSystem:
    """Get or create the global learning system"""
    global _learning_system
    if _learning_system is None:
        _learning_system = ToolLearningSystem()
    return _learning_system


def record_tool_usage(
    tool_name: str,
    objective: str,
    mode: str,
    success: bool,
    execution_time: float,
    context_keywords: List[str] | None = None,
) -> None:
    """Convenience function to record tool usage"""
    get_learning_system().record_usage(
        tool_name, objective, mode, success, execution_time, context_keywords
    )
