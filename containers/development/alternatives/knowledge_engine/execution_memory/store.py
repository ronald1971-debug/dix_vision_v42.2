"""Execution memory module — knowledge about execution quality and venue performance."""

from __future__ import annotations

import time
from dataclasses import dataclass, field
from typing import Any


@dataclass(frozen=True, slots=True)
class ExecutionMemory:
    venue: str
    symbol: str
    observed_at: int
    last_updated: int
    avg_slippage: float = 0.0
    fill_rate: float = 0.0
    latency_ms: float = 0.0
    regime_performance: dict[str, float] = field(default_factory=dict)
    confidence: float = 0.0
    metadata: dict[str, Any] = field(default_factory=dict)


class ExecutionKnowledgeStore:
    def __init__(self) -> None:
        self._memories: dict[str, ExecutionMemory] = {}

    def store(self, venue: str, symbol: str, **kwargs: Any) -> ExecutionMemory:
        now = time.time_ns()
        key = f"{venue}:{symbol}"
        existing = self._memories.get(key)
        memory = ExecutionMemory(
            venue=venue,
            symbol=symbol,
            observed_at=existing.observed_at if existing else now,
            last_updated=now,
            **kwargs,
        )
        self._memories[key] = memory
        return memory

    def get(self, venue: str, symbol: str) -> ExecutionMemory | None:
        return self._memories.get(f"{venue}:{symbol}")

    def query_by_venue(self, venue: str) -> list[ExecutionMemory]:
        return [m for m in self._memories.values() if m.venue == venue]

    def get_best_venue(self, symbol: str, regime: str | None = None) -> ExecutionMemory | None:
        candidates = [m for m in self._memories.values() if m.symbol == symbol]
        if regime:
            candidates = [c for c in candidates if regime in c.regime_performance]
        if not candidates:
            return None
        return max(candidates, key=lambda m: m.fill_rate - m.avg_slippage)
