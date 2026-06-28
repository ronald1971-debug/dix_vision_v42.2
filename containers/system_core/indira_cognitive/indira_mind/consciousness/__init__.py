"""
indira_cognitive.indira_mind.consciousness
DIX VISION v42.2 — INDIRA Mind Consciousness Interface

Enhanced trading consciousness with advanced attention, metacognitive monitoring,
and neuro-symbolic reasoning capabilities.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import datetime
from enum import StrEnum
from typing import Any, Dict, List, Optional

from indira_cognitive.indira_mind.self_awareness import (
    EnhancedINDIRASelfAwareness,
    INDIRASelfAwarenessInterface,
)
from indira_cognitive.shared_interfaces.enhanced_types import (
    AttentionType,
    ConfidenceLevel,
    CuriosityScore,
    MetacognitiveState,
    SelfAwarenessLevel,
)


class ConsciousnessState(StrEnum):
    """States of INDIRA consciousness."""

    ACTIVE = "active"
    FOCUSED = "focused"
    REFLECTING = "reflecting"
    LEARNING = "learning"
    OFFLINE = "offline"


@dataclass
class MarketBelief:
    """Enhanced belief about market state with vector storage support."""

    belief_id: str
    category: str  # regime | trend | volatility | correlation | custom
    claim: str
    confidence: float
    evidence_ids: List[str] = field(default_factory=list)
    formed_at: datetime = field(default_factory=datetime.utcnow)
    last_validated: datetime = field(default_factory=datetime.utcnow)
    vector_embedding: Optional[List[float]] = None  # Enhanced: vector support
    metadata: Dict[str, Any] = field(default_factory=dict)

    @property
    def confidence_level(self) -> ConfidenceLevel:
        if self.confidence >= 0.8:
            return ConfidenceLevel.VERY_HIGH
        if self.confidence >= 0.6:
            return ConfidenceLevel.HIGH
        if self.confidence >= 0.4:
            return ConfidenceLevel.MODERATE
        if self.confidence >= 0.2:
            return ConfidenceLevel.LOW
        return ConfidenceLevel.NONE

    def is_stale(self, max_age_seconds: float = 300.0) -> bool:
        return (datetime.utcnow() - self.last_validated).total_seconds() > max_age_seconds


@dataclass
class TradingHypothesis:
    """Enhanced trading hypothesis with advanced management capabilities."""

    hypothesis_id: str
    title: str
    thesis: str
    symbol: str
    direction: str  # long | short
    confidence: float
    evidence_ids: List[str] = field(default_factory=list)
    belief_ids: List[str] = field(default_factory=list)
    status: str = "FORMING"  # FORMING | ACTIVE | VALIDATED | INVALIDATED | EXPIRED | EXECUTED
    expected_return: float = 0.0
    risk_estimate: float = 0.0
    time_horizon_seconds: float = 0.0
    formed_at: datetime = field(default_factory=datetime.utcnow)
    expires_at: float = 0.0
    vector_embedding: Optional[List[float]] = None  # Enhanced: vector support
    bayesian_probability: Optional[float] = None  # Enhanced: Bayesian evaluation
    metadata: Dict[str, Any] = field(default_factory=dict)

    @property
    def risk_reward_ratio(self) -> float:
        if self.risk_estimate == 0:
            return 0.0
        return self.expected_return / self.risk_estimate

    def is_expired(self) -> bool:
        if self.expires_at <= 0:
            return False
        return datetime.utcnow().timestamp() > self.expires_at


@dataclass
class TradingIntent:
    """Enhanced trading intent with neuro-symbolic reasoning."""

    intent_id: str
    intent_type: str  # BUY | SELL | HOLD | DELEGATE
    asset: str
    side: str  # BUY | SELL | NONE
    order_type: str  # MARKET | LIMIT | NONE
    size_usd: float
    confidence: float
    reasoning_chain: List[str] = field(default_factory=list)  # Enhanced: neuro-symbolic chain
    neural_reasoning: Optional[str] = None  # Enhanced: LLM reasoning
    symbolic_reasoning: Optional[str] = None  # Enhanced: knowledge graph reasoning
    confidence_breakdown: Dict[str, float] = field(
        default_factory=dict
    )  # Enhanced: confidence breakdown
    timestamp_utc: str = ""
    metadata: Dict[str, Any] = field(default_factory=dict)


class INDIRAMindInterface(ABC):
    """
    Enhanced INDIRA Mind interface with advanced cognitive capabilities.

    Enhanced Features:
    - Advanced attention management
    - Metacognitive monitoring
    - Neuro-symbolic reasoning
    - Curiosity-driven exploration
    - Advanced self-awareness
    """

    @abstractmethod
    def get_consciousness_state(self) -> ConsciousnessState:
        """Get current consciousness state."""

    @abstractmethod
    def form_market_belief(
        self, category: str, claim: str, confidence: float, evidence_ids: List[str] | None = None
    ) -> MarketBelief:
        """Form a market belief with vector storage support."""

    @abstractmethod
    def generate_trading_hypothesis(
        self,
        title: str,
        thesis: str,
        symbol: str,
        direction: str,
        confidence: float,
        expected_return: float = 0.0,
        risk_estimate: float = 0.0,
        time_horizon_seconds: float = 3600.0,
        belief_ids: List[str] | None = None,
    ) -> TradingHypothesis:
        """Generate a trading hypothesis with advanced management."""

    @abstractmethod
    def produce_trading_intent(
        self,
        intent_type: str,
        asset: str,
        side: str,
        size_usd: float,
        confidence: float,
        reasoning_chain: List[str] | None = None,
        neural_reasoning: str | None = None,
        symbolic_reasoning: str | None = None,
    ) -> TradingIntent:
        """Produce trading intent with neuro-symbolic reasoning."""

    @abstractmethod
    def allocate_attention(
        self, attention_targets: List[str], attention_type: AttentionType = AttentionType.ADAPTIVE
    ) -> Dict[str, float]:
        """Allocate attention to different cognitive targets."""

    @abstractmethod
    def get_curiosity_score(self, situation: Dict[str, Any]) -> CuriosityScore:
        """Get curiosity score for a given situation (information-theoretic)."""

    @abstractmethod
    def get_metacognitive_state(self) -> MetacognitiveState:
        """Get current metacognitive state."""

    @abstractmethod
    def explain_reasoning(self, decision_id: str) -> str:
        """Explain reasoning for a decision (self-explanation capability)."""

    @abstractmethod
    def calibrate_confidence(self, actual_outcome: float, predicted_outcome: float) -> float:
        """Calibrate confidence based on outcome."""

    @abstractmethod
    def assess_self_performance(self) -> SelfAwarenessLevel:
        """Assess own performance level."""


class EnhancedINDIRAMind(INDIRAMindInterface):
    """
    Enhanced implementation of INDIRA Mind with all cognitive enhancements.
    """

    def __init__(self) -> None:
        self._consciousness_state = ConsciousnessState.ACTIVE
        self._beliefs: Dict[str, MarketBelief] = {}
        self._hypotheses: Dict[str, TradingHypothesis] = {}
        self._intent_history: List[TradingIntent] = []
        self._attention_allocation: Dict[str, float] = {}
        self._metacognitive_state = MetacognitiveState()
        # ENHANCED: Comprehensive self-awareness for trading
        self._self_awareness: INDIRASelfAwarenessInterface = EnhancedINDIRASelfAwareness()

    def get_consciousness_state(self) -> ConsciousnessState:
        return self._consciousness_state

    def form_market_belief(
        self, category: str, claim: str, confidence: float, evidence_ids: List[str] | None = None
    ) -> MarketBelief:
        belief = MarketBelief(
            belief_id=self._generate_id("belief"),
            category=category,
            claim=claim,
            confidence=max(0.0, min(1.0, confidence)),
            evidence_ids=evidence_ids or [],
        )
        self._beliefs[belief.belief_id] = belief
        return belief

    def generate_trading_hypothesis(
        self,
        title: str,
        thesis: str,
        symbol: str,
        direction: str,
        confidence: float,
        expected_return: float = 0.0,
        risk_estimate: float = 0.0,
        time_horizon_seconds: float = 3600.0,
        belief_ids: List[str] | None = None,
    ) -> TradingHypothesis:
        # Check hypothesis limits
        active_count = sum(
            1 for h in self._hypotheses.values() if h.status in ("FORMING", "ACTIVE")
        )
        if active_count >= 10:  # Max 10 active hypotheses
            return None

        hypothesis = TradingHypothesis(
            hypothesis_id=self._generate_id("hypothesis"),
            title=title,
            thesis=thesis,
            symbol=symbol,
            direction=direction,
            confidence=max(0.0, min(1.0, confidence)),
            expected_return=expected_return,
            risk_estimate=risk_estimate,
            time_horizon_seconds=time_horizon_seconds,
            belief_ids=belief_ids or [],
            status="FORMING",
            expires_at=datetime.utcnow().timestamp() + time_horizon_seconds,
        )
        self._hypotheses[hypothesis.hypothesis_id] = hypothesis
        return hypothesis

    def produce_trading_intent(
        self,
        intent_type: str,
        asset: str,
        side: str,
        size_usd: float,
        confidence: float,
        reasoning_chain: List[str] | None = None,
        neural_reasoning: str | None = None,
        symbolic_reasoning: str | None = None,
    ) -> TradingIntent:
        intent = TradingIntent(
            intent_id=self._generate_id("intent"),
            intent_type=intent_type,
            asset=asset,
            side=side,
            size_usd=size_usd,
            confidence=max(0.0, min(1.0, confidence)),
            reasoning_chain=reasoning_chain or [],
            neural_reasoning=neural_reasoning,
            symbolic_reasoning=symbolic_reasoning,
            timestamp_utc=datetime.utcnow().isoformat(),
        )
        self._intent_history.append(intent)
        return intent

    def allocate_attention(
        self, attention_targets: List[str], attention_type: AttentionType = AttentionType.ADAPTIVE
    ) -> Dict[str, float]:
        # Enhanced attention allocation
        total_targets = len(attention_targets)
        if total_targets == 0:
            return {}

        # Adaptive attention distribution
        if attention_type == AttentionType.ADAPTIVE:
            # Distribute attention based on importance (simplified)
            base_attention = 1.0 / total_targets
            allocation = {target: base_attention for target in attention_targets}
        elif attention_type == AttentionType.MULTI_HEAD:
            # Multi-head attention (each target gets dedicated attention)
            allocation = {target: 1.0 for target in attention_targets}
        else:
            # Hierarchical attention
            allocation = {target: 1.0 / total_targets for target in attention_targets}

        self._attention_allocation = allocation
        return allocation

    def get_curiosity_score(self, situation: Dict[str, Any]) -> CuriosityScore:
        # Information-theoretic curiosity (simplified)
        # In production, this would use information gain calculations
        return CuriosityScore(score=0.5, information_gain=0.3, novelty=0.7, importance=0.6)

    def get_metacognitive_state(self) -> MetacognitiveState:
        return self._metacognitive_state

    def explain_reasoning(self, decision_id: str) -> str:
        # Self-explanation capability
        # In production, this would provide detailed reasoning chains
        return f"Decision {decision_id} was made based on market analysis and risk assessment"

    def calibrate_confidence(self, actual_outcome: float, predicted_outcome: float) -> float:
        # Confidence calibration
        # Simplified calibration approach
        error = abs(actual_outcome - predicted_outcome)
        if error > 0.5:
            return max(0.0, 1.0 - 0.2)  # Reduce confidence
        return min(1.0, 1.0 + 0.1)  # Increase confidence

    def assess_self_performance(self) -> SelfAwarenessLevel:
        # ENHANCED: Use comprehensive self-awareness module
        performance_assessment = self._self_awareness.assess_performance()
        return (
            performance_assessment.performance_rating >= 0.7
            and SelfAwarenessLevel.CONFIDENT
            or SelfAwarenessLevel.COMPETENT
        )

    def get_trading_self_awareness(self) -> INDIRASelfAwarenessInterface:
        """Get INDIRA's comprehensive trading self-awareness module."""
        return self._self_awareness

    def comprehensive_self_awareness_check(self) -> str:
        """Perform comprehensive self-awareness check with detailed analysis."""
        awareness = self._self_awareness.get_comprehensive_self_awareness()
        return self._self_awareness.self_reflect({"type": "comprehensive_check"})

    def _generate_id(self, prefix: str) -> str:
        import time
        import uuid

        return f"{prefix}_{uuid.uuid4().hex[:12]}_{int(time.time())}"


__all__ = [
    "ConsciousnessState",
    "MarketBelief",
    "TradingHypothesis",
    "TradingIntent",
    "INDIRAMindInterface",
    "EnhancedINDIRAMind",
    # Enhanced self-awareness
    "INDIRASelfAwarenessInterface",
    "EnhancedINDIRASelfAwareness",
]
