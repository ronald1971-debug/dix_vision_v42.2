"""Belief System – INDIRA's internal model of market state.

Beliefs are formed from observations and validated knowledge.
They represent what INDIRA currently holds to be true.
"""

from __future__ import annotations

import time
import uuid
from dataclasses import dataclass, field
from typing import Any

from core.mcos_kernel import ConfidenceLevel


@dataclass
class Belief:
    belief_id: str = field(default_factory=lambda: uuid.uuid4().hex[:12])
    category: str = ""  # regime | trend | volatility | correlation | custom
    claim: str = ""
    confidence: float = 0.0
    evidence_ids: list[str] = field(default_factory=list)
    formed_at: float = field(default_factory=time.time)
    last_validated: float = field(default_factory=time.time)
    metadata: dict[str, Any] = field(default_factory=dict)

    @property
    def confidence_level(self) -> ConfidenceLevel:
        if self.confidence >= 0.8:
            return ConfidenceLevel.VERY_HIGH
        if self.confidence >= 0.6:
            return ConfidenceLevel.HIGH
        if self.confidence >= 0.4:
            return ConfidenceLevel.MODERATE
        if self.confidence >= 0.2:
            return ConfidenceLevel.LOW
        return ConfidenceLevel.NONE

    def is_stale(self, max_age_seconds: float = 300.0) -> bool:
        return (time.time() - self.last_validated) > max_age_seconds


class BeliefSystem:
    """Manages INDIRA's beliefs about market state."""

    def __init__(self) -> None:
        self._beliefs: dict[str, Belief] = {}
        self._history: list[Belief] = []

    def form_belief(
        self,
        category: str,
        claim: str,
        confidence: float,
        evidence_ids: list[str] | None = None,
    ) -> Belief:
        belief = Belief(
            category=category,
            claim=claim,
            confidence=max(0.0, min(1.0, confidence)),
            evidence_ids=evidence_ids or [],
        )
        self._beliefs[belief.belief_id] = belief
        self._history.append(belief)
        return belief

    def update_belief(
        self, belief_id: str, new_confidence: float, new_evidence: list[str] | None = None
    ) -> Belief | None:
        belief = self._beliefs.get(belief_id)
        if not belief:
            return None
        belief.confidence = max(0.0, min(1.0, new_confidence))
        belief.last_validated = time.time()
        if new_evidence:
            belief.evidence_ids.extend(new_evidence)
        return belief

    def invalidate_belief(self, belief_id: str) -> bool:
        if belief_id in self._beliefs:
            self._beliefs[belief_id].confidence = 0.0
            del self._beliefs[belief_id]
            return True
        return False

    def get_beliefs(self, category: str | None = None) -> list[Belief]:
        beliefs = list(self._beliefs.values())
        if category:
            beliefs = [b for b in beliefs if b.category == category]
        return sorted(beliefs, key=lambda b: b.confidence, reverse=True)

    def get_regime_belief(self) -> Belief | None:
        regime_beliefs = self.get_beliefs("regime")
        return regime_beliefs[0] if regime_beliefs else None

    def prune_stale(self, max_age_seconds: float = 300.0) -> int:
        stale = [
            bid for bid, b in self._beliefs.items() if b.is_stale(max_age_seconds)
        ]
        for bid in stale:
            del self._beliefs[bid]
        return len(stale)

    @property
    def active_count(self) -> int:
        return len(self._beliefs)
