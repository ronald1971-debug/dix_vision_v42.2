"""Belief consensus — resolves conflicts between competing beliefs.

Example:
    Signal Engine: Bullish
    Trader Model: Bearish
    Macro Model: Neutral
    
    Who wins? This module answers that.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Protocol


class BeliefSource(Protocol):
    def get_belief(self) -> str: ...
    def get_confidence(self) -> float: ...


@dataclass(frozen=True, slots=True)
class BeliefVote:
    source: str
    belief: str  # "bullish", "bearish", "neutral"
    confidence: float  # 0.0 to 1.0


@dataclass(frozen=True, slots=True)
class ConsensusResult:
    winning_belief: str
    confidence: float
    votes: tuple[BeliefVote, ...]
    dissent_count: int
    requires_review: bool  # True if disagreement > threshold


def compute_consensus(votes: tuple[BeliefVote, ...],
                      disagreement_threshold: float = 0.3) -> ConsensusResult:
    """Compute belief consensus from multiple sources.

    Args:
        votes: Belief votes from different sources (signal, trader, macro, etc.)
        disagreement_threshold: Threshold above which human review is required

    Returns:
        ConsensusResult with winning belief, confidence, and review flag
    """
    if not votes:
        return ConsensusResult(
            winning_belief="neutral",
            confidence=0.0,
            votes=(),
            dissent_count=0,
            requires_review=False,
        )

    weighted_votes: dict[str, float] = {}
    total_confidence = 0.0

    for vote in votes:
        weighted_votes[vote.belief] = weighted_votes.get(vote.belief, 0.0) + vote.confidence
        total_confidence += vote.confidence

    if not weighted_votes:
        winning = "neutral"
        confidence = 0.0
    else:
        winning = max(weighted_votes, key=weighted_votes.get)
        confidence = min(1.0, weighted_votes[winning] / total_confidence if total_confidence > 0 else 0.0)

    dissent_count = len([v for v in votes if v.belief != winning])
    max_other_conf = max((weighted_votes.get(b, 0.0) for b in weighted_votes if b != winning), default=0.0)

    requires_review = dissent_count > 0 and max_other_conf > disagreement_threshold

    return ConsensusResult(
        winning_belief=winning,
        confidence=confidence,
        votes=votes,
        dissent_count=dissent_count,
        requires_review=requires_review,
    )