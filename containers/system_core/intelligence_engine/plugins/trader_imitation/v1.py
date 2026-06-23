"""IND-L12 trader imitation plugin v1 — Indira learning layer #11.

Trader behavior analysis and pattern recognition.

Pure (INV-15 / TEST-01): no clock, no PRNG, no IO.
"""

from __future__ import annotations

from collections import deque
from dataclasses import dataclass, field

from core.contracts.engine import (
    HealthState,
    HealthStatus,
    MicrostructurePlugin,
    PluginLifecycle,
)
from core.contracts.events import Side, SignalEvent
from core.contracts.market import MarketTick


@dataclass(slots=True)
class TraderImitationV1(MicrostructurePlugin):
    """Eleventh concrete intelligence plugin (IND-L12 v1)."""

    name: str = "trader_imitation_v1"
    version: str = "0.1.0"
    lifecycle: PluginLifecycle = PluginLifecycle.ACTIVE
    window_size: int = 5
    pattern_threshold: float = 0.6
    confidence_scale: float = 0.2
    min_confidence: float = 0.05
    _pattern_window: deque[Side] = field(init=False, repr=False)

    def __post_init__(self) -> None:
        if self.window_size < 2:
            raise ValueError("window_size must be >= 2")
        if not 0.0 < self.pattern_threshold <= 1.0:
            raise ValueError("pattern_threshold must be in (0, 1]")
        if self.confidence_scale <= 0.0:
            raise ValueError("confidence_scale must be > 0")
        if not 0.0 <= self.min_confidence <= 1.0:
            raise ValueError("min_confidence must be in [0, 1]")
        self._pattern_window = deque(maxlen=self.window_size)

    def on_tick(self, tick: MarketTick) -> tuple[SignalEvent, ...]:
        if tick.bid <= 0.0 or tick.ask <= 0.0 or tick.last <= 0.0:
            return ()
        if tick.ask < tick.bid:
            return ()

        mid = 0.5 * (tick.bid + tick.ask)
        if mid <= 0.0:
            return ()

        # Determine trader action based on tick position
        if tick.last > mid:
            side = Side.BUY
        elif tick.last < mid:
            side = Side.SELL
        else:
            side = Side.HOLD

        if side == Side.HOLD:
            return ()

        self._pattern_window.append(side)

        if len(self._pattern_window) < self.window_size:
            return ()

        # Analyze pattern for consistency
        buy_count = sum(1 for s in self._pattern_window if s == Side.BUY)
        sell_count = sum(1 for s in self._pattern_window if s == Side.SELL)
        pattern_strength = max(buy_count, sell_count) / len(self._pattern_window)

        if pattern_strength < self.pattern_threshold:
            return ()

        predicted_side = Side.BUY if buy_count > sell_count else Side.SELL

        confidence = min(1.0, pattern_strength / self.confidence_scale)
        if confidence < self.min_confidence:
            return ()

        return (
            SignalEvent(
                ts_ns=tick.ts_ns,
                symbol=tick.symbol,
                side=predicted_side,
                confidence=confidence,
                plugin_chain=(self.name,),
                meta={
                    "pattern_strength": f"{pattern_strength:.4f}",
                    "pattern_threshold": f"{self.pattern_threshold:.4f}",
                    "buy_count": f"{buy_count}",
                    "sell_count": f"{sell_count}",
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
                f"window={self.window_size} "
                f"pattern_thresh={self.pattern_threshold}"
            ),
        )


__all__ = ["TraderImitationV1"]
