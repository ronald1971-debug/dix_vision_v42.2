"""evolution_engine.dyon.predictive_scaling — Predictive Scaling for DYON Resource Management.

Automatic resource scaling based on predictive analysis for system optimization.

This implementation provides predictive scaling capabilities:
- Resource demand prediction
- Automatic scaling recommendations
- Scaling cost analysis
- Scaling optimization strategies
- Multi-resource coordination
- Predictive resource allocation
- Scaling policy management
- Resource utilization forecasting

Authority (L2/B1): evolution_engine.* only at module level.
DYON provides predictive scaling for system optimization, never for trading purposes.
"""

from __future__ import annotations

import logging
import statistics
import threading
import time
from collections import defaultdict, deque
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Dict, List, Optional

_logger = logging.getLogger(__name__)


class ResourceType(Enum):
    """Types of resources that can be scaled."""

    CPU = "cpu"
    MEMORY = "memory"
    DISK = "disk"
    NETWORK = "network"
    DATABASE_CONNECTIONS = "database_connections"
    CONTAINER_INSTANCES = "container_instances"
    FUNCTION_EXECUTIONS = "function_executions"
    STORAGE = "storage"


class ScalingAction(Enum):
    """Types of scaling actions."""

    SCALE_UP = "scale_up"
    SCALE_DOWN = "scale_down"
    SCALE_OUT = "scale_out"  # Add more instances
    SCALE_IN = "scale_in"  # Remove instances
    NO_ACTION = "no_action"


class ScalingPolicyType(Enum):
    """Types of scaling policies."""

    THRESHOLD_BASED = "threshold_based"
    PREDICTIVE = "predictive"
    SCHEDULE_BASED = "schedule_based"
    HYBRID = "hybrid"


@dataclass
class ResourceMetric:
    """Current metric for a resource."""

    resource_type: ResourceType
    current_value: float
    capacity: float
    utilization: float
    timestamp: float
    unit: str = ""  # cores, GB, Mbps, etc.


@dataclass
class ScalingRecommendation:
    """Recommendation for scaling action."""

    recommendation_id: str
    resource_type: ResourceType
    action: ScalingAction
    current_value: float
    recommended_value: float
    reason: str
    confidence: float
    estimated_cost_impact: float
    estimated_performance_impact: float
    priority: str  # critical, high, medium, low
    execution_time: float  # When to execute scaling


@dataclass
class ScalingPolicy:
    """Policy for automatic scaling."""

    policy_id: str
    policy_name: str
    policy_type: ScalingPolicyType
    resource_type: ResourceType
    scale_up_threshold: float
    scale_down_threshold: float
    min_capacity: float
    max_capacity: float
    cooldown_period: float  # seconds
    is_active: bool = True
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class ScalingHistory:
    """History of scaling actions."""

    scaling_id: str
    timestamp: float
    resource_type: ResourceType
    action: ScalingAction
    previous_value: float
    new_value: float
    reason: str
    success: bool
    cost_impact: float


