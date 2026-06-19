"""Curiosity Scorer - prioritizes questions for investigation."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any


@dataclass
class CuriosityScore:
    """Score for a potential investigation."""

    novelty: float = 0.0
    impact: float = 0.0
    urgency: float = 0.0
    total: float = 0.0
    rationale: str = ""


class CuriosityScorer:
    """Scores questions for investigation priority.

    Higher scores indicate more worthwhile investigations.
    """

    def __init__(self) -> None:
        self._weights = {
            "novelty": 0.3,
            "impact": 0.4,
            "urgency": 0.3,
        }

    def score(
        self,
        novelty: float,
        impact: float,
        urgency: float,
        rationale: str = "",
    ) -> CuriosityScore:
        """Calculate curiosity score."""
        total = (
            novelty * self._weights["novelty"]
            + impact * self._weights["impact"]
            + urgency * self._weights["urgency"]
        )
        return CuriosityScore(
            novelty=novelty,
            impact=impact,
            urgency=urgency,
            total=total,
            rationale=rationale,
        )

    def score_question(
        self,
        question: str,
        context: dict[str, Any] | None = None,
    ) -> CuriosityScore:
        """Score a question based on context analysis."""
        ctx = context or {}

        # Novelty: how different from known patterns
        novelty = ctx.get("novelty", 0.5)

        # Impact: potential effect on PnL or understanding
        impact = ctx.get("impact", 0.5)

        # Urgency: time-sensitive?
        urgency = ctx.get("urgency", 0.3)

        return self.score(novelty, impact, urgency, f"scored: {question[:50]}")

    def rank(self, scores: list[CuriosityScore]) -> list[tuple[int, CuriosityScore]]:
        """Rank scores in descending order."""
        return list(enumerate(sorted(scores, key=lambda s: s.total, reverse=True), 1))