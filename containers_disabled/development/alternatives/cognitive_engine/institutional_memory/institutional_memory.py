"""Institutional Memory — long-term strategic memory.

Eventually DIXVISION should remember:
  - Important Discoveries
  - Major Mistakes
  - Successful Evolutions
  - Critical Failures

for years.

(Item 36 from the cognitive operating system roadmap)
"""

from __future__ import annotations

import threading
import time as _time
from collections import deque
from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class MemoryEntry:
    entry_id: str
    category: str
    title: str
    description: str
    significance: float
    ts_ns: int


class InstitutionalMemory:
    """Long-term memory for discoveries, mistakes, evolutions, failures."""

    def __init__(self) -> None:
        self._lock = threading.Lock()
        self._entries: dict[str, deque] = {}
        self._categories = {
            "discovery",
            "mistake",
            "evolution",
            "failure",
        }

    def store(
        self, category: str, title: str, description: str, significance: float
    ) -> MemoryEntry:
        if category not in self._categories:
            category = "discovery"
        eid = f"MEM-{category[:4].upper()}-{_time.time_ns():x}"
        entry = MemoryEntry(
            entry_id=eid,
            category=category,
            title=title,
            description=description,
            significance=significance,
            ts_ns=_now_ns(),
        )
        with self._lock:
            self._entries.setdefault(category, deque(maxlen=5000)).append(entry)
        return entry

    def recall(self, category: str, limit: int = 50) -> list[dict]:
        with self._lock:
            dq = self._entries.get(category, deque())
            items = list(dq)[-limit:]
            return [
                {
                    "entry_id": e.entry_id,
                    "category": e.category,
                    "title": e.title,
                    "description": e.description,
                    "significance": e.significance,
                    "ts_ns": e.ts_ns,
                }
                for e in items
            ]

    def summary(self) -> dict:
        with self._lock:
            cats = {}
            for cat, dq in self._entries.items():
                cats[cat] = len(dq)
            total = sum(cats.values())
            return {
                "total_entries": total,
                "by_category": cats,
                "retention_max": 5000,
                "ts_ns": _now_ns(),
            }


def _now_ns() -> int:
    try:
        from system.time_source import wall_ns

        return wall_ns()
    except Exception:
        return int(_time.time() * 1e9)


_instance: InstitutionalMemory | None = None
_lock = threading.Lock()


def get_institutional_memory() -> InstitutionalMemory:
    global _instance
    if _instance is None:
        with _lock:
            if _instance is None:
                _instance = InstitutionalMemory()
    return _instance


__all__ = [
    "MemoryEntry",
    "InstitutionalMemory",
    "get_institutional_memory",
]
