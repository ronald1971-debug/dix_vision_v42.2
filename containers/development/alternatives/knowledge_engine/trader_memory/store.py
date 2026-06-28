"""Trader knowledge store — accumulated understanding of trader profiles.

Example:
    Trader A learns:
        works in: high volatility, low liquidity
        confidence: 0.81
        observed: 2026-06-01

    Years later:
        INDIRA remembers it.

Not just data — actual accumulated knowledge.
"""

from __future__ import annotations

import time
import uuid
from dataclasses import dataclass, field
from typing import Any


@dataclass(frozen=True, slots=True)
class VolatilityExposure:
    """Trader's performance in volatility regimes."""

    high: float = 0.0
    medium: float = 0.0
    low: float = 0.0

    def best_regime(self) -> str:
        exposures = [("high", self.high), ("medium", self.medium), ("low", self.low)]
        return max(exposures, key=lambda x: x[1])[0]


@dataclass(frozen=True, slots=True)
class LiquidityExposure:
    """Trader's performance in liquidity conditions."""

    low: float = 0.0
    normal: float = 0.0
    high: float = 0.0

    def best_condition(self) -> str:
        exposures = [("low", self.low), ("normal", self.normal), ("high", self.high)]
        return max(exposures, key=lambda x: x[1])[0]


@dataclass(frozen=True, slots=True)
class TraderMemory:
    """Accumulated knowledge about a trader's behavior and performance.

    This represents INDIRA's long-term memory of trader A:
        - What regimes they excel in
        - Their risk patterns
        - Observed behavior patterns with timestamps
        - Confidence in the profile accuracy
    """

    trader_id: str
    observed_at: int  # nanosecond timestamp of first observation
    last_updated: int  # last update timestamp
    volatility_exposure: VolatilityExposure = field(default_factory=VolatilityExposure)
    liquidity_exposure: LiquidityExposure = field(default_factory=LiquidityExposure)
    confidence: float = 0.0
    belief_system: dict[str, float] = field(default_factory=dict)
    behavior_patterns: tuple[str, ...] = ()  # pattern IDs from TraderKnowledgeStore
    regime_accuracy: dict[str, float] = field(default_factory=dict)  # regime -> accuracy
    decay_weight: float = 1.0

    def is_reliable_in_regime(self, regime: str, threshold: float = 0.7) -> bool:
        return self.regime_accuracy.get(regime, 0.0) >= threshold


@dataclass
class TraderObservation:
    """A validated observation about a trader's behavior."""

    observation_id: str = field(default_factory=lambda: uuid.uuid4().hex[:12])
    trader_id: str = ""
    timestamp: int = field(default_factory=lambda: time.time_ns())
    regime: str = ""
    volatility_level: str = "medium"
    liquidity_level: str = "normal"
    pnl: float = 0.0
    confidence_signal: float = 0.0
    pattern_detected: str = ""
    metadata: dict[str, Any] = field(default_factory=dict)


class TraderKnowledgeStore:
    """Long-term memory store for trader knowledge.

    Supports:
        - Store trader memory records
        - Query by regime compatibility
        - Retrieve traders effective in specific conditions
        - Consolidate/expire stale knowledge
        - Export as unified ontology Knowledge objects
    """

    def __init__(self) -> None:
        self._memories: dict[str, TraderMemory] = {}
        self._index_by_regime: dict[str, list[str]] = {}

    def record_observation(self, obs: TraderObservation) -> None:
        memory = self._memories.get(obs.trader_id)
        if memory is None:
            self._memories[obs.trader_id] = TraderMemory(
                trader_id=obs.trader_id,
                observed_at=obs.timestamp,
                last_updated=obs.timestamp,
                confidence=1.0,
            )
            return

        updates = {
            "last_updated": obs.timestamp,
        }
        if obs.volatility_level == "high":
            updates["volatility_high"] = obs.pnl
        elif obs.volatility_level == "medium":
            updates["volatility_medium"] = obs.pnl
        elif obs.volatility_level == "low":
            updates["volatility_low"] = obs.pnl

        self._memories[obs.trader_id] = _update_memory_with(obs, self._memories[obs.trader_id])
        regime = obs.regime
        if regime and obs.trader_id not in self._index_by_regime.get(regime, []):
            self._index_by_regime.setdefault(regime, []).append(obs.trader_id)

    def get_memory(self, trader_id: str) -> TraderMemory | None:
        return self._memories.get(trader_id)

    def query_by_regime(self, regime: str) -> list[TraderMemory]:
        trader_ids = self._index_by_regime.get(regime, [])
        return [self._memories[pid] for pid in trader_ids if pid in self._memories]

    def get_reliable_traders(self, regime: str, min_confidence: float = 0.7) -> list[TraderMemory]:
        return [
            m for m in self._memories.values() if m.is_reliable_in_regime(regime, min_confidence)
        ]


def _update_memory_with(obs: TraderObservation, mem: TraderMemory) -> TraderMemory:
    vol_exp = VolatilityExposure(
        high=getattr(mem.volatility_exposure, "high", 0.0),
        medium=getattr(mem.volatility_exposure, "medium", 0.0),
        low=getattr(mem.volatility_exposure, "low", 0.0),
    )
    if obs.volatility_level == "high":
        vol_exp = VolatilityExposure(
            high=vol_exp.high + obs.pnl, medium=vol_exp.medium, low=vol_exp.low
        )
    elif obs.volatility_level == "medium":
        vol_exp = VolatilityExposure(
            high=vol_exp.high, medium=vol_exp.medium + obs.pnl, low=vol_exp.low
        )
    elif obs.volatility_level == "low":
        vol_exp = VolatilityExposure(
            high=vol_exp.high, medium=vol_exp.medium, low=vol_exp.low + obs.pnl
        )

    reg_acc = dict(mem.regime_accuracy)
    current = reg_acc.get(obs.regime, 0.0)
    reg_acc[obs.regime] = (current + obs.confidence_signal) / 2

    return TraderMemory(
        trader_id=mem.trader_id,
        observed_at=mem.observed_at,
        last_updated=obs.timestamp,
        volatility_exposure=vol_exp,
        liquidity_exposure=mem.liquidity_exposure,
        confidence=min(1.0, mem.confidence * 0.99 + 0.01),
        belief_system=mem.belief_system,
        behavior_patterns=mem.behavior_patterns,
        regime_accuracy=reg_acc,
        decay_weight=mem.decay_weight,
    )
