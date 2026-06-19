"""Read-only Kraken public WebSocket adapter (SRC-MARKET-KRAKEN-001).

Streams public market data from Kraken WebSocket API
and converts each frame into a canonical :class:`core.contracts.market.MarketTick`.

Layered split:

* :func:`make_combined_stream_url` — pure URL builder.
* :func:`parse_ticker_frame` — pure frame → ``MarketTick`` projection.
* :class:`KrakenPublicWSPump` — thin async I/O wrapper with reconnect
  + exponential backoff.
* :class:`FeedStatus` — frozen telemetry snapshot.

INV-15: the parser is pure (caller-supplied ``ts_ns``); the pump is
non-deterministic by design (network), but every event it emits is
funneled into the harness via the same code path as ``POST /api/tick``.

Kraken WebSocket API reference:
https://docs.kraken.com/websockets/#message-ticker
"""

from __future__ import annotations

import asyncio
import json
import logging
from collections.abc import (
    AsyncIterable,
    Awaitable,
    Callable,
    Mapping,
    Sequence,
)
from dataclasses import dataclass
from typing import Any, Protocol

from core.contracts.market import MarketTick

LOG = logging.getLogger(__name__)

#: Canonical public WS host (no auth required).
KRAKEN_PUBLIC_WS_BASE = "wss://ws.kraken.com"

#: Default reconnect backoff floor + ceiling (seconds).
DEFAULT_RECONNECT_DELAY_S = 5.0
DEFAULT_RECONNECT_DELAY_MAX_S = 60.0

#: Default symbol set used when the operator hits ``start`` with no body.
#: Kraken uses XBT for Bitcoin in some APIs, but we use BTC for consistency
DEFAULT_SYMBOLS: tuple[str, ...] = ("XBT/USD", "ETH/USD")

#: Venue tag stamped onto every emitted ``MarketTick``.
VENUE_TAG = "KRAKEN"


def make_combined_stream_url(symbols: Sequence[str]) -> str:
    """Build the combined-stream URL for the given symbols.

    Returns ``"{BASE}"`` with subscription sent as first message.
    Kraken uses a subscription message format rather than URL parameters.
    """
    if not symbols:
        raise ValueError("make_combined_stream_url: at least one symbol required")
    cleaned: list[str] = []
    for raw in symbols:
        s = raw.upper().strip()
        if not s:
            raise ValueError(f"make_combined_stream_url: invalid symbol {raw!r}")
        cleaned.append(s)
    return KRAKEN_PUBLIC_WS_BASE


def parse_ticker_frame(
    payload: Mapping[str, Any] | Any,
    *,
    ts_ns: int,
    venue: str = VENUE_TAG,
) -> MarketTick | None:
    """Project one Kraken ticker frame into a :class:`MarketTick`.

    Returns ``None`` (never raises) if ``payload`` is not a recognisable
    ticker frame.
    """
    if not isinstance(payload, Mapping):
        return None

    # Kraken format: {"channelID": 123, "event": "subscriptionStatus", ...}
    # or for ticker: {"channelID": 123, "channel": "ticker", "pair": "XBT/USD", ...}
    channel = payload.get("channel")
    if channel != "ticker":
        return None

    try:
        # Kraken ticker format: [bid, bid_size, ask, ask_size, vwap, last, ...]
        data = payload.get("data", [])
        if not isinstance(data, list) or len(data) < 9:
            return None

        ticker = data[0]  # First element is the ticker array
        if not isinstance(ticker, list) or len(ticker) < 9:
            return None

        symbol = str(payload.get("pair", "")).upper()
        bid = float(ticker[0])
        ask = float(ticker[2])
        last = float(ticker[6])
        volume = float(ticker[8])
    except (KeyError, ValueError, TypeError, IndexError):
        return None

    # Normalize symbol names (Kraken uses XBT, we use BTC for consistency)
    symbol = symbol.replace("XBT", "BTC")

    if not symbol:
        return None
    if bid <= 0 or ask <= 0 or last <= 0:
        return None
    if volume < 0:
        return None

    return MarketTick(
        ts_ns=ts_ns,
        symbol=symbol,
        bid=bid,
        ask=ask,
        last=last,
        volume=volume,
        venue=venue,
    )


class _WSConnection(Protocol):
    """Minimal subset of ``websockets.WebSocketClientProtocol`` we use."""

    def __aiter__(self) -> AsyncIterable[str]:
        ...

    async def close(self) -> None:
        ...


WSConnect = Callable[[str], Awaitable[_WSConnection]]
"""Async URL → connection callable. Production uses ``websockets.connect``."""


async def _default_connect(url: str, symbols: Sequence[str]) -> _WSConnection:
    """Default connector — connects and sends subscription message."""

    import websockets  # local import; heavy dependency

    ws = await websockets.connect(  # type: ignore[return-value]
        url,
        ping_interval=None,
        open_timeout=10,
        close_timeout=5,
    )

    # Subscribe to ticker channels
    subscribe_msg = {
        "event": "subscribe",
        "pair": list(symbols),
        "subscription": {"name": "ticker"},
    }
    await ws.send(json.dumps(subscribe_msg))

    return ws


