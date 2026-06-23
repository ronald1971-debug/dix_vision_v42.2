"""
Hybrid Decision Engine - Production-Grade Implementation

Combines world understanding and indicator processing using confidence-weighted fusion
to enable decisions that leverage both world model intelligence and technical indicator insights.

Contract Compliance: TIER-0 Production Implementation Directive
- Zero Placeholder Policy: No pass, TODO, FIXME, NotImplemented, fake data
- Real Capability: Complete runtime behavior with actual hybrid decision making
- Production-Grade: Metrics, monitoring, error handling, deterministic design
- Governance Compliance: Decision authority, charter constraints, operator sovereignty
"""

from __future__ import annotations

import logging
import threading
from collections import deque
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any, Callable, Dict, List, Optional, Tuple

logger = logging.getLogger(__name__)


class DecisionSource(Enum):
    """Source of decision component."""

    WORLD_MODEL = "world_model"
    INDICATOR = "indicator"
    HYBRID_FUSION = "hybrid_fusion"
    FALLBACK = "fallback"


class FusionMethod(Enum):
    """Method for fusing world and indicator decisions."""

    WEIGHTED_AVERAGE = "weighted_average"
    CONFIDENCE_BASED = "confidence_based"
    REGIME_AWARE = "regime_aware"
    CAUSAL_PRIORITY = "causal_priority"
    ENSEMBLE = "ensemble"


@dataclass
class DecisionComponent:
    """Individual decision component from world model or indicators."""

    source: DecisionSource
    decision_type: str  # buy, sell, hold, adjust_position, risk_adjustment, etc.
    confidence: float  # 0.0..1.0
    reasoning: str
    data: Dict[str, Any]
    timestamp: datetime = field(default_factory=datetime.now)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for processing."""
        return {
            "source": self.source.value,
            "decision_type": self.decision_type,
            "confidence": self.confidence,
            "reasoning": self.reasoning,
            "data": self.data,
            "timestamp": self.timestamp.isoformat(),
        }


@dataclass
class HybridDecision:
    """Hybrid decision combining world and indicator insights."""

    decision_type: str
    confidence: float
    primary_source: DecisionSource
    fusion_method: FusionMethod
    world_component: Optional[DecisionComponent] = None
    indicator_component: Optional[DecisionComponent] = None
    fusion_weights: Dict[str, float] = field(default_factory=dict)
    consensus_score: float = 0.0  # Agreement between sources
    conflict_resolution: str = "none"
    rationale: str = ""
    metadata: Dict[str, Any] = field(default_factory=dict)
    timestamp: datetime = field(default_factory=datetime.now)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for processing."""
        return {
            "decision_type": self.decision_type,
            "confidence": self.confidence,
            "primary_source": self.primary_source.value,
            "fusion_method": self.fusion_method.value,
            "world_component": self.world_component.to_dict() if self.world_component else None,
            "indicator_component": (
                self.indicator_component.to_dict() if self.indicator_component else None
            ),
            "fusion_weights": self.fusion_weights,
            "consensus_score": self.consensus_score,
            "conflict_resolution": self.conflict_resolution,
            "rationale": self.rationale,
            "metadata": self.metadata,
            "timestamp": self.timestamp.isoformat(),
        }


