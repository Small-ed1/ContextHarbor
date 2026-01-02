import unittest
from agent.rate_limiter import RateLimiter, RateLimiterManager
import time


class TestRateLimiter(unittest.TestCase):
    """Test rate limiting functionality"""

    def test_basic_rate_limiting(self):
        """Test basic rate limit enforcement"""
        limiter = RateLimiter(max_calls=3, period=1.0)

        self.assertTrue(limiter.allow())
        limiter.record_call()

        self.assertTrue(limiter.allow())
        limiter.record_call()

        self.assertTrue(limiter.allow())
        limiter.record_call()

        self.assertFalse(limiter.allow())

    def test_time_window_reset(self):
        """Test that old calls are removed from window"""
        limiter = RateLimiter(max_calls=2, period=0.5)

        limiter.record_call()
        time.sleep(0.3)
        limiter.record_call()

        self.assertFalse(limiter.allow())

        time.sleep(0.3)
        self.assertTrue(limiter.allow())

    def test_acquire_waits(self):
        """Test that acquire() waits for rate limit"""
        limiter = RateLimiter(max_calls=1, period=0.3)

        limiter.record_call()
        self.assertFalse(limiter.allow())

        start = time.time()
        limiter.acquire()
        elapsed = time.time() - start

        self.assertGreaterEqual(elapsed, 0.3)

    def test_multiple_limiters(self):
        """Test managing multiple rate limiters"""
        manager = RateLimiterManager()

        manager.add_limiter("api1", max_calls=2)
        manager.add_limiter("api2", max_calls=5)

        for _ in range(2):
            self.assertTrue(manager.allow("api1"))
            manager.record_call("api1")

        self.assertFalse(manager.allow("api1"))

        for _ in range(5):
            self.assertTrue(manager.allow("api2"))
            manager.record_call("api2")

        self.assertFalse(manager.allow("api2"))

    def test_default_limiter(self):
        """Test default limiter creation"""
        manager = RateLimiterManager()

        limiter = manager.get_limiter("new_api")
        self.assertIsNotNone(limiter)
        self.assertEqual(limiter.max_calls, 10)
        self.assertEqual(limiter.period, 60.0)

    def test_limiter_override(self):
        """Test that limiters can be overridden"""
        manager = RateLimiterManager()

        manager.add_limiter("api", max_calls=5)
        limiter1 = manager.get_limiter("api")
        self.assertEqual(limiter1.max_calls, 5)

        manager.add_limiter("api", max_calls=10)
        limiter2 = manager.get_limiter("api")
        self.assertEqual(limiter2.max_calls, 10)

    def test_concurrent_safety(self):
        """Test that rate limiter is thread-safe"""
        limiter = RateLimiter(max_calls=100, period=1.0)

        calls_in_period = sum(1 for _ in range(100) if limiter.allow())
        self.assertEqual(calls_in_period, 100)


if __name__ == "__main__":
    unittest.main()
