"""
evolution_engine.predictive.evolution_forecasting
DIX VISION v42.2 — Predictive Evolution Planning (Priority 2)

Provides predictive system evolution planning based on system trends and requirements.
This is a Priority 2 enhancement for proactive system evolution.
"""

from __future__ import annotations

import logging
import threading
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional

logger = logging.getLogger(__name__)


class TrendDirection(Enum):
    """Direction of trend."""

    INCREASING = "INCREASING"
    DECREASING = "DECREASING"
    STABLE = "STABLE"
    VOLATILE = "VOLATILE"


@dataclass
class TrendAnalysis:
    """Analysis of a system trend."""

    metric_name: str
    direction: TrendDirection
    current_value: float
    historical_values: List[float] = field(default_factory=list)
    forecast_values: List[float] = field(default_factory=list)
    confidence: float = 0.0  # 0.0 to 1.0
    trend_strength: float = 0.0  # 0.0 to 1.0


@dataclass
class RequirementPrediction:
    """Predicted future requirement."""

    requirement_type: str  # PERFORMANCE, SECURITY, SCALABILITY, FEATURE
    description: str
    importance: str  # LOW, MEDIUM, HIGH, CRITICAL
    time_horizon_months: int
    probability: float = 0.0  # 0.0 to 1.0
    estimated_effort_months: float = 0.0


@dataclass
class CapabilityGap:
    """Gap between current capabilities and future requirements."""

    capability_name: str
    current_status: str
    required_status: str
    gap_severity: str  # LOW, MEDIUM, HIGH, CRITICAL
    closure_complexity: str  # LOW, MEDIUM, HIGH
    estimated_closure_time_months: float = 0.0
    priority: int = 0  # Higher is more important


@dataclass
class EvolutionPlan:
    """Plan for system evolution."""

    plan_id: str
    plan_name: str
    time_horizon_months: int
    predicted_gaps: List[CapabilityGap] = field(default_factory=list)
    predicted_requirements: List[RequirementPrediction] = field(default_factory=list)
    recommended_actions: List[str] = field(default_factory=list)
    resource_estimates: Dict[str, float] = field(default_factory=dict)
    confidence_level: float = 0.0
    risk_assessment: str = "MEDIUM"
    creation_date: datetime = field(default_factory=datetime.utcnow)


@dataclass
class EvolutionForecast:
    """Comprehensive evolution forecast."""

    evolution_plans: List[EvolutionPlan]
    trend_analyses: Dict[str, TrendAnalysis]
    confidence_level: float
    resource_requirements: Dict[str, float]
    recommended_timeline: str


