"""Cognitive Health Monitor - monitors cognitive failures.

Monitors the same categories as system resources:
- CPU → Belief Drift
- Memory → Knowledge Drift
- Latency → Reasoning Quality
"""

from __future__ import annotations

from cognitive_engine.cognitive_health.drift_detector import DriftDetector, DriftType
from cognitive_engine.cognitive_health.health_report import HealthReport, HealthStatus


class CognitiveHealthMonitor:
    """Monitors cognitive health of INDIRA.

    Tracks cognitive failures analogous to system failures:
    - Belief Drift (like CPU overload)
    - Knowledge Drift (like memory corruption)
    - Strategy Drift (like latency)
    - Confidence Inflation (overconfidence)
    - Memory Corruption (lost knowledge)
    - Reasoning Quality (decision quality)
    """

    def __init__(self) -> None:
        self._detector = DriftDetector()
        self._reports: list[HealthReport] = []
        self._memory_checksums: dict[str, str] = {}

    def check_belief_drift(self, entity_id: str, prediction: float, actual: float) -> None:
        """Check for belief drift."""
        delta = abs(prediction - actual)
        self._detector.check_drift(entity_id, delta, DriftType.BELIEF_DRIFT)

    def check_knowledge_drift(self, entity_id: str, metric: float) -> None:
        """Check for knowledge drift."""
        self._detector.check_drift(entity_id, metric, DriftType.KNOWLEDGE_DRIFT)

    def check_strategy_drift(self, strategy_id: str, metric: float) -> None:
        """Check for strategy drift."""
        self._detector.check_drift(strategy_id, metric, DriftType.STRATEGY_DRIFT)

    def check_confidence_inflation(self, entity_id: str, confidence: float, accuracy: float) -> None:
        """Check for confidence inflation."""
        inflation = confidence - accuracy
        self._detector.check_drift(entity_id, inflation, DriftType.CONFIDENCE_INFLATION)

    def verify_memory_integrity(self, storage_key: str, checksum: str) -> bool:
        """Verify memory hasn't been corrupted."""
        if storage_key in self._memory_checksums:
            if self._memory_checksums[storage_key] != checksum:
                return False
        self._memory_checksums[storage_key] = checksum
        return True

    def generate_report(self) -> HealthReport:
        """Generate cognitive health report."""
        events = self._detector.get_events(100)

        status = HealthStatus.HEALTHY
        if len(events) > 50:
            status = HealthStatus.CRITICAL
        elif len(events) > 20:
            status = HealthStatus.DEGRADED

        report = HealthReport(
            status=status,
            belief_drift_count=len(self._detector.get_events_by_type(DriftType.BELIEF_DRIFT)),
            knowledge_drift_count=len(self._detector.get_events_by_type(DriftType.KNOWLEDGE_DRIFT)),
            strategy_drift_count=len(self._detector.get_events_by_type(DriftType.STRATEGY_DRIFT)),
            confidence_inflation_count=len(self._detector.get_events_by_type(DriftType.CONFIDENCE_INFLATION)),
            drift_events=tuple(events),
        )
        self._reports.append(report)
        return report

    def get_latest_report(self) -> HealthReport | None:
        """Get most recent health report."""
        return self._reports[-1] if self._reports else None

    def get_report_history(self, limit: int = 10) -> list[HealthReport]:
        """Get health report history."""
        return self._reports[-limit:]