class PredictiveScaling:
    """Predictive scaling system for automatic resource management.

    DYON uses this to predict resource needs and recommend scaling actions
    without performing trading operations.
    """

    def __init__(self, repo_root: str = "."):
        """Initialize predictive scaling system.

        Args:
            repo_root: Path to repository root
        """
        self.repo_root = repo_root
        self._lock = threading.Lock()
        self._current_metrics: Dict[ResourceType, ResourceMetric] = {}
        self._metric_history: Dict[ResourceType, deque] = defaultdict(lambda: deque(maxlen=1000))
        self._scaling_policies: Dict[str, ScalingPolicy] = {}
        self._scaling_history: List[ScalingHistory] = []
        self._resource_predictions: Dict[ResourceType, List[float]] = {}
        self._active_recommendations: List[ScalingRecommendation] = []

        # Initialize default policies
        self._initialize_default_policies()

        _logger.info(
            f"[PredictiveScaling] Initialized with repo_root={repo_root}, "
            f"policies={len(self._scaling_policies)}"
        )

    def _initialize_default_policies(self) -> None:
        """Initialize default scaling policies."""
        default_policies = [
            ScalingPolicy(
                policy_id="cpu_scale_policy",
                policy_name="CPU Scaling Policy",
                policy_type=ScalingPolicyType.HYBRID,
                resource_type=ResourceType.CPU,
                scale_up_threshold=0.75,
                scale_down_threshold=0.25,
                min_capacity=1.0,
                max_capacity=100.0,
                cooldown_period=300.0,
            ),
            ScalingPolicy(
                policy_id="memory_scale_policy",
                policy_name="Memory Scaling Policy",
                policy_type=ScalingPolicyType.HYBRID,
                resource_type=ResourceType.MEMORY,
                scale_up_threshold=0.80,
                scale_down_threshold=0.30,
                min_capacity=4.0,
                max_capacity=128.0,
                cooldown_period=300.0,
            ),
            ScalingPolicy(
                policy_id="container_scale_policy",
                policy_name="Container Instance Scaling Policy",
                policy_type=ScalingPolicyType.PREDICTIVE,
                resource_type=ResourceType.CONTAINER_INSTANCES,
                scale_up_threshold=0.70,
                scale_down_threshold=0.20,
                min_capacity=1.0,
                max_capacity=50.0,
                cooldown_period=600.0,
            ),
        ]

        for policy in default_policies:
            self._scaling_policies[policy.policy_id] = policy

        _logger.info("[PredictiveScaling] Initialized default scaling policies")

    def record_metric(self, metric: ResourceMetric) -> None:
        """Record a resource metric.

        Args:
            metric: Resource metric to record
        """
        with self._lock:
            self._current_metrics[metric.resource_type] = metric
            self._metric_history[metric.resource_type].append(metric)

            _logger.debug(
                f"[PredictiveScaling] Recorded metric: {metric.resource_type.value} "
                f"utilization={metric.utilization:.2f}"
            )

    def add_scaling_policy(self, policy: ScalingPolicy) -> bool:
        """Add a scaling policy.

        Args:
            policy: Scaling policy to add

        Returns:
            True if added successfully
        """
        with self._lock:
            if policy.policy_id in self._scaling_policies:
                _logger.warning(f"[PredictiveScaling] Policy already exists: {policy.policy_id}")
                return False

            self._scaling_policies[policy.policy_id] = policy
            _logger.info(f"[PredictiveScaling] Added scaling policy: {policy.policy_id}")

            return True

    def update_resource_predictions(
        self, resource_type: ResourceType, predictions: List[float]
    ) -> None:
        """Update predictions for a resource.

        Args:
            resource_type: Type of resource
            predictions: List of predicted future values
        """
        with self._lock:
            self._resource_predictions[resource_type] = predictions

            _logger.debug(
                f"[PredictiveScaling] Updated predictions for {resource_type.value}: "
                f"{len(predictions)} predictions"
            )

    def generate_scaling_recommendations(self) -> List[ScalingRecommendation]:
        """Generate scaling recommendations based on current state and predictions.

        Returns:
            List of scaling recommendations
        """
        with self._lock:
            recommendations = []

            for policy_id, policy in self._scaling_policies.items():
                if not policy.is_active:
                    continue

                # Get current metric
                current_metric = self._current_metrics.get(policy.resource_type)
                if not current_metric:
                    continue

                # Check cooldown period
                if self._is_in_cooldown(policy):
                    continue

                # Generate recommendation based on policy type
                if policy.policy_type == ScalingPolicyType.THRESHOLD_BASED:
                    recommendation = self._generate_threshold_based_recommendation(
                        policy, current_metric
                    )
                elif policy.policy_type == ScalingPolicyType.PREDICTIVE:
                    recommendation = self._generate_predictive_recommendation(
                        policy, current_metric
                    )
                elif policy.policy_type == ScalingPolicyType.HYBRID:
                    recommendation = self._generate_hybrid_recommendation(policy, current_metric)
                else:
                    continue

                if recommendation:
                    recommendations.append(recommendation)

            self._active_recommendations = recommendations

            _logger.info(
                f"[PredictiveScaling] Generated {len(recommendations)} scaling recommendations"
            )

            return recommendations

    def _is_in_cooldown(self, policy: ScalingPolicy) -> bool:
        """Check if policy is in cooldown period.

        Args:
            policy: Scaling policy to check

        Returns:
            True if in cooldown period
        """
        current_time = time.time()

        # Find most recent scaling action for this resource type
        recent_scaling = [
            h
            for h in self._scaling_history
            if h.resource_type == policy.resource_type
            and current_time - h.timestamp < policy.cooldown_period
        ]

        return len(recent_scaling) > 0

    def _generate_threshold_based_recommendation(
        self, policy: ScalingPolicy, metric: ResourceMetric
    ) -> Optional[ScalingRecommendation]:
        """Generate threshold-based scaling recommendation.

        Args:
            policy: Scaling policy
            metric: Current resource metric

        Returns:
            Scaling recommendation or None
        """
        if metric.utilization >= policy.scale_up_threshold:
            # Scale up
            recommended_value = min(metric.capacity * 1.5, policy.max_capacity)
            action = ScalingAction.SCALE_UP
            reason = f"Utilization {metric.utilization:.2f} exceeds scale-up threshold {policy.scale_up_threshold}"
            priority = "high"

        elif metric.utilization <= policy.scale_down_threshold:
            # Scale down
            recommended_value = max(metric.capacity * 0.7, policy.min_capacity)
            action = ScalingAction.SCALE_DOWN
            reason = f"Utilization {metric.utilization:.2f} below scale-down threshold {policy.scale_down_threshold}"
            priority = "medium"
        else:
            return None

        # Check if within bounds
        if recommended_value == metric.capacity:
            return None

        return ScalingRecommendation(
            recommendation_id=f"rec_{int(time.time())}_{policy.policy_id}",
            resource_type=policy.resource_type,
            action=action,
            current_value=metric.capacity,
            recommended_value=recommended_value,
            reason=reason,
            confidence=0.8,
            estimated_cost_impact=self._estimate_cost_impact(
                policy.resource_type, metric.capacity, recommended_value
            ),
            estimated_performance_impact=self._estimate_performance_impact(
                action, metric.utilization
            ),
            priority=priority,
            execution_time=time.time(),
        )

    def _generate_predictive_recommendation(
        self, policy: ScalingPolicy, metric: ResourceMetric
    ) -> Optional[ScalingRecommendation]:
        """Generate predictive scaling recommendation.

        Args:
            policy: Scaling policy
            metric: Current resource metric

        Returns:
            Scaling recommendation or None
        """
        predictions = self._resource_predictions.get(policy.resource_type, [])

        if not predictions:
            return self._generate_threshold_based_recommendation(policy, metric)

        # Average prediction for next period
        avg_prediction = statistics.mean(predictions)
        predicted_utilization = avg_prediction / policy.max_capacity

        if predicted_utilization >= policy.scale_up_threshold:
            # Scale up based on prediction
            scale_factor = 1.0 + (predicted_utilization - policy.scale_up_threshold) * 2.0
            recommended_value = min(metric.capacity * scale_factor, policy.max_capacity)
            action = ScalingAction.SCALE_UP
            reason = f"Predicted utilization {predicted_utilization:.2f} exceeds threshold in next period"
            priority = "high"
            confidence = 0.7

        elif predicted_utilization <= policy.scale_down_threshold:
            # Scale down based on prediction
            scale_factor = 1.0 - (policy.scale_down_threshold - predicted_utilization) * 2.0
            recommended_value = max(metric.capacity * scale_factor, policy.min_capacity)
            action = ScalingAction.SCALE_DOWN
            reason = (
                f"Predicted utilization {predicted_utilization:.2f} below threshold in next period"
            )
            priority = "low"
            confidence = 0.6
        else:
            return None

        # Check if within bounds
        if recommended_value == metric.capacity:
            return None

        return ScalingRecommendation(
            recommendation_id=f"rec_{int(time.time())}_{policy.policy_id}",
            resource_type=policy.resource_type,
            action=action,
            current_value=metric.capacity,
            recommended_value=recommended_value,
            reason=reason,
            confidence=confidence,
            estimated_cost_impact=self._estimate_cost_impact(
                policy.resource_type, metric.capacity, recommended_value
            ),
            estimated_performance_impact=self._estimate_performance_impact(
                action, metric.utilization
            ),
            priority=priority,
            execution_time=time.time(),
        )

    def _generate_hybrid_recommendation(
        self, policy: ScalingPolicy, metric: ResourceMetric
    ) -> Optional[ScalingRecommendation]:
        """Generate hybrid (threshold + predictive) scaling recommendation.

        Args:
            policy: Scaling policy
            metric: Current resource metric

        Returns:
            Scaling recommendation or None
        """
        # Get both types of recommendations
        threshold_rec = self._generate_threshold_based_recommendation(policy, metric)
        predictive_rec = self._generate_predictive_recommendation(policy, metric)

        # Prefer threshold-based for immediate action, predictive for proactive
        if threshold_rec and threshold_rec.priority == "high":
            return threshold_rec
        elif predictive_rec:
            return predictive_rec
        elif threshold_rec:
            return threshold_rec
        else:
            return None

    def _estimate_cost_impact(
        self, resource_type: ResourceType, current_value: float, recommended_value: float
    ) -> float:
        """Estimate cost impact of scaling action.

        Args:
            resource_type: Type of resource
            current_value: Current capacity
            recommended_value: Recommended capacity

        Returns:
            Estimated cost impact (positive = increase, negative = decrease)
        """
        # Simplified cost model (would be more sophisticated in production)
        cost_per_unit = {
            ResourceType.CPU: 0.05,
            ResourceType.MEMORY: 0.01,
            ResourceType.CONTAINER_INSTANCES: 0.10,
            ResourceType.DATABASE_CONNECTIONS: 0.02,
        }.get(resource_type, 0.01)

        value_change = recommended_value - current_value
        cost_impact = value_change * cost_per_unit

        return cost_impact

    def _estimate_performance_impact(
        self, action: ScalingAction, current_utilization: float
    ) -> float:
        """Estimate performance impact of scaling action.

        Args:
            action: Scaling action
            current_utilization: Current utilization

        Returns:
            Estimated performance impact (-1.0 to 1.0)
        """
        if action == ScalingAction.SCALE_UP:
            # Scale up improves performance if utilization is high
            if current_utilization > 0.7:
                return 0.5  # Significant improvement
            else:
                return 0.2  # Minor improvement
        elif action == ScalingAction.SCALE_DOWN:
            # Scale down may reduce performance if utilization is moderate
            if current_utilization > 0.5:
                return -0.3  # Potential degradation
            else:
                return 0.0  # Minimal impact
        else:
            return 0.0

    def execute_scaling(self, recommendation: ScalingRecommendation) -> ScalingHistory:
        """Execute a scaling recommendation (simulation).

        Args:
            recommendation: Scaling recommendation to execute

        Returns:
            Scaling history record
        """
        with self._lock:
            scaling_id = f"scale_{int(time.time())}"

            # Simulate scaling execution
            success = True  # In production, this would actually execute the scaling
            cost_impact = recommendation.estimated_cost_impact

            # Record scaling history
            history = ScalingHistory(
                scaling_id=scaling_id,
                timestamp=time.time(),
                resource_type=recommendation.resource_type,
                action=recommendation.action,
                previous_value=recommendation.current_value,
                new_value=recommendation.recommended_value,
                reason=recommendation.reason,
                success=success,
                cost_impact=cost_impact,
            )

            self._scaling_history.append(history)

            # Update current metric
            current_metric = self._current_metrics.get(recommendation.resource_type)
            if current_metric:
                current_metric.capacity = recommendation.recommended_value
                current_metric.utilization = (
                    current_metric.current_value / current_metric.capacity
                    if current_metric.capacity > 0
                    else 0.0
                )

            _logger.info(
                f"[PredictiveScaling] Executed scaling: {recommendation.resource_type.value} "
                f"{recommendation.action.value} from {recommendation.current_value} to "
                f"{recommendation.recommended_value}"
            )

            return history

    def get_scaling_history(self, limit: int = 10) -> List[ScalingHistory]:
        """Get scaling history.

        Args:
            limit: Maximum number of history records to return

        Returns:
            List of scaling history records
        """
        with self._lock:
            return list(self._scaling_history[-limit:])

    def get_active_recommendations(self) -> List[ScalingRecommendation]:
        """Get active scaling recommendations.

        Returns:
            List of active recommendations
        """
        with self._lock:
            return list(self._active_recommendations)

    def get_resource_summary(self) -> Dict[str, Any]:
        """Get summary of current resource state.

        Returns:
            Resource summary
        """
        with self._lock:
            return {
                "resource_count": len(self._current_metrics),
                "resources": {
                    rt.value: {
                        "current_capacity": m.capacity,
                        "current_utilization": m.utilization,
                        "predictions_available": len(self._resource_predictions.get(rt, [])),
                    }
                    for rt, m in self._current_metrics.items()
                },
                "active_recommendations": len(self._active_recommendations),
                "total_scaling_actions": len(self._scaling_history),
                "total_cost_impact": sum(h.cost_impact for h in self._scaling_history),
            }


# Singleton instance
_predictive_scaling: Optional[PredictiveScaling] = None
_scaling_lock = threading.Lock()


def get_predictive_scaling(repo_root: str = ".") -> PredictiveScaling:
    """Get singleton instance of predictive scaling.

    Args:
        repo_root: Path to repository root

    Returns:
        Predictive scaling instance
    """
    global _predictive_scaling

    with _scaling_lock:
        if _predictive_scaling is None:
            _predictive_scaling = PredictiveScaling(repo_root)
        return _predictive_scaling