class SystemTrendAnalyzer:
    """Analyzes system trends for predictive evolution."""

    def __init__(self):
        self._lock = threading.Lock()
        self._historical_data: Dict[str, List[float]] = {}
        self._trend_window_size = 10  # Number of data points for trend analysis

        logger.info("[TREND_ANALYZER] Initialized with window size: {self._trend_window_size}")

    def analyze(
        self, current_metrics: Dict[str, float], time_horizon_months: int = 6
    ) -> Dict[str, TrendAnalysis]:
        """
        Analyze system trends based on current metrics.

        Args:
            current_metrics: Current system metrics
            time_horizon_months: Time horizon for trend forecasting

        Returns:
            Trend analysis for each metric
        """
        with self._lock:
            trend_analyses = {}

            for metric_name, current_value in current_metrics.items():
                # Add current value to historical data
                if metric_name not in self._historical_data:
                    self._historical_data[metric_name] = []
                self._historical_data[metric_name].append(current_value)

                # Keep only recent data
                if len(self._historical_data[metric_name]) > self._trend_window_size:
                    self._historical_data[metric_name] = self._historical_data[metric_name][
                        -self._trend_window_size :
                    ]

                # Analyze trend
                historical = self._historical_data[metric_name]
                if len(historical) >= 3:
                    direction = self._determine_direction(historical)
                    confidence = self._calculate_confidence(historical)
                    strength = self._calculate_strength(historical)
                    forecast = self._forecast_trend(historical, time_horizon_months)
                else:
                    direction = TrendDirection.STABLE
                    confidence = 0.5
                    strength = 0.0
                    forecast = []

                trend_analyses[metric_name] = TrendAnalysis(
                    metric_name=metric_name,
                    direction=direction,
                    current_value=current_value,
                    historical_values=historical,
                    forecast_values=forecast,
                    confidence=confidence,
                    trend_strength=strength,
                )

            return trend_analyses

    def _determine_direction(self, values: List[float]) -> TrendDirection:
        """Determine trend direction."""
        if len(values) < 2:
            return TrendDirection.STABLE

        # Calculate trend
        recent = values[-3:]
        earlier = values[-6:-3] if len(values) >= 6 else values[:-3]

        if not earlier:
            return TrendDirection.STABLE

        recent_avg = sum(recent) / len(recent)
        earlier_avg = sum(earlier) / len(earlier)

        if recent_avg > earlier_avg * 1.05:
            return TrendDirection.INCREASING
        elif recent_avg < earlier_avg * 0.95:
            return TrendDirection.DECREASING
        else:
            # Check for volatility
            variance = max(values) - min(values)
            if variance > recent_avg * 0.3:
                return TrendDirection.VOLATILE
            else:
                return TrendDirection.STABLE

    def _calculate_confidence(self, values: List[float]) -> float:
        """Calculate confidence in trend analysis."""
        if len(values) < 3:
            return 0.3

        # More data points = higher confidence
        confidence = min(len(values) / self._trend_window_size, 1.0)

        # Lower volatility = higher confidence
        variance = max(values) - min(values)
        if variance > 0:
            avg_value = sum(values) / len(values)
            if avg_value > 0:
                volatility_factor = 1.0 - min(variance / avg_value, 0.5)
                confidence *= volatility_factor

        return max(confidence, 0.0)

    def _calculate_strength(self, values: List[float]) -> float:
        """Calculate trend strength."""
        if len(values) < 2:
            return 0.0

        # Simple linear regression slope
        n = len(values)
        sum_x = sum(range(n))
        sum_y = sum(values)
        sum_xy = sum(i * values[i] for i in range(n))
        sum_x2 = sum(i * i for i in range(n))

        denominator = n * sum_x2 - sum_x * sum_x
        if denominator == 0:
            return 0.0

        slope = (n * sum_xy - sum_x * sum_y) / denominator
        avg_value = sum(values) / len(values)

        if avg_value == 0:
            return 0.0

        # Normalized strength
        strength = abs(slope / avg_value) * n
        return min(strength, 1.0)

    def _forecast_trend(self, values: List[float], time_horizon_months: int) -> List[float]:
        """Forecast future trend values."""
        if len(values) < 2:
            return [values[-1]] * time_horizon_months

        # Simple linear forecast
        direction = self._determine_direction(values)
        strength = self._calculate_strength(values)
        last_value = values[-1]

        forecast = []
        current_value = last_value

        for _ in range(time_horizon_months):
            change_rate = strength * 0.1  # Conservative change rate

            if direction == TrendDirection.INCREASING:
                current_value = current_value * (1 + change_rate)
            elif direction == TrendDirection.DECREASING:
                current_value = current_value * (1 - change_rate)
            # For STABLE or VOLATILE, keep current value

            forecast.append(current_value)

        return forecast


