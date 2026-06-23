"""Liquid State Machine for DYON Anomaly Detection.

This module provides LSM capabilities for detecting temporal anomalies in
system metrics, enabling real-time detection of performance degradation,
resource pressure, and other system issues.
"""

from __future__ import annotations

import logging
import threading
import time
from collections import deque
from dataclasses import dataclass
from enum import Enum
from typing import Any, Dict, List, Optional

import numpy as np

logger = logging.getLogger(__name__)


class AnomalyType(str, Enum):
    """Types of anomalies detected."""

    PERFORMANCE_DEGRADATION = "PERFORMANCE_DEGRADATION"
    RESOURCE_PRESSURE = "RESOURCE_PRESSURE"
    ERROR_SPIKE = "ERROR_SPIKE"
    LATENCY_DRIFT = "LATENCY_DRIFT"
    MEMORY_LEAK = "MEMORY_LEAK"
    CODE_QUALITY_DECLINE = "CODE_QUALITY_DECLINE"
    TEST_COVERAGE_DROP = "TEST_COVERAGE_DROP"


@dataclass
class AnomalyDetectionResult:
    """Result of anomaly detection."""

    anomaly_id: str
    anomaly_type: AnomalyType
    severity: float  # 0-1
    component: str
    temporal_signature: np.ndarray
    predicted_impact: str
    confidence: float
    timestamp: float


class DYONLiquidReservoir:
    """Liquid reservoir for system anomaly detection."""

    def __init__(
        self, n_neurons: int = 80, connectivity: float = 0.15, spectral_radius: float = 0.85
    ):
        """
        Initialize DYON liquid reservoir.

        Args:
            n_neurons: Number of reservoir neurons
            connectivity: Connectivity probability
            spectral_radius: Spectral radius for stability
        """
        self.n_neurons = n_neurons
        self.connectivity = connectivity
        self.spectral_radius = spectral_radius

        # Build reservoir weights with higher connectivity for system monitoring
        self.reservoir_weights = self._build_reservoir_weights()

        # Reservoir state
        self.state = np.zeros(n_neurons)

        # Input weights
        self.input_weights = None

        # Baseline state for comparison
        self.baseline_state = np.zeros(n_neurons)
        self.baseline_history: deque = deque(maxlen=100)

        logger.info(f"[DYON_LSM] DYON Liquid Reservoir initialized with {n_neurons} neurons")

    def _build_reservoir_weights(self) -> np.ndarray:
        """Build reservoir weight matrix."""
        weights = np.random.randn(self.n_neurons, self.n_neurons)

        # Apply connectivity mask
        mask = np.random.random((self.n_neurons, self.n_neurons)) < self.connectivity
        weights = weights * mask

        # Scale to desired spectral radius
        try:
            eigenvalues = np.linalg.eigvals(weights)
            max_eigenvalue = np.max(np.abs(eigenvalues))
            if max_eigenvalue > 0:
                weights = weights / max_eigenvalue * self.spectral_radius
        except:
            pass  # Fallback if eigenvalue computation fails

        return weights

    def initialize_input_weights(self, n_inputs: int) -> None:
        """Initialize input weights."""
        self.input_weights = np.random.uniform(-0.3, 0.3, (self.n_neurons, n_inputs))

    def update(self, input_signal: np.ndarray, dt: float = 1.0) -> np.ndarray:
        """
        Update reservoir state with input signal.

        Args:
            input_signal: Input signal vector
            dt: Time step

        Returns:
            New reservoir state
        """
        if self.input_weights is None or self.input_weights.shape[1] != len(input_signal):
            self.initialize_input_weights(len(input_signal))

        # Compute reservoir update
        input_projection = self.input_weights @ input_signal
        reservoir_projection = self.reservoir_weights @ self.state

        # Apply tanh activation for stability
        new_state = np.tanh(input_projection + reservoir_projection)

        # Apply leaky integration
        leak = 0.95
        new_state = leak * self.state + (1 - leak) * new_state

        # Update state
        self.state = new_state

        # Update baseline periodically
        self._update_baseline()

        return new_state

    def _update_baseline(self) -> None:
        """Update baseline state."""
        self.baseline_history.append(self.state.copy())
        if len(self.baseline_history) > 10:
            self.baseline_state = np.mean(list(self.baseline_history), axis=0)

    def get_deviation_from_baseline(self) -> float:
        """Calculate deviation from baseline state."""
        deviation = np.linalg.norm(self.state - self.baseline_state)
        return deviation

    def reset(self) -> None:
        """Reset reservoir state."""
        self.state = np.zeros(self.n_neurons)
        self.baseline_state = np.zeros(self.n_neurons)
        self.baseline_history.clear()


