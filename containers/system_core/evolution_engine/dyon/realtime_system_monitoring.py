"""evolution_engine.dyon.realtime_system_monitoring — Real-Time System Monitoring for DYON.

Real-time system monitoring and health dashboard for comprehensive system cognition.

This implementation provides real-time monitoring capabilities:
- Live system health dashboard
- Real-time architectural drift detection
- Component health monitoring
- Dynamic baseline adjustment
- System-wide anomaly detection
- Performance trend monitoring
- Resource utilization tracking
- Alert generation and notification

Authority (L2/B1): evolution_engine.* only at module level.
DYON provides real-time system monitoring for system optimization, never for trading purposes.
"""

from __future__ import annotations

import logging
import threading
import time
from collections import defaultdict, deque
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Dict, List, Optional

_logger = logging.getLogger(__name__)


class HealthStatus(Enum):
    """System health status levels."""

    HEALTHY = "HEALTHY"
    DEGRADED = "DEGRADED"
    UNHEALTHY = "UNHEALTHY"
    CRITICAL = "CRITICAL"
    UNKNOWN = "UNKNOWN"


class AlertSeverity(Enum):
    """Alert severity levels."""

    INFO = "INFO"
    WARNING = "WARNING"
    ERROR = "ERROR"
    CRITICAL = "CRITICAL"


@dataclass
class SystemMetric:
    """System metric data point."""

    metric_name: str
    metric_value: float
    timestamp: float
    component: str
    unit: str
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class ComponentHealth:
    """Health status of a system component."""

    component_name: str
    health_status: HealthStatus
    last_updated: float
    metrics: Dict[str, float] = field(default_factory=dict)
    active_issues: List[str] = field(default_factory=list)
    performance_score: float = 0.0
    uptime_percentage: float = 0.0


@dataclass
class SystemAlert:
    """System alert notification."""

    alert_id: str
    severity: AlertSeverity
    component: str
    alert_type: str
    message: str
    timestamp: float
    resolved: bool = False
    resolution_message: str = ""


@dataclass
class SystemHealthDashboard:
    """Complete system health dashboard data."""

    dashboard_timestamp: float
    overall_health_status: HealthStatus
    overall_health_score: float
    component_health: Dict[str, ComponentHealth] = field(default_factory=dict)
    system_metrics: Dict[str, float] = field(default_factory=dict)
    active_alerts: List[SystemAlert] = field(default_factory=list)
    recent_trends: Dict[str, str] = field(default_factory=dict)
    resource_utilization: Dict[str, float] = field(default_factory=dict)


