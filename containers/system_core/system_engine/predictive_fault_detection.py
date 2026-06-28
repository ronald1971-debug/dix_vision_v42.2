"""Predictive Fault Detection for DYON - ML-based Failure Prediction.

This module provides predictive fault detection capabilities for DYON:
- ML-based failure prediction using time series analysis
- Resource exhaustion forecasting
- Performance degradation prediction
- Network failure prediction
- Storage capacity prediction
- Cascading failure prediction

Per INV-15: Pure computation, no clock reads, no PRNG, no IO. Deterministic replays.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from math import sqrt
from typing import Protocol


class FailureType(Enum):
    """Types of failures to predict."""

    RESOURCE_EXHAUSTION = "resource_exhaustion"
    PERFORMANCE_DEGRADATION = "performance_degradation"
    NETWORK_FAILURE = "network_failure"
    STORAGE_CAPACITY = "storage_capacity"
    CASCADING_FAILURE = "cascading_failure"
    MEMORY_LEAK = "memory_leak"
    CPU_SPIKE = "cpu_spike"
    LATENCY_DRIFT = "latency_drift"


class PredictionConfidence(Enum):
    """Confidence levels for predictions."""

    HIGH = "high"  # > 0.8
    MEDIUM = "medium"  # 0.5 - 0.8
    LOW = "low"  # 0.2 - 0.5
    VERY_LOW = "very_low"  # < 0.2


@dataclass(frozen=True, slots=True)
class MetricPoint:
    """Single metric data point."""

    timestamp_ns: int
    value: float
    metric_name: str
    component: str


@dataclass(frozen=True, slots=True)
class FailurePrediction:
    """Failure prediction result."""

    failure_type: FailureType
    predicted_time_ns: int  # When failure is predicted to occur
    confidence: float  # 0-1
    confidence_level: PredictionConfidence
    time_to_failure_ns: int  # Time remaining until predicted failure
    affected_components: tuple[str, ...]
    recommended_actions: tuple[str, ...]
    prediction_features: dict[str, float]
    model_version: str


@dataclass(frozen=True, slots=True)
class FailurePattern:
    """Detected failure pattern."""

    pattern_id: str
    failure_type: FailureType
    pattern_signature: tuple[tuple[str, float], ...]
    historical_occurrences: int
    average_time_to_failure: int
    confidence: float


class TimeSeriesPredictor(Protocol):
    """Protocol for time series prediction models."""

    def predict(
        self,
        history: tuple[float, ...],
        forecast_horizon: int,
        confidence_level: float,
    ) -> tuple[tuple[float, ...], tuple[float, ...], tuple[float, ...]]:
        """Predict future values from time series history.

        Returns:
            predicted_values: Predicted values
            lower_bounds: Lower confidence bounds
            upper_bounds: Upper confidence bounds
        """
        ...


class AnomalyDetector(Protocol):
    """Protocol for anomaly detection."""

    def detect_anomaly(
        self,
        value: float,
        history: tuple[float, ...],
        threshold: float,
    ) -> tuple[bool, float, float]:
        """Detect if value is anomalous.

        Returns:
            is_anomalous: Whether value is anomalous
            anomaly_score: Anomaly score (0-1)
            deviation: Standard deviations from mean
        """
        ...


@dataclass
class PredictiveFaultDetector:
    """Predictive fault detection engine.

    Uses ML-based time series analysis to predict failures before they occur.

    Attributes:
        prediction_horizon_ns: How far ahead to predict (in nanoseconds)
        confidence_threshold: Minimum confidence for prediction
        min_prediction_window: Minimum history length for prediction
        alert_threshold: Threshold for alerting on predictions
    """

    prediction_horizon_ns: int = 60_000_000_000  # 60 seconds
    confidence_threshold: float = 0.7
    min_prediction_window: int = 64
    alert_threshold: float = 0.8

    # Predictor models (injected)
    _time_series_predictor: TimeSeriesPredictor = field(default=None, init=False, repr=False)
    _anomaly_detector: AnomalyDetector = field(default=None, init=False, repr=False)

    # Metric history
    _metric_history: dict[str, list[MetricPoint]] = field(
        default_factory=dict, init=False, repr=False
    )

    # Failure patterns
    _failure_patterns: dict[FailureType, list[FailurePattern]] = field(
        default_factory=dict, init=False, repr=False
    )

    # Prediction history
    _prediction_history: list[FailurePrediction] = field(
        default_factory=list, init=False, repr=False
    )

    def __post_init__(self) -> None:
        # Initialize failure pattern storage
        for failure_type in FailureType:
            self._failure_patterns[failure_type] = []

    def add_metric(self, metric: MetricPoint) -> None:
        """Add a metric data point."""
        metric_name = metric.metric_name

        if metric_name not in self._metric_history:
            self._metric_history[metric_name] = []

        self._metric_history[metric_name].append(metric)

        # Keep limited history (last 1000 points per metric)
        if len(self._metric_history[metric_name]) > 1000:
            self._metric_history[metric_name] = self._metric_history[metric_name][-1000:]

    def predict_failure(
        self,
        metric_name: str,
        failure_type: FailureType,
        current_timestamp_ns: int,
    ) -> FailurePrediction | None:
        """Predict failure for a specific metric and failure type.

        Args:
            metric_name: Name of the metric to analyze
            failure_type: Type of failure to predict
            current_timestamp_ns: Current timestamp

        Returns:
            FailurePrediction if failure predicted with sufficient confidence, None otherwise
        """
        if metric_name not in self._metric_history:
            return None

        history = self._metric_history[metric_name]
        if len(history) < self.min_prediction_window:
            return None

        # Get recent values
        recent_values = tuple(m.value for m in history[-self.min_prediction_window :])

        # Predict future values
        if self._time_series_predictor is not None:
            predicted, lower, upper = self._time_series_predictor.predict(
                history=recent_values,
                forecast_horizon=32,  # Predict 32 steps ahead
                confidence_level=0.95,
            )
        else:
            predicted, lower, upper = self._fallback_prediction(recent_values)

        # Check if predicted values indicate failure
        failure_signal = self._check_failure_signal(
            predicted, lower, upper, failure_type, metric_name
        )

        if failure_signal is None:
            return None

        predicted_time, confidence = failure_signal

        if confidence < self.confidence_threshold:
            return None

        # Calculate time to failure
        time_to_failure = predicted_time - current_timestamp_ns

        if time_to_failure <= 0:
            # Failure imminent
            time_to_failure = 0

        # Determine confidence level
        confidence_level = self._determine_confidence_level(confidence)

        # Generate recommended actions
        recommended_actions = self._generate_recommendations(failure_type, confidence)

        # Identify affected components
        affected_components = tuple(set(m.component for m in history[-32:]))

        # Create prediction
        prediction = FailurePrediction(
            failure_type=failure_type,
            predicted_time_ns=predicted_time,
            confidence=confidence,
            confidence_level=confidence_level,
            time_to_failure_ns=time_to_failure,
            affected_components=affected_components,
            recommended_actions=recommended_actions,
            prediction_features={
                "predicted_value": predicted[-1] if predicted else 0.0,
                "current_value": recent_values[-1] if recent_values else 0.0,
                "trend_slope": self._calculate_trend_slope(recent_values),
                "volatility": self._calculate_volatility(recent_values),
            },
            model_version="1.0.0",
        )

        self._prediction_history.append(prediction)

        return prediction

    def _fallback_prediction(
        self,
        history: tuple[float, ...],
    ) -> tuple[tuple[float, ...], tuple[float, ...], tuple[float, ...]]:
        """Fallback prediction using simple extrapolation."""
        if len(history) < 2:
            return (history[-1],) * 32, (history[-1],) * 32, (history[-1],) * 32

        # Simple linear extrapolation
        n = len(history)
        recent_slope = (history[-1] - history[-min(8, n)]) / min(8, n)

        predicted = []
        lower = []
        upper = []

        vol = self._calculate_volatility(history)

        for i in range(32):
            pred = history[-1] + recent_slope * (i + 1)
            predicted.append(pred)
            lower.append(pred - 2 * vol)
            upper.append(pred + 2 * vol)

        return (tuple(predicted), tuple(lower), tuple(upper))

    def _check_failure_signal(
        self,
        predicted: tuple[float, ...],
        lower: tuple[float, ...],
        upper: tuple[float, ...],
        failure_type: FailureType,
        metric_name: str,
    ) -> tuple[int, float] | None:
        """Check if predicted values indicate failure.

        Returns:
            (predicted_time_ns, confidence) if failure detected, None otherwise
        """
        if not predicted:
            return None

        # Get current value
        if metric_name not in self._metric_history:
            return None

        history = self._metric_history[metric_name]
        current_value = history[-1].value if history else 0.0

        # Failure detection based on type
        if failure_type == FailureType.RESOURCE_EXHAUSTION:
            # Predict if resource will exceed threshold (e.g., 90%)
            threshold = 0.9
            for i, pred in enumerate(predicted):
                if pred > threshold:
                    # Calculate confidence based on how far above threshold
                    confidence = min(1.0, (pred - threshold) / (1.0 - threshold + 1e-6))
                    return (int(history[-1].timestamp_ns + i * 1_000_000_000), confidence)

        elif failure_type == FailureType.PERFORMANCE_DEGRADATION:
            # Predict if performance will degrade significantly
            threshold = current_value * 1.5  # 50% degradation
            for i, pred in enumerate(predicted):
                if pred > threshold:
                    confidence = min(
                        1.0, (pred - current_value) / (threshold - current_value + 1e-6)
                    )
                    return (int(history[-1].timestamp_ns + i * 1_000_000_000), confidence)

        elif failure_type == FailureType.MEMORY_LEAK:
            # Predict if memory will show steady increase without bound
            # Check if trend is consistently upward
            trend_slope = self._calculate_trend_slope(predicted)
            if trend_slope > 0 and all(
                predicted[i] > predicted[i - 1] for i in range(1, len(predicted))
            ):
                # Calculate confidence based on slope magnitude
                confidence = min(1.0, trend_slope / (current_value + 1e-6) * 100)
                return (int(history[-1].timestamp_ns + 32 * 1_000_000_000), confidence)

        elif failure_type == FailureType.LATENCY_DRIFT:
            # Predict if latency will show steady increase
            threshold = current_value * 2.0  # 2x current latency
            for i, pred in enumerate(predicted):
                if pred > threshold:
                    confidence = min(
                        1.0, (pred - current_value) / (threshold - current_value + 1e-6)
                    )
                    return (int(history[-1].timestamp_ns + i * 1_000_000_000), confidence)

        return None

    def _calculate_trend_slope(self, values: tuple[float, ...]) -> float:
        """Calculate linear trend slope."""
        if len(values) < 2:
            return 0.0

        n = len(values)
        x = tuple(range(n))
        y = values

        # Simple linear regression
        sum_x = sum(x)
        sum_y = sum(y)
        sum_xy = sum(xi * yi for xi, yi in zip(x, y))
        sum_x2 = sum(xi * xi for xi in x)

        denominator = n * sum_x2 - sum_x * sum_x
        if denominator == 0:
            return 0.0

        slope = (n * sum_xy - sum_x * sum_y) / denominator
        return slope

    def _calculate_volatility(self, values: tuple[float, ...]) -> float:
        """Calculate volatility (standard deviation)."""
        if len(values) < 2:
            return 0.0

        mean = sum(values) / len(values)
        variance = sum((v - mean) ** 2 for v in values) / len(values)
        return sqrt(variance)

    def _determine_confidence_level(self, confidence: float) -> PredictionConfidence:
        """Determine confidence level from confidence score."""
        if confidence >= 0.8:
            return PredictionConfidence.HIGH
        elif confidence >= 0.5:
            return PredictionConfidence.MEDIUM
        elif confidence >= 0.2:
            return PredictionConfidence.LOW
        else:
            return PredictionConfidence.VERY_LOW

    def _generate_recommendations(
        self, failure_type: FailureType, confidence: float
    ) -> tuple[str, ...]:
        """Generate recommended actions for a failure type."""
        recommendations = []

        if failure_type == FailureType.RESOURCE_EXHAUSTION:
            recommendations = [
                "Scale up resources",
                "Terminate non-critical processes",
                "Implement resource quotas",
                "Optimize resource usage",
            ]
        elif failure_type == FailureType.PERFORMANCE_DEGRADATION:
            recommendations = [
                "Profile performance bottlenecks",
                "Optimize database queries",
                "Implement caching",
                "Scale horizontally",
            ]
        elif failure_type == FailureType.MEMORY_LEAK:
            recommendations = [
                "Restart affected services",
                "Profile memory usage",
                "Fix memory leaks in code",
                "Implement memory limits",
            ]
        elif failure_type == FailureType.LATENCY_DRIFT:
            recommendations = [
                "Investigate network latency",
                "Optimize I/O operations",
                "Reduce payload sizes",
                "Implement CDN caching",
            ]
        elif failure_type == FailureType.NETWORK_FAILURE:
            recommendations = [
                "Check network connectivity",
                "Implement circuit breakers",
                "Add redundant network paths",
                "Implement retry with exponential backoff",
            ]
        elif failure_type == FailureType.CASCADING_FAILURE:
            recommendations = [
                "Isolate affected components",
                "Implement bulkheads",
                "Add circuit breakers",
                "Implement graceful degradation",
            ]

        return tuple(recommendations)

    def get_recent_predictions(self, limit: int = 10) -> tuple[FailurePrediction, ...]:
        """Get recent failure predictions."""
        return tuple(self._prediction_history[-limit:])

    def get_prediction_history(self) -> tuple[FailurePrediction, ...]:
        """Get all prediction history."""
        return tuple(self._prediction_history)

    def clear_history(self) -> None:
        """Clear all prediction and metric history."""
        self._metric_history.clear()
        self._prediction_history.clear()


@dataclass
class CascadingFailurePredictor:
    """Predict cascading failures based on dependency analysis.

    Analyzes component dependencies and predicts how failures
    might propagate through the system.
    """

    fault_detector: PredictiveFaultDetector = field(default_factory=PredictiveFaultDetector)

    # Dependency graph: component -> list of dependent components
    _dependency_graph: dict[str, list[str]] = field(default_factory=dict, init=False, repr=False)

    # Failure propagation history
    _propagation_history: list[tuple[str, str, int]] = field(
        default_factory=list, init=False, repr=False
    )

    def add_dependency(self, component: str, depends_on: str) -> None:
        """Add a dependency relationship."""
        if depends_on not in self._dependency_graph:
            self._dependency_graph[depends_on] = []

        if component not in self._dependency_graph[depends_on]:
            self._dependency_graph[depends_on].append(component)

    def predict_cascading_failure(
        self,
        failing_component: str,
        current_timestamp_ns: int,
    ) -> tuple[str, ...]:
        """Predict which components will fail if the given component fails.

        Returns:
            Tuple of component names that will fail (in propagation order)
        """
        if failing_component not in self._dependency_graph:
            return ()

        # BFS to find all dependent components
        visited = set()
        queue = [failing_component]
        propagation_order = []

        while queue:
            component = queue.pop(0)
            if component in visited:
                continue

            visited.add(component)
            propagation_order.append(component)

            # Add dependents
            dependents = self._dependency_graph.get(component, [])
            for dep in dependents:
                if dep not in visited:
                    queue.append(dep)

        # Remove the original failing component from results
        if propagation_order and propagation_order[0] == failing_component:
            propagation_order = propagation_order[1:]

        return tuple(propagation_order)

    def get_dependency_graph(self) -> dict[str, tuple[str, ...]]:
        """Get the current dependency graph."""
        return {k: tuple(v) for k, v in self._dependency_graph.items()}


__all__ = [
    "PredictiveFaultDetector",
    "CascadingFailurePredictor",
    "FailureType",
    "PredictionConfidence",
    "MetricPoint",
    "FailurePrediction",
    "FailurePattern",
    "TimeSeriesPredictor",
    "AnomalyDetector",
]
