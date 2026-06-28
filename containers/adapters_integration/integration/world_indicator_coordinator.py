"""World-Indicator Integration Coordinator

Main coordinator for the integrated world understanding + indicator processing architecture.
This is the core component that implements the architectural principle that signal processing
is the primary driver (85%) for profitable trading, with world understanding (15%) providing
essential enhancement for risk management and regime awareness in the cognitive trading system.
"""

import logging
import threading
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional

logger = logging.getLogger(__name__)


class IntegrationMode(Enum):
    """Integration mode for world+indicator processing."""

    WORLD_ENHANCED_INDICATORS = "world_enhanced_indicators"
    INDICATOR_VALIDATED_WORLD = "indicator_validated_world"
    HYBRID_DECISION_FUSION = "hybrid_decision_fusion"
    FEEDBACK_LOOP = "feedback_loop"
    ADAPTIVE_WEIGHTING = "adaptive_weighting"


@dataclass
class IntegratedMarketAnalysis:
    """Combined analysis from world understanding and indicator processing."""

    # World understanding components
    world_regime: str  # bullish, bearish, sideways, high_volatility
    world_trend: str  # trending, mean_reverting
    world_confidence: float  # 0.0 to 1.0

    # Indicator components
    indicator_signals: Dict[str, float]  # indicator_name → signal_value
    indicator_confidence: float  # 0.0 to 1.0

    # Integrated components
    integrated_decision: str  # buy, sell, hold
    integrated_confidence: float  # 0.0 to 1.0
    integration_mode: IntegrationMode

    # Contribution analysis
    world_contribution: float  # 0.0 to 1.0
    indicator_contribution: float  # 0.0 to 1.0

    # Meta information
    analysis_timestamp: datetime = field(default_factory=datetime.now)
    validation_status: str = "valid"  # valid, conflicted, uncertain


@dataclass
class IntegrationPerformanceMetrics:
    """Performance metrics for world-indicator integration."""

    total_integrations: int = 0
    successful_integrations: int = 0
    conflict_count: int = 0
    average_confidence: float = 0.0
    average_processing_time_ms: float = 0.0

    # Mode-specific metrics
    mode_performance: Dict[str, Dict[str, float]] = field(default_factory=dict)


