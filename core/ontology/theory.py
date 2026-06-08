from __future__ import annotations

from dataclasses import dataclass

from core.ontology.base import CognitiveObject, ObjectKind


@dataclass(frozen=True, slots=True)
class Theory(CognitiveObject):
    theory_name: str = ""
    description: str = ""
    domain: str = "unknown"
    testable_hypotheses: tuple[str, ...] = ()
    implementing_strategies: tuple[str, ...] = ()
    empirical_support: float = 0.0
    falsification_attempts: int = 0
    falsified: bool = False
    confidence: float = 0.0

    @classmethod
    def create(cls, *, object_id: str, ts_ns: int, **kwargs):
        return cls(
            object_id=object_id,
            object_type=ObjectKind.THEORY,
            ts_ns=ts_ns,
            **kwargs,
        )

    def is_falsifiable(self) -> bool:
        return len(self.testable_hypotheses) > 0

    def is_supported(self, threshold: float = 0.6) -> bool:
        return not self.falsified and self.empirical_support >= threshold

    def has_implementation(self) -> bool:
        return len(self.implementing_strategies) > 0
