"""Strategy memory module — knowledge about evolved strategies.

Supports mutation, combination, evolution, and retirement of strategies.
"""

from __future__ import annotations

import time
from dataclasses import dataclass, field
from typing import Any


@dataclass
class StrategyMemory:
    """Accumulated knowledge about a strategy's performance and characteristics.

    Example:
        Inputs: ["price", "volume", "regime"]
        Features: ["momentum", "mean_reversion"]
        Logic: "enter on regime flip + momentum confirmation"
        Risk Profile: "fixed fractional, ATR stop"
        Markets: ["BTC", "ETH", "SPY"]
        Timeframes: ["1h", "4h", "1d"]
        Failure Modes: ["regime flip false positive", "low liquidity slippage"]
    """

    strategy_id: str
    genome_id: str
    name: str
    inputs: tuple[str, ...] = ()
    features: tuple[str, ...] = ()
    logic: str = ""
    risk_profile: str = ""
    markets: tuple[str, ...] = ()
    timeframes: tuple[str, ...] = ()
    failure_modes: tuple[str, ...] = ()
    performance_score: float = 0.0
    confidence: float = 0.0
    observed_at: int = field(default_factory=lambda: time.time_ns())
    last_updated: int = field(default_factory=lambda: time.time_ns())
    win_rate: float = 0.0
    sharpe_ratio: float = 0.0
    max_drawdown: float = 0.0
    metadata: dict[str, Any] = field(default_factory=dict)


class StrategyKnowledgeStore:
    """Long-term memory for evolved strategies.

    Supports:
        - Store strategy genome knowledge
        - Query by performance, market, timeframe
        - Retrieve strategies for evolution
        - Track strategy lineage and mutations
    """

    def __init__(self) -> None:
        self._memories: dict[str, StrategyMemory] = {}
        self._index_by_market: dict[str, list[str]] = {}
        self._index_by_timeframe: dict[str, list[str]] = {}
        self._retired: set[str] = set()

    def store(self, memory: StrategyMemory) -> None:
        self._memories[memory.strategy_id] = memory
        for m in memory.markets:
            self._index_by_market.setdefault(m, []).append(memory.strategy_id)
        for tf in memory.timeframes:
            self._index_by_timeframe.setdefault(tf, []).append(memory.strategy_id)

    def get(self, strategy_id: str) -> StrategyMemory | None:
        if strategy_id in self._retired:
            return None
        return self._memories.get(strategy_id)

    def query_by_market(self, market: str) -> list[StrategyMemory]:
        ids = self._index_by_market.get(market, [])
        return [
            self._memories[sid] for sid in ids
            if sid in self._memories and sid not in self._retired
        ]

    def query_by_timeframe(self, timeframe: str) -> list[StrategyMemory]:
        ids = self._index_by_timeframe.get(timeframe, [])
        return [
            self._memories[sid] for sid in ids
            if sid in self._memories and sid not in self._retired
        ]

    def retire(self, strategy_id: str) -> bool:
        if strategy_id in self._memories:
            self._retired.add(strategy_id)
            return True
        return False

    @property
    def strategy_count(self) -> int:
        return len(self._memories) - len(self._retired)