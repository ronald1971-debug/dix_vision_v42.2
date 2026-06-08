from __future__ import annotations

from dataclasses import dataclass, field

from core.ontology.base import CognitiveObject, ObjectKind


@dataclass(frozen=True, slots=True)
class Trader(CognitiveObject):
    trader_id: str = ""
    trader_type: str = "UNKNOWN"
    name: str = ""
    style_tags: tuple[str, ...] = ()
    performance: dict = field(default_factory=dict)
    regime_performance: dict = field(default_factory=dict)
    confidence: float = 0.0
    philosophy: dict = field(default_factory=dict)
    influence_score: float = 0.0
    active: bool = True

    @classmethod
    def create(cls, *, object_id: str, ts_ns: int, trader_id: str, trader_type: str = "UNKNOWN", **kwargs):
        return cls(
            object_id=object_id,
            object_type=ObjectKind.TRADER,
            ts_ns=ts_ns,
            trader_id=trader_id,
            trader_type=trader_type,
            **kwargs,
        )

    def is_scalper(self) -> bool:
        return self.trader_type == "SCALPER"

    def is_momentum(self) -> bool:
        return self.trader_type in {"MOMENTUM", "TREND"}
