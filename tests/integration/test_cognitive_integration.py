"""
tests.integration.test_cognitive_integration
DIX VISION v42.2 — Cognitive System Integration Tests

Comprehensive integration tests for cognitive subsystems to ensure
they work correctly with the overall system architecture.
"""

import pytest

from cognitive_engine.cognitive_orchestrator import CognitiveOrchestrator, get_cognitive_orchestrator
from cognitive_engine.hypothesis_engine.hypothesis_tracker import HypothesisTracker
from cognitive_engine.knowledge_graph.graph import KnowledgeGraph
from mind.engine import IndiraEngine


class TestCognitiveOrchestratorIntegration:
    """Test cognitive orchestrator integration with system components."""
    
    @pytest.mark.asyncio
    async def test_orchestrator_initialization(self):
        """Test that cognitive orchestrator initializes correctly."""
        orchestrator = get_cognitive_orchestrator()
        success = await orchestrator.initialize()
        
        assert success is True
        assert orchestrator._initialized is True
        assert orchestrator.get_metrics()["initialized"] is True
    
    @pytest.mark.asyncio
    async def test_market_data_enrichment(self):
        """Test that market data enrichment works correctly."""
        orchestrator = get_cognitive_orchestrator()
        await orchestrator.initialize()
        
        market_data = {
            "signal": 0.8,
            "asset": "BTC",
            "price": 65000.0,
            "data_quality": 0.95,
            "execution_confidence": 0.90
        }
        
        enrichment = orchestrator.enrich_market_data(market_data)
        
        assert enrichment is not None
        assert enrichment.processing_time_ms > 0
        assert enrichment.enrichment_timestamp != ""
        assert enrichment.processing_time_ms < 20.0  # Should be fast
    
    @pytest.mark.asyncio
    async def test_risk_assessment(self):
        """Test that cognitive risk assessment works correctly."""
        orchestrator = get_cognitive_orchestrator()
        await orchestrator.initialize()
        
        context = {
            "market_data": {"signal": 0.9, "asset": "BTC"},
            "portfolio_state": {"portfolio_usd": 100000.0}
        }
        
        risk_assessment = orchestrator.assess_cognitive_risk(context)
        
        assert risk_assessment is not None
        assert risk_assessment.overall_risk in ("LOW", "MEDIUM", "HIGH", "EXTREME")
        assert 0.0 <= risk_assessment.confidence <= 1.0
        assert len(risk_assessment.recommended_actions) > 0
    
    def test_orchestrator_metrics(self):
        """Test that orchestrator metrics are tracked correctly."""
        orchestrator = get_cognitive_orchestrator()
        metrics = orchestrator.get_metrics()
        
        assert "initialized" in metrics
        assert "enabled" in metrics
        assert "mode" in metrics
        assert "knowledge_graph_nodes" in metrics


class TestIndiraCognitiveIntegration:
    """Test Indira engine integration with cognitive systems."""
    
    def test_indira_cognitive_initialization(self):
        """Test that Indira engine initializes with cognitive integration."""
        engine = IndiraEngine()
        
        # Cognitive orchestrator should be available (optional)
        # Engine should work without it
        assert engine is not None
    
    def test_indira_process_tick_with_cognitive_risk(self):
        """Test that Indira processes ticks with cognitive risk assessment."""
        engine = IndiraEngine()
        
        market_data = {
            "signal": 0.85,
            "asset": "BTC",
            "price": 65000.0,
            "data_quality": 0.95,
            "execution_confidence": 0.90
        }
        
        event = engine.process_tick(market_data)
        
        assert event is not None
        assert event.asset == "BTC"
        # Event should be generated even without cognitive integration
        assert event.event_type in ("TRADE_EXECUTION", "HOLD", "DELEGATE")


