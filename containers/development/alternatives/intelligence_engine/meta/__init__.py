"""Trader Intelligence consumer package (TI-CONS).

The meta layer (per dixvision_executive_summary.md "intelligence_engine/
meta/") is where the read-only trader-archetype registry is loaded and
exposed to downstream consumers (the strategy synthesizer + Darwinian
arena). This bootstrap module ships the loader; the synthesizer and
arena land in subsequent PRs.
"""

from intelligence_engine.meta.archetype_embedding_pipeline import (
    ArchetypeEmbeddingPipeline,
    ArchetypeEmbeddingRecord,
    get_archetype_embedding_pipeline,
)
from intelligence_engine.meta.trader_archetypes import (
    TraderArchetype,
    TraderArchetypeRegistry,
    load_trader_archetypes,
)
from intelligence_engine.meta.trader_pattern_selector import (
    MarketContext,
    PatternMatch,
    PatternSource,
    SelectionResult,
    TraderPatternSelector,
)

__all__ = [
    "ArchetypeEmbeddingPipeline",
    "ArchetypeEmbeddingRecord",
    "MarketContext",
    "PatternMatch",
    "PatternSource",
    "SelectionResult",
    "TraderArchetype",
    "TraderArchetypeRegistry",
    "TraderPatternSelector",
    "get_archetype_embedding_pipeline",
    "load_trader_archetypes",
]
