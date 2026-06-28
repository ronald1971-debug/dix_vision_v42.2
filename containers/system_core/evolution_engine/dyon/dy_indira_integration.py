"""evolution_engine.dyon.indira_integration — DYON-INDIRA Integration for System-Optimization Synergy.

Integration layer between DYON system cognition and INDIRA market intelligence for optimal system performance.

This implementation provides DYON-INDIRA integration capabilities:
- System performance insights for INDIRA optimization
- Resource scaling recommendations for trading operations
- Predictive maintenance integration with trading schedules
- Real-time monitoring integration with market data processing
- Dependency analysis for trading system reliability
- System behavior modeling for trading system optimization
- ML predictions for trading system resource needs
- Cost optimization for trading infrastructure

Authority (L2/B1): evolution_engine.* only at module level.
DYON provides system insights for INDIRA optimization, never for trading operations.
DYON maintains strict domain separation: SYSTEM (DYON) vs MARKET (INDIRA).
"""

from __future__ import annotations

import copy
import logging
import threading
import time
from collections import defaultdict, deque
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Dict, List, Optional, Tuple

_logger = logging.getLogger(__name__)


class IntegrationMode(Enum):
    """Modes of DYON-INDIRA integration."""

    PASSIVE = "passive"  # DYON provides recommendations only
    ADVISORY = "advisory"  # DYON provides actionable insights
    AUTOMATED = "automated"  # DYON recommendations are automatically applied (governed)


class InsightType(Enum):
    """Types of insights DYON provides to INDIRA."""

    RESOURCE_ALLOCATION = "resource_allocation"
    PERFORMANCE_OPTIMIZATION = "performance_optimization"
    MAINTENANCE_SCHEDULING = "maintenance_scheduling"
    SYSTEM_HEALTH = "system_health"
    CAPACITY_PLANNING = "capacity_planning"
    DEPENDENCY_RISK = "dependency_risk"
    COST_OPTIMIZATION = "cost_optimization"


@dataclass
class SystemInsight:
    """Insight from DYON for INDIRA optimization."""

    insight_id: str
    insight_type: InsightType
    timestamp: float
    source_component: str  # Which DYON component generated this
    title: str
    description: str
    actionable: bool
    priority: str  # critical, high, medium, low
    confidence: float
    data: Dict[str, Any] = field(default_factory=dict)
    recommendations: List[str] = field(default_factory=list)
    estimated_impact: Dict[str, float] = field(default_factory=dict)


@dataclass
class TradingScheduleRecommendation:
    """Recommendation for trading schedule optimization based on system state."""

    recommendation_id: str
    timestamp: float
    trading_activity: str  # high_frequency, algorithmic, discretionary, etc.
    system_state: str  # optimal, degraded, maintenance_needed
    recommended_action: str
    reason: str
    time_window: Tuple[float, float]  # (start_time, end_time)
    resource_requirements: Dict[str, float] = field(default_factory=dict)


@dataclass
class IntegrationMetrics:
    """Metrics for DYON-INDIRA integration."""

    insights_generated: int = 0
    insights_applied: int = 0
    recommendations_followed: int = 0
    system_impact_score: float = 0.0
    cost_savings: float = 0.0
    performance_improvement: float = 0.0
    uptime_improvement: float = 0.0


