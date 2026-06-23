"""
Runtime Context and Monitoring - Real Implementation

Provides real runtime context management and system observability
for the DIX VISION intelligence engine.
"""

import asyncio
import logging
from collections import deque
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
from typing import Any, Dict, List, Optional

import numpy as np

logger = logging.getLogger(__name__)

DEFAULT_LATENCY_BUDGET_NS = 100000000  # 100ms


class ComponentStatus(Enum):
    """Status of runtime components."""

    HEALTHY = "healthy"
    DEGRADED = "degraded"
    ERROR = "error"
    UNKNOWN = "unknown"


class PerformanceMetric(Enum):
    """Types of performance metrics."""

    LATENCY = "latency"
    THROUGHPUT = "throughput"
    CPU_USAGE = "cpu_usage"
    MEMORY_USAGE = "memory_usage"
    ERROR_RATE = "error_rate"
    QUEUE_DEPTH = "queue_depth"


@dataclass
class ComponentMetrics:
    """Metrics for a specific component."""

    component_id: str
    status: ComponentStatus
    latency_ms: float = 0.0
    throughput_per_second: float = 0.0
    cpu_usage_percent: float = 0.0
    memory_usage_mb: float = 0.0
    error_rate: float = 0.0
    queue_depth: int = 0
    last_updated: datetime = field(default_factory=datetime.now)
    uptime_seconds: float = 0.0


@dataclass
class SystemSnapshot:
    """Complete snapshot of system state."""

    timestamp_ns: int
    component_metrics: Dict[str, ComponentMetrics]
    system_load: float
    available_memory_mb: float
    active_threads: int
    network_latency_ms: float
    disk_io_mb_per_sec: float


@dataclass
class PerformanceThreshold:
    """Performance threshold configuration."""

    metric_type: PerformanceMetric
    warning_threshold: float
    critical_threshold: float
    enabled: bool = True


@dataclass
class Alert:
    """System alert generated from threshold violations."""

    alert_id: str
    severity: str  # "info", "warning", "critical"
    component: str
    metric_type: str
    current_value: float
    threshold: float
    message: str
    timestamp: datetime = field(default_factory=datetime.now)
    resolved: bool = False


