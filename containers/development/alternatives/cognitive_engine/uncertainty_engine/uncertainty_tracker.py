"""Uncertainty Tracker - maintains explicit knowledge state categories.

Example:
    Market direction:
        confidence: 0.85 (Known)

    Liquidity conditions:
        confidence: 0.82 (Known)

    Macro catalyst:
        UNKNOWN (Known Unknown)
"""

from __future__ import annotations

import time
from dataclasses import dataclass, field
from enum import Enum
from typing import Any


class KnowledgeType(Enum):
    """Three categories of knowledge states."""

    KNOWN = "known"
    KNOWN_UNKNOWN = "known_unknown"
    UNKNOWN_UNKNOWN = "unknown_unknown"


@dataclass(frozen=True, slots=True)
class KnowledgeState:
    """A knowledge state entry with confidence and category."""

    domain: str
    knowledge_type: KnowledgeType
    confidence: float = 1.0
    evidence: tuple[str, ...] = ()
    last_updated: int = field(default_factory=lambda: time.time_ns())
    metadata: dict[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        if not 0.0 <= self.confidence <= 1.0:
            raise ValueError(f"confidence must be between 0 and 1, got {self.confidence}")


@dataclass
class UncertaintyMetrics:
    """Aggregated uncertainty metrics for a domain."""

    known_count: int = 0
    known_unknown_count: int = 0
    unknown_unknown_count: int = 0
    avg_confidence_known: float = 0.0


class UncertaintyTracker:
    """Tracks knowledge states to prevent overconfidence.

    Maintains three explicit categories:
    - Known: Confirmed knowledge with measurable confidence
    - Known Unknown: Recognized gaps or missing information
    - Unknown Unknown: Detected blind spots via anomaly detection
    """

    def __init__(self) -> None:
        self._states: dict[str, KnowledgeState] = {}
        self._by_type: dict[KnowledgeType, list[str]] = {
            KnowledgeType.KNOWN: [],
            KnowledgeType.KNOWN_UNKNOWN: [],
            KnowledgeType.UNKNOWN_UNKNOWN: [],
        }
        self._domain_index: dict[str, list[str]] = {}

    def track(
        self,
        domain: str,
        knowledge_type: KnowledgeType,
        confidence: float,
        evidence: str | tuple[str, ...] = (),
    ) -> None:
        """Record a knowledge state."""
        if isinstance(evidence, str):
            evidence = (evidence,)

        state = KnowledgeState(
            domain=domain,
            knowledge_type=knowledge_type,
            confidence=confidence,
            evidence=evidence,
        )
        self._states[domain] = state

        if domain not in self._by_type[knowledge_type]:
            self._by_type[knowledge_type].append(domain)
        if domain not in self._domain_index.get(knowledge_type.value, []):
            self._domain_index.setdefault(knowledge_type.value, []).append(domain)

    def mark_known(
        self, domain: str, confidence: float, evidence: str | tuple[str, ...] = ()
    ) -> None:
        """Mark a domain as having confirmed knowledge."""
        self.track(domain, KnowledgeType.KNOWN, confidence, evidence)

    def mark_known_unknown(self, domain: str, evidence: str | tuple[str, ...] = ()) -> None:
        """Mark a recognized knowledge gap."""
        self.track(domain, KnowledgeType.KNOWN_UNKNOWN, 0.0, evidence)

    def mark_unknown_unknown(self, domain: str, evidence: str | tuple[str, ...] = ()) -> None:
        """Mark a detected blind spot."""
        self.track(domain, KnowledgeType.UNKNOWN_UNKNOWN, 0.0, evidence)

    def get_state(self, domain: str) -> KnowledgeState | None:
        """Get the knowledge state for a domain."""
        return self._states.get(domain)

    def get_by_type(self, knowledge_type: KnowledgeType) -> list[KnowledgeState]:
        """Get all states of a given knowledge type."""
        return [self._states[d] for d in self._by_type[knowledge_type] if d in self._states]

    def get_metrics(self) -> UncertaintyMetrics:
        """Get aggregated uncertainty metrics."""
        known_states = self.get_by_type(KnowledgeType.KNOWN)
        if known_states:
            avg_conf = sum(s.confidence for s in known_states) / len(known_states)
        else:
            avg_conf = 0.0

        return UncertaintyMetrics(
            known_count=len(self._by_type[KnowledgeType.KNOWN]),
            known_unknown_count=len(self._by_type[KnowledgeType.KNOWN_UNKNOWN]),
            unknown_unknown_count=len(self._by_type[KnowledgeType.UNKNOWN_UNKNOWN]),
            avg_confidence_known=avg_conf,
        )

    def uncertainty_ratio(self) -> float:
        """Ratio of unknown states to total states (higher = more uncertainty)."""
        total = len(self._states)
        if total == 0:
            return 0.0
        unknown = len(self._by_type[KnowledgeType.KNOWN_UNKNOWN]) + len(
            self._by_type[KnowledgeType.UNKNOWN_UNKNOWN]
        )
        return unknown / total

    def list_unknown_unknowns(self) -> list[str]:
        """Get list of detected blind spots for investigation."""
        return list(self._by_type[KnowledgeType.UNKNOWN_UNKNOWN])
