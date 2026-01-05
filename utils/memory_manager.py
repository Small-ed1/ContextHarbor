"""
RAM Monitoring and Management System
Monitors system RAM usage and implements automatic optimization strategies.
"""

import asyncio
import gc
import logging
import os
import signal
from dataclasses import dataclass
from datetime import datetime, timedelta
from enum import Enum
from typing import Any, Callable, Dict, List, Optional

import psutil


class MemoryAction(Enum):
    """Actions to take when memory is low."""

    SUMMARIZE_CONTEXT = "summarize_context"
    REDUCE_AGENTS = "reduce_agents"
    LOWER_MODEL_SIZE = "lower_model_size"
    RESTART_PROCESSES = "restart_processes"
    FORCE_GC = "force_gc"
    CLEAR_CACHE = "clear_cache"


@dataclass
class MemoryThreshold:
    """Memory usage thresholds and actions."""

    warning_mb: int = 12 * 1024  # 12GB warning
    critical_mb: int = 14 * 1024  # 14GB critical
    emergency_mb: int = 15 * 1024  # 15GB emergency

    # Action priorities when memory is low
    warning_actions: Optional[List[MemoryAction]] = None
    critical_actions: Optional[List[MemoryAction]] = None
    emergency_actions: Optional[List[MemoryAction]] = None

    def __post_init__(self):
        if self.warning_actions is None:
            self.warning_actions = [MemoryAction.FORCE_GC, MemoryAction.CLEAR_CACHE]
        if self.critical_actions is None:
            self.critical_actions = [
                MemoryAction.SUMMARIZE_CONTEXT,
                MemoryAction.REDUCE_AGENTS,
            ]
        if self.emergency_actions is None:
            self.emergency_actions = [
                MemoryAction.LOWER_MODEL_SIZE,
                MemoryAction.RESTART_PROCESSES,
            ]


@dataclass
class MemoryStats:
    """Current memory statistics."""

    total_mb: float
    used_mb: float
    available_mb: float
    usage_percent: float
    timestamp: datetime

    @property
    def is_warning(self) -> bool:
        return self.used_mb >= 12 * 1024

    @property
    def is_critical(self) -> bool:
        return self.used_mb >= 14 * 1024

    @property
    def is_emergency(self) -> bool:
        return self.used_mb >= 15 * 1024


