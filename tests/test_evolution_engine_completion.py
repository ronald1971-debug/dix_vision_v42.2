"""Tests for Evolution Engine Completion (Autonomous Capabilities)."""

import unittest
import sys
import os

# Add paths to imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from evolution_engine import (
    AutonomousEvolutionEngine,
    get_autonomous_evolution_engine,
    AutonomyLevel,
    AutonomyScope,
    AutonomyDecision,
    AutonomousEvolutionResult,
)


class TestAutonomousEvolutionEngine(unittest.TestCase):
    """Test cases for autonomous evolution engine."""

    def setUp(self):
        """Set up test fixtures."""
        self.engine = get_autonomous_evolution_engine()

    def test_singleton_engine(self):
        """Test that the engine is a singleton."""
        engine1 = get_autonomous_evolution_engine()
        engine2 = get_autonomous_evolution_engine()
        self.assertIs(engine1, engine2)

    def test_set_autonomy_level(self):
        """Test setting autonomy level."""
        self.engine.set_autonomy_level(AutonomyLevel.AUTONOMOUS)

        # Should not raise
        stats = self.engine.get_statistics()
        self.assertEqual(stats["autonomy_level"], AutonomyLevel.AUTONOMOUS)

    def test_enable_disable_autonomy_scope(self):
        """Test enabling and disabling autonomy scopes."""
        # Initially should have parameter tuning enabled
        self.assertIn(AutonomyScope.PARAMETER_TUNING, self.engine._autonomy_scopes)

        # Disable parameter tuning
        self.engine.disable_autonomy_scope(AutonomyScope.PARAMETER_TUNING)
        self.assertNotIn(AutonomyScope.PARAMETER_TUNING, self.engine._autonomy_scopes)

        # Re-enable
        self.engine.enable_autonomy_scope(AutonomyScope.PARAMETER_TUNING)
        self.assertIn(AutonomyScope.PARAMETER_TUNING, self.engine._autonomy_scopes)

    def test_autonomous_parameter_tuning_enabled(self):
        """Test autonomous parameter tuning when enabled."""
        parameters = {"learning_rate": 0.01, "threshold": 0.5}
        performance_metrics = {"accuracy": 0.85, "loss": 0.15}
        context = {"mode": "training"}

        result = self.engine.autonomous_parameter_tuning(
            parameters=parameters,
            performance_metrics=performance_metrics,
            context=context,
        )

        self.assertIsInstance(result, AutonomousEvolutionResult)
        self.assertEqual(result.scope, AutonomyScope.PARAMETER_TUNING)
        self.assertIsInstance(result.autonomous_decision, AutonomyDecision)

    def test_autonomous_parameter_tuning_disabled(self):
        """Test autonomous parameter tuning when disabled."""
        self.engine.disable_autonomy_scope(AutonomyScope.PARAMETER_TUNING)

        parameters = {"learning_rate": 0.01}
        performance_metrics = {"accuracy": 0.85}
        context = {"mode": "training"}

        result = self.engine.autonomous_parameter_tuning(
            parameters=parameters,
            performance_metrics=performance_metrics,
            context=context,
        )

        self.assertIsInstance(result, AutonomousEvolutionResult)
        self.assertEqual(result.scope, AutonomyScope.PARAMETER_TUNING)
        # Should have zero mutations since autonomy is disabled
        self.assertEqual(result.mutations_applied, 0)

        # Re-enable for other tests
        self.engine.enable_autonomy_scope(AutonomyScope.PARAMETER_TUNING)

    def test_autonomous_strategy_mutation_enabled(self):
        """Test autonomous strategy mutation when enabled."""
        self.engine.enable_autonomy_scope(AutonomyScope.STRATEGY_MUTATION)

        strategy_config = {"momentum_factor": "0.2", "lookback": "10"}
        performance_history = [0.7, 0.75, 0.8, 0.85]
        context = {"strategy": "momentum"}

        result = self.engine.autonomous_strategy_mutation(
            strategy_config=strategy_config,
            performance_history=performance_history,
            context=context,
        )

        self.assertIsInstance(result, AutonomousEvolutionResult)
        self.assertEqual(result.scope, AutonomyScope.STRATEGY_MUTATION)
        self.assertIsInstance(result.autonomous_decision, AutonomyDecision)

    def test_autonomous_strategy_mutation_disabled(self):
        """Test autonomous strategy mutation when disabled."""
        # Ensure it's disabled
        self.engine.disable_autonomy_scope(AutonomyScope.STRATEGY_MUTATION)

        strategy_config = {"momentum_factor": "0.2"}
        performance_history = [0.7, 0.75]
        context = {"strategy": "momentum"}

        result = self.engine.autonomous_strategy_mutation(
            strategy_config=strategy_config,
            performance_history=performance_history,
            context=context,
        )

        self.assertIsInstance(result, AutonomousEvolutionResult)
        self.assertEqual(result.scope, AutonomyScope.STRATEGY_MUTATION)
        self.assertEqual(result.mutations_applied, 0)

    def test_autonomous_self_improvement_enabled(self):
        """Test autonomous self-improvement when enabled."""
        self.engine.enable_autonomy_scope(AutonomyScope.SYSTEM_ADAPTATION)

        system_metrics = {"cpu_usage": 0.7, "memory_usage": 0.6}
        performance_metrics = {"latency": 0.3, "throughput": 0.8}
        context = {"component": "execution"}

        result = self.engine.autonomous_self_improvement(
            system_metrics=system_metrics,
            performance_metrics=performance_metrics,
            context=context,
        )

        self.assertIsInstance(result, AutonomousEvolutionResult)
        self.assertEqual(result.scope, AutonomyScope.SYSTEM_ADAPTATION)
        self.assertIsInstance(result.autonomous_decision, AutonomyDecision)

    def test_autonomous_self_improvement_disabled(self):
        """Test autonomous self-improvement when disabled."""
        self.engine.disable_autonomy_scope(AutonomyScope.SYSTEM_ADAPTATION)

        system_metrics = {"cpu_usage": 0.7}
        performance_metrics = {"latency": 0.3}
        context = {"component": "execution"}

        result = self.engine.autonomous_self_improvement(
            system_metrics=system_metrics,
            performance_metrics=performance_metrics,
            context=context,
        )

        self.assertIsInstance(result, AutonomousEvolutionResult)
        self.assertEqual(result.scope, AutonomyScope.SYSTEM_ADAPTATION)
        self.assertEqual(result.mutations_applied, 0)

    def test_autonomy_decision_approval(self):
        """Test autonomy decision approval based on level."""
        # Test manual level - should not be approved
        self.engine.set_autonomy_level(AutonomyLevel.MANUAL)

        result = self.engine.autonomous_parameter_tuning(
            parameters={"lr": 0.01},
            performance_metrics={"acc": 0.85},
            context={"mode": "test"},
        )

        self.assertFalse(result.autonomous_decision.approved)

        # Test autonomous level - should be approved
        self.engine.set_autonomy_level(AutonomyLevel.AUTONOMOUS)

        result = self.engine.autonomous_parameter_tuning(
            parameters={"lr": 0.01},
            performance_metrics={"acc": 0.85},
            context={"mode": "test"},
        )

        self.assertTrue(result.autonomous_decision.approved)

    def test_statistics(self):
        """Test autonomous evolution statistics."""
        stats = self.engine.get_statistics()

        self.assertIsInstance(stats, dict)
        self.assertIn("total_decisions", stats)
        self.assertIn("total_evolutions", stats)
        self.assertIn("autonomy_level", stats)


