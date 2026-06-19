"""IND-L05 VPIN imbalance plugin v1 — Indira learning layer #4.

Volume-synchronized probability of informed trading (VPIN) analysis.

Calculates volume-bucketed toxicity ratio normalized in [0, 1].
This is distinct from footprint_delta which reports raw signed cumulative
delta in volume units.

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
class VpinImbalanceV1(MicrostructurePlugin):
    """Fourth concrete intelligence plugin (IND-L05 v1)."""

    name: str = "vpin_imbalance_v1"
    version: str = "0.1.0"
    lifecycle: PluginLifecycle = PluginLifecycle.ACTIVE
    bucket_size: int = 1000
    window_buckets: int = 10
    vpin_threshold: float = 0.05
    confidence_scale: float = 0.1
    min_confidence: float = 0.05
    _buckets: deque[float] = field(init=False, repr=False)
    _current_bucket: list[float] = field(default_factory=list, init=False, repr=False)
    _current_vol: float = field(default=0.0, init=False, repr=False)

    def __post_init__(self) -> None:
        if self.bucket_size <= 0:
            raise ValueError("bucket_size must be > 0")
        if self.window_buckets < 2:
            raise ValueError("window_buckets must be >= 2")
        if not 0.0 < self.vpin_threshold <= 1.0:
            raise ValueError("vpin_threshold must be in (0, 1]")
        if self.confidence_scale <= 0.0:
            raise ValueError("confidence_scale must be > 0")
        if not 0.0 <= self.min_confidence <= 1.0:
            raise ValueError("min_confidence must be in [0, 1]")
        self._buckets = deque(maxlen=self.window_buckets)

    def on_tick(self, tick: MarketTick) -> tuple[SignalEvent, ...]:
        if tick.bid <= 0.0 or tick.ask <= 0.0 or tick.last <= 0.0:
            return ()
        if tick.ask < tick.bid:
            return ()

        mid = 0.5 * (tick.bid + tick.ask)
        if mid <= 0.0:
            return ()

        # Calculate price impact
        price_move = abs(tick.last - mid) / mid
        self._current_bucket.append(price_move)
        self._current_vol += float(tick.volume)

        # Check if bucket is full
        if self._current_vol >= self.bucket_size:
            # Calculate bucket toxicity
            if self._current_bucket:
                bucket_toxicity = max(self._current_bucket)
            else:
                bucket_toxicity = 0.0

            self._buckets.append(bucket_toxicity)
            self._current_bucket = []
            self._current_vol = 0.0

        if len(self._buckets) < self.window_buckets:
            return ()

        # Calculate VPIN
        avg_toxicity = sum(self._buckets) / len(self._buckets)
        vpin = avg_toxicity

        if vpin > self.vpin_threshold:
            side = Side.HOLD  # VPIN indicates stress, avoid trading
        else:
            return ()

        confidence = min(1.0, vpin / self.confidence_scale)
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
                    "vpin": f"{vpin:.6f}",
                    "vpin_threshold": f"{self.vpin_threshold:.6f}",
                    "bucket_size": f"{self.bucket_size}",
                    "window_buckets": f"{self.window_buckets}",
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
                f"bucket={self.bucket_size} "
                f"window={self.window_buckets} "
                f"thresh={self.vpin_threshold}"
            ),
        )


__all__ = ["VpinImbalanceV1"]
