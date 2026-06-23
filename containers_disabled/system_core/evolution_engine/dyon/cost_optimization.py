"""evolution_engine.dyon.cost_optimization — Cost Optimization for DYON Cloud Resource Management.

Cost optimization capabilities for cloud resource management and infrastructure optimization.

This implementation provides cost optimization capabilities:
- Cloud resource cost analysis
- Resource utilization cost optimization
- Right-sizing recommendations
- Spot instance analysis
- Reserved instance optimization
- Multi-cloud cost comparison
- Cost anomaly detection
- Budget forecasting and optimization

Authority (L2/B1): evolution_engine.* only at module level.
DYON provides cost optimization for system resource management, never for trading purposes.
"""

from __future__ import annotations

import logging
import statistics
import threading
import time
from collections import defaultdict
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Dict, List, Optional, Tuple

_logger = logging.getLogger(__name__)


class CloudProvider(Enum):
    """Cloud service providers."""

    AWS = "aws"
    GCP = "gcp"
    AZURE = "azure"
    ALIBABA = "alibaba"
    OCI = "oracle"
    CUSTOM = "custom"


class ResourceType(Enum):
    """Types of cloud resources."""

    COMPUTE = "compute"
    STORAGE = "storage"
    NETWORK = "network"
    DATABASE = "database"
    CONTAINER = "container"
    SERVERLESS = "serverless"
    LOAD_BALANCER = "load_balancer"


class InstanceType(Enum):
    """Types of compute instances."""

    ON_DEMAND = "on_demand"
    RESERVED = "reserved"
    SPOT = "spot"
    PREEMPTIBLE = "preemptible"
    DEDICATED = "dedicated"


class OptimizationStrategy(Enum):
    """Cost optimization strategies."""

    RIGHT_SIZING = "right_sizing"
    INSTANCE_TYPE_CHANGE = "instance_type_change"
    SCHEDULED_SCALING = "scheduled_scaling"
    SPOT_INSTANCE = "spot_instance"
    RESERVED_INSTANCE = "reserved_instance"
    MULTI_REGION = "multi_region"
    ARCHITECTURE_OPTIMIZATION = "architecture_optimization"


@dataclass
class CloudResource:
    """Cloud resource definition."""

    resource_id: str
    resource_type: ResourceType
    provider: CloudProvider
    instance_type: str  # e.g., t3.medium, n1-standard-2
    region: str
    availability_zone: str
    cpu_cores: float
    memory_gb: float
    storage_gb: float
    hourly_cost: float
    monthly_cost: float
    utilization: float  # 0.0 to 1.0
    tags: Dict[str, str] = field(default_factory=dict)
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class CostOptimization:
    """Cost optimization recommendation."""

    optimization_id: str
    resource_id: str
    strategy: OptimizationStrategy
    current_monthly_cost: float
    optimized_monthly_cost: float
    savings_percentage: float
    estimated_monthly_savings: float
    confidence: float
    risk_level: str  # low, medium, high
    implementation_effort: str  # low, medium, high
    description: str
    action_steps: List[str] = field(default_factory=list)
    prerequisites: List[str] = field(default_factory=list)


@dataclass
class CostAnomaly:
    """Anomaly detected in costs."""

    anomaly_id: str
    timestamp: float
    resource_id: str
    anomaly_type: str  # spike, unexpected_charge, zero_cost, budget_exceeded
    expected_cost: float
    actual_cost: float
    deviation_percentage: float
    severity: str  # low, medium, high, critical
    description: str
    possible_causes: List[str] = field(default_factory=list)
    recommendations: List[str] = field(default_factory=list)


@dataclass
class BudgetForecast:
    """Budget forecast for cloud resources."""

    forecast_id: str
    period_start: float
    period_end: float
    forecasted_cost: float
    confidence_interval: Tuple[float, float]  # (lower, upper)
    cost_drivers: List[str] = field(default_factory=list)
    optimization_opportunities: List[str] = field(default_factory=list)
    recommended_budget: float = 0.0


