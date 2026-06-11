"""LEARNING-01 — Performance attribution and adaptive learning.

Enhances INDIRA's learning capabilities with performance attribution,
decision quality analysis, and adaptive parameter optimization.

Pure computation. No clocks, no I/O. INV-15 deterministic.
B1: No imports from execution_engine/governance_engine/learning_engine/evolution_engine.
"""

from __future__ import annotations

import math
from dataclasses import dataclass
from typing import Any
from collections import deque
from enum import Enum


class AttributionType(Enum):
    """Types of performance attribution."""
    SIGNAL_QUALITY = "signal_quality"
    EXECUTION_QUALITY = "execution_quality"
    TIMING = "timing"
    POSITION_SIZING = "position_sizing"
    RISK_MANAGEMENT = "risk_management"
    MARKET_REGIME = "market_regime"


@dataclass(frozen=True, slots=True)
class DecisionAttribution:
    """Attribution of a decision to its outcome."""
    decision_id: str
    decision_type: str
    outcome: str  # "success", "failure", "partial"
    attribution_breakdown: dict[AttributionType, float]  # Contribution of each factor
    total_attribution: float  # Sum of attributions
    confidence_attribution: float  # How confidence affected outcome
    timing_attribution: float  # How timing affected outcome
    key_learnings: tuple[str, ...]
    timestamp_ns: int


@dataclass(frozen=True, slots=True)
class PerformanceMetric:
    """Performance metric for tracking."""
    metric_name: str
    metric_value: float
    target_value: float
    trend: str  # "improving", "stable", "declining"
    historical_values: tuple[float, ...]
    attribution_factors: tuple[str, ...]  # Factors influencing this metric
    last_updated_ns: int


@dataclass(frozen=True, slots=True)
class LearningInsight:
    """Insight derived from performance analysis."""
    insight_id: str
    insight_type: str  # "pattern", "correlation", "opportunity", "risk"
    confidence: float  # Confidence in the insight
    actionability: float  # How actionable the insight is
    description: str
    suggested_actions: tuple[str, ...]
    expected_improvement: float  # Expected improvement if acted upon
    timestamp_ns: int


