"""Cognitive Audit Trail bridge.

Captures cognitive state transitions so they can be replayed or inspected.

Integrates with:
  cognitive_engine.epistemology_engine EpistemologyEngine
  core.ontology.audit_trail CognitiveAuditTrail
  core.ontology.belief CognitiveBelief
  core.ontology.knowledge Knowledge
"""

from __future__ import annotations

from dataclasses import dataclass

from core.ontology.belief import CognitiveBelief
from core.ontology.knowledge import Knowledge


@dataclass(frozen=True, slots=True)
class CognitiveCapture:
    trail_id: str = ""
    captured_by: str = ""
    ts_ns: int = 0
    belief_snapshot_count: int = 0
    knowledge_snapshot_count: int = 0


class CognitiveAuditRecorder:
    """Record and restore cognitive-state snapshots."""

    def __init__(self) -> None:
        self._captures: dict[str, CognitiveCapture] = {}

    def capture(
        self,
        trail_id: str,
        beliefs: tuple[CognitiveBelief, ...],
        knowledge: tuple[Knowledge, ...],
        ts_ns: int,
    ) -> CognitiveCapture:
        capture = CognitiveCapture(
            trail_id=trail_id,
            captured_by="CognitiveAuditRecorder",
            ts_ns=ts_ns,
            belief_snapshot_count=len(beliefs),
            knowledge_snapshot_count=len(knowledge),
        )
        self._captures[trail_id] = capture
        return capture

    def restore(self, trail_id: str) -> CognitiveCapture | None:
        return self._captures.get(trail_id)


__all__ = ["CognitiveAuditRecorder", "CognitiveCapture"]