class SystemAnomalyDetector:
    """Anomaly detection using LSM for system monitoring."""

    def __init__(self, n_reservoir_neurons: int = 80):
        """
        Initialize system anomaly detector.

        Args:
            n_reservoir_neurons: Number of reservoir neurons
        """
        self.liquid_reservoir = DYONLiquidReservoir(n_neurons=n_reservoir_neurons)

        # Anomaly database
        self.anomaly_database: Dict[str, AnomalyDetectionResult] = {}

        # Anomaly thresholds
        self.deviation_thresholds = {
            AnomalyType.PERFORMANCE_DEGRADATION: 2.0,
            AnomalyType.RESOURCE_PRESSURE: 2.5,
            AnomalyType.ERROR_SPIKE: 3.0,
            AnomalyType.LATENCY_DRIFT: 2.2,
            AnomalyType.MEMORY_LEAK: 1.8,
            AnomalyType.CODE_QUALITY_DECLINE: 1.5,
            AnomalyType.TEST_COVERAGE_DROP: 1.5,
        }

        # Temporal window
        self.metric_history: deque = deque(maxlen=100)

        self.lock = threading.Lock()

        logger.info("[DYON_LSM] System Anomaly Detector initialized")

    def detect_anomaly(
        self, current_metrics: Dict[str, float], historical_window: List[Dict[str, float]] = None
    ) -> Optional[AnomalyDetectionResult]:
        """
        Detect anomaly in current metrics.

        Args:
            current_metrics: Current system metrics
            historical_window: Historical metrics for context

        Returns:
            Anomaly detection result if anomaly detected, None otherwise
        """
        with self.lock:
            anomaly_id = f"anomaly_{int(time.time())}"

            # Convert metrics to feature vector
            features = self._metrics_to_features(current_metrics)

            # Process through reservoir
            reservoir_state = self.liquid_reservoir.update(features)

            # Calculate deviation from baseline
            deviation = self.liquid_reservoir.get_deviation_from_baseline()

            # Store in history
            self.metric_history.append(current_metrics)

            # Check against thresholds for each anomaly type
            detected_anomalies = []
            for anomaly_type, threshold in self.deviation_thresholds.items():
                if deviation > threshold:
                    severity = min((deviation - threshold) / threshold, 1.0)

                    # Determine component
                    component = self._identify_responsible_component(current_metrics)

                    # Extract temporal signature
                    temporal_signature = self._extract_temporal_signature()

                    # Predict impact
                    predicted_impact = self._predict_impact(anomaly_type, severity)

                    # Calculate confidence
                    confidence = min(deviation / (threshold * 1.5), 1.0)

                    anomaly_result = AnomalyDetectionResult(
                        anomaly_id=anomaly_id,
                        anomaly_type=anomaly_type,
                        severity=severity,
                        component=component,
                        temporal_signature=temporal_signature,
                        predicted_impact=predicted_impact,
                        confidence=confidence,
                        timestamp=time.time(),
                    )

                    detected_anomalies.append(anomaly_result)

            # Return most severe anomaly if any
            if detected_anomalies:
                most_severe = max(detected_anomalies, key=lambda a: a.severity)
                self.anomaly_database[anomaly_id] = most_severe
                return most_severe

            return None

    def _metrics_to_features(self, metrics: Dict[str, float]) -> np.ndarray:
        """Convert metrics to feature vector."""
        # Normalize metrics
        features = []

        feature_mappings = [
            ("cpu_usage", lambda v: v / 100.0),
            ("memory_usage", lambda v: v / 100.0),
            ("latency_p99", lambda v: min(v / 1000.0, 1.0)),
            ("error_rate", lambda v: min(v * 10.0, 1.0)),
            ("event_rate", lambda v: min(v / 1000.0, 1.0)),
            ("test_coverage", lambda v: v / 100.0),
            ("code_complexity", lambda v: min(v / 50.0, 1.0)),
        ]

        for metric_name, normalization_func in feature_mappings:
            value = metrics.get(metric_name, 0.0)
            features.append(normalization_func(value))

        return np.array(features)

    def _identify_responsible_component(self, metrics: Dict[str, float]) -> str:
        """Identify component responsible for anomaly."""
        # Find metric with highest deviation from normal
        component_scores = {}

        if metrics.get("cpu_usage", 0) > 80:
            component_scores["compute"] = metrics["cpu_usage"]
        if metrics.get("memory_usage", 0) > 80:
            component_scores["memory"] = metrics["memory_usage"]
        if metrics.get("latency_p99", 0) > 500:
            component_scores["network"] = metrics["latency_p99"] / 10
        if metrics.get("error_rate", 0) > 0.1:
            component_scores["application"] = metrics["error_rate"] * 100

        if component_scores:
            return max(component_scores, key=component_scores.get)
        return "unknown"

    def _extract_temporal_signature(self) -> np.ndarray:
        """Extract temporal signature from metric history."""
        if len(self.metric_history) < 10:
            return np.zeros(8)

        recent_metrics = list(self.metric_history)[-10:]

        # Compute trend for each metric
        signature = []
        metric_names = ["cpu_usage", "memory_usage", "latency_p99", "error_rate"]

        for metric in metric_names:
            values = [m.get(metric, 0) for m in recent_metrics]
            if values:
                trend = (values[-1] - values[0]) / max(1.0, values[0]) if values[0] > 0 else 0
                signature.append(trend)
            else:
                signature.append(0.0)

        # Add variance components
        for metric in metric_names:
            values = [m.get(metric, 0) for m in recent_metrics]
            if values:
                variance = np.var(values) / (max(values) if max(values) > 0 else 1.0)
                signature.append(variance)
            else:
                signature.append(0.0)

        return np.array(signature)

    def _predict_impact(self, anomaly_type: AnomalyType, severity: float) -> str:
        """Predict impact of anomaly."""
        impact_map = {
            AnomalyType.PERFORMANCE_DEGRADATION: (
                "reduced_system_responsiveness" if severity < 0.7 else "system_slowdown"
            ),
            AnomalyType.RESOURCE_PRESSURE: (
                "increased_resource_contention" if severity < 0.7 else "resource_exhaustion"
            ),
            AnomalyType.ERROR_SPIKE: "service_degradation" if severity < 0.7 else "service_failure",
            AnomalyType.LATENCY_DRIFT: (
                "increased_response_times" if severity < 0.7 else "timeout_errors"
            ),
            AnomalyType.MEMORY_LEAK: "gradual_memory_increase" if severity < 0.7 else "oom_risk",
            AnomalyType.CODE_QUALITY_DECLINE: (
                "maintainability_decrease" if severity < 0.7 else "technical_debt_accumulation"
            ),
            AnomalyType.TEST_COVERAGE_DROP: (
                "quality_risk_increase" if severity < 0.7 else "regression_risk"
            ),
        }

        return impact_map.get(anomaly_type, "unknown_impact")

    def train_baseline(self, normal_metrics: List[Dict[str, float]]) -> None:
        """
        Train baseline with normal system metrics.

        Args:
            normal_metrics: List of normal metric readings
        """
        logger.info(f"[DYON_LSM] Training baseline with {len(normal_metrics)} samples")

        # Reset before training
        self.liquid_reservoir.reset()

        for metrics in normal_metrics:
            features = self._metrics_to_features(metrics)
            self.liquid_reservoir.update(features)

            # Ensure baseline updates
            self.liquid_reservoir._update_baseline()

        # Final baseline update
        if self.liquid_reservoir.baseline_history:
            self.liquid_reservoir.baseline_state = np.mean(
                list(self.liquid_reservoir.baseline_history), axis=0
            )

        logger.info("[DYON_LSM] Baseline training completed")

    def get_statistics(self) -> Dict[str, Any]:
        """Get anomaly detection statistics."""
        with self.lock:
            return {
                "reservoir_neurons": self.liquid_reservoir.n_neurons,
                "anomalies_detected": len(self.anomaly_database),
                "baseline_state_norm": np.linalg.norm(self.liquid_reservoir.baseline_state),
                "metric_history_size": len(self.metric_history),
                "deviation_from_baseline": self.liquid_reservoir.get_deviation_from_baseline(),
            }


