"""Focus Policy - determines what gets cognitive attention."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from cognitive_engine.attention_engine.priority import AttentionPriority, AttentionWeight


@dataclass
class FocusTarget:
    """A target for cognitive attention."""

    target_id: str
    domain: str
    priority: AttentionPriority
    score: float = 0.0
    rationale: str = ""
    metadata: dict[str, Any] = field(default_factory=dict)


class FocusPolicy:
    """Policy for allocating attention across cognitive targets.

    Scores are computed based on:
    - Opportunity: Potential for alpha generation
    - Risk: Potential for loss or failure
    - Novelty: How unexpected/unfamiliar the situation
    - Uncertainty: Confidence level (low confidence = high uncertainty)
    """

    def __init__(self, weight: AttentionWeight | None = None) -> None:
        self._weight = weight or AttentionWeight()
        self._max_targets = 100
        self._allocated: dict[str, FocusTarget] = {}

    def allocate(
        self,
        target_id: str,
        domain: str,
        opportunity: float,
        risk: float,
        novelty: float,
        uncertainty: float,
        rationale: str = "",
    ) -> FocusTarget:
        """Allocate attention to a target."""
        raw_score = (
            opportunity * self._weight.opportunity
            + risk * self._weight.risk
            + novelty * self._weight.novelty
            + uncertainty * self._weight.uncertainty
        )
        # Normalize to 0-1 range
        score = min(1.0, raw_score / 4.0)

        priority = self._determine_priority(score)

        target = FocusTarget(
            target_id=target_id,
            domain=domain,
            priority=priority,
            score=score,
            rationale=rationale,
            metadata={
                "opportunity": opportunity,
                "risk": risk,
                "novelty": novelty,
                "uncertainty": uncertainty,
            },
        )
        self._allocated[target_id] = target
        return target

    def _determine_priority(self, score: float) -> AttentionPriority:
        """Determine priority level from score."""
        if score >= 0.8:
            return AttentionPriority.CRITICAL
        if score >= 0.6:
            return AttentionPriority.HIGH
        if score >= 0.4:
            return AttentionPriority.MEDIUM
        return AttentionPriority.LOW

    def get_targets(self, min_priority: AttentionPriority | None = None) -> list[FocusTarget]:
        """Get allocated targets, optionally filtered by priority."""
        targets = list(self._allocated.values())
        if min_priority is not None:
            targets = [t for t in targets if t.priority >= min_priority]
        return sorted(targets, key=lambda t: t.score, reverse=True)

    def top_targets(self, n: int = 10) -> list[FocusTarget]:
        """Get top N targets by attention score."""
        return self.get_targets()[:n]

    def refresh(self, target_id: str) -> FocusTarget | None:
        """Refresh a target's timestamp and return it."""
        if target_id in self._allocated:
            # In a real implementation, this would update last_accessed
            return self._allocated[target_id]
        return None