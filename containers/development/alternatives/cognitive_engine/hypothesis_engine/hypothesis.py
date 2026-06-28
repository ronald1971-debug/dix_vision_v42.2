"""Hypothesis - data structures for hypothesis management."""

from __future__ import annotations

import time
from dataclasses import dataclass, field
from enum import Enum
from typing import Any


class HypothesisStatus(Enum):
    """Status of a hypothesis in the lifecycle."""

    PROPOSED = "proposed"
    TESTING = "testing"
    VALIDATED = "validated"
    INVALIDATED = "invalidated"
    LEARNED_FROM = "learned_from"


@dataclass
class Hypothesis:
    """A testable hypothesis about market behavior."""

    hypothesis_id: str = field(default_factory=lambda: f"hyp_{time.time_ns()}")
    statement: str = ""
    domain: str = ""
    evidence: tuple[str, ...] = ()
    status: HypothesisStatus = HypothesisStatus.PROPOSED
    confidence: float = 0.5
    created_at: int = field(default_factory=lambda: time.time_ns())
    tested_at: int | None = None
    validated_at: int | None = None
    invalidated_at: int | None = None
    support_score: float = 0.0
    contradiction_score: float = 0.0
    metadata: dict[str, Any] = field(default_factory=dict)

    def add_evidence(self, evidence: str) -> None:
        """Add supporting evidence."""
        self.evidence = (*self.evidence, evidence)

    def update_support(self, score: float) -> None:
        """Update support score."""
        self.support_score = max(self.support_score, score)

    def update_contradiction(self, score: float) -> None:
        """Update contradiction score."""
        self.contradiction_score = max(self.contradiction_score, score)

    def transition_to_testing(self) -> None:
        """Move hypothesis to testing phase."""
        self.status = HypothesisStatus.TESTING
        self.tested_at = time.time_ns()

    def validate(self) -> None:
        """Mark hypothesis as validated."""
        self.status = HypothesisStatus.VALIDATED
        self.confidence = min(1.0, self.confidence + 0.1)
        self.validated_at = time.time_ns()

    def invalidate(self) -> None:
        """Mark hypothesis as invalidated."""
        self.status = HypothesisStatus.INVALIDATED
        self.confidence = max(0.0, self.confidence - 0.1)
        self.invalidated_at = time.time_ns()

    def learn(self) -> None:
        """Mark hypothesis as learned from."""
        self.status = HypothesisStatus.LEARNED_FROM


@dataclass
class HypothesisResult:
    """Result of testing a hypothesis."""

    hypothesis_id: str
    validated: bool
    confidence: float
    evidence_gathered: tuple[str, ...] = ()
    insights: tuple[str, ...] = ()
