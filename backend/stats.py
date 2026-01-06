"""Statistics tracking for the backend API.

Provides thread-safe counters for requests, chats, and research operations.
"""

from threading import Lock

stats = {"requests": 0, "chats": 0, "research": 0}
stats_lock = Lock()


def increment_stat(key: str):
    with stats_lock:
        stats[key] += 1


def get_stats():
    with stats_lock:
        return stats.copy()
