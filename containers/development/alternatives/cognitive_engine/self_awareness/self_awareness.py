"""Self-Awareness — system knows its own boundaries.

Not consciousness. Architecture.

DIXVISION should know:
  What I know.
  What I don't know.
  What I can do.
  What I cannot do.
  What I should improve next.
"""

from __future__ import annotations

import threading
import time as _time
from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class CompetencyProfile:
    capability_id: str
    name: str
    proficiency: float
    usage_count: int


class SelfAwarenessEngine:
    """Formal self-model tracking known capabilities, limitations, and gaps."""

    def __init__(self) -> None:
        self._lock = threading.Lock()
        self._capabilities: dict[str, CompetencyProfile] = {}
        self._limitations: dict[str, dict] = {}
        self._knowledge_gaps: dict[str, dict] = {}
        self._recommendations: list[dict] = []

    @staticmethod
    def _now_ns() -> int:
        try:
            from system.time_source import wall_ns

            return wall_ns()
        except Exception:
            return int(_time.time() * 1e9)

    def register_capability(
        self,
        capability_id: str,
        name: str,
        proficiency: float = 0.5,
    ) -> None:
        prof = CompetencyProfile(
            capability_id=capability_id,
            name=name,
            proficiency=max(0.0, min(1.0, proficiency)),
            usage_count=0,
        )
        with self._lock:
            self._capabilities[capability_id] = prof

    def register_limitation(
        self,
        limitation_id: str,
        description: str,
        severity: str = "MEDIUM",
    ) -> None:
        with self._lock:
            self._limitations[limitation_id] = {
                "limitation_id": limitation_id,
                "description": description,
                "severity": severity,
                "ts_ns": self._now_ns(),
            }

    def raise_gap(
        self,
        gap_id: str,
        description: str,
        impact: str = "MEDIUM",
    ) -> None:
        with self._lock:
            self._knowledge_gaps[gap_id] = {
                "gap_id": gap_id,
                "description": description,
                "impact": impact,
                "ts_ns": self._now_ns(),
            }
        self._auto_recommend(gap_id, description)

    def _auto_recommend(self, gap_id: str, description: str) -> None:
        rec = {
            "recommendation_id": f"REC-{self._now_ns():x}",
            "gap_id": gap_id,
            "description": f"Address gap: {description}",
            "priority": "HIGH",
            "ts_ns": self._now_ns(),
        }
        with self._lock:
            self._recommendations.append(rec)

    def report(self) -> dict:
        with self._lock:
            return {
                "known_capabilities": tuple(self._capabilities.keys()),
                "known_limitations": tuple(self._limitations.keys()),
                "knowledge_gaps": tuple(self._knowledge_gaps.keys()),
                "recommended_improvements": tuple(r["description"] for r in self._recommendations),
                "confidence_in_self_model": self._self_model_confidence(),
                "capability_count": len(self._capabilities),
                "limitation_count": len(self._limitations),
                "gap_count": len(self._knowledge_gaps),
                "ts_ns": self._now_ns(),
            }

    def _self_model_confidence(self) -> float:
        caps = len(self._capabilities)
        lims = len(self._limitations)
        gaps = len(self._knowledge_gaps)
        total = caps + lims + gaps
        if total == 0:
            return 0.0
        coverage = min(1.0, total / 50.0)
        return round(coverage, 2)


_instance: SelfAwarenessEngine | None = None
_lock = threading.Lock()


def get_self_awareness() -> SelfAwarenessEngine:
    global _instance
    if _instance is None:
        with _lock:
            if _instance is None:
                _instance = SelfAwarenessEngine()
    return _instance


__all__ = [
    "CompetencyProfile",
    "SelfAwarenessEngine",
    "get_self_awareness",
]
