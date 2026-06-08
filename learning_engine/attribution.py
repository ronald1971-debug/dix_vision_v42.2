"""Outcome Attribution – traces trade outcomes back to beliefs and hypotheses.

Determines which cognitive decisions led to profits or losses.
"""

from __future__ import annotations

import time
import uuid
from dataclasses import dataclass, field

from core.types import TradeResult


@dataclass
class Attribution:
    attribution_id: str = field(default_factory=lambda: uuid.uuid4().hex[:12])
    trade_id: str = ""
    hypothesis_id: str = ""
    belief_ids: list[str] = field(default_factory=list)
    pnl: float = 0.0
    attribution_factors: dict[str, float] = field(default_factory=dict)
    timestamp: float = field(default_factory=time.time)


class AttributionEngine:
    """Attributes trade outcomes to cognitive origins."""

    def __init__(self) -> None:
        self._attributions: list[Attribution] = []
        self._hypothesis_pnl: dict[str, float] = {}
        self._belief_pnl: dict[str, float] = {}

    def attribute(
        self,
        trade: TradeResult,
        hypothesis_id: str,
        belief_ids: list[str],
        entry_price: float = 0.0,
    ) -> Attribution:
        if entry_price > 0 and trade.fill_price > 0:
            if trade.direction == "long":
                pnl = (trade.fill_price - entry_price) * trade.fill_quantity - trade.fees
            else:
                pnl = (entry_price - trade.fill_price) * trade.fill_quantity - trade.fees
        else:
            pnl = 0.0

        factors: dict[str, float] = {}
        if belief_ids:
            per_belief = pnl / len(belief_ids) if belief_ids else 0.0
            for bid in belief_ids:
                factors[bid] = per_belief
                self._belief_pnl[bid] = self._belief_pnl.get(bid, 0.0) + per_belief

        self._hypothesis_pnl[hypothesis_id] = (
            self._hypothesis_pnl.get(hypothesis_id, 0.0) + pnl
        )

        attr = Attribution(
            trade_id=trade.trade_id,
            hypothesis_id=hypothesis_id,
            belief_ids=belief_ids,
            pnl=pnl,
            attribution_factors=factors,
        )
        self._attributions.append(attr)
        return attr

    def get_hypothesis_pnl(self, hypothesis_id: str) -> float:
        return self._hypothesis_pnl.get(hypothesis_id, 0.0)

    def get_belief_pnl(self, belief_id: str) -> float:
        return self._belief_pnl.get(belief_id, 0.0)

    def get_total_pnl(self) -> float:
        return sum(a.pnl for a in self._attributions)

    def get_attributions(self) -> list[Attribution]:
        return list(self._attributions)
