"""Tests for INDIRA Knowledge Integration."""

import os
import sys

# Add project root to path
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, project_root)

import threading
import time
import unittest


class TestINDIRAKnowledgeIntegration(unittest.TestCase):
    """Test INDIRA knowledge integration system."""

    def setUp(self):
        """Set up test fixtures."""
        from indira_cognitive.knowledge_integration import get_indira_knowledge_integration

        self.knowledge_integration = get_indira_knowledge_integration()

    def test_knowledge_integration_initialization(self):
        """Test knowledge integration initialization."""
        self.assertIsNotNone(self.knowledge_integration)
        stats = self.knowledge_integration.get_knowledge_statistics()
        self.assertIn("cached_signals", stats)
        self.assertIn("learning_history_entries", stats)

    def test_signal_creation(self):
        """Test signal creation and processing."""
        from indira_cognitive.knowledge_integration import Signal, SignalType

        signal = Signal(
            signal_id="test_signal_001",
            signal_type=SignalType.PRICE,
            symbol="BTC",
            value=50000.0,
            source="exchange_api",
            timestamp=time.time(),
            metadata={"exchange": "binance"},
        )

        self.assertEqual(signal.signal_id, "test_signal_001")
        self.assertEqual(signal.signal_type, SignalType.PRICE)
        self.assertEqual(signal.symbol, "BTC")
        self.assertEqual(signal.value, 50000.0)

    def test_process_signal_with_knowledge(self):
        """Test signal processing through knowledge layers."""
        from indira_cognitive.knowledge_integration import Signal, SignalType

        signal = Signal(
            signal_id="test_signal_002",
            signal_type=SignalType.VOLUME,
            symbol="ETH",
            value=1000000.0,
            source="order_book",
            timestamp=time.time(),
        )

        enhanced = self.knowledge_integration.process_signal_with_knowledge(signal)

        self.assertIsNotNone(enhanced)
        self.assertEqual(enhanced.signal.signal_id, "test_signal_002")
        self.assertIsNotNone(enhanced.knowledge_level)
        self.assertGreater(enhanced.confidence, 0.0)
        self.assertLessEqual(enhanced.confidence, 1.0)

    def test_signal_caching(self):
        """Test signal caching mechanism."""
        from indira_cognitive.knowledge_integration import Signal, SignalType

        signal = Signal(
            signal_id="test_signal_003",
            signal_type=SignalType.SENTIMENT,
            symbol="BTC",
            value=0.8,
            source="sentiment_analysis",
            timestamp=time.time(),
        )

        # Process signal
        enhanced = self.knowledge_integration.process_signal_with_knowledge(signal)

        # Retrieve from cache
        cached = self.knowledge_integration.get_cached_signal("test_signal_003")

        self.assertIsNotNone(cached)
        self.assertEqual(cached.signal.signal_id, "test_signal_003")

    def test_cache_miss(self):
        """Test cache miss behavior."""
        cached = self.knowledge_integration.get_cached_signal("nonexistent_signal")
        self.assertIsNone(cached)

    def test_query_market_knowledge(self):
        """Test market knowledge querying."""
        knowledge = self.knowledge_integration.query_market_knowledge(
            symbol="BTC", context={"query_type": "market_conditions"}
        )

        self.assertIsNotNone(knowledge)
        self.assertIsInstance(knowledge, dict)

    def test_apply_market_knowledge_to_strategy(self):
        """Test applying market knowledge to strategy."""
        strategy = {
            "symbol": "ETH",
            "type": "momentum",
            "risk_level": "moderate",
            "position_size": 100,
        }

        enhanced_strategy = self.knowledge_integration.apply_market_knowledge_to_strategy(strategy)

        self.assertIn("knowledge_applied", enhanced_strategy)
        self.assertIn("market_knowledge", enhanced_strategy)
        self.assertIn("adjustments", enhanced_strategy)

    def test_strategy_without_symbol(self):
        """Test strategy application when symbol is missing."""
        strategy = {"type": "momentum", "risk_level": "high"}

        enhanced_strategy = self.knowledge_integration.apply_market_knowledge_to_strategy(strategy)

        # Should handle gracefully without symbol
        self.assertIn("knowledge_applied", enhanced_strategy)
        # Knowledge not applied due to missing symbol
        self.assertFalse(enhanced_strategy.get("knowledge_applied", True))

    def test_learn_from_execution_results(self):
        """Test learning from execution results."""
        execution_results = [
            {
                "symbol": "BTC",
                "strategy": "momentum",
                "success": True,
                "execution_time": 0.5,
                "expected_execution_time": 1.0,
                "position_size_optimal": True,
                "market_conditions_favorable": True,
            },
            {
                "symbol": "ETH",
                "strategy": "mean_reversion",
                "success": False,
                "execution_time": 2.0,
                "expected_execution_time": 1.0,
                "position_size_over_risk": True,
                "adverse_market_movement": True,
            },
        ]

        self.knowledge_integration.learn_from_execution_results(execution_results)

        # Check that learning history was updated
        stats = self.knowledge_integration.get_knowledge_statistics()
        self.assertGreater(stats["learning_history_entries"], 0)

    def test_success_factor_identification(self):
        """Test identification of success factors."""
        success_result = {
            "success": True,
            "execution_time": 0.5,
            "expected_execution_time": 1.0,
            "position_size_optimal": True,
            "market_conditions_favorable": True,
        }

        factors = self.knowledge_integration._identify_success_factors(success_result)

        self.assertIn("optimal_timing", factors)
        self.assertIn("optimal_position_size", factors)
        self.assertIn("favorable_market_conditions", factors)

    def test_failure_factor_identification(self):
        """Test identification of failure factors."""
        failure_result = {
            "success": False,
            "execution_time": 2.0,
            "expected_execution_time": 1.0,
            "position_size_over_risk": True,
            "adverse_market_movement": True,
            "execution_error": True,
        }

        factors = self.knowledge_integration._identify_failure_factors(failure_result)

        self.assertIn("suboptimal_timing", factors)
        self.assertIn("excessive_position_size", factors)
        self.assertIn("adverse_market_movement", factors)
        self.assertIn("execution_infrastructure_issue", factors)

    def test_learning_history_limit(self):
        """Test that learning history is limited."""
        # Add many execution results
        for i in range(1500):
            execution_results = [{"symbol": f"TEST_{i}", "strategy": "test", "success": True}]
            self.knowledge_integration.learn_from_execution_results(execution_results)

        # History should be limited to 1000 entries
        stats = self.knowledge_integration.get_knowledge_statistics()
        self.assertLessEqual(stats["learning_history_entries"], 1000)

    def test_knowledge_statistics(self):
        """Test knowledge statistics."""
        stats = self.knowledge_integration.get_knowledge_statistics()

        self.assertIn("cached_signals", stats)
        self.assertIn("learning_history_entries", stats)
        self.assertIn("knowledge_validator_available", stats)
        self.assertIn("source_conflict_graph_available", stats)
        self.assertIn("edge_case_memory_available", stats)
        self.assertIn("drift_monitor_available", stats)
        self.assertIn("memory_index_available", stats)

    def test_thread_safety(self):
        """Test thread safety of knowledge integration."""

        def process_signal(index):
            from indira_cognitive.knowledge_integration import Signal, SignalType

            signal = Signal(
                signal_id=f"thread_test_{index}",
                signal_type=SignalType.PRICE,
                symbol="BTC",
                value=float(index),
                source="test",
                timestamp=time.time(),
            )
            return self.knowledge_integration.process_signal_with_knowledge(signal)

        threads = []
        for i in range(10):
            thread = threading.Thread(target=process_signal, args=(i,))
            threads.append(thread)
            thread.start()

        for thread in threads:
            thread.join()

        # Should have processed all signals
        stats = self.knowledge_integration.get_knowledge_statistics()
        self.assertGreaterEqual(stats["cached_signals"], 10)


