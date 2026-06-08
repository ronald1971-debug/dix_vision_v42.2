"""Knowledge Acquisition – builds and maintains INDIRA's knowledge base.

Knowledge is derived from validated observations and represents
persistent understanding that outlives individual observations.
"""

from __future__ import annotations

import time
import uuid
from dataclasses import dataclass, field
from typing import Any


@dataclass
class KnowledgeItem:
    item_id: str = field(default_factory=lambda: uuid.uuid4().hex[:12])
    category: str = ""  # market_structure | correlation | pattern | anomaly
    key: str = ""
    value: Any = None
    confidence: float = 0.0
    source_observations: list[str] = field(default_factory=list)
    created_at: float = field(default_factory=time.time)
    last_updated: float = field(default_factory=time.time)
    access_count: int = 0
    metadata: dict[str, Any] = field(default_factory=dict)


class KnowledgeBase:
    """INDIRA's long-term knowledge store."""

    def __init__(self) -> None:
        self._items: dict[str, KnowledgeItem] = {}
        self._index_by_category: dict[str, list[str]] = {}
        self._index_by_key: dict[str, str] = {}

    def acquire(
        self,
        category: str,
        key: str,
        value: Any,
        confidence: float = 0.5,
        source_observations: list[str] | None = None,
    ) -> KnowledgeItem:
        existing_id = self._index_by_key.get(f"{category}:{key}")
        if existing_id and existing_id in self._items:
            item = self._items[existing_id]
            item.value = value
            item.confidence = max(0.0, min(1.0, confidence))
            item.last_updated = time.time()
            if source_observations:
                item.source_observations.extend(source_observations)
            return item

        item = KnowledgeItem(
            category=category,
            key=key,
            value=value,
            confidence=max(0.0, min(1.0, confidence)),
            source_observations=source_observations or [],
        )
        self._items[item.item_id] = item
        self._index_by_key[f"{category}:{key}"] = item.item_id

        if category not in self._index_by_category:
            self._index_by_category[category] = []
        self._index_by_category[category].append(item.item_id)

        return item

    def query(self, category: str | None = None, key: str | None = None) -> list[KnowledgeItem]:
        if key and category:
            item_id = self._index_by_key.get(f"{category}:{key}")
            if item_id and item_id in self._items:
                item = self._items[item_id]
                item.access_count += 1
                return [item]
            return []

        if category:
            ids = self._index_by_category.get(category, [])
            items = [self._items[i] for i in ids if i in self._items]
            for item in items:
                item.access_count += 1
            return items

        result = list(self._items.values())
        for item in result:
            item.access_count += 1
        return result

    def consolidate(self, min_confidence: float = 0.3) -> int:
        to_remove = [
            iid for iid, item in self._items.items() if item.confidence < min_confidence
        ]
        for iid in to_remove:
            item = self._items.pop(iid)
            cat_key = f"{item.category}:{item.key}"
            self._index_by_key.pop(cat_key, None)
            cat_ids = self._index_by_category.get(item.category, [])
            if iid in cat_ids:
                cat_ids.remove(iid)
        return len(to_remove)

    @property
    def item_count(self) -> int:
        return len(self._items)
