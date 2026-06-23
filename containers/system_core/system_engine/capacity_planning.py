"""Capacity Planning Intelligence for DYON - Load Forecasting and Optimization.

This module provides capacity planning capabilities for DYON:
- Dynamic resource scaling
- Load forecasting
- Cost optimization
- Performance tuning
- Resource efficiency monitoring
- Right-sizing recommendations
- Resource allocation optimization

Per INV-15: Pure computation, no clock reads, no PRNG, no IO. Deterministic replays.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from math import sqrt
from typing import Protocol


class ResourceType(Enum):
    """Types of resources to plan for."""

    CPU = "cpu"
    MEMORY = "memory"
    DISK = "disk"
    NETWORK = "network"
    GPU = "gpu"
    DATABASE_CONNECTIONS = "database_connections"
    API_RATE_LIMIT = "api_rate_limit"


class ScalingAction(Enum):
    """Types of scaling actions."""

    SCALE_UP = "scale_up"
    SCALE_DOWN = "scale_down"
    SCALE_OUT = "scale_out"
    SCALE_IN = "scale_in"
    NO_ACTION = "no_action"
    OPTIMIZE = "optimize"


@dataclass(frozen=True, slots=True)
class ResourceUsage:
    """Current resource usage."""

    resource_type: ResourceType
    component: str
    current_usage: float  # 0-1 (percentage) or absolute value
    max_capacity: float
    timestamp_ns: int
    metadata: dict[str, float]


@dataclass(frozen=True, slots=True)
class LoadForecast:
    """Load forecast for a resource."""

    resource_type: ResourceType
    component: str
    forecast_horizon_ns: int
    predicted_peak_usage: float
    predicted_average_usage: float
    confidence_interval: tuple[float, float]  # (lower, upper)
    forecast_points: tuple[float, ...]  # Predicted usage over time
    timestamp_ns: int


@dataclass(frozen=True, slots=True)
class ScalingRecommendation:
    """Scaling recommendation for a resource."""

    resource_type: ResourceType
    component: str
    action: ScalingAction
    current_capacity: float
    recommended_capacity: float
    confidence: float
    reason: str
    estimated_cost_impact: float
    estimated_performance_impact: float
    timestamp_ns: int


@dataclass(frozen=True, slots=True)
class CapacityPlan:
    """Comprehensive capacity plan."""

    plan_id: str
    component: str
    scaling_recommendations: tuple[ScalingRecommendation, ...]
    total_cost_impact: float
    total_performance_impact: float
    priority: str  # "high", "medium", "low"
    timestamp_ns: int


class LoadForecaster(Protocol):
    """Protocol for load forecasting models."""

    def forecast_load(
        self,
        historical_usage: tuple[float, ...],
        forecast_horizon_steps: int,
        confidence_level: float,
    ) -> tuple[tuple[float, ...], tuple[float, float], float]:
        """Forecast future load from historical usage.

        Returns:
            forecast_points: Predicted usage over time
            confidence_interval: (lower_bound, upper_bound)
            trend: Trend coefficient
        """
        ...


@dataclass
class CapacityPlanningEngine:
    """Capacity planning and optimization engine.

    Analyzes resource usage patterns and provides scaling recommendations
    and capacity optimization suggestions.

    Attributes:
        forecast_horizon_ns: How far ahead to forecast load
        scaling_threshold: Threshold for triggering scaling (0-1)
        cost_sensitivity: Sensitivity to cost (0-1, higher = more cost-conscious)
        performance_sensitivity: Sensitivity to performance (0-1, higher = more performance-conscious)
    """

    forecast_horizon_ns: int = 300_000_000_000  # 5 minutes
    scaling_threshold: float = 0.7
    cost_sensitivity: float = 0.5
    performance_sensitivity: float = 0.5

    # Forecaster (injected)
    _load_forecaster: LoadForecaster = field(default=None, init=False, repr=False)

    # Resource usage history
    _usage_history: dict[tuple[ResourceType, str], list[ResourceUsage]] = field(
        default_factory=dict, init=False, repr=False
    )

    # Load forecasts
    _forecasts: dict[tuple[ResourceType, str], LoadForecast] = field(
        default_factory=dict, init=False, repr=False
    )

    # Scaling recommendations
    _recommendations: list[ScalingRecommendation] = field(
        default_factory=list, init=False, repr=False
    )

    # Capacity plans
    _capacity_plans: dict[str, CapacityPlan] = field(default_factory=dict, init=False, repr=False)

    def __post_init__(self) -> None:
        if not 0.0 <= self.scaling_threshold <= 1.0:
            raise ValueError("scaling_threshold must be in [0, 1]")
        if not 0.0 <= self.cost_sensitivity <= 1.0:
            raise ValueError("cost_sensitivity must be in [0, 1]")
        if not 0.0 <= self.performance_sensitivity <= 1.0:
            raise ValueError("performance_sensitivity must be in [0, 1]")

    def add_usage(self, usage: ResourceUsage) -> None:
        """Add a resource usage data point."""
        key = (usage.resource_type, usage.component)

        if key not in self._usage_history:
            self._usage_history[key] = []

        self._usage_history[key].append(usage)

        # Keep limited history (last 500 points per resource)
        if len(self._usage_history[key]) > 500:
            self._usage_history[key] = self._usage_history[key][-500:]

    def forecast_load(
        self,
        resource_type: ResourceType,
        component: str,
        current_timestamp_ns: int,
    ) -> LoadForecast | None:
        """Forecast load for a specific resource and component.

        Args:
            resource_type: Type of resource to forecast
            component: Component to forecast for
            current_timestamp_ns: Current timestamp

        Returns:
            LoadForecast if forecast available, None otherwise
        """
        key = (resource_type, component)

        if key not in self._usage_history:
            return None

        history = self._usage_history[key]
        if len(history) < 32:
            return None

        # Get historical usage (normalized to 0-1)
        historical = tuple(
            u.current_usage / u.max_capacity if u.max_capacity > 0 else 0.0 for u in history[-64:]
        )

        # Forecast load
        if self._load_forecaster is not None:
            forecast_points, confidence_interval, trend = self._load_forecaster.forecast_load(
                historical_usage=historical,
                forecast_horizon_steps=32,
                confidence_level=0.95,
            )
        else:
            forecast_points, confidence_interval, trend = self._fallback_forecast(historical)

        # Calculate forecast metrics
        predicted_peak = max(forecast_points) if forecast_points else 0.0
        predicted_average = sum(forecast_points) / len(forecast_points) if forecast_points else 0.0

        # Create forecast
        forecast = LoadForecast(
            resource_type=resource_type,
            component=component,
            forecast_horizon_ns=self.forecast_horizon_ns,
            predicted_peak_usage=predicted_peak,
            predicted_average_usage=predicted_average,
            confidence_interval=confidence_interval,
            forecast_points=forecast_points,
            timestamp_ns=current_timestamp_ns,
        )

        self._forecasts[key] = forecast
        return forecast

    def _fallback_forecast(
        self,
        historical: tuple[float, ...],
    ) -> tuple[tuple[float, ...], tuple[float, float], float]:
        """Fallback forecast using simple extrapolation."""
        if len(historical) < 2:
            return (historical[-1],) * 32, (0.0, 1.0), 0.0

        # Simple linear extrapolation
        n = len(historical)
        recent_slope = (historical[-1] - historical[-min(8, n)]) / min(8, n)

        forecast_points = []
        current = historical[-1]

        for i in range(32):
            pred = current + recent_slope * (i + 1)
            # Clamp to [0, 1]
            pred = max(0.0, min(1.0, pred))
            forecast_points.append(pred)

        # Calculate confidence interval (simplified)
        vol = sqrt(
            sum((x - sum(historical) / len(historical)) ** 2 for x in historical) / len(historical)
        )
        confidence_interval = (
            max(0.0, historical[-1] - 2 * vol),
            min(1.0, historical[-1] + 2 * vol),
        )

        return (tuple(forecast_points), confidence_interval, recent_slope)

    def generate_scaling_recommendations(
        self,
        resource_type: ResourceType,
        component: str,
        current_timestamp_ns: int,
    ) -> ScalingRecommendation | None:
        """Generate scaling recommendation for a resource.

        Args:
            resource_type: Type of resource
            component: Component to recommend for
            current_timestamp_ns: Current timestamp

        Returns:
            ScalingRecommendation if action recommended, None otherwise
        """
        key = (resource_type, component)

        # Get current usage
        if key not in self._usage_history:
            return None

        current_usage = self._usage_history[key][-1]
        current_utilization = current_usage.current_usage / current_usage.max_capacity

        # Get forecast
        forecast = self._forecasts.get(key)
        if forecast is None:
            forecast = self.forecast_load(resource_type, component, current_timestamp_ns)
            if forecast is None:
                return None

        # Determine action
        action, reason, recommended_capacity = self._determine_scaling_action(
            current_utilization,
            forecast.predicted_peak_usage,
            current_usage.max_capacity,
        )

        if action == ScalingAction.NO_ACTION:
            return None

        # Calculate confidence
        confidence = self._calculate_scaling_confidence(
            current_utilization,
            forecast.predicted_peak_usage,
            forecast.confidence_interval,
        )

        # Calculate impacts
        cost_impact = self._calculate_cost_impact(
            action, recommended_capacity, current_usage.max_capacity
        )
        performance_impact = self._calculate_performance_impact(
            action, current_utilization, forecast.predicted_peak_usage
        )

        # Create recommendation
        recommendation = ScalingRecommendation(
            resource_type=resource_type,
            component=component,
            action=action,
            current_capacity=current_usage.max_capacity,
            recommended_capacity=recommended_capacity,
            confidence=confidence,
            reason=reason,
            estimated_cost_impact=cost_impact,
            estimated_performance_impact=performance_impact,
            timestamp_ns=current_timestamp_ns,
        )

        self._recommendations.append(recommendation)

        return recommendation

    def _determine_scaling_action(
        self,
        current_utilization: float,
        predicted_peak: float,
        current_capacity: float,
    ) -> tuple[ScalingAction, str, float]:
        """Determine scaling action based on utilization and forecast."""
        # Scale up if predicted peak exceeds threshold
        if predicted_peak > self.scaling_threshold:
            # Calculate required capacity
            required_capacity = current_capacity * (predicted_peak / (self.scaling_threshold * 0.9))

            if predicted_peak > 0.9:
                return (
                    ScalingAction.SCALE_UP,
                    f"Predicted peak usage {predicted_peak:.1%} exceeds critical threshold",
                    required_capacity,
                )
            else:
                return (
                    ScalingAction.SCALE_OUT,
                    f"Predicted peak usage {predicted_peak:.1%} exceeds threshold",
                    required_capacity,
                )

        # Scale down if current and predicted utilization are low
        if current_utilization < 0.3 and predicted_peak < 0.4:
            required_capacity = current_capacity * 0.7  # Scale down to 70%
            return (
                ScalingAction.SCALE_DOWN,
                f"Low utilization {current_utilization:.1%} with slack capacity",
                required_capacity,
            )

        # Optimize if utilization is moderate but could be improved
        if 0.5 <= current_utilization <= 0.7 and predicted_peak <= 0.8:
            # Slight optimization
            required_capacity = current_capacity * 1.1
            return (
                ScalingAction.OPTIMIZE,
                f"Moderate utilization with optimization opportunity",
                required_capacity,
            )

        return (ScalingAction.NO_ACTION, "No scaling action needed", current_capacity)

    def _calculate_scaling_confidence(
        self,
        current_utilization: float,
        predicted_peak: float,
        confidence_interval: tuple[float, float],
    ) -> float:
        """Calculate confidence in scaling recommendation."""
        # Higher confidence when:
        # 1. Current utilization is high/low (clear signal)
        # 2. Predicted peak is significantly above/below threshold
        # 3. Confidence interval is narrow (precise forecast)

        utilization_signal = max(current_utilization, 1.0 - current_utilization)
        forecast_signal = max(predicted_peak, 1.0 - predicted_peak)

        confidence_width = confidence_interval[1] - confidence_interval[0]
        precision = max(0.0, 1.0 - confidence_width)

        confidence = (utilization_signal + forecast_signal + precision) / 3.0
        return max(0.0, min(1.0, confidence))

    def _calculate_cost_impact(
        self,
        action: ScalingAction,
        recommended_capacity: float,
        current_capacity: float,
    ) -> float:
        """Calculate estimated cost impact of scaling action.

        Returns:
            Cost impact as a percentage (positive = increased cost)
        """
        if action in (ScalingAction.SCALE_UP, ScalingAction.SCALE_OUT):
            # Scaling up increases cost proportionally
            cost_impact = (recommended_capacity - current_capacity) / current_capacity
        elif action in (ScalingAction.SCALE_DOWN, ScalingAction.SCALE_IN):
            # Scaling down reduces cost
            cost_impact = (recommended_capacity - current_capacity) / current_capacity
        else:
            cost_impact = 0.0

        # Adjust for cost sensitivity
        cost_impact *= self.cost_sensitivity

        return cost_impact

    def _calculate_performance_impact(
        self,
        action: ScalingAction,
        current_utilization: float,
        predicted_peak: float,
    ) -> float:
        """Calculate estimated performance impact of scaling action.

        Returns:
            Performance impact as a percentage (positive = improved performance)
        """
        if action in (ScalingAction.SCALE_UP, ScalingAction.SCALE_OUT):
            # Scaling up improves performance when under load
            if current_utilization > 0.7:
                performance_impact = (current_utilization - 0.7) * 2.0  # Up to 60% improvement
            else:
                performance_impact = 0.0
        elif action in (ScalingAction.SCALE_DOWN, ScalingAction.SCALE_IN):
            # Scaling down may degrade performance but saves cost
            performance_impact = -0.1  # Slight degradation
        else:
            performance_impact = 0.0

        # Adjust for performance sensitivity
        performance_impact *= self.performance_sensitivity

        return performance_impact

    def generate_capacity_plan(
        self,
        component: str,
        current_timestamp_ns: int,
    ) -> CapacityPlan | None:
        """Generate comprehensive capacity plan for a component.

        Args:
            component: Component to generate plan for
            current_timestamp_ns: Current timestamp

        Returns:
            CapacityPlan if recommendations available, None otherwise
        """
        # Generate recommendations for all resource types
        recommendations = []

        for resource_type in ResourceType:
            rec = self.generate_scaling_recommendations(
                resource_type, component, current_timestamp_ns
            )
            if rec is not None:
                recommendations.append(rec)

        if not recommendations:
            return None

        # Calculate total impacts
        total_cost_impact = sum(r.estimated_cost_impact for r in recommendations)
        total_performance_impact = sum(r.estimated_performance_impact for r in recommendations)

        # Determine priority
        priority = self._determine_priority(recommendations)

        # Create plan
        plan_id = f"capacity_plan_{component}_{current_timestamp_ns}"

        plan = CapacityPlan(
            plan_id=plan_id,
            component=component,
            scaling_recommendations=tuple(recommendations),
            total_cost_impact=total_cost_impact,
            total_performance_impact=total_performance_impact,
            priority=priority,
            timestamp_ns=current_timestamp_ns,
        )

        self._capacity_plans[plan_id] = plan

        return plan

    def _determine_priority(self, recommendations: list[ScalingRecommendation]) -> str:
        """Determine priority of capacity plan."""
        # High priority if scaling up critical resources
        for rec in recommendations:
            if rec.action in (ScalingAction.SCALE_UP, ScalingAction.SCALE_OUT):
                if rec.confidence > 0.8:
                    return "high"

        # Medium priority if optimization or moderate scaling
        for rec in recommendations:
            if rec.action == ScalingAction.OPTIMIZE:
                return "medium"

        # Low priority if only scaling down
        for rec in recommendations:
            if rec.action in (ScalingAction.SCALE_DOWN, ScalingAction.SCALE_IN):
                return "low"

        return "medium"

    def get_forecasts(self) -> tuple[LoadForecast, ...]:
        """Get all current forecasts."""
        return tuple(self._forecasts.values())

    def get_recommendations(self, limit: int = 10) -> tuple[ScalingRecommendation, ...]:
        """Get recent scaling recommendations."""
        return tuple(self._recommendations[-limit:])

    def get_capacity_plans(self) -> tuple[CapacityPlan, ...]:
        """Get all capacity plans."""
        return tuple(self._capacity_plans.values())

    def clear_history(self) -> None:
        """Clear all history and forecasts."""
        self._usage_history.clear()
        self._forecasts.clear()
        self._recommendations.clear()
        self._capacity_plans.clear()


@dataclass
class ResourceEfficiencyMonitor:
    """Monitor resource efficiency and identify optimization opportunities.

    Tracks resource utilization patterns and identifies inefficiencies.
    """

    capacity_engine: CapacityPlanningEngine = field(default_factory=CapacityPlanningEngine)

    # Efficiency metrics
    _efficiency_scores: dict[str, float] = field(default_factory=dict, init=False, repr=False)

    # Optimization opportunities
    _optimization_opportunities: list[tuple[str, str, float]] = field(
        default_factory=list, init=False, repr=False
    )  # (component, opportunity_type, potential_savings)

    def calculate_efficiency_score(
        self,
        component: str,
        resource_type: ResourceType,
    ) -> float:
        """Calculate efficiency score for a component-resource pair.

        Returns:
            Efficiency score (0-1, higher is more efficient)
        """
        key = (resource_type, component)

        if key not in self.capacity_engine._usage_history:
            return 0.5  # Default efficiency

        history = self.capacity_engine._usage_history[key]
        if len(history) < 32:
            return 0.5

        # Calculate efficiency based on utilization variance
        utilizations = tuple(
            u.current_usage / u.max_capacity if u.max_capacity > 0 else 0.0 for u in history[-32:]
        )

        mean_utilization = sum(utilizations) / len(utilizations)
        variance = sum((u - mean_utilization) ** 2 for u in utilizations) / len(utilizations)
        std_dev = sqrt(variance)

        # Efficiency is higher when:
        # 1. Utilization is moderate (not too low, not too high)
        # 2. Variance is low (stable utilization)

        ideal_utilization = 0.7  # Target 70% utilization
        utilization_score = 1.0 - abs(mean_utilization - ideal_utilization) / ideal_utilization
        stability_score = 1.0 - min(1.0, std_dev)

        efficiency = (utilization_score + stability_score) / 2.0

        self._efficiency_scores[f"{component}_{resource_type.value}"] = efficiency

        return efficiency

    def identify_optimization_opportunities(
        self,
        component: str,
    ) -> tuple[tuple[str, str, float], ...]:
        """Identify optimization opportunities for a component.

        Returns:
            Tuple of (component, opportunity_type, potential_savings)
        """
        opportunities = []

        for resource_type in ResourceType:
            efficiency = self.calculate_efficiency_score(component, resource_type)

            if efficiency < 0.5:
                # Low efficiency - optimization opportunity
                potential_savings = (1.0 - efficiency) * 100.0  # Percentage savings
                opportunities.append(
                    (component, f"optimize_{resource_type.value}", potential_savings)
                )

        self._optimization_opportunities.extend(opportunities)

        return tuple(opportunities)

    def get_efficiency_scores(self) -> dict[str, float]:
        """Get all efficiency scores."""
        return self._efficiency_scores.copy()

    def get_optimization_opportunities(self) -> tuple[tuple[str, str, float], ...]:
        """Get all optimization opportunities."""
        return tuple(self._optimization_opportunities)


__all__ = [
    "CapacityPlanningEngine",
    "ResourceEfficiencyMonitor",
    "ResourceType",
    "ScalingAction",
    "ResourceUsage",
    "LoadForecast",
    "ScalingRecommendation",
    "CapacityPlan",
    "LoadForecaster",
]
