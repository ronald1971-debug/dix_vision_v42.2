"""Tests for ``intelligence_engine.meta.archetype_embedding_pipeline`` (TI-EMBED).

Five test groups:
* Determinism: identical inputs → identical embeddings
* 300-archetype coverage: all registered archetypes embed successfully
* Similarity search: nearest-neighbour semantics work
* Incremental: only changed texts trigger re-embed
* Registry integration: group/philosophy fields round-trip through text
"""

from __future__ import annotations

from pathlib import Path

from intelligence_engine.meta.archetype_embedding_pipeline import (
    ArchetypeEmbeddingPipeline,
    get_archetype_embedding_pipeline,
)
from intelligence_engine.meta.trader_archetypes import (
    load_trader_archetypes,
)

REPO_ROOT = Path(__file__).resolve().parents[1]


def _pipeline(path: Path | None = None) -> ArchetypeEmbeddingPipeline:
    registry = load_trader_archetypes(path)
    return ArchetypeEmbeddingPipeline(registry=registry)


# -------------------------------------------------------------------
# Determinism
# -------------------------------------------------------------------


def test_identical_archetypes_produce_identical_embeddings() -> None:
    pipeline = _pipeline()
    pipeline.run()
    first = pipeline.store()._records[0].vector
    pipeline.run()  # second full run
    second = pipeline.store()._records[0].vector
    assert first == second, "re-running pipeline must produce identical embeddings"


def test_embedding_dimension() -> None:
    pipeline = _pipeline()
    pipeline.run()
    for rec in pipeline.store()._records:
        assert len(rec.vector) == 64, "expected 64-dimensional embeddings"


def test_embeddings_are_normalised() -> None:
    import math

    pipeline = _pipeline()
    pipeline.run()
    for rec in pipeline.store()._records:
        norm = math.sqrt(sum(x * x for x in rec.vector))
        assert abs(norm - 1.0) < 1e-6, "embeddings should be L2-normalised"


# -------------------------------------------------------------------
# 300-archetype coverage
# -------------------------------------------------------------------


def test_all_300_archetypes_embed() -> None:
    registry = load_trader_archetypes()
    assert len(registry) == 300, f"expected 300 archetypes, got {len(registry)}"
    pipeline = _pipeline()
    count = pipeline.run()
    assert count == 300, f"expected 300 embeddings written, got {count}"
    assert pipeline.store().size == 300


def test_all_groups_present() -> None:
    pipeline = _pipeline()
    pipeline.run()
    records = pipeline.store()._records
    groups = set()
    for rec in records:
        aid = rec.record_id
        archetype = pipeline.registry().get(aid)
        assert archetype is not None, f"missing archetype {aid}"
        groups.add(archetype.group)
    expected = {"MACRO", "TREND", "QUANT", "DISCRETIONARY", "EVENT", "CRYPTO", "META", "VALUE", "FLOW"}
    assert groups == expected, f"missing groups: {expected - groups}"


# -------------------------------------------------------------------
# Similarity search
# -------------------------------------------------------------------


def test_find_similar_returns_self_excluded() -> None:
    pipeline = _pipeline()
    pipeline.run()
    results = pipeline.find_similar("TA-MACRO-001", top_k=5)
    assert all(r[1].archetype_id != "TA-MACRO-001" for r in results), "self must be excluded"


def test_find_similar_same_group_scores_higher() -> None:
    pipeline = _pipeline()
    pipeline.run()
    results = pipeline.find_similar("TA-MACRO-001", top_k=10)
    same_group = [
        r for r in results if pipeline.registry().get(r[1].archetype_id).group == "MACRO"
    ]
    different_group = [
        r for r in results if pipeline.registry().get(r[1].archetype_id).group != "MACRO"
    ]
    if same_group and different_group:
        assert max(s[0] for s in same_group) >= max(d[0] for d in different_group)


def test_find_similar_missing_id_returns_empty() -> None:
    pipeline = _pipeline()
    pipeline.run()
    assert pipeline.find_similar("TA-DOES-NOT-EXIST") == []


# -------------------------------------------------------------------
# Incremental re-embed
# -------------------------------------------------------------------


def test_incremental_skips_unchanged() -> None:
    pipeline = _pipeline()
    pipeline.run()
    count = pipeline.run(incremental=True)
    assert count == 0, "incremental run with no changes should produce 0 new embeddings"


# -------------------------------------------------------------------
# Registry integration (group/philosophy fields)
# -------------------------------------------------------------------


def test_group_and_philosophy_roundtrip() -> None:
    pipeline = _pipeline()
    for archetype_id in pipeline.registry().ids():
        archetype = pipeline.registry().get(archetype_id)
        assert archetype.group, f"{archetype_id} missing group"
        assert archetype.philosophy, f"{archetype_id} missing philosophy"
        text = pipeline._archetype_to_text(archetype)
        assert f"group:{archetype.group}" in text
        assert f"philosophy:{archetype.philosophy}" in text


# -------------------------------------------------------------------
# Factory
# -------------------------------------------------------------------


def test_factory_builds_pipeline() -> None:
    pipeline = get_archetype_embedding_pipeline()
    assert isinstance(pipeline, ArchetypeEmbeddingPipeline)
    assert pipeline.registry() is not None
    assert len(pipeline.registry()) == 300


# -------------------------------------------------------------------
# EmbeddingRecord conversion
# -------------------------------------------------------------------


def test_embedding_record_conversion() -> None:
    pipeline = _pipeline()
    pipeline.run()
    rec = pipeline.get_embedding("TA-MACRO-001")
    assert rec is not None
    er = rec.to_embedding_record()
    assert er.record_id == "TA-MACRO-001"
    assert len(er.vector) == 64
    assert er.metadata["source_text"] == rec.source_text
