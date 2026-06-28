"""state.memory.index — MemoryIndexAuthority.

Inverted keyword index over MemoryRecord tags and summary tokens.
Enables fast cross-store keyword search without a vector query.

Design:
- In-process dict-based inverted index (token → set of record_ids)
- Tokens: tags + lowercased summary words (alpha-only, len >= 3)
- Thread-safe via a single RWLock simulation (one mutex)
- No external dependencies; no IO; no clock (INV-15)
"""

from __future__ import annotations

import logging
import re
import threading
from collections import defaultdict
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from state.memory.contracts import MemoryRecord

_logger = logging.getLogger(__name__)
_TOKENRE = re.compile(r"[a-z]{3,}")


def _tokenize(text: str) -> list[str]:
    return _TOKENRE.findall(text.lower())


class MemoryIndexAuthority:
    """Enhanced memory index with temporal, semantic, and conflict-aware indexing.

    Provides:
    - Inverted keyword index over MemoryRecord tags and summary tokens
    - Temporal indexing for knowledge evolution tracking
    - Semantic indexing for concept-based retrieval
    - Conflict-aware indexing for source dispute resolution
    - Performance optimization for large-scale knowledge graphs

    Design:
    - In-process dict-based inverted index (token → set of record_ids)
    - Tokens: tags + lowercased summary words (alpha-only, len >= 3)
    - Thread-safe via a single RWLock simulation (one mutex)
    - No external dependencies; no IO; no clock (INV-15)
    """

    def __init__(self) -> None:
        self._lock: threading.Lock = threading.Lock()
        self._index: dict[str, set[str]] = defaultdict(set)  # token → record_ids
        self._records: dict[str, MemoryRecord] = {}  # record_id → record
        self._total: int = 0

        # Enhanced indexing for M-1 Knowledge Layer
        self._temporal_index: dict[int, set[str]] = defaultdict(set)  # timestamp → record_ids
        self._semantic_index: dict[str, set[str]] = defaultdict(set)  # concept → record_ids
        self._conflict_index: dict[str, set[str]] = defaultdict(set)  # conflict_group → record_ids
        self._source_index: dict[str, set[str]] = defaultdict(set)  # source → record_ids
        self._kind_index: dict[str, set[str]] = defaultdict(set)  # MemoryKind → record_ids

    # ------------------------------------------------------------------
    # Write
    # ------------------------------------------------------------------

    def index(self, record: MemoryRecord) -> None:
        """Index one record with enhanced M-1 Knowledge Layer indexing. Idempotent (re-indexing same id is safe)."""
        try:
            tokens = set(_tokenize(record.summary))
            tokens.update(t.lower() for t in record.tags)
            tokens.update(_tokenize(record.source))

            # Extract semantic concepts for semantic indexing
            concepts = self._extract_concepts(record)

            with self._lock:
                self._records[record.record_id] = record

                # Traditional keyword indexing
                for tok in tokens:
                    self._index[tok].add(record.record_id)

                # Temporal indexing for knowledge evolution tracking
                self._temporal_index[self._quantize_timestamp(record.ts_ns)].add(record.record_id)

                # Semantic indexing for concept-based retrieval
                for concept in concepts:
                    self._semantic_index[concept].add(record.record_id)

                # Source indexing for source-aware retrieval
                self._source_index[record.source].add(record.record_id)

                # Kind indexing for type-based retrieval
                self._kind_index[record.kind.value].add(record.record_id)

                # Conflict-aware indexing (if conflict information in body)
                if "conflict_group" in record.body:
                    self._conflict_index[record.body["conflict_group"]].add(record.record_id)

                self._total += 1
        except Exception as exc:
            _logger.debug("index.index error: %s", exc)

    # ------------------------------------------------------------------
    # Read
    # ------------------------------------------------------------------

    def search(self, keywords: list[str], limit: int = 20) -> list[MemoryRecord]:
        """Return records matching ALL keywords (AND semantics)."""
        if not keywords:
            return []
        try:
            tokens = [kw.lower() for kw in keywords if len(kw) >= 3]
            if not tokens:
                return []
            with self._lock:
                candidate_sets = [self._index.get(t, set()) for t in tokens]
                if not candidate_sets:
                    return []
                ids = set.intersection(*candidate_sets)
                records = [self._records[rid] for rid in ids if rid in self._records]
            records.sort(key=lambda r: r.ts_ns, reverse=True)
            return records[:limit]
        except Exception as exc:
            _logger.debug("index.search error: %s", exc)
            return []

    def search_any(self, keywords: list[str], limit: int = 20) -> list[MemoryRecord]:
        """Return records matching ANY keyword (OR semantics)."""
        if not keywords:
            return []
        try:
            tokens = [kw.lower() for kw in keywords if len(kw) >= 3]
            with self._lock:
                ids: set[str] = set()
                for t in tokens:
                    ids.update(self._index.get(t, set()))
                records = [self._records[rid] for rid in ids if rid in self._records]
            records.sort(key=lambda r: r.ts_ns, reverse=True)
            return records[:limit]
        except Exception as exc:
            _logger.debug("index.search_any error: %s", exc)
            return []

    def snapshot(self) -> dict:
        with self._lock:
            return {
                "active": True,
                "indexed_records": len(self._records),
                "token_count": len(self._index),
                "total_indexed": self._total,
                "temporal_buckets": len(self._temporal_index),
                "semantic_concepts": len(self._semantic_index),
                "conflict_groups": len(self._conflict_index),
                "sources": len(self._source_index),
                "kinds": len(self._kind_index),
            }

    # ------------------------------------------------------------------
    # Enhanced M-1 Knowledge Layer Search Methods
    # ------------------------------------------------------------------

    def search_temporal(self, start_ns: int, end_ns: int, limit: int = 20) -> list[MemoryRecord]:
        """Search records by temporal range for knowledge evolution tracking.

        Args:
            start_ns: Start timestamp in nanoseconds
            end_ns: End timestamp in nanoseconds
            limit: Maximum number of records to return

        Returns:
            Records within the temporal range, sorted by timestamp
        """
        if start_ns >= end_ns:
            return []

        try:
            start_bucket = self._quantize_timestamp(start_ns)
            end_bucket = self._quantize_timestamp(end_ns)

            with self._lock:
                candidate_ids: set[str] = set()
                for bucket in range(start_bucket, end_bucket + 1):
                    candidate_ids.update(self._temporal_index.get(bucket, set()))

                records = [
                    self._records[rid]
                    for rid in candidate_ids
                    if rid in self._records and start_ns <= self._records[rid].ts_ns <= end_ns
                ]

            records.sort(key=lambda r: r.ts_ns, reverse=True)
            return records[:limit]
        except Exception as exc:
            _logger.debug("index.search_temporal error: %s", exc)
            return []

    def search_semantic(self, concepts: list[str], limit: int = 20) -> list[MemoryRecord]:
        """Search records by semantic concepts for concept-based retrieval.

        Args:
            concepts: List of semantic concepts to search for
            limit: Maximum number of records to return

        Returns:
            Records containing the semantic concepts, sorted by confidence
        """
        if not concepts:
            return []

        try:
            normalized_concepts = [c.lower() for c in concepts if len(c) >= 3]
            if not normalized_concepts:
                return []

            with self._lock:
                candidate_sets = [self._semantic_index.get(c, set()) for c in normalized_concepts]
                if not candidate_sets:
                    return []
                ids = set.intersection(*candidate_sets)
                records = [self._records[rid] for rid in ids if rid in self._records]

            # Sort by confidence for semantic results
            records.sort(key=lambda r: r.confidence, reverse=True)
            return records[:limit]
        except Exception as exc:
            _logger.debug("index.search_semantic error: %s", exc)
            return []

    def search_conflict_group(self, conflict_group: str, limit: int = 20) -> list[MemoryRecord]:
        """Search records by conflict group for source dispute resolution.

        Args:
            conflict_group: Conflict group identifier
            limit: Maximum number of records to return

        Returns:
            Records belonging to the conflict group
        """
        if not conflict_group:
            return []

        try:
            with self._lock:
                ids = self._conflict_index.get(conflict_group, set())
                records = [self._records[rid] for rid in ids if rid in self._records]

            records.sort(key=lambda r: r.ts_ns, reverse=True)
            return records[:limit]
        except Exception as exc:
            _logger.debug("index.search_conflict_group error: %s", exc)
            return []

    def search_by_source(self, source: str, limit: int = 20) -> list[MemoryRecord]:
        """Search records by source for source-aware retrieval.

        Args:
            source: Source identifier to search for
            limit: Maximum number of records to return

        Returns:
            Records from the specified source
        """
        if not source:
            return []

        try:
            with self._lock:
                ids = self._source_index.get(source.lower(), set())
                records = [self._records[rid] for rid in ids if rid in self._records]

            records.sort(key=lambda r: r.ts_ns, reverse=True)
            return records[:limit]
        except Exception as exc:
            _logger.debug("index.search_by_source error: %s", exc)
            return []

    def search_by_kind(self, kind: str, limit: int = 20) -> list[MemoryRecord]:
        """Search records by MemoryKind for type-based retrieval.

        Args:
            kind: MemoryKind to search for
            limit: Maximum number of records to return

        Returns:
            Records of the specified MemoryKind
        """
        if not kind:
            return []

        try:
            with self._lock:
                ids = self._kind_index.get(kind.upper(), set())
                records = [self._records[rid] for rid in ids if rid in self._records]

            records.sort(key=lambda r: r.ts_ns, reverse=True)
            return records[:limit]
        except Exception as exc:
            _logger.debug("index.search_by_kind error: %s", exc)
            return []

    def search_hybrid(
        self,
        keywords: list[str] | None = None,
        concepts: list[str] | None = None,
        source: str | None = None,
        kind: str | None = None,
        start_ns: int | None = None,
        end_ns: int | None = None,
        limit: int = 20,
    ) -> list[MemoryRecord]:
        """Hybrid search combining multiple search criteria.

        Args:
            keywords: Optional keywords for traditional search
            concepts: Optional concepts for semantic search
            source: Optional source filter
            kind: Optional MemoryKind filter
            start_ns: Optional start timestamp for temporal filter
            end_ns: Optional end timestamp for temporal filter
            limit: Maximum number of records to return

        Returns:
            Records matching all specified criteria, sorted by relevance
        """
        try:
            candidate_sets: list[set[str]] = []

            with self._lock:
                # Keyword search
                if keywords:
                    tokens = [kw.lower() for kw in keywords if len(kw) >= 3]
                    if tokens:
                        keyword_sets = [self._index.get(t, set()) for t in tokens]
                        if keyword_sets:
                            candidate_sets.append(set.intersection(*keyword_sets))

                # Semantic search
                if concepts:
                    normalized_concepts = [c.lower() for c in concepts if len(c) >= 3]
                    if normalized_concepts:
                        concept_sets = [
                            self._semantic_index.get(c, set()) for c in normalized_concepts
                        ]
                        if concept_sets:
                            candidate_sets.append(set.intersection(*concept_sets))

                # Source filter
                if source:
                    candidate_sets.append(self._source_index.get(source.lower(), set()))

                # Kind filter
                if kind:
                    candidate_sets.append(self._kind_index.get(kind.upper(), set()))

                # Temporal filter
                if start_ns is not None or end_ns is not None:
                    if start_ns is not None and end_ns is not None:
                        start_bucket = self._quantize_timestamp(start_ns)
                        end_bucket = self._quantize_timestamp(end_ns)
                        temporal_ids: set[str] = set()
                        for bucket in range(start_bucket, end_bucket + 1):
                            temporal_ids.update(self._temporal_index.get(bucket, set()))

                        # Filter by exact timestamp range
                        temporal_ids = {
                            rid
                            for rid in temporal_ids
                            if rid in self._records
                            and start_ns <= self._records[rid].ts_ns <= end_ns
                        }
                        candidate_sets.append(temporal_ids)

                # Intersect all candidate sets
                if candidate_sets:
                    ids = set.intersection(*candidate_sets)
                else:
                    ids = set(self._records.keys())

                records = [self._records[rid] for rid in ids if rid in self._records]

            # Sort by combined relevance (timestamp + confidence)
            records.sort(key=lambda r: (r.confidence, r.ts_ns), reverse=True)
            return records[:limit]
        except Exception as exc:
            _logger.debug("index.search_hybrid error: %s", exc)
            return []

    # ------------------------------------------------------------------
    # Private helper methods for enhanced indexing
    # ------------------------------------------------------------------

    def _extract_concepts(self, record: MemoryRecord) -> list[str]:
        """Extract semantic concepts from a memory record.

        This method analyzes the record's summary, tags, and body
        to identify key concepts for semantic indexing.
        """
        concepts: list[str] = []

        # Extract from tags
        concepts.extend([t.lower() for t in record.tags if len(t) >= 3])

        # Extract from summary
        summary_concepts = _tokenize(record.summary)
        concepts.extend(summary_concepts)

        # Extract from body if available
        for key, value in record.body.items():
            if len(key) >= 3:
                concepts.append(key.lower())
            if len(value) >= 3:
                concepts.extend(_tokenize(value))

        # Remove duplicates and return
        return list(set(concepts))

    def _quantize_timestamp(self, timestamp_ns: int) -> int:
        """Quantize timestamp into buckets for temporal indexing.

        This groups timestamps into buckets for efficient temporal range queries.
        Current implementation uses 1-hour buckets (3.6e12 nanoseconds).
        """
        bucket_size_ns = 3_600_000_000_000  # 1 hour in nanoseconds
        return timestamp_ns // bucket_size_ns


# Alias for backward compatibility
MemoryIndex = MemoryIndexAuthority

_singleton: MemoryIndexAuthority | None = None
_lock = threading.Lock()


def get_memory_index() -> MemoryIndexAuthority:
    global _singleton
    if _singleton is None:
        with _lock:
            if _singleton is None:
                _singleton = MemoryIndexAuthority()
    return _singleton


__all__ = ["MemoryIndexAuthority", "MemoryIndex", "get_memory_index"]
