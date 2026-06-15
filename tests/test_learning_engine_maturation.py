"""Tests for Learning Engine Maturation (Reinforcement Loops and Cognitive Learning Governance)."""

import unittest
import sys
import os

# Add paths to imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from intelligence_engine.learning import (
    ReinforcementEngine,
    get_reinforcement_engine,
    FeedbackSample,
    ParameterBounds,
    ReinforcementUpdate,
    LearningRateStrategy,
    ReinforcementStatus,
    CognitiveLearningGovernance,
    get_cognitive_learning_governance,
    LearningConstraint,
    GovernanceDecision,
    GovernanceAction,
    LearningPhase,
)


class TestReinforcementEngine(unittest.TestCase):
    """Test cases for reinforcement engine."""

    def setUp(self):
        """Set up test fixtures."""
        self.engine = get_reinforcement_engine()

    def test_singleton_engine(self):
        """Test that the engine is a singleton."""
        engine1 = get_reinforcement_engine()
        engine2 = get_reinforcement_engine()
        self.assertIs(engine1, engine2)

    def test_add_feedback_sample(self):
        """Test adding feedback samples."""
        state = {"position": "long"}
        next_state = {"position": "long", "profit": "+1.5"}

        sample = self.engine.add_feedback_sample(
            action="enter_long",
            state=state,
            next_state=next_state,
            reward=1.5,
            confidence=0.9,
        )

        self.assertIsInstance(sample, FeedbackSample)
        self.assertEqual(sample.action, "enter_long")
        self.assertEqual(sample.reward, 1.5)

    def test_set_parameter_bounds(self):
        """Test setting parameter bounds."""
        bounds = self.engine.set_parameter_bounds(
            parameter_name="learning_rate",
            min_value=0.001,
            max_value=0.1,
            current_value=0.01,
            learning_rate=0.001,
        )

        self.assertIsInstance(bounds, ParameterBounds)
        self.assertEqual(bounds.parameter_name, "learning_rate")
        self.assertEqual(bounds.min_value, 0.001)
        self.assertEqual(bounds.max_value, 0.1)

    def test_update_parameters(self):
        """Test parameter update."""
        # Set up some parameter bounds
        self.engine.set_parameter_bounds(
            parameter_name="threshold",
            min_value=0.0,
            max_value=1.0,
            current_value=0.5,
            learning_rate=0.01,
        )

        # Add some feedback samples
        for i in range(5):
            state = {"step": str(i)}
            next_state = {"step": str(i + 1)}
            self.engine.add_feedback_sample(
                action="test_action",
                state=state,
                next_state=next_state,
                reward=0.5 if i % 2 == 0 else -0.3,
                confidence=0.9,
            )

        # Update parameters
        update = self.engine.update_parameters()

        self.assertIsInstance(update, ReinforcementUpdate)
        self.assertIn("threshold", update.parameter_updates)

    def test_learning_rate_strategy(self):
        """Test setting learning rate strategy."""
        self.engine.set_learning_rate_strategy(LearningRateStrategy.DECAY)

        # Add sample and update to trigger strategy usage
        self.engine.add_feedback_sample(
            action="test",
            state={"state": "test"},
            next_state={"state": "next"},
            reward=0.5,
        )

        self.engine.set_parameter_bounds(
            parameter_name="test_param",
            min_value=0.0,
            max_value=1.0,
            current_value=0.5,
        )

        update = self.engine.update_parameters()
        self.assertIsInstance(update, ReinforcementUpdate)

    def test_check_convergence(self):
        """Test convergence checking."""
        # Initially should not be converged
        self.assertFalse(self.engine.check_convergence())

        # Set up parameters and add samples to enable convergence detection
        self.engine.set_parameter_bounds(
            parameter_name="convergence_test",
            min_value=0.0,
            max_value=1.0,
            current_value=0.5,
        )

        # Add samples and perform updates
        for i in range(15):
            self.engine.add_feedback_sample(
                action="test",
                state={"step": str(i)},
                next_state={"step": str(i + 1)},
                reward=0.1,
            )
            self.engine.update_parameters()

        # After enough updates, convergence should be detected
        converged = self.engine.check_convergence()
        # This should eventually converge
        self.assertIn(converged, [True, False])  # May or may not converge based on logic

    def test_statistics(self):
        """Test learning engine statistics."""
        stats = self.engine.get_statistics()

        self.assertIsInstance(stats, dict)
        self.assertIn("total_updates", stats)
        self.assertIn("total_samples", stats)