class PerformanceAttributor:
    """Attributes performance to decision factors.
    
    Analyzes decision outcomes to understand what contributed to
    success or failure, enabling targeted improvements.
    """
    
    def __init__(self, attribution_window: int = 100) -> None:
        self._attribution_window = attribution_window
        
        self._decision_history: deque[dict[str, Any]] = deque(maxlen=attribution_window)
        self._attribution_patterns: dict[str, dict[str, float]] = {}
        
    def attribute_decision(
        self,
        decision_id: str,
        decision_type: str,
        context: dict[str, Any],
        outcome: str,
        outcome_value: float,  # e.g., profit/loss
        timestamp_ns: int = 0
    ) -> DecisionAttribution:
        """Attribute decision outcome to contributing factors.
        
        Args:
            decision_id: Unique decision identifier
            decision_type: Type of decision
            context: Decision context
            outcome: Outcome type
            outcome_value: Quantitative outcome value
            timestamp_ns: Decision timestamp
            
        Returns:
            Decision attribution breakdown
        """
        # Extract key factors from context
        signal_confidence = context.get("signal_confidence", 0.5)
        execution_quality = context.get("execution_quality", 0.8)
        timing_score = context.get("timing_score", 0.5)
        position_size = context.get("position_size", 1.0)
        risk_level = context.get("risk_level", 0.5)
        market_regime = context.get("market_regime", "neutral")
        
        # Calculate attributions based on outcome
        attributions = {}
        
        if outcome == "success":
            # Positive attributions for success
            attributions[AttributionType.SIGNAL_QUALITY] = signal_confidence * 0.3
            attributions[AttributionType.EXECUTION_QUALITY] = execution_quality * 0.2
            attributions[AttributionType.TIMING] = timing_score * 0.2
            attributions[AttributionType.POSITION_SIZING] = min(1.0, position_size / 2.0) * 0.15
            attributions[AttributionType.RISK_MANAGEMENT] = (1.0 - risk_level) * 0.1
            attributions[AttributionType.MARKET_REGIME] = 0.3 if market_regime == "favorable" else 0.1
        else:
            # Negative attributions for failure
            attributions[AttributionType.SIGNAL_QUALITY] = (1.0 - signal_confidence) * -0.3
            attributions[AttributionType.EXECUTION_QUALITY] = (1.0 - execution_quality) * -0.2
            attributions[AttributionType.TIMING] = (1.0 - timing_score) * -0.2
            attributions[AttributionType.POSITION_SIZING] = -min(1.0, position_size / 2.0) * 0.15
            attributions[AttributionType.RISK_MANAGEMENT] = -(risk_level) * 0.1
            attributions[AttributionType.MARKET_REGIME] = -0.3 if market_regime == "unfavorable" else 0.0
        
        total_attribution = sum(abs(v) for v in attributions.values())
        
        # Generate key learnings
        key_learnings = self._generate_learnings(attributions, context, outcome)
        
        attribution = DecisionAttribution(
            decision_id=decision_id,
            decision_type=decision_type,
            outcome=outcome,
            attribution_breakdown=attributions,
            total_attribution=total_attribution,
            confidence_attribution=attributions.get(AttributionType.SIGNAL_QUALITY, 0.0),
            timing_attribution=attributions.get(AttributionType.TIMING, 0.0),
            key_learnings=tuple(key_learnings),
            timestamp_ns=timestamp_ns
        )
        
        # Store in history
        self._decision_history.append({
            "decision_id": decision_id,
            "decision_type": decision_type,
            "context": context,
            "outcome": outcome,
            "outcome_value": outcome_value,
            "attribution": attribution,
            "timestamp_ns": timestamp_ns
        })
        
        # Update attribution patterns
        self._update_attribution_patterns(decision_type, attributions)
        
        return attribution
    
    def _generate_learnings(
        self,
        attributions: dict[AttributionType, float],
        context: dict[str, Any],
        outcome: str
    ) -> list[str]:
        """Generate key learnings from attribution."""
        learnings = []
        
        # Find strongest contributing factors
        sorted_attributions = sorted(attributions.items(), key=lambda x: abs(x[1]), reverse=True)
        
        if outcome == "success":
            for attr_type, value in sorted_attributions[:3]:
                if value > 0.2:
                    learnings.append(f"Strong positive contribution from {attr_type.value}")
        else:
            for attr_type, value in sorted_attributions[:3]:
                if value < -0.2:
                    learnings.append(f"Negative impact from {attr_type.value}")
        
        # Add regime-specific learning
        market_regime = context.get("market_regime", "neutral")
        if market_regime != "neutral":
            if outcome == "success":
                learnings.append(f"Favorable regime alignment: {market_regime}")
            else:
                learnings.append(f"Unfavorable regime alignment: {market_regime}")
        
        return learnings if learnings else ["No clear attribution factors identified"]
    
    def _update_attribution_patterns(
        self,
        decision_type: str,
        attributions: dict[AttributionType, float]
    ) -> None:
        """Update attribution patterns for a decision type."""
        if decision_type not in self._attribution_patterns:
            self._attribution_patterns[decision_type] = {}
        
        for attr_type, value in attributions.items():
            if attr_type not in self._attribution_patterns[decision_type]:
                self._attribution_patterns[decision_type][attr_type] = []
            self._attribution_patterns[decision_type][attr_type].append(value)
    
    def get_attribution_patterns(self, decision_type: str) -> dict[AttributionType, tuple[float, ...]]:
        """Get historical attribution patterns for a decision type."""
        if decision_type not in self._attribution_patterns:
            return {}
        
        patterns = {}
        for attr_type, values in self._attribution_patterns[decision_type].items():
            if values:
                patterns[attr_type] = tuple(values[-20:])  # Last 20 values
            else:
                patterns[attr_type] = ()
        
        return patterns


