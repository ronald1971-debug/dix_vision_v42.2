from __future__ import annotations

from dataclasses import dataclass, field

from core.ontology.base import CognitiveObject, ObjectKind


@dataclass(frozen=True, slots=True)
class Portfolio(CognitiveObject):
    total_value_usd: float = 0.0
    free_capital: float = 0.0
    allocated_capital: float = 0.0
    exposure_by_symbol: dict = field(default_factory=dict)
    correlation_risk: float = 0.0
    max_single_position_pct: float = 0.0
    current_utilization: float = 0.0
    open_positions: tuple[str, ...] = ()

    @classmethod
    def create(cls, *, object_id: str, ts_ns: int, **kwargs):
        return cls(
            object_id=object_id,
            object_type=ObjectKind.PORTFOLIO,
            ts_ns=ts_ns,
            **kwargs,
        )

    def utilization(self) -> float:
        if self.total_value_usd == 0:
            return 0.0
        return self.allocated_capital / self.total_value_usd