class DyonIndiraIntegration:
    """Integration layer between DYON and INDIRA systems.

    DYON provides system cognition insights to optimize INDIRA's performance
    without performing any trading operations or market analysis.
    """

    def __init__(self, repo_root: str = "."):
        """Initialize DYON-INDIRA integration.

        Args:
            repo_root: Path to repository root
        """
        self.repo_root = repo_root
        self._lock = threading.Lock()
        self._integration_mode = IntegrationMode.ADVISORY
        self._insights: List[SystemInsight] = []
        self._schedule_recommendations: List[TradingScheduleRecommendation] = []
        self._metrics = IntegrationMetrics()
        self._insight_history: deque = deque(maxlen=1000)

        # Component references (would be injected in production)
        self._predictive_maintenance = None
        self._system_behavior_modeling = None
        self._dependency_management = None
        self._ml_predictive_engine = None
        self._realtime_simulation = None
        self._predictive_scaling = None

        _logger.info(
            f"[DyonIndiraIntegration] Initialized with repo_root={repo_root}, "
            f"mode={self._integration_mode.value}"
        )

    def set_integration_mode(self, mode: IntegrationMode) -> None:
        """Set integration mode.

        Args:
            mode: Integration mode to use
        """
        with self._lock:
            self._integration_mode = mode
            _logger.info(f"[DyonIntIndiraegration] Set integration mode: {mode.value}")

    def register_dy_component(self, component_name: str, component_instance: Any) -> bool:
        """Register a DYON component for integration.

        Args:
            component_name: Name of the component
            component_instance: Component instance

        Returns:
            True if registered successfully
        """
        with self._lock:
            component_map = {
                "predictive_maintenance": "_predictive_maintenance",
                "system_behavior_modeling": "_system_behavior_modeling",
                "dependency_management": "_dependency_management",
                "ml_predictive_engine": "_ml_predictive_engine",
                "realtime_simulation": "_realtime_simulation",
                "predictive_scaling": "_predictive_scaling",
            }

            if component_name not in component_map:
                _logger.warning(f"[DyonIndiraIntegration] Unknown component: {component_name}")
                return False

            setattr(self, component_map[component_name], component_instance)
            _logger.info(f"[DyonIndiraIntegration] Registered component: {component_name}")

            return True

    def generate_system_insights(self) -> List[SystemInsight]:
        """Generate system insights for INDIRA optimization.

        Returns:
            List of system insights
        """
        with self._lock:
            insights = []

            # Generate insights from predictive maintenance
            if self._predictive_maintenance:
                maintenance_insights = self._generate_maintenance_insights()
                insights.extend(maintenance_insights)

            # Generate insights from system behavior modeling
            if self._system_behavior_modeling:
                behavior_insights = self._generate_behavior_insights()
                insights.extend(behavior_insights)

            # Generate insights from dependency management
            if self._dependency_management:
                dependency_insights = self._generate_dependency_insights()
                insights.extend(dependency_insights)

            # Generate insights from predictive scaling
            if self._predictive_scaling:
                scaling_insights = self._generate_scaling_insights()
                insights.extend(scaling_insights)

            # Store insights
            self._insights = insights
            self._insight_history.extend(insights)
            self._metrics.insights_generated += len(insights)

            _logger.info(f"[DyonIndiraIntegration] Generated {len(insights)} system insights")

            return insights

    def _generate_maintenance_insights(self) -> List[SystemInsight]:
        """Generate insights from predictive maintenance.

        Returns:
            List of maintenance insights
        """
        insights = []

        # Simulate predictive maintenance insights
        # In production, this would call actual predictive maintenance methods
        insights.append(
            SystemInsight(
                insight_id=f"maint_insight_{int(time.time())}",
                insight_type=InsightType.MAINTENANCE_SCHEDULING,
                timestamp=time.time(),
                source_component="predictive_maintenance",
                title="Predicted database performance degradation",
                description="Database performance degradation predicted in 24-48 hours",
                actionable=True,
                priority="high",
                confidence=0.8,
                data={
                    "affected_component": "database",
                    "predicted_time_to_issue": 36.0,
                    "severity": "high",
                },
                recommendations=[
                    "Schedule database maintenance during low-activity trading periods",
                    "Increase database capacity before predicted degradation",
                    "Monitor database metrics more closely",
                ],
                estimated_impact={"performance": 0.3, "reliability": 0.2},
            )
        )

        return insights

    def _generate_behavior_insights(self) -> List[SystemInsight]:
        """Generate insights from system behavior modeling.

        Returns:
            List of behavior insights
        """
        insights = []

        # Simulate system behavior insights
        insights.append(
            SystemInsight(
                insight_id=f"behavior_insight_{int(time.time())}",
                insight_type=InsightType.PERFORMANCE_OPTIMIZATION,
                timestamp=time.time(),
                source_component="system_behavior_modeling",
                title="System bottleneck identified in signal processing",
                description="Signal processing latency increases under high load conditions",
                actionable=True,
                priority="medium",
                confidence=0.7,
                data={
                    "bottleneck_component": "signal_processing",
                    "load_threshold": "80% CPU",
                    "current_latency_ms": 150,
                    "target_latency_ms": 100,
                },
                recommendations=[
                    "Scale signal processing resources during high-frequency trading periods",
                    "Implement async processing for non-critical signals",
                    "Add caching for repeated signal priority calculations",
                ],
                estimated_impact={"performance": 0.4, "cost": 0.1},
            )
        )

        return insights

    def _generate_dependency_insights(self) -> List[SystemInsight]:
        """Generate insights from dependency management.

        Returns:
            List of dependency insights
        """
        insights = []

        # Simulate dependency insights
        insights.append(
            SystemInsight(
                insight_id=f"dep_insight_{int(time.time())}",
                insight_type=InsightType.DEPENDENCY_RISK,
                timestamp=time.time(),
                source_component="dependency_management",
                title="Critical dependency requires update for security",
                description="Trading system dependency has security vulnerability",
                actionable=True,
                priority="critical",
                confidence=0.9,
                data={
                    "dependency_name": "trading-connector-lib",
                    "current_version": "2.1.0",
                    "vulnerability_severity": "HIGH",
                    "patched_version": "2.1.3",
                },
                recommendations=[
                    "Schedule immediate update of trading-connector-lib",
                    "Test patched version in staging environment",
                    "Coordinate update with trading desk for minimal disruption",
                ],
                estimated_impact={"security": 0.8, "reliability": 0.3},
            )
        )

        return insights

    def _generate_scaling_insights(self) -> List[SystemInsight]:
        """Generate insights from predictive scaling.

        Returns:
            List of scaling insights
        """
        insights = []

        # Simulate scaling insights
        insights.append(
            SystemInsight(
                insight_id=f"scaling_insight_{int(time.time())}",
                insight_type=InsightType.RESOURCE_ALLOCATION,
                timestamp=time.time(),
                source_component="predictive_scaling",
                title="Predicted resource needs for market opening",
                description="Increased CPU and memory resources predicted for market open period",
                actionable=True,
                priority="high",
                confidence=0.8,
                data={
                    "resource_type": "CPU",
                    "current_capacity": "50 cores",
                    "predicted_capacity": "80 cores",
                    "time_window": "09:30-10:00 EST",
                },
                recommendations=[
                    "Scale CPU resources 30 minutes before market open",
                    "Scale memory resources to handle increased data processing",
                    "Pre-allocate database connections for expected load",
                ],
                estimated_impact={"performance": 0.5, "cost": 0.2},
            )
        )

        return insights

    def generate_trading_schedule_recommendations(self) -> List[TradingScheduleRecommendation]:
        """Generate trading schedule recommendations based on system state.

        Returns:
            List of trading schedule recommendations
        """
        with self._lock:
            recommendations = []

            current_time = time.time()

            # Generate recommendation for high-frequency trading
            if self._predictive_scaling:
                system_state = self._assess_system_state()

                if system_state == "optimal":
                    recommendations.append(
                        TradingScheduleRecommendation(
                            recommendation_id=f"schedule_rec_{int(time.time())}_1",
                            timestamp=current_time,
                            trading_activity="high_frequency",
                            system_state=system_state,
                            recommended_action="proceed_with_normal_operations",
                            reason="System resources optimal for high-frequency trading",
                            time_window=(current_time, current_time + 3600),
                            resource_requirements={
                                "cpu_cores": 80,
                                "memory_gb": 128,
                                "network_bandwidth_mbps": 1000,
                            },
                        )
                    )
                elif system_state == "degraded":
                    recommendations.append(
                        TradingScheduleRecommendation(
                            recommendation_id=f"schedule_rec_{int(time.time())}_2",
                            timestamp=current_time,
                            trading_activity="high_frequency",
                            system_state=system_state,
                            recommended_action="reduce_frequency_or_scale_resources",
                            reason="System degraded - consider reducing trading frequency or scaling resources",
                            time_window=(current_time, current_time + 1800),
                            resource_requirements={
                                "cpu_cores": 60,
                                "memory_gb": 96,
                                "network_bandwidth_mbps": 750,
                            },
                        )
                    )
                else:
                    recommendations.append(
                        TradingScheduleRecommendation(
                            recommendation_id=f"schedule_rec_{int(time.time())}_3",
                            timestamp=current_time,
                            trading_activity="high_frequency",
                            system_state=system_state,
                            recommended_action="postpone_or_use_alternate_strategy",
                            reason="System requires maintenance - postpone high-frequency trading",
                            time_window=(current_time + 3600, current_time + 7200),
                            resource_requirements={
                                "cpu_cores": 40,
                                "memory_gb": 64,
                                "network_bandwidth_mbps": 500,
                            },
                        )
                    )

            self._schedule_recommendations = recommendations

            _logger.info(
                f"[DyonIndiraIntegration] Generated {len(recommendations)} "
                f"trading schedule recommendations"
            )

            return recommendations

    def _assess_system_state(self) -> str:
        """Assess current system state.

        Returns:
            System state: optimal, degraded, or maintenance_needed
        """
        # Simulate system state assessment
        # In production, this would aggregate metrics from all DYON components

        if self._predictive_scaling:
            metrics = self._predictive_scaling.get_resource_summary()

            # Simple heuristic based on resource utilization
            if metrics.get("active_recommendations", 0) == 0:
                return "optimal"
            elif metrics.get("active_recommendations", 0) < 3:
                return "degraded"
            else:
                return "maintenance_needed"

        return "optimal"

    def apply_insight(self, insight_id: str) -> bool:
        """Apply a system insight (simulate application).

        Args:
            insight_id: Insight identifier

        Returns:
            True if applied successfully
        """
        with self._lock:
            insight = next((i for i in self._insights if i.insight_id == insight_id), None)

            if not insight:
                _logger.warning(f"[DyonIndiraIntegration] Unknown insight: {insight_id}")
                return False

            if not insight.actionable:
                _logger.warning(f"[DyonIndiraIntegration] Insight not actionable: {insight_id}")
                return False

            # Simulate applying insight
            # In production, this would execute the recommendations
            _logger.info(f"[DyonIndiraIntegration] Applied insight: {insight_id}")

            self._metrics.insights_applied += 1

            return True

    def get_integration_metrics(self) -> IntegrationMetrics:
        """Get integration metrics.

        Returns:
            Integration metrics
        """
        with self._lock:
            return copy.deepcopy(self._metrics)

    def get_active_insights(self) -> List[SystemInsight]:
        """Get active system insights.

        Returns:
            List of active insights
        """
        with self._lock:
            return list(self._insights)

    def get_schedule_recommendations(self) -> List[TradingScheduleRecommendation]:
        """Get trading schedule recommendations.

        Returns:
            List of schedule recommendations
        """
        with self._lock:
            return list(self._schedule_recommendations)

    def generate_integration_report(self) -> Dict[str, Any]:
        """Generate comprehensive integration report.

        Returns:
            Integration report
        """
        with self._lock:
            return {
                "integration_mode": self._integration_mode.value,
                "active_insights": len(self._insights),
                "schedule_recommendations": len(self._schedule_recommendations),
                "metrics": {
                    "insights_generated": self._metrics.insights_generated,
                    "insights_applied": self._metrics.insights_applied,
                    "recommendations_followed": self._metrics.recommendations_followed,
                    "system_impact_score": self._metrics.system_impact_score,
                    "cost_savings": self._metrics.cost_savings,
                    "performance_improvement": self._metrics.performance_improvement,
                    "uptime_improvement": self._metrics.uptime_improvement,
                },
                "insights_by_type": self._count_insights_by_type(),
                "insights_by_priority": self._count_insights_by_priority(),
                "generated_at": time.time(),
            }

    def _count_insights_by_type(self) -> Dict[str, int]:
        """Count insights by type.

        Returns:
            Dictionary mapping insight types to counts
        """
        counts = defaultdict(int)
        for insight in self._insights:
            counts[insight.insight_type.value] += 1
        return dict(counts)

    def _count_insights_by_priority(self) -> Dict[str, int]:
        """Count insights by priority.

        Returns:
            Dictionary mapping priorities to counts
        """
        counts = defaultdict(int)
        for insight in self._insights:
            counts[insight.priority] += 1
        return dict(counts)


# Singleton instance
_dy_indira_integration: Optional[DyonIndiraIntegration] = None
_integration_lock = threading.Lock()


def get_dy_indira_integration(repo_root: str = ".") -> DyonIndiraIntegration:
    """Get singleton instance of DYON-INDIRA integration.

    Args:
        repo_root: Path to repository root

    Returns:
        DYON-INDIRA integration instance
    """
    global _dy_indira_integration

    with _integration_lock:
        if _dy_indira_integration is None:
            _dy_indira_integration = DyonIndiraIntegration(repo_root)
        return _dy_indira_integration