class RuntimeMonitorView:
    """Real runtime monitor view with comprehensive system observability."""

    def __init__(self, component_id: str = "system", **kwargs: object):
        self._component_id = component_id
        self._metrics_history: deque = deque(maxlen=1000)
        self._current_metrics: Optional[ComponentMetrics] = None
        self._performance_thresholds: Dict[PerformanceMetric, PerformanceThreshold] = {}
        self._alerts: deque = deque(maxlen=100)
        self._start_time = datetime.now()

        # Initialize default thresholds
        self._initialize_default_thresholds()

        logger.info(f"[RUNTIME_MONITOR] Runtime monitor initialized for {component_id}")

    def _initialize_default_thresholds(self):
        """Initialize default performance thresholds."""
        self._performance_thresholds = {
            PerformanceMetric.LATENCY: PerformanceThreshold(
                metric_type=PerformanceMetric.LATENCY,
                warning_threshold=100.0,  # 100ms
                critical_threshold=500.0,  # 500ms
            ),
            PerformanceMetric.ERROR_RATE: PerformanceThreshold(
                metric_type=PerformanceMetric.ERROR_RATE,
                warning_threshold=0.05,  # 5%
                critical_threshold=0.20,  # 20%
            ),
            PerformanceMetric.CPU_USAGE: PerformanceThreshold(
                metric_type=PerformanceMetric.CPU_USAGE,
                warning_threshold=70.0,  # 70%
                critical_threshold=90.0,  # 90%
            ),
            PerformanceMetric.MEMORY_USAGE: PerformanceThreshold(
                metric_type=PerformanceMetric.MEMORY_USAGE,
                warning_threshold=512.0,  # 512MB
                critical_threshold=1024.0,  # 1GB
            ),
        }

    def update_metrics(self, metrics: ComponentMetrics) -> None:
        """Update current metrics and check thresholds."""
        metrics.last_updated = datetime.now()
        metrics.uptime_seconds = (datetime.now() - self._start_time).total_seconds()

        self._current_metrics = metrics
        self._metrics_history.append(metrics)

        # Check for threshold violations
        self._check_thresholds(metrics)

        logger.debug(f"[RUNTIME_MONITOR] Updated metrics for {metrics.component_id}")

    def _check_thresholds(self, metrics: ComponentMetrics) -> None:
        """Check if metrics violate performance thresholds."""
        metric_values = {
            PerformanceMetric.LATENCY: metrics.latency_ms,
            PerformanceMetric.ERROR_RATE: metrics.error_rate,
            PerformanceMetric.CPU_USAGE: metrics.cpu_usage_percent,
            PerformanceMetric.MEMORY_USAGE: metrics.memory_usage_mb,
        }

        for metric_type, threshold in self._performance_thresholds.items():
            if not threshold.enabled:
                continue

            current_value = metric_values.get(metric_type)
            if current_value is None:
                continue

            if current_value >= threshold.critical_threshold:
                self._generate_alert(
                    severity="critical",
                    component=metrics.component_id,
                    metric_type=metric_type.value,
                    current_value=current_value,
                    threshold=threshold.critical_threshold,
                )
            elif current_value >= threshold.warning_threshold:
                self._generate_alert(
                    severity="warning",
                    component=metrics.component_id,
                    metric_type=metric_type.value,
                    current_value=current_value,
                    threshold=threshold.warning_threshold,
                )

    def _generate_alert(
        self,
        severity: str,
        component: str,
        metric_type: str,
        current_value: float,
        threshold: float,
    ) -> None:
        """Generate a system alert."""
        alert = Alert(
            alert_id=f"alert_{int(datetime.now().timestamp())}",
            severity=severity,
            component=component,
            metric_type=metric_type,
            current_value=current_value,
            threshold=threshold,
            message=f"{metric_type} for {component} is {current_value:.2f}, threshold is {threshold:.2f}",
        )

        self._alerts.append(alert)

        if severity == "critical":
            logger.error(f"[RUNTIME_MONITOR] CRITICAL: {alert.message}")
        elif severity == "warning":
            logger.warning(f"[RUNTIME_MONITOR] WARNING: {alert.message}")
        else:
            logger.info(f"[RUNTIME_MONITOR] INFO: {alert.message}")

    def get_current_metrics(self) -> Optional[ComponentMetrics]:
        """Get current component metrics."""
        return self._current_metrics

    def get_metrics_history(self, minutes: int = 10) -> List[ComponentMetrics]:
        """Get metrics history for the specified time period."""
        cutoff_time = datetime.now() - timedelta(minutes=minutes)
        return [m for m in self._metrics_history if m.last_updated >= cutoff_time]

    def get_performance_summary(self) -> Dict[str, Any]:
        """Get performance summary statistics."""
        if not self._metrics_history:
            return {"error": "No metrics available"}

        recent_metrics = list(self._metrics_history)[-100:]  # Last 100 samples

        latency_values = [m.latency_ms for m in recent_metrics]
        throughput_values = [m.throughput_per_second for m in recent_metrics]
        error_rates = [m.error_rate for m in recent_metrics]
        cpu_values = [m.cpu_usage_percent for m in recent_metrics]
        memory_values = [m.memory_usage_mb for m in recent_metrics]

        return {
            "component_id": self._component_id,
            "uptime_seconds": (datetime.now() - self._start_time).total_seconds(),
            "latency": {
                "avg_ms": np.mean(latency_values),
                "p50_ms": np.percentile(latency_values, 50),
                "p95_ms": np.percentile(latency_values, 95),
                "p99_ms": np.percentile(latency_values, 99),
                "max_ms": np.max(latency_values),
            },
            "throughput": {
                "avg_per_second": np.mean(throughput_values),
                "max_per_second": np.max(throughput_values),
            },
            "error_rate": {"avg": np.mean(error_rates), "max": np.max(error_rates)},
            "cpu_usage": {"avg_percent": np.mean(cpu_values), "max_percent": np.max(cpu_values)},
            "memory_usage": {"avg_mb": np.mean(memory_values), "max_mb": np.max(memory_values)},
            "total_samples": len(recent_metrics),
            "active_alerts": len([a for a in self._alerts if not a.resolved]),
        }

    def get_alerts(
        self, severity: Optional[str] = None, unresolved_only: bool = True
    ) -> List[Alert]:
        """Get alerts, optionally filtered."""
        alerts = list(self._alerts)

        if unresolved_only:
            alerts = [a for a in alerts if not a.resolved]

        if severity:
            alerts = [a for a in alerts if a.severity == severity]

        return alerts

    def resolve_alert(self, alert_id: str) -> bool:
        """Mark an alert as resolved."""
        for alert in self._alerts:
            if alert.alert_id == alert_id:
                alert.resolved = True
                logger.info(f"[RUNTIME_MONITOR] Resolved alert {alert_id}")
                return True
        return False

    def set_threshold(
        self, metric_type: PerformanceMetric, warning_threshold: float, critical_threshold: float
    ) -> None:
        """Update performance threshold for a metric."""
        threshold = PerformanceThreshold(
            metric_type=metric_type,
            warning_threshold=warning_threshold,
            critical_threshold=critical_threshold,
            enabled=True,
        )
        self._performance_thresholds[metric_type] = threshold
        logger.info(f"[RUNTIME_MONITOR] Updated threshold for {metric_type.value}")