@dataclass(frozen=True, slots=True)
class FeedStatus:
    """Snapshot of pump health — exposed by ``GET /api/feeds/kraken/status``."""

    running: bool
    symbols: tuple[str, ...]
    url: str
    last_tick_ts_ns: int | None
    ticks_received: int
    errors: int


class KrakenPublicWSPump:
    """Async pump streaming Kraken public ticker frames into a sink.

    The sink callable runs synchronously inside the asyncio loop; for
    cross-thread state mutation use :class:`ui.feeds.runner.FeedRunner`
    which wraps the pump and bridges to the FastAPI sync world.
    """

    def __init__(
        self,
        symbols: Sequence[str],
        sink: Callable[[MarketTick], None],
        *,
        clock_ns: Callable[[], int],
        connect: WSConnect | None = None,
        reconnect_delay_s: float = DEFAULT_RECONNECT_DELAY_S,
        reconnect_delay_max_s: float = DEFAULT_RECONNECT_DELAY_MAX_S,
        venue: str = VENUE_TAG,
    ) -> None:
        if not symbols:
            raise ValueError("KrakenPublicWSPump: at least one symbol required")
        if reconnect_delay_s <= 0:
            raise ValueError("KrakenPublicWSPump: reconnect_delay_s must be positive")
        if reconnect_delay_max_s < reconnect_delay_s:
            raise ValueError(
                "KrakenPublicWSPump: reconnect_delay_max_s must be >= reconnect_delay_s"
            )
        self._symbols: tuple[str, ...] = tuple(s.upper() for s in symbols)
        self._sink = sink
        self._clock_ns = clock_ns
        self._connect = connect if connect is not None else _default_connect
        self._reconnect_delay_s = reconnect_delay_s
        self._reconnect_delay_max_s = reconnect_delay_max_s
        self._venue = venue
        self._url = make_combined_stream_url(symbols)
        self._stop_event = asyncio.Event()
        self._ticks_received = 0
        self._errors = 0
        self._last_tick_ts_ns: int | None = None
        self._running = False

    @property
    def url(self) -> str:
        return self._url

    @property
    def symbols(self) -> tuple[str, ...]:
        return self._symbols

    def status(self) -> FeedStatus:
        return FeedStatus(
            running=self._running,
            symbols=self._symbols,
            url=self._url,
            last_tick_ts_ns=self._last_tick_ts_ns,
            ticks_received=self._ticks_received,
            errors=self._errors,
        )

    def stop(self) -> None:
        """Signal the run loop to exit on its next iteration."""
        self._stop_event.set()

    async def run(self) -> None:
        """Connect → consume → reconnect on error until ``stop()``."""
        self._running = True
        delay = self._reconnect_delay_s
        try:
            while not self._stop_event.is_set():
                conn: _WSConnection | None = None
                try:
                    conn = await self._connect(self._url, self._symbols)
                    LOG.info(
                        "kraken_public_ws: connected url=%s symbols=%s",
                        self._url,
                        ",".join(self._symbols),
                    )
                    delay = self._reconnect_delay_s
                    async for raw in conn:  # type: ignore[union-attr]
                        if self._stop_event.is_set():
                            break
                        self._handle_frame(raw)
                except Exception:  # noqa: BLE001
                    self._errors += 1
                    LOG.exception(
                        "kraken_public_ws: connection failure; reconnecting in %.1fs",
                        delay,
                    )
                finally:
                    if conn is not None:
                        try:
                            await conn.close()
                        except Exception:  # noqa: BLE001
                            pass
                if self._stop_event.is_set():
                    break
                try:
                    await asyncio.wait_for(self._stop_event.wait(), timeout=delay)
                except TimeoutError:
                    pass
                delay = min(delay * 2, self._reconnect_delay_max_s)
        finally:
            self._running = False

    def _handle_frame(self, raw: str | bytes) -> None:
        """Decode + parse + dispatch a single WS frame."""
        if isinstance(raw, (bytes, bytearray)):
            try:
                raw = raw.decode("utf-8")
            except UnicodeDecodeError:
                self._errors += 1
                return
        try:
            payload = json.loads(raw)
        except (json.JSONDecodeError, ValueError):
            self._errors += 1
            return
        tick = parse_ticker_frame(payload, ts_ns=self._clock_ns(), venue=self._venue)
        if tick is None:
            return
        self._ticks_received += 1
        self._last_tick_ts_ns = tick.ts_ns
        try:
            self._sink(tick)
        except Exception:  # noqa: BLE001
            self._errors += 1
            LOG.exception("kraken_public_ws: sink failed")


__all__ = [
    "KRAKEN_PUBLIC_WS_BASE",
    "DEFAULT_RECONNECT_DELAY_S",
    "DEFAULT_RECONNECT_DELAY_MAX_S",
    "DEFAULT_SYMBOLS",
    "VENUE_TAG",
    "make_combined_stream_url",
    "parse_ticker_frame",
    "FeedStatus",
    "KrakenPublicWSPump",
]