"""evolution_engine.dyon.indira_performance_monitor — INDIRA Performance Monitoring for DYON.

System cognition component for monitoring INDIRA's system performance to optimize overall system performance.

This implementation provides performance monitoring capabilities for:
- Signal processing latency tracking
- Agent decision latency monitoring
- Portfolio update performance analysis
- Memory usage pattern analysis
- CPU utilization pattern tracking
- I/O bottleneck identification
- Performance anomaly detection
- Resource usage prediction
- Performance regression detection

Authority (L2/B1): evolution_engine.* only at module level.
DYON monitors INDIRA's system performance for optimization, never for trading purposes.
"""

from __future__ import annotations

import logging
import statistics
import threading
import time
from collections import defaultdict, deque
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Dict, List, Optional, Tuple

_logger = logging.getLogger(__name__)


class PerformanceMetricType(Enum):
    """Types of performance metrics."""

    LATENCY = "latency"
    THROUGHPUT = "throughput"
    MEMORY_USAGE = "memory_usage"
    CPU_UTILIZATION = "cpu_utilization"
    IO_OPERATIONS = "io_operations"
    ERROR_RATE = "error_rate"
    QUEUE_DEPTH = "queue_depth"


class INDIRAComponent(Enum):
    """INDIRA components for performance monitoring."""

    SIGNAL_FUSION = "signal_fusion"
    PORTFOLIO_REASONING = "portfolio_reasoning"
    EXECUTION_INTENT_FORMATION = "execution_intent_formation"
    TRADER_PROFILING = "trader_profiling"
    STRATEGY_DISCOVERY = "strategy_discovery"
    META_LEARNING = "meta_learning"


class AnomalySeverity(Enum):
    """Severity of performance anomalies."""

    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    CRITICAL = "CRITICAL"


@dataclass
class PerformanceMetric:
    """Single performance metric data point."""

    timestamp: float
    component: str
    metric_type: PerformanceMetricType
    value: float
    unit: str
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class PerformanceBaseline:
    """Performance baseline for a metric."""

    component: str
    metric_type: PerformanceMetricType
    baseline_mean: float
    baseline_std: float
    baseline_min: float
    baseline_max: float
    sample_count: int
    established_timestamp: float


@dataclass
class PerformanceAnomaly:
    """Performance anomaly detected."""

    anomaly_type: str
    component: str
    metric_type: PerformanceMetricType
    severity: AnomalySeverity
    detected_timestamp: float
    actual_value: float
    expected_range: Tuple[float, float]
    deviation: float
    description: str
    suggested_action: str


@dataclass
class PerformanceReport:
    """Complete performance monitoring report."""

    report_timestamp: float
    monitoring_period_seconds: float
    components_monitored: List[str]
    metrics_collected: int
    anomalies_detected: int
    baselines_established: int
    overall_health_score: float
    component_reports: Dict[str, Dict[str, Any]] = field(default_factory=dict)
    anomalies: List[PerformanceAnomaly] = field(default_factory=list)
    recommendations: List[str] = field(default_factory=list)


