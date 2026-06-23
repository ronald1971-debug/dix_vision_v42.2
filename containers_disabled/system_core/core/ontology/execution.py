from __future__ import annotations

from dataclasses import dataclass

from core.ontology.base import CognitiveObject, ObjectKind


@dataclass(frozen=True, slots=True)
class Execution(CognitiveObject):
    intent_id: str = ""
    symbol: str = ""
    side: str = "HOLD"
    order_type: str = "MARKET"
    quantity: float = 0.0
    price: float | None = None
    status: str = "PENDING"
    filled_quantity: float = 0.0
    filled_price: float | None = None
    slippage_bps: float = 0.0
    latency_ms: float = 0.0
    fee_usd: float = 0.0
    realized_pnl: float = 0.0
    adapter_id: str = ""
    governance_signature: str = ""

    @classmethod
    def create(cls, *, object_id: str, ts_ns: int, **kwargs):
        return cls(
            object_id=object_id,
            object_type=ObjectKind.EXECUTION,
            ts_ns=ts_ns,
            **kwargs,
        )

    def is_filled(self) -> bool:
        return self.status == "FILLED"

    def is_rejected(self) -> bool:
        return self.status == "REJECTED"
