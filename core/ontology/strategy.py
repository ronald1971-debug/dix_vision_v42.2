from __future__ import annotations

from dataclasses import dataclass, field

from core.ontology.base import CognitiveObject, ObjectKind


@dataclass(frozen=True, slots=True)
class Strategy(CognitiveObject):
    strategy_id: str = ""
    name: str = ""
    family: str = ""
    description: str = ""
    lifecycle: str = "DRAFT"
    parameters: dict = field(default_factory=dict)
    composed_from: tuple[str, ...] = ()
    mutable_parameters: tuple[str, ...] = ()
    parameter_bounds: dict = field(default_factory=dict)
    sharpe_ratio: float | None = None
    max_drawdown: float | None = None
    total_pnl: float = 0.0
    regime_fitness: dict = field(default_factory=dict)

    @classmethod
    def create(cls, *, object_id: str, ts_ns: int, strategy_id: str, lifecycle: str = 'DRAFT', **kwargs):
        return cls(
            object_id=object_id,
            object_type=ObjectKind.STRATEGY,
            ts_ns=ts_ns,
            strategy_id=strategy_id,
            lifecycle=lifecycle,
            **kwargs,
        )

    def is_approved(self) -> bool:
        return self.lifecycle == "APPROVED"

    def is_retired(self) -> bool:
        return self.lifecycle == "RETIRED"