class MemoryManager:
    """Comprehensive memory management system."""

    def __init__(self, thresholds: Optional[MemoryThreshold] = None):
        self.thresholds = thresholds or MemoryThreshold()
        self.logger = logging.getLogger(__name__)
        self.monitoring_active = False
        self.monitor_task: Optional[asyncio.Task] = None
        self.memory_history: List[MemoryStats] = []
        self.max_history_size = 100

        # Callbacks for memory actions
        self.action_callbacks: Dict[MemoryAction, List[Callable]] = {
            action: [] for action in MemoryAction
        }

        # Track last action times to prevent spam
        self.last_action_times: Dict[MemoryAction, datetime] = {}

    def register_callback(self, action: MemoryAction, callback: Callable):
        """Register a callback for a specific memory action."""
        self.action_callbacks[action].append(callback)

    async def start_monitoring(self, check_interval: float = 5.0):
        """Start background memory monitoring."""
        if self.monitoring_active:
            return

        self.monitoring_active = True
        self.monitor_task = asyncio.create_task(self._monitor_loop(check_interval))
        self.logger.info("Memory monitoring started")

    async def stop_monitoring(self):
        """Stop memory monitoring."""
        self.monitoring_active = False
        if self.monitor_task:
            self.monitor_task.cancel()
            try:
                await self.monitor_task
            except asyncio.CancelledError:
                pass
        self.logger.info("Memory monitoring stopped")

    def get_current_stats(self) -> MemoryStats:
        """Get current memory statistics."""
        memory = psutil.virtual_memory()
        stats = MemoryStats(
            total_mb=memory.total / (1024 * 1024),
            used_mb=memory.used / (1024 * 1024),
            available_mb=memory.available / (1024 * 1024),
            usage_percent=memory.percent,
            timestamp=datetime.now(),
        )

        # Keep history
        self.memory_history.append(stats)
        if len(self.memory_history) > self.max_history_size:
            self.memory_history.pop(0)

        return stats

    async def _monitor_loop(self, check_interval: float):
        """Main monitoring loop."""
        while self.monitoring_active:
            try:
                stats = self.get_current_stats()

                if stats.is_emergency:
                    await self._execute_actions(
                        self.thresholds.emergency_actions or [], stats
                    )
                elif stats.is_critical:
                    await self._execute_actions(
                        self.thresholds.critical_actions or [], stats
                    )
                elif stats.is_warning:
                    await self._execute_actions(
                        self.thresholds.warning_actions or [], stats
                    )

                await asyncio.sleep(check_interval)

            except Exception as e:
                self.logger.error(f"Error in memory monitoring loop: {e}")
                await asyncio.sleep(check_interval)

    async def _execute_actions(self, actions: List[MemoryAction], stats: MemoryStats):
        """Execute memory optimization actions."""
        for action in actions:
            # Check if we recently executed this action (prevent spam)
            last_time = self.last_action_times.get(action)
            if last_time and (datetime.now() - last_time) < timedelta(minutes=5):
                continue

            self.logger.warning(
                f"Executing memory action: {action.value} (RAM: {stats.used_mb:.1f}MB)"
            )

            try:
                # Execute all callbacks for this action
                for callback in self.action_callbacks[action]:
                    await callback(stats)

                # Execute built-in actions
                await self._execute_builtin_action(action, stats)

                self.last_action_times[action] = datetime.now()

            except Exception as e:
                self.logger.error(f"Error executing memory action {action.value}: {e}")

    async def _execute_builtin_action(self, action: MemoryAction, stats: MemoryStats):
        """Execute built-in memory optimization actions."""
        if action == MemoryAction.FORCE_GC:
            gc.collect()
            self.logger.info("Forced garbage collection")

        elif action == MemoryAction.CLEAR_CACHE:
            # This will be implemented by other components
            # They can register callbacks for this action
            pass

        elif action == MemoryAction.SUMMARIZE_CONTEXT:
            # This will be handled by context manager
            pass

        elif action == MemoryAction.REDUCE_AGENTS:
            # This will be handled by agent manager
            pass

        elif action == MemoryAction.LOWER_MODEL_SIZE:
            # This will be handled by Ollama client
            pass

        elif action == MemoryAction.RESTART_PROCESSES:
            # This will be handled by session manager
            pass

    def get_memory_history(self, hours: int = 1) -> List[MemoryStats]:
        """Get memory history for the last N hours."""
        cutoff = datetime.now() - timedelta(hours=hours)
        return [stats for stats in self.memory_history if stats.timestamp >= cutoff]

    def get_memory_report(self) -> Dict[str, Any]:
        """Generate a comprehensive memory report."""
        current = self.get_current_stats()
        history = self.get_memory_history(1)

        if not history:
            return {"current": current.__dict__}

        # Calculate trends
        recent_avg = sum(s.used_mb for s in history[-10:]) / min(10, len(history))
        trend = "stable"
        if len(history) >= 2:
            start_avg = sum(s.used_mb for s in history[:10]) / min(10, len(history))
            if recent_avg > start_avg * 1.1:
                trend = "increasing"
            elif recent_avg < start_avg * 0.9:
                trend = "decreasing"

        return {
            "current": current.__dict__,
            "trend": trend,
            "average_last_hour_mb": sum(s.used_mb for s in history) / len(history),
            "peak_last_hour_mb": max(s.used_mb for s in history),
            "trough_last_hour_mb": min(s.used_mb for s in history),
            "warning_threshold_mb": self.thresholds.warning_mb,
            "critical_threshold_mb": self.thresholds.critical_mb,
            "emergency_threshold_mb": self.thresholds.emergency_mb,
        }


class MemoryAwareMixin:
    """Mixin class for components that need memory awareness."""

    def __init__(self, memory_manager: MemoryManager):
        self.memory_manager = memory_manager
        self._register_memory_callbacks()

    def _register_memory_callbacks(self):
        """Register memory management callbacks."""
        # Override in subclasses to register specific callbacks
        pass

    def check_memory_before_operation(self) -> bool:
        """Check if there's enough memory for an operation."""
        stats = self.memory_manager.get_current_stats()
        return not stats.is_emergency

    async def memory_safe_operation(self, operation: Callable, *args, **kwargs):
        """Execute an operation only if memory allows."""
        if not self.check_memory_before_operation():
            # Use memory manager's logger
            self.memory_manager.logger.warning("Skipping operation due to low memory")
            return None

        return await operation(*args, **kwargs)
