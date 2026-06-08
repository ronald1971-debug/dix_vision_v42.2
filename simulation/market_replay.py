"""Market Replay – replays historical market data through the cognitive pipeline.

Supports deterministic replay for backtesting and validation.
"""

from __future__ import annotations

import time
from collections.abc import Iterator
from dataclasses import dataclass, field
from typing import Any

from mind.observation import Observation, ObservationType


@dataclass(frozen=True)
class MarketTick:
    symbol: str
    price: float
    volume: float
    timestamp: float
    bid: float = 0.0
    ask: float = 0.0
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass
class ReplayConfig:
    speed_multiplier: float = 1.0  # 1.0 = real-time, 0.0 = as fast as possible
    start_time: float = 0.0
    end_time: float = 0.0
    symbols: list[str] = field(default_factory=list)


@dataclass
class ReplayResult:
    ticks_replayed: int = 0
    observations_generated: int = 0
    duration_seconds: float = 0.0
    start_time: float = 0.0
    end_time: float = 0.0


class MarketReplay:
    """Replays market data for simulation and backtesting."""

    def __init__(self, config: ReplayConfig | None = None) -> None:
        self._config = config or ReplayConfig()
        self._data: list[MarketTick] = []
        self._position: int = 0

    def load_data(self, ticks: list[MarketTick]) -> int:
        self._data = sorted(ticks, key=lambda t: t.timestamp)
        self._position = 0
        return len(self._data)

    def generate_synthetic_data(
        self,
        symbol: str,
        num_ticks: int = 1000,
        base_price: float = 100.0,
        volatility: float = 0.02,
    ) -> int:
        """Generate synthetic market data for testing."""
        import random

        ticks: list[MarketTick] = []
        price = base_price
        ts = time.time() - (num_ticks * 60)

        for i in range(num_ticks):
            change = random.gauss(0, volatility) * price
            price = max(0.01, price + change)
            volume = random.uniform(100, 10000)
            spread = price * 0.001
            ticks.append(
                MarketTick(
                    symbol=symbol,
                    price=round(price, 4),
                    volume=round(volume, 2),
                    timestamp=ts + (i * 60),
                    bid=round(price - spread, 4),
                    ask=round(price + spread, 4),
                )
            )

        return self.load_data(ticks)

    def replay(self) -> Iterator[Observation]:
        """Yield observations from market data sequentially."""
        for tick in self._data[self._position:]:
            self._position += 1
            yield Observation(
                obs_type=ObservationType.PRICE_TICK,
                symbol=tick.symbol,
                value=tick.price,
                context={
                    "volume": tick.volume,
                    "bid": tick.bid,
                    "ask": tick.ask,
                },
                confidence=1.0,
                timestamp=tick.timestamp,
                source="market_replay",
            )

    def reset(self) -> None:
        self._position = 0

    @property
    def total_ticks(self) -> int:
        return len(self._data)

    @property
    def remaining_ticks(self) -> int:
        return len(self._data) - self._position