class TestAutonomousEvolutionIntegration(unittest.TestCase):
    """Integration tests for autonomous evolution with existing orchestrator."""

    def test_autonomous_with_existing_orchestrator(self):
        """Test autonomous evolution working with existing orchestrator."""
        from evolution_engine import EvolutionOrchestrator, get_evolution_orchestrator

        orchestrator = get_evolution_orchestrator()
        autonomous_engine = get_autonomous_evolution_engine()

        # Set up autonomous engine
        autonomous_engine.set_autonomy_level(AutonomyLevel.AUTONOMOUS)
        autonomous_engine.enable_autonomy_scope(AutonomyScope.PARAMETER_TUNING)

        # Perform autonomous parameter tuning
        result = autonomous_engine.autonomous_parameter_tuning(
            parameters={"threshold": 0.5},
            performance_metrics={"performance": 0.8},
            context={"strategy": "test"},
        )

        self.assertIsInstance(result, AutonomousEvolutionResult)
        self.assertGreater(result.fitness_improvement, 0.0)


def run_tests():
    """Run all evolution engine completion tests."""
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()

    suite.addTests(loader.loadTestsFromTestCase(TestAutonomousEvolutionEngine))
    suite.addTests(loader.loadTestsFromTestCase(TestAutonomousEvolutionIntegration))

    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)

    print("\n" + "="*70)
    print("EVOLUTION ENGINE COMPLETION TEST SUMMARY")
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
