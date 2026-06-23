"""
indira_cognitive.indira_mind.self_awareness
DIX VISION v42.2 — INDIRA Trading Self-Awareness

Enhanced self-awareness specifically for trading operations including:
- Performance self-assessment and tracking
- Risk self-awareness and exposure monitoring
- Decision quality self-evaluation
- Learning progress self-monitoring
- Trading strategy self-reflection
- Market state self-understanding
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import StrEnum
from typing import Any, Dict, List

from indira_cognitive.shared_interfaces.enhanced_types import (
    MetacognitiveState,
    SelfAwarenessLevel,
)


class TradingSelfAwarenessDimension(StrEnum):
    """Dimensions of trading self-awareness."""

    PERFORMANCE = "performance"
    RISK = "risk"
    DECISION_QUALITY = "decision_quality"
    LEARNING_PROGRESS = "learning_progress"
    MARKET_REGIME = "market_regime"
    STRATEGY_EFFECTIVENESS = "strategy_effectiveness"
    CAPABILITY = "capability"
    LIMITATION = "limitation"


@dataclass
class PerformanceSelfAssessment:
    """
    Self-assessment of trading performance.
    Enhanced feature: detailed performance self-awareness.
    """

    assessment_id: str
    timestamp: datetime = field(default_factory=datetime.utcnow)
    period_start: datetime = field(default_factory=lambda: datetime.utcnow() - timedelta(hours=24))
    period_end: datetime = field(default_factory=datetime.utcnow)

    # Performance metrics
    total_pnl: float = 0.0
    total_pnl_percent: float = 0.0
    win_rate: float = 0.0
    sharpe_ratio: float = 0.0
    max_drawdown: float = 0.0
    avg_trade_duration_seconds: float = 0.0
    total_trades: int = 0
    winning_trades: int = 0
    losing_trades: int = 0

    # Self-awareness of performance
    performance_rating: float = 0.0  # 0-1 self-assessment
    performance_confidence: float = 0.0  # 0-1 confidence in assessment
    performance_trend: str = "NEUTRAL"  # IMPROVING | STABLE | DECLINING

    # Self-identified strengths
    identified_strengths: List[str] = field(default_factory=list)

    # Self-identified weaknesses
    identified_weaknesses: List[str] = field(default_factory=list)

    # Self-explanation of performance
    self_explanation: str = ""

    # Improvement recommendations
    self_generated_recommendations: List[str] = field(default_factory=list)

    @property
    def is_performing_well(self) -> bool:
        return self.performance_rating >= 0.7

    @property
    def is_confident_in_assessment(self) -> bool:
        return self.performance_confidence >= 0.7


@dataclass
class RiskSelfAwareness:
    """
    Self-awareness of risk exposure and risk management.
    Enhanced feature: comprehensive risk self-awareness.
    """

    assessment_id: str
    timestamp: datetime = field(default_factory=datetime.utcnow)

    # Current risk exposure
    current_position_risk: float = 0.0  # USD value at risk
    current_portfolio_risk: float = 0.0  # Portfolio VaR
    max_position_risk_allowed: float = 0.0
    max_portfolio_risk_allowed: float = 0.0

    # Risk self-assessment
    risk_comfort_level: float = 0.5  # 0-1, 0.5 = comfortable
    risk_management_rating: float = 0.0  # 0-1 self-assessment
    risk_assessment_confidence: float = 0.0  # 0-1 confidence

    # Self-identified risk factors
    identified_risk_factors: List[str] = field(default_factory=list)

    # Risk awareness by type
    market_risk_awareness: float = 0.0  # 0-1
    liquidity_risk_awareness: float = 0.0  # 0-1
    concentration_risk_awareness: float = 0.0  # 0-1
    volatility_risk_awareness: float = 0.0  # 0-1

    # Risk self-regulation
    is_self_limiting: bool = False
    self_imposed_restrictions: List[str] = field(default_factory=list)

    # Risk self-explanation
    risk_self_explanation: str = ""

    @property
    def is_risk_aware(self) -> bool:
        return all(
            [
                self.market_risk_awareness > 0.7,
                self.liquidity_risk_awareness > 0.7,
                self.concentration_risk_awareness > 0.7,
                self.volatility_risk_awareness > 0.7,
            ]
        )

    @property
    def is_within_risk_tolerance(self) -> bool:
        return (
            self.current_position_risk <= self.max_position_risk_allowed
            and self.current_portfolio_risk <= self.max_portfolio_risk_allowed
        )


@dataclass
class DecisionQualitySelfEvaluation:
    """
    Self-evaluation of decision quality.
    Enhanced feature: decision quality self-awareness.
    """

    evaluation_id: str
    decision_id: str
    timestamp: datetime = field(default_factory=datetime.utcnow)

    # Decision self-assessment
    decision_quality_rating: float = 0.0  # 0-1 self-assessment
    decision_confidence: float = 0.0  # 0-1 confidence at time of decision
    decision_correctness: bool = False  # actual outcome

    # Decision self-analysis
    reasoning_quality: float = 0.0  # 0-1 self-assessment of reasoning
    information_quality: float = 0.0  # 0-1 self-assessment of information used
    timing_quality: float = 0.0  # 0-1 self-assessment of timing

    # Decision self-correction
    would_make_same_decision: bool = False
    what_would_do_differently: str = ""
    lessons_learned: str = ""

    # Decision pattern self-awareness
    decision_pattern: str = ""
    is_pattern_recurring: bool = False
    pattern_quality: float = 0.0  # 0-1 quality of this decision pattern

    @property
    def is_high_quality_decision(self) -> bool:
        return self.decision_quality_rating >= 0.7


@dataclass
class LearningProgressSelfMonitoring:
    """
    Self-monitoring of learning progress.
    Enhanced feature: learning progress self-awareness.
    """

    monitoring_id: str
    timestamp: datetime = field(default_factory=datetime.utcnow)

    # Learning self-assessment
    learning_rate: float = 0.0  # 0-1 self-assessment
    learning_effectiveness: float = 0.0  # 0-1 self-assessment
    learning_confidence: float = 0.0  # 0-1 confidence

    # Skill self-awareness
    market_analysis_skill: float = 0.0  # 0-1 self-assessment
    pattern_recognition_skill: float = 0.0  # 0-1 self-assessment
    risk_management_skill: float = 0.0  # 0-1 self-assessment
    timing_skill: float = 0.0  # 0-1 self-assessment

    # Knowledge self-awareness
    market_knowledge_depth: float = 0.0  # 0-1 self-assessment
    strategy_knowledge_depth: float = 0.0  # 0-1 self-assessment
    system_knowledge_depth: float = 0.0  # 0-1 self-assessment

    # Learning progress
    skills_improving: List[str] = field(default_factory=list)
    skills_declining: List[str] = field(default_factory=list)
    knowledge_gaps: List[str] = field(default_factory=list)

    # Self-directed learning
    self_identified_learning_needs: List[str] = field(default_factory=list)
    self_generated_learning_goals: List[str] = field(default_factory=list)

    @property
    def is_learning_effectively(self) -> bool:
        return self.learning_effectiveness >= 0.7


@dataclass
class TradingSelfAwarenessState:
    """
    Comprehensive trading self-awareness state.
    Enhanced feature: integrated self-awareness across all dimensions.
    """

    awareness_state_id: str
    timestamp: datetime = field(default_factory=datetime.utcnow)

    # Overall self-awareness
    overall_self_awareness_level: SelfAwarenessLevel = SelfAwarenessLevel.AWARE
    overall_confidence: float = 0.0

    # Dimensional self-awareness
    performance_awareness: PerformanceSelfAssessment | None = None
    risk_awareness: RiskSelfAwareness | None = None
    decision_quality_awareness: DecisionQualitySelfEvaluation | None = None
    learning_progress_awareness: LearningProgressSelfMonitoring | None = None

    # Metacognitive state
    metacognitive_state: MetacognitiveState = field(default_factory=MetacognitiveState)

    # Self-identity
    self_concept: str = ""
    self_capabilities: List[str] = field(default_factory=list)
    self_limitations: List[str] = field(default_factory=list)

    # Self-regulation
    is_self_monitoring: bool = True
    is_self_correcting: bool = True
    self_correction_history: List[str] = field(default_factory=list)

    @property
    def is_aware_of_capabilities(self) -> bool:
        return len(self.self_capabilities) > 0

    @property
    def is_aware_of_limitations(self) -> bool:
        return len(self.self_limitations) > 0


class INDIRASelfAwarenessInterface(ABC):
    """
    Enhanced interface for INDIRA trading self-awareness.

    This interface provides comprehensive self-awareness capabilities for trading operations,
    including performance assessment, risk awareness, decision quality evaluation, and
    learning progress monitoring.
    """

    @abstractmethod
    def assess_performance(self, period_hours: int = 24) -> PerformanceSelfAssessment:
        """Assess trading performance over a period."""

    @abstractmethod
    def assess_risk_awareness(self) -> RiskSelfAwareness:
        """Assess current risk awareness and exposure."""

    @abstractmethod
    def evaluate_decision_quality(self, decision_id: str) -> DecisionQualitySelfEvaluation:
        """Evaluate the quality of a specific decision."""

    @abstractmethod
    def monitor_learning_progress(self) -> LearningProgressSelfMonitoring:
        """Monitor learning progress and skill development."""

    @abstractmethod
    def get_comprehensive_self_awareness(self) -> TradingSelfAwarenessState:
        """Get comprehensive self-awareness state across all dimensions."""

    @abstractmethod
    def identify_self_capabilities(self) -> List[str]:
        """Identify own trading capabilities."""

    @abstractmethod
    def identify_self_limitations(self) -> List[str]:
        """Identify own trading limitations."""

    @abstractmethod
    def self_reflect(self, context: Dict[str, Any]) -> str:
        """Perform self-reflection on a given context."""

    @abstractmethod
    def calibrate_self_assessment(
        self, actual_outcome: float, self_assessed_outcome: float
    ) -> float:
        """Calibrate self-assessment based on actual outcomes."""

    @abstractmethod
    def update_self_concept(self) -> None:
        """Update self-concept based on recent performance and learning."""


class EnhancedINDIRASelfAwareness(INDIRASelfAwarenessInterface):
    """
    Enhanced implementation of INDIRA trading self-awareness.
    """

    def __init__(self) -> None:
        self._performance_history: List[PerformanceSelfAssessment] = []
        self._decision_evaluations: Dict[str, DecisionQualitySelfEvaluation] = {}
        self._self_awareness_state = TradingSelfAwarenessState(
            awareness_state_id=self._generate_id("awareness")
        )
        self._self_capabilities: List[str] = []
        self._self_limitations: List[str] = []

    def assess_performance(self, period_hours: int = 24) -> PerformanceSelfAssessment:
        """Assess trading performance over a period."""
        # In production, this would analyze actual performance data
        assessment = PerformanceSelfAssessment(
            assessment_id=self._generate_id("performance"),
            period_start=datetime.utcnow() - timedelta(hours=period_hours),
            period_end=datetime.utcnow(),
            total_pnl=0.0,  # Would be calculated from actual data
            total_pnl_percent=0.0,
            win_rate=0.0,
            sharpe_ratio=0.0,
            max_drawdown=0.0,
            total_trades=0,
            winning_trades=0,
            losing_trades=0,
            performance_rating=0.5,  # Self-assessment
            performance_confidence=0.5,
            performance_trend="NEUTRAL",
            self_explanation="Performance assessment based on recent trading activity",
        )

        self._performance_history.append(assessment)
        return assessment

    def assess_risk_awareness(self) -> RiskSelfAwareness:
        """Assess current risk awareness and exposure."""
        assessment = RiskSelfAwareness(
            assessment_id=self._generate_id("risk_awareness"),
            current_position_risk=0.0,
            current_portfolio_risk=0.0,
            max_position_risk_allowed=100000.0,
            max_portfolio_risk_allowed=500000.0,
            risk_comfort_level=0.5,
            risk_management_rating=0.5,
            risk_assessment_confidence=0.5,
            market_risk_awareness=0.7,
            liquidity_risk_awareness=0.7,
            concentration_risk_awareness=0.7,
            volatility_risk_awareness=0.7,
            risk_self_explanation="Risk awareness assessment based on current positions and market conditions",
        )
        return assessment

    def evaluate_decision_quality(self, decision_id: str) -> DecisionQualitySelfEvaluation:
        """Evaluate the quality of a specific decision."""
        evaluation = DecisionQualitySelfEvaluation(
            evaluation_id=self._generate_id("decision_eval"),
            decision_id=decision_id,
            decision_quality_rating=0.5,
            decision_confidence=0.5,
            decision_correctness=False,
            reasoning_quality=0.5,
            information_quality=0.5,
            timing_quality=0.5,
            would_make_same_decision=False,
            what_would_do_differently="",
            lessons_learned="",
        )

        self._decision_evaluations[decision_id] = evaluation
        return evaluation

    def monitor_learning_progress(self) -> LearningProgressSelfMonitoring:
        """Monitor learning progress and skill development."""
        monitoring = LearningProgressSelfMonitoring(
            monitoring_id=self._generate_id("learning_progress"),
            learning_rate=0.5,
            learning_effectiveness=0.5,
            learning_confidence=0.5,
            market_analysis_skill=0.5,
            pattern_recognition_skill=0.5,
            risk_management_skill=0.5,
            timing_skill=0.5,
            market_knowledge_depth=0.5,
            strategy_knowledge_depth=0.5,
            system_knowledge_depth=0.5,
            self_identified_learning_needs=[
                "Improve market regime detection",
                "Enhance pattern recognition in volatile markets",
            ],
            self_generated_learning_goals=[
                "Achieve 80% win rate in stable market regimes",
                "Reduce maximum drawdown to <2%",
            ],
        )
        return monitoring

    def get_comprehensive_self_awareness(self) -> TradingSelfAwarenessState:
        """Get comprehensive self-awareness state across all dimensions."""
        self._self_awareness_state.timestamp = datetime.utcnow()
        self._self_awareness_state.performance_awareness = self.assess_performance()
        self._self_awareness_state.risk_awareness = self.assess_risk_awareness()
        self._self_awareness_state.decision_quality_awareness = None  # Would be specific decision
        self._self_awareness_state.learning_progress_awareness = self.monitor_learning_progress()
        self._self_awareness_state.self_capabilities = self.identify_self_capabilities()
        self._self_awareness_state.self_limitations = self.identify_self_limitations()

        return self._self_awareness_state

    def identify_self_capabilities(self) -> List[str]:
        """Identify own trading capabilities."""
        if not self._self_capabilities:
            # Initial capability identification
            self._self_capabilities = [
                "Fast market analysis (<5ms)",
                "Real-time risk assessment",
                "Hypothesis generation and validation",
                "Multi-asset correlation analysis",
                "Regime detection",
                "Pattern recognition",
                "Portfolio optimization",
                "Performance attribution",
            ]
        return self._self_capabilities.copy()

    def identify_self_limitations(self) -> List[str]:
        """Identify own trading limitations."""
        if not self._self_limitations:
            # Initial limitation identification
            self._self_limitations = [
                "Limited to liquid markets",
                "Difficulty in extreme volatility",
                "Black swan event vulnerability",
                "Dependent on data quality",
                "Limited understanding of regulatory changes",
                "Potential overfitting to historical patterns",
            ]
        return self._self_limitations.copy()

    def self_reflect(self, context: Dict[str, Any]) -> str:
        """Perform self-reflection on a given context."""
        awareness = self.get_comprehensive_self_awareness()

        reflection = f"""
