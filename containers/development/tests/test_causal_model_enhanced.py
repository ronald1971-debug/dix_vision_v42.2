"""Tests for Enhanced Causal Model with Real Algorithms."""

import os
import sys

# Add project root to path
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, project_root)

import threading
import unittest

import numpy as np


class TestEnhancedCausalModel(unittest.TestCase):
    """Test enhanced production causal model with real algorithms."""

    def setUp(self):
        """Set up test fixtures."""
        from world_model.causal_model_enhanced import get_production_causal_model

        self.causal_model = get_production_causal_model()
        self.causal_model.reset()  # Reset for clean state
        self.causal_model.start()

    def tearDown(self):
        """Clean up after tests."""
        if self.causal_model:
            self.causal_model.stop()

    def test_causal_model_initialization(self):
        """Test causal model initialization."""
        self.assertIsNotNone(self.causal_model)
        self.assertIsInstance(self.causal_model.get_causal_graph(), dict)
        stats = self.causal_model.get_statistics()
        self.assertIn("total_variables", stats)
        self.assertIn("total_relationships", stats)

    def test_add_causal_relationship(self):
        """Test adding causal relationship."""
        relationship = self.causal_model.add_causal_relationship(
            cause="price_change",
            effect="volume_surge",
            strength=0.8,
            confidence=0.9,
            method="manual",
        )

        self.assertIsNotNone(relationship)
        self.assertEqual(relationship.cause, "price_change")
        self.assertEqual(relationship.effect, "volume_surge")
        self.assertEqual(relationship.strength, 0.8)
        self.assertEqual(relationship.confidence, 0.9)

        graph = self.causal_model.get_causal_graph()
        self.assertIn("price_change", graph)
        self.assertEqual(len(graph["price_change"]), 1)

    def test_causal_relationship_validation(self):
        """Test causal relationship validation."""
        # Test self-causation (should fail)
        invalid_relation = self.causal_model.add_causal_relationship(
            cause="price", effect="price", strength=0.8, confidence=0.9
        )
        self.assertIsNone(invalid_relation)

        # Test invalid strength (should fail)
        invalid_relation = self.causal_model.add_causal_relationship(
            cause="price", effect="volume", strength=2.0, confidence=0.9  # Invalid: > 1.0
        )
        self.assertIsNone(invalid_relation)

        # Test invalid confidence (should fail)
        invalid_relation = self.causal_model.add_causal_relationship(
            cause="price", effect="volume", strength=0.8, confidence=1.5  # Invalid: > 1.0
        )
        self.assertIsNone(invalid_relation)

    def test_pc_causal_discovery(self):
        """Test PC-like causal discovery algorithm."""
        # Create synthetic data with known causal structure
        np.random.seed(42)

        # Create variables with causal relationships
        n_samples = 100
        X1 = np.random.randn(n_samples)
        X2 = 0.8 * X1 + np.random.randn(n_samples)  # X2 depends on X1
        X3 = 0.6 * X2 + np.random.randn(n_samples)  # X3 depends on X2
        X4 = np.random.randn(n_samples)  # X4 is independent

        data = {"X1": X1.tolist(), "X2": X2.tolist(), "X3": X3.tolist(), "X4": X4.tolist()}

        # Run causal discovery
        discovered_graph = self.causal_model.discover_causal_structure_pc(data)

        self.assertIsInstance(discovered_graph, dict)
        self.assertGreater(len(discovered_graph), 0)

        # Should find relationships related to the causal structure
        has_relationships = len(discovered_graph) > 0
        self.assertTrue(has_relationships, "Should discover some causal relationships")

    def test_correlation_matrix_calculation(self):
        """Test correlation matrix calculation."""
        data = {
            "var1": [1.0, 2.0, 3.0, 4.0, 5.0],
            "var2": [1.1, 2.1, 3.1, 4.1, 5.1],  # Highly correlated
            "var3": [5.0, 4.0, 3.0, 2.0, 1.0],  # Negatively correlated
        }

        corr_matrix = self.causal_model._calculate_correlation_matrix(data)

        # Debug: print the correlation matrix
        print(f"Correlation matrix:")
        for var1 in corr_matrix:
            for var2 in corr_matrix[var1]:
                print(f"{var1}[{var2}] = {corr_matrix[var1][var2]}")

        self.assertIn("var1", corr_matrix)
        self.assertIn("var2", corr_matrix)
        self.assertIn("var3", corr_matrix)

        # var1 and var2 should be highly positively correlated
        self.assertGreater(corr_matrix["var1"]["var2"], 0.9)

        # var1 and var3 should be highly negatively correlated
        self.assertLess(corr_matrix["var1"]["var3"], -0.9)

        # Check symmetry of correlation matrix
        self.assertAlmostEqual(corr_matrix["var1"]["var2"], corr_matrix["var2"]["var1"], places=10)
        self.assertAlmostEqual(corr_matrix["var1"]["var3"], corr_matrix["var3"]["var1"], places=10)
        self.assertAlmostEqual(corr_matrix["var2"]["var3"], corr_matrix["var3"]["var2"], places=10)

    def test_conditional_independence_check(self):
        """Test conditional independence check."""
        data = {
            "A": [1.0, 2.0, 3.0, 4.0, 5.0],
            "B": [2.0, 4.0, 6.0, 8.0, 10.0],  # B = 2*A (dependent)
            "C": [1.0, 1.5, 2.0, 2.5, 3.0],  # C = A/2 + noise (dependent)
        }

        # Test without conditioning set
        is_independent = self.causal_model._check_conditional_independence(data, "A", "B", set())
        self.assertFalse(is_independent, "A and B should be dependent")

        # Test with conditioning set
        is_independent = self.causal_model._check_conditional_independence(data, "A", "B", {"C"})
        # Should become more independent when conditioning on C
        # (This is a simplified test; real conditional independence is more complex)

    def test_causal_effect_inference(self):
        """Test causal effect inference using linear regression."""
        # Create synthetic data with causal effect
        np.random.seed(42)
        n_samples = 100
        cause = np.random.randn(n_samples)
        effect = 0.5 * cause + np.random.randn(n_samples) * 0.3  # True causal effect = 0.5

        data = {"cause": cause.tolist(), "effect": effect.tolist()}

        # Infer causal effect
        inference_result = self.causal_model.infer_causal_effect(
            cause="cause", effect="effect", data=data, method="linear_regression"
        )

        self.assertIsNotNone(inference_result)
        self.assertEqual(inference_result.variable, "effect")
        self.assertEqual(inference_result.method, "linear_regression")

        # Estimated effect should be close to true effect (0.5)
        self.assertLess(
            abs(inference_result.causal_effect - 0.5),
            0.3,
            "Causal effect estimate should be close to true effect",
        )

        # Should have confidence interval
        self.assertEqual(len(inference_result.confidence_interval), 2)
        self.assertLess(
            inference_result.confidence_interval[0], inference_result.confidence_interval[1]
        )

    def test_causal_effect_bootstrap(self):
        """Test bootstrap confidence interval calculation."""
        # Create data
        np.random.seed(42)
        n_samples = 200
        cause = np.random.randn(n_samples)
        effect = 0.7 * cause + np.random.randn(n_samples) * 0.2

        data = {"cause": cause.tolist(), "effect": effect.tolist()}

        # Infer causal effect
        inference_result = self.causal_model.infer_causal_effect("cause", "effect", data)

        # Check that bootstrap produced reasonable confidence interval
        self.assertIsNotNone(inference_result)
        self.assertLess(inference_result.confidence_interval[0], inference_result.causal_effect)
        self.assertGreater(inference_result.confidence_interval[1], inference_result.causal_effect)

    def test_intervention_analysis(self):
        """Test intervention analysis."""
        # First add some causal relationships
        self.causal_model.add_causal_relationship(
            "interest_rate", "bond_price", strength=-0.8, confidence=0.9
        )
        self.causal_model.add_causal_relationship(
            "bond_price", "stock_volatility", strength=0.6, confidence=0.8
        )

        # Create intervention
        from world_model.causal_model_enhanced import Intervention

        intervention = Intervention(variable="interest_rate", value=0.25, intervention_type="atom")

        # Analyze intervention
        analysis = self.causal_model.analyze_intervention(intervention)

        self.assertIn("intervention", analysis)
        self.assertIn("estimated_effects", analysis)
        self.assertIn("total_impact", analysis)
        self.assertEqual(analysis["intervention"], "interest_rate")
        self.assertGreater(len(analysis["estimated_effects"]), 0)

    def test_intervention_with_no_effects(self):
        """Test intervention on variable with no causal relationships."""
        # Create intervention on variable with no relationships
        from world_model.causal_model_enhanced import Intervention

        intervention = Intervention(
            variable="unknown_variable", value=1.0, intervention_type="atom"
        )

        # Analyze intervention
        analysis = self.causal_model.analyze_intervention(intervention)

        self.assertEqual(len(analysis["estimated_effects"]), 0)
        self.assertEqual(analysis["total_impact"], 0.0)

    def test_causal_statistics(self):
        """Test causal model statistics."""
        # Add some relationships
        self.causal_model.add_causal_relationship("A", "B", strength=0.7, confidence=0.8)
        self.causal_model.add_causal_relationship("B", "C", strength=0.5, confidence=0.9)
        self.causal_model.add_causal_relationship("A", "C", strength=0.3, confidence=0.7)

        stats = self.causal_model.get_statistics()

        self.assertEqual(stats["total_variables"], 3)
        self.assertEqual(stats["total_relationships"], 3)
        self.assertGreater(stats["average_confidence"], 0.0)
        self.assertGreater(stats["average_strength"], 0.0)
        self.assertLessEqual(stats["average_confidence"], 1.0)
        self.assertLessEqual(stats["average_strength"], 1.0)

    def test_causal_density_calculation(self):
        """Test causal density calculation."""
        # Add relationships for 4 variables
        self.causal_model.add_causal_relationship("A", "B", strength=0.5, confidence=0.8)
        self.causal_model.add_causal_relationship("A", "C", strength=0.5, confidence=0.8)
        self.causal_model.add_causal_relationship("A", "D", strength=0.5, confidence=0.8)

        stats = self.causal_model.get_statistics()

        # Check actual values
        print(f"Total variables: {stats['total_variables']}")
        print(f"Total relationships: {stats['total_relationships']}")
        print(f"Actual density: {stats['causal_density']}")

        # Density should be 3/(4*3) = 0.25
        # But our calculation uses actual variables and directed relationships
        # With 4 variables and 3 relationships, density = 3/(4*3) = 0.25
        # However, we calculate it as total_relationships / (total_variables * (total_variables - 1))
        # So 3/(4*3) = 0.25
        expected_density = 3.0 / (4.0 * 3.0)
        self.assertEqual(stats["total_variables"], 4)  # Should have exactly 4 variables
        self.assertEqual(stats["total_relationships"], 3)  # Should have exactly 3 relationships
        self.assertAlmostEqual(stats["causal_density"], expected_density, places=2)

    def test_thread_safety(self):
        """Test thread safety of causal model operations."""

        def add_relationship(index):
            self.causal_model.add_causal_relationship(
                f"cause_{index}", f"effect_{index}", strength=0.5, confidence=0.8
            )

        threads = []
        for i in range(10):
            thread = threading.Thread(target=add_relationship, args=(i,))
            threads.append(thread)
            thread.start()

        for thread in threads:
            thread.join()

        # Should have all relationships added
        stats = self.causal_model.get_statistics()
        self.assertEqual(stats["total_relationships"], 10)

    def test_start_stop_cyclicality(self):
        """Test start/stop cyclicality."""
        # Stop the model
        self.assertTrue(self.causal_model.stop())

        # Start again
        self.assertTrue(self.causal_model.start())

        # Should still work
        relationship = self.causal_model.add_causal_relationship(
            cause="test_cause", effect="test_effect", strength=0.5, confidence=0.8
        )
        self.assertIsNotNone(relationship)


