"""Memory Indexing – persistent memory for the learning engine.

Indexes and retrieves past experiences for pattern recognition.
"""

from __future__ import annotations

import time
from dataclasses import dataclass, field
from typing import Any


@dataclass
class MemoryEntry:
    memory_id: str = ""
    category: str = ""  # trade | error | regime_change | belief_shift
    summary: str = ""
    details: dict[str, Any] = field(default_factory=dict)
    importance: float = 0.5
    access_count: int = 0
    created_at: float = field(default_factory=time.time)
    last_accessed: float = field(default_factory=time.time)


class MemoryIndex:
    """Indexed memory store for experiential learning."""

    def __init__(self, max_entries: int = 10000) -> None:
        self._entries: dict[str, MemoryEntry] = {}
        self._max_entries = max_entries
        self._category_index: dict[str, list[str]] = {}

    def store(
        self,
        memory_id: str,
        category: str,
        summary: str,
        details: dict[str, Any] | None = None,
        importance: float = 0.5,
    ) -> MemoryEntry:
        entry = MemoryEntry(
            memory_id=memory_id,
            category=category,
            summary=summary,
            details=details or {},
            importance=max(0.0, min(1.0, importance)),
        )
        self._entries[memory_id] = entry

        if category not in self._category_index:
            self._category_index[category] = []
        self._category_index[category].append(memory_id)

        self._evict_if_needed()
        return entry

    def recall(self, memory_id: str) -> MemoryEntry | None:
        entry = self._entries.get(memory_id)
        if entry:
            entry.access_count += 1
            entry.last_accessed = time.time()
        return entry

    def recall_by_category(self, category: str, limit: int = 50) -> list[MemoryEntry]:
        ids = self._category_index.get(category, [])
        entries = [self._entries[mid] for mid in ids if mid in self._entries]
        entries.sort(key=lambda e: e.importance, reverse=True)
        for e in entries[:limit]:
            e.access_count += 1
            e.last_accessed = time.time()
        return entries[:limit]

    def search(self, keyword: str) -> list[MemoryEntry]:
        kw = keyword.lower()
        return [
            e for e in self._entries.values() if kw in e.summary.lower() or kw in e.category.lower()
        ]

    @property
    def entry_count(self) -> int:
        return len(self._entries)

    def _evict_if_needed(self) -> None:
        if len(self._entries) <= self._max_entries:
            return
        sorted_entries = sorted(
            self._entries.values(),
            key=lambda e: (e.importance, e.last_accessed),
        )
        to_remove = sorted_entries[: len(self._entries) - self._max_entries]
        for entry in to_remove:
            self._entries.pop(entry.memory_id, None)
