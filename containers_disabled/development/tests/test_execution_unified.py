"""Tests for the unified execution system consolidation."""

import os
import sys
import unittest
import warnings

# Add paths to imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

# Import the unified execution system
from execution_unified import (
    Action,
    ExecutionLane,
    ExecutionRequest,
    ExecutionResult,
    ExecutionStatus,
    ExecutionType,
    Intent,
    UnifiedExecutionKernel,
    get_unified_execution_kernel,
)


class TestUnifiedExecutionSystem(unittest.TestCase):
    """Test cases for the unified execution system."""

    def setUp(self):
        """Set up test fixtures."""
        self.kernel = get_unified_execution_kernel()

    def test_singleton_kernel(self):
        """Test that the execution kernel is a singleton."""
        kernel1 = get_unified_execution_kernel()
        kernel2 = get_unified_execution_kernel()
        self.assertIs(kernel1, kernel2)

    def test_execution_request_creation(self):
        """Test creating an execution request."""
        request = ExecutionRequest(
            request_id="test_request_1",
            execution_type=ExecutionType.TACTICAL,
            source="indira_cognitive",
            payload={"action": "execute_trade", "symbol": "BTC"},
            priority=8,
            preferred_lane=ExecutionLane.FAST_LANE,
            timestamp_ns=123456789,
        )

        self.assertEqual(request.request_id, "test_request_1")
        self.assertEqual(request.execution_type, ExecutionType.TACTICAL)
        self.assertEqual(request.source, "indira_cognitive")
        self.assertEqual(request.priority, 8)

    def test_strategic_execution(self):
        """Test strategic execution functionality."""
        strategy = {
            "strategy_type": "momentum",
            "portfolio": "main",
            "risk_level": "medium",
        }

        result = self.kernel.execute_strategy(strategy)

        self.assertIsInstance(result, ExecutionResult)
        self.assertIn(result.status, ExecutionStatus)
        self.assertEqual(result.executed_lane, ExecutionLane.NORMAL_LANE)

    def test_tactical_execution(self):
        """Test tactical trade execution functionality."""
        trade = {
            "symbol": "ETH",
            "size": "2.0",
            "side": "buy",
            "price": "2000.0",
        }

        result = self.kernel.execute_trade(trade)

        self.assertIsInstance(result, ExecutionResult)
        self.assertIn(result.status, ExecutionStatus)

    def test_intent_to_action_execution(self):
        """Test intent to action boundary execution."""
        intent = Intent(
            intent_id="intent_1",
            intent_type="trading",
            content={"symbol": "BTC", "size": "1.0"},
            confidence=0.9,
            source="INDIRA",
        )

        action = self.kernel.execute_intent(intent)

        self.assertIsInstance(action, Action)
        self.assertEqual(action.intent_id, "intent_1")

    def test_execution_monitoring(self):
        """Test execution monitoring functionality."""
        # Execute a request first
        trade = {"symbol": "BTC", "size": "1.0"}
        result = self.kernel.execute_trade(trade)

        # Monitor the execution
        status = self.kernel.monitor_execution(result.request_id)

        # Should be completed (not in active requests)
        self.assertIsNotNone(status)
        self.assertEqual(status, ExecutionStatus.COMPLETED)

    def test_hazard_handling(self):
        """Test hazard event handling."""
        hazard = {
            "hazard_type": "price_spike",
            "severity": "HIGH",
            "symbol": "BTC",
        }

        result = self.kernel.handle_hazard(hazard)

        self.assertIsInstance(result, ExecutionResult)
        self.assertEqual(result.executed_lane, ExecutionLane.HAZARD_LANE)

    def test_execution_statistics(self):
        """Test execution statistics."""
        # Execute some operations to generate statistics
        self.kernel.execute_strategy({"test": "strategy"})
        self.kernel.execute_trade({"test": "trade"})

        stats = self.kernel.get_execution_statistics()

        self.assertIsInstance(stats, dict)
        self.assertIn("total_executions", stats)
        self.assertIn("total_strategic", stats)
        self.assertIn("total_tactical", stats)
        self.assertGreater(stats["total_executions"], 0)

    def test_backward_compatibility_execution(self):
        """Test backward compatibility with old execution imports."""
        with warnings.catch_warnings():
            warnings.simplefilter("ignore", DeprecationWarning)

            try:
                from execution import DyonEngine

                # The returned engine should be the unified one
                engine = DyonEngine()
                self.assertIsInstance(engine, UnifiedExecutionKernel)
            except ImportError:
                self.skipTest("execution_unified not available for legacy compatibility test")

    def test_backward_compatibility_execution_engine(self):
        """Test backward compatibility with old execution_engine imports."""
        with warnings.catch_warnings():
            warnings.simplefilter("ignore", DeprecationWarning)

            try:
                from execution_engine import ExecutionEngine

                # The returned engine should be the unified kernel
                engine = ExecutionEngine()
                self.assertIsInstance(engine, UnifiedExecutionKernel)
            except ImportError:
                self.skipTest("execution_unified not available for legacy compatibility test")


class TestExecutionIntegration(unittest.TestCase):
    """Test execution integration scenarios."""

    def test_intent_to_action_boundary(self):
        """Test the clean intent → action boundary."""
        kernel = get_unified_execution_kernel()

        # Create a trading intent from INDIRA
        intent = Intent(
            intent_id="test_intent_1",
            intent_type="trading",
            content={"symbol": "ETH", "side": "buy", "size": "2.0"},
            confidence=0.85,
            source="INDIRA",
        )

        # Execute the intent (converts to action)
        action = kernel.execute_intent(intent)

        # Verify the boundary is maintained
        self.assertEqual(action.intent_id, "test_intent_1")
        self.assertIn("execution", action.action_type.lower())
        # The action should be implementation, not intent generation
        self.assertNotIn("intent", action.action_type.lower())


def run_tests():
    """Run all unified execution system tests."""
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()

    suite.addTests(loader.loadTestsFromTestCase(TestUnifiedExecutionSystem))
    suite.addTests(loader.loadTestsFromTestCase(TestExecutionIntegration))

    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)

    print("\n" + "=" * 70)
    print("UNIFIED EXECUTION SYSTEM TEST SUMMARY")
    print("=" * 70)
    print(f"Tests run: {result.testsRun}")
    print(f"Successes: {result.testsRun - len(result.failures) - len(result.errors)}")
    print(f"Failures: {len(result.failures)}")
    print(f"Errors: {len(result.errors)}")
    print(f"Skipped: {len(result.skipped)}")
    print("=" * 70)

    return result.wasSuccessful()


if __name__ == "__main__":
    success = run_tests()
    sys.exit(0 if success else 1)