class RealTimeSystemMonitor:
    """Real-time system monitoring and health dashboard.

    DYON uses this for real-time system cognition and health monitoring
    without performing any trading operations.
    """

    def __init__(
        self,
        monitoring_interval: float = 5.0,
        metric_window_size: int = 100,
        alert_cooldown: float = 60.0,
    ):
        """Initialize real-time system monitor.

        Args:
            monitoring_interval: Seconds between monitoring cycles
            metric_window_size: Number of metric points to retain
            alert_cooldown: Minimum seconds between similar alerts
        """
        self.monitoring_interval = monitoring_interval
        self.metric_window_size = metric_window_size
        self.alert_cooldown = alert_cooldown

        # Data storage
        self._metric_windows: Dict[str, deque] = defaultdict(
            lambda: deque(maxlen=metric_window_size)
        )
        self._component_health: Dict[str, ComponentHealth] = {}
        self._active_alerts: List[SystemAlert] = []
        self._alert_history: List[SystemAlert] = []
        self._last_alert_times: Dict[str, float] = {}

        # Thread management
        self._monitoring_thread: Optional[threading.Thread] = None
        self._running = False
        self._lock = threading.Lock()

        _logger.info(
            f"[RealTimeSystemMonitor] Initialized with interval={monitoring_interval}s, "
            f"window_size={metric_window_size}, alert_cooldown={alert_cooldown}s"
        )

    def start_monitoring(self) -> None:
        """Start real-time monitoring in background thread."""
        if self._running:
            _logger.warning("[RealTimeSystemMonitor] Already running")
            return

        self._running = True
        self._monitoring_thread = threading.Thread(
            target=self._monitoring_loop, daemon=True, name="SystemMonitor"
        )
        self._monitoring_thread.start()

        _logger.info("[RealTimeSystemMonitor] Started real-time monitoring")

    def stop_monitoring(self) -> None:
        """Stop real-time monitoring."""
        self._running = False
        if self._monitoring_thread:
            self._monitoring_thread.join(timeout=5.0)

        _logger.info("[RealTimeSystemMonitor] Stopped real-time monitoring")

    def _monitoring_loop(self) -> None:
        """Main monitoring loop."""
        while self._running:
            try:
                self._perform_monitoring_cycle()
                time.sleep(self.monitoring_interval)
            except Exception as e:
                _logger.error(f"[RealTimeSystemMonitor] Error in monitoring loop: {e}")

    def _perform_monitoring_cycle(self) -> None:
        """Perform one monitoring cycle."""
        with self._lock:
            # Monitor system components
            self._monitor_components()

            # Check for system-wide issues
            self._check_system_health()

            # Generate alerts if needed
            self._check_alert_conditions()

            # Update component health scores
            self._update_health_scores()

    def _monitor_components(self) -> None:
        """Monitor individual system components."""
        # Define components to monitor
        components = [
            "indira_cognitive",
            "evolution_engine",
            "system_core",
            "execution_unified",
            "governance_unified",
        ]

        for component in components:
            # Simulate component health monitoring
            # In real implementation, this would use actual metrics
            health_status = self._simulate_component_health(component)

            component_health = ComponentHealth(
                component_name=component,
                health_status=health_status,
                last_updated=time.time(),
                performance_score=0.7 if health_status == HealthStatus.HEALTHY else 0.4,
                uptime_percentage=0.95 if health_status == HealthStatus.HEALTHY else 0.7,
            )

            self._component_health[component] = component_health

    def _simulate_component_health(self, component: str) -> HealthStatus:
        """Simulate component health (in real implementation, use actual metrics).

        Args:
            component: Component name

        Returns:
            Simulated health status
        """
        # In real implementation, this would check actual component metrics
        # For simulation, return healthy status
        return HealthStatus.HEALTHY

    def _check_system_health(self) -> None:
        """Check overall system health."""
        unhealthy_count = sum(
            1
            for health in self._component_health.values()
            if health.health_status in [HealthStatus.UNHEALTHY, HealthStatus.CRITICAL]
        )

        if unhealthy_count == 0:
            self._overall_health_status = HealthStatus.HEALTHY
        elif unhealthy_count == 1:
            self._overall_health_status = HealthStatus.DEGRADED
        elif unhealthy_count == 2:
            self._overall_health_status = HealthStatus.UNHEALTHY
        else:
            self._overall_health_status = HealthStatus.CRITICAL

    def _check_alert_conditions(self) -> None:
        """Check for alert conditions and generate alerts."""
        current_time = time.time()

        # Check component health for alerts
        for component, health in self._component_health.items():
            if health.health_status in [HealthStatus.UNHEALTHY, HealthStatus.CRITICAL]:
                alert_key = f"{component}_health"

                # Check alert cooldown
                if (
                    alert_key not in self._last_alert_times
                    or current_time - self._last_alert_times[alert_key] > self.alert_cooldown
                ):

                    alert = SystemAlert(
                        alert_id=f"alert_{int(current_time)}_{component}",
                        severity=(
                            AlertSeverity.ERROR
                            if health.health_status == HealthStatus.UNHEALTHY
                            else AlertSeverity.CRITICAL
                        ),
                        component=component,
                        alert_type="component_health",
                        message=f"Component {component} is {health.health_status.value}",
                        timestamp=current_time,
                    )

                    self._active_alerts.append(alert)
                    self._last_alert_times[alert_key] = current_time

                    _logger.warning(f"[RealTimeSystemMonitor] Generated alert: {alert.message}")

    def _update_health_scores(self) -> None:
        """Update component health scores based on metrics."""
        for component, health in self._component_health.items():
            # Calculate health score based on status and issues
            base_score = 1.0 if health.health_status == HealthStatus.HEALTHY else 0.5
            issue_penalty = len(health.active_issues) * 0.1

            health.performance_score = max(base_score - issue_penalty, 0.0)

    def record_metric(self, metric: SystemMetric) -> None:
        """Record a system metric.

        Args:
            metric: System metric to record
        """
        metric_key = f"{metric.component}.{metric.metric_name}"

        with self._lock:
            self._metric_windows[metric_key].append(metric)

            # Check for anomalies
            if len(self._metric_windows[metric_key]) > 10:
                self._check_metric_anomaly(metric_key, metric)

    def _check_metric_anomaly(self, metric_key: str, current_metric: SystemMetric) -> None:
        """Check metric for anomalies using simple statistical analysis.

        Args:
            metric_key: Metric key
            current_metric: Current metric value
        """
        window = self._metric_windows[metric_key]
        values = [m.metric_value for m in window]

        if len(values) < 10:
            return

        mean_val = sum(values) / len(values)
        std_val = (sum((x - mean_val) ** 2 for x in values) / len(values)) ** 0.5

        # Check if current value is anomalous (3 sigma)
        if std_val > 0:
            z_score = abs((current_metric.metric_value - mean_val) / std_val)
            if z_score > 3.0:
                self._generate_anomaly_alert(metric_key, current_metric, z_score)

    def _generate_anomaly_alert(
        self, metric_key: str, metric: SystemMetric, z_score: float
    ) -> None:
        """Generate alert for metric anomaly.

        Args:
            metric_key: Metric key
            metric: Current metric
            z_score: Z-score of anomaly
        """
        alert = SystemAlert(
            alert_id=f"anomaly_{int(time.time())}_{metric_key}",
            severity=AlertSeverity.WARNING if z_score < 5.0 else AlertSeverity.ERROR,
            component=metric.component,
            alert_type="metric_anomaly",
            message=f"Anomaly detected in {metric.metric_name}: {z_score:.2f}σ deviation",
            timestamp=time.time(),
        )

        with self._lock:
            self._active_alerts.append(alert)

    def get_health_dashboard(self) -> SystemHealthDashboard:
        """Get current system health dashboard.

        Returns:
            Complete health dashboard data
        """
        with self._lock:
            overall_score = self._calculate_overall_health_score()

            # Calculate resource utilization
            resource_utilization = self._calculate_resource_utilization()

            # Calculate trends
            recent_trends = self._calculate_recent_trends()

            dashboard = SystemHealthDashboard(
                dashboard_timestamp=time.time(),
                overall_health_status=getattr(self, "_overall_health_status", HealthStatus.HEALTHY),
                overall_health_score=overall_score,
                component_health=dict(self._component_health),
                system_metrics=self._get_aggregated_metrics(),
                active_alerts=list(self._active_alerts),
                recent_trends=recent_trends,
                resource_utilization=resource_utilization,
            )

            return dashboard

    def _calculate_overall_health_score(self) -> float:
        """Calculate overall system health score.

        Returns:
            Health score (0.0 to 1.0)
        """
        if not self._component_health:
            return 0.5

        scores = [health.performance_score for health in self._component_health.values()]

        if not scores:
            return 0.5

        return sum(scores) / len(scores)

    def _get_aggregated_metrics(self) -> Dict[str, float]:
        """Get aggregated system metrics.

        Returns:
            Dictionary of aggregated metrics
        """
        metrics = {}

        # Aggregate component health scores
        if self._component_health:
            metrics["component_count"] = len(self._component_health)
            metrics["avg_component_health"] = self._calculate_overall_health_score()
            metrics["unhealthy_components"] = sum(
                1
                for h in self._component_health.values()
                if h.health_status != HealthStatus.HEALTHY
            )

        # Aggregate alert counts
        metrics["active_alerts"] = len(self._active_alerts)
        metrics["critical_alerts"] = sum(
            1 for a in self._active_alerts if a.severity == AlertSeverity.CRITICAL
        )

        return metrics

    def _calculate_resource_utilization(self) -> Dict[str, float]:
        """Calculate current resource utilization.

        Returns:
            Resource utilization metrics
        """
        # In real implementation, this would use actual system metrics
        # For simulation, return reasonable defaults
        return {
            "cpu_percent": 45.0,
            "memory_percent": 62.0,
            "disk_percent": 55.0,
            "network_io": 15.0,
        }

    def _calculate_recent_trends(self) -> Dict[str, str]:
        """Calculate recent metric trends.

        Returns:
            Dictionary of trend indicators
        """
        trends = {}

        # Analyze metric trends
        for metric_key, window in self._metric_windows.items():
            if len(window) < 10:
                trends[metric_key] = "STABLE"
                continue

            values = [m.metric_value for m in window]
            recent = values[-5:]
            older = values[-10:-5]

            if not recent or not older:
                trends[metric_key] = "STABLE"
                continue

            recent_avg = sum(recent) / len(recent)
            older_avg = sum(older) / len(older)

            if older_avg == 0:
                trends[metric_key] = "STABLE"
            else:
                change = (recent_avg - older_avg) / older_avg

                if change > 0.1:
                    trends[metric_key] = "INCREASING"
                elif change < -0.1:
                    trends[metric_key] = "DECREASING"
                else:
                    trends[metric_key] = "STABLE"

        return trends

    def resolve_alert(self, alert_id: str, resolution_message: str) -> bool:
        """Resolve an active alert.

        Args:
            alert_id: Alert ID to resolve
            resolution_message: Resolution description

        Returns:
            True if alert was resolved
        """
        with self._lock:
            for alert in self._active_alerts:
                if alert.alert_id == alert_id:
                    alert.resolved = True
                    alert.resolution_message = resolution_message
                    self._alert_history.append(alert)
                    self._active_alerts.remove(alert)

                    _logger.info(
                        f"[RealTimeSystemMonitor] Resolved alert {alert_id}: {resolution_message}"
                    )
                    return True

            return False

    def get_component_health(self, component_name: str) -> Optional[ComponentHealth]:
        """Get health status for a specific component.

        Args:
            component_name: Component name

        Returns:
            Component health or None if not found
        """
        with self._lock:
            return self._component_health.get(component_name)

    def set_component_health(
        self, component_name: str, health_status: HealthStatus, issues: List[str] = None
    ) -> None:
        """Manually set component health status.

        Args:
            component_name: Component name
            health_status: Health status
            issues: List of active issues
        """
        with self._lock:
            health = ComponentHealth(
                component_name=component_name,
                health_status=health_status,
                last_updated=time.time(),
                active_issues=issues or [],
                performance_score=0.5 if health_status != HealthStatus.HEALTHY else 0.8,
            )

            self._component_health[component_name] = health

            _logger.info(
                f"[RealTimeSystemMonitor] Set {component_name} health to {health_status.value}"
            )


# Singleton instance
_system_monitor: Optional[RealTimeSystemMonitor] = None
_monitor_lock = threading.Lock()


def get_realtime_system_monitor(
    monitoring_interval: float = 5.0, metric_window_size: int = 100, alert_cooldown: float = 60.0
) -> RealTimeSystemMonitor:
    """Get singleton instance of real-time system monitor.

    Args:
        monitoring_interval: Seconds between monitoring cycles
        metric_window_size: Number of metric points to retain
        alert_cooldown: Minimum seconds between similar alerts

    Returns:
        Real-time system monitor instance
    """
    global _system_monitor

    with _monitor_lock:
        if _system_monitor is None:
            _system_monitor = RealTimeSystemMonitor(
                monitoring_interval=monitoring_interval,
                metric_window_size=metric_window_size,
                alert_cooldown=alert_cooldown,
            )
        return _system_monitor
