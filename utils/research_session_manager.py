"""
Research Session Manager
Manages active research sessions for real-time progress tracking
"""

import asyncio
import json
import logging
import os
import threading
from datetime import datetime
from pathlib import Path
from typing import Dict, Optional, Set, cast
from dataclasses import dataclass, field

from agent.ollama_client import OllamaConfig
from agent.research.multi_agent_system import MultiAgentSystem
from agent.research.research_orchestrator import ResearchOrchestrator
from utils.memory_manager import MemoryManager


@dataclass
class ActiveResearchSession:
    """An active research session with real-time tracking."""
    task_id: str
    orchestrator: Optional[ResearchOrchestrator] = None
    multi_agent_system: Optional[MultiAgentSystem] = None
    memory_manager: Optional[MemoryManager] = None
    start_time: datetime = field(default_factory=datetime.now)
    last_update: datetime = field(default_factory=datetime.now)
    subscribers: Set[asyncio.Queue] = field(default_factory=set)
    _running_task: Optional[asyncio.Task] = None
    plan_id: Optional[str] = None

    async def start_research(self, topic: str, depth: str = "standard"):
        """Start the research asynchronously."""
        if self.orchestrator is None or self._running_task is not None:
            return  # Not initialized or already running

        # Create research plan
        self.plan_id = await self.orchestrator.create_research_plan(  # type: ignore
            title=f"Research: {topic}",
            description=f"Research on topic: {topic}",
            time_budget_hours=2.0,
        )

        # Start execution
        self._running_task = asyncio.create_task(
            self.orchestrator.execute_research_plan(self.plan_id)  # type: ignore
        )

        # Start progress broadcasting
        asyncio.create_task(self._broadcast_progress())

        return self.plan_id

    async def _broadcast_progress(self):
        """Continuously broadcast progress updates to subscribers."""
        while True:
            try:
                # Get current status
                if self.orchestrator is None or self.plan_id is None:
                    await asyncio.sleep(1)
                    continue
                status = await self.orchestrator.get_research_status(self.plan_id)  # type: ignore
                if "error" not in status:
                    plan = status["plan"]
                    progress = status["progress"]

                    # Calculate progress percentage
                    total_topics = progress["total_topics"]
                    completed_topics = progress["completed_topics"]
                    progress_percent = (
                        (completed_topics / total_topics * 100) if total_topics > 0 else 0
                    )

                    update = {
                        "task_id": self.task_id,
                        "timestamp": datetime.now().isoformat(),
                        "status": "completed" if plan["completed_at"] else "running",
                        "progress": progress_percent,
                        "phase": plan["phase"],
                        "topics_completed": completed_topics,
                        "total_topics": total_topics,
                        "findings_count": progress["findings_count"],
                    }

                    # Send to all subscribers
                    dead_queues = set()
                    for queue in self.subscribers:
                        try:
                            await queue.put(update)
                        except Exception:
                            dead_queues.add(queue)

                    # Clean up dead queues
                    self.subscribers -= dead_queues

                self.last_update = datetime.now()

                # Check if research is complete
                if status.get("plan", {}).get("completed_at"):
                    break

                await asyncio.sleep(2)  # Update every 2 seconds

            except Exception as e:
                logging.error(f"Error broadcasting progress: {e}")
                await asyncio.sleep(5)

    def subscribe(self) -> asyncio.Queue:
        """Subscribe to progress updates."""
        queue = asyncio.Queue()
        self.subscribers.add(queue)
        return queue

    def unsubscribe(self, queue: asyncio.Queue):
        """Unsubscribe from progress updates."""
        self.subscribers.discard(queue)

    async def stop(self):
        """Stop the research session."""
        if self._running_task:
            self._running_task.cancel()
            try:
                await self._running_task
            except asyncio.CancelledError:
                pass

        # Clean up subscribers
        for queue in self.subscribers:
            try:
                await queue.put({"type": "complete"})
            except Exception:
                pass
        self.subscribers.clear()