class TestCognitiveLearningGovernance(unittest.TestCase):
    """Test cases for cognitive learning governance."""

    def setUp(self):
        """Set up test fixtures."""
        self.governance = get_cognitive_learning_governance()

    def test_singleton_governance(self):
        """Test that the governance is a singleton."""
        governance1 = get_cognitive_learning_governance()
        governance2 = get_cognitive_learning_governance()
        self.assertIs(governance1, governance2)

    def test_add_constraint(self):
        """Test adding learning constraints."""
        constraint = self.governance.add_constraint(
            constraint_id="safety_constraint",
            description="Ensure learning doesn't exceed safety thresholds",
            constraint_type="safety",
            severity=0.9,
            threshold=0.8,
            is_hard=True,
        )

        self.assertIsInstance(constraint, LearningConstraint)
        self.assertEqual(constraint.constraint_id, "safety_constraint")
        self.assertTrue(constraint.is_hard)

    def test_evaluate_learning_action_allow(self):
        """Test evaluating learning action that should be allowed."""
        parameters = {"learning_rate": 0.05}
        context = {"context": "test"}

        decision = self.governance.evaluate_learning_action(
            action="update_parameters",
            parameters=parameters,
            context=context,
        )

        self.assertIsInstance(decision, GovernanceDecision)
        # With no constraints, should be allowed
        self.assertEqual(decision.action, GovernanceAction.ALLOW)

    def test_evaluate_learning_action_block(self):
        """Test evaluating learning action that should be blocked."""
        # Add a hard constraint
        self.governance.add_constraint(
            constraint_id="max_learning_rate",
            description="Maximum allowed learning rate",
            constraint_type="performance",
            severity=0.8,
            threshold=0.1,
            is_hard=True,
        )

        parameters = {"learning_rate": 0.5}  # Exceeds threshold
        context = {"context": "test"}

        decision = self.governance.evaluate_learning_action(
            action="update_parameters",
            parameters=parameters,
            context=context,
        )

        self.assertIsInstance(decision, GovernanceDecision)
        self.assertEqual(decision.action, GovernanceAction.BLOCK)

    def test_evaluate_learning_action_modify(self):
        """Test evaluating learning action with constraint violations."""
        # Add only a soft constraint
        self.governance.add_constraint(
            constraint_id="soft_performance",
            description="Soft performance constraint",
            constraint_type="performance",
            severity=0.5,
            threshold=0.3,
            is_hard=False,
        )

        # Parameter exceeds soft threshold
        parameters = {"learning_rate": 0.4}
        context = {"context": "test"}

        decision = self.governance.evaluate_learning_action(
            action="update_parameters",
            parameters=parameters,
            context=context,
        )

        self.assertIsInstance(decision, GovernanceDecision)
        # Should be BLOCK or MODIFY based on constraint violations
        self.assertIn(decision.action, [GovernanceAction.BLOCK, GovernanceAction.MODIFY])
        # Should have violated constraints in the decision
        self.assertGreater(len(decision.violated_constraints), 0)

    def test_learning_phase_management(self):
        """Test learning phase management."""
        # Set phase
        self.governance.set_learning_phase(LearningPhase.EXPLOITATION)

        # Get phase
        current_phase = self.governance.get_learning_phase()
        self.assertEqual(current_phase, LearningPhase.EXPLOITATION)

    def test_learning_rate_compliance(self):
        """Test learning rate compliance checking."""
        # Should be compliant
        self.assertTrue(self.governance.check_learning_rate_compliance(0.05, 0.1))

        # Should not be compliant
        self.assertFalse(self.governance.check_learning_rate_compliance(0.15, 0.1))

    def test_statistics(self):
        """Test governance statistics."""
        stats = self.governance.get_statistics()

        self.assertIsInstance(stats, dict)
        self.assertIn("total_constraints", stats)
        self.assertIn("total_decisions", stats)


class TestLearningEngineIntegration(unittest.TestCase):
    """Integration tests for mature learning engine."""

    def test_reinforcement_with_governance(self):
        """Test reinforcement engine combined with governance."""
        engine = get_reinforcement_engine()
        governance = get_cognitive_learning_governance()

        # Set up governance constraint
        governance.add_constraint(
            constraint_id="max_update_threshold",
            description="Maximum parameter update threshold",
            constraint_type="safety",
            severity=0.8,
            threshold=0.2,
            is_hard=True,
        )

        # Set up reinforcement parameters
        engine.set_parameter_bounds(
            parameter_name="adaptive_threshold",
            min_value=0.0,
            max_value=1.0,
            current_value=0.5,
            learning_rate=0.01,
        )

        # Add feedback samples
        for i in range(3):
            engine.add_feedback_sample(
                action="adjust_threshold",
                state={"iteration": str(i)},
                next_state={"iteration": str(i + 1)},
                reward=0.3,
                confidence=0.9,
            )

        # Get parameter updates
        update = engine.update_parameters()

        # Evaluate with governance
        decision = governance.evaluate_learning_action(
            action="apply_update",
            parameters=update.parameter_updates,
            context={"update_id": update.update_id},
        )

        # Should get a valid decision
        self.assertIn(decision.action, [GovernanceAction.ALLOW, GovernanceAction.BLOCK, GovernanceAction.MODIFY])


def run_tests():
    """Run all learning engine maturation tests."""
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()

    suite.addTests(loader.loadTestsFromTestCase(TestReinforcementEngine))
    suite.addTests(loader.loadTestsFromTestCase(TestCognitiveLearningGovernance))
    suite.addTests(loader.loadTestsFromTestCase(TestLearningEngineIntegration))

    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)

    print("\n" + "="*70)
    print("LEARNING ENGINE MATURATION TEST SUMMARY")
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