class AdaptiveLearningEngine:
    """Adaptive learning engine for continuous improvement.
    
    Learns from performance data to optimize parameters and strategies.
    """
    
    def __init__(self, learning_rate: float = 0.05) -> None:
        self._learning_rate = learning_rate
        
        self._performance_metrics: dict[str, PerformanceMetric] = {}
        self._learning_insights: deque[LearningInsight] = deque(maxlen=50)
        self._parameter_adjustments: dict[str, float] = {}
        
    def update_performance_metric(
        self,
        metric_name: str,
        metric_value: float,
        target_value: float,
        attribution_factors: tuple[str, ...] = (),
        timestamp_ns: int = 0
    ) -> None:
        """Update a performance metric.
        
        Args:
            metric_name: Metric name
            metric_value: Current metric value
            target_value: Target value
            attribution_factors: Factors influencing this metric
            timestamp_ns: Timestamp
        """
        if metric_name not in self._performance_metrics:
            self._performance_metrics[metric_name] = PerformanceMetric(
                metric_name=metric_name,
                metric_value=metric_value,
                target_value=target_value,
                trend="stable",
                historical_values=(metric_value,),
                attribution_factors=attribution_factors,
                last_updated_ns=timestamp_ns
            )
        else:
            old_metric = self._performance_metrics[metric_name]
            
            # Determine trend
            if len(old_metric.historical_values) >= 3:
                recent = old_metric.historical_values[-3:]
                if recent[-1] > recent[-2] > recent[-3]:
                    trend = "improving"
                elif recent[-1] < recent[-2] < recent[-3]:
                    trend = "declining"
                else:
                    trend = "stable"
            else:
                trend = "stable"
            
            # Update historical values
            historical_values = old_metric.historical_values + (metric_value,)
            
            self._performance_metrics[metric_name] = PerformanceMetric(
                metric_name=metric_name,
                metric_value=metric_value,
                target_value=target_value,
                trend=trend,
                historical_values=historical_values[-50:],  # Keep last 50
                attribution_factors=attribution_factors,
                last_updated_ns=timestamp_ns
            )
    
    def generate_insights(self, timestamp_ns: int = 0) -> tuple[LearningInsight, ...]:
        """Generate learning insights from performance metrics.
        
        Args:
            timestamp_ns: Current timestamp
            
        Returns:
            Tuple of generated insights
        """
        insights = []
        
        # Analyze each performance metric
        for metric_name, metric in self._performance_metrics.items():
            gap = metric.target_value - metric.metric_value
            
            if gap > 0.1:  # Significant gap from target
                if metric.trend == "improving":
                    insight_type = "opportunity"
                    confidence = 0.7
                    actionability = 0.8
                    description = f"{metric_name} is improving but still {gap:.1%} below target"
                    suggested_actions = ("continue_current_strategy", "accelerate_improvement")
                    expected_improvement = gap * 0.5
                elif metric.trend == "declining":
                    insight_type = "risk"
                    confidence = 0.9
                    actionability = 0.9
                    description = f"{metric_name} is declining and {gap:.1%} below target"
                    suggested_actions = ("strategy_adjustment", "parameter_optimization")
                    expected_improvement = gap * 0.3
                else:
                    insight_type = "opportunity"
                    confidence = 0.6
                    actionability = 0.7
                    description = f"{metric_name} is stable but {gap:.1%} below target"
                    suggested_actions = ("incremental_improvement", "parameter_fine_tuning")
                    expected_improvement = gap * 0.4
            elif gap < -0.05:  # Exceeding target
                insight_type = "pattern"
                confidence = 0.5
                actionability = 0.6
                description = f"{metric_name} exceeds target by {-gap:.1%}"
                suggested_actions = ("maintain_current_strategy", "raise_target")
                expected_improvement = 0.0
            else:  # At or near target
                insight_type = "pattern"
                confidence = 0.8
                actionability = 0.3
                description = f"{metric_name} is at target level"
                suggested_actions = ("maintain_strategy", "monitor_continuously")
                expected_improvement = 0.0
                
                insight = LearningInsight(
                    insight_id=f"insight_{metric_name}_{timestamp_ns}",
                    insight_type=insight_type,
                    confidence=confidence,
                    actionability=actionability,
                    description=description,
                    suggested_actions=suggested_actions,
                    expected_improvement=expected_improvement,
                    timestamp_ns=timestamp_ns
                )
                
                insights.append(insight)
        
        # Store insights
        for insight in insights:
            self._learning_insights.append(insight)
        
        return tuple(insights)
    
    def calculate_parameter_adjustment(
        self,
        parameter_name: str,
        current_value: float,
        performance_feedback: dict[str, float]
    ) -> float:
        """Calculate parameter adjustment based on performance feedback.
        
        Args:
            parameter_name: Parameter to adjust
            current_value: Current parameter value
            performance_feedback: Performance feedback signals
            
        Returns:
            Adjusted parameter value
        """
        # Calculate adjustment direction and magnitude
        adjustment = 0.0
        
        for metric_name, feedback in performance_feedback.items():
            if metric_name in self._performance_metrics:
                metric = self._performance_metrics[metric_name]
                gap = metric.target_value - metric.metric_value
                
                # Adjust in direction to close gap
                if gap > 0:
                    adjustment += gap * self._learning_rate
                elif gap < 0:
                    adjustment -= abs(gap) * self._learning_rate * 0.5  # More conservative on overshoot
        
        # Apply adjustment with bounds
        new_value = current_value + adjustment
        
        # Ensure reasonable bounds
        if parameter_name == "confidence_threshold":
            new_value = max(0.1, min(0.9, new_value))
        elif parameter_name == "position_size_multiplier":
            new_value = max(0.5, min(2.0, new_value))
        elif parameter_name == "risk_aversion":
            new_value = max(0.1, min(0.9, new_value))
        else:
            new_value = max(0.0, min(1.0, new_value))  # General normalization
        
        # Store adjustment
        self._parameter_adjustments[parameter_name] = new_value
        
        return new_value
    
    def get_parameter_adjustments(self) -> dict[str, float]:
        """Get current parameter adjustments."""
        return dict(self._parameter_adjustments)
    
    def get_performance_summary(self) -> dict[str, Any]:
        """Get summary of performance metrics."""
        summary = {}
        
        for metric_name, metric in self._performance_metrics.items():
            summary[metric_name] = {
                "current_value": metric.metric_value,
                "target_value": metric.target_value,
                "gap": metric.target_value - metric.metric_value,
                "trend": metric.trend,
                "gap_percentage": abs(metric.target_value - metric.metric_value) / metric.target_value if metric.target_value > 0 else 0.0
            }
        
        return summary
    
    def get_recent_insights(self, limit: int = 10) -> tuple[LearningInsight, ...]:
        """Get recent learning insights."""
        return tuple(list(self._learning_insights)[-limit:])


__all__ = [
    "AttributionType",
    "DecisionAttribution",
    "PerformanceMetric",
    "LearningInsight",
    "PerformanceAttributor",
    "AdaptiveLearningEngine"
]