class TestKnowledgeBasedIntelligence(unittest.TestCase):
    """Test knowledge-based intelligence system."""

    def setUp(self):
        """Set up test fixtures."""
        from indira_cognitive.knowledge_integration import get_knowledge_based_intelligence

        self.knowledge_intelligence = get_knowledge_based_intelligence()

    def test_knowledge_intelligence_initialization(self):
        """Test knowledge-based intelligence initialization."""
        self.assertIsNotNone(self.knowledge_intelligence)

    def test_generate_knowledge_based_insights(self):
        """Test generation of knowledge-based insights."""
        market_state = {
            "symbol": "BTC",
            "price": 50000.0,
            "volume": 1000000.0,
            "timestamp": time.time(),
        }

        insights = self.knowledge_intelligence.generate_knowledge_based_insights(market_state)

        self.assertIsNotNone(insights)
        self.assertIn("signal_insights", insights)
        self.assertIn("knowledge_insights", insights)
        self.assertIn("world_context", insights)
        self.assertIn("combined_intelligence", insights)

    def test_combined_intelligence(self):
        """Test combined intelligence calculation."""
        signal_insights = {"signal_quality": "high", "signal_confidence": 0.8}

        knowledge_insights = {"knowledge_level": "knowledge_based", "confidence": 0.9}

        world_context = {"market_regime": "bullish", "volatility": "moderate"}

        combined = self.knowledge_intelligence._combine_intelligence(
            signal_insights, knowledge_insights, world_context
        )

        self.assertIn("combined_confidence", combined)
        self.assertGreater(combined["combined_confidence"], 0.0)
        self.assertIn("timestamp", combined)

    def test_signal_component_weight(self):
        """Test signal component weight in combined intelligence."""
        insights = self.knowledge_intelligence._combine_intelligence(
            {"signal_confidence": 1.0}, {"confidence": 0.0}, {}
        )

        # Should give weight 0.3 to signal component
        expected = 1.0 * 0.3 + 0.0 * 0.5
        self.assertAlmostEqual(insights["combined_confidence"], expected, places=2)

    def test_knowledge_component_weight(self):
        """Test knowledge component weight in combined intelligence."""
        insights = self.knowledge_intelligence._combine_intelligence(
            {"signal_confidence": 0.0}, {"confidence": 1.0}, {}
        )

        # Should give weight 0.5 to knowledge component
        expected = 0.0 * 0.3 + 1.0 * 0.5
        self.assertAlmostEqual(insights["combined_confidence"], expected, places=2)


