"""Market memory module — accumulated knowledge about market structures."""

from __future__ import annotations

import time
from dataclasses import dataclass, field
from typing import Any


@dataclass(frozen=True, slots=True)
class MarketMemory:
    symbol: str
    observed_at: int
    last_updated: int
    structure_type: str = "unknown"
    typical_range: tuple[float, float] | None = None
    key_levels: tuple[float, ...] = ()
    regime_patterns: tuple[str, ...] = ()
    confidence: float = 0.0
    metadata: dict[str, Any] = field(default_factory=dict)


class MarketKnowledgeStore:
    def __init__(self) -> None:
        self._memories: dict[str, MarketMemory] = {}

    def store(self, symbol: str, structure_type: str, **kwargs: Any) -> MarketMemory:
        now = time.time_ns()
        existing = self._memories.get(symbol)
        memory = MarketMemory(
            symbol=symbol,
            observed_at=existing.observed_at if existing else now,
            last_updated=now,
            structure_type=structure_type,
            **kwargs,
        )
        self._memories[symbol] = memory
        return memory

    def get(self, symbol: str) -> MarketMemory | None:
        return self._memories.get(symbol)

    def query(self, structure_type: str | None = None) -> list[MarketMemory]:
        if structure_type is None:
            return list(self._memories.values())
        return [m for m in self._memories.values() if m.structure_type == structure_type]
