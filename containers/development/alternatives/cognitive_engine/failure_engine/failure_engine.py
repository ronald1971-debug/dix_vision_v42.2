"""Failure Intelligence — failures studied as assets.

Most systems log failures. Few study them.

Tracks:
  - Strategy Failures
  - Prediction Failures
  - Trader Model Failures
  - Governance Failures
  - Execution Failures

Failures become assets.
"""

from __future__ import annotations

import threading
import time as _time
from collections import Counter, defaultdict
from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class FailureRecord:
    """A single failure."""
    ts_ns: int
    failure_id: str
    category: str
    strategy_id: str
    prediction_id: str
    root_cause: str
    severity: str = "INFO"
    resolved: bool = False
    repeat_count: int = 0


class FailureTracker:
    """Tracks and analyzes failures so they become assets."""

    def __init__(self) -> None:
        self._lock = threading.Lock()
        self._records: dict[str, FailureRecord] = {}
        self._by_category: dict[str, list[str]] = defaultdict(list)
        self._by_root_cause: dict[str, list[str]] = defaultdict(list)
        self._repeat_counts: dict[str, int] = defaultdict(int)
        self._resolved: list[str] = []

    def classify(
        self,
        failure_id: str,
        category: str,
        strategy_id: str,
        prediction_id: str,
        root_cause: str,
        severity: str = "INFO",
    ) -> FailureRecord:
        rec = FailureRecord(
            ts_ns=_now_ns(),
            failure_id=failure_id,
            category=category,
            strategy_id=strategy_id,
            prediction_id=prediction_id,
            root_cause=root_cause,
            severity=severity,
        )
        with self._lock:
            self._records[failure_id] = rec
            self._by_category[category].append(failure_id)
            self._by_root_cause[root_cause].append(failure_id)
        return rec

    def mark_resolved(self, failure_id: str) -> bool:
        with self._lock:
            if failure_id in self._records:
                rec = self._records[failure_id]
                self._records[failure_id] = FailureRecord(
                    ts_ns=rec.ts_ns,
                    failure_id=rec.failure_id,
                    category=rec.category,
                    strategy_id=rec.strategy_id,
                    prediction_id=rec.prediction_id,
                    root_cause=rec.root_cause,
                    severity=rec.severity,
                    resolved=True,
                    repeat_count=rec.repeat_count,
                )
                if failure_id not in self._resolved:
                    self._resolved.append(failure_id)
                return True
        return False

    def mark_repeat(self, failure_id: str) -> int:
        with self._lock:
            if failure_id in self._records:
                rec = self._records[failure_id]
                new_count = rec.repeat_count + 1
                self._records[failure_id] = FailureRecord(
                    ts_ns=rec.ts_ns,
                    failure_id=rec.failure_id,
                    category=rec.category,
                    strategy_id=rec.strategy_id,
                    prediction_id=rec.prediction_id,
                    root_cause=rec.root_cause,
                    severity=rec.severity,
                    resolved=rec.resolved,
                    repeat_count=new_count,
                )
                return new_count
        return 0

    def pattern_report(self) -> dict:
        with self._lock:
            cat_counts = {k: len(v) for k, v in self._by_category.items()}
            root_counts = Counter(self._by_root_cause)
            return {
                "total_failures": len(self._records),
                "resolved": len(self._resolved),
                "by_category": cat_counts,
                "repeat_root_causes": dict(root_counts.most_common(10)),
                "ts_ns": _now_ns(),
            }

    def get_record(self, failure_id: str) -> dict | None:
        with self._lock:
            rec = self._records.get(failure_id)
            if rec is None:
                return None
            return {
                "failure_id": rec.failure_id,
                "category": rec.category,
                "strategy_id": rec.strategy_id,
                "prediction_id": rec.prediction_id,
                "root_cause": rec.root_cause,
                "severity": rec.severity,
                "resolved": rec.resolved,
                "repeat_count": rec.repeat_count,
            }


def _now_ns() -> int:
    try:
        from system.time_source import wall_ns
        return wall_ns()
    except Exception:
        return int(_time.time() * 1e9)


class FailureEngine:
    """Top-level failure intelligence coordinator."""

    def __init__(self) -> None:
        self._tracker = FailureTracker()
        self._lock = threading.Lock()

    def classify(self, *args, **kwargs) -> FailureRecord:
        return self._tracker.classify(*args, **kwargs)

    def mark_resolved(self, failure_id: str) -> bool:
        return self._tracker.mark_resolved(failure_id)

    def mark_repeat(self, failure_id: str) -> int:
        return self._tracker.mark_repeat(failure_id)

    def pattern_report(self) -> dict:
        return self._tracker.pattern_report()

    def get_record(self, failure_id: str) -> dict | None:
        return self._tracker.get_record(failure_id)


_instance: FailureEngine | None = None
_lock = threading.Lock()


def get_failure_engine() -> FailureEngine:
    global _instance
    if _instance is None:
        with _lock:
            if _instance is None:
                _instance = FailureEngine()
    return _instance


__all__ = [
    "FailureRecord",
    "FailureTracker",
    "FailureEngine",
    "get_failure_engine",
]
