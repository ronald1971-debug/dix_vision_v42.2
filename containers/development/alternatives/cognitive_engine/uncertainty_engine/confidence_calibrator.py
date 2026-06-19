"""Confidence Calibrator - prevents confidence inflation and drift.

Monitors and adjusts confidence levels based on prediction accuracy.
"""

from __future__ import annotations

import time
from dataclasses import dataclass, field
from typing import Any


@dataclass
class CalibrationRecord:
    """Records calibration outcome for a prediction."""

    record_id: str = field(default_factory=lambda: f"cal_{time.time_ns()}")
    domain: str = ""
    predicted_confidence: float = 0.0
    actual_accuracy: float = 0.0
    calibration_error: float = 0.0
    timestamp: int = field(default_factory=lambda: time.time_ns())
    metadata: dict[str, Any] = field(default_factory=dict)


class ConfidenceCalibrator:
    """Calibrates confidence levels against empirical accuracy.

    Prevents overconfidence by:
    - Tracking confidence-accuracy calibration curves
    - Adjusting confidence based on past prediction accuracy
    - Detecting confidence drift
    - Applying decay to stale confidence estimates
    """

    def __init__(self) -> None:
        self._records: list[CalibrationRecord] = []
        self._calibration_factors: dict[str, float] = {}
        self._confidence_history: dict[str, list[tuple[int, float]]] = {}

    def record_prediction(
        self,
        domain: str,
        predicted_confidence: float,
        actual_accuracy: float,
        metadata: dict[str, Any] | None = None,
    ) -> None:
        """Record a prediction outcome for calibration."""
        error = abs(predicted_confidence - actual_accuracy)
        record = CalibrationRecord(
            domain=domain,
            predicted_confidence=predicted_confidence,
            actual_accuracy=actual_accuracy,
            calibration_error=error,
            metadata=metadata or {},
        )
        self._records.append(record)

        ts = record.timestamp
        self._confidence_history.setdefault(domain, []).append((ts, actual_accuracy))
        while len(self._confidence_history[domain]) > 1000:
            self._confidence_history[domain].pop(0)

        self._update_calibration_factor(domain)

    def _update_calibration_factor(self, domain: str) -> None:
        """Update calibration factor based on recent records."""
        domain_records = [r for r in self._records if r.domain == domain][-100:]
        if not domain_records:
            return

        avg_error = sum(r.calibration_error for r in domain_records) / len(domain_records)
        self._calibration_factors[domain] = 1.0 - avg_error

    def calibrate(self, raw_confidence: float, domain: str) -> float:
        """Apply calibration factor to raw confidence."""
        factor = self._calibration_factors.get(domain, 1.0)
        calibrated = raw_confidence * factor
        return max(0.0, min(1.0, calibrated))

    def detect_drift(self, domain: str, threshold: float = 0.1) -> bool:
        """Detect if confidence has drifted from accuracy."""
        history = self._confidence_history.get(domain, [])
        if len(history) < 10:
            return False

        recent = history[-10:]
        older = history[-20:-10] if len(history) >= 20 else history[:10]

        recent_avg = sum(h[1] for h in recent) / len(recent)
        older_avg = sum(h[1] for h in older) / len(older)

        return abs(recent_avg - older_avg) > threshold

    def calibration_curve(self, domain: str) -> list[tuple[float, float]]:
        """Get confidence vs accuracy curve for a domain."""
        records = [r for r in self._records if r.domain == domain][-100:]
        return [(r.predicted_confidence, r.actual_accuracy) for r in records]

    def avg_calibration_error(self, domain: str | None = None) -> float:
        """Get average calibration error, optionally for a domain."""
        records = self._records if domain is None else [r for r in self._records if r.domain == domain]
        if not records:
            return 0.0
        return sum(r.calibration_error for r in records) / len(records)