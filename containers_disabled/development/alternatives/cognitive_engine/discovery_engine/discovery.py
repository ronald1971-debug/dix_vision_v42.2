"""Discovery Engine — search for unknown opportunities.

Most systems optimize existing knowledge. Few search for unknown opportunities.

Searches for:
  - unknown trader archetypes
  - unknown market structures
  - unknown strategy families

(Discovery — Item 32 from the cognitive operating system roadmap)
"""

from __future__ import annotations

import threading
import time as _time
from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True, slots=True)
class Discovery:
    discovery_id: str
    category: str
    description: str
    confidence: float
    discovered_by: str
    ts_ns: int


class DiscoveryEngine:
    """Search for unknown opportunities."""

    def __init__(self) -> None:
        self._lock = threading.Lock()
        self._discoveries: dict[str, Discovery] = {}
        self._by_category: dict[str, list[str]] = {}
        self._ontology_projections: dict[str, dict[str, Any]] = {}

    def record_discovery(
        self,
        category: str,
        description: str,
        confidence: float,
        discovered_by: str,
    ) -> Discovery:
        did = f"DISC-{_time.time_ns():x}"
        disc = Discovery(
            discovery_id=did,
            category=category,
            description=description,
            confidence=confidence,
            discovered_by=discovered_by,
            ts_ns=_now_ns(),
        )
        with self._lock:
            self._discoveries[did] = disc
            self._by_category.setdefault(category, []).append(did)
            self._ontology_projections[did] = {
                "object_id": did,
                "object_type": category,
                "ts_ns": disc.ts_ns,
                "source": disc.discovered_by,
                "confidence": disc.confidence,
                "description": disc.description,
            }
        return disc

    def get_discoveries(self, category: str | None = None) -> list[dict]:
        with self._lock:
            ids = (
                self._by_category.get(category, []) if category else list(self._discoveries.keys())
            )
        return [self._to_dict(self._discoveries[i]) for i in ids]

    def search(self) -> list[dict]:
        return self.get_discoveries()

    def _to_dict(self, d: Discovery) -> dict:
        return {
            "discovery_id": d.discovery_id,
            "category": d.category,
            "description": d.description,
            "confidence": d.confidence,
            "ts_ns": d.ts_ns,
        }

    def get_ontology_projections(self, category: str | None = None) -> list[dict]:
        with self._lock:
            if category:
                ids = self._by_category.get(category, [])
            else:
                ids = list(self._discoveries.keys())
            return [self._ontology_projections[i] for i in ids if i in self._ontology_projections]

    def report(self) -> dict:
        with self._lock:
            return {
                "total_discoveries": len(self._discoveries),
                "by_category": {k: len(v) for k, v in self._by_category.items()},
                "ts_ns": _now_ns(),
            }


def _now_ns() -> int:
    try:
        from system.time_source import wall_ns

        return wall_ns()
    except Exception:
        return int(_time.time() * 1e9)


_instance: DiscoveryEngine | None = None
_lock = threading.Lock()


def get_discovery_engine() -> DiscoveryEngine:
    global _instance
    if _instance is None:
        with _lock:
            if _instance is None:
                _instance = DiscoveryEngine()
    return _instance


__all__ = [
    "Discovery",
    "DiscoveryEngine",
    "get_discovery_engine",
]
