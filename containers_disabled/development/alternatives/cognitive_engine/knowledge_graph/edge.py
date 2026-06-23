"""Knowledge Edge - relationships between knowledge nodes."""

from __future__ import annotations

import time
from dataclasses import dataclass, field
from enum import Enum
from typing import Any


class EdgeType(Enum):
    """Types of relationships between nodes."""

    USES = "uses"
    WORKS_DURING = "works_during"
    APPEARS_WHEN = "appears_when"
    EXECUTED_ON = "executed_on"
    INFLUENCES = "influences"
    CORRELATED_WITH = "correlated_with"


@dataclass
class KnowledgeEdge:
    """A relationship between knowledge nodes."""

    edge_id: str
    source_id: str
    target_id: str
    edge_type: EdgeType
    strength: float = 1.0
    created_at: int = field(default_factory=lambda: time.time_ns())
    evidence: tuple[str, ...] = ()
    metadata: dict[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        self.strength = max(0.0, min(1.0, self.strength))