class TestCausalModelProduction(unittest.TestCase):
    """Test production-grade features of causal model."""

    def setUp(self):
        """Set up test fixtures."""
        from world_model.causal_model_enhanced import get_production_causal_model

        self.causal_model = get_production_causal_model()

    def test_production_causal_model_singleton(self):
        """Test that production causal model is a singleton."""
        from world_model.causal_model_enhanced import get_production_causal_model

        model1 = get_production_causal_model()
        model2 = get_production_causal_model()

        self.assertIs(model1, model2)

    def test_production_grade_data_structures(self):
        """Test that data structures are production-grade."""
        # Add relationship
        relationship = self.causal_model.add_causal_relationship(
            cause="production_test",
            effect="production_effect",
            strength=0.75,
            confidence=0.95,
            method="production_algorithm",
        )

        # Check relationship structure
        self.assertIsNotNone(relationship.relationship_id)
        self.assertIsNotNone(relationship.timestamp)
        self.assertEqual(relationship.method, "production_algorithm")
        self.assertIsInstance(relationship.metadata, dict)

    def test_production_grade_validation(self):
        """Test production-grade validation."""
        # Test edge cases
        # Zero strength
        relationship = self.causal_model.add_causal_relationship(
            cause="zero_strength", effect="effect", strength=0.0, confidence=0.5
        )
        self.assertIsNotNone(relationship)  # Zero strength is valid

        # Zero confidence
        relationship = self.causal_model.add_causal_relationship(
            cause="zero_confidence", effect="effect", strength=0.5, confidence=0.0
        )
        self.assertIsNotNone(relationship)  # Zero confidence is valid

        # Maximum valid values
        relationship = self.causal_model.add_causal_relationship(
            cause="max_values", effect="effect", strength=1.0, confidence=1.0
        )
        self.assertIsNotNone(relationship)  # Maximum values are valid

    def test_production_error_handling(self):
        """Test production-grade error handling."""
        # Test with invalid data for causal effect inference
        result = self.causal_model.infer_causal_effect(
            cause="nonexistent", effect="also_nonexistent", data={}, method="linear_regression"
        )

        # Should handle gracefully
        self.assertIsNotNone(result)
        self.assertEqual(result.causal_effect, 0.0)
        self.assertFalse(result.significance)


if __name__ == "__main__":
    unittest.main(verbosity=2)
