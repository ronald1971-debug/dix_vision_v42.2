"""IND-L04 order book pressure plugin v1 — Indira learning layer #3.

Analyzes order book pressure and depth imbalances.

Pure (INV-15 / TEST-01): no clock, no PRNG, no IO.
"""

from __future__ import annotations

from dataclasses import dataclass

from core.contracts.engine import (
    HealthState,
    HealthStatus,
    PluginLifecycle,
    MicrostructurePlugin,
)
from core.contracts.events import Side, SignalEvent
from core.contracts.market import MarketTick


@dataclass(slots=True)
class OrderBookPressureV1(MicrostructurePlugin):
    """Third concrete intelligence plugin (IND-L04 v1)."""

    name: str = "order_book_pressure_v1"
    version: str = "0.1.0"
    lifecycle: PluginLifecycle = PluginLifecycle.ACTIVE
    spread_threshold: float = 0.001
    pressure_threshold: float = 0.5
    confidence_scale: float = 0.01
    min_confidence: float = 0.05

    def __post_init__(self) -> None:
        if self.spread_threshold < 0.0:
            raise ValueError("spread_threshold must be >= 0")
        if not 0.0 < self.pressure_threshold <= 1.0:
            raise ValueError("pressure_threshold must be in (0, 1]")
        if self.confidence_scale <= 0.0:
            raise ValueError("confidence_scale must be > 0")
        if not 0.0 <= self.min_confidence <= 1.0:
            raise ValueError("min_confidence must be in [0, 1]")

    def on_tick(self, tick: MarketTick) -> tuple[SignalEvent, ...]:
        if tick.bid <= 0.0 or tick.ask <= 0.0 or tick.last <= 0.0:
            return ()
        if tick.ask < tick.bid:
            return ()

        mid = 0.5 * (tick.bid + tick.ask)
        if mid <= 0.0:
            return ()

        spread = (tick.ask - tick.bid) / mid
        if spread > self.spread_threshold:
            return ()

        # Calculate pressure based on last position relative to spread
        position = (tick.last - tick.bid) / (tick.ask - tick.bid)
        
        if position > (0.5 + self.pressure_threshold / 2):
            side = Side.BUY
        elif position < (0.5 - self.pressure_threshold / 2):
            side = Side.SELL
        else:
            return ()

        confidence = min(1.0, abs(position - 0.5) / self.confidence_scale)
        if confidence < self.min_confidence:
            return ()

        return (
            SignalEvent(
                ts_ns=tick.ts_ns,
                symbol=tick.symbol,
                side=side,
                confidence=confidence,
                plugin_chain=(self.name,),
                meta={
                    "mid": f"{mid:.10f}",
                    "spread": f"{spread:.6f}",
                    "position": f"{position:.6f}",
                    "pressure_threshold": f"{self.pressure_threshold:.6f}",
                },
                produced_by_engine="intelligence_engine",
            ),
        )

    def check_self(self) -> HealthStatus:
        return HealthStatus(
            engine_name=self.name,
            state=HealthState.OK,
            detail=(
                f"{self.name} v{self.version} "
                f"lifecycle={self.lifecycle} "
                f"spread_thresh={self.spread_threshold}"
            ),
        )


__all__ = ["OrderBookPressureV1"]