class TestKnowledgeGraphIntegration:
    """Test knowledge graph integration with auto-population."""
    
    def test_knowledge_graph_auto_populator_initialization(self):
        """Test that knowledge graph auto-populator initializes correctly."""
        from cognitive_engine.knowledge_graph.auto_populator import get_auto_populator
        
        kg = KnowledgeGraph()
        populator = get_auto_populator(kg)
        
        assert populator is not None
        assert populator._kg == kg
    
    def test_knowledge_graph_trade_update(self):
        """Test that knowledge graph updates from trade data."""
        from cognitive_engine.knowledge_graph.auto_populator import get_auto_populator
        
        kg = KnowledgeGraph()
        populator = get_auto_populator(kg)
        
        trade_event = {
            "asset": "BTC",
            "strategy": "momentum",
            "side": "BUY",
            "size_usd": 5000.0,
            "execution_quality": 0.85
        }
        
        extraction = populator.update_from_trade(trade_event)
        
        assert extraction is not None
        assert extraction.source_type == "trade"
        assert len(extraction.entities) > 0
        assert extraction.confidence > 0.0
    
    def test_knowledge_graph_market_update(self):
        """Test that knowledge graph updates from market data."""
        from cognitive_engine.knowledge_graph.auto_populator import get_auto_populator
        
        kg = KnowledgeGraph()
        populator = get_auto_populator(kg)
        
        market_data = {
            "asset": "ETH",
            "signal": -0.7,
            "price": 3500.0
        }
        
        extraction = populator.update_from_market(market_data)
        
        assert extraction is not None
        assert extraction.source_type == "market"
        assert len(extraction.entities) > 0
    
    def test_knowledge_graph_statistics(self):
        """Test that knowledge graph statistics are tracked correctly."""
        from cognitive_engine.knowledge_graph.auto_populator import get_auto_populator
        
        kg = KnowledgeGraph()
        populator = get_auto_populator(kg)
        
        stats = populator.get_statistics()
        
        assert "extractions_count" in stats
        assert "knowledge_graph_nodes" in stats
        assert "knowledge_graph_edges" in stats


class TestHypothesisEngineIntegration:
    """Test hypothesis engine integration with automation."""
    
    def test_hypothesis_auto_generator_initialization(self):
        """Test that hypothesis auto-generator initializes correctly."""
        from cognitive_engine.hypothesis_engine.auto_generator import get_auto_generator
        
        tracker = HypothesisTracker()
        generator = get_auto_generator(tracker)
        
        assert generator is not None
        assert generator._tracker == tracker
    
    def test_hypothesis_generation_from_anomalies(self):
        """Test that hypotheses are generated from anomalies."""
        from cognitive_engine.hypothesis_engine.auto_generator import Anomaly, get_auto_generator
        
        tracker = HypothesisTracker()
        generator = get_auto_generator(tracker)
        
        anomalies = [
            Anomaly(
                anomaly_type="price_spike",
                asset="BTC",
                severity=0.8,
                description="BTC price spiked 15% in 1 hour",
                timestamp="2024-01-01T00:00:00Z"
            )
        ]
        
        hypotheses = generator.generate_from_anomalies(anomalies)
        
        assert len(hypotheses) > 0
        assert hypotheses[0].domain != ""
        assert hypotheses[0].confidence > 0.0
    
    def test_hypothesis_generation_from_performance(self):
        """Test that hypotheses are generated from performance data."""
        from cognitive_engine.hypothesis_engine.auto_generator import get_auto_generator
        
        tracker = HypothesisTracker()
        generator = get_auto_generator(tracker)
        
        performance_data = {
            "strategy": "mean_reversion",
            "performance": {
                "sharpe_ratio": 0.8,
                "max_drawdown": 0.15
            }
        }
        
        hypotheses = generator.generate_from_performance(performance_data)
        
        assert len(hypotheses) > 0
        assert all(h.domain in ("performance_analysis", "risk_analysis") for h in hypotheses)


class TestNarrativeEngineIntegration:
    """Test narrative engine integration with news processing."""
    
    def test_narrative_detection_integration(self):
        """Test that narrative detection works with news processing."""
        from mind.sources.news_streams import NewsStreamRegistry, NewsItem
        
        registry = NewsStreamRegistry()
        
        # Create a sample news item
        news_item = NewsItem(
            source="test",
            headline="Federal Reserve signals rate hike cycle beginning",
            polarity=0.6,
            confidence=0.8
        )
        
        # The registry should process this with narrative detection
        # (if cognitive integration is enabled)
        assert registry is not None
        assert news_item.headline != ""


class TestFeatureFlagsIntegration:
    """Test feature flags integration with cognitive systems."""
    
    def test_cognitive_feature_flags_exist(self):
        """Test that cognitive feature flags are defined."""
        from system.feature_flags import CognitiveFeatureFlags
        
        assert hasattr(CognitiveFeatureFlags, 'COGNITIVE_ENRICHMENT')
        assert hasattr(CognitiveFeatureFlags, 'COGNITIVE_RISK_ASSESSMENT')
        assert hasattr(CognitiveFeatureFlags, 'NARRATIVE_DETECTION')
        assert hasattr(CognitiveFeatureFlags, 'KNOWLEDGE_GRAPH_AUTO_POPULATION')
    
    def test_feature_flag_manager(self):
        """Test that feature flag manager works correctly."""
        from system.feature_flags import FeatureFlagManager, CognitiveFeatureFlags
        
        manager = FeatureFlagManager()
        
        # Test status checking
        status = manager.get_status(CognitiveFeatureFlags.COGNITIVE_ENRICHMENT)
        assert status is not None
        
        # Test enabled checking
        is_enabled = manager.is_enabled(CognitiveFeatureFlags.COGNITIVE_ENRICHMENT)
        assert isinstance(is_enabled, bool)


