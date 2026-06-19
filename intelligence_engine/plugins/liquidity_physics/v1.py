"""IND-L07 liquidity physics plugin v1 — Indira learning layer #6.

Analyzes liquidity physics and market depth dynamics.

Pure (INV-15 / TEST-01): no clock, no PRNG, no IO.
"""

from __future__ import annotations

from collections import deque
from dataclasses import dataclass, field

from core.contracts.engine import (
    HealthState,
    HealthStatus,
    PluginLifecycle,
    MicrostructurePlugin,
)
from core.contracts.events import Side, SignalEvent
from core.contracts.market import MarketTick


@dataclass(slots=True)
class LiquidityPhysicsV1(MicrostructurePlugin):
    """Sixth concrete intelligence plugin (IND-L07 v1)."""

    name: str = "liquidity_physics_v1"
    version: str = "0.1.0"
    lifecycle: PluginLifecycle = PluginLifecycle.ACTIVE
    window_size: int = 20
    volume_threshold: float = 1000.0
    liquidity_threshold: float = 0.3
    confidence_scale: float = 1000.0
    min_confidence: float = 0.05
    _volume_window: deque[float] = field(init=False, repr=False)

    def __post_init__(self) -> None:
        if self.window_size < 2:
            raise ValueError("window_size must be >= 2")
        if self.volume_threshold < 0.0:
            raise ValueError("volume_threshold must be >= 0")
        if not 0.0 < self.liquidity_threshold <= 1.0:
            raise ValueError("liquidity_threshold must be in (0, 1]")
        if self.confidence_scale <= 0.0:
            raise ValueError("confidence_scale must be > 0")
        if not 0.0 <= self.min_confidence <= 1.0:
            raise ValueError("min_confidence must be in [0, 1]")
        self._volume_window = deque(maxlen=self.window_size)

    def on_tick(self, tick: MarketTick) -> tuple[SignalEvent, ...]:
        if tick.bid <= 0.0 or tick.ask <= 0.0 or tick.last <= 0.0:
            return ()
        if tick.ask < tick.bid:
            return ()
        if tick.volume < 0.0:
            return ()

        self._volume_window.append(float(tick.volume))

        if len(self._volume_window) < self.window_size:
            return ()

        avg_volume = sum(self._volume_window) / len(self._volume_window)
        current_volume = float(tick.volume)

        # Liquidity ratio
        liquidity_ratio = current_volume / avg_volume if avg_volume > 0 else 1.0

        if liquidity_ratio > (1.0 + self.liquidity_threshold):
            side = Side.BUY  # High volume suggests liquidity absorption
        elif liquidity_ratio < (1.0 - self.liquidity_threshold):
            side = Side.SELL  # Low volume suggests liquidity drying
        else:
            return ()

        confidence = min(1.0, abs(liquidity_ratio - 1.0) * self.volume_threshold / self.confidence_scale)
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
                    "avg_volume": f"{avg_volume:.2f}",
                    "current_volume": f"{current_volume:.2f}",
                    "liquidity_ratio": f"{liquidity_ratio:.4f}",
                    "liquidity_threshold": f"{self.liquidity_threshold:.4f}",
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
                f"vol_thresh={self.volume_threshold}"
            ),
        )


__all__ = ["LiquidityPhysicsV1"]
