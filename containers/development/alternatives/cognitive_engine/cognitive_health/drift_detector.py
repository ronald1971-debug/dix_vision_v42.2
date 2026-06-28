"""Drift Detector - detects cognitive drifts in real-time."""

from __future__ import annotations

import time
from dataclasses import dataclass, field
from enum import Enum
from typing import Any


class DriftType(Enum):
    """Types of cognitive drift to monitor."""

    BELIEF_DRIFT = "belief_drift"
    KNOWLEDGE_DRIFT = "knowledge_drift"
    STRATEGY_DRIFT = "strategy_drift"
    CONFIDENCE_INFLATION = "confidence_inflation"


@dataclass
class DriftEvent:
    """Detected drift event."""

    event_id: str = field(default_factory=lambda: f"drift_{time.time_ns()}")
    drift_type: DriftType = DriftType.BELIEF_DRIFT
    entity_id: str = ""
    before_value: float = 0.0
    after_value: float = 0.0
    magnitude: float = 0.0
    detected_at: int = field(default_factory=lambda: time.time_ns())
    details: dict[str, Any] = field(default_factory=dict)


class DriftDetector:
    """Detects drift in cognitive systems.

    Monitors for:
    - Belief drift: predictions diverging from reality
    - Knowledge drift: understanding changing unexpectedly
    - Strategy drift: strategy performance patterns changing
    - Confidence inflation: confidence rising without accuracy
    """

    def __init__(self, thresholds: dict[DriftType, float] | None = None) -> None:
        self._history: dict[str, list[float]] = {}
        self._events: list[DriftEvent] = []
        self._thresholds = thresholds or {
            DriftType.BELIEF_DRIFT: 0.1,
            DriftType.KNOWLEDGE_DRIFT: 0.15,
            DriftType.STRATEGY_DRIFT: 0.2,
            DriftType.CONFIDENCE_INFLATION: 0.25,
        }

    def check_drift(
        self,
        entity_id: str,
        metric: float,
        drift_type: DriftType,
    ) -> DriftEvent | None:
        """Check if metric indicates drift."""
        history = self._history.setdefault(entity_id, [])
        history.append(metric)

        if len(history) < 10:
            return None

        baseline = sum(history[:10]) / 10
        current = sum(history[-10:]) / 10
        magnitude = abs(current - baseline)

        threshold = self._thresholds.get(drift_type, 0.1)
        if magnitude > threshold:
            event = DriftEvent(
                drift_type=drift_type,
                entity_id=entity_id,
                before_value=baseline,
                after_value=current,
                magnitude=magnitude,
                details={"history_length": len(history)},
            )
            self._events.append(event)
            return event

        return None

    def get_events(self, limit: int = 100) -> list[DriftEvent]:
        """Get drift events."""
        return self._events[-limit:]

    def get_events_by_type(self, drift_type: DriftType) -> list[DriftEvent]:
        """Get events by drift type."""
        return [e for e in self._events if e.drift_type == drift_type]
