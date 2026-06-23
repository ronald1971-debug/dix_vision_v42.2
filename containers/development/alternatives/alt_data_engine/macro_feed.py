"""Macro-feed provider for the alternative-data engine.

Wraps a concrete ``MacroProvider`` implementation and exposes it
through :class:`alt_data_engine.AltDataEngine`.
"""

from __future__ import annotations

from collections import deque

from alt_data_engine import MacroData


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
