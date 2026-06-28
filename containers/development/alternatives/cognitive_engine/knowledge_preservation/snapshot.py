"""Knowledge Snapshot - captures knowledge state for preservation."""

from __future__ import annotations

import time
from dataclasses import dataclass, field
from typing import Any


@dataclass
class KnowledgeSnapshot:
    """A snapshot of knowledge at a point in time."""

    snapshot_id: str = field(default_factory=lambda: f"snapshot_{time.time_ns()}")
    created_at: int = field(default_factory=lambda: time.time_ns())
    trader_knowledge: dict[str, Any] = field(default_factory=dict)
    strategy_knowledge: dict[str, Any] = field(default_factory=dict)
    market_knowledge: dict[str, Any] = field(default_factory=dict)
    regime_knowledge: dict[str, Any] = field(default_factory=dict)
    execution_knowledge: dict[str, Any] = field(default_factory=dict)
    cognitive_knowledge: dict[str, Any] = field(default_factory=dict)
    hash_checksum: str = ""
    schema_version: str = "1.0"

    def total_entries(self) -> int:
        """Get total knowledge entries in snapshot."""
        return (
            len(self.trader_knowledge)
            + len(self.strategy_knowledge)
            + len(self.market_knowledge)
            + len(self.regime_knowledge)
            + len(self.execution_knowledge)
            + len(self.cognitive_knowledge)
        )
