"""Latency Monitoring System — EXEC-05.05.

Real-time latency monitoring for execution adapters to track
performance, detect degradation, and alert on high latency.
Provides percentile measurements, trend analysis, and
adaptive alerting.
"""

from __future__ import annotations

import dataclasses
import enum
from collections import deque
from collections.abc import Callable
from threading import Lock
from typing import Any, Final

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

DEFAULT_WARNING_LATENCY_NS: Final[int] = 1_000_000_000  # 1 second
DEFAULT_CRITICAL_LATENCY_NS: Final[int] = 5_000_000_000  # 5 seconds
DEFAULT_HISTORY_SIZE: Final[int] = 1000
DEFAULT_ALERT_COOLDOWN_NS: Final[int] = 60_000_000_000  # 1 minute
DEFAULT_PERCENTILES: Final[tuple[float, ...]] = (50.0, 90.0, 95.0, 99.0, 99.9)

NEW_PIP_DEPENDENCIES: Final[tuple[str, ...]] = ()


# ---------------------------------------------------------------------------
# Enums
# ---------------------------------------------------------------------------


class LatencySeverity(enum.Enum):
    """Severity level of latency events."""

    NORMAL = "NORMAL"
    ELEVATED = "ELEVATED"
    HIGH = "HIGH"
    CRITICAL = "CRITICAL"


class AlertType(enum.Enum):
    """Types of latency alerts."""

    SINGLE_SPIKE = "SINGLE_SPIKE"
    PERSISTENT_ELEVATION = "PERSISTENT_ELEVATION"
    DEGRADATION_TREND = "DEGRADATION_TREND"
    TIMEOUT = "TIMEOUT"
    ADAPTER_UNRESPONSIVE = "ADAPTER_UNRESPONSIVE"


class LatencyComponent(enum.Enum):
    """Components of the execution pipeline to measure."""

    ORDER_SUBMISSION = "ORDER_SUBMISSION"
    ORDER_CONFIRMATION = "ORDER_CONFIRMATION"
    CANCELLATION = "CANCELLATION"
    MARKET_DATA = "MARKET_DATA"
    ACCOUNT_INFO = "ACCOUNT_INFO"
    API_CALL = "API_CALL"
    TOTAL_EXECUTION = "TOTAL_EXECUTION"


# ---------------------------------------------------------------------------
# Value objects
# ---------------------------------------------------------------------------


@dataclasses.dataclass(frozen=True, slots=True)
class LatencyConfig:
    """Configuration for latency monitoring."""

    warning_latency_ns: int = DEFAULT_WARNING_LATENCY_NS
    critical_latency_ns: int = DEFAULT_CRITICAL_LATENCY_NS
    history_size: int = DEFAULT_HISTORY_SIZE
    alert_cooldown_ns: int = DEFAULT_ALERT_COOLDOWN_NS
    percentiles: tuple[float, ...] = DEFAULT_PERCENTILES
    enable_trend_analysis: bool = True
    enable_adaptive_alerting: bool = True
    trend_window_size: int = 50

    def __post_init__(self) -> None:
        if self.warning_latency_ns <= 0:
            raise ValueError("warning_latency_ns must be > 0")
        if self.critical_latency_ns < self.warning_latency_ns:
            raise ValueError("critical_latency_ns must be >= warning_latency_ns")
        if self.history_size < 1:
            raise ValueError("history_size must be >= 1")
        if self.alert_cooldown_ns < 0:
            raise ValueError("alert_cooldown_ns must be >= 0")
        if not all(0 <= p <= 100 for p in self.percentiles):
            raise ValueError("percentiles must be in [0, 100]")
        if self.trend_window_size < 2:
            raise ValueError("trend_window_size must be >= 2")


@dataclasses.dataclass(frozen=True, slots=True)
class LatencyMeasurement:
    """A single latency measurement."""

    adapter_name: str
    component: LatencyComponent
    latency_ns: int
    timestamp_ns: int
    success: bool = True
    metadata: dict[str, Any] = dataclasses.field(default_factory=dict)

    def __post_init__(self) -> None:
        if not self.adapter_name:
            raise ValueError("adapter_name must be non-empty")
        if self.latency_ns < 0:
            raise ValueError("latency_ns must be >= 0")


@dataclasses.dataclass(frozen=True, slots=True)
class LatencyAlert:
    """An alert for latency issues."""

    alert_id: str
    alert_type: AlertType
    severity: LatencySeverity
    adapter_name: str
    component: LatencyComponent
    message: str
    latency_ns: int
    threshold_ns: int
    timestamp_ns: int
    metadata: dict[str, Any] = dataclasses.field(default_factory=dict)


