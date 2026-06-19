"""
cognitive_engine.cognitive_orchestrator
DIX VISION v42.2 — Central Cognitive Orchestrator

Integration point for all cognitive subsystems. Provides unified interface
for cognitive enrichment and coordinates between different cognitive modules.
"""

from __future__ import annotations

import asyncio
import logging
from dataclasses import dataclass
from typing import Any

from cognitive_engine.attention_engine.attention_manager import AttentionManager
from cognitive_engine.cognitive_simulator.engine import CognitiveSimulator
from cognitive_engine.curiosity_engine.curiosity_scorer import CuriosityScorer
from cognitive_engine.hypothesis_engine.hypothesis_tracker import HypothesisTracker
from cognitive_engine.knowledge_graph.graph import KnowledgeGraph
from cognitive_engine.narrative_engine.engine import NarrativeEngine
from system.time_source import now

logger = logging.getLogger(__name__)


@dataclass
class CognitiveEnrichment:
    """Result of cognitive enrichment process."""

    narratives: list[Any] = None
    knowledge_context: dict[str, Any] = None
    risk_assessment: dict[str, Any] = None
    hypothesis_insights: list[Any] = None
    curiosity_score: float = 0.0
    processing_time_ms: float = 0.0
    enrichment_timestamp: str = ""

    def __post_init__(self):
        if self.narratives is None:
            self.narratives = []
        if self.knowledge_context is None:
            self.knowledge_context = {}
        if self.risk_assessment is None:
            self.risk_assessment = {}
        if self.hypothesis_insights is None:
            self.hypothesis_insights = []
        if not self.enrichment_timestamp:
            self.enrichment_timestamp = now().utc_time.isoformat()


@dataclass
class RiskAssessment:
    """Risk assessment from cognitive simulation."""

    overall_risk: str  # LOW | MEDIUM | HIGH | EXTREME
    confidence: float
    scenarios_analyzed: int
    high_risk_scenarios: list[str]
    recommended_actions: list[str]
    exposure_multiplier: float = 1.0

    def should_reduce_exposure(self) -> bool:
        return self.overall_risk in ("HIGH", "EXTREME")