class RequirementPredictor:
    """Predicts future system requirements."""

    def __init__(self):
        self._lock = threading.Lock()

        logger.info("[REQUIREMENT_PREDICTOR] Initialized")

    def predict(
        self, trend_analyses: Dict[str, TrendAnalysis], time_horizon_months: int = 12
    ) -> List[RequirementPrediction]:
        """
        Predict future requirements based on trend analyses.

        Args:
            trend_analyses: Trend analyses from system analyzer
            time_horizon_months: Time horizon for predictions

        Returns:
            Predicted future requirements
        """
        with self._lock:
            requirements = []

            # Analyze performance trends
            cpu_trend = trend_analyses.get("cpu_usage")
            if cpu_trend and cpu_trend.direction == TrendDirection.INCREASING:
                requirements.append(
                    RequirementPrediction(
                        requirement_type="PERFORMANCE",
                        description="CPU scaling required due to increasing usage",
                        importance="HIGH" if cpu_trend.trend_strength > 0.5 else "MEDIUM",
                        time_horizon_months=min(6, time_horizon_months),
                        probability=cpu_trend.confidence * cpu_trend.trend_strength,
                        estimated_effort_months=2.0,
                    )
                )

            # Analyze memory trends
            memory_trend = trend_analyses.get("memory_usage")
            if memory_trend and memory_trend.direction == TrendDirection.INCREASING:
                requirements.append(
                    RequirementPrediction(
                        requirement_type="SCALABILITY",
                        description="Memory scaling required due to increasing usage",
                        importance="HIGH" if memory_trend.trend_strength > 0.5 else "MEDIUM",
                        time_horizon_months=min(6, time_horizon_months),
                        probability=memory_trend.confidence * memory_trend.trend_strength,
                        estimated_effort_months=1.5,
                    )
                )

            # Analyze error rate trends
            error_trend = trend_analyses.get("error_rate")
            if error_trend and error_trend.direction == TrendDirection.INCREASING:
                requirements.append(
                    RequirementPrediction(
                        requirement_type="SECURITY",
                        description="Error rate increasing - requires stability improvements",
                        importance="CRITICAL" if error_trend.trend_strength > 0.7 else "HIGH",
                        time_horizon_months=min(3, time_horizon_months),
                        probability=error_trend.confidence * error_trend.trend_strength,
                        estimated_effort_months=3.0,
                    )
                )

            # Analyze latency trends
            latency_trend = trend_analyses.get("latency_ms")
            if latency_trend and latency_trend.direction == TrendDirection.INCREASING:
                requirements.append(
                    RequirementPrediction(
                        requirement_type="PERFORMANCE",
                        description="Latency increasing - requires optimization",
                        importance="HIGH" if latency_trend.trend_strength > 0.5 else "MEDIUM",
                        time_horizon_months=min(6, time_horizon_months),
                        probability=latency_trend.confidence * latency_trend.trend_strength,
                        estimated_effort_months=2.5,
                    )
                )

            # Sort by importance and probability
            requirements.sort(key=lambda r: (r.importance, r.probability), reverse=True)

            return requirements


class CapabilityGapAnalyzer:
    """Analyzes gaps between current capabilities and future requirements."""

    def __init__(self):
        self._lock = threading.Lock()

        # Current capabilities (placeholder - would be loaded from system)
        self._current_capabilities = {
            "cpu_scaling": "MANUAL",
            "memory_scaling": "MANUAL",
            "auto_healing": "BASIC",
            "predictive_scaling": "NONE",
            "anomaly_detection": "BASIC",
        }

        logger.info("[CAPABILITY_GAP_ANALYZER] Initialized")

    def analyze(
        self, current_capabilities: Dict[str, str], future_requirements: List[RequirementPrediction]
    ) -> List[CapabilityGap]:
        """
        Analyze gaps between current capabilities and future requirements.

        Args:
            current_capabilities: Current system capabilities
            future_requirements: Predicted future requirements

        Returns:
            Capability gaps prioritized by severity
        """
        with self._lock:
            gaps = []

            # Map requirements to capabilities
            for req in future_requirements:
                if req.requirement_type == "PERFORMANCE":
                    gaps.extend(self._analyze_performance_gaps(req))
                elif req.requirement_type == "SCALABILITY":
                    gaps.extend(self._analyze_scalability_gaps(req))
                elif req.requirement_type == "SECURITY":
                    gaps.extend(self._analyze_security_gaps(req))

            # Prioritize gaps
            for i, gap in enumerate(gaps):
                gap.priority = self._calculate_priority(gap)

            gaps.sort(key=lambda g: g.priority, reverse=True)

            return gaps

    def _analyze_performance_gaps(self, req: RequirementPrediction) -> List[CapabilityGap]:
        """Analyze performance-related capability gaps."""
        gaps = []

        if self._current_capabilities.get("predictive_scaling") != "ADVANCED":
            gaps.append(
                CapabilityGap(
                    capability_name="predictive_scaling",
                    current_status=self._current_capabilities.get("predictive_scaling", "NONE"),
                    required_status="ADVANCED",
                    gap_severity="HIGH" if req.importance == "CRITICAL" else "MEDIUM",
                    closure_complexity="MEDIUM",
                    estimated_closure_time_months=3.0,
                )
            )

        return gaps

    def _analyze_scalability_gaps(self, req: RequirementPrediction) -> List[CapabilityGap]:
        """Analyze scalability-related capability gaps."""
        gaps = []

        if self._current_capabilities.get("cpu_scaling") != "AUTOMATIC":
            gaps.append(
                CapabilityGap(
                    capability_name="cpu_scaling",
                    current_status=self._current_capabilities.get("cpu_scaling", "MANUAL"),
                    required_status="AUTOMATIC",
                    gap_severity="HIGH" if req.importance == "CRITICAL" else "MEDIUM",
                    closure_complexity="MEDIUM",
                    estimated_closure_time_months=2.0,
                )
            )

        if self._current_capabilities.get("memory_scaling") != "AUTOMATIC":
            gaps.append(
                CapabilityGap(
                    capability_name="memory_scaling",
                    current_status=self._current_capabilities.get("memory_scaling", "MANUAL"),
                    required_status="AUTOMATIC",
                    gap_severity="MEDIUM",
                    closure_complexity="MEDIUM",
                    estimated_closure_time_months=2.0,
                )
            )

        return gaps

    def _analyze_security_gaps(self, req: RequirementPrediction) -> List[CapabilityGap]:
        """Analyze security-related capability gaps."""
        gaps = []

        if self._current_capabilities.get("auto_healing") != "ADVANCED":
            gaps.append(
                CapabilityGap(
                    capability_name="auto_healing",
                    current_status=self._current_capabilities.get("auto_healing", "BASIC"),
                    required_status="ADVANCED",
                    gap_severity="HIGH" if req.importance == "CRITICAL" else "MEDIUM",
                    closure_complexity="HIGH",
                    estimated_closure_time_months=4.0,
                )
            )

        return gaps

    def _calculate_priority(self, gap: CapabilityGap) -> int:
        """Calculate gap priority."""
        priority = 0

        # Severity contribution
        if gap.gap_severity == "CRITICAL":
            priority += 100
        elif gap.gap_severity == "HIGH":
            priority += 75
        elif gap.gap_severity == "MEDIUM":
            priority += 50
        else:
            priority += 25

        # Complexity contribution (simpler = higher priority for quick wins)
        if gap.closure_complexity == "LOW":
            priority += 20
        elif gap.closure_complexity == "MEDIUM":
            priority += 10

        return priority


