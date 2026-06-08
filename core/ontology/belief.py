from __future__ import annotations

from dataclasses import dataclass

from core.ontology.base import CognitiveObject, ObjectKind


@dataclass(frozen=True, slots=True)
class CognitiveBelief(CognitiveObject):
    domain: str = "unknown"
    claim: str = ""
    confidence: float = 0.0
    uncertainty: float = 0.5
    consensus_weight: float = 1.0
    revision_count: int = 0

    @classmethod
    def create(cls, *, object_id: str, ts_ns: int, domain: str = "unknown", claim: str = "", **kwargs):
        return cls(
            object_id=object_id,
            object_type=ObjectKind.BELIEF,
            ts_ns=ts_ns,
            domain=domain,
            claim=claim,
            **kwargs,
        )

    def is_confident(self, threshold: float = 0.7) -> bool:
        return self.confidence >= threshold

    def is_certain(self, threshold: float = 0.2) -> bool:
        return self.uncertainty <= threshold
