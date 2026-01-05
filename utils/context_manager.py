"""
Context Manager for Large Conversation Context Handling
Provides sliding window context management for long conversations and research sessions.
"""

import asyncio
import json
import logging
import os
import threading
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any, Dict, List, Optional, Set, Tuple, Union

from .memory_manager import MemoryAwareMixin, MemoryManager


@dataclass
class ContextWindowStrategy:
    """Strategy for managing context windows."""

    window_size: int = 4000  # tokens
    overlap: int = 200  # tokens to overlap between windows
    max_windows: int = 10
    priority_decay: float = 0.8  # how much priority decays over time
    importance_threshold: float = 0.3  # minimum importance to keep


@dataclass
class ContextChunk:
    """A chunk of context with metadata."""

    id: str
    content: str
    timestamp: datetime = field(default_factory=datetime.now)
    importance: float = 0.5
    source: str = ""
    topic: str = ""
    token_count: int = 0
    metadata: Dict[str, Any] = field(default_factory=dict)
    references: Set[str] = field(default_factory=set)  # IDs of related chunks
    effective_importance: float = field(default=0.0, init=False)  # Computed at runtime


@dataclass
class ContextSession:
    """A conversation or research session with managed context."""

    session_id: str
    title: str
    description: str
    created_at: datetime = field(default_factory=datetime.now)
    last_accessed: datetime = field(default_factory=datetime.now)
    total_tokens: int = 0
    chunk_count: int = 0
    chunks: Dict[str, ContextChunk] = field(default_factory=dict)
    metadata: Dict[str, Any] = field(default_factory=dict)
    strategy: ContextWindowStrategy = field(default_factory=ContextWindowStrategy)


