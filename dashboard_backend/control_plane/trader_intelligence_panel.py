"""Trader Intelligence Dashboard Widgets.

Provides visualization panels for TIS:
- Trader Intelligence Panel
- Pattern Performance Tracker
"""

from __future__ import annotations

from dataclasses import dataclass, field

from intelligence_engine.meta.trader_pattern_selector import (
    TraderPatternSelector,
)
from sensory.web_autolearn.trader_intelligence.contracts import TraderPattern


@dataclass(frozen=True, slots=True)
class TraderIntelligenceSnapshot:
    """Snapshot for Trader Intelligence Panel."""

    trader_counts_by_category: dict[str, int] = field(default_factory=dict)
    pattern_counts_by_regime: dict[str, int] = field(default_factory=dict)
    top_patterns_by_confidence: tuple[TraderPattern, ...] = ()
    recent_patterns_24h: int = 0
    avg_credibility_score: float = 0.0
    ts_ns: int = 0


@dataclass(frozen=True, slots=True)
class PatternPerformance:
    """Performance metrics for a pattern."""

    pattern_id: str
    source_trader_id: str
    uses: int
    win_rate: float
    avg_pnl_bps: float
    sharpe_ratio: float
    last_used_ts_ns: int
    regime_distribution: dict[str, int] = field(default_factory=dict)


@dataclass(frozen=True, slots=True)
class PatternPerformanceSnapshot:
    """Snapshot for Pattern Performance Tracker widget."""

    patterns: tuple[PatternPerformance, ...] = ()
    top_performers: tuple[PatternPerformance, ...] = ()
    declining_patterns: tuple[PatternPerformance, ...] = ()
    ts_ns: int = 0


class TraderIntelligencePanel:
    """Dashboard widget for Trader Intelligence overview."""

    def __init__(self, selector: TraderPatternSelector | None = None) -> None:
        self._selector = selector

    def get_snapshot(
        self,
        patterns: list[TraderPattern],
        ts_ns: int = 0,
    ) -> TraderIntelligenceSnapshot:
        """Generate panel snapshot from available patterns."""
        by_category: dict[str, int] = {}
        for p in patterns:
            cat = p.source_category.value
            by_category[cat] = by_category.get(cat, 0) + 1

        by_regime: dict[str, int] = {}
        for p in patterns:
            for regime in p.context_conditions:
                by_regime[regime] = by_regime.get(regime, 0) + 1

        sorted_patterns = sorted(patterns, key=lambda p: p.confidence, reverse=True)[:10]

        avg_cred = sum(p.credibility_score for p in patterns) / max(len(patterns), 1)

        return TraderIntelligenceSnapshot(
            trader_counts_by_category=by_category,
            pattern_counts_by_regime=by_regime,
            top_patterns_by_confidence=tuple(sorted_patterns),
            recent_patterns_24h=len(patterns),
            avg_credibility_score=avg_cred,
            ts_ns=ts_ns,
        )


class PatternPerformanceTracker:
    """Dashboard widget for pattern performance tracking."""

    def __init__(self) -> None:
        self._performance: dict[str, PatternPerformance] = {}

    def record_pattern_use(
        self,
        pattern_id: str,
        source_trader_id: str,
        pnl_bps: float,
        *,
        regime: str = "UNKNOWN",
        ts_ns: int = 0,
    ) -> None:
        """Record a pattern being used in a trade."""
        if pattern_id in self._performance:
            perf = self._performance[pattern_id]
            new_uses = perf.uses + 1
            new_win_rate = (perf.win_rate * perf.uses + (1.0 if pnl_bps > 0 else 0.0)) / new_uses
            new_avg_pnl = (perf.avg_pnl_bps * perf.uses + pnl_bps) / new_uses
            regimes = dict(perf.regime_distribution)
            regimes[regime] = regimes.get(regime, 0) + 1
            self._performance[pattern_id] = PatternPerformance(
                pattern_id=pattern_id,
                source_trader_id=source_trader_id,
                uses=new_uses,
                win_rate=new_win_rate,
                avg_pnl_bps=new_avg_pnl,
                sharpe_ratio=perf.sharpe_ratio,
                last_used_ts_ns=ts_ns,
                regime_distribution=regimes,
            )
        else:
            self._performance[pattern_id] = PatternPerformance(
                pattern_id=pattern_id,
                source_trader_id=source_trader_id,
                uses=1,
                win_rate=1.0 if pnl_bps > 0 else 0.0,
                avg_pnl_bps=pnl_bps,
                sharpe_ratio=0.0,
                last_used_ts_ns=ts_ns,
                regime_distribution={regime: 1},
            )

    def get_snapshot(self, ts_ns: int = 0) -> PatternPerformanceSnapshot:
        """Get current performance snapshot."""
        patterns = tuple(self._performance.values())
        top = tuple(sorted(patterns, key=lambda p: p.avg_pnl_bps, reverse=True)[:5])
        declining = tuple(
            p for p in patterns if p.win_rate < 0.3 or p.avg_pnl_bps < -5.0
        )
        return PatternPerformanceSnapshot(
            patterns=patterns,
            top_performers=top,
            declining_patterns=declining,
            ts_ns=ts_ns,
        )


__all__ = [
    "TraderIntelligencePanel",
    "TraderIntelligenceSnapshot",
    "PatternPerformance",
    "PatternPerformanceSnapshot",
    "PatternPerformanceTracker",
]