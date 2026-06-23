"""IND-L10 news reaction plugin v1 — Indira learning layer #9.

Market reaction analysis to news events.

Pure (INV-15 / TEST-01): no clock, no PRNG, no IO.
"""

from __future__ import annotations

from dataclasses import dataclass

from core.contracts.engine import (
    HealthState,
    HealthStatus,
    MicrostructurePlugin,
    PluginLifecycle,
)
from core.contracts.events import Side, SignalEvent
from core.contracts.market import MarketTick


@dataclass(slots=True)
class NewsReactionV1(MicrostructurePlugin):
    """Ninth concrete intelligence plugin (IND-L10 v1)."""

    name: str = "news_reaction_v1"
    version: str = "0.1.0"
    lifecycle: PluginLifecycle = PluginLifecycle.ACTIVE
    reaction_threshold: float = 0.002
    confidence_scale: float = 0.01
    min_confidence: float = 0.05

    def __post_init__(self) -> None:
        if self.reaction_threshold < 0.0:
            raise ValueError("reaction_threshold must be >= 0")
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

        # Calculate price change from previous tick (simplified)
        # In production, this would integrate with actual news feed
        price_change = abs(tick.last - mid) / mid

        if price_change > self.reaction_threshold:
            side = Side.BUY if tick.last > mid else Side.SELL
        else:
            return ()

        confidence = min(1.0, price_change / self.confidence_scale)
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
                    "price_change": f"{price_change:.6f}",
                    "reaction_threshold": f"{self.reaction_threshold:.6f}",
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
                f"reaction_thresh={self.reaction_threshold}"
            ),
        )


__all__ = ["NewsReactionV1"]