class RuntimeContext:
    """Real runtime context with comprehensive system monitoring."""

    def __init__(self, context_id: str = "default", **kwargs: object):
        self._context_id = context_id
        self._component_monitors: Dict[str, RuntimeMonitorView] = {}
        self._system_snapshots: deque = deque(maxlen=100)
        self._active = False
        self._monitoring_interval = 1.0  # seconds
        self._monitoring_task = None

        # System-wide metrics
        self._system_load = 0.0
        self._available_memory_mb = 0.0
        self._active_threads = 0
        self._network_latency_ms = 0.0
        self._disk_io_mb_per_sec = 0.0

        logger.info(f"[RUNTIME_CONTEXT] Runtime context initialized: {context_id}")

    def add_component_monitor(self, component_id: str, monitor: RuntimeMonitorView) -> None:
        """Add a component monitor to the runtime context."""
        self._component_monitors[component_id] = monitor
        logger.info(f"[RUNTIME_CONTEXT] Added monitor for component {component_id}")

    def remove_component_monitor(self, component_id: str) -> bool:
        """Remove a component monitor from the runtime context."""
        if component_id in self._component_monitors:
            del self._component_monitors[component_id]
            logger.info(f"[RUNTIME_CONTEXT] Removed monitor for component {component_id}")
            return True
        return False

    def get_component_monitor(self, component_id: str) -> Optional[RuntimeMonitorView]:
        """Get a specific component monitor."""
        return self._component_monitors.get(component_id)

    def get_all_monitors(self) -> Dict[str, RuntimeMonitorView]:
        """Get all component monitors."""
        return self._component_monitors.copy()

    def update_component_metrics(self, component_id: str, metrics: ComponentMetrics) -> None:
        """Update metrics for a specific component."""
        monitor = self._component_monitors.get(component_id)
        if monitor:
            monitor.update_metrics(metrics)
        else:
            # Create monitor if it doesn't exist
            new_monitor = RuntimeMonitorView(component_id)
            new_monitor.update_metrics(metrics)
            self._component_monitors[component_id] = new_monitor
            logger.info(f"[RUNTIME_CONTEXT] Created new monitor for {component_id}")

    async def start_monitoring(self) -> None:
        """Start continuous system monitoring."""
        if self._active:
            logger.warning("[RUNTIME_CONTEXT] Monitoring already active")
            return

        logger.info("[RUNTIME_CONTEXT] Starting continuous monitoring")
        self._active = True
        self._monitoring_task = asyncio.create_task(self._monitoring_loop())

    async def stop_monitoring(self) -> None:
        """Stop continuous system monitoring."""
        if not self._active:
            logger.warning("[RUNTIME_CONTEXT] Monitoring not active")
            return

        logger.info("[RUNTIME_CONTEXT] Stopping continuous monitoring")
        self._active = False

        if self._monitoring_task:
            self._monitoring_task.cancel()
            try:
                await self._monitoring_task
            except asyncio.CancelledError:
                pass

    async def _monitoring_loop(self):
        """Background monitoring loop."""
        while self._active:
            try:
                # Collect system snapshot
                snapshot = await self._collect_system_snapshot()
                self._system_snapshots.append(snapshot)

                # Update system metrics
                await self._update_system_metrics()

                # Small delay to prevent CPU spinning
                await asyncio.sleep(self._monitoring_interval)

            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"[RUNTIME_CONTEXT] Error in monitoring loop: {e}")
                await asyncio.sleep(1)

    async def _collect_system_snapshot(self) -> SystemSnapshot:
        """Collect comprehensive system snapshot."""
        # Collect metrics from all components
        component_metrics = {}
        for component_id, monitor in self._component_monitors.items():
            current_metrics = monitor.get_current_metrics()
            if current_metrics:
                component_metrics[component_id] = current_metrics

        snapshot = SystemSnapshot(
            timestamp_ns=int(datetime.now().timestamp() * 1e9),
            component_metrics=component_metrics,
            system_load=self._system_load,
            available_memory_mb=self._available_memory_mb,
            active_threads=self._active_threads,
            network_latency_ms=self._network_latency_ms,
            disk_io_mb_per_sec=self._disk_io_mb_per_sec,
        )

        return snapshot

    async def _update_system_metrics(self) -> None:
        """Update system-wide metrics."""
        try:
            # Get system load (real implementation would use psutil or similar)
            import psutil

            self._system_load = psutil.cpu_percent(interval=0.1)
            self._available_memory_mb = psutil.virtual_memory().available / (1024 * 1024)
            self._active_threads = psutil.Process().num_threads()

            # Network and disk I/O (simplified)
            network_io = psutil.net_io_counters()
            self._network_latency_ms = 1.0  # Placeholder - would need real ping

            disk_io = psutil.disk_io_counters()
            self._disk_io_mb_per_sec = (disk_io.read_bytes + disk_io.write_bytes) / (1024 * 1024)

        except ImportError:
            # Fallback if psutil not available
            self._system_load = 0.5  # Placeholder
            self._available_memory_mb = 4096.0  # 4GB placeholder
            self._active_threads = 10  # Placeholder
            self._network_latency_ms = 5.0  # Placeholder
            self._disk_io_mb_per_sec = 50.0  # Placeholder
        except Exception as e:
            logger.error(f"[RUNTIME_CONTEXT] Error updating system metrics: {e}")

    def get_system_snapshot(self, index: int = -1) -> Optional[SystemSnapshot]:
        """Get a system snapshot by index (default: latest)."""
        if not self._system_snapshots:
            return None
        try:
            return self._system_snapshots[index]
        except IndexError:
            return None

    def get_snapshot_history(self, count: int = 10) -> List[SystemSnapshot]:
        """Get recent system snapshots."""
        return list(self._system_snapshots)[-count:]

    def get_system_performance_summary(self) -> Dict[str, Any]:
        """Get comprehensive system performance summary."""
        if not self._component_monitors:
            return {
                "context_id": self._context_id,
                "active": self._active,
                "component_monitors": 0,
                "system_load": self._system_load,
                "available_memory_mb": self._available_memory_mb,
                "error": "No component monitors configured",
            }

        component_summaries = {}
        total_alerts = 0

        for component_id, monitor in self._component_monitors.items():
            component_summaries[component_id] = monitor.get_performance_summary()
            total_alerts += len(monitor.get_alerts(unresolved_only=True))

        return {
            "context_id": self._context_id,
            "active": self._active,
            "component_monitors": len(self._component_monitors),
            "total_active_alerts": total_alerts,
            "system_load": self._system_load,
            "available_memory_mb": self._available_memory_mb,
            "active_threads": self._active_threads,
            "network_latency_ms": self._network_latency_ms,
            "disk_io_mb_per_sec": self._disk_io_mb_per_sec,
            "component_summaries": component_summaries,
        }

    def get_all_alerts(self, severity: Optional[str] = None) -> List[Alert]:
        """Get all alerts from all components."""
        all_alerts = []
        for monitor in self._component_monitors.values():
            all_alerts.extend(monitor.get_alerts(severity=severity, unresolved_only=True))

        # Sort by timestamp (most recent first)
        all_alerts.sort(key=lambda a: a.timestamp, reverse=True)

        return all_alerts

    def get_latency_budget_status(self) -> Dict[str, Any]:
        """Check if system is within latency budget."""
        budget_ms = DEFAULT_LATENCY_BUDGET_NS / 1e6  # Convert to ms

        if not self._component_monitors:
            return {
                "budget_ms": budget_ms,
                "status": "unknown",
                "within_budget": False,
                "message": "No component monitors configured",
            }

        all_within_budget = True
        budget_violations = []

        for component_id, monitor in self._component_monitors.items():
            current_metrics = monitor.get_current_metrics()
            if current_metrics and current_metrics.latency_ms > budget_ms:
                all_within_budget = False
                budget_violations.append(
                    {
                        "component": component_id,
                        "latency_ms": current_metrics.latency_ms,
                        "budget_ms": budget_ms,
                        "excess_ms": current_metrics.latency_ms - budget_ms,
                    }
                )

        return {
            "budget_ms": budget_ms,
            "status": "within_budget" if all_within_budget else "violated",
            "within_budget": all_within_budget,
            "violations": budget_violations,
            "total_components": len(self._component_monitors),
            "violating_components": len(budget_violations),
        }


