"""Recursive Governance — self-improvement safety.

Not: Can DYON improve DIXVISION?
But: How much improvement is safe?

This becomes a formal governance discipline.

(Item 39 — cognitive operating system roadmap)
"""

from __future__ import annotations

import threading
import time as _time
from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class ImprovementGate:
    proposal_id: str
    max_allowed_risk: float
    actual_risk: float
    approved: bool
    ts_ns: int


class RecursiveGovernance:
    """Governs how much self-improvement is safe."""

    def __init__(self) -> None:
        self._lock = threading.Lock()
        self._audit: list[ImprovementGate] = []

    def gate_improvement(self, proposal_id: str, max_allowed_risk: float,
                         actual_risk: float) -> ImprovementGate:
        approved = actual_risk <= max_allowed_risk
        gate = ImprovementGate(
            proposal_id=proposal_id,
            max_allowed_risk=max_allowed_risk,
            actual_risk=actual_risk,
            approved=approved,
            ts_ns=_now_ns(),
        )
        with self._lock:
            self._audit.append(gate)
        return gate

    def audit(self) -> dict:
        with self._lock:
            approved = sum(1 for g in self._audit if g.approved)
            rejected = len(self._audit) - approved
            return {
                "total_gates": len(self._audit),
                "approved": approved,
                "rejected": rejected,
                "ts_ns": _now_ns(),
            }


def _now_ns() -> int:
    try:
        from system.time_source import wall_ns
        return wall_ns()
    except Exception:
        return int(_time.time() * 1e9)


_instance: RecursiveGovernance | None = None
_lock = threading.Lock()


def get_recursive_governance() -> RecursiveGovernance:
    global _instance
    if _instance is None:
        with _lock:
            if _instance is None:
                _instance = RecursiveGovernance()
    return _instance


__all__ = [
    "ImprovementGate",
    "RecursiveGovernance",
    "get_recursive_governance",
]
