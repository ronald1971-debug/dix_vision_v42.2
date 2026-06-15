"""Tests for Unified Cognitive OS Architecture Integration."""

import unittest
import sys
import os
from typing import Mapping

# Add paths to imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from cognitive_os import (
    CognitiveOSKernel,
    get_cognitive_os_kernel,
    SystemLayer,
    SystemStatus,
    CognitiveOSMetrics,
)


class TestCognitiveOSKernel(unittest.TestCase):
    """Test cases for Cognitive OS kernel."""

    def setUp(self):
        """Set up test fixtures."""
        self.kernel = get_cognitive_os_kernel()

    def test_singleton_kernel(self):
        """Test that the kernel is a singleton."""
        kernel1 = get_cognitive_os_kernel()
        kernel2 = get_cognitive_os_kernel()
        self.assertIs(kernel1, kernel2)

    def test_initialize_system(self):
        """Test system initialization."""
        success = self.kernel.initialize_system()

        self.assertTrue(success)
        self.assertEqual(self.kernel._status, SystemStatus.OPERATIONAL)

    def test_get_system_metrics(self):
        """Test getting system metrics."""
        # Initialize first
        self.kernel.initialize_system()

        metrics = self.kernel.get_system_metrics()

        self.assertIsInstance(metrics, CognitiveOSMetrics)
        self.assertEqual(metrics.system_id, "cognitive_os_v42.2")
        self.assertEqual(metrics.status, SystemStatus.OPERATIONAL)
        self.assertGreaterEqual(metrics.health_score, 0.0)
        self.assertLessEqual(metrics.health_score, 1.0)

    def test_get_component_status(self):
        """Test getting component status."""
        # Initialize first
        self.kernel.initialize_system()

        status = self.kernel.get_component_status()

        self.assertIsInstance(status, Mapping)
        self.assertIn("governance_unified", status)
        self.assertIn("execution_unified", status)
        self.assertIn("m1_knowledge_layer", status)

    def test_activate_layer(self):
        """Test layer activation."""
        # Deactivate a layer first
        self.kernel._active_layers.discard(SystemLayer.OPERATOR)

        success = self.kernel.activate_layer(SystemLayer.OPERATOR)

        self.assertTrue(success)
        self.assertIn(SystemLayer.OPERATOR, self.kernel._active_layers)

    def test_deactivate_layer(self):
        """Test layer deactivation."""
        # Ensure layer is active
        self.kernel._active_layers.add(SystemLayer.OPERATOR)

        success = self.kernel.deactivate_layer(SystemLayer.OPERATOR)

        self.assertTrue(success)
        self.assertNotIn(SystemLayer.OPERATOR, self.kernel._active_layers)

    def test_statistics(self):
        """Test Cognitive OS statistics."""
        # Initialize first
        self.kernel.initialize_system()

        stats = self.kernel.get_statistics()

        self.assertIsInstance(stats, dict)
        self.assertEqual(stats["system_id"], "cognitive_os_v42.2")
        self.assertEqual(stats["status"], SystemStatus.OPERATIONAL)
        self.assertIn("active_layers", stats)
        self.assertIn("total_integrations", stats)


class TestCognitiveOSIntegration(unittest.TestCase):
    """Integration tests for complete Cognitive OS architecture."""

    def test_complete_system_startup(self):
        """Test complete system startup with all phases."""
        kernel = get_cognitive_os_kernel()

        # Initialize system
        success = kernel.initialize_system()
        self.assertTrue(success)

        # Verify system is operational
        metrics = kernel.get_system_metrics()
        self.assertEqual(metrics.status, SystemStatus.OPERATIONAL)
        self.assertGreater(metrics.health_score, 0.5)  # Should have most components active

        # Verify components are integrated
        component_status = kernel.get_component_status()
        total_active = sum(1 for status in component_status.values() if status == "active")
        self.assertGreater(total_active, 2)  # At least some components should be active

    def test_layer_activation_sequence(self):
        """Test proper layer activation sequence."""
        kernel = get_cognitive_os_kernel()

        # Test operator layer (highest level)
        kernel.activate_layer(SystemLayer.OPERATOR)
        self.assertIn(SystemLayer.OPERATOR, kernel._active_layers)

        # Test governance layer
        kernel.activate_layer(SystemLayer.GOVERNANCE)
        self.assertIn(SystemLayer.GOVERNANCE, kernel._active_layers)

        # Test cognitive layer
        kernel.activate_layer(SystemLayer.COGNITIVE)
        self.assertIn(SystemLayer.COGNITIVE, kernel._active_layers)

        # Test execution layer
        kernel.activate_layer(SystemLayer.EXECUTION)
        self.assertIn(SystemLayer.EXECUTION, kernel._active_layers)

        # Test capital layer (lowest level)
        kernel.activate_layer(SystemLayer.CAPITAL)
        self.assertIn(SystemLayer.CAPITAL, kernel._active_layers)

    def test_system_health_calculation(self):
        """Test system health calculation."""
        kernel = get_cognitive_os_kernel()
        kernel.initialize_system()

        metrics = kernel.get_system_metrics()

        # Health score should be between 0 and 1
        self.assertGreaterEqual(metrics.health_score, 0.0)
        self.assertLessEqual(metrics.health_score, 1.0)

        # Performance score should also be between 0 and 1
        self.assertGreaterEqual(metrics.performance_score, 0.0)
        self.assertLessEqual(metrics.performance_score, 1.0)


def run_tests():
    """Run all unified Cognitive OS architecture tests."""
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()

    suite.addTests(loader.loadTestsFromTestCase(TestCognitiveOSKernel))
    suite.addTests(loader.loadTestsFromTestCase(TestCognitiveOSIntegration))

    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)

    print("\n" + "="*70)
    print("UNIFIED COGNITIVE OS ARCHITECTURE TEST SUMMARY")
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
