"""Adversary Agent — simulates manipulative trading behavior.

Models predatory market behavior for robustness testing.
Part of adversarial modeling (TIS Section 4).
"""

from __future__ import annotations

import random
from dataclasses import dataclass
from enum import StrEnum

from simulation.multi_agent_market import MarketState, SimFill, SimOrder


class AdversaryBehavior(StrEnum):
    """Types of adversarial behavior simulated."""

    PUMP_AND_DUMP = "PUMP_AND_DUMP"
    STOP_HUNT = "STOP_HUNT"
    LAYERING = "LAYERING"
    ICEBERG_PULL = "ICEBERG_PULL"


@dataclass(frozen=True, slots=True)
class AdversaryAction:
    """Action to take in market."""

    orders: tuple[SimOrder, ...]
    target_price: float | None = None
    trigger_condition: str = ""


class AdversaryAgent:
    """Simulates adversarial trader behavior for testing.

    Injects manipulative patterns into simulations:
    - Pump & dump at technical levels
    - Stop hunting around round numbers
    - Layering to create false depth
    - Iceberg pulling to trap other traders
    """

    def __init__(
        self,
        agent_id: str,
        behavior: AdversaryBehavior = AdversaryBehavior.PUMP_AND_DUMP,
        *,
        seed: int | None = None,
    ) -> None:
        self.agent_id = agent_id
        self.agent_type = "ADVERSARY"
        self.behavior = behavior
        self._rng = random.Random(seed if seed else hash(agent_id) % 2147483647)
        self._position: float = 0.0
        self._phase: int = 0

    def decide(self, state: MarketState) -> list[SimOrder]:
        """Generate adversarial orders based on behavior type."""
        if self.behavior == AdversaryBehavior.PUMP_AND_DUMP:
            return self._pump_and_dump_strategy(state)
        elif self.behavior == AdversaryBehavior.STOP_HUNT:
            return self._stop_hunt_strategy(state)
        elif self.behavior == AdversaryBehavior.LAYERING:
            return self._layering_strategy(state)
        else:
            return self._iceberg_strategy(state)

    def _pump_and_dump_strategy(self, state: MarketState) -> list[SimOrder]:
        """Buy aggressively, then sell into retail buying."""
        if self._phase == 0:
            # Accumulate at lower prices
            self._phase = 1
            return [SimOrder(self.agent_id, "BUY", state.best_ask, 50.0, "MARKET", state.tick)]
        elif self._phase == 1:
            # Mark up price
            self._phase = 2
            return [
                SimOrder(self.agent_id, "BUY", state.best_ask, 20.0, "MARKET", state.tick),
                SimOrder(self.agent_id, "SELL", state.best_bid, 10.0, "LIMIT", state.tick),
            ]
        else:
            # Dump into retail
            return [SimOrder(self.agent_id, "SELL", state.best_bid, 70.0, "MARKET", state.tick)]

    def _stop_hunt_strategy(self, state: MarketState) -> list[SimOrder]:
        """Hunt stops around psychological levels."""
        target = self._find_round_number_target(state.mid_price)
        side = "SELL" if state.mid_price > target else "BUY"
        size = 100.0 if abs(state.mid_price - target) / target > 0.01 else 25.0
        return [SimOrder(self.agent_id, side, state.best_ask, size, "MARKET", state.tick)]

    def _layering_strategy(self, state: MarketState) -> list[SimOrder]:
        """Place many small orders on one side then reverse."""
        orders = []
        for i in range(5):
            price = state.best_ask * (1 + i * 0.001)
            orders.append(SimOrder(self.agent_id, "BUY", price, 10.0, "LIMIT", state.tick))
        return orders

    def _iceberg_strategy(self, state: MarketState) -> list[SimOrder]:
        """Hide large order behind small displays."""
        return [SimOrder(self.agent_id, "BUY", state.best_ask, 10.0, "LIMIT", state.tick)]

    def _find_round_number_target(self, price: float) -> float:
        """Find nearest round number psychological level."""
        for level in [1000, 5000, 10000, 50000, 100000, 500000]:
            if price < level:
                return float(level)
        return price * 0.95  # Fall back

    def on_fill(self, fill: SimFill) -> None:
        """Record fill and update position."""
        # Position tracking omitted for simplicity


__all__ = [
    "AdversaryAgent",
    "AdversaryAction",
    "AdversaryBehavior",
]
