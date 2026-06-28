"""Alt-data provider implementations.

Concrete providers for the :class:`alt_data_engine.AltDataEngine`
protocol interface.  Each provider is deterministic / pure-Python
and safe to call from the intelligence hot path (no IO beyond
in-memory caches).
"""

from __future__ import annotations

from collections import deque
from dataclasses import dataclass

# ---------------------------------------------------------------------------
# DTOs
# ---------------------------------------------------------------------------


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
    sentiment_score: float  # [-1, 1]
    impact_score: float  # [0, 1]
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


# ---------------------------------------------------------------------------
# Macro feed
# ---------------------------------------------------------------------------


class MacroFeed:
    """In-memory macro-data provider with deterministic updates.

    Maintains a rolling window of economic indicators and exposes
    them through the ``MacroProvider`` protocol so
    :class:`alt_data_engine.AltDataEngine` can consume them.

    The feed is *push-updatable* — callers call :meth:`update_indicator`
    whenever a new value arrives; :meth:`get_latest` returns the
    most recent values within ``lookback`` ticks.
    """

    def __init__(self, *, lookback: int = 64) -> None:
        self._lookback = lookback
        self._history: dict[str, deque[MacroData]] = {}

    def update_indicator(
        self,
        indicator: str,
        value: float,
        ts_ns: int,
        source: str = "macro_feed",
        confidence: float = 1.0,
    ) -> None:
        rec = MacroData(
            indicator=indicator,
            value=value,
            ts_ns=ts_ns,
            source=source,
            confidence=confidence,
        )
        self._history.setdefault(indicator, deque(maxlen=self._lookback)).append(rec)

    def get_latest(self) -> list[MacroData]:
        out: list[MacroData] = []
        for dq in self._history.values():
            if dq:
                out.append(dq[-1])
        return out

    def get_history(self, indicator: str) -> tuple[MacroData, ...]:
        dq = self._history.get(indicator)
        return tuple(dq) if dq else ()

    def regime_signal(self) -> str:
        latest = self.get_latest()
        if not latest:
            return "NEUTRAL"
        rates_up = any(m.indicator.upper().endswith("RATE") and m.value > 0 for m in latest)
        inflation_up = any(
            any(k in m.indicator.upper() for k in ("CPI", "INFLATION")) and m.value > 3.0
            for m in latest
        )
        if rates_up and not inflation_up:
            return "RISK_ON"
        if inflation_up:
            return "RISK_OFF"
        return "NEUTRAL"


# ---------------------------------------------------------------------------
# News parser
# ---------------------------------------------------------------------------


@dataclass(frozen=True, slots=True)
class ParseResult:
    events: tuple[NewsEvent, ...]
    composite_sentiment: float


class NewsParser:
    """Structured news-ingestion helper.

    Accepts raw headline + body strings, applies a vocabulary-based
    sentiment model (no external model required), and emits typed
    :class:`NewsEvent` records.

    Deterministic: same inputs -> identical outputs (INV-15).
    """

    _POSITIVE: frozenset[str] = frozenset(
        {
            "beat",
            "beats",
            "surge",
            "surges",
            "gain",
            "gains",
            "rally",
            "rallies",
            "bullish",
            "upgrade",
            "upgraded",
            "outperform",
            "growth",
            "positive",
            "profit",
            "profits",
        }
    )
    _NEGATIVE: frozenset[str] = frozenset(
        {
            "miss",
            "misses",
            "plunge",
            "plunges",
            "loss",
            "losses",
            "bearish",
            "downgrade",
            "downgraded",
            "underperform",
            "recession",
            "negative",
            "crisis",
            "crash",
            "collapse",
        }
    )
    _IMPACT: frozenset[str] = frozenset(
        {
            "federal",
            "fed",
            "ecb",
            "boj",
            "treasury",
            "inflation",
            "cpi",
            "gdp",
            "employment",
            "nfp",
            "rate",
            "rates",
            "earnings",
            "merger",
            "acquisition",
            "sec",
            "lawsuit",
        }
    )

    def parse(
        self,
        headline: str,
        body: str,
        *,
        ts_ns: int,
        source: str = "news_parser",
        symbols: tuple[str, ...] = (),
    ) -> NewsEvent:
        text = f"{headline} {body}".lower()
        tokens = set(text.split())
        pos_hits = tokens & self._POSITIVE
        neg_hits = tokens & self._NEGATIVE
        denom = max(len(pos_hits) + len(neg_hits), 1)
        score = max(-1.0, min(1.0, (len(pos_hits) - len(neg_hits)) / denom))
        impact_hits = tokens & self._IMPACT
        impact = min(1.0, len(impact_hits) * 0.25 + 0.1)
        return NewsEvent(
            headline=headline,
            body=body,
            ts_ns=ts_ns,
            source=source,
            sentiment_score=score,
            impact_score=impact,
            symbols_mentioned=symbols,
        )

    def parse_batch(
        self,
        items: list[tuple[str, str, tuple[str, ...] | None]],
        *,
        ts_ns: int,
        source: str = "news_parser",
    ) -> ParseResult:
        events: list[NewsEvent] = []
        s_sum = 0.0
        for headline, body, syms in items:
            ev = self.parse(
                headline,
                body,
                ts_ns=ts_ns,
                source=source,
                symbols=tuple(syms) if syms else (),
            )
            events.append(ev)
            s_sum += ev.sentiment_score * ev.impact_score
        composite = (s_sum / len(events)) * 0.5 if events else 0.0
        return ParseResult(events=tuple(events), composite_sentiment=composite)


# ---------------------------------------------------------------------------
# Re-exports for convenience
# ---------------------------------------------------------------------------

__all__ = [
    "MacroData",
    "MacroFeed",
    "NewsEvent",
    "NewsParser",
    "ParseResult",
    "SocialSignal",
]
