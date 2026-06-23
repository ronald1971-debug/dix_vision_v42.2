from __future__ import annotations

from dataclasses import dataclass

from core.ontology.base import CognitiveObject


@dataclass(frozen=True, slots=True)
class BeliefTransition:
    belief_id: str
    previous_confidence: float
    new_confidence: float
    previous_claim: str = ""
    new_claim: str = ""
    triggering_evidence_ids: tuple[str, ...] = ()
    contributing_engines: tuple[str, ...] = ()
    reason: str = ""
    revision_count: int = 0

    @property
    def confidence_delta(self) -> float:
        return self.new_confidence - self.previous_confidence

    def is_large_shift(self, threshold: float = 0.4) -> bool:
        return abs(self.confidence_delta) >= threshold


@dataclass(frozen=True, slots=True)
class AuditTrail(CognitiveObject):
    audit_id: str = ""
    audit_type: str = "generic"
    event_description: str = ""
    actor: str = ""
    outcome: str = ""

    def succeeded(self) -> bool:
        return self.outcome.lower() in ("success", "approved", "completed")

    def failed(self) -> bool:
        return self.outcome.lower() in ("failure", "rejected", "blocked")


@dataclass(frozen=True, slots=True)
class CognitiveAuditTrail(CognitiveObject):
    transitions: tuple = ()
    decision_id: str = ""
    hypothesis: str = ""
    test_result: str = ""
    meta_notes: tuple[str, ...] = ()

    def has_large_shifts(self, threshold: float = 0.4) -> bool:
        return any(t.is_large_shift for t in self.transitions if isinstance(t, BeliefTransition))

    def involves_belief(self, belief_id: str) -> bool:
        return any(
            t.belief_id == belief_id for t in self.transitions if isinstance(t, BeliefTransition)
        )


__all__ = [
    "AuditTrail",
    "BeliefTransition",
    "CognitiveAuditTrail",
]
