"""Belief arbitration — decides which belief wins in conflicts.

Arbitration rules:
    1. Higher confidence -> trust
    2. Source authority weighting
    3. Recent observations -> more weight
    4. Consistency history -> weight boost
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum


class ArbitrationRule(StrEnum):
    CONFIDENCE_WEIGHTED = "CONFIDENCE_WEIGHTED"
    SOURCE_AUTHORITY = "SOURCE_AUTHORITY"
    RECENCY_BONUS = "RECENCY_BONUS"
    CONSISTENCY_BOOST = "CONSISTENCY_BOOST"


@dataclass(frozen=True, slots=True)
class ArbitrationContext:
    signal_confidence: float
    trader_confidence: float
    macro_confidence: float
    signal_recency_ns: int
    trader_recency_ns: int
    macro_recency_ns: int
    signal_consistent: bool
    trader_consistent: bool
    macro_consistent: bool


@dataclass(frozen=True, slots=True)
class ArbitrationResult:
    winner: str  # "signal", "trader", "macro"
    belief: str
    effective_confidence: float
    applied_rules: tuple[str, ...]


def arbitrate(context: ArbitrationContext) -> ArbitrationResult:
    """Arbitrate between signal, trader, and macro beliefs.

    Decision logic:
        1. Start with confidence-weighted scores
        2. Apply source authority multipliers
        3. Apply recency bonuses
        4. Apply consistency boosts
    """
    scores = {
        "signal": context.signal_confidence,
        "trader": context.trader_confidence * 1.2,  # Trader models get authority boost
        "macro": context.macro_confidence * 1.1,  # Macro gets slight boost
    }

    now = max(context.signal_recency_ns, context.trader_recency_ns, context.macro_recency_ns)
    recency_half_life = 86400 * 1e9  # 1 day in nanoseconds

    def recency_bonus(age_ns: int) -> float:
        if age_ns <= 0:
            return 1.0
        decay = 0.5 ** (age_ns / recency_half_life)
        return 1.0 + 0.2 * (1 - decay)

    scores["signal"] *= recency_bonus(now - context.signal_recency_ns)
    scores["trader"] *= recency_bonus(now - context.trader_recency_ns)
    scores["macro"] *= recency_bonus(now - context.macro_recency_ns)

    if context.signal_consistent:
        scores["signal"] *= 1.1
    if context.trader_consistent:
        scores["trader"] *= 1.15
    if context.macro_consistent:
        scores["macro"] *= 1.05

    winner = max(scores, key=scores.get)
    beliefs = {
        "signal": (
            "bullish"
            if scores["signal"] > 0.5
            else "bearish" if scores["signal"] < 0.5 else "neutral"
        ),
        "trader": (
            "bullish"
            if scores["trader"] > 0.5
            else "bearish" if scores["trader"] < 0.5 else "neutral"
        ),
        "macro": (
            "bullish"
            if scores["macro"] > 0.5
            else "bearish" if scores["macro"] < 0.5 else "neutral"
        ),
    }

    return ArbitrationResult(
        winner=winner,
        belief=beliefs[winner],
        effective_confidence=scores[winner],
        applied_rules=(
            ArbitrationRule.CONFIDENCE_WEIGHTED,
            ArbitrationRule.SOURCE_AUTHORITY,
            ArbitrationRule.RECENCY_BONUS,
            ArbitrationRule.CONSISTENCY_BOOST,
        ),
    )
