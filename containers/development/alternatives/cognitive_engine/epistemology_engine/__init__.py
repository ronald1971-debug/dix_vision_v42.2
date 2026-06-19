"""Epistemology Engine — belief lineage tracking.

Every belief must carry lineage, not just value.

(Item 27 — cognitive operating system roadmap)
"""

from cognitive_engine.epistemology_engine.epistemology_engine import (
    BeliefHistoryEntry,
    EpistemologyEngine,
    Evidence,
    get_epistemology_engine,
)

__all__ = [
    "Evidence",
    "BeliefHistoryEntry",
    "EpistemologyEngine",
    "get_epistemology_engine",
]
