"""Blindspot Detector - identifies unknown unknowns.

Uses anomaly detection and pattern recognition to find knowledge gaps
that haven't been explicitly recognized.
"""

from __future__ import annotations

import time
from dataclasses import dataclass, field
from typing import Any


@dataclass
class BlindspotSignal:
    """Detected blindspot indicator."""

    signal_id: str = field(default_factory=lambda: f"blindspot_{time.time_ns()}")
    domain: str = ""
    pattern: str = ""
    anomaly_score: float = 0.0
    timestamp: int = field(default_factory=lambda: time.time_ns())
    context: dict[str, Any] = field(default_factory=dict)


class BlindspotDetector:
    """Detects unknown unknowns through anomaly and variance analysis.

    Monitors for:
    - Unexpected outcome patterns
    - Performance gaps not explained by known factors
    - Regime changes not captured in current models
    - Trader behavior that doesn't fit existing archetypes
    """

    def __init__(self, threshold: float = 0.7) -> None:
        self.threshold = threshold
        self._signals: list[BlindspotSignal] = []
        self._domain_variance: dict[str, float] = {}

    def analyze(
        self, domain: str, expected: float, actual: float, context: dict[str, Any] | None = None
    ) -> BlindspotSignal | None:
        """Analyze deviation and detect if it indicates a blindspot.

        Args:
            domain: The knowledge domain being analyzed
            expected: Expected value based on current knowledge
            actual: Actual observed value
            context: Additional context for the analysis

        Returns:
            BlindspotSignal if deviation indicates unknown unknown, None otherwise
        """
        variance = abs(expected - actual)
        self._domain_variance[domain] = variance

        if variance > self.threshold:
            signal = BlindspotSignal(
                domain=domain,
                pattern=f"{domain}_variance_spike",
                anomaly_score=variance,
                context=context or {},
            )
            self._signals.append(signal)
            return signal
        return None

    def detect_pattern_gap(
        self, pattern_id: str, expected_count: int, actual_count: int
    ) -> BlindspotSignal | None:
        """Detect gaps in pattern recognition."""
        gap_ratio = abs(expected_count - actual_count) / max(expected_count, 1)
        if gap_ratio > self.threshold:
            signal = BlindspotSignal(
                domain="pattern_recognition",
                pattern=f"pattern_gap_{pattern_id}",
                anomaly_score=gap_ratio,
            )
            self._signals.append(signal)
            return signal
        return None

    def detect_regime_mismatch(self, regime: str, confidence: float) -> BlindspotSignal | None:
        """Detect when regime classification confidence is low."""
        if confidence < 0.5:
            signal = BlindspotSignal(
                domain="regime_detection",
                pattern=f"regime_mismatch_{regime}",
                anomaly_score=1.0 - confidence,
            )
            self._signals.append(signal)
            return signal
        return None

    def get_recent_signals(self, limit: int = 10) -> list[BlindspotSignal]:
        """Get most recent blindspot signals."""
        return self._signals[-limit:]

    def get_signals_by_domain(self, domain: str) -> list[BlindspotSignal]:
        """Get blindspot signals for a specific domain."""
        return [s for s in self._signals if s.domain == domain]
