"""Failure Tracker — tracks classification, repeat counts, root causes, and statistics."""

from __future__ import annotations

import threading
from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True, slots=True)
class FailureRecord:
    """A single failure event."""
    failure_id: str
    classification: str
    repeat_count: int
    root_cause: str
    ts_ns: int


class FailureTracker:
    """Tracks failures with classification, repetition, and root cause analysis."""

    def __init__(self) -> None:
        self._lock = threading.Lock()
        self._failures: dict[str, FailureRecord] = {}
        self._stats: dict[str, int] = {}

    def record(self, failure_id: str, classification: str, root_cause: str, ts_ns: int) -> FailureRecord:
        """Record a failure and update repeat count and stats."""
        with self._lock:
            existing = self._failures.get(failure_id)
            repeat_count = existing.repeat_count + 1 if existing else 1
            record = FailureRecord(
                failure_id=failure_id,
                classification=classification,
                repeat_count=repeat_count,
                root_cause=root_cause,
                ts_ns=ts_ns,
            )
            self._failures[failure_id] = record
            self._stats[classification] = self._stats.get(classification, 0) + 1
            return record

    def get_failure(self, failure_id: str) -> dict[str, Any] | None:
        """Get a failure record by ID."""
        with self._lock:
            record = self._failures.get(failure_id)
            if record is None:
                return None
            return {
                "failure_id": record.failure_id,
                "classification": record.classification,
                "repeat_count": record.repeat_count,
                "root_cause": record.root_cause,
                "ts_ns": record.ts_ns,
            }

    def get_stats(self) -> dict[str, Any]:
        """Get failure statistics."""
        with self._lock:
            return {
                "total_failures": len(self._failures),
                "classifications": dict(self._stats),
                "ts_ns": 0,
            }


_instance: FailureTracker | None = None
_singleton_lock = threading.Lock()


def get_failure_tracker() -> FailureTracker:
    global _instance
    if _instance is None:
        with _singleton_lock:
            if _instance is None:
                _instance = FailureTracker()
    return _instance