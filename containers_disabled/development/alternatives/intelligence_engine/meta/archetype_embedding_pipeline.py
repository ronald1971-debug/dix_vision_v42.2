"""Archetype embedding pipeline (TI-EMBED).

Projects all active archetypes into a lower-dimensional embedding space
using the deterministic hashed-token embedder and stores them in the
trader embedding store for similarity search, clustering, and
philosophy matching.

Governance rules (INV-51 / B1):

* **Read-only on hot path** — the pipeline is invoked offline / during
  registry sync; engines never mutate the embedding store at runtime.
* **Offline-only** — the pipeline lives in the meta layer; it never
  imports from ``execution_engine``, ``governance_engine``,
  ``system_engine``, or ``core``.
* **INV-15** — deterministic output: the same archetype registry
  always produces the same embeddings because it uses the pure-stdlib
  ``embed_text`` hashed-token backend with a fixed spec.
* **Versioned** — embedding specs are tracked in
  ``registry/versions.yaml``; the pipeline emits a ledger event
  (INTELLIGENCE stream) when a full re-embed is triggered.
"""

from __future__ import annotations

import logging
from dataclasses import dataclass
from pathlib import Path

from intelligence_engine.meta.trader_archetypes import (
    TraderArchetype,
    TraderArchetypeRegistry,
    load_trader_archetypes,
)
from learning_engine.vector_memory.trader_embeddings import (
    EmbeddingRecord,
    TraderEmbeddingStore,
)
from state.memory_tensor.embedder import EmbedderSpec, embed_text

_logger = logging.getLogger(__name__)

# Canonical embedder spec for archetype texts.
#   dim=64   → enough headroom for ~300 archetypes with low collision
#   normalize → cosine-similarity-ready
#   unigrams  → simple, fast, deterministic
_ARCHETYPE_EMBED_SPEC = EmbedderSpec(dim=64, normalize=True, ngram_range=(1, 1))


@dataclass(frozen=True, slots=True)
class ArchetypeEmbeddingRecord:
    """Links an archetype_id to its embedding and raw text."""

    archetype_id: str
    embedding: tuple[float, ...]
    source_text: str
    ts_ns: int

    def to_embedding_record(self) -> EmbeddingRecord:
        return EmbeddingRecord(
            record_id=self.archetype_id,
            vector=self.embedding,
            metadata={
                "source_text": self.source_text,
                "archetype_id": self.archetype_id,
            },
        )