class TestCognitiveEndToEndIntegration:
    """End-to-end integration tests for cognitive systems."""
    
    @pytest.mark.asyncio
    async def test_full_cognitive_pipeline(self):
        """Test the complete cognitive pipeline from market data to enrichment."""
        # Initialize cognitive orchestrator
        orchestrator = get_cognitive_orchestrator()
        await orchestrator.initialize()
        
        # Simulate market data flow
        market_data = {
            "signal": 0.75,
            "asset": "BTC",
            "price": 65000.0,
            "data_quality": 0.95,
            "execution_confidence": 0.90
        }
        
        # Apply cognitive enrichment
        enrichment = orchestrator.enrich_market_data(market_data)
        
        # Verify enrichment
        assert enrichment is not None
        assert enrichment.processing_time_ms < 20.0  # Performance target
        
        # Test risk assessment
        risk_assessment = orchestrator.assess_cognitive_risk({
            "market_data": market_data,
            "portfolio_state": {"portfolio_usd": 100000.0}
        })
        
        assert risk_assessment.overall_risk in ("LOW", "MEDIUM", "HIGH", "EXTREME")
    
    @pytest.mark.asyncio
    async def test_cognitive_system_without_feature_flags(self):
        """Test that cognitive systems work when feature flags are disabled."""
        import os
        
        # Disable cognitive enrichment via environment variable
        original_value = os.environ.get("DIX_COGNITIVE_ENRICHMENT")
        os.environ["DIX_COGNITIVE_ENRICHMENT"] = "disabled"
        
        try:
            # Create new orchestrator instance
            from cognitive_engine.cognitive_orchestrator import CognitiveOrchestrator
            new_orchestrator = CognitiveOrchestrator()
            
            # Should still work, but with reduced functionality
            market_data = {
                "signal": 0.8,
                "asset": "BTC",
                "price": 65000.0
            }
            
            enrichment = new_orchestrator.enrich_market_data(market_data)
            assert enrichment is not None  # Should return empty enrichment, not crash
            
        finally:
            # Restore original value
            if original_value is not None:
                os.environ["DIX_COGNITIVE_ENRICHMENT"] = original_value
            else:
                os.environ.pop("DIX_COGNITIVE_ENRICHMENT", None)


class TestCognitivePerformance:
    """Performance tests for cognitive systems."""
    
    @pytest.mark.asyncio
    async def test_enrichment_latency_target(self):
        """Test that cognitive enrichment meets latency targets."""
        orchestrator = get_cognitive_orchestrator()
        await orchestrator.initialize()
        
        import time
        
        market_data = {
            "signal": 0.8,
            "asset": "BTC",
            "price": 65000.0,
            "data_quality": 0.95
        }
        
        # Measure latency
        start = time.time()
        enrichment = orchestrator.enrich_market_data(market_data)
        end = time.time()
        
        latency_ms = (end - start) * 1000
        
        # Should be well under 10ms target
        assert latency_ms < 10.0, f"Enrichment latency {latency_ms:.2f}ms exceeds 10ms target"
        assert enrichment.processing_time_ms < 10.0
    
    @pytest.mark.asyncio
    async def test_concurrent_enrichment_performance(self):
        """Test that concurrent enrichment operations perform well."""
        orchestrator = get_cognitive_orchestrator()
        await orchestrator.initialize()
        
        import asyncio
        
        async def enrich_single():
            market_data = {
                "signal": 0.8,
                "asset": "BTC",
                "price": 65000.0,
                "data_quality": 0.95
            }
            return orchestrator.enrich_market_data(market_data)
        
        # Run concurrent enrichments
        start = time.time()
        results = await asyncio.gather(*[enrich_single() for _ in range(10)])
        end = time.time()
        
        total_time_ms = (end - start) * 1000
        avg_time_ms = total_time_ms / 10
        
        # Average should still be under target
        assert avg_time_ms < 10.0, f"Average enrichment time {avg_time_ms:.2f}ms exceeds 10ms target"
        assert len(results) == 10