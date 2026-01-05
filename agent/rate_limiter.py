from __future__ import annotations

import time
from threading import Lock
from typing import Dict


class RateLimiter:
    """Simple rate limiter for API calls"""

    def __init__(self, max_calls: int, period: float = 60.0):
        """
        Initialize rate limiter

        Args:
            max_calls: Maximum number of calls allowed in the period
            period: Time period in seconds (default: 60 seconds)
        """
        self.max_calls = max_calls
        self.period = period
        self.calls: list[float] = []
        self._lock = Lock()

    def allow(self) -> bool:
        """Check if a call is allowed under the rate limit"""
        with self._lock:
            now = time.time()
            self.calls = [
                call_time for call_time in self.calls if now - call_time < self.period
            ]
            return len(self.calls) < self.max_calls

    def acquire(self) -> None:
        """Wait until a call is allowed"""
        while not self.allow():
            time.sleep(0.1)

    def record_call(self) -> None:
        """Record that a call was made"""
        with self._lock:
            self.calls.append(time.time())


class RateLimiterManager:
    """Manage multiple rate limiters for different APIs"""

    def __init__(self):
        self.limiters: Dict[str, RateLimiter] = {}

    def add_limiter(self, name: str, max_calls: int, period: float = 60.0) -> None:
        """Add or update a rate limiter"""
        self.limiters[name] = RateLimiter(max_calls, period)

    def get_limiter(self, name: str) -> RateLimiter:
        """Get a rate limiter by name"""
        if name not in self.limiters:
            self.add_limiter(name, max_calls=10, period=60.0)
        return self.limiters[name]

    def allow(self, name: str) -> bool:
        """Check if a call is allowed for a specific limiter"""
        return self.get_limiter(name).allow()

    def acquire(self, name: str) -> None:
        """Wait until a call is allowed for a specific limiter"""
        self.get_limiter(name).acquire()

    def record_call(self, name: str) -> None:
        """Record that a call was made for a specific limiter"""
        self.get_limiter(name).record_call()
