"""Alternative Data Engine — fuses news, sentiment, macro, and social data.

Provides context for intelligence layer (TIS Section 9).
All inputs are structured and ledgered; no raw ingestion into trading path.
"""

from __future__ import annotations

from collections import deque
from dataclasses import dataclass
from typing import Protocol


@dataclass(frozen=True, slots=True)
class MacroData:
    indicator: str
    value: float
    ts_ns: int
    source: str
    confidence: float = 1.0


@dataclass(frozen=True, slots=True)
class NewsEvent:
    headline: str
    body: str
    ts_ns: int
    source: str
    sentiment_score: float
    impact_score: float
    symbols_mentioned: tuple[str, ...] = ()


@dataclass(frozen=True, slots=True)
class SocialSignal:
    platform: str
    author: str
    content: str
    ts_ns: int
    sentiment_score: float
    engagement_score: float
    symbols_mentioned: tuple[str, ...] = ()


@dataclass(frozen=True, slots=True)
class SocialBatch:
    symbol: str
    ts_ns: int
    avg_sentiment: float
    total_engagement: float
    signal_count: int
    bullish_ratio: float
    bearish_ratio: float


@dataclass(frozen=True, slots=True)
class AltDataContext:
    ts_ns: int
    macro_snapshot: tuple[MacroData, ...] = ()
    news_snapshot: tuple[NewsEvent, ...] = ()
    social_snapshots: tuple[SocialBatch, ...] = ()
    composite_sentiment: float = 0.0


class MacroProvider(Protocol):
    def get_latest(self) -> list[MacroData]: ...


class NewsProvider(Protocol):
    def get_recent(self, hours: int = 24) -> list[NewsEvent]: ...


class SocialProvider(Protocol):
    def get_recent(self, symbols: list[str] | None = None) -> list[SocialSignal]: ...


class AltDataEngine:
    def __init__(
        self,
        *,
        macro_provider: MacroProvider | None = None,
        news_provider: NewsProvider | None = None,
        social_provider: SocialProvider | None = None,
    ) -> None:
        self._macro = macro_provider
        self._news = news_provider
        self._social = social_provider
        self._history: deque[AltDataContext] = deque(maxlen=10000)

    def refresh(self, ts_ns: int) -> AltDataContext:
        macro_data: tuple[MacroData, ...] = ()
        if self._macro is not None:
            macro_data = tuple(self._macro.get_latest())
        news_data: tuple[NewsEvent, ...] = ()
        if self._news is not None:
            news_data = tuple(self._news.get_recent(hours=24))
        social_data: tuple[SocialSignal, ...] = ()
        if self._social is not None:
            social_data = tuple(self._social.get_recent())
        social_batches = self._aggregate_social(social_data, ts_ns)
        composite = self._compute_composite_sentiment(news_data, social_batches)
        context = AltDataContext(
            ts_ns=ts_ns,
            macro_snapshot=macro_data,
            news_snapshot=news_data,
            social_snapshots=social_batches,
            composite_sentiment=composite,
        )
        self._history.append(context)
        return context

    def _aggregate_social(
        self, signals: tuple[SocialSignal, ...], ts_ns: int
    ) -> tuple[SocialBatch, ...]:
        by_symbol: dict[str, list[SocialSignal]] = {}
        for sig in signals:
            for sym in sig.symbols_mentioned or ["GENERAL"]:
                by_symbol.setdefault(sym, []).append(sig)
        batches: list[SocialBatch] = []
        for sym, symsigs in sorted(by_symbol.items()):
            if not symsigs:
                continue
            total_eng = sum(s.engagement_score for s in symsigs)
            bullish = sum(1 for s in symsigs if s.sentiment_score > 0.1)
            bearish = sum(1 for s in symsigs if s.sentiment_score < -0.1)
            total = len(symsigs)
            avg_sent = sum(s.sentiment_score for s in symsigs) / max(total, 1)
            batches.append(
                SocialBatch(
                    symbol=sym,
                    ts_ns=ts_ns,
                    avg_sentiment=avg_sent,
                    total_engagement=total_eng,
                    signal_count=total,
                    bullish_ratio=bullish / max(total, 1),
                    bearish_ratio=bearish / max(total, 1),
                )
            )
        return tuple(batches)

    def _compute_composite_sentiment(
        self, news: tuple[NewsEvent, ...], social: tuple[SocialBatch, ...]
    ) -> float:
        news_sent = 0.0
        if news:
            news_sent = sum(e.sentiment_score * e.impact_score for e in news) / len(news)
        social_sent = 0.0
        if social:
            social_sent = sum(b.avg_sentiment * b.total_engagement for b in social) / sum(
                b.total_engagement for b in social
            )
        return (news_sent * 0.3 + social_sent * 0.7) * 0.5

    def get_context_for_symbol(self, symbol: str, ts_ns: int) -> AltDataContext | None:
        for ctx in reversed(self._history):
            for batch in ctx.social_snapshots:
                if batch.symbol == symbol:
                    return ctx
        return None


__all__ = [
    "AltDataContext",
    "AltDataEngine",
    "MacroData",
    "MacroProvider",
    "NewsEvent",
    "NewsProvider",
    "SocialBatch",
    "SocialProvider",
    "SocialSignal",
]
