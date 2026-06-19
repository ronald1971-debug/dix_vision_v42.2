"""Tests for the unified governance system consolidation."""

import unittest
import warnings
import sys
import os

# Add paths to imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

# Import the unified governance system
from governance_unified import (
    UnifiedGovernanceKernel,
    get_unified_governance_kernel,
    GovernanceRequest,
    GovernanceDecision,
    GovernanceOutcome,
    AuthorityRequest,
    AuthorityDecision,
    ModeTransitionRequest,
    ModeTransitionResult,
    RiskAssessment,
    SystemMode,
    IntentType,
)


class TestUnifiedGovernanceSystem(unittest.TestCase):
    """Test cases for the unified governance system."""

    def setUp(self):
        """Set up test fixtures."""
        self.kernel = get_unified_governance_kernel()

    def test_singleton_kernel(self):
        """Test that the governance kernel is a singleton."""
        kernel1 = get_unified_governance_kernel()
        kernel2 = get_unified_governance_kernel()
        self.assertIs(kernel1, kernel2)

    def test_governance_request_creation(self):
        """Test creating a governance request."""
        request = GovernanceRequest(
            request_id="test_request_1",
            intent_type=IntentType.MARKET_INTENT,
            source="indira_cognitive",
            payload={"action": "execute_trade", "symbol": "BTC"},
            priority=8,
            timestamp_ns=123456789,
        )

        self.assertEqual(request.request_id, "test_request_1")
        self.assertEqual(request.intent_type, IntentType.MARKET_INTENT)
        self.assertEqual(request.source, "indira_cognitive")
        self.assertEqual(request.priority, 8)

    def test_governance_decision_processing(self):
        """Test processing a governance request."""
        request = GovernanceRequest(
            request_id="test_request_2",
            intent_type=IntentType.MARKET_INTENT,
            source="indira_cognitive",
            payload={"action": "execute_trade"},
            priority=5,
        )

        decision = self.kernel.process_governance_request(request)

        self.assertIsInstance(decision, GovernanceDecision)
        self.assertEqual(decision.request_id, "test_request_2")
        self.assertIn(decision.outcome, GovernanceOutcome)

    def test_authority_check(self):
        """Test authority checking functionality."""
        request = AuthorityRequest(
            request_id="auth_test_1",
            actor="operator",
            action="execute_trade",
            resource="trading_account",
            context={"clearance": "admin"},
            timestamp_ns=123456789,
        )

        decision = self.kernel.authority_check(request)

        self.assertIsInstance(decision, AuthorityDecision)
        self.assertEqual(decision.request_id, "auth_test_1")

    def test_mode_transition(self):
        """Test system mode transitions."""
        request = ModeTransitionRequest(
            request_id="mode_test_1",
            current_mode=SystemMode.NORMAL,
            target_mode=SystemMode.CONSERVATIVE,
            reason="Market volatility increased",
            requested_by="operator",
            timestamp_ns=123456789,
        )

        result = self.kernel.mode_transition(request)

        self.assertIsInstance(result, ModeTransitionResult)
        self.assertEqual(result.request_id, "mode_test_1")

        if result.success:
            self.assertEqual(self.kernel.get_current_mode(), SystemMode.CONSERVATIVE)

    def test_risk_assessment(self):
        """Test risk assessment functionality."""
        action = {
            "type": "trade",
            "symbol": "BTC",
            "size": "1.0",
            "leverage": "2.0",
        }

        assessment = self.kernel.risk_assessment(action)

        self.assertIsInstance(assessment, RiskAssessment)
        self.assertGreaterEqual(assessment.risk_level, 0.0)
        self.assertLessEqual(assessment.risk_level, 1.0)

    def test_governance_statistics(self):
        """Test governance statistics."""
        stats = self.kernel.get_governance_statistics()

        self.assertIsInstance(stats, dict)
        self.assertIn("total_decisions", stats)
        self.assertIn("total_authority_checks", stats)
        self.assertIn("total_mode_transitions", stats)
        self.assertIn("current_mode", stats)

    def test_backward_compatibility_governance(self):
        """Test backward compatibility with old governance imports."""
        # Suppress deprecation warnings for this test
        with warnings.catch_warnings():
            warnings.simplefilter("ignore", DeprecationWarning)
            
            try:
                # This should work due to backward compatibility
                from governance import get_governance_kernel
                
                # The returned kernel should be the unified one
                legacy_kernel = get_governance_kernel()
                self.assertIsInstance(legacy_kernel, UnifiedGovernanceKernel)
            except ImportError:
                # If governance_unified is not available, this is expected
                self.skipTest("governance_unified not available for legacy compatibility test")

    def test_backward_compatibility_governance_engine(self):
        """Test backward compatibility with old governance_engine imports."""
        with warnings.catch_warnings():
            warnings.simplefilter("ignore", DeprecationWarning)
            
            try:
                from governance_engine import GovernanceEngine
                
                # The returned engine should be the unified kernel
                engine = GovernanceEngine()
                self.assertIsInstance(engine, UnifiedGovernanceKernel)
            except ImportError:
                # If governance_unified is not available, this is expected
                self.skipTest("governance_unified not available for legacy compatibility test")


class TestSystemIntegration(unittest.TestCase):
    """Test system integration with unified governance."""

    def test_end_to_end_governance_flow(self):
        """Test complete governance flow from request to decision."""
        kernel = get_unified_governance_kernel()

        # Create a market intent request
        request = GovernanceRequest(
            request_id="e2e_test_1",
            intent_type=IntentType.MARKET_INTENT,
            source="indira_cognitive",
            payload={
                "strategy": "momentum",
                "symbol": "ETH",
                "size": "2.0",
            },
            priority=7,
        )

        # Process the request
        decision = kernel.process_governance_request(request)

        # Verify the decision
        self.assertEqual(decision.request_id, "e2e_test_1")
        self.assertIsNotNone(decision.outcome)

        # Check that the decision was recorded
        stats = kernel.get_governance_statistics()
        self.assertGreater(stats["total_decisions"], 0)


def run_tests():
    """Run all unified governance system tests."""
    # Create test suite
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()

    # Add all test classes
    suite.addTests(loader.loadTestsFromTestCase(TestUnifiedGovernanceSystem))
    suite.addTests(loader.loadTestsFromTestCase(TestSystemIntegration))

    # Run tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)

    # Print summary
    print("\n" + "="*70)
    print("UNIFIED GOVERNANCE SYSTEM TEST SUMMARY")
    print("="*70)
    print(f"Tests run: {result.testsRun}")
    print(f"Successes: {result.testsRun - len(result.failures) - len(result.errors)}")
    print(f"Failures: {len(result.failures)}")
    print(f"Errors: {len(result.errors)}")
    print(f"Skipped: {len(result.skipped)}")
    print("="*70)

    return result.wasSuccessful()


if __name__ == "__main__":
    success = run_tests()
    sys.exit(0 if success else 1)