"""IND-L11 sentiment aggregator plugin v1 — Indira learning layer #10.

Aggregates multiple sentiment sources.

Pure (INV-15 / TEST-01): no clock, no PRNG, no IO.
"""

from __future__ import annotations

from collections import deque
from dataclasses import dataclass, field

from core.contracts.engine import (
    HealthState,
    HealthStatus,
    PluginLifecycle,
)
from core.contracts.engine import MicrostructurePlugin
from core.contracts.events import Side, SignalEvent
from core.contracts.market import MarketTick


@dataclass(slots=True)
class SentimentAggregatorV1(MicrostructurePlugin):
    """Tenth concrete intelligence plugin (IND-L11 v1)."""

    name: str = "sentiment_aggregator_v1"
    version: str = "0.1.0"
    lifecycle: PluginLifecycle = PluginLifecycle.ACTIVE
    window_size: int = 10
    sentiment_threshold: float = 0.3
    confidence_scale: float = 0.5
    min_confidence: float = 0.05
    _sentiment_window: deque[float] = field(init=False, repr=False)

    def __post_init__(self) -> None:
        if self.window_size < 2:
            raise ValueError("window_size must be >= 2")
        if not 0.0 < self.sentiment_threshold <= 1.0:
            raise ValueError("sentiment_threshold must be in (0, 1]")
        if self.confidence_scale <= 0.0:
            raise ValueError("confidence_scale must be > 0")
        if not 0.0 <= self.min_confidence <= 1.0:
            raise ValueError("min_confidence must be in [0, 1]")
        self._sentiment_window = deque(maxlen=self.window_size)

    def on_tick(self, tick: MarketTick) -> tuple[SignalEvent, ...]:
        if tick.bid <= 0.0 or tick.ask <= 0.0 or tick.last <= 0.0:
            return ()
        if tick.ask < tick.bid:
            return ()

        mid = 0.5 * (tick.bid + tick.ask)
        if mid <= 0.0:
            return ()

        # Use price position relative to mid as sentiment proxy
        position = (tick.last - mid) / mid
        sentiment = position  # Simple proxy for sentiment

        self._sentiment_window.append(sentiment)

        if len(self._sentiment_window) < self.window_size:
            return ()

        avg_sentiment = sum(self._sentiment_window) / len(self._sentiment_window)

        if avg_sentiment > self.sentiment_threshold:
            side = Side.BUY
        elif avg_sentiment < -self.sentiment_threshold:
            side = Side.SELL
        else:
            return ()

        confidence = min(1.0, abs(avg_sentiment) / self.confidence_scale)
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
                    "avg_sentiment": f"{avg_sentiment:.6f}",
                    "sentiment_threshold": f"{self.sentiment_threshold:.6f}",
                    "window_size": f"{self.window_size}",
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
                f"sentiment_thresh={self.sentiment_threshold}"
            ),
        )


__all__ = ["SentimentAggregatorV1"]
