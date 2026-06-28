"""Cognitive Versioning — version belief, knowledge, and theory objects."""

from __future__ import annotations

from collections import deque
from dataclasses import dataclass
from typing import Any

from core.ontology.theory import Theory


@dataclass(frozen=True, slots=True)
class TheoryVersionEntry:
    theory_id: str
    version: str = ""
    empirical_support: float = 0.0
    falsified: bool = False
    revision_count: int = 0
    last_updated_ns: int = 0
    notes: str = ""


class CognitiveVersionRegistry:
    """Maintains version history for cognitive objects."""

    def __init__(self) -> None:
        self._lock = _NoOpLock()
        self._theories: dict[str, deque[TheoryVersionEntry]] = {}

    def record_theory_version(self, theory: Theory) -> TheoryVersionEntry:
        existing = self._theories.get(theory.object_id, deque())
        version = f"v{len(existing) + 1}.0.0"
        entry = TheoryVersionEntry(
            theory_id=theory.object_id,
            version=version,
            empirical_support=theory.empirical_support,
            falsified=theory.falsified,
            revision_count=theory.falsification_attempts,
            last_updated_ns=theory.ts_ns,
            notes=theory.theory_name,
        )
        existing.append(entry)
        self._theories[theory.object_id] = existing
        return entry

    def get_theory_history(self, theory_id: str) -> tuple[TheoryVersionEntry, ...]:
        return tuple(self._theories.get(theory_id, ()))

    def latest_theory_version(self, theory_id: str) -> TheoryVersionEntry | None:
        history = self._theories.get(theory_id)
        return history[-1] if history else None


class _NoOpLock:
    def __enter__(self) -> _NoOpLock:
        return self

    def __exit__(self, *_exc: Any) -> None:
        return None


__all__ = [
    "CognitiveVersionRegistry",
    "TheoryVersionEntry",
]