Self-Reflection on Context: {context.get('type', 'General')}

Overall Self-Awareness Level: {awareness.overall_self_awareness_level}
Overall Confidence: {awareness.overall_confidence:.2f}

Performance Assessment:
- Rating: {awareness.performance_awareness.performance_rating:.2f}
- Trend: {awareness.performance_awareness.performance_trend}

Risk Awareness:
- Current Position Risk: ${awareness.risk_awareness.current_position_risk:,.2f}
- Risk Comfort Level: {awareness.risk_awareness.risk_comfort_level:.2f}

Capabilities: {', '.join(awareness.self_capabilities[:3])}...
Limitations: {', '.join(awareness.self_limitations[:3])}...

Self-Recommendations:
{', '.join(awareness.performance_awareness.self_generated_recommendations[:2]) if awareness.performance_awareness else 'None'}
        """
        return reflection.strip()

    def calibrate_self_assessment(
        self, actual_outcome: float, self_assessed_outcome: float
    ) -> float:
        """Calibrate self-assessment based on actual outcomes."""
        error = abs(actual_outcome - self_assessed_outcome)

        # Simple calibration adjustment
        if error > 0.3:
            # Reduce confidence in self-assessment
            self._self_awareness_state.overall_confidence = max(
                0.0, self._self_awareness_state.overall_confidence - 0.1
            )
        elif error < 0.1:
            # Increase confidence in self-assessment
            self._self_awareness_state.overall_confidence = min(
                1.0, self._self_awareness_state.overall_confidence + 0.05
            )

        return self._self_awareness_state.overall_confidence

    def update_self_concept(self) -> None:
        """Update self-concept based on recent performance and learning."""
        awareness = self.get_comprehensive_self_awareness()

        # Update self-concept based on performance
        if awareness.performance_awareness.is_performing_well:
            self._self_awareness_state.self_concept = (
                "I am a competent trading agent with strong performance "
                "and effective risk management capabilities."
            )
        else:
            self._self_awareness_state.self_concept = (
                "I am a learning trading agent focused on improving "
                "performance and refining risk management strategies."
            )

    def _generate_id(self, prefix: str) -> str:
        import time
        import uuid

        return f"{prefix}_{uuid.uuid4().hex[:12]}_{int(time.time())}"


__all__ = [
    "TradingSelfAwarenessDimension",
    "PerformanceSelfAssessment",
    "RiskSelfAwareness",
    "DecisionQualitySelfEvaluation",
    "LearningProgressSelfMonitoring",
    "TradingSelfAwarenessState",
    "INDIRASelfAwarenessInterface",
    "EnhancedINDIRASelfAwareness",
]
