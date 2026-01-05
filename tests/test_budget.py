import unittest

from agent.budget import BudgetExceeded, BudgetManager


class TestBudgetManager(unittest.TestCase):
    """Test budget management and resource limits"""

    def test_basic_consumption(self):
        """Test basic tool consumption tracking"""
        bm = BudgetManager(limits={"read_file": 5})
        self.assertEqual(bm.remaining("read_file"), 5)
        bm.consume("read_file", 2)
        self.assertEqual(bm.remaining("read_file"), 3)
        self.assertEqual(bm.used["read_file"], 2)

    def test_budget_enforcement(self):
        """Test that budget limits are enforced"""
        bm = BudgetManager(limits={"read_file": 3})
        bm.consume("read_file", 2)
        self.assertEqual(bm.remaining("read_file"), 1)
        with self.assertRaises(BudgetExceeded):
            bm.consume("read_file", 2)

    def test_zero_consumption(self):
        """Test that consuming zero or negative is a no-op"""
        bm = BudgetManager(limits={"read_file": 5})
        bm.consume("read_file", 0)
        bm.consume("read_file", -1)
        self.assertEqual(bm.remaining("read_file"), 5)
        self.assertEqual(bm.used.get("read_file"), None)

    def test_unlimited_tool(self):
        """Test tools without limits have zero remaining"""
        bm = BudgetManager(limits={"read_file": 5})
        self.assertEqual(bm.remaining("write_file"), 0)

    def test_total_used_calculation(self):
        """Test total usage calculation across multiple tools"""
        bm = BudgetManager(limits={"read_file": 5, "write_file": 3, "search": 10})
        bm.consume("read_file", 3)
        bm.consume("write_file", 2)
        bm.consume("search", 5)
        self.assertEqual(bm.total_used(), 10)

    def test_max_total_budget(self):
        """Test global total budget enforcement"""
        bm = BudgetManager(limits={"read_file": 10, "write_file": 10}, max_total=5)
        bm.consume("read_file", 3)
        with self.assertRaises(BudgetExceeded) as cm:
            bm.consume("write_file", 3)
        self.assertIn("Total tool budget exceeded", str(cm.exception))

    def test_multiple_limits(self):
        """Test managing limits for multiple tools independently"""
        bm = BudgetManager(limits={"tool1": 10, "tool2": 5, "tool3": 3})
        bm.consume("tool1", 5)
        bm.consume("tool2", 3)
        bm.consume("tool3", 2)
        self.assertEqual(bm.remaining("tool1"), 5)
        self.assertEqual(bm.remaining("tool2"), 2)
        self.assertEqual(bm.remaining("tool3"), 1)

    def test_exact_limit_consumption(self):
        """Test consuming exactly the limit amount works"""
        bm = BudgetManager(limits={"tool": 5})
        bm.consume("tool", 5)
        self.assertEqual(bm.remaining("tool"), 0)
        with self.assertRaises(BudgetExceeded):
            bm.consume("tool", 1)

    def test_remaining_never_negative(self):
        """Test remaining() never returns negative values"""
        bm = BudgetManager(limits={"tool": 5})
        with self.assertRaises(BudgetExceeded):
            bm.consume("tool", 7)
        self.assertEqual(bm.remaining("tool"), 5)

    def test_budget_error_message(self):
        """Test that BudgetExceeded has descriptive messages"""
        bm = BudgetManager(limits={"read_file": 3})
        bm.consume("read_file", 2)
        with self.assertRaises(BudgetExceeded) as cm:
            bm.consume("read_file", 3)
        msg = str(cm.exception)
        self.assertIn("read_file", msg)
        self.assertIn("attempted to consume 3", msg)
        self.assertIn("but only 1 remaining", msg)

    def test_empty_budget_manager(self):
        """Test BudgetManager with no limits"""
        bm = BudgetManager(limits={})
        self.assertEqual(bm.total_used(), 0)
        self.assertEqual(bm.remaining("any_tool"), 0)


if __name__ == "__main__":
    unittest.main()
