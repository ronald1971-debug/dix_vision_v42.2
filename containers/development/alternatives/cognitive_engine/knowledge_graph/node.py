"""Knowledge Node - node types for the knowledge graph."""

from __future__ import annotations

import time
from dataclasses import dataclass, field
from enum import Enum
from typing import Any


class NodeType(Enum):
    """Types of knowledge nodes."""

    TRADER = "trader"
    STRATEGY = "strategy"
    REGIME = "regime"
    MARKET = "market"
    EXECUTION = "execution"
    CATALYST = "catalyst"
    NARRATIVE = "narrative"


@dataclass
class KnowledgeNode:
    """A node in the knowledge graph."""

    node_id: str
    node_type: NodeType
    name: str = ""
    properties: dict[str, Any] = field(default_factory=dict)
    created_at: int = field(default_factory=lambda: time.time_ns())
    confidence: float = 1.0

    def update_property(self, key: str, value: Any) -> None:
        """Update a property value."""
        self.properties[key] = value

    def update_confidence(self, confidence: float) -> None:
        """Update node confidence."""
        self.confidence = max(0.0, min(1.0, confidence))
