"""Regime memory module — knowledge about market regime transitions and characteristics."""

from __future__ import annotations

import time
from dataclasses import dataclass, field
from typing import Any


@dataclass(frozen=True, slots=True)
class RegimeMemory:
    regime: str
    observed_at: int
    last_updated: int
    avg_duration_seconds: float = 0.0
    transition_patterns: tuple[str, ...] = ()
    strategy_performance: dict[str, float] = field(default_factory=dict)
    confidence: float = 0.0
    metadata: dict[str, Any] = field(default_factory=dict)


class RegimeKnowledgeStore:
    def __init__(self) -> None:
        self._memories: dict[str, RegimeMemory] = {}

    def store(self, regime: str, **kwargs: Any) -> RegimeMemory:
        now = time.time_ns()
        existing = self._memories.get(regime)
        memory = RegimeMemory(
            regime=regime,
            observed_at=existing.observed_at if existing else now,
            last_updated=now,
            **kwargs,
        )
        self._memories[regime] = memory
        return memory

    def get(self, regime: str) -> RegimeMemory | None:
        return self._memories.get(regime)

    def all_regimes(self) -> list[RegimeMemory]:
        return list(self._memories.values())