class INDIRAPerformanceMonitor:
    """Monitor INDIRA's system performance for optimization.

    DYON uses this monitor to track INDIRA's performance characteristics
    and identify optimization opportunities without interfering with trading operations.
    """

    def __init__(
        self, window_size: int = 100, baseline_samples: int = 50, anomaly_threshold_std: float = 2.5
    ):
        """Initialize INDIRA performance monitor.

        Args:
            window_size: Number of data points to keep in sliding window
            baseline_samples: Number of samples needed to establish baseline
            anomaly_threshold_std: Standard deviations for anomaly detection
        """
        self.window_size = window_size
        self.baseline_samples = baseline_samples
        self.anomaly_threshold_std = anomaly_threshold_std

        self._metric_windows: Dict[str, deque] = defaultdict(lambda: deque(maxlen=window_size))
        self._baselines: Dict[str, PerformanceBaseline] = {}
        self._anomalies: List[PerformanceAnomaly] = []
        self._lock = threading.Lock()

        _logger.info(
            f"[INDIRAPerformanceMonitor] Initialized with window_size={window_size}, "
            f"baseline_samples={baseline_samples}, anomaly_threshold={anomaly_threshold_std}"
        )

    def record_metric(self, metric: PerformanceMetric) -> None:
        """Record a performance metric.

        Args:
            metric: Performance metric to record
        """
        metric_key = f"{metric.component}.{metric.metric_type.value}"

        with self._lock:
            self._metric_windows[metric_key].append(metric)

            # Check if we should establish/update baseline
            if len(self._metric_windows[metric_key]) >= self.baseline_samples:
                self._establish_baseline(metric_key)

            # Check for anomalies if baseline exists
            if metric_key in self._baselines:
                self._check_for_anomaly(metric, metric_key)

    def record_signal_processing_latency(
        self, latency_ms: float, signal_type: str = "generic"
    ) -> None:
        """Record signal processing latency.

        Args:
            latency_ms: Processing latency in milliseconds
            signal_type: Type of signal being processed
        """
        metric = PerformanceMetric(
            timestamp=time.time(),
            component=INDIRAComponent.SIGNAL_FUSION.value,
            metric_type=PerformanceMetricType.LATENCY,
            value=latency_ms,
            unit="ms",
            metadata={"signal_type": signal_type},
        )
        self.record_metric(metric)

    def record_agent_decision_latency(self, agent_name: str, latency_ms: float) -> None:
        """Record agent decision-making latency.

        Args:
            agent_name: Name of the agent
            latency_ms: Decision latency in milliseconds
        """
        metric = PerformanceMetric(
            timestamp=time.time(),
            component=agent_name,
            metric_type=PerformanceMetricType.LATENCY,
            value=latency_ms,
            unit="ms",
            metadata={"agent_type": "decision"},
        )
        self.record_metric(metric)

    def record_portfolio_update_latency(self, latency_ms: float) -> None:
        """Record portfolio update latency.

        Args:
            latency_ms: Portfolio update latency in milliseconds
        """
        metric = PerformanceMetric(
            timestamp=time.time(),
            component=INDIRAComponent.PORTFOLIO_REASONING.value,
            metric_type=PerformanceMetricType.LATENCY,
            value=latency_ms,
            unit="ms",
        )
        self.record_metric(metric)

    def record_memory_usage(self, component: str, memory_mb: float) -> None:
        """Record memory usage for a component.

        Args:
            component: Component name
            memory_mb: Memory usage in megabytes
        """
        metric = PerformanceMetric(
            timestamp=time.time(),
            component=component,
            metric_type=PerformanceMetricType.MEMORY_USAGE,
            value=memory_mb,
            unit="MB",
        )
        self.record_metric(metric)

    def record_cpu_utilization(self, component: str, cpu_percent: float) -> None:
        """Record CPU utilization for a component.

        Args:
            component: Component name
            cpu_percent: CPU utilization percentage (0-100)
        """
        metric = PerformanceMetric(
            timestamp=time.time(),
            component=component,
            metric_type=PerformanceMetricType.CPU_UTILIZATION,
            value=cpu_percent,
            unit="percent",
        )
        self.record_metric(metric)

    def _establish_baseline(self, metric_key: str) -> None:
        """Establish performance baseline for a metric.

        Args:
            metric_key: Key for the metric
        """
        window = self._metric_windows[metric_key]
        if len(window) < self.baseline_samples:
            return

        values = [m.value for m in window]

        component, metric_type = metric_key.rsplit(".", 1)

        baseline = PerformanceBaseline(
            component=component,
            metric_type=PerformanceMetricType(metric_type),
            baseline_mean=statistics.mean(values),
            baseline_std=statistics.stdev(values) if len(values) > 1 else 0.0,
            baseline_min=min(values),
            baseline_max=max(values),
            sample_count=len(values),
            established_timestamp=time.time(),
        )

        self._baselines[metric_key] = baseline
        _logger.debug(
            f"[INDIRAPerformanceMonitor] Established baseline for {metric_key}: "
            f"mean={baseline.baseline_mean:.2f}, std={baseline.baseline_std:.2f}"
        )

    def _check_for_anomaly(self, metric: PerformanceMetric, metric_key: str) -> None:
        """Check if a metric value indicates an anomaly.

        Args:
            metric: Metric to check
            metric_key: Key for the metric
        """
        baseline = self._baselines.get(metric_key)
        if not baseline:
            return

        # Calculate z-score
        if baseline.baseline_std > 0:
            z_score = abs((metric.value - baseline.baseline_mean) / baseline.baseline_std)
        else:
            z_score = 0.0

        # Check if anomaly
        if z_score > self.anomaly_threshold_std:
            severity = self._determine_anomaly_severity(z_score)

            anomaly = PerformanceAnomaly(
                anomaly_type="statistical",
                component=metric.component,
                metric_type=metric.metric_type,
                severity=severity,
                detected_timestamp=time.time(),
                actual_value=metric.value,
                expected_range=(
                    baseline.baseline_mean - baseline.baseline_std * self.anomaly_threshold_std,
                    baseline.baseline_mean + baseline.baseline_std * self.anomaly_threshold_std,
                ),
                deviation=z_score,
                description=f"{metric.metric_type.value} for {metric.component} is {z_score:.2f}σ from baseline",
                suggested_action=self._generate_anomaly_suggestion(metric, baseline, z_score),
            )

            self._anomalies.append(anomaly)
            _logger.warning(
                f"[INDIRAPerformanceMonitor] Anomaly detected: {anomaly.description} "
                f"(severity={severity.value})"
            )

    def _determine_anomaly_severity(self, z_score: float) -> AnomalySeverity:
        """Determine severity of anomaly based on z-score.

        Args:
            z_score: Standard deviation score

        Returns:
            Anomaly severity
        """
        if z_score > 5.0:
            return AnomalySeverity.CRITICAL
        elif z_score > 4.0:
            return AnomalySeverity.HIGH
        elif z_score > 3.0:
            return AnomalySeverity.MEDIUM
        else:
            return AnomalySeverity.LOW

    def _generate_anomaly_suggestion(
        self, metric: PerformanceMetric, baseline: PerformanceBaseline, z_score: float
    ) -> str:
        """Generate suggestion for addressing anomaly.

        Args:
            metric: Anomalous metric
            baseline: Performance baseline
            z_score: Standard deviation score

        Returns:
            Suggested action
        """
        if metric.metric_type == PerformanceMetricType.LATENCY:
            if metric.value > baseline.baseline_mean:
                return "Investigate potential bottlenecks or increased load"
            else:
                return "Verify measurement accuracy - unusually low latency"

        elif metric.metric_type == PerformanceMetricType.MEMORY_USAGE:
            if metric.value > baseline.baseline_mean:
                return "Investigate potential memory leak or increased data processing"
            else:
                return "Verify memory measurement accuracy"

        elif metric.metric_type == PerformanceMetricType.CPU_UTILIZATION:
            if metric.value > baseline.baseline_mean:
                return "Investigate CPU-intensive operations or consider scaling"
            else:
                return "Verify CPU measurement accuracy"

        return "Investigate the root cause of the performance deviation"

    def get_current_performance_report(self) -> PerformanceReport:
        """Generate current performance monitoring report.

        Returns:
            Complete performance report
        """
        with self._lock:
            component_reports = {}
            total_metrics = sum(len(window) for window in self._metric_windows.values())

            # Generate component-specific reports
            for component in INDIRAComponent:
                component_data = self._generate_component_report(component.value)
                if component_data:
                    component_reports[component.value] = component_data

            # Calculate overall health score
            health_score = self._calculate_overall_health_score(component_reports)

            # Generate recommendations
            recommendations = self._generate_recommendations(component_reports, self._anomalies)

            report = PerformanceReport(
                report_timestamp=time.time(),
                monitoring_period_seconds=0.0,  # Would be tracked in real implementation
                components_monitored=list(component_reports.keys()),
                metrics_collected=total_metrics,
                anomalies_detected=len(self._anomalies),
                baselines_established=len(self._baselines),
                overall_health_score=health_score,
                component_reports=component_reports,
                anomalies=self._anomalies.copy(),
                recommendations=recommendations,
            )

            return report

    def _generate_component_report(self, component_name: str) -> Optional[Dict[str, Any]]:
        """Generate performance report for a specific component.

        Args:
            component_name: Name of the component

        Returns:
            Component performance report or None
        """
        component_metrics = {}
        has_data = False

        for metric_type in PerformanceMetricType:
            metric_key = f"{component_name}.{metric_type.value}"
            window = self._metric_windows.get(metric_key)

            if window and len(window) > 0:
                values = [m.value for m in window]
                component_metrics[metric_type.value] = {
                    "current_value": values[-1],
                    "mean": statistics.mean(values),
                    "min": min(values),
                    "max": max(values),
                    "std": statistics.stdev(values) if len(values) > 1 else 0.0,
                    "sample_count": len(values),
                    "has_baseline": metric_key in self._baselines,
                }
                has_data = True

        if has_data:
            return component_metrics
        return None

    def _calculate_overall_health_score(
        self, component_reports: Dict[str, Dict[str, Any]]
    ) -> float:
        """Calculate overall system health score.

        Args:
            component_reports: Component performance reports

        Returns:
            Health score (0-1, higher is better)
        """
        if not component_reports:
            return 0.5  # Neutral when no data

        total_score = 0.0
        component_count = 0

        # Score based on number of anomalies and baseline deviations
        anomaly_penalty = min(len(self._anomalies) * 0.05, 0.5)

        for component, metrics in component_reports.items():
            component_score = 0.0
            metric_count = 0

            for metric_name, metric_data in metrics.items():
                if metric_data.get("has_baseline", False):
                    # If baseline exists, check for stability
                    if metric_data["std"] < metric_data["mean"] * 0.1:
                        component_score += 1.0
                    else:
                        component_score += 0.7
                else:
                    component_score += 0.5

                metric_count += 1

            if metric_count > 0:
                total_score += component_score / metric_count
                component_count += 1

        if component_count > 0:
            base_score = total_score / component_count
            return max(base_score - anomaly_penalty, 0.0)

        return 0.5

    def _generate_recommendations(
        self, component_reports: Dict[str, Dict[str, Any]], anomalies: List[PerformanceAnomaly]
    ) -> List[str]:
        """Generate performance optimization recommendations.

        Args:
            component_reports: Component performance reports
            anomalies: Detected performance anomalies

        Returns:
            List of recommendations
        """
        recommendations = []

        # Anomaly-based recommendations
        critical_anomalies = [a for a in anomalies if a.severity == AnomalySeverity.CRITICAL]
        if critical_anomalies:
            recommendations.append(
                f"Address {len(critical_anomalies)} critical performance anomalies immediately"
            )

        high_anomalies = [a for a in anomalies if a.severity == AnomalySeverity.HIGH]
        if high_anomalies:
            recommendations.append(
                f"Investigate {len(high_anomalies)} high-severity performance issues"
            )

        # Component-specific recommendations
        for component, metrics in component_reports.items():
            if "latency" in metrics:
                latency_data = metrics["latency"]
                if latency_data["std"] > latency_data["mean"] * 0.2:
                    recommendations.append(
                        f"High latency variance in {component} - investigate inconsistent performance"
                    )

            if "memory_usage" in metrics:
                memory_data = metrics["memory_usage"]
                if memory_data["max"] > memory_data["mean"] * 2:
                    recommendations.append(
                        f"Memory usage spikes in {component} - potential memory leak"
                    )

        return recommendations

    def identify_performance_bottlenecks(self) -> List[Dict[str, Any]]:
        """Identify potential performance bottlenecks.

        Returns:
            List of identified bottlenecks
        """
        bottlenecks = []

        with self._lock:
            for component in INDIRAComponent:
                component_bottlenecks = self._identify_component_bottlenecks(component.value)
                if component_bottlenecks:
                    bottlenecks.extend(component_bottlenecks)

        return bottlenecks

    def _identify_component_bottlenecks(self, component_name: str) -> List[Dict[str, Any]]:
        """Identify bottlenecks in a specific component.

        Args:
            component_name: Name of the component

        Returns:
            List of bottlenecks for the component
        """
        bottlenecks = []

        # Check latency bottlenecks
        latency_key = f"{component_name}.latency"
        latency_window = self._metric_windows.get(latency_key)

        if latency_window and len(latency_window) > 10:
            values = [m.value for m in latency_window]
            if statistics.mean(values) > 100:  # 100ms threshold
                bottlenecks.append(
                    {
                        "component": component_name,
                        "type": "high_latency",
                        "severity": "HIGH" if statistics.mean(values) > 500 else "MEDIUM",
                        "current_value": statistics.mean(values),
                        "threshold": 100,
                        "description": f"{component_name} has high average latency",
                    }
                )

        # Check memory bottlenecks
        memory_key = f"{component_name}.memory_usage"
        memory_window = self._metric_windows.get(memory_key)

        if memory_window and len(memory_window) > 10:
            values = [m.value for m in memory_window]
            if max(values) > 1000:  # 1GB threshold
                bottlenecks.append(
                    {
                        "component": component_name,
                        "type": "high_memory",
                        "severity": "HIGH" if max(values) > 2000 else "MEDIUM",
                        "current_value": max(values),
                        "threshold": 1000,
                        "description": f"{component_name} has high memory usage spikes",
                    }
                )

        return bottlenecks

    def predict_resource_usage(
        self, component: str, horizon_seconds: float = 300
    ) -> Dict[str, Any]:
        """Predict future resource usage for a component.

        Args:
            component: Component name
            horizon_seconds: Prediction horizon in seconds

        Returns:
            Resource usage prediction
        """
        memory_key = f"{component}.memory_usage"
        cpu_key = f"{component}.cpu_utilization"

        memory_window = self._metric_windows.get(memory_key)
        cpu_window = self._metric_windows.get(cpu_key)

        prediction = {
            "component": component,
            "horizon_seconds": horizon_seconds,
            "memory_prediction": None,
            "cpu_prediction": None,
            "confidence": 0.0,
        }

        if memory_window and len(memory_window) > 5:
            values = [m.value for m in memory_window]
            # Simple linear extrapolation
            trend = (values[-1] - values[0]) / len(values)
            predicted_memory = values[-1] + trend * (
                horizon_seconds / 60
            )  # Assume per-minute trend

            prediction["memory_prediction"] = {
                "current_mb": values[-1],
                "predicted_mb": max(predicted_memory, 0),
                "trend_mb_per_minute": trend,
            }

        if cpu_window and len(cpu_window) > 5:
            values = [m.value for m in cpu_window]
            trend = (values[-1] - values[0]) / len(values)
            predicted_cpu = values[-1] + trend * (horizon_seconds / 60)

            prediction["cpu_prediction"] = {
                "current_percent": values[-1],
                "predicted_percent": max(min(predicted_cpu, 100), 0),
                "trend_percent_per_minute": trend,
            }

        # Calculate confidence based on data stability
        if prediction["memory_prediction"] or prediction["cpu_prediction"]:
            prediction["confidence"] = 0.6  # Moderate confidence for simple extrapolation

        return prediction

    def detect_performance_regression(
        self, component: str, metric_type: PerformanceMetricType
    ) -> Optional[Dict[str, Any]]:
        """Detect performance regression for a component metric.

        Args:
            component: Component name
            metric_type: Type of metric to check

        Returns:
            Regression detection result or None
        """
        metric_key = f"{component}.{metric_type.value}"
        baseline = self._baselines.get(metric_key)
        window = self._metric_windows.get(metric_key)

        if not baseline or not window or len(window) < 10:
            return None

        recent_values = [m.value for m in list(window)[-10:]]
        recent_mean = statistics.mean(recent_values)

        # Check if recent performance is significantly worse than baseline
        if metric_type in [
            PerformanceMetricType.LATENCY,
            PerformanceMetricType.MEMORY_USAGE,
            PerformanceMetricType.ERROR_RATE,
        ]:
            # Higher values are worse
            if recent_mean > baseline.baseline_mean * 1.5:  # 50% degradation threshold
                return {
                    "component": component,
                    "metric_type": metric_type.value,
                    "baseline_mean": baseline.baseline_mean,
                    "recent_mean": recent_mean,
                    "degradation_percent": (
                        (recent_mean - baseline.baseline_mean) / baseline.baseline_mean
                    )
                    * 100,
                    "severity": "HIGH" if recent_mean > baseline.baseline_mean * 2.0 else "MEDIUM",
                    "description": f"{component} {metric_type.value} has degraded by {((recent_mean - baseline.baseline_mean) / baseline.baseline_mean) * 100:.1f}%",
                }
        elif metric_type == PerformanceMetricType.THROUGHPUT:
            # Lower values are worse
            if recent_mean < baseline.baseline_mean * 0.5:  # 50% degradation threshold
                return {
                    "component": component,
                    "metric_type": metric_type.value,
                    "baseline_mean": baseline.baseline_mean,
                    "recent_mean": recent_mean,
                    "degradation_percent": (
                        (baseline.baseline_mean - recent_mean) / baseline.baseline_mean
                    )
                    * 100,
                    "severity": "HIGH" if recent_mean < baseline.baseline_mean * 0.25 else "MEDIUM",
                    "description": f"{component} {metric_type.value} has degraded by {((baseline.baseline_mean - recent_mean) / baseline.baseline_mean) * 100:.1f}%",
                }

        return None


# Singleton instance
_performance_monitor: Optional[INDIRAPerformanceMonitor] = None
_monitor_lock = threading.Lock()


def get_indira_performance_monitor(
    window_size: int = 100, baseline_samples: int = 50, anomaly_threshold_std: float = 2.5
) -> INDIRAPerformanceMonitor:
    """Get singleton instance of INDIRA performance monitor.

    Args:
        window_size: Number of data points in sliding window
        baseline_samples: Samples needed for baseline
        anomaly_threshold_std: Standard deviations for anomaly detection

    Returns:
        INDIRA performance monitor instance
    """
    global _performance_monitor

    with _monitor_lock:
        if _performance_monitor is None:
            _performance_monitor = INDIRAPerformanceMonitor(
                window_size=window_size,
                baseline_samples=baseline_samples,
                anomaly_threshold_std=anomaly_threshold_std,
            )
        return _performance_monitor