class TestKnowledgeIntegrationProduction(unittest.TestCase):
    """Test production-grade features of knowledge integration."""

    def setUp(self):
        """Set up test fixtures."""
        from indira_cognitive.knowledge_integration import get_indira_knowledge_integration

        self.knowledge_integration = get_indira_knowledge_integration()

    def test_singleton_pattern(self):
        """Test that knowledge integration follows singleton pattern."""
        from indira_cognitive.knowledge_integration import get_indira_knowledge_integration

        instance1 = get_indira_knowledge_integration()
        instance2 = get_indira_knowledge_integration()

        self.assertIs(instance1, instance2)

    def test_knowledge_based_intelligence_singleton(self):
        """Test that knowledge-based intelligence follows singleton pattern."""
        from indira_cognitive.knowledge_integration import get_knowledge_based_intelligence

        instance1 = get_knowledge_based_intelligence()
        instance2 = get_knowledge_based_intelligence()

        self.assertIs(instance1, instance2)

    def test_signal_enumeration(self):
        """Test signal type enumeration."""
        from indira_cognitive.knowledge_integration import SignalType

        self.assertEqual(SignalType.PRICE, "PRICE")
        self.assertEqual(SignalType.VOLUME, "VOLUME")
        self.assertEqual(SignalType.ORDER_FLOW, "ORDER_FLOW")
        self.assertEqual(SignalType.SENTIMENT, "SENTIMENT")
        self.assertEqual(SignalType.NEWS, "NEWS")
        self.assertEqual(SignalType.TECHNICAL, "TECHNICAL")

    def test_knowledge_level_enumeration(self):
        """Test knowledge level enumeration."""
        from indira_cognitive.knowledge_integration import KnowledgeLevel

        self.assertEqual(KnowledgeLevel.RAW, "RAW")
        self.assertEqual(KnowledgeLevel.VALIDATED, "VALIDATED")
        self.assertEqual(KnowledgeLevel.CONFLICTING, "CONFLICTING")
        self.assertEqual(KnowledgeLevel.EDGE_CASE, "EDGE_CASE")
        self.assertEqual(KnowledgeLevel.DRIFTING, "DRIFTING")

    def test_production_error_handling(self):
        """Test production-grade error handling."""
        # Test with invalid market state
        try:
            insights = self.knowledge_integration.generate_knowledge_based_insights({})
        except AttributeError:
            # The method doesn't exist on INDIRAKnowledgeIntegration, which is expected
            # Test error handling on a method that does exist
            from indira_cognitive.knowledge_integration import KnowledgeBasedIntelligence

            kb_intelligence = KnowledgeBasedIntelligence()
            insights = kb_intelligence.generate_knowledge_based_insights({})

        # Should handle gracefully
        self.assertIsNotNone(insights)

    def test_empty_execution_results_learning(self):
        """Test learning with empty execution results."""
        # Should handle empty results gracefully
        self.knowledge_integration.learn_from_execution_results([])

        stats = self.knowledge_integration.get_knowledge_statistics()
        # Should not crash
        self.assertIsNotNone(stats)


if __name__ == "__main__":
    unittest.main(verbosity=2)