class CostOptimizationEngine:
    """Cost optimization engine for cloud resource management.

    DYON uses this to optimize cloud resource costs for system efficiency
    without performing trading operations.
    """

    def __init__(self, repo_root: str = "."):
        """Initialize cost optimization engine.

        Args:
            repo_root: Path to repository root
        """
        self.repo_root = repo_root
        self._lock = threading.Lock()
        self._resources: Dict[str, CloudResource] = {}
        self._optimizations: List[CostOptimization] = []
        self._cost_anomalies: List[CostAnomaly] = []
        self._budget_forecasts: List[BudgetForecast] = []
        self._cost_history: Dict[str, List[float]] = defaultdict(list)
        self._pricing_cache: Dict[str, float] = {}

        # Initialize pricing data
        self._initialize_pricing_cache()

        _logger.info(
            f"[CostOptimizationEngine] Initialized with repo_root={repo_root}, "
            f"resources={len(self._resources)}"
        )

    def _initialize_pricing_cache(self) -> None:
        """Initialize pricing cache for common instance types.

        In production, this would query actual cloud provider pricing APIs.
        """
        # Simplified pricing data (in USD per hour)
        self._pricing_cache = {
            # AWS pricing (simplified)
            "aws_t3_micro": 0.008,
            "aws_t3_small": 0.016,
            "aws_t3_medium": 0.032,
            "aws_t3_large": 0.064,
            "aws_m5_large": 0.096,
            "aws_m5_xlarge": 0.192,
            "aws_c5_large": 0.102,
            "aws_c5_xlarge": 0.204,
            # GCP pricing (simplified)
            "gcp_n1_standard_1": 0.047,
            "gcp_n1_standard_2": 0.094,
            "gcp_n1_standard_4": 0.188,
            "gcp_n1_highmem_4": 0.248,
            "gcp_n1_highcpu_4": 0.159,
            # Azure pricing (simplified)
            "azure_b2s": 0.04,
            "azure_b2ms": 0.08,
            "azure_b4ms": 0.16,
            "azure_d2s_v3": 0.13,
            "azure_d4s_v3": 0.26,
        }

        _logger.info("[CostOptimizationEngine] Initialized pricing cache")

    def add_resource(self, resource: CloudResource) -> bool:
        """Add a cloud resource.

        Args:
            resource: Cloud resource to add

        Returns:
            True if added successfully
        """
        with self._lock:
            if resource.resource_id in self._resources:
                _logger.warning(f"[CostOptimizationEngine] Resource exists: {resource.resource_id}")
                return False

            self._resources[resource.resource_id] = resource

            # Add to cost history
            self._cost_history[resource.resource_id].append(resource.hourly_cost)

            _logger.info(f"[CostOptimizationEngine] Added resource: {resource.resource_id}")

            return True

    def analyze_right_sizing(self) -> List[CostOptimization]:
        """Analyze resources for right-sizing opportunities.

        Returns:
            List of right-sizing optimizations
        """
        optimizations = []

        with self._lock:
            for resource_id, resource in self._resources.items():
                # Check for over-provisioned resources
                if resource.utilization < 0.3:  # Less than 30% utilization
                    # Find appropriate smaller instance type
                    recommended_type = self._find_smaller_instance_type(
                        resource.provider, resource.instance_type, resource.utilization
                    )

                    if recommended_type:
                        new_hourly_cost = self._pricing_cache.get(
                            f"{resource.provider.value}_{recommended_type}", resource.hourly_cost
                        )

                        current_monthly_cost = resource.monthly_cost
                        optimized_monthly_cost = (
                            new_hourly_cost * 730
                        )  # Approximate hours per month
                        savings = current_monthly_cost - optimized_monthly_cost
                        savings_percentage = (
                            (savings / current_monthly_cost * 100)
                            if current_monthly_cost > 0
                            else 0
                        )

                        optimization = CostOptimization(
                            optimization_id=f"rightsize_{resource_id}_{int(time.time())}",
                            resource_id=resource_id,
                            strategy=OptimizationStrategy.RIGHT_SIZING,
                            current_monthly_cost=current_monthly_cost,
                            optimized_monthly_cost=optimized_monthly_cost,
                            savings_percentage=savings_percentage,
                            estimated_monthly_savings=savings,
                            confidence=0.8 if resource.utilization < 0.2 else 0.6,
                            risk_level="low",
                            implementation_effort="low",
                            description=f"Right-size {resource.resource_id} from {resource.instance_type} to {recommended_type}",
                            action_steps=[
                                f"Identify current workload patterns",
                                f"Select appropriate smaller instance type: {recommended_type}",
                                f"Schedule maintenance window for migration",
                                f"Monitor performance after migration",
                            ],
                            prerequisites=[
                                "Validate performance requirements",
                                "Ensure application compatibility with new instance type",
                            ],
                        )

                        optimizations.append(optimization)

                # Check for under-provisioned resources
                elif resource.utilization > 0.8:  # More than 80% utilization
                    recommended_type = self._find_larger_instance_type(
                        resource.provider, resource.instance_type, resource.utilization
                    )

                    if recommended_type:
                        new_hourly_cost = self._pricing_cache.get(
                            f"{resource.provider.value}_{recommended_type}",
                            resource.hourly_cost * 1.5,  # Estimate
                        )

                        current_monthly_cost = resource.monthly_cost
                        optimized_monthly_cost = new_hourly_cost * 730
                        additional_cost = optimized_monthly_cost - current_monthly_cost

                        # For under-provisioned, it's not a cost saving but performance optimization
                        optimization = CostOptimization(
                            optimization_id=f"rightsize_{resource_id}_{int(time.time())}",
                            resource_id=resource_id,
                            strategy=OptimizationStrategy.RIGHT_SIZING,
                            current_monthly_cost=current_monthly_cost,
                            optimized_monthly_cost=optimized_monthly_cost,
                            savings_percentage=0.0,
                            estimated_monthly_savings=-additional_cost,  # Negative indicates cost increase
                            confidence=0.9,
                            risk_level="low",
                            implementation_effort="low",
                            description=f"Scale up {resource.resource_id} from {resource.instance_type} to {recommended_type} for performance",
                            action_steps=[
                                f"Analyze current performance bottlenecks",
                                f"Select appropriate larger instance type: {recommended_type}",
                                f"Scale up during off-peak hours",
                                f"Monitor performance improvement",
                            ],
                            prerequisites=[
                                "Budget approval for increased costs",
                                "Performance improvement validation",
                            ],
                        )

                        optimizations.append(optimization)

        self._optimizations.extend(optimizations)

        _logger.info(
            f"[CostOptimizationEngine] Generated {len(optimizations)} right-sizing optimizations"
        )

        return optimizations

    def _find_smaller_instance_type(
        self, provider: CloudProvider, current_type: str, utilization: float
    ) -> Optional[str]:
        """Find appropriate smaller instance type.

        Args:
            provider: Cloud provider
            current_type: Current instance type
            utilization: Current utilization

        Returns:
            Recommended smaller instance type or None
        """
        # Simplified logic - in production would use instance family mappings
        smaller_types = {
            "aws": {
                "t3_large": "t3_medium",
                "t3_medium": "t3_small",
                "t3_small": "t3_micro",
                "m5_xlarge": "m5_large",
                "m5_large": "m5_medium",
                "c5_xlarge": "c5_large",
                "c5_large": "c5_medium",
            },
            "gcp": {
                "n1_standard_4": "n1_standard_2",
                "n1_standard_2": "n1_standard_1",
                "n1_highmem_4": "n1_standard_2",
            },
            "azure": {"d4s_v3": "d2s_v3", "d2s_v3": "b4ms", "b4ms": "b2ms"},
        }

        provider_types = smaller_types.get(provider.value, {})
        return provider_types.get(current_type)

    def _find_larger_instance_type(
        self, provider: CloudProvider, current_type: str, utilization: float
    ) -> Optional[str]:
        """Find appropriate larger instance type.

        Args:
            provider: Cloud provider
            current_type: Current instance type
            utilization: Current utilization

        Returns:
            Recommended larger instance type or None
        """
        # Simplified logic - in production would use instance family mappings
        larger_types = {
            "aws": {
                "t3_micro": "t3_small",
                "t3_small": "t3_medium",
                "t3_medium": "t3_large",
                "m5_large": "m5_xlarge",
                "c5_large": "c5_xlarge",
            },
            "gcp": {
                "n1_standard_1": "n1_standard_2",
                "n1_standard_2": "n1_standard_4",
                "n1_standard_4": "n1_highmem_4",
            },
            "azure": {"b2ms": "b4ms", "b4ms": "d2s_v3", "d2s_v3": "d4s_v3"},
        }

        provider_types = larger_types.get(provider.value, {})
        return provider_types.get(current_type)

    def analyze_spot_instances(self) -> List[CostOptimization]:
        """Analyze resources for spot instance opportunities.

        Returns:
            List of spot instance optimizations
        """
        optimizations = []

        with self._lock:
            for resource_id, resource in self._resources.items():
                # Check if resource is suitable for spot instances
                if self._is_suitable_for_spot(resource):
                    # Spot instances typically cost 70-90% less than on-demand
                    spot_discount = 0.7  # 70% discount
                    spot_hourly_cost = resource.hourly_cost * (1 - spot_discount)

                    current_monthly_cost = resource.monthly_cost
                    optimized_monthly_cost = spot_hourly_cost * 730
                    savings = current_monthly_cost - optimized_monthly_cost
                    savings_percentage = (
                        (savings / current_monthly_cost * 100) if current_monthly_cost > 0 else 0
                    )

                    optimization = CostOptimization(
                        optimization_id=f"spot_{resource_id}_{int(time.time())}",
                        resource_id=resource_id,
                        strategy=OptimizationStrategy.SPOT_INSTANCE,
                        current_monthly_cost=current_monthly_cost,
                        optimized_monthly_cost=optimized_monthly_cost,
                        savings_percentage=savings_percentage,
                        estimated_monthly_savings=savings,
                        confidence=0.7,
                        risk_level="medium",
                        implementation_effort="medium",
                        description=f"Migrate {resource.resource_id} to spot instances for 70% cost savings",
                        action_steps=[
                            "Evaluate workload tolerance for interruptions",
                            "Implement checkpointing and state recovery",
                            "Use spot instance fleets for redundancy",
                            "Configure auto-scaling with spot instances",
                        ],
                        prerequisites=[
                            "Workload must be interruptible",
                            "State management and recovery mechanisms",
                            "Fallback to on-demand instances",
                        ],
                    )

                    optimizations.append(optimization)

        self._optimizations.extend(optimizations)

        _logger.info(
            f"[CostOptimizationEngine] Generated {len(optimizations)} spot instance optimizations"
        )

        return optimizations

    def _is_suitable_for_spot(self, resource: CloudResource) -> bool:
        """Check if resource is suitable for spot instances.

        Args:
            resource: Cloud resource

        Returns:
            True if suitable for spot instances
        """
        # Heuristics for spot instance suitability
        # In production, this would be more sophisticated

        # Compute and batch processing workloads are good candidates
        suitable_resource_types = [ResourceType.COMPUTE, ResourceType.CONTAINER]

        if resource.resource_type not in suitable_resource_types:
            return False

        # Workloads with fault tolerance are good candidates
        # Check if resource has tags indicating suitability
        fault_tolerant = resource.tags.get("fault_tolerant", "false") == "true"
        batch_workload = resource.tags.get("workload_type", "") == "batch"

        return fault_tolerant or batch_workload

    def analyze_reserved_instances(self) -> List[CostOptimization]:
        """Analyze resources for reserved instance opportunities.

        Returns:
            List of reserved instance optimizations
        """
        optimizations = []

        with self._lock:
            for resource_id, resource in self._resources.items():
                # Reserved instances require stable long-term usage
                if resource.utilization > 0.5:  # Consistently used
                    # Reserved instances typically offer 30-75% savings
                    # Assume 1-year or 3-year reservation
                    reserved_discount = 0.5  # 50% discount
                    reserved_hourly_cost = resource.hourly_cost * (1 - reserved_discount)

                    current_monthly_cost = resource.monthly_cost
                    optimized_monthly_cost = reserved_hourly_cost * 730
                    savings = current_monthly_cost - optimized_monthly_cost
                    savings_percentage = (
                        (savings / current_monthly_cost * 100) if current_monthly_cost > 0 else 0
                    )

                    optimization = CostOptimization(
                        optimization_id=f"reserved_{resource_id}_{int(time.time())}",
                        resource_id=resource_id,
                        strategy=OptimizationStrategy.RESERVED_INSTANCE,
                        current_monthly_cost=current_monthly_cost,
                        optimized_monthly_cost=optimized_monthly_cost,
                        savings_percentage=savings_percentage,
                        estimated_monthly_savings=savings,
                        confidence=0.8,
                        risk_level="low",
                        implementation_effort="low",
                        description=f"Purchase reserved instances for {resource.resource_id} for 50% cost savings",
                        action_steps=[
                            "Analyze usage patterns over time",
                            "Commit to 1-year or 3-year reservation",
                            "Purchase reserved capacity",
                            "Update cost allocation",
                        ],
                        prerequisites=[
                            "Stable, long-term workload",
                            "Commitment to resource reservation period",
                        ],
                    )

                    optimizations.append(optimization)

        self._optimizations.extend(optimizations)

        _logger.info(
            f"[CostOptimizationEngine] Generated {len(optimizations)} reserved instance optimizations"
        )

        return optimizations

    def detect_cost_anomalies(self, threshold: float = 0.5) -> List[CostAnomaly]:
        """Detect anomalies in cloud costs.

        Args:
            threshold: Anomaly detection threshold (percentage deviation)

        Returns:
            List of cost anomalies
        """
        anomalies = []

        with self._lock:
            for resource_id, cost_history in self._cost_history.items():
                if len(cost_history) < 10:
                    continue

                # Calculate expected cost based on historical average
                avg_cost = statistics.mean(cost_history[:-1])  # Exclude most recent
                recent_cost = cost_history[-1]

                # Calculate deviation
                if avg_cost > 0:
                    deviation = abs(recent_cost - avg_cost) / avg_cost

                    if deviation > threshold:
                        anomaly_type = "spike" if recent_cost > avg_cost else "unexpected_charge"
                        severity = "high" if deviation > 1.0 else "medium"

                        if deviation > 2.0:
                            severity = "critical"

                        anomaly = CostAnomaly(
                            anomaly_id=f"anomaly_{resource_id}_{int(time.time())}",
                            timestamp=time.time(),
                            resource_id=resource_id,
                            anomaly_type=anomaly_type,
                            expected_cost=avg_cost,
                            actual_cost=recent_cost,
                            deviation_percentage=deviation * 100,
                            severity=severity,
                            description=f"Cost anomaly detected for {resource_id}: {deviation:.1%} deviation",
                            possible_causes=[
                                "Unexpected resource scaling",
                                "Increase in resource usage",
                                "Pricing changes",
                                "Configuration errors",
                                "Data transfer charges",
                            ],
                            recommendations=[
                                "Review recent scaling activities",
                                "Check resource utilization",
                                "Verify configuration changes",
                                "Review billing breakdown",
                            ],
                        )

                        anomalies.append(anomaly)

        self._cost_anomalies.extend(anomalies)

        _logger.info(f"[CostOptimizationEngine] Detected {len(anomalies)} cost anomalies")

        return anomalies

    def generate_budget_forecast(self, months: int = 12) -> BudgetForecast:
        """Generate budget forecast for cloud resources.

        Args:
            months: Number of months to forecast

        Returns:
            Budget forecast
        """
        with self._lock:
            current_time = time.time()
            forecast_id = f"forecast_{int(current_time)}"

            # Calculate total current monthly cost
            total_monthly_cost = sum(resource.monthly_cost for resource in self._resources.values())

            # Forecast based on historical trends (simplified)
            # In production, would use more sophisticated forecasting
            forecasted_cost = total_monthly_cost * (
                1 + 0.05 * months
            )  # 5% monthly growth assumption

            # Confidence interval (simplified)
            confidence_interval = (forecasted_cost * 0.8, forecasted_cost * 1.2)

            # Identify cost drivers
            cost_drivers = [
                resource.resource_id
                for resource in sorted(
                    self._resources.values(), key=lambda x: x.monthly_cost, reverse=True
                )[:5]
            ]

            # Identify optimization opportunities
            optimization_opportunities = []
            for opt in self._optimizations:
                if opt.estimated_monthly_savings > 0:
                    optimization_opportunities.append(opt.description)

            forecast = BudgetForecast(
                forecast_id=forecast_id,
                period_start=current_time,
                period_end=current_time + (months * 30 * 24 * 3600),
                forecasted_cost=forecasted_cost,
                confidence_interval=confidence_interval,
                cost_drivers=cost_drivers,
                optimization_opportunities=optimization_opportunities,
                recommended_budget=forecasted_cost * 0.9,  # 10% buffer
            )

            self._budget_forecasts.append(forecast)

            _logger.info(
                f"[CostOptimizationEngine] Generated budget forecast: ${forecasted_cost:.2f}"
            )

            return forecast

    def get_cost_summary(self) -> Dict[str, Any]:
        """Get cost summary for all resources.

        Returns:
            Cost summary
        """
        with self._lock:
            total_monthly_cost = sum(resource.monthly_cost for resource in self._resources.values())

            # Calculate by resource type
            costs_by_type = defaultdict(float)
            for resource in self._resources.values():
                costs_by_type[resource.resource_type.value] += resource.monthly_cost

            # Calculate by provider
            costs_by_provider = defaultdict(float)
            for resource in self._resources.values():
                costs_by_provider[resource.provider.value] += resource.monthly_cost

            return {
                "total_monthly_cost": total_monthly_cost,
                "total_annual_cost": total_monthly_cost * 12,
                "resource_count": len(self._resources),
                "costs_by_type": dict(costs_by_type),
                "costs_by_provider": dict(costs_by_provider),
                "optimization_count": len(self._optimizations),
                "potential_monthly_savings": sum(
                    opt.estimated_monthly_savings
                    for opt in self._optimizations
                    if opt.estimated_monthly_savings > 0
                ),
                "anomaly_count": len(self._cost_anomalies),
            }

    def get_optimizations(self, limit: int = 10) -> List[CostOptimization]:
        """Get cost optimization recommendations.

        Args:
            limit: Maximum number of optimizations to return

        Returns:
            List of optimizations
        """
        with self._lock:
            # Sort by estimated savings
            sorted_opts = sorted(
                self._optimizations, key=lambda x: x.estimated_monthly_savings, reverse=True
            )
            return list(sorted_opts[:limit])

    def get_cost_anomalies(self, limit: int = 10) -> List[CostAnomaly]:
        """Get cost anomalies.

        Args:
            limit: Maximum number of anomalies to return

        Returns:
            List of anomalies
        """
        with self._lock:
            return list(self._cost_anomalies[-limit:])


# Singleton instance
_cost_optimization_engine: Optional[CostOptimizationEngine] = None
_cost_lock = threading.Lock()


def get_cost_optimization_engine(repo_root: str = ".") -> CostOptimizationEngine:
    """Get singleton instance of cost optimization engine.

    Args:
        repo_root: Path to repository root

    Returns:
        Cost optimization engine instance
    """
    global _cost_optimization_engine

    with _cost_lock:
        if _cost_optimization_engine is None:
            _cost_optimization_engine = CostOptimizationEngine(repo_root)
        return _cost_optimization_engine
