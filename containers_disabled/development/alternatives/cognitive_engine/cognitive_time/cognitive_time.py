"""Cognitive Time System.

Most systems only see: now

This module maintains:
  - past_beliefs (history of beliefs)
  - current_beliefs
  - projected_beliefs

(Cognitive Time — Item 30 from the roadmap)
"""

from __future__ import annotations

import threading
import time as _time
from collections import deque
from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class BeliefRecord:
    ts_ns: int
    belief_id: str
    domain: str
    claim: str
    confidence: float
    source: str


class CognitiveTime:
    """Track belief states across past, present, and future.
    Most systems only see "now." This one sees timeline.
    """

    def __init__(self) -> None:
        self._lock = threading.Lock()
        self._past: dict[str, deque] = {}
        self._current: dict[str, dict] = {}
        self._projected: dict[str, dict] = {}

    def record_belief(
        self, belief_id: str, domain: str, claim: str, confidence: float, source: str
    ) -> None:
        ts_ns = _now_ns()
        rec = BeliefRecord(
            ts_ns=ts_ns,
            belief_id=belief_id,
            domain=domain,
            claim=claim,
            confidence=confidence,
            source=source,
        )
        with self._lock:
            self._current[belief_id] = {
                "belief_id": belief_id,
                "domain": domain,
                "claim": claim,
                "confidence": confidence,
                "ts_ns": ts_ns,
            }
            if belief_id not in self._past:
                self._past[belief_id] = deque(maxlen=500)
            self._past[belief_id].append(rec)

    def project_belief(
        self, belief_id: str, future_claim: str, projected_confidence: float, horizon_ns: int
    ) -> dict:
        ts_ns = _now_ns()
        proj = {
            "belief_id": belief_id,
            "projected_claim": future_claim,
            "projected_confidence": projected_confidence,
            "horizon_ns": horizon_ns,
            "created_at_ns": ts_ns,
            "expires_at_ns": ts_ns + horizon_ns,
        }
        with self._lock:
            self._projected[belief_id] = proj
        return proj

    def get_history(self, belief_id: str) -> list[dict]:
        with self._lock:
            dq = self._past.get(belief_id, deque())
            return [
                {
                    "ts_ns": r.ts_ns,
                    "domain": r.domain,
                    "claim": r.claim,
                    "confidence": r.confidence,
                    "source": r.source,
                }
                for r in dq
            ]

    def current_beliefs(self) -> dict:
        with self._lock:
            return dict(self._current)

    def projected_beliefs(self) -> dict:
        with self._lock:
            return dict(self._projected)

    def timeline_report(self) -> dict:
        with self._lock:
            total_history = sum(len(dq) for dq in self._past.values())
            return {
                "total_belief_tracks": len(self._past),
                "total_history_entries": total_history,
                "current_beliefs": len(self._current),
                "projected_beliefs": len(self._projected),
                "ts_ns": _now_ns(),
            }


def _now_ns() -> int:
    try:
        from system.time_source import wall_ns

        return wall_ns()
    except Exception:
        return int(_time.time() * 1e9)


_instance: CognitiveTime | None = None
_lock = threading.Lock()


def get_cognitive_time() -> CognitiveTime:
    global _instance
    if _instance is None:
        with _lock:
            if _instance is None:
                _instance = CognitiveTime()
    return _instance


__all__ = [
    "BeliefRecord",
    "CognitiveTime",
    "get_cognitive_time",
]
