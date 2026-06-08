from __future__ import annotations

from dataclasses import dataclass

from core.ontology.base import CognitiveObject, ObjectKind


@dataclass(frozen=True, slots=True)
class Market(CognitiveObject):
    symbol: str = ""
    market_structure: dict | None = None
    regime: str = "unknown"
    regime_confidence: float = 0.0
    volatility: float = 0.0
    liquidity_score: float = 0.0
    last_tick_ts_ns: int = 0

    @classmethod
    def create(cls, *, object_id: str, ts_ns: int, symbol: str, **kwargs):
        return cls(
            object_id=object_id,
            object_type=ObjectKind.MARKET,
            ts_ns=ts_ns,
            symbol=symbol,
            **kwargs,
        )

    def is_confident(self, threshold: float = 0.7) -> bool:
        return self.regime_confidence >= threshold
