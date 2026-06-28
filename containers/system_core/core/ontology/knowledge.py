from __future__ import annotations

from dataclasses import dataclass, field

from core.ontology.base import CognitiveObject, ObjectKind


@dataclass(frozen=True, slots=True)
class Knowledge(CognitiveObject):
    knowledge_domain: str = "unknown"
    validated_claims: dict = field(default_factory=dict)
    confidence: float = 0.0
    validation_sources: int = 0
    last_validated_ts_ns: int = 0
    maturity: str = "nascent"
    contradiction_risk: float = 0.0

    @classmethod
    def create(cls, *, object_id: str, ts_ns: int, **kwargs):
        return cls(
            object_id=object_id,
            object_type=ObjectKind.KNOWLEDGE,
            ts_ns=ts_ns,
            **kwargs,
        )

    def is_validated(self) -> bool:
        return self.validation_sources >= 2

    def is_entrenched(self) -> bool:
        return self.maturity == "entrenched"