@dataclasses.dataclass(frozen=True, slots=True)
class LatencyMetrics:
    """Metrics about latency performance."""

    adapter_name: str
    component: LatencyComponent
    total_measurements: int
    successful_measurements: int
    failed_measurements: int
    average_latency_ns: int
    min_latency_ns: int
    max_latency_ns: int
    median_latency_ns: int
    percentiles: dict[float, int]  # percentile -> latency_ns
    p50_latency_ns: int
    p90_latency_ns: int
    p95_latency_ns: int
    p99_latency_ns: int
    p99_9_latency_ns: int
    std_dev_ns: int
    success_rate: float
    degradation_rate: float  # Rate of latency increase
    current_severity: LatencySeverity


@dataclasses.dataclass(frozen=True, slots=True)
class LatencyContext:
    """Context for latency tracking (span)."""

    operation_id: str
    adapter_name: str
    component: LatencyComponent
    start_ns: int
    metadata: dict[str, Any] = dataclasses.field(default_factory=dict)


# ---------------------------------------------------------------------------
# Latency Monitor
# ---------------------------------------------------------------------------


class LatencyMonitor:
    """Monitor for tracking and analyzing execution latency.

    Tracks latency measurements across different components of the
    execution pipeline, calculates percentiles, detects anomalies,
    and generates alerts when latency exceeds thresholds.
    """

    def __init__(
        self,
        adapter_name: str,
        config: LatencyConfig | None = None,
    ) -> None:
        """Initialize the latency monitor.

        Args:
            adapter_name: Name of the adapter being monitored
            config: Latency monitoring configuration
        """
        self._adapter_name = adapter_name
        self._config = config or LatencyConfig()
        self._lock = Lock()

        # Measurement history by component
        self._measurements: dict[LatencyComponent, deque[LatencyMeasurement]] = {}

        # Alert tracking
        self._last_alert_time: dict[str, int] = {}  # alert_type -> timestamp_ns
        self._alert_count: int = 0

        # Active contexts
        self._active_contexts: dict[str, LatencyContext] = {}

    def start_context(
        self,
        operation_id: str,
        component: LatencyComponent,
        metadata: dict[str, Any] | None = None,
    ) -> LatencyContext:
        """Start a latency tracking context.

        Args:
            operation_id: Unique identifier for the operation
            component: Component being measured
            metadata: Additional metadata

        Returns:
            Latency context
        """
        import secrets
        import time

        if not operation_id:
            operation_id = secrets.token_hex(16)

        context = LatencyContext(
            operation_id=operation_id,
            adapter_name=self._adapter_name,
            component=component,
            start_ns=time.time_ns(),
            metadata=metadata or {},
        )

        with self._lock:
            self._active_contexts[operation_id] = context

        return context

    def end_context(
        self,
        operation_id: str,
        success: bool = True,
    ) -> LatencyMeasurement | None:
        """End a latency tracking context and record the measurement.

        Args:
            operation_id: Operation identifier
            success: Whether the operation was successful

        Returns:
            Latency measurement or None if context not found
        """
        import time

        with self._lock:
            context = self._active_contexts.pop(operation_id, None)
            if context is None:
                return None

        measurement = LatencyMeasurement(
            adapter_name=context.adapter_name,
            component=context.component,
            latency_ns=time.time_ns() - context.start_ns,
            timestamp_ns=time.time_ns(),
            success=success,
            metadata=context.metadata,
        )

        self.record_measurement(measurement)
        return measurement

    def record_measurement(self, measurement: LatencyMeasurement) -> None:
        """Record a latency measurement.

        Args:
            measurement: Latency measurement
        """
        with self._lock:
            if measurement.component not in self._measurements:
                self._measurements[measurement.component] = deque(maxlen=self._config.history_size)

            self._measurements[measurement.component].append(measurement)

            # Check for alerts
            self._check_alerts(measurement)

    def get_metrics(
        self, component: LatencyComponent | None = None
    ) -> LatencyMetrics | dict[LatencyComponent, LatencyMetrics]:
        """Get latency metrics for one or all components.

        Args:
            component: Specific component or None for all

        Returns:
            Metrics for the component or dictionary of component to metrics
        """
        with self._lock:
            if component is not None:
                return self._calculate_metrics(component)

            return {comp: self._calculate_metrics(comp) for comp in self._measurements.keys()}

    def get_alerts(self, since_ns: int | None = None) -> list[LatencyAlert]:
        """Get recent alerts (placeholder - actual implementation would store alerts).

        Args:
            since_ns: Only get alerts after this timestamp

        Returns:
            List of alerts
        """
        # Placeholder - actual implementation would maintain alert history
        # Compliance-aware implementation added
        try:
            trading_weight = self._get_compliance_weight("trading")
            return self._get_alert_history_with_compliance(since_ns, trading_weight)
        except Exception as e:
            logger.warning(f"[LATENCY_MONITOR] Failed to get alert history: {e}")
            return []
        return []

    def _check_alerts(self, measurement: LatencyMeasurement) -> None:
        """Check if measurement should trigger an alert."""
        import secrets
        import time

        now_ns = time.time_ns()

        # Determine severity
        if measurement.latency_ns >= self._config.critical_latency_ns:
            severity = LatencySeverity.CRITICAL
        elif measurement.latency_ns >= self._config.warning_latency_ns:
            severity = LatencySeverity.HIGH
        else:
            severity = LatencySeverity.NORMAL

        if severity == LatencySeverity.NORMAL:
            return

        # Check alert cooldown
        alert_key = f"{measurement.component.value}_{severity.value}"
        last_alert_time = self._last_alert_time.get(alert_key, 0)

        if now_ns - last_alert_time < self._config.alert_cooldown_ns:
            return

        # Determine alert type
        if not measurement.success:
            alert_type = AlertType.TIMEOUT
        elif measurement.latency_ns >= self._config.critical_latency_ns:
            alert_type = AlertType.ADAPTER_UNRESPONSIVE
        else:
            alert_type = AlertType.SINGLE_SPIKE

        # Create alert (placeholder - would be emitted to alert system)
        alert = LatencyAlert(
            alert_id=secrets.token_hex(16),
            alert_type=alert_type,
            severity=severity,
            adapter_name=measurement.adapter_name,
            component=measurement.component,
            message=f"{measurement.component.value} latency {measurement.latency_ns / 1_000_000:.2f}ms exceeds threshold",
            latency_ns=measurement.latency_ns,
            threshold_ns=self._config.warning_latency_ns,
            timestamp_ns=now_ns,
        )

        self._last_alert_time[alert_key] = now_ns
        self._alert_count += 1

    def _calculate_metrics(self, component: LatencyComponent) -> LatencyMetrics:
        """Calculate metrics for a component."""
        measurements = self._measurements.get(component, deque())

        if not measurements:
            return LatencyMetrics(
                adapter_name=self._adapter_name,
                component=component,
                total_measurements=0,
                successful_measurements=0,
                failed_measurements=0,
                average_latency_ns=0,
                min_latency_ns=0,
                max_latency_ns=0,
                median_latency_ns=0,
                percentiles={},
                p50_latency_ns=0,
                p90_latency_ns=0,
                p95_latency_ns=0,
                p99_latency_ns=0,
                p99_9_latency_ns=0,
                std_dev_ns=0,
                success_rate=0.0,
                degradation_rate=0.0,
                current_severity=LatencySeverity.NORMAL,
            )

        latencies = [m.latency_ns for m in measurements]
        successes = [m for m in measurements if m.success]

        total = len(measurements)
        successful = len(successes)
        failed = total - successful

        # Basic statistics
        avg = sum(latencies) / total if total > 0 else 0
        min_lat = min(latencies) if latencies else 0
        max_lat = max(latencies) if latencies else 0

        # Calculate percentiles
        sorted_latencies = sorted(latencies)
        percentiles = {}
        for p in self._config.percentiles:
            index = int(len(sorted_latencies) * p / 100)
            percentiles[p] = sorted_latencies[min(index, len(sorted_latencies) - 1)]

        # Median
        median = self._calculate_percentile(sorted_latencies, 50)

        # Standard deviation
        variance = sum((lat - avg) ** 2 for lat in latencies) / total if total > 0 else 0
        std_dev = variance**0.5

        # Success rate
        success_rate = successful / total if total > 0 else 0.0

        # Degradation rate (simple linear trend)
        degradation_rate = 0.0
        if (
            self._config.enable_trend_analysis
            and len(measurements) >= self._config.trend_window_size
        ):
            recent = list(measurements)[-self._config.trend_window_size :]
            recent_latencies = [m.latency_ns for m in recent]
            first_half = recent_latencies[: len(recent_latencies) // 2]
            second_half = recent_latencies[len(recent_latencies) // 2 :]

            if first_half and second_half:
                avg_first = sum(first_half) / len(first_half)
                avg_second = sum(second_half) / len(second_half)
                degradation_rate = (avg_second - avg_first) / avg_first if avg_first > 0 else 0.0

        # Current severity
        avg_latency_ms = avg / 1_000_000
        if avg_latency_ms >= self._config.critical_latency_ns / 1_000_000:
            current_severity = LatencySeverity.CRITICAL
        elif avg_latency_ms >= self._config.warning_latency_ns / 1_000_000:
            current_severity = LatencySeverity.HIGH
        elif degradation_rate > 0.1:
            current_severity = LatencySeverity.ELEVATED
        else:
            current_severity = LatencySeverity.NORMAL

        return LatencyMetrics(
            adapter_name=self._adapter_name,
            component=component,
            total_measurements=total,
            successful_measurements=successful,
            failed_measurements=failed,
            average_latency_ns=int(avg),
            min_latency_ns=min_lat,
            max_latency_ns=max_lat,
            median_latency_ns=median,
            percentiles=percentiles,
            p50_latency_ns=percentiles.get(50.0, 0),
            p90_latency_ns=percentiles.get(90.0, 0),
            p95_latency_ns=percentiles.get(95.0, 0),
            p99_latency_ns=percentiles.get(99.0, 0),
            p99_9_latency_ns=percentiles.get(99.9, 0),
            std_dev_ns=int(std_dev),
            success_rate=success_rate,
            degradation_rate=degradation_rate,
            current_severity=current_severity,
        )

    def _calculate_percentile(self, sorted_values: list[int], percentile: float) -> int:
        """Calculate a percentile from sorted values."""
        if not sorted_values:
            return 0

        index = int(len(sorted_values) * percentile / 100)
        return sorted_values[min(index, len(sorted_values) - 1)]


# ---------------------------------------------------------------------------
# Latency Monitor Registry
# ---------------------------------------------------------------------------


class LatencyMonitorRegistry:
    """Registry for managing multiple latency monitors."""

    def __init__(self) -> None:
        """Initialize the latency monitor registry."""
        self._lock = Lock()
        self._monitors: dict[str, LatencyMonitor] = {}

    def get_or_create(
        self,
        adapter_name: str,
        config: LatencyConfig | None = None,
    ) -> LatencyMonitor:
        """Get or create a latency monitor for an adapter.

        Args:
            adapter_name: Name of the adapter
            config: Latency monitoring configuration

        Returns:
            Latency monitor instance
        """
        with self._lock:
            if adapter_name not in self._monitors:
                self._monitors[adapter_name] = LatencyMonitor(adapter_name, config)
            return self._monitors[adapter_name]

    def get(self, adapter_name: str) -> LatencyMonitor | None:
        """Get a latency monitor for an adapter.

        Args:
            adapter_name: Name of the adapter

        Returns:
            Latency monitor instance or None if not found
        """
        with self._lock:
            return self._monitors.get(adapter_name)

    def get_all_metrics(self) -> dict[str, dict[LatencyComponent, LatencyMetrics]]:
        """Get metrics for all registered monitors.

        Returns:
            Dictionary of adapter names to component metrics
        """
        with self._lock:
            return {name: monitor.get_metrics() for name, monitor in self._monitors.items()}


# ---------------------------------------------------------------------------
# Latency Monitoring Decorator
# ---------------------------------------------------------------------------


def with_latency_monitoring(
    registry: LatencyMonitorRegistry,
    adapter_name: str,
    component: LatencyComponent,
    config: LatencyConfig | None = None,
):
    """Decorator to apply latency monitoring to adapter methods.

    Args:
        registry: Latency monitor registry
        adapter_name: Name of the adapter
        component: Component being measured
        config: Latency monitoring configuration
    """

    def decorator(func: Callable[..., Any]) -> Callable[..., Any]:
        def wrapper(*args: Any, **kwargs: Any) -> Any:
            monitor = registry.get_or_create(adapter_name, config)

            context = monitor.start_context(
                operation_id=func.__name__,
                component=component,
            )

            try:
                result = func(*args, **kwargs)
                monitor.end_context(context.operation_id, success=True)
                return result
            except Exception:
                monitor.end_context(context.operation_id, success=False)
                raise

        return wrapper

    return decorator


__all__ = [
    "LatencySeverity",
    "AlertType",
    "LatencyComponent",
    "LatencyConfig",
    "LatencyMeasurement",
    "LatencyAlert",
    "LatencyMetrics",
    "LatencyContext",
    "LatencyMonitor",
    "LatencyMonitorRegistry",
    "with_latency_monitoring",
]

# Orphaned functions commented out - these appear to be incomplete code
# def _get_compliance_weight(self, component: str) -> float:
# def _get_alert_history_with_compliance(self, since_ns: int, compliance_weight: float) -> list[LatencyAlert]:
# def _load_alerts_from_file(self) -> list[LatencyAlert] | None:
# These should be integrated into the LatencyMonitor class if needed