class DYONLSMAnomalyIntelligence:
    """DYON LSM anomaly intelligence integration."""

    def __init__(self):
        self.anomaly_detector = SystemAnomalyDetector()
        self._initialized = False

    def start(self) -> bool:
        """Start LSM anomaly intelligence."""
        logger.info("[DYON_LSM] Starting DYON LSM anomaly intelligence...")
        self._initialized = True
        logger.info("[DYON_LSM] DYON LSM anomaly intelligence started")
        return True

    def stop(self) -> bool:
        """Stop LSM anomaly intelligence."""
        logger.info("[DYON_LSM] Stopping DYON LSM anomaly intelligence...")
        self._initialized = False
        logger.info("[DYON_LSM] DYON LSM anomaly intelligence stopped")
        return True

    def detect_system_anomaly(
        self, current_metrics: Dict[str, float]
    ) -> Optional[AnomalyDetectionResult]:
        """Detect system anomaly."""
        return self.anomaly_detector.detect_anomaly(current_metrics)

    def get_statistics(self) -> Dict[str, Any]:
        """Get LSM anomaly intelligence statistics."""
        return self.anomaly_detector.get_statistics()


# Singleton instance
_dyon_lsm_anomaly_intelligence: Optional[DYONLSMAnomalyIntelligence] = None
_dyon_lsm_anomaly_intelligence_lock = threading.Lock()


def get_dyon_lsm_anomaly_intelligence() -> DYONLSMAnomalyIntelligence:
    """Get the singleton DYON LSM anomaly intelligence instance."""
    global _dyon_lsm_anomaly_intelligence
    if _dyon_lsm_anomaly_intelligence is None:
        with _dyon_lsm_anomaly_intelligence_lock:
            if _dyon_lsm_anomaly_intelligence is None:
                _dyon_lsm_anomaly_intelligence = DYONLSMAnomalyIntelligence()
    return _dyon_lsm_anomaly_intelligence


__all__ = [
    "DYONLSMAnomalyIntelligence",
    "get_dyon_lsm_anomaly_intelligence",
    "SystemAnomalyDetector",
    "DYONLiquidReservoir",
    "AnomalyDetectionResult",
    "AnomalyType",
]