class ArchetypeEmbeddingPipeline:
    """End-to-end pipeline: registry → text → embeddings → vector store.

    Usage::

        pipeline = ArchetypeEmbeddingPipeline()
        pipeline.run()                        # re-embed everything
        pipeline.run(incremental=True)        # only new/changed
        similar = pipeline.find_similar("TA-MACRO-001", top_k=5)
    """

    def __init__(
        self,
        registry: TraderArchetypeRegistry | None = None,
        store: TraderEmbeddingStore | None = None,
        spec: EmbedderSpec = _ARCHETYPE_EMBED_SPEC,
    ) -> None:
        self._registry = registry or load_trader_archetypes()
        self._store = store or TraderEmbeddingStore(dimension=spec.dim)
        self._spec = spec
        self._cached_texts: dict[str, str] = {}
        self._rebuild_cached_texts()

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def run(self, *, incremental: bool = False, ts_ns: int = 0) -> int:
        """Re-embed archetypes and update the vector store.

        Args:
            incremental: if True, only embed archetypes whose source
                text has changed since the last run.
            ts_ns: caller-supplied timestamp (INV-15).

        Returns:
            Number of embeddings written to the store.
        """
        records = self._build_records(ts_ns=ts_ns, incremental=incremental)
        self._store._records.clear()
        self._store._vectors.clear()
        for rec in records:
            self._store.add(rec.to_embedding_record())
        if records:
            self._emit_ledger(records, ts_ns=ts_ns)
        return len(records)

    def find_similar(
        self,
        archetype_id: str,
        *,
        top_k: int = 5,
    ) -> list[tuple[ArchetypeEmbeddingRecord, float]]:
        """Find the top-k most similar archetypes to ``archetype_id``."""
        query_rec = self._get_embedding_record(archetype_id)
        if query_rec is None:
            return []
        candidates = [
            self._get_embedding_record(aid) for aid in self._registry.ids() if aid != archetype_id
        ]
        scored = [(self._cosine_similarity(query_rec, c), c) for c in candidates if c is not None]
        scored.sort(key=lambda x: x[0], reverse=True)
        return scored[:top_k]

    def get_embedding(self, archetype_id: str) -> ArchetypeEmbeddingRecord | None:
        """Return the cached embedding record for an archetype."""
        return self._get_embedding_record(archetype_id)

    def store(self) -> TraderEmbeddingStore:
        """Return the underlying vector store."""
        return self._store

    def registry(self) -> TraderArchetypeRegistry:
        """Return the archetype registry."""
        return self._registry

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    def _rebuild_cached_texts(self) -> None:
        self._cached_texts = {
            aid: self._archetype_to_text(a) for aid, a in self._registry.by_id.items()
        }

    @staticmethod
    def _archetype_to_text(archetype: TraderArchetype) -> str:
        """Serialise an archetype into a deterministic text string."""
        parts = [
            f"id:{archetype.archetype_id}",
            f"name:{archetype.name}",
            f"seed:{archetype.seed_trader}",
            f"group:{archetype.group}",
            f"philosophy:{archetype.philosophy}",
        ]
        dims_parts = []
        dims_parts.append(f"risk:{archetype.risk_attitude.value}")
        dims_parts.append(f"horizon:{archetype.time_horizon.value}")
        dims_parts.append(f"conviction:{archetype.conviction_style.value}")
        for tag, strength in sorted(archetype.belief_system.items()):
            dims_parts.append(f"belief:{tag}:{strength:.4f}")
        for regime, score in sorted(archetype.regime_performance.items()):
            dims_parts.append(f"regime:{regime}:{score:.4f}")
        parts.append("|".join(dims_parts))
        return " ".join(parts)

    def _build_records(
        self,
        *,
        ts_ns: int,
        incremental: bool,
    ) -> list[ArchetypeEmbeddingRecord]:
        records: list[ArchetypeEmbeddingRecord] = []
        for archetype_id in self._registry.ids():
            text = self._cached_texts[archetype_id]
            if incremental and self._store.size > 0:
                existing = self._store._records
                match = next((r for r in existing if r.record_id == archetype_id), None)
                if match is not None and match.metadata.get("source_text") == text:
                    continue
            vec = embed_text(text, self._spec)
            records.append(
                ArchetypeEmbeddingRecord(
                    archetype_id=archetype_id,
                    embedding=vec,
                    source_text=text,
                    ts_ns=ts_ns,
                )
            )
        return records

    def _get_embedding_record(self, archetype_id: str) -> ArchetypeEmbeddingRecord | None:
        rec = next(
            (r for r in self._store._records if r.record_id == archetype_id),
            None,
        )
        if rec is None:
            return None
        return ArchetypeEmbeddingRecord(
            archetype_id=archetype_id,
            embedding=rec.vector,
            source_text=rec.metadata.get("source_text", ""),
            ts_ns=0,
        )

    @staticmethod
    def _cosine_similarity(
        a: ArchetypeEmbeddingRecord,
        b: ArchetypeEmbeddingRecord,
    ) -> float:
        import math

        def _norm(v: tuple[float, ...]) -> float:
            return math.sqrt(sum(x * x for x in v))

        na, nb = _norm(a.embedding), _norm(b.embedding)
        if na < 1e-12 or nb < 1e-12:
            return 0.0
        return sum(x * y for x, y in zip(a.embedding, b.embedding)) / (na * nb)

    def _emit_ledger(self, records: list[ArchetypeEmbeddingRecord], *, ts_ns: int) -> None:
        try:
            from state.ledger.append import append_event

            append_event(
                stream="INTELLIGENCE",
                kind="ARCHETYPE_EMBEDDING_REFRESH",
                source="INDIRA",
                payload={
                    "count": len(records),
                    "archetype_ids": [r.archetype_id for r in records],
                    "embed_spec": {
                        "dim": self._spec.dim,
                        "normalize": self._spec.normalize,
                        "ngram_range": list(self._spec.ngram_range),
                    },
                    "ts_ns": ts_ns,
                },
            )
        except Exception:
            pass


# ---------------------------------------------------------------------------
# Module-level factory
# ---------------------------------------------------------------------------


def get_archetype_embedding_pipeline(
    *,
    registry_path: str | Path | None = None,
    spec: EmbedderSpec = _ARCHETYPE_EMBED_SPEC,
) -> ArchetypeEmbeddingPipeline:
    """Factory: load registry from disk and build the pipeline."""
    registry = load_trader_archetypes(registry_path)
    store = TraderEmbeddingStore(dimension=spec.dim)
    return ArchetypeEmbeddingPipeline(registry=registry, store=store, spec=spec)


__all__ = [
    "ArchetypeEmbeddingPipeline",
    "ArchetypeEmbeddingRecord",
    "get_archetype_embedding_pipeline",
]