class ContextManager(MemoryAwareMixin):
    """
    Manages large conversation contexts using sliding windows and importance-based retention.
    Integrates with memory manager for RAM optimization.
    """

    def __init__(
        self,
        memory_manager: MemoryManager,
        storage_dir: str = "./data/contexts",
        max_sessions: int = 50,
        cleanup_interval: int = 3600,  # seconds
    ):
        super().__init__(memory_manager)
        self.storage_dir = Path(storage_dir)
        self.storage_dir.mkdir(parents=True, exist_ok=True)

        self.max_sessions = max_sessions
        self.sessions: Dict[str, ContextSession] = {}
        self.lock = threading.RLock()

        # Background cleanup
        self.cleanup_interval = cleanup_interval
        self._cleanup_thread: Optional[threading.Thread] = None
        self._running = True

        # Token estimation (rough)
        self.avg_chars_per_token = 4

        self.logger = logging.getLogger(__name__)

        # Start background cleanup
        self._start_cleanup_thread()

    def __del__(self):
        """Cleanup on destruction."""
        self._running = False
        if self._cleanup_thread:
            self._cleanup_thread.join(timeout=5)

    async def create_session(
        self,
        title: str,
        description: str = "",
        metadata: Optional[Dict[str, Any]] = None,
        strategy: Optional[ContextWindowStrategy] = None,
    ) -> str:
        """Create a new context session."""
        session_id = f"ctx_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{hash(title) % 10000}"

        session = ContextSession(
            session_id=session_id,
            title=title,
            description=description,
            metadata=metadata or {},
            strategy=strategy or ContextWindowStrategy(),
        )

        with self.lock:
            self.sessions[session_id] = session

            # Enforce session limit
            if len(self.sessions) > self.max_sessions:
                self._cleanup_old_sessions()

        self.logger.info(f"Created context session: {session_id} - {title}")
        return session_id

    async def add_context(
        self,
        content: str,
        window_id: str,
        topic: str = "",
        importance: float = 0.5,
        source: str = "",
        metadata: Optional[Dict[str, Any]] = None,
    ) -> str:
        """Add context content to a session."""
        if window_id not in self.sessions:
            raise ValueError(f"Session {window_id} not found")

        session = self.sessions[window_id]

        # Estimate token count
        token_count = len(content) // self.avg_chars_per_token

        # Create chunk
        chunk_id = f"chunk_{session.session_id}_{len(session.chunks)}"
        chunk = ContextChunk(
            id=chunk_id,
            content=content,
            importance=importance,
            source=source,
            topic=topic,
            token_count=token_count,
            metadata=metadata or {},
        )

        with self.lock:
            session.chunks[chunk_id] = chunk
            session.total_tokens += token_count
            session.chunk_count += 1
            session.last_accessed = datetime.now()

        self.logger.debug(f"Added context chunk: {chunk_id} ({token_count} tokens)")

        # Check if we need to optimize context
        await self._optimize_context_if_needed(session)

        return chunk_id

    async def get_context(
        self,
        session_id: str,
        max_tokens: Optional[int] = None,
        include_metadata: bool = False,
    ) -> Dict[str, Any]:
        """Get optimized context for a session."""
        if session_id not in self.sessions:
            raise ValueError(f"Session {session_id} not found")

        session = self.sessions[session_id]
        strategy = session.strategy

        # Update access time
        session.last_accessed = datetime.now()

        # Get relevant chunks
        chunks = list(session.chunks.values())

        # Sort by importance and recency
        now = datetime.now()
        for chunk in chunks:
            # Apply time decay to importance
            age_hours = (now - chunk.timestamp).total_seconds() / 3600
            time_decay = max(0.1, strategy.priority_decay ** age_hours)
            chunk.effective_importance = chunk.importance * time_decay

        chunks.sort(key=lambda x: x.effective_importance, reverse=True)

        # Build context windows
        windows = []
        current_window = []
        current_tokens = 0

        for chunk in chunks:
            if current_tokens + chunk.token_count > strategy.window_size:
                if current_window:
                    windows.append(current_window)
                    current_window = []
                    current_tokens = 0

                # If chunk is too big, truncate it
                if chunk.token_count > strategy.window_size:
                    truncated_content = chunk.content[: strategy.window_size * self.avg_chars_per_token]
                    chunk_copy = ContextChunk(
                        id=chunk.id,
                        content=truncated_content,
                        timestamp=chunk.timestamp,
                        importance=chunk.importance,
                        source=chunk.source,
                        topic=chunk.topic,
                        token_count=strategy.window_size,
                        metadata=chunk.metadata,
                        references=chunk.references,
                    )
                    current_window.append(chunk_copy)
                    current_tokens = strategy.window_size
                else:
                    current_window.append(chunk)
                    current_tokens += chunk.token_count
            else:
                current_window.append(chunk)
                current_tokens += chunk.token_count

        if current_window:
            windows.append(current_window)

        # Limit number of windows
        windows = windows[: strategy.max_windows]

        # Convert to response format
        context_data = {
            "session_id": session_id,
            "title": session.title,
            "total_tokens": session.total_tokens,
            "windows": [],
        }

        for i, window in enumerate(windows):
            window_content = []
            window_tokens = 0

            for chunk in window:
                chunk_data = {
                    "id": chunk.id,
                    "content": chunk.content,
                    "importance": chunk.importance,
                    "source": chunk.source,
                    "topic": chunk.topic,
                    "token_count": chunk.token_count,
                }

                if include_metadata:
                    chunk_data["metadata"] = chunk.metadata
                    chunk_data["timestamp"] = chunk.timestamp.isoformat()
                    chunk_data["references"] = list(chunk.references)

                window_content.append(chunk_data)
                window_tokens += chunk.token_count

            context_data["windows"].append({
                "window_id": i,
                "content": window_content,
                "total_tokens": window_tokens,
            })

        return context_data

    async def update_chunk_importance(
        self, session_id: str, chunk_id: str, importance: float
    ):
        """Update the importance of a context chunk."""
        if session_id not in self.sessions:
            raise ValueError(f"Session {session_id} not found")

        session = self.sessions[session_id]
        if chunk_id not in session.chunks:
            raise ValueError(f"Chunk {chunk_id} not found in session {session_id}")

        session.chunks[chunk_id].importance = max(0.0, min(1.0, importance))
        session.chunks[chunk_id].timestamp = datetime.now()  # Refresh timestamp

    async def delete_session(self, session_id: str):
        """Delete a context session."""
        if session_id in self.sessions:
            with self.lock:
                del self.sessions[session_id]
            self._delete_session_file(session_id)
            self.logger.info(f"Deleted context session: {session_id}")

    async def list_sessions(self) -> List[Dict[str, Any]]:
        """List all active sessions."""
        sessions_data = []
        for session in self.sessions.values():
            sessions_data.append({
                "session_id": session.session_id,
                "title": session.title,
                "description": session.description,
                "created_at": session.created_at.isoformat(),
                "last_accessed": session.last_accessed.isoformat(),
                "total_tokens": session.total_tokens,
                "chunk_count": session.chunk_count,
                "metadata": session.metadata,
            })

        return sessions_data

    def _start_cleanup_thread(self):
        """Start background cleanup thread."""
        self._cleanup_thread = threading.Thread(target=self._cleanup_worker, daemon=True)
        self._cleanup_thread.start()

    def _cleanup_worker(self):
        """Background cleanup worker."""
        while self._running:
            try:
                asyncio.run(self._perform_cleanup())
            except Exception as e:
                self.logger.error(f"Cleanup error: {e}")

            # Wait for next cleanup cycle
            import time
            time.sleep(self.cleanup_interval)

    async def _perform_cleanup(self):
        """Perform cleanup of old sessions and optimize memory."""
        # Remove old sessions
        cutoff = datetime.now() - timedelta(days=7)  # Keep sessions for 7 days
        to_remove = []

        with self.lock:
            for session_id, session in self.sessions.items():
                if session.last_accessed < cutoff:
                    to_remove.append(session_id)

            for session_id in to_remove:
                del self.sessions[session_id]
                self._delete_session_file(session_id)

        if to_remove:
            self.logger.info(f"Cleaned up {len(to_remove)} old context sessions")

        # Save current sessions to disk
        await self._save_sessions()

    def _cleanup_old_sessions(self):
        """Remove oldest sessions when limit exceeded."""
        if len(self.sessions) <= self.max_sessions:
            return

        # Sort by last accessed
        sorted_sessions = sorted(
            self.sessions.items(),
            key=lambda x: x[1].last_accessed
        )

        to_remove = len(self.sessions) - self.max_sessions
        for session_id, _ in sorted_sessions[:to_remove]:
            del self.sessions[session_id]
            self._delete_session_file(session_id)

    async def _optimize_context_if_needed(self, session: ContextSession):
        """Optimize context if memory usage is high."""
        strategy = session.strategy

        # Check if we exceed memory thresholds
        if session.total_tokens > strategy.window_size * strategy.max_windows:
            await self._optimize_session_context(session)

    async def _optimize_session_context(self, session: ContextSession):
        """Optimize a session's context by removing low-importance chunks."""
        strategy = session.strategy

        # Get chunks sorted by importance
        chunks = list(session.chunks.values())
        chunks.sort(key=lambda x: x.importance)

        # Remove chunks below importance threshold
        to_remove = []
        for chunk in chunks:
            if chunk.importance < strategy.importance_threshold:
                to_remove.append(chunk.id)

        # Also remove oldest chunks if still too many
        remaining_chunks = [c for c in chunks if c.id not in to_remove]
        if len(remaining_chunks) > strategy.max_windows * 2:  # Allow some buffer
            remaining_chunks.sort(key=lambda x: x.timestamp)
            extra_to_remove = len(remaining_chunks) - (strategy.max_windows * 2)
            to_remove.extend([c.id for c in remaining_chunks[:extra_to_remove]])

        # Remove chunks
        for chunk_id in to_remove:
            if chunk_id in session.chunks:
                session.total_tokens -= session.chunks[chunk_id].token_count
                session.chunk_count -= 1
                del session.chunks[chunk_id]

        if to_remove:
            self.logger.debug(f"Optimized session {session.session_id}: removed {len(to_remove)} chunks")

    async def _save_sessions(self):
        """Save sessions to disk."""
        for session_id, session in self.sessions.items():
            await self._save_session(session)

    async def _save_session(self, session: ContextSession):
        """Save a session to disk."""
        session_file = self.storage_dir / f"{session.session_id}.json"

        session_data = {
            "session_id": session.session_id,
            "title": session.title,
            "description": session.description,
            "created_at": session.created_at.isoformat(),
            "last_accessed": session.last_accessed.isoformat(),
            "total_tokens": session.total_tokens,
            "chunk_count": session.chunk_count,
            "metadata": session.metadata,
            "strategy": {
                "window_size": session.strategy.window_size,
                "overlap": session.strategy.overlap,
                "max_windows": session.strategy.max_windows,
                "priority_decay": session.strategy.priority_decay,
                "importance_threshold": session.strategy.importance_threshold,
            },
            "chunks": {},
        }

        for chunk_id, chunk in session.chunks.items():
            session_data["chunks"][chunk_id] = {
                "id": chunk.id,
                "content": chunk.content,
                "timestamp": chunk.timestamp.isoformat(),
                "importance": chunk.importance,
                "source": chunk.source,
                "topic": chunk.topic,
                "token_count": chunk.token_count,
                "metadata": chunk.metadata,
                "references": list(chunk.references),
            }

        try:
            with open(session_file, "w", encoding="utf-8") as f:
                json.dump(session_data, f, indent=2, ensure_ascii=False)
        except Exception as e:
            self.logger.error(f"Failed to save session {session.session_id}: {e}")

    async def _load_sessions(self):
        """Load sessions from disk."""
        if not self.storage_dir.exists():
            return

        for session_file in self.storage_dir.glob("*.json"):
            try:
                with open(session_file, "r", encoding="utf-8") as f:
                    session_data = json.load(f)

                # Reconstruct session
                strategy_data = session_data.get("strategy", {})
                strategy = ContextWindowStrategy(
                    window_size=strategy_data.get("window_size", 4000),
                    overlap=strategy_data.get("overlap", 200),
                    max_windows=strategy_data.get("max_windows", 10),
                    priority_decay=strategy_data.get("priority_decay", 0.8),
                    importance_threshold=strategy_data.get("importance_threshold", 0.3),
                )

                session = ContextSession(
                    session_id=session_data["session_id"],
                    title=session_data["title"],
                    description=session_data.get("description", ""),
                    created_at=datetime.fromisoformat(session_data["created_at"]),
                    last_accessed=datetime.fromisoformat(session_data["last_accessed"]),
                    total_tokens=session_data.get("total_tokens", 0),
                    chunk_count=session_data.get("chunk_count", 0),
                    metadata=session_data.get("metadata", {}),
                    strategy=strategy,
                )

                # Reconstruct chunks
                for chunk_data in session_data.get("chunks", {}).values():
                    chunk = ContextChunk(
                        id=chunk_data["id"],
                        content=chunk_data["content"],
                        timestamp=datetime.fromisoformat(chunk_data["timestamp"]),
                        importance=chunk_data.get("importance", 0.5),
                        source=chunk_data.get("source", ""),
                        topic=chunk_data.get("topic", ""),
                        token_count=chunk_data.get("token_count", 0),
                        metadata=chunk_data.get("metadata", {}),
                        references=set(chunk_data.get("references", [])),
                    )
                    session.chunks[chunk.id] = chunk

                self.sessions[session.session_id] = session

            except Exception as e:
                self.logger.error(f"Failed to load session from {session_file}: {e}")

    def _delete_session_file(self, session_id: str):
        """Delete a session file from disk."""
        session_file = self.storage_dir / f"{session_id}.json"
        try:
            if session_file.exists():
                session_file.unlink()
        except Exception as e:
            self.logger.error(f"Failed to delete session file {session_file}: {e}")

    async def get_memory_stats(self) -> Dict[str, Any]:
        """Get memory usage statistics."""
        total_sessions = len(self.sessions)
        total_chunks = sum(len(s.chunks) for s in self.sessions.values())
        total_tokens = sum(s.total_tokens for s in self.sessions.values())

        return {
            "total_sessions": total_sessions,
            "total_chunks": total_chunks,
            "total_tokens": total_tokens,
            "avg_chunks_per_session": total_chunks / max(total_sessions, 1),
            "avg_tokens_per_session": total_tokens / max(total_sessions, 1),
        }