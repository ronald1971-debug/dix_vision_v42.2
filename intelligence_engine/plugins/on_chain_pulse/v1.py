"""IND-L09 on-chain pulse plugin v1 — Indira learning layer #8.

On-chain data analysis for crypto markets.

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
class OnChainPulseV1(MicrostructurePlugin):
    """Eighth concrete intelligence plugin (IND-L09 v1)."""

    name: str = "on_chain_pulse_v1"
    version: str = "0.1.0"
    lifecycle: PluginLifecycle = PluginLifecycle.ACTIVE
    pulse_threshold: float = 0.5
    confidence_scale: float = 0.1
    min_confidence: float = 0.05

    def __post_init__(self) -> None:
        if not 0.0 < self.pulse_threshold <= 1.0:
            raise ValueError("pulse_threshold must be in (0, 1]")
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

        # In production, this would integrate with actual on-chain data
        # For now, use volume as a proxy for on-chain activity
        volume_pulse = float(tick.volume) / 1000.0  # Normalized proxy

        if volume_pulse > self.pulse_threshold:
            side = Side.BUY  # High on-chain activity suggests buying pressure
        else:
            return ()

        confidence = min(1.0, volume_pulse / self.confidence_scale)
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
                    "volume_pulse": f"{volume_pulse:.6f}",
                    "pulse_threshold": f"{self.pulse_threshold:.6f}",
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
                f"pulse_thresh={self.pulse_threshold}"
            ),
        )


__all__ = ["OnChainPulseV1"]
