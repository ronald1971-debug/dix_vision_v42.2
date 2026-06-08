from __future__ import annotations

from dataclasses import dataclass, field

from core.ontology.base import CognitiveObject, ObjectKind


@dataclass(frozen=True, slots=True)
class Evidence(CognitiveObject):
    evidence_type: str = "observation"
    description: str = ""
    source: str = ""
    weight: float = 1.0
    content: dict = field(default_factory=dict)
    supports: tuple[str, ...] = ()
    contradicts: tuple[str, ...] = ()
    reliability: float = 1.0

    @classmethod
    def create(cls, *, object_id: str, ts_ns: int, **kwargs):
        return cls(
            object_id=object_id,
            object_type=ObjectKind.EVIDENCE,
            ts_ns=ts_ns,
            **kwargs,
        )

    def is_supporting(self, belief_id: str) -> bool:
        return belief_id in self.supports

    def is_contradicting(self, belief_id: str) -> bool:
        return belief_id in self.contradicts
