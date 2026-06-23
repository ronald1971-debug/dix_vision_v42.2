"""Concept Formation — learns concepts, not just data.

The highest form of learning.

Instead of learning data, INDIRA learns concepts:
  - Liquidity Trap
  - False Breakout
  - Exhaustion Event
  - Panic Cascade

These become reusable abstractions.

(Item 33 from the cognitive operating system roadmap)
"""

from __future__ import annotations

import threading
import time as _time
from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class Concept:
    concept_id: str
    name: str
    definition: str
    features: tuple[str, ...]
    examples: tuple[str, ...]
    confidence: float
    formed_at: int
    usage_count: int = 0


class ConceptFormationEngine:
    """Learn reusable concepts — not just data points."""

    def __init__(self) -> None:
        self._lock = threading.Lock()
        self._concepts: dict[str, Concept] = {}
        self._by_name: dict[str, str] = {}

    def form_concept(
        self,
        name: str,
        definition: str,
        features: list[str],
        examples: list[str],
        confidence: float = 0.5,
    ) -> Concept:
        cid = f"CONCEPT-{_time.time_ns():x}"
        concept = Concept(
            concept_id=cid,
            name=name,
            definition=definition,
            features=tuple(features),
            examples=tuple(examples),
            confidence=confidence,
            formed_at=_now_ns(),
        )
        with self._lock:
            self._concepts[cid] = concept
            self._by_name[name.lower()] = cid
        return concept

    def get_concept(self, concept_id: str) -> Concept | None:
        with self._lock:
            return self._concepts.get(concept_id)

    def find_by_name(self, name: str) -> Concept | None:
        with self._lock:
            cid = self._by_name.get(name.lower())
            if cid:
                return self._concepts.get(cid)
        return None

    def all_concepts(self) -> dict:
        with self._lock:
            return {
                cid: {
                    "concept_id": c.concept_id,
                    "name": c.name,
                    "definition": c.definition,
                    "features": c.features,
                    "confidence": c.confidence,
                    "usage_count": c.usage_count,
                }
                for cid, c in self._concepts.items()
            }

    def use_concept(self, concept_id: str) -> None:
        with self._lock:
            if concept_id in self._concepts:
                c = self._concepts[concept_id]
                self._concepts[concept_id] = Concept(
                    concept_id=c.concept_id,
                    name=c.name,
                    definition=c.definition,
                    features=c.features,
                    examples=c.examples,
                    confidence=c.confidence,
                    formed_at=c.formed_at,
                    usage_count=c.usage_count + 1,
                )


def _now_ns() -> int:
    try:
        from system.time_source import wall_ns

        return wall_ns()
    except Exception:
        return int(_time.time() * 1e9)


_instance: ConceptFormationEngine | None = None
_lock = threading.Lock()


def get_concept_formation() -> ConceptFormationEngine:
    global _instance
    if _instance is None:
        with _lock:
            if _instance is None:
                _instance = ConceptFormationEngine()
    return _instance


__all__ = [
    "Concept",
    "ConceptFormationEngine",
    "get_concept_formation",
]