class CognitiveOrchestrator:
    """Central coordinator for all cognitive subsystems.

    Provides unified interface for cognitive enrichment and coordinates
    between different cognitive modules while maintaining performance
    and safety guarantees.
    """

    def __init__(self) -> None:
        self._simulator = CognitiveSimulator()
        self._hypothesis_tracker = HypothesisTracker()
        self._knowledge_graph = KnowledgeGraph()
        self._narrative_engine = NarrativeEngine()
        self._curiosity_scorer = CuriosityScorer()
        self._attention_manager = AttentionManager()
        
        self._initialized = False
        self._enabled = True
        self._mode = "observation"  # observation | shadow | active
        
        # Performance tracking
        self._enrichment_count = 0
        self._total_enrichment_time_ms = 0.0
        
    async def initialize(self) -> bool:
        """Initialize all cognitive subsystems."""
        try:
            logger.info("[COGNITIVE_ORCHESTRATOR] Initializing cognitive subsystems...")
            
            # Initialize knowledge graph with seed data
            await self._initialize_knowledge_graph()
            
            # Register common market narratives
            await self._register_common_narratives()
            
            self._initialized = True
            logger.info("[COGNITIVE_ORCHESTRATOR] All cognitive subsystems initialized")
            return True
            
        except Exception as e:
            logger.error(f"[COGNITIVE_ORCHESTRATOR] Initialization failed: {e}")
            return False
    
    async def _initialize_knowledge_graph(self) -> None:
        """Initialize knowledge graph with seed data."""
        # Add common market conditions as nodes
        conditions = [
            ("high_volatility", "MARKET_CONDITION", {"volatility_level": "high"}),
            ("low_liquidity", "MARKET_CONDITION", {"liquidity_level": "low"}),
            ("trending_up", "MARKET_CONDITION", {"trend": "upward"}),
            ("trending_down", "MARKET_CONDITION", {"trend": "downward"}),
        ]
        
        for name, node_type, props in conditions:
            self._knowledge_graph.add_node(
                node_type=node_type,
                name=name,
                **props
            )
        
        logger.info(f"[COGNITIVE_ORCHESTRATOR] Knowledge graph seeded with {len(conditions)} conditions")
    
    async def _register_common_narratives(self) -> None:
        """Register common market narratives."""
        narratives = [
            ("rate_hike_cycle", "Central bank raising interest rates", ("BTC", "ETH", "SPY")),
            ("crypto_adoption", "Institutional crypto adoption increasing", ("BTC", "ETH", "SOL")),
            ("regulatory_crackdown", "Increased regulatory scrutiny", ("CRYPTO",)),
            ("tech_bull_market", "Technology sector bull market", ("SPY", "QQQ")),
        ]
        
        for name, description, assets in narratives:
            self._narrative_engine.register(name, description, assets)
        
        logger.info(f"[COGNITIVE_ORCHESTRATOR] Registered {len(narratives)} common narratives")
    
    def enrich_market_data(self, market_data: dict[str, Any]) -> CognitiveEnrichment:
        """Enrich market data with cognitive insights.

        Synchronous version for compatibility with existing code.
        Cognitive operations should be fast (<10ms target).
        """
        if not self._initialized or not self._enabled:
            return CognitiveEnrichment()
        
        start_time = now().monotonic_ns()
        
        try:
            enrichment = CognitiveEnrichment()
            
            # Narrative context
            asset = market_data.get("asset", "")
            if asset:
                enrichment.narratives = self._narrative_engine.narratives_for_asset(asset)
            
            # Knowledge context
            enrichment.knowledge_context = self._query_knowledge_context(market_data)
            
            # Risk assessment (simplified for synchronous call)
            enrichment.risk_assessment = self._quick_risk_assessment(market_data)
            
            # Processing time tracking
            processing_time_ms = (now().monotonic_ns() - start_time) / 1_000_000
            enrichment.processing_time_ms = processing_time_ms
            
            # Update metrics
            self._enrichment_count += 1
            self._total_enrichment_time_ms += processing_time_ms
            
            # Alert if latency exceeds target
            if processing_time_ms > 10.0:
                logger.warning(
                    f"[COGNITIVE_ORCHESTRATOR] Enrichment latency {processing_time_ms:.2f}ms exceeds 10ms target"
                )
            
            return enrichment
            
        except Exception as e:
            logger.error(f"[COGNITIVE_ORCHESTRATOR] Enrichment failed: {e}")
            return CognitiveEnrichment()
    
    def _query_knowledge_context(self, market_data: dict[str, Any]) -> dict[str, Any]:
        """Query knowledge graph for relevant context."""
        context = {}
        
        try:
            # Simple context extraction based on market data
            signal = market_data.get("signal", 0.0)
            
            if signal > 0.7:
                context["regime"] = "bullish"
                context["related_conditions"] = ["trending_up"]
            elif signal < -0.7:
                context["regime"] = "bearish"
                context["related_conditions"] = ["trending_down"]
            else:
                context["regime"] = "neutral"
            
        except Exception as e:
            logger.error(f"[COGNITIVE_ORCHESTRATOR] Knowledge query failed: {e}")
        
        return context
    
    def _quick_risk_assessment(self, market_data: dict[str, Any]) -> dict[str, Any]:
        """Quick risk assessment without full simulation."""
        risk = {
            "level": "LOW",
            "confidence": 0.7,
            "factors": []
        }
        
        try:
            signal = market_data.get("signal", 0.0)
            volatility = abs(signal)
            
            if volatility > 0.8:
                risk["level"] = "MEDIUM"
                risk["factors"].append("high_signal_volatility")
            
            if volatility > 0.9:
                risk["level"] = "HIGH"
                risk["factors"].append("extreme_signal_volatility")
            
        except Exception as e:
            logger.error(f"[COGNITIVE_ORCHESTRATOR] Risk assessment failed: {e}")
        
        return risk
    
    def assess_cognitive_risk(self, context: dict[str, Any]) -> RiskAssessment:
        """Comprehensive risk assessment using cognitive simulation.

        This is a more thorough assessment that can run asynchronously.
        Used for pre-trade risk evaluation and scenario analysis.
        """
        if not self._initialized or not self._enabled:
            return RiskAssessment(
                overall_risk="LOW",
                confidence=0.5,
                scenarios_analyzed=0,
                high_risk_scenarios=[],
                recommended_actions=["proceed_with_caution"]
            )
        
        try:
            # Run scenario simulations
            from cognitive_engine.cognitive_simulator.scenario import Scenario, ScenarioType
            
            scenarios = [
                self._simulator.run_volatility_explosion(),
                self._simulator.run_liquidity_collapse(),
            ]
            
            high_risk = [s.scenario_id for s in scenarios if s.risk_level.value in ("HIGH", "EXTREME")]
            
            overall_risk = "EXTREME" if high_risk else "MEDIUM" if len(scenarios) > 1 else "LOW"
            
            return RiskAssessment(
                overall_risk=overall_risk,
                confidence=0.8,
                scenarios_analyzed=len(scenarios),
                high_risk_scenarios=high_risk,
                recommended_actions=self._generate_risk_recommendations(overall_risk),
                exposure_multiplier=0.7 if overall_risk == "HIGH" else 0.5 if overall_risk == "EXTREME" else 1.0
            )
            
        except Exception as e:
            logger.error(f"[COGNITIVE_ORCHESTRATOR] Cognitive risk assessment failed: {e}")
            return RiskAssessment(
                overall_risk="LOW",
                confidence=0.5,
                scenarios_analyzed=0,
                high_risk_scenarios=[],
                recommended_actions=["proceed_with_caution"]
            )
    
    def _generate_risk_recommendations(self, risk_level: str) -> list[str]:
        """Generate recommendations based on risk level."""
        if risk_level == "EXTREME":
            return ["reduce_exposure_significantly", "activate_circuit_breakers", "consider_halt"]
        elif risk_level == "HIGH":
            return ["reduce_exposure", "tighten_stops", "increase_monitoring"]
        elif risk_level == "MEDIUM":
            return ["monitor_closely", "prepare_contingency"]
        else:
            return ["normal_operation"]
    
    def generate_investigations(self, limit: int = 10) -> list[Any]:
        """Generate prioritized investigations based on curiosity scoring.
        
        This identifies the most valuable questions to investigate.
        """
        if not self._initialized or not self._enabled:
            return []
        
        try:
            # In a full implementation, this would:
            # 1. Identify anomalies and patterns
            # 2. Generate questions about them
            # 3. Score questions by curiosity
            # 4. Return prioritized investigations
            
            # Placeholder implementation
            return []
            
        except Exception as e:
            logger.error(f"[COGNITIVE_ORCHESTRATOR] Investigation generation failed: {e}")
            return []
    
    def set_mode(self, mode: str) -> None:
        """Set cognitive orchestrator mode.
        
        Args:
            mode: "observation" (read-only), "shadow" (recommendations only),
                  "active" (full integration)
        """
        valid_modes = ["observation", "shadow", "active"]
        if mode not in valid_modes:
            logger.warning(f"[COGNITIVE_ORCHESTRATOR] Invalid mode: {mode}")
            return
        
        self._mode = mode
        logger.info(f"[COGNITIVE_ORCHESTRATOR] Mode set to {mode}")
    
    def enable(self) -> None:
        """Enable cognitive orchestrator."""
        self._enabled = True
        logger.info("[COGNITIVE_ORCHESTRATOR] Enabled")
    
    def disable(self) -> None:
        """Disable cognitive orchestrator."""
        self._enabled = False
        logger.info("[COGNITIVE_ORCHESTRATOR] Disabled")
    
    def get_metrics(self) -> dict[str, Any]:
        """Get cognitive orchestrator metrics."""
        avg_latency = (
            self._total_enrichment_time_ms / self._enrichment_count
            if self._enrichment_count > 0 else 0.0
        )
        
        return {
            "initialized": self._initialized,
            "enabled": self._enabled,
            "mode": self._mode,
            "enrichment_count": self._enrichment_count,
            "avg_enrichment_latency_ms": avg_latency,
            "knowledge_graph_nodes": self._knowledge_graph.get_node_count(),
            "knowledge_graph_edges": self._knowledge_graph.get_edge_count(),
            "narratives_count": len(self._narrative_engine.get_all()),
        }


# Singleton instance
_orchestrator: CognitiveOrchestrator | None = None
_lock = None


def get_cognitive_orchestrator() -> CognitiveOrchestrator:
    """Get the singleton cognitive orchestrator instance."""
    global _orchestrator
    if _orchestrator is None:
        import threading
        global _lock
        if _lock is None:
            _lock = threading.Lock()
        
        with _lock:
            if _orchestrator is None:
                _orchestrator = CognitiveOrchestrator()
    
    return _orchestrator


__all__ = [
    "CognitiveEnrichment",
    "CognitiveOrchestrator", 
    "RiskAssessment",
    "get_cognitive_orchestrator",
]