class EvolutionPlanningSystem:
    """
    Predictive system evolution planning.

    Features:
    - Trend analysis and forecasting
    - Requirement prediction
    - Capability gap analysis
    - Evolution plan generation
    - Resource estimation
    """

    def __init__(self):
        self._lock = threading.Lock()

        # Components
        self._trend_analyzer = SystemTrendAnalyzer()
        self._requirement_predictor = RequirementPredictor()
        self._capability_gap_analyzer = CapabilityGapAnalyzer()

        # Planning history
        self._plan_history: List[EvolutionPlan] = []

        logger.info("[EVOLUTION_PLANNING] Predictive Evolution Planning System initialized")

    def forecast_evolution_needs(
        self, current_metrics: Dict[str, float], time_horizon_months: int = 12
    ) -> EvolutionForecast:
        """
        Forecast evolution needs based on system trends and requirements.

        Args:
            current_metrics: Current system metrics
            time_horizon_months: Time horizon for forecasting

        Returns:
            Comprehensive evolution forecast
        """
        with self._lock:
            # Step 1: Analyze trends
            trend_analyses = self._trend_analyzer.analyze(current_metrics, time_horizon_months)

            # Step 2: Predict requirements
            future_requirements = self._requirement_predictor.predict(
                trend_analyses, time_horizon_months
            )

            # Step 3: Analyze capability gaps
            current_capabilities = self._get_current_capabilities()
            capability_gaps = self._capability_gap_analyzer.analyze(
                current_capabilities, future_requirements
            )

            # Step 4: Generate evolution plan
            evolution_plan = self._generate_evolution_plan(
                time_horizon_months, future_requirements, capability_gaps, trend_analyses
            )

            # Step 5: Estimate resources
            resource_estimates = self._estimate_resources(evolution_plan)

            # Step 6: Assess risk
            risk_assessment = self._assess_risk(evolution_plan, trend_analyses)

            return EvolutionForecast(
                evolution_plans=[evolution_plan],
                trend_analyses=trend_analyses,
                confidence_level=evolution_plan.confidence_level,
                resource_requirements=resource_estimates,
                recommended_timeline=f"{time_horizon_months} months",
            )

    def _get_current_capabilities(self) -> Dict[str, str]:
        """Get current system capabilities."""
        # Placeholder - would query actual system capabilities
        return self._capability_gap_analyzer._current_capabilities

    def _generate_evolution_plan(
        self,
        time_horizon_months: int,
        requirements: List[RequirementPrediction],
        gaps: List[CapabilityGap],
        trend_analyses: Dict[str, TrendAnalysis],
    ) -> EvolutionPlan:
        """Generate evolution plan based on analysis."""
        plan_id = f"plan_{int(datetime.utcnow().timestamp() * 1000)}"

        # Generate recommended actions
        recommended_actions = []
        for gap in gaps[:5]:  # Top 5 gaps
            action = (
                f"Close {gap.capability_name} gap: {gap.current_status} -> {gap.required_status}"
            )
            recommended_actions.append(action)

        # Estimate resources
        resource_estimates = {
            "engineer_months": sum(gap.estimated_closure_time_months for gap in gaps),
            "budget_estimate": sum(gap.estimated_closure_time_months for gap in gaps)
            * 15000,  # $15k/month
            "infrastructure_months": 2.0,
        }

        # Calculate confidence level
        avg_confidence = (
            sum(analysis.confidence for analysis in trend_analyses.values()) / len(trend_analyses)
            if trend_analyses
            else 0.5
        )

        plan = EvolutionPlan(
            plan_id=plan_id,
            plan_name=f"Evolution Plan {time_horizon_months} Months",
            time_horizon_months=time_horizon_months,
            predicted_gaps=gaps,
            predicted_requirements=requirements,
            recommended_actions=recommended_actions,
            resource_estimates=resource_estimates,
            confidence_level=avg_confidence,
            risk_assessment="MEDIUM",
        )

        self._plan_history.append(plan)

        return plan

    def _estimate_resources(self, plan: EvolutionPlan) -> Dict[str, float]:
        """Estimate resource requirements."""
        return {
            "total_engineer_months": plan.resource_estimates.get("engineer_months", 0.0),
            "budget_estimate": plan.resource_estimates.get("budget_estimate", 0.0),
            "infrastructure_months": plan.resource_estimates.get("infrastructure_months", 0.0),
            "estimated_completion_months": plan.time_horizon_months,
        }

    def _assess_risk(self, plan: EvolutionPlan, trend_analyses: Dict[str, TrendAnalysis]) -> str:
        """Assess risk of evolution plan."""
        # Count critical gaps
        critical_gaps = sum(1 for gap in plan.predicted_gaps if gap.gap_severity == "CRITICAL")

        if critical_gaps > 2:
            return "HIGH"
        elif critical_gaps > 0:
            return "MEDIUM"
        else:
            return "LOW"

    def get_statistics(self) -> Dict[str, Any]:
        """Get evolution planning statistics."""
        with self._lock:
            return {
                "plan_history_size": len(self._plan_history),
                "current_capabilities": self._capability_gap_analyzer._current_capabilities,
                "last_forecast_confidence": 0.8,  # Placeholder for actual last confidence
            }


# Singleton instance
_evolution_planning_system: Optional[EvolutionPlanningSystem] = None
_evolution_planning_lock = threading.Lock()


def get_evolution_planning_system() -> EvolutionPlanningSystem:
    """Get the singleton evolution planning system instance."""
    global _evolution_planning_system
    if _evolution_planning_system is None:
        with _evolution_planning_lock:
            if _evolution_planning_system is None:
                _evolution_planning_system = EvolutionPlanningSystem()
    return _evolution_planning_system


def get_evolution_forecasting_system() -> EvolutionPlanningSystem:
    """Get the singleton evolution forecasting system instance (alias)."""
    return get_evolution_planning_system()


__all__ = [
    "TrendDirection",
    "TrendAnalysis",
    "RequirementPrediction",
    "CapabilityGap",
    "EvolutionPlan",
    "EvolutionForecast",
    "SystemTrendAnalyzer",
    "RequirementPredictor",
    "CapabilityGapAnalyzer",
    "EvolutionPlanningSystem",
    "get_evolution_planning_system",
    "get_evolution_forecasting_system",
]