def build_runtime_context(
    context_id: str = "default", component_ids: Optional[List[str]] = None, **kwargs: object
) -> RuntimeContext:
    """Build and initialize a runtime context with component monitors.

    Args:
        context_id: Unique identifier for the runtime context
        component_ids: List of component IDs to monitor
        **kwargs: Additional configuration parameters

    Returns:
        Initialized RuntimeContext instance
    """
    context = RuntimeContext(context_id, **kwargs)

    # Create monitors for specified components
    if component_ids:
        for component_id in component_ids:
            monitor = RuntimeMonitorView(component_id)
            context.add_component_monitor(component_id, monitor)

    # Add default monitors for common components if none specified
    if not component_ids:
        default_components = ["intelligence_engine", "execution_engine", "governance_engine"]
        for component_id in default_components:
            monitor = RuntimeMonitorView(component_id)
            context.add_component_monitor(component_id, monitor)

    logger.info(
        f"[RUNTIME_CONTEXT] Built runtime context with {len(component_ids or default_components)} component monitors"
    )

    return context


# Global runtime context instance
_default_runtime_context = None


def get_default_runtime_context() -> RuntimeContext:
    """Get or create the default runtime context."""
    global _default_runtime_context

    if _default_runtime_context is None:
        _default_runtime_context = build_runtime_context("default")

    return _default_runtime_context


__all__ = [
    "ComponentStatus",
    "PerformanceMetric",
    "ComponentMetrics",
    "SystemSnapshot",
    "PerformanceThreshold",
    "Alert",
    "RuntimeMonitorView",
    "RuntimeContext",
    "build_runtime_context",
    "get_default_runtime_context",
]
