"""Observation Layer – raw market data intake and normalization.

First stage of the cognitive pipeline: receives raw data and
produces structured observations for knowledge acquisition.
"""

from __future__ import annotations

import time
import uuid
from dataclasses import dataclass, field
from enum import Enum, auto
from typing import Any


class ObservationType(Enum):
    PRICE_TICK = auto()
    ORDER_BOOK_UPDATE = auto()
    VOLUME_SPIKE = auto()
    VOLATILITY_CHANGE = auto()
    REGIME_SIGNAL = auto()
    NEWS_EVENT = auto()
    CORRELATION_SHIFT = auto()


@dataclass(frozen=True)
class Observation:
    observation_id: str = field(default_factory=lambda: uuid.uuid4().hex[:12])
    obs_type: ObservationType = ObservationType.PRICE_TICK
    symbol: str = ""
    value: float = 0.0
    context: dict[str, Any] = field(default_factory=dict)
    confidence: float = 1.0
    timestamp: float = field(default_factory=time.time)
    source: str = ""


class ObservationBuffer:
    """Sliding window buffer for recent observations."""

    def __init__(self, max_size: int = 10000, max_age_seconds: float = 300.0) -> None:
        self._buffer: list[Observation] = []
        self._max_size = max_size
        self._max_age = max_age_seconds

    def add(self, obs: Observation) -> None:
        self._buffer.append(obs)
        self._evict()

    def get_recent(self, count: int = 100) -> list[Observation]:
        return self._buffer[-count:]

    def get_by_type(self, obs_type: ObservationType) -> list[Observation]:
        return [o for o in self._buffer if o.obs_type == obs_type]

    def get_by_symbol(self, symbol: str) -> list[Observation]:
        return [o for o in self._buffer if o.symbol == symbol]

    @property
    def size(self) -> int:
        return len(self._buffer)

    def _evict(self) -> None:
        if len(self._buffer) > self._max_size:
            self._buffer = self._buffer[-self._max_size:]

        cutoff = time.time() - self._max_age
        self._buffer = [o for o in self._buffer if o.timestamp >= cutoff]


class ObservationProcessor:
    """Processes raw market data into structured observations."""

    def __init__(self) -> None:
        self._buffer = ObservationBuffer()
        self._processors: dict[str, Any] = {}

    @property
    def buffer(self) -> ObservationBuffer:
        return self._buffer

    def process_tick(
        self, symbol: str, price: float, volume: float, source: str = ""
    ) -> Observation:
        obs = Observation(
            obs_type=ObservationType.PRICE_TICK,
            symbol=symbol,
            value=price,
            context={"volume": volume},
            source=source,
        )
        self._buffer.add(obs)
        return obs

    def process_volume_spike(
        self, symbol: str, volume: float, threshold: float, source: str = ""
    ) -> Observation | None:
        if volume <= threshold:
            return None
        obs = Observation(
            obs_type=ObservationType.VOLUME_SPIKE,
            symbol=symbol,
            value=volume,
            context={"threshold": threshold, "ratio": volume / threshold},
            source=source,
        )
        self._buffer.add(obs)
        return obs

    def process_regime_signal(
        self, regime: str, confidence: float, source: str = ""
    ) -> Observation:
        obs = Observation(
            obs_type=ObservationType.REGIME_SIGNAL,
            value=confidence,
            context={"regime": regime},
            confidence=confidence,
            source=source,
        )
        self._buffer.add(obs)
        return obs