class ResearchSessionManager:
    """Global manager for active research sessions."""

    _instance = None
    _lock = threading.RLock()

    def __init__(self):
        self.sessions: Dict[str, ActiveResearchSession] = {}
        self._cleanup_task: Optional[asyncio.Task] = None
        self.sessions_dir = Path("data/research_sessions")
        self.sessions_dir.mkdir(parents=True, exist_ok=True)
        # Load saved sessions on startup
        self.load_sessions()

    def __new__(cls):
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super().__new__(cls)
        return cls._instance

    async def start_research(self, topic: str, depth: str = "standard") -> str:
        """Start a new research session."""
        # Generate unique task ID
        task_id = f"research_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{hash(topic) % 1000}"

        # Initialize components
        memory_manager = MemoryManager()
        ollama_config = OllamaConfig()
        multi_agent_system = MultiAgentSystem(memory_manager, ollama_config)
        orchestrator = ResearchOrchestrator(multi_agent_system, None, memory_manager)

        # Initialize systems
        await multi_agent_system.initialize_system(num_workers=2)
        await memory_manager.start_monitoring()

        # Perform cleanup
        await multi_agent_system.perform_memory_cleanup()

        # Create session
        session = ActiveResearchSession(
            task_id=task_id,
            orchestrator=orchestrator,
            multi_agent_system=multi_agent_system,
            memory_manager=memory_manager
        )

        self.sessions[task_id] = session

        # Start research
        await session.start_research(topic, depth)

        # Save session to disk
        self.save_session(session)

        # Start cleanup task if not already running
        if self._cleanup_task is None or self._cleanup_task.done():
            self._cleanup_task = asyncio.create_task(self._cleanup_old_sessions())

        return task_id

    async def get_status(self, task_id: str) -> Optional[Dict]:
        """Get status of a research session."""
        session = self.sessions.get(task_id)
        if not session:
            return None

        try:
            if session.orchestrator is None or session.plan_id is None:
                return {"task_id": task_id, "status": "error", "error": "Research session not fully initialized"}
            status = await session.orchestrator.get_research_status(session.plan_id)  # type: ignore
            if "error" in status:
                return {"error": status["error"], "status": "not_found"}

            plan = status["plan"]
            progress = status["progress"]

            total_topics = progress["total_topics"]
            completed_topics = progress["completed_topics"]
            progress_percent = (
                (completed_topics / total_topics * 100) if total_topics > 0 else 0
            )

            return {
                "task_id": task_id,
                "status": "completed" if plan["completed_at"] else "running",
                "progress": progress_percent,
                "phase": plan["phase"],
                "topics_completed": completed_topics,
                "total_topics": total_topics,
                "findings_count": progress["findings_count"],
                "start_time": session.start_time.isoformat(),
                "last_update": session.last_update.isoformat(),
            }
        except Exception as e:
            return {"task_id": task_id, "status": "error", "error": str(e)}

    async def subscribe_progress(self, task_id: str):
        """Subscribe to real-time progress updates for a session."""
        session = self.sessions.get(task_id)
        if not session:
            raise ValueError(f"Research session {task_id} not found")

        return session.subscribe()

    async def stop_research(self, task_id: str):
        """Stop a research session."""
        session = self.sessions.get(task_id)
        if session:
            await session.stop()
            del self.sessions[task_id]
            return {"status": "stopped"}
        return {"error": "Session not found"}

    async def _cleanup_old_sessions(self):
        """Periodically clean up old completed sessions."""
        while True:
            try:
                current_time = datetime.now()
                to_remove = []

                for task_id, session in self.sessions.items():
                    # Remove sessions older than 1 hour that are completed
                    if (current_time - session.start_time).total_seconds() > 3600:
                        if session._running_task and not session._running_task.done():
                            await session.stop()
                        to_remove.append(task_id)

                for task_id in to_remove:
                    del self.sessions[task_id]
                    logging.info(f"Cleaned up old research session: {task_id}")

                await asyncio.sleep(300)  # Check every 5 minutes

            except Exception as e:
                logging.error(f"Error in session cleanup: {e}")
                await asyncio.sleep(60)

    def save_session(self, session: ActiveResearchSession):
        """Save a research session to disk."""
        try:
            session_data = {
                "task_id": session.task_id,
                "plan_id": session.plan_id,
                "start_time": session.start_time.isoformat(),
                "last_update": session.last_update.isoformat(),
                "status": "running" if session._running_task and not session._running_task.done() else "stopped",
            }

            session_file = self.sessions_dir / f"{session.task_id}.json"
            with open(session_file, 'w') as f:
                json.dump(session_data, f, indent=2)

            logging.debug(f"Saved research session: {session.task_id}")
        except Exception as e:
            logging.error(f"Failed to save session {session.task_id}: {e}")

    def load_sessions(self):
        """Load saved research sessions from disk."""
        try:
            for session_file in self.sessions_dir.glob("*.json"):
                try:
                    with open(session_file, 'r') as f:
                        session_data = json.load(f)

                    # Only load sessions that were running (can be resumed)
                    if session_data.get("status") == "running":
                        # Create a minimal session for resuming
                        # Note: This won't restore the full orchestrator state
                        # but allows checking status and stopping
                        task_id = session_data["task_id"]
                        session = ActiveResearchSession(
                            task_id=task_id,
                            start_time=datetime.fromisoformat(session_data["start_time"]),
                            last_update=datetime.fromisoformat(session_data["last_update"])
                        )
                        session.plan_id = session_data.get("plan_id")

                        self.sessions[task_id] = session
                        logging.info(f"Loaded saved research session: {task_id}")

                except Exception as e:
                    logging.error(f"Failed to load session from {session_file}: {e}")
                    # Remove corrupted session file
                    session_file.unlink()

        except Exception as e:
            logging.error(f"Error loading sessions: {e}")

    async def resume_session(self, task_id: str) -> Optional[ActiveResearchSession]:
        """Resume a saved research session."""
        if task_id not in self.sessions:
            return None

        session = self.sessions[task_id]

        # Recreate the full session components
        try:
            memory_manager = MemoryManager()
            ollama_config = OllamaConfig()
            multi_agent_system = MultiAgentSystem(memory_manager, ollama_config)
            orchestrator = ResearchOrchestrator(multi_agent_system, None, memory_manager)

            # Initialize systems
            await multi_agent_system.initialize_system(num_workers=2)
            await memory_manager.start_monitoring()

            # Update session with full components
            session.orchestrator = orchestrator
            session.multi_agent_system = multi_agent_system
            session.memory_manager = memory_manager

            # Start progress broadcasting again
            asyncio.create_task(session._broadcast_progress())

            logging.info(f"Resumed research session: {task_id}")
            return session

        except Exception as e:
            logging.error(f"Failed to resume session {task_id}: {e}")
            return None

    def list_saved_sessions(self) -> Dict[str, Dict]:
        """List all saved research sessions."""
        sessions = {}
        try:
            for session_file in self.sessions_dir.glob("*.json"):
                try:
                    with open(session_file, 'r') as f:
                        session_data = json.load(f)
                    sessions[session_data["task_id"]] = session_data
                except Exception as e:
                    logging.error(f"Error reading session file {session_file}: {e}")
        except Exception as e:
            logging.error(f"Error listing sessions: {e}")

        return sessions

    def delete_session(self, task_id: str):
        """Delete a saved research session."""
        try:
            session_file = self.sessions_dir / f"{task_id}.json"
            if session_file.exists():
                session_file.unlink()

            if task_id in self.sessions:
                session = self.sessions[task_id]
                if session._running_task and not session._running_task.done():
                    session._running_task.cancel()
                del self.sessions[task_id]

            logging.info(f"Deleted research session: {task_id}")
        except Exception as e:
            logging.error(f"Failed to delete session {task_id}: {e}")


# Global instance
research_session_manager = ResearchSessionManager()