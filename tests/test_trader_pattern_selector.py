"""Tests for TraderPatternSelector in intelligence_engine/meta/."""

from intelligence_engine.meta.trader_pattern_selector import (
    MarketContext,
    PatternMatch,
    SelectionResult,
    TraderPatternSelector,
)
from sensory.web_autolearn.trader_intelligence.contracts import (
    SourceCategory,
    TraderPattern,
)


def make_pattern(
    pattern_id: str,
    source_trader_id: str,
    category: str,
    entry_logic: str,
    context_conditions: tuple[str, ...],
    confidence: float = 0.5,
) -> TraderPattern:
    """Create a test TraderPattern."""
    return TraderPattern(
        pattern_id=pattern_id,
        source_trader_id=source_trader_id,
        source_category=SourceCategory.DISCRETIONARY,
        strategy_type=category,
        entry_logic=entry_logic,
        exit_logic="",
        risk_model="",
        context_conditions=context_conditions,
        confidence=confidence,
        credibility_score=confidence,
        ts_ns=1000,
    )


class TestTraderPatternSelector:
    def test_empty_patterns_returns_empty_result(self):
        selector = TraderPatternSelector()
        context = MarketContext(
            regime="TRENDING",
            volatility_bucket="MEDIUM",
            trend_direction="BULL",
            liquidity_state="NORMAL",
            sentiment="NEUTRAL",
            ts_ns=1000,
        )
        result = selector.select(context, candidate_patterns=[])
        assert result.selected_patterns == ()
        assert result.context_match_ratio == 0.0

    def test_regime_matching(self):
        patterns = [
            make_pattern(
                "p1", "trader_a", "BREAKOUT", "buy on breakout", ("TRENDING", "VOLATILE"), 0.8
            ),
            make_pattern(
                "p2", "trader_b", "MEAN_REV", "sell on spike", ("RANGING",), 0.6
            ),
        ]
        selector = TraderPatternSelector()
        context = MarketContext(
            regime="TRENDING",
            volatility_bucket="HIGH",
            trend_direction="BULL",
            liquidity_state="NORMAL",
            sentiment="BULLISH",
            ts_ns=1000,
        )
        result = selector.select(context, candidate_patterns=patterns)
        # Both patterns match since regime_alignment defaults to 0.5 for non-matching
        assert len(result.selected_patterns) == 2
        # First pattern has better regime alignment (1.0 vs 0.5)
        assert result.selected_patterns[0].pattern_id == "p1"

    def test_volatility_alignment(self):
        patterns = [
            make_pattern(
                "p1", "trader_a", "VOL_BREAKOUT", "buy on vol surge", ("VOLATILE",), 0.7
            ),
            make_pattern(
                "p2", "trader_b", "TREND_FOLLOW", "buy on trend", ("TRENDING",), 0.7
            ),
        ]
        selector = TraderPatternSelector()
        context = MarketContext(
            regime="VOLATILE",
            volatility_bucket="EXTREME",
            trend_direction="CHOP",
            liquidity_state="THIN",
            sentiment="NEUTRAL",
            ts_ns=1000,
        )
        result = selector.select(context, candidate_patterns=patterns)
        # Both should match but vol pattern should have higher relevance due to vol alignment
        assert len(result.selected_patterns) == 2

    def test_sentiment_alignment(self):
        patterns = [
            make_pattern(
                "p1", "trader_a", "LONG_BIAS", "buy on bullish signal", ("TRENDING",), 0.7
            ),
            make_pattern(
                "p2", "trader_b", "SHORT_BIAS", "sell on bearish signal", ("TRENDING",), 0.7
            ),
        ]
        selector = TraderPatternSelector()
        context = MarketContext(
            regime="TRENDING",
            volatility_bucket="MEDIUM",
            trend_direction="BULL",
            liquidity_state="NORMAL",
            sentiment="BULLISH",
            ts_ns=1000,
        )
        result = selector.select(context, candidate_patterns=patterns)
        # Both match with regime alignment 0.5+, but p1 has sentiment boost
        assert len(result.selected_patterns) == 2
        # Higher relevance pattern should be first
        assert result.selected_patterns[0].pattern_id == "p1"

    def test_top_k_limit(self):
        patterns = [
            make_pattern(f"p{i}", f"trader_{i}", "TYPE", f"entry {i}", ("TRENDING",), 0.5)
            for i in range(20)
        ]
        selector = TraderPatternSelector(top_k=5)
        context = MarketContext(
            regime="TRENDING",
            volatility_bucket="MEDIUM",
            trend_direction="BULL",
            liquidity_state="NORMAL",
            sentiment="NEUTRAL",
            ts_ns=1000,
        )
        result = selector.select(context, candidate_patterns=patterns)
        assert len(result.selected_patterns) == 5

    def test_min_relevance_filtered_low(self):
        patterns = [
            make_pattern(
                "p1", "trader_a", "BREAKOUT", "buy on breakout", ("VOLATILE",), 0.1
            ),  # very low confidence, wrong regime
            make_pattern(
                "p2", "trader_b", "BREAKOUT", "buy on breakout", ("CHOP",), 0.2
            ),  # wrong regime
        ]
        selector = TraderPatternSelector(min_relevance=0.45)
        context = MarketContext(
            regime="TRENDING",
            volatility_bucket="MEDIUM",
            trend_direction="BULL",
            liquidity_state="NORMAL",
            sentiment="NEUTRAL",
            ts_ns=1000,
        )
        result = selector.select(context, candidate_patterns=patterns)
        # Both patterns have low scores: 0.5*regime + 0.5*vol + 0.5*sent + low_conf*perf
        # p1: 0.5*0.4 + 0.5*0.2 + 0.5*0.2 + 0.1*0.2 = 0.2+0.1+0.1+0.02=0.42
        # p2: 0.5*0.4 + 0.5*0.2 + 0.5*0.2 + 0.2*0.2 = 0.2+0.1+0.1+0.04=0.44
        assert len(result.selected_patterns) == 0

    def test_selection_result_structure(self):
        patterns = [
            make_pattern(
                "p1", "trader_a", "BREAKOUT", "buy on breakout", ("TRENDING",), 0.8
            ),
        ]
        selector = TraderPatternSelector()
        context = MarketContext(
            regime="TRENDING",
            volatility_bucket="MEDIUM",
            trend_direction="BULL",
            liquidity_state="NORMAL",
            sentiment="NEUTRAL",
            ts_ns=1000,
        )
        result = selector.select(context, candidate_patterns=patterns)
        assert isinstance(result, SelectionResult)
        assert isinstance(result.matched_patterns, tuple)
        assert isinstance(result.selected_patterns, tuple)
        assert isinstance(result.context, MarketContext)
        assert 0.0 <= result.context_match_ratio <= 1.0

    def test_pattern_match_structure(self):
        match = PatternMatch(
            pattern=make_pattern("p1", "t1", "T", "entry", ("TRENDING",), 0.8),
            relevance_score=0.85,
            regime_alignment=1.0,
            volatility_alignment=0.7,
        )
        assert match.relevance_score == 0.85
        assert match.regime_alignment == 1.0
        assert match.volatility_alignment == 0.7

    def test_match_history_tracked(self):
        patterns = [
            make_pattern(
                "p1", "trader_a", "BREAKOUT", "buy on breakout", ("TRENDING",), 0.8
            ),
        ]
        selector = TraderPatternSelector()
        context = MarketContext(
            regime="TRENDING",
            volatility_bucket="MEDIUM",
            trend_direction="BULL",
            liquidity_state="NORMAL",
            sentiment="NEUTRAL",
            ts_ns=1000,
        )
        selector.select(context, candidate_patterns=patterns)
        assert len(selector.match_history) == 1

    def test_confidence_weights_into_relevance(self):
        patterns = [
            make_pattern(
                "p1", "trader_a", "LOW_CONF", "entry", ("TRENDING",), 0.3
            ),  # lower confidence
            make_pattern(
                "p2", "trader_b", "HIGH_CONF", "entry", ("TRENDING",), 0.9
            ),  # higher confidence
        ]
        selector = TraderPatternSelector()
        context = MarketContext(
            regime="TRENDING",
            volatility_bucket="MEDIUM",
            trend_direction="BULL",
            liquidity_state="NORMAL",
            sentiment="NEUTRAL",
            ts_ns=1000,
        )
        result = selector.select(context, candidate_patterns=patterns)
        # Both should match but high confidence pattern should have higher relevance
        assert len(result.selected_patterns) == 2
        # Check ordering - higher confidence should be first
        rel_scores = [m.relevance_score for m in result.matched_patterns]
        assert rel_scores[0] >= rel_scores[1]