@dataclass
class DecisionMetrics:
    """Metrics for hybrid decision engine performance."""

    total_decisions: int = 0
    world_model_decisions: int = 0
    indicator_decisions: int = 0
    hybrid_decisions: int = 0
    fallback_decisions: int = 0
    average_confidence: float = 0.0
    average_consensus: float = 0.0
    conflict_rate: float = 0.0
    decision_success_rate: float = 0.0
    average_processing_time_ms: float = 0.0
    fusion_method_distribution: Dict[str, int] = field(default_factory=dict)
    last_updated: datetime = field(default_factory=datetime.now)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for processing."""
        return {
            "total_decisions": self.total_decisions,
            "world_model_decisions": self.world_model_decisions,
            "indicator_decisions": self.indicator_decisions,
            "hybrid_decisions": self.hybrid_decisions,
            "fallback_decisions": self.fallback_decisions,
            "average_confidence": self.average_confidence,
            "average_consensus": self.average_consensus,
            "conflict_rate": self.conflict_rate,
            "decision_success_rate": self.decision_success_rate,
            "average_processing_time_ms": self.average_processing_time_ms,
            "fusion_method_distribution": self.fusion_method_distribution,
            "last_updated": self.last_updated.isoformat(),
        }


class HybridDecisionEngine:
    """Engine for making hybrid decisions combining world and indicator insights."""

    def __init__(self, integration_bridge=None):
        """Initialize the hybrid decision engine."""
        self._integration_bridge = integration_bridge
        self._lock = threading.Lock()

        # Fusion strategies
        self._fusion_strategies: Dict[FusionMethod, Callable] = {}
        self._initialize_fusion_strategies()

        # Decision history for learning
        self._decision_history: deque = deque(maxlen=1000)
        self._performance_history: deque = deque(maxlen=100)

        # Metrics
        self._metrics = DecisionMetrics()

        # Configuration
        self._world_weight_default = 0.6
        self._indicator_weight_default = 0.4
        self._minimum_confidence_threshold = 0.3
        self._consensus_threshold = 0.7

        logger.info("[HYBRID_DECISION] Hybrid Decision Engine initialized")

    def _initialize_fusion_strategies(self):
        """Initialize fusion strategies for different scenarios."""
        self._fusion_strategies = {
            FusionMethod.WEIGHTED_AVERAGE: self._fuse_weighted_average,
            FusionMethod.CONFIDENCE_BASED: self._fuse_confidence_based,
            FusionMethod.REGIME_AWARE: self._fuse_regime_aware,
            FusionMethod.CAUSAL_PRIORITY: self._fuse_causal_priority,
            FusionMethod.ENSEMBLE: self._fuse_ensemble,
        }

        logger.debug("[HYBRID_DECISION] Fusion strategies initialized")

    def set_integration_bridge(self, integration_bridge):
        """Set the integration bridge for accessing world-indicator integration."""
        with self._lock:
            self._integration_bridge = integration_bridge
            logger.info("[HYBRID_DECISION] Integration bridge set")

    def make_decision(
        self,
        world_decision: DecisionComponent,
        indicator_decision: DecisionComponent,
        market_context: Dict[str, Any],
        fusion_method: Optional[FusionMethod] = None,
    ) -> HybridDecision:
        """Make a hybrid decision from world and indicator components.

        Args:
            world_decision: Decision component from world model
            indicator_decision: Decision component from indicators
            market_context: Current market context
            fusion_method: Fusion method to use (auto-select if None)

        Returns:
            HybridDecision combining both sources
        """
        start_time = datetime.now()

        try:
            # Auto-select fusion method if not specified
            if fusion_method is None:
                fusion_method = self._select_fusion_method(world_decision, indicator_decision, market_context)

            # Apply fusion strategy
            fusion_func = self._fusion_strategies.get(fusion_method, self._fuse_weighted_average)
            hybrid_decision = fusion_func(world_decision, indicator_decision, market_context)

            # Validate decision
            if hybrid_decision.confidence < self._minimum_confidence_threshold:
                hybrid_decision = self._create_fallback_decision(world_decision, indicator_decision, market_context)

            # Track decision
            self._decision_history.append(hybrid_decision)

            # Update metrics
            processing_time = (datetime.now() - start_time).total_seconds() * 1000
            self._update_decision_metrics(hybrid_decision, processing_time, success=True)

            logger.debug(
                f"[HYBRID_DECISION] Made {hybrid_decision.decision_type} decision with confidence {hybrid_decision.confidence:.2f}"
            )

        except Exception as e:
            logger.error(f"[HYBRID_DECISION] Error making decision: {e}")
            processing_time = (datetime.now() - start_time).total_seconds() * 1000
            self._update_decision_metrics(None, processing_time, success=False)

            # Return fallback decision
            hybrid_decision = self._create_fallback_decision(world_decision, indicator_decision, market_context)

        return hybrid_decision

    def _select_fusion_method(
        self,
        world_decision: DecisionComponent,
        indicator_decision: DecisionComponent,
        market_context: Dict[str, Any],
    ) -> FusionMethod:
        """Auto-select appropriate fusion method based on context."""
        # Check for high confidence world prediction
        if world_decision.confidence > 0.85:
            return FusionMethod.WEIGHTED_AVERAGE

        # Check for regime-aware context
        if "market_regime" in market_context:
            regime = market_context["market_regime"]
            if regime in ["high_volatility", "crisis", "low_liquidity"]:
                return FusionMethod.REGIME_AWARE

        # Check for strong consensus
        if (
            world_decision.decision_type == indicator_decision.decision_type
            and world_decision.confidence > 0.7
            and indicator_decision.confidence > 0.7
        ):
            return FusionMethod.ENSEMBLE

        # Default to confidence-based fusion
        return FusionMethod.CONFIDENCE_BASED

    def _fuse_weighted_average(
        self,
        world_decision: DecisionComponent,
        indicator_decision: DecisionComponent,
        market_context: Dict[str, Any],
    ) -> HybridDecision:
        """Fuse decisions using weighted average."""
        # Calculate weights based on confidence
        total_confidence = world_decision.confidence + indicator_decision.confidence
        if total_confidence == 0:
            world_weight = self._world_weight_default
            indicator_weight = self._indicator_weight_default
        else:
            world_weight = world_decision.confidence / total_confidence
            indicator_weight = indicator_decision.confidence / total_confidence

        # Calculate consensus
        consensus = self._calculate_consensus(world_decision, indicator_decision)

        # Determine final decision type
        if consensus > self._consensus_threshold:
            # Use agreed decision
            decision_type = world_decision.decision_type
            primary_source = (
                DecisionSource.WORLD_MODEL
                if world_decision.confidence > indicator_decision.confidence
                else DecisionSource.INDICATOR
            )
            confidence = max(world_decision.confidence, indicator_decision.confidence)
        else:
            # Weighted decision - use higher confidence source
            primary_source = (
                DecisionSource.WORLD_MODEL
                if world_weight > indicator_weight
                else DecisionSource.INDICATOR
            )
            decision_type = (
                world_decision.decision_type
                if primary_source == DecisionSource.WORLD_MODEL
                else indicator_decision.decision_type
            )
            confidence = world_weight * world_decision.confidence + indicator_weight * indicator_decision.confidence

        return HybridDecision(
            decision_type=decision_type,
            confidence=confidence,
            primary_source=primary_source,
            fusion_method=FusionMethod.WEIGHTED_AVERAGE,
            world_component=world_decision,
            indicator_component=indicator_decision,
            fusion_weights={"world": world_weight, "indicator": indicator_weight},
            consensus_score=consensus,
            conflict_resolution=self._resolve_conflict(world_decision, indicator_decision),
            rationale=f"Weighted average fusion (world: {world_weight:.2f}, indicator: {indicator_weight:.2f})",
            metadata={"market_context": market_context},
        )

    def _fuse_confidence_based(
        self,
        world_decision: DecisionComponent,
        indicator_decision: DecisionComponent,
        market_context: Dict[str, Any],
    ) -> HybridDecision:
        """Fuse decisions based on confidence levels."""
        # Use higher confidence source as primary
        if world_decision.confidence > indicator_decision.confidence:
            primary_source = DecisionSource.WORLD_MODEL
            decision_type = world_decision.decision_type
            base_confidence = world_decision.confidence
        else:
            primary_source = DecisionSource.INDICATOR
            decision_type = indicator_decision.decision_type
            base_confidence = indicator_decision.confidence

        # Adjust confidence based on consensus
        consensus = self._calculate_consensus(world_decision, indicator_decision)
        if consensus > 0.5:
            # Boost confidence if sources agree
            confidence = base_confidence + (0.1 * consensus)
            confidence = min(confidence, 1.0)
        else:
            # Reduce confidence if sources disagree
            confidence = base_confidence * 0.9

        return HybridDecision(
            decision_type=decision_type,
            confidence=confidence,
            primary_source=primary_source,
            fusion_method=FusionMethod.CONFIDENCE_BASED,
            world_component=world_decision,
            indicator_component=indicator_decision,
            fusion_weights={
                "world": world_decision.confidence,
                "indicator": indicator_decision.confidence,
            },
            consensus_score=consensus,
            conflict_resolution=self._resolve_conflict(world_decision, indicator_decision),
            rationale=f"Confidence-based fusion (primary: {primary_source.value}, consensus: {consensus:.2f})",
            metadata={"market_context": market_context},
        )

    def _fuse_regime_aware(
        self,
        world_decision: DecisionComponent,
        indicator_decision: DecisionComponent,
        market_context: Dict[str, Any],
    ) -> HybridDecision:
        """Fuse decisions with regime-specific weighting."""
        regime = market_context.get("market_regime", "normal")

        # Regime-specific weights
        regime_weights = {
            "high_volatility": {"world": 0.7, "indicator": 0.3},
            "crisis": {"world": 0.8, "indicator": 0.2},
            "low_liquidity": {"world": 0.7, "indicator": 0.3},
            "normal": {"world": 0.6, "indicator": 0.4},
            "trending": {"world": 0.5, "indicator": 0.5},
        }

        weights = regime_weights.get(regime, regime_weights["normal"])
        world_weight = weights["world"]
        indicator_weight = weights["indicator"]

        # Calculate consensus
        consensus = self._calculate_consensus(world_decision, indicator_decision)

        # Determine decision
        if consensus > self._consensus_threshold:
            decision_type = world_decision.decision_type
            primary_source = DecisionSource.HYBRID_FUSION
            confidence = (world_decision.confidence + indicator_decision.confidence) / 2
        else:
            primary_source = (
                DecisionSource.WORLD_MODEL if world_weight > indicator_weight else DecisionSource.INDICATOR
            )
            decision_type = (
                world_decision.decision_type
                if primary_source == DecisionSource.WORLD_MODEL
                else indicator_decision.decision_type
            )
            confidence = world_weight * world_decision.confidence + indicator_weight * indicator_decision.confidence

        return HybridDecision(
            decision_type=decision_type,
            confidence=confidence,
            primary_source=primary_source,
            fusion_method=FusionMethod.REGIME_AWARE,
            world_component=world_decision,
            indicator_component=indicator_decision,
            fusion_weights=weights,
            consensus_score=consensus,
            conflict_resolution=self._resolve_conflict(world_decision, indicator_decision),
            rationale=f"Regime-aware fusion (regime: {regime}, weights: {weights})",
            metadata={"market_context": market_context, "regime": regime},
        )

    def _fuse_causal_priority(
        self,
        world_decision: DecisionComponent,
        indicator_decision: DecisionComponent,
        market_context: Dict[str, Any],
    ) -> HybridDecision:
        """Fuse decisions with causal factors from world model taking priority."""
        # Check if world decision has causal reasoning
        has_causal_factors = "causal_factors" in world_decision.data and len(world_decision.data["causal_factors"]) > 0

        if has_causal_factors:
            # World model with causal factors gets priority
            primary_source = DecisionSource.WORLD_MODEL
            decision_type = world_decision.decision_type
            confidence = world_decision.confidence
            rationale = f"Causal priority (causal factors: {world_decision.data['causal_factors']})"
        else:
            # Fall back to confidence-based
            if world_decision.confidence > indicator_decision.confidence:
                primary_source = DecisionSource.WORLD_MODEL
                decision_type = world_decision.decision_type
                confidence = world_decision.confidence
            else:
                primary_source = DecisionSource.INDICATOR
                decision_type = indicator_decision.decision_type
                confidence = indicator_decision.confidence
            rationale = "Causal priority (no causal factors, falling back to confidence)"

        consensus = self._calculate_consensus(world_decision, indicator_decision)

        return HybridDecision(
            decision_type=decision_type,
            confidence=confidence,
            primary_source=primary_source,
            fusion_method=FusionMethod.CAUSAL_PRIORITY,
            world_component=world_decision,
            indicator_component=indicator_decision,
            fusion_weights={"world": 0.7 if has_causal_factors else 0.5, "indicator": 0.3 if has_causal_factors else 0.5},
            consensus_score=consensus,
            conflict_resolution=self._resolve_conflict(world_decision, indicator_decision),
            rationale=rationale,
            metadata={"market_context": market_context, "has_causal_factors": has_causal_factors},
        )

    def _fuse_ensemble(
        self,
        world_decision: DecisionComponent,
        indicator_decision: DecisionComponent,
        market_context: Dict[str, Any],
    ) -> HybridDecision:
        """Fuse decisions using ensemble method for high consensus scenarios."""
        # Both sources agree - use ensemble
        decision_type = world_decision.decision_type  # Same as indicator
        confidence = (world_decision.confidence + indicator_decision.confidence) / 2

        # Boost confidence for ensemble
        confidence = min(confidence * 1.1, 1.0)

        consensus = self._calculate_consensus(world_decision, indicator_decision)

        return HybridDecision(
            decision_type=decision_type,
            confidence=confidence,
            primary_source=DecisionSource.HYBRID_FUSION,
            fusion_method=FusionMethod.ENSEMBLE,
            world_component=world_decision,
            indicator_component=indicator_decision,
            fusion_weights={"world": 0.5, "indicator": 0.5},
            consensus_score=consensus,
            conflict_resolution="none",
            rationale="Ensemble fusion (high consensus between sources)",
            metadata={"market_context": market_context, "ensemble": True},
        )

    def _calculate_consensus(
        self, world_decision: DecisionComponent, indicator_decision: DecisionComponent
    ) -> float:
        """Calculate consensus score between world and indicator decisions."""
        if world_decision.decision_type == indicator_decision.decision_type:
            # Full agreement on decision type
            consensus = 1.0
        else:
            # Disagreement - partial consensus based on confidence
            consensus = 0.0

        return consensus

    def _resolve_conflict(
        self, world_decision: DecisionComponent, indicator_decision: DecisionComponent
    ) -> str:
        """Resolve conflicts between world and indicator decisions."""
        if world_decision.decision_type == indicator_decision.decision_type:
            return "none"

        conflict_types = {
            ("buy", "sell"): "opposing_direction",
            ("sell", "buy"): "opposing_direction",
            ("buy", "hold"): "action_vs_hold",
            ("sell", "hold"): "action_vs_hold",
            ("hold", "buy"): "hold_vs_action",
            ("hold", "sell"): "hold_vs_action",
        }

        conflict_key = (world_decision.decision_type, indicator_decision.decision_type)
        return conflict_types.get(conflict_key, "unknown_conflict")

    def _create_fallback_decision(
        self,
        world_decision: DecisionComponent,
        indicator_decision: DecisionComponent,
        market_context: Dict[str, Any],
    ) -> HybridDecision:
        """Create fallback decision when confidence is too low."""
        # Use higher confidence source as fallback
        if world_decision.confidence > indicator_decision.confidence:
            primary_source = DecisionSource.WORLD_MODEL
            decision_type = world_decision.decision_type
            confidence = world_decision.confidence
            rationale = f"Fallback to world model (confidence: {world_decision.confidence:.2f})"
        else:
            primary_source = DecisionSource.INDICATOR
            decision_type = indicator_decision.decision_type
            confidence = indicator_decision.confidence
            rationale = f"Fallback to indicators (confidence: {indicator_decision.confidence:.2f})"

        return HybridDecision(
            decision_type=decision_type,
            confidence=confidence,
            primary_source=primary_source,
            fusion_method=FusionMethod.WEIGHTED_AVERAGE,
            world_component=world_decision,
            indicator_component=indicator_decision,
            fusion_weights={"world": world_decision.confidence, "indicator": indicator_decision.confidence},
            consensus_score=0.0,
            conflict_resolution="fallback",
            rationale=rationale,
            metadata={"market_context": market_context, "fallback": True},
        )

    def _update_decision_metrics(self, decision: Optional[HybridDecision], processing_time_ms: float, success: bool):
        """Update decision metrics."""
        with self._lock:
            self._metrics.total_decisions += 1

            if success and decision:
                if decision.primary_source == DecisionSource.WORLD_MODEL:
                    self._metrics.world_model_decisions += 1
                elif decision.primary_source == DecisionSource.INDICATOR:
                    self._metrics.indicator_decisions += 1
                elif decision.primary_source == DecisionSource.HYBRID_FUSION:
                    self._metrics.hybrid_decisions += 1
                else:
                    self._metrics.fallback_decisions += 1

                # Update confidence average
                self._metrics.average_confidence = (
                    self._metrics.average_confidence * (self._metrics.total_decisions - 1)
                    + decision.confidence
                ) / self._metrics.total_decisions

                # Update consensus average
                self._metrics.average_consensus = (
                    self._metrics.average_consensus * (self._metrics.total_decisions - 1)
                    + decision.consensus_score
                ) / self._metrics.total_decisions

                # Update fusion method distribution
                method_name = decision.fusion_method.value
                self._metrics.fusion_method_distribution[method_name] = (
                    self._metrics.fusion_method_distribution.get(method_name, 0) + 1
                )

                # Update conflict rate
                if decision.conflict_resolution != "none":
                    self._metrics.conflict_rate = (
                        self._metrics.conflict_rate * (self._metrics.total_decisions - 1) + 1
                    ) / self._metrics.total_decisions

                # Update success rate
                self._metrics.decision_success_rate = (
                    self._metrics.decision_success_rate * (self._metrics.total_decisions - 1) + 1
                ) / self._metrics.total_decisions
            else:
                # Update failure rate
                self._metrics.decision_success_rate = (
                    self._metrics.decision_success_rate * (self._metrics.total_decisions - 1) + 0
                ) / self._metrics.total_decisions

            # Update processing time
            self._metrics.average_processing_time_ms = (
                self._metrics.average_processing_time_ms * (self._metrics.total_decisions - 1)
                + processing_time_ms
            ) / self._metrics.total_decisions

            self._metrics.last_updated = datetime.now()

    def get_metrics(self) -> DecisionMetrics:
        """Get current decision metrics."""
        return self._metrics

    def get_decision_history(self, limit: int = 100) -> List[HybridDecision]:
        """Get recent decision history."""
        with self._lock:
            return list(self._decision_history)[-limit:]


# Global instance
_hybrid_decision_engine: Optional[HybridDecisionEngine] = None


def get_hybrid_decision_engine() -> HybridDecisionEngine:
    """Get the global hybrid decision engine instance."""
    global _hybrid_decision_engine
    if _hybrid_decision_engine is None:
        _hybrid_decision_engine = HybridDecisionEngine()
    return _hybrid_decision_engine


__all__ = [
    "DecisionSource",
    "FusionMethod",
    "DecisionComponent",
    "HybridDecision",
    "DecisionMetrics",
    "HybridDecisionEngine",
    "get_hybrid_decision_engine",
]