"""Temporal Reasoning."""

from .temporal_reasoning import (
    TemporalKnowledgeReasoner,
    get_temporal_reasoner,
)

# Alias for consistency
get_temporal_reasoner = get_temporal_reasoner

__all__ = [
    "TemporalKnowledgeReasoner",
    "get_temporal_reasoner",
]