class WorldIndicatorCoordinator:
    """Main coordinator for integrated world+indicator processing."""

    def __init__(self):
        self._lock = threading.Lock()
        self._integration_mode = IntegrationMode.HYBRID_DECISION_FUSION
        self._metrics = IntegrationPerformanceMetrics()
        self._analysis_history: List[IntegratedMarketAnalysis] = []
        self._performance_target = 0.7  # Target confidence threshold

        # Component references (set during initialization)
        self._world_model = None
        self._indicator_processor = None
        self._integration_bridge = None

        logger.info("[WORLD_INDICATOR_COORDINATOR] Coordinator initialized")

    def initialize(
        self,
        world_model=None,
        indicator_processor=None,
        integration_bridge=None,
    ) -> bool:
        """Initialize the coordinator with component references."""
        try:
            self._world_model = world_model
            self._indicator_processor = indicator_processor
            self._integration_bridge = integration_bridge

            logger.info("[WORLD_INDICATOR_COORDINATOR] Components initialized")
            return True

        except Exception as e:
            logger.error(f"Error initializing coordinator: {e}")
            return False

    def set_integration_mode(self, mode: IntegrationMode) -> None:
        """Set the integration mode."""
        with self._lock:
            self._integration_mode = mode
            logger.info(f"[WORLD_INDICATOR_COORDINATOR] Integration mode set to {mode.value}")

    def analyze_market_integrated(
        self,
        market_data: Dict[str, Any],
        world_context: Optional[Dict[str, Any]] = None,
        indicator_data: Optional[Dict[str, Any]] = None,
    ) -> IntegratedMarketAnalysis:
        """Perform integrated market analysis using world+indicator processing."""
        start_time = datetime.now()

        try:
            # Get world understanding
            if world_context and self._world_model:
                world_analysis = self._analyze_world_context(world_context)
            else:
                world_analysis = self._get_default_world_analysis()

            # Get indicator analysis
            if indicator_data and self._indicator_processor:
                indicator_analysis = self._analyze_indicators(indicator_data)
            else:
                indicator_analysis = self._get_default_indicator_analysis()

            # Integrate based on mode
            if self._integration_mode == IntegrationMode.WORLD_ENHANCED_INDICATORS:
                integrated_analysis = self._world_enhanced_indicators(
                    world_analysis, indicator_analysis
                )
            elif self._integration_mode == IntegrationMode.INDICATOR_VALIDATED_WORLD:
                integrated_analysis = self._indicator_validated_world(
                    world_analysis, indicator_analysis
                )
            elif self._integration_mode == IntegrationMode.HYBRID_DECISION_FUSION:
                integrated_analysis = self._hybrid_decision_fusion(
                    world_analysis, indicator_analysis, market_data
                )
            else:
                integrated_analysis = self._adaptive_weighting(world_analysis, indicator_analysis)

            # Set meta information
            integrated_analysis.analysis_timestamp = datetime.now()
            integrated_analysis.integration_mode = self._integration_mode

            # Validate analysis
            integrated_analysis.validation_status = self._validate_analysis(integrated_analysis)

            # Update metrics
            processing_time_ms = (datetime.now() - start_time).total_seconds() * 1000
            self._update_metrics(integrated_analysis, processing_time_ms)

            # Store in history
            with self._lock:
                self._analysis_history.append(integrated_analysis)
                if len(self._analysis_history) > 1000:
                    self._analysis_history = self._analysis_history[-1000:]

            logger.info(
                f"[WORLD_INDICATOR_COORDINATOR] Integrated analysis completed: {integrated_analysis.integrated_decision} (confidence: {integrated_analysis.integrated_confidence:.2f})"
            )

            return integrated_analysis

        except Exception as e:
            logger.error(f"Error in integrated market analysis: {e}")
            # Return fallback analysis
            return self._get_fallback_analysis(market_data)

    def _analyze_world_context(self, world_context: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze world context from world model."""
        try:
            # Extract world understanding from context
            world_regime = world_context.get("market_regime", "neutral")
            world_trend = world_context.get("market_trend", "sideways")
            world_confidence = world_context.get("prediction_confidence", 0.5)

            # Analyze agent activity
            agent_activity = world_context.get("agent_activity", {})
            dominant_agents = self._identify_dominant_agents(agent_activity)

            # Analyze causal factors
            causal_factors = world_context.get("causal_factors", [])

            return {
                "regime": world_regime,
                "trend": world_trend,
                "confidence": world_confidence,
                "agent_activity": agent_activity,
                "dominant_agents": dominant_agents,
                "causal_factors": causal_factors,
                "environment_conditions": world_context.get("environment_conditions", {}),
            }

        except Exception as e:
            logger.error(f"Error analyzing world context: {e}")
            return self._get_default_world_analysis()

    def _analyze_indicators(self, indicator_data: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze indicator signals."""
        try:
            # Extract indicator values and calculate composite signal
            indicator_signals = {}
            total_signal = 0.0
            signal_count = 0

            for indicator_name, indicator_value in indicator_data.items():
                if isinstance(indicator_value, (int, float)):
                    indicator_signals[indicator_name] = indicator_value
                    total_signal += indicator_value
                    signal_count += 1

            # Calculate indicator confidence
            if signal_count > 0:
                avg_signal = total_signal / signal_count
                indicator_confidence = min(abs(avg_signal) / 10.0, 1.0)  # Normalize
            else:
                indicator_confidence = 0.5

            return {
                "signals": indicator_signals,
                "composite_signal": avg_signal if signal_count > 0 else 0.0,
                "confidence": indicator_confidence,
                "signal_count": signal_count,
            }

        except Exception as e:
            logger.error(f"Error analyzing indicators: {e}")
            return self._get_default_indicator_analysis()

    def _world_enhanced_indicators(
        self,
        world_analysis: Dict[str, Any],
        indicator_analysis: Dict[str, Any],
    ) -> IntegratedMarketAnalysis:
        """World model enhances indicator processing."""
        # World context adjusts indicator interpretation
        regime_adjustments = {
            "bullish": 1.2,  # Amplify signals in bull markets
            "bearish": -1.2,  # Invert signals in bear markets
            "sideways": 1.0,  # Normal in sideways
            "high_volatility": 0.7,  # Reduce signal strength in high vol
            "low_volatility": 1.3,  # Amplify signals in low vol
        }

        regime = world_analysis["regime"]
        adjustment_factor = regime_adjustments.get(regime, 1.0)

        # Adjust indicator signals
        enhanced_signals = {}
        for indicator_name, signal_value in indicator_analysis["signals"].items():
            enhanced_signals[indicator_name] = signal_value * adjustment_factor

        # Calculate integrated decision
        composite_signal = (
            sum(enhanced_signals.values()) / len(enhanced_signals) if enhanced_signals else 0.0
        )
        world_confidence = world_analysis["confidence"]
        indicator_confidence = indicator_analysis["confidence"]

        # Weighted decision
        integrated_decision = self._signal_to_decision(composite_signal)
        integrated_confidence = (world_confidence * 0.6) + (indicator_confidence * 0.4)

        # Contribution analysis
        world_contribution = world_confidence * 0.7
        indicator_contribution = indicator_confidence * 0.3

        return IntegratedMarketAnalysis(
            world_regime=regime,
            world_trend=world_analysis["trend"],
            world_confidence=world_confidence,
            indicator_signals=enhanced_signals,
            indicator_confidence=indicator_confidence,
            integrated_decision=integrated_decision,
            integrated_confidence=integrated_confidence,
            integration_mode=IntegrationMode.WORLD_ENHANCED_INDICATORS,
            world_contribution=world_contribution,
            indicator_contribution=indicator_contribution,
        )

    def _indicator_validated_world(
        self,
        world_analysis: Dict[str, Any],
        indicator_analysis: Dict[str, Any],
    ) -> IntegratedMarketAnalysis:
        """Indicators validate world model predictions."""
        # Indicators check world model predictions
        world_prediction = world_analysis["regime"]
        indicator_composite = indicator_analysis["composite_signal"]

        # Check alignment
        alignment = self._check_prediction_indicator_alignment(
            world_prediction, indicator_composite
        )

        # Adjust world confidence based on indicator validation
        if alignment > 0.7:
            validated_world_confidence = min(world_analysis["confidence"] * 1.2, 1.0)
        elif alignment < -0.7:
            validated_world_confidence = max(world_analysis["confidence"] * 0.8, 0.0)
        else:
            validated_world_confidence = world_analysis["confidence"]

        # Decision based on validated world understanding
        integrated_decision = self._regime_to_decision(world_prediction)
        integrated_confidence = (validated_world_confidence * 0.7) + (
            indicator_analysis["confidence"] * 0.3
        )

        return IntegratedMarketAnalysis(
            world_regime=world_analysis["regime"],
            world_trend=world_analysis["trend"],
            world_confidence=validated_world_confidence,
            indicator_signals=indicator_analysis["signals"],
            indicator_confidence=indicator_analysis["confidence"],
            integrated_decision=integrated_decision,
            integrated_confidence=integrated_confidence,
            integration_mode=IntegrationMode.INDICATOR_VALIDATED_WORLD,
            world_contribution=validated_world_confidence * 0.8,
            indicator_contribution=indicator_analysis["confidence"] * 0.2,
        )

    def _hybrid_decision_fusion(
        self,
        world_analysis: Dict[str, Any],
        indicator_analysis: Dict[str, Any],
        market_data: Dict[str, Any],
    ) -> IntegratedMarketAnalysis:
        """Fuse world and indicator decisions."""
        # Get world decision
        world_decision = self._regime_to_decision(world_analysis["regime"])
        world_confidence = world_analysis["confidence"]

        # Get indicator decision
        indicator_decision = self._signal_to_decision(indicator_analysis["composite_signal"])
        indicator_confidence = indicator_analysis["confidence"]

        # Fuse decisions based on confidence
        if world_confidence > indicator_confidence:
            integrated_decision = world_decision
            integrated_confidence = world_confidence
            world_contribution = 0.7
            indicator_contribution = 0.3
        elif indicator_confidence > world_confidence:
            integrated_decision = indicator_decision
            integrated_confidence = indicator_confidence
            world_contribution = 0.3
            indicator_contribution = 0.7
        else:
            # Equal confidence - balanced approach
            integrated_decision = self._resolve_equal_confidence(
                world_decision, indicator_decision, market_data
            )
            integrated_confidence = (world_confidence + indicator_confidence) / 2
            world_contribution = 0.5
            indicator_contribution = 0.5

        return IntegratedMarketAnalysis(
            world_regime=world_analysis["regime"],
            world_trend=world_analysis["trend"],
            world_confidence=world_confidence,
            indicator_signals=indicator_analysis["signals"],
            indicator_confidence=indicator_confidence,
            integrated_decision=integrated_decision,
            integrated_confidence=integrated_confidence,
            integration_mode=IntegrationMode.HYBRID_DECISION_FUSION,
            world_contribution=world_contribution,
            indicator_contribution=indicator_contribution,
        )

    def _adaptive_weighting(
        self,
        world_analysis: Dict[str, Any],
        indicator_analysis: Dict[str, Any],
    ) -> IntegratedMarketAnalysis:
        """Adaptively weight world and indicators based on performance."""
        # Calculate performance-based weights
        world_performance = self._get_world_performance_metric()
        indicator_performance = self._get_indicator_performance_metric()

        # Normalize weights
        total_performance = world_performance + indicator_performance
        world_weight = world_performance / total_performance if total_performance > 0 else 0.5
        indicator_weight = (
            indicator_performance / total_performance if total_performance > 0 else 0.5
        )

        # Calculate weighted decision
        world_decision = self._regime_to_decision(world_analysis["regime"])
        indicator_decision = self._signal_to_decision(indicator_analysis["composite_signal"])

        # Weight decision combination
        integrated_decision = self._weight_decisions(
            world_decision, indicator_decision, world_weight, indicator_weight
        )

        integrated_confidence = (
            world_analysis["confidence"] * world_weight
            + indicator_analysis["confidence"] * indicator_weight
        )

        return IntegratedMarketAnalysis(
            world_regime=world_analysis["regime"],
            world_trend=world_analysis["trend"],
            world_confidence=world_analysis["confidence"],
            indicator_signals=indicator_analysis["signals"],
            indicator_confidence=indicator_analysis["confidence"],
            integrated_decision=integrated_decision,
            integrated_confidence=integrated_confidence,
            integration_mode=IntegrationMode.ADAPTIVE_WEIGHTING,
            world_contribution=world_weight,
            indicator_contribution=indicator_weight,
        )

    # Helper methods
    def _get_default_world_analysis(self) -> Dict[str, Any]:
        """Get default world analysis when world model unavailable."""
        return {
            "regime": "neutral",
            "trend": "sideways",
            "confidence": 0.5,
            "agent_activity": {},
            "dominant_agents": [],
            "causal_factors": [],
            "environment_conditions": {},
        }

    def _get_default_indicator_analysis(self) -> Dict[str, Any]:
        """Get default indicator analysis when indicators unavailable."""
        return {
            "signals": {},
            "composite_signal": 0.0,
            "confidence": 0.5,
            "signal_count": 0,
        }

    def _get_fallback_analysis(self, market_data: Dict[str, Any]) -> IntegratedMarketAnalysis:
        """Get fallback analysis when integration fails."""
        return IntegratedMarketAnalysis(
            world_regime="neutral",
            world_trend="sideways",
            world_confidence=0.5,
            indicator_signals={},
            indicator_confidence=0.5,
            integrated_decision="hold",
            integrated_confidence=0.3,
            integration_mode=IntegrationMode.HYBRID_DECISION_FUSION,
            world_contribution=0.5,
            indicator_contribution=0.5,
            validation_status="fallback",
        )

    def _identify_dominant_agents(self, agent_activity: Dict[str, float]) -> List[str]:
        """Identify dominant market agents from activity data."""
        if not agent_activity:
            return []

        # Sort by activity level
        sorted_agents = sorted(agent_activity.items(), key=lambda x: x[1], reverse=True)

        # Return top agents
        return [agent[0] for agent in sorted_agents[:3]]

    def _signal_to_decision(self, signal: float) -> str:
        """Convert signal value to trading decision."""
        if signal > 0.5:
            return "buy"
        elif signal < -0.5:
            return "sell"
        else:
            return "hold"

    def _regime_to_decision(self, regime: str) -> str:
        """Convert regime to trading decision."""
        regime_decisions = {
            "bullish": "buy",
            "bearish": "sell",
            "sideways": "hold",
            "high_volatility": "hold",
            "low_volatility": "buy",
        }
        return regime_decisions.get(regime.lower(), "hold")

    def _check_prediction_indicator_alignment(
        self, prediction: str, indicator_signal: float
    ) -> float:
        """Check alignment between world prediction and indicator signal."""
        prediction_direction = (
            1.0
            if prediction.lower() in ["bullish", "buy", "positive"]
            else (-1.0 if prediction.lower() in ["bearish", "sell", "negative"] else 0.0)
        )

        # Normalize indicator signal
        normalized_signal = max(min(indicator_signal / 10.0, 1.0), -1.0)

        # Calculate alignment (both pointing same direction = high alignment)
        alignment = prediction_direction * normalized_signal

        return alignment

    def _resolve_equal_confidence(
        self,
        world_decision: str,
        indicator_decision: str,
        market_data: Dict[str, Any],
    ) -> str:
        """Resolve decision when world and indicators have equal confidence."""
        # Prefer world understanding in volatile markets
        if market_data.get("volatility", 0) > 0.3:
            return world_decision
        else:
            # Prefer indicators in stable markets
            return indicator_decision

    def _weight_decisions(
        self,
        world_decision: str,
        indicator_decision: str,
        world_weight: float,
        indicator_weight: float,
    ) -> str:
        """Weight decision combination based on weights."""
        decisions = {
            "buy": 1.0,
            "sell": -1.0,
            "hold": 0.0,
        }

        world_value = decisions.get(world_decision, 0.0) * world_weight
        indicator_value = decisions.get(indicator_decision, 0.0) * indicator_weight

        combined_value = world_value + indicator_value

        if combined_value > 0.3:
            return "buy"
        elif combined_value < -0.3:
            return "sell"
        else:
            return "hold"

    def _get_world_performance_metric(self) -> float:
        """Get world model performance metric from history."""
        with self._lock:
            if not self._analysis_history:
                return 0.5

            # Calculate world contribution performance
            world_contributions = [
                analysis.world_contribution
                for analysis in self._analysis_history[-50:]  # Last 50 analyses
            ]

            if world_contributions:
                avg_world_contribution = sum(world_contributions) / len(world_contributions)
                # Higher contribution = better performance
                return avg_world_contribution

            return 0.5

    def _get_indicator_performance_metric(self) -> float:
        """Get indicator performance metric from history."""
        with self._lock:
            if not self._analysis_history:
                return 0.5

            # Calculate indicator contribution performance
            indicator_contributions = [
                analysis.indicator_contribution
                for analysis in self._analysis_history[-50:]  # Last 50 analyses
            ]

            if indicator_contributions:
                avg_indicator_contribution = sum(indicator_contributions) / len(
                    indicator_contributions
                )
                # Higher contribution = better performance
                return avg_indicator_contribution

            return 0.5

    def _validate_analysis(self, analysis: IntegratedMarketAnalysis) -> str:
        """Validate integrated analysis for conflicts or uncertainty."""
        # Check for decision confidence
        if analysis.integrated_confidence < 0.4:
            return "uncertain"

        # Check for world-indicator conflict
        if analysis.world_contribution > 0.6 and analysis.indicator_contribution > 0.6:
            # Both strongly contributing but may conflict
            if analysis.world_regime in ["bullish", "bearish"]:
                # Check if decision aligns with regime
                regime_expected = self._regime_to_decision(analysis.world_regime)
                if analysis.integrated_decision != regime_expected:
                    return "conflicted"

        return "valid"

    def _update_metrics(
        self,
        analysis: IntegratedMarketAnalysis,
        processing_time_ms: float,
    ) -> None:
        """Update performance metrics."""
        with self._lock:
            self._metrics.total_integrations += 1

            if analysis.validation_status == "valid":
                self._metrics.successful_integrations += 1

            if analysis.validation_status == "conflicted":
                self._metrics.conflict_count += 1

            # Update average confidence
            if self._metrics.total_integrations == 1:
                self._metrics.average_confidence = analysis.integrated_confidence
            else:
                self._metrics.average_confidence = (
                    0.95 * self._metrics.average_confidence + 0.05 * analysis.integrated_confidence
                )

            # Update average processing time
            if self._metrics.total_integrations == 1:
                self._metrics.average_processing_time_ms = processing_time_ms
            else:
                self._metrics.average_processing_time_ms = (
                    0.9 * self._metrics.average_processing_time_ms + 0.1 * processing_time_ms
                )

            # Update mode-specific performance
            mode = analysis.integration_mode.value
            if mode not in self._metrics.mode_performance:
                self._metrics.mode_performance[mode] = {}

            self._metrics.mode_performance[mode]["count"] = (
                self._metrics.mode_performance[mode].get("count", 0) + 1
            )
            self._metrics.mode_performance[mode]["avg_confidence"] = (
                self._metrics.mode_performance[mode].get("avg_confidence", 0.5) * 0.9
                + analysis.integrated_confidence * 0.1
            )

    def get_performance_metrics(self) -> IntegrationPerformanceMetrics:
        """Get current performance metrics."""
        with self._lock:
            return self._metrics

    def get_analysis_summary(self) -> Dict[str, Any]:
        """Get summary of recent analyses."""
        with self._lock:
            if not self._analysis_history:
                return {"message": "No analysis history available"}

            recent_analyses = self._analysis_history[-10:]

            return {
                "recent_decisions": [analysis.integrated_decision for analysis in recent_analyses],
                "average_confidence": sum(
                    analysis.integrated_confidence for analysis in recent_analyses
                )
                / len(recent_analyses),
                "decision_distribution": self._count_decision_distribution(recent_analyses),
                "mode_distribution": self._count_mode_distribution(recent_analyses),
                "validation_status_distribution": self._count_validation_status_distribution(
                    recent_analyses
                ),
                "timestamp": datetime.now().isoformat(),
            }

    def _count_decision_distribution(
        self, analyses: List[IntegratedMarketAnalysis]
    ) -> Dict[str, int]:
        """Count distribution of decisions in analyses."""
        distribution = {"buy": 0, "sell": 0, "hold": 0}
        for analysis in analyses:
            decision = analysis.integrated_decision
            if decision in distribution:
                distribution[decision] += 1
        return distribution

    def _count_mode_distribution(self, analyses: List[IntegratedMarketAnalysis]) -> Dict[str, int]:
        """Count distribution of integration modes used."""
        distribution = {}
        for analysis in analyses:
            mode = analysis.integration_mode.value
            distribution[mode] = distribution.get(mode, 0) + 1
        return distribution

    def _count_validation_status_distribution(
        self, analyses: List[IntegratedMarketAnalysis]
    ) -> Dict[str, int]:
        """Count distribution of validation statuses."""
        distribution = {"valid": 0, "conflicted": 0, "uncertain": 0}
        for analysis in analyses:
            status = analysis.validation_status
            if status in distribution:
                distribution[status] += 1
        return distribution


# Singleton instance
_coordinator_instance = None
_coordinator_lock = threading.Lock()


def get_world_indicator_coordinator() -> WorldIndicatorCoordinator:
    """Get the singleton world-indicator coordinator instance."""
    global _coordinator_instance
    if _coordinator_instance is None:
        with _coordinator_lock:
            if _coordinator_instance is None:
                _coordinator_instance = WorldIndicatorCoordinator()
    return _coordinator_instance


__all__ = [
    "IntegrationMode",
    "IntegratedMarketAnalysis",
    "IntegrationPerformanceMetrics",
    "WorldIndicatorCoordinator",
    "get_world_indicator_coordinator",
]
