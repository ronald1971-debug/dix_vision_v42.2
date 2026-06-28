"""Collective Intelligence — tracks individual AND group trader understanding.

(Item 37 — cognitive operating system roadmap)
"""

from cognitive_engine.collective_intelligence.collective_intelligence import (
    Cluster,
    CollectiveIntelligenceEngine,
    TraderProfile,
    get_collective_intelligence,
)

__all__ = [
    "CollectiveIntelligenceEngine",
    "TraderProfile",
    "Cluster",
    "get_collective_intelligence",
]
