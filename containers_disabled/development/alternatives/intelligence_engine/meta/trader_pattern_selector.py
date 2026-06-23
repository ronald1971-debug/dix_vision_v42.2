"""Trader Pattern Selector — selects matching trader patterns based on market context.

Part of TIS (Trader Intelligence System) - Section 8.
Matches market state to relevant trader patterns from the knowledge store,
then selects best candidates for strategy synthesis.

Market state flows through → relevant patterns are matched → best candidates
are selected and combined for IndiraIntent emission.
"""

from __future__ import annotations

from collections import deque
from dataclasses import dataclass
from typing import Protocol

from sensory.web_autolearn.trader_intelligence.contracts import TraderPattern


@dataclass(frozen=True, slots=True)
class MarketContext:
    """Current market conditions for pattern matching."""

    regime: str
    volatility_bucket: str  # "LOW", "MEDIUM", "HIGH", "EXTREME"
    trend_direction: str  # "BULL", "BEAR", "FLAT", "CHOP"
    liquidity_state: str  # "DEEP", "NORMAL", "THIN", "STRESSED"
    sentiment: str  # "BULLISH", "BEARISH", "NEUTRAL"
    ts_ns: int


@dataclass(frozen=True, slots=True)
class PatternMatch:
    """A matched pattern with relevance score."""

    pattern: TraderPattern
    relevance_score: float  # [0, 1] how relevant to current context
    regime_alignment: float  # [0, 1] how well pattern fits regime
    volatility_alignment: float  # [0, 1]


@dataclass(frozen=True, slots=True)
class SelectionResult:
    """Output of pattern selection for strategy synthesis."""

    matched_patterns: tuple[PatternMatch, ...]
    selected_patterns: tuple[TraderPattern, ...]
    context: MarketContext
    context_match_ratio: float  # ratio of patterns that matched context


class PatternSource(Protocol):
    """Protocol for pattern storage backends."""

    def get_patterns_by_regime(self, regime: str) -> list[TraderPattern]:
        """Get patterns applicable to a regime."""
        ...

    def get_all_patterns(self) -> list[TraderPattern]:
        """Get all available patterns."""
        ...


class TraderPatternSelector:
    """Selects relevant trader patterns based on market context.

    Flow:
    1. Match patterns to current market context
    2. Rank by relevance score
    3. Select top candidates for strategy synthesis
    """

    def __init__(
        self,
        pattern_source: PatternSource | None = None,
        *,
        top_k: int = 10,
        min_relevance: float = 0.3,
        regime_weight: float = 0.4,
        volatility_weight: float = 0.2,
        sentiment_weight: float = 0.2,
        performance_weight: float = 0.2,
    ) -> None:
        self._pattern_source = pattern_source
        self._top_k = top_k
        self._min_relevance = min_relevance
        self._weights = {
            "regime": regime_weight,
            "volatility": volatility_weight,
            "sentiment": sentiment_weight,
            "performance": performance_weight,
        }
        self._match_history: deque[PatternMatch] = deque(maxlen=1000)

    def select(
        self,
        context: MarketContext,
        *,
        candidate_patterns: list[TraderPattern] | None = None,
    ) -> SelectionResult:
        """Select patterns matching current market context.

        Args:
            context: Current market conditions
            candidate_patterns: Optional pre-filtered patterns; if None,
                pulls from pattern source

        Returns:
            SelectionResult with matched and selected patterns
        """
        candidates = candidate_patterns
        if candidates is None and self._pattern_source is not None:
            candidates = self._pattern_source.get_patterns_by_regime(context.regime)

        if candidates is None:
            candidates = []

        matches: list[PatternMatch] = []
        for pattern in candidates:
            match = self._score_pattern_match(pattern, context)
            if match.relevance_score >= self._min_relevance:
                matches.append(match)

        # Sort by relevance
        matches.sort(key=lambda m: m.relevance_score, reverse=True)

        # Take top-k
        selected = matches[: self._top_k]
        selected_patterns = tuple(m.pattern for m in selected)

        # Record matches
        for m in selected:
            self._match_history.append(m)

        # Compute match ratio
        match_ratio = len(selected) / max(len(candidates), 1)

        return SelectionResult(
            matched_patterns=tuple(matches),
            selected_patterns=selected_patterns,
            context=context,
            context_match_ratio=match_ratio,
        )

    def _score_pattern_match(
        self,
        pattern: TraderPattern,
        context: MarketContext,
    ) -> PatternMatch:
        """Compute relevance score for a pattern in current context."""
        # Regime alignment
        regime_alignment = 1.0 if context.regime in pattern.context_conditions else 0.5

        # Volatility alignment
        vol_alignment = 0.5
        if context.volatility_bucket == "HIGH" and "volatility" in pattern.entry_logic.lower():
            vol_alignment = 0.9
        elif context.volatility_bucket == "LOW" and "trend" in pattern.entry_logic.lower():
            vol_alignment = 0.8

        # Sentiment alignment
        sentiment_alignment = 0.5
        pattern_desc = (pattern.entry_logic + pattern.exit_logic).lower()
        if context.sentiment == "BULLISH" and "long" in pattern_desc:
            sentiment_alignment = 0.8
        elif context.sentiment == "BEARISH" and "short" in pattern_desc:
            sentiment_alignment = 0.8

        # Performance weight from pattern confidence
        performance = pattern.confidence

        # Composite relevance
        relevance = (
            regime_alignment * self._weights["regime"]
            + vol_alignment * self._weights["volatility"]
            + sentiment_alignment * self._weights["sentiment"]
            + performance * self._weights["performance"]
        )

        return PatternMatch(
            pattern=pattern,
            relevance_score=relevance,
            regime_alignment=regime_alignment,
            volatility_alignment=vol_alignment,
        )

    def record_outcome(
        self,
        pattern_id: str,
        *,
        was_profitable: bool,
        pnl_bps: float,
    ) -> None:
        """Record outcome for a matched pattern (for future scoring)."""
        # Implementation would update pattern performance metrics

    @property
    def match_history(self) -> list[PatternMatch]:
        """Historical pattern matches."""
        return list(self._match_history)


__all__ = [
    "MarketContext",
    "PatternMatch",
    "PatternSource",
    "SelectionResult",
    "TraderPatternSelector",
]
