"""Observability Layer – Phase 10.

Real-time cognition visualization: operator sees cognition live.
  - Indira beliefs & hypotheses
  - DYON dependency graph
  - Governance approvals
  - Learning updates
  - Evolution proposals
"""

from __future__ import annotations

import time
from dataclasses import dataclass, field
from typing import Any


@dataclass
class CognitionSnapshot:
    """Point-in-time snapshot of the cognitive system state."""
    timestamp: float = field(default_factory=time.time)
    beliefs: list[dict[str, Any]] = field(default_factory=list)
    hypotheses: list[dict[str, Any]] = field(default_factory=list)
    active_intents: list[dict[str, Any]] = field(default_factory=list)
    governance_decisions: list[dict[str, Any]] = field(default_factory=list)
    learning_signals: list[dict[str, Any]] = field(default_factory=list)
    evolution_proposals: list[dict[str, Any]] = field(default_factory=list)
    system_health: dict[str, Any] = field(default_factory=dict)
    hazards: list[dict[str, Any]] = field(default_factory=list)


class ObservabilityHub:
    """Central hub for real-time system observation."""

    def __init__(self) -> None:
        self._snapshots: list[CognitionSnapshot] = []
        self._max_snapshots = 1000
        self._subscribers: list[Any] = []

    def capture_snapshot(self, snapshot: CognitionSnapshot) -> None:
        self._snapshots.append(snapshot)
        if len(self._snapshots) > self._max_snapshots:
            self._snapshots = self._snapshots[-self._max_snapshots:]
        self._notify_subscribers(snapshot)

    def get_latest(self) -> CognitionSnapshot | None:
        return self._snapshots[-1] if self._snapshots else None

    def get_history(self, count: int = 100) -> list[CognitionSnapshot]:
        return self._snapshots[-count:]

    def subscribe(self, callback: Any) -> None:
        self._subscribers.append(callback)

    def _notify_subscribers(self, snapshot: CognitionSnapshot) -> None:
        for sub in self._subscribers:
            try:
                sub(snapshot)
            except Exception:
                pass

    def build_snapshot(
        self,
        beliefs: list[dict[str, Any]] | None = None,
        hypotheses: list[dict[str, Any]] | None = None,
        governance_decisions: list[dict[str, Any]] | None = None,
        learning_signals: list[dict[str, Any]] | None = None,
        evolution_proposals: list[dict[str, Any]] | None = None,
        system_health: dict[str, Any] | None = None,
        hazards: list[dict[str, Any]] | None = None,
    ) -> CognitionSnapshot:
        snapshot = CognitionSnapshot(
            beliefs=beliefs or [],
            hypotheses=hypotheses or [],
            governance_decisions=governance_decisions or [],
            learning_signals=learning_signals or [],
            evolution_proposals=evolution_proposals or [],
            system_health=system_health or {},
            hazards=hazards or [],
        )
        self.capture_snapshot(snapshot)
        return snapshot
