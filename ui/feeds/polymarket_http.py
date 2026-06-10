"""Polymarket HTTP adapter for prediction markets (SRC-ALT-POLYMARKET-001).

Fetches prediction market data from Polymarket and converts it into
canonical prediction market data.

Layered split:

* :func:`fetch_polymarket_markets` — HTTP fetcher for market data.
* :func:`parse_polymarket_market` — pure market → ``PredictionMarket`` projection.
* :class:`PolymarketHTTPPoller` — periodic poller with error handling.
* :class:`FeedStatus` — frozen telemetry snapshot.

INV-15: the parser is pure (caller-supplied ``ts_ns``); the poller
uses HTTP but every event it emits is funneled into the harness.

Polymarket API reference:
https://docs.polymarket.com/
"""

from __future__ import annotations

import asyncio
import logging
from collections.abc import Callable, Mapping, Sequence
from dataclasses import dataclass
from typing import Any

import httpx

LOG = logging.getLogger(__name__)

#: Polymarket API endpoint.
POLYMARKET_URL = "https://clob.polymarket.com"

#: Default poll interval (seconds).
DEFAULT_POLL_INTERVAL_S = 30.0

#: Default market categories to monitor.
DEFAULT_CATEGORIES: tuple[str, ...] = (
    "cryptocurrency",
    "politics",
    "economics",
    "technology",
)

#: Venue tag stamped onto every emitted prediction market.
VENUE_TAG = "POLYMARKET"


def parse_polymarket_market(
    market_data: Mapping[str, Any],
    *,
    ts_ns: int,
    venue: str = VENUE_TAG,
) -> dict[str, Any] | None:
    """Project Polymarket market data into a prediction market structure.

    Returns ``None`` (never raises) if ``market_data`` is malformed.
    """
    try:
        # Polymarket CLOB API format
        market_id = str(market_data.get("market_id", ""))
        question = str(market_data.get("question", ""))
        description = str(market_data.get("description", ""))
        
        # Price and outcome data
        price = float(market_data.get("price", "0"))
        volume = float(market_data.get("volume", "0"))
        
        # Market metadata
        end_time = market_data.get("end_date")
        category = str(market_data.get("category", "general"))
        
        # Outcome information
        outcome_type = str(market_data.get("outcome_type", "binary"))
        
        # Determine market status
        active = market_data.get("active", True)
        
        # Calculate implied probability from price
        if outcome_type == "binary":
            probability = price  # Price is probability for binary markets
        else:
            probability = price * 100  # Rough estimate for other types
        
    except (KeyError, ValueError, TypeError):
        return None

    if not market_id:
        return None
    if not question:
        return None
    if price < 0 or price > 1:
        return None
    if volume < 0:
        return None

    return {
        "ts_ns": ts_ns,
        "source": venue,
        "market_id": market_id,
        "question": question,
        "description": description,
        "category": category,
        "outcome_type": outcome_type,
        "price": price,
        "probability": probability,
        "volume": volume,
        "end_time": end_time,
        "active": active,
    }


async def fetch_polymarket_markets(
    client: httpx.AsyncClient,
    category: str | None = None,
    limit: int = 25,
) -> list[dict[str, Any]] | None:
    """Fetch prediction markets from Polymarket CLOB."""
    
    headers = {
        "User-Agent": "DixVision/1.0 (Market Intelligence System)",
        "Accept": "application/json",
    }

    try:
        # Build query parameters
        params = {"limit": limit}
        if category:
            params["category"] = category

        response = await client.get(
            f"{POLYMARKET_URL}/markets",
            headers=headers,
            params=params,
            timeout=15.0,
        )
        response.raise_for_status()
        data = response.json()
        
        # Parse market data
        markets = data.get("data", [])
        return markets
    except Exception as e:
        LOG.warning(f"Failed to fetch Polymarket markets for category '{category}': {e}")
        return None


@dataclass(frozen=True, slots=True)
class FeedStatus:
    """Snapshot of poller health — exposed by ``GET /api/feeds/polymarket/status``."""

    running: bool
    categories: tuple[str, ...]
    last_tick_ts_ns: int | None
    markets_received: int
    errors: int


class PolymarketHTTPPoller:
    """HTTP poller streaming Polymarket prediction markets into a sink.

    The sink callable runs synchronously; for cross-thread state
    mutation use :class:`ui.feeds.runner.FeedRunner` which wraps
    the poller and bridges to the FastAPI sync world.
    """

    def __init__(
        self,
        categories: Sequence[str],
        sink: Callable[[dict[str, Any]], None],
        *,
        clock_ns: Callable[[], int],
        poll_interval_s: float = DEFAULT_POLL_INTERVAL_S,
        venue: str = VENUE_TAG,
    ) -> None:
        if not categories:
            raise ValueError("PolymarketHTTPPoller: at least one category required")
        if poll_interval_s <= 0:
            raise ValueError("PolymarketHTTPPoller: poll_interval_s must be positive")

        self._categories: tuple[str, ...] = tuple(categories)
        self._sink = sink
        self._clock_ns = clock_ns
        self._poll_interval_s = poll_interval_s
        self._venue = venue
        self._stop_event = asyncio.Event()
        self._markets_received = 0
        self._errors = 0
        self._last_tick_ts_ns: int | None = None
        self._running = False

    @property
    def categories(self) -> tuple[str, ...]:
        return self._categories

    def status(self) -> FeedStatus:
        return FeedStatus(
            running=self._running,
            categories=self._categories,
            last_tick_ts_ns=self._last_tick_ts_ns,
            markets_received=self._markets_received,
            errors=self._errors,
        )

    def stop(self) -> None:
        """Signal the run loop to exit on its next iteration."""
        self._stop_event.set()

    async def run(self) -> None:
        """Poll Polymarket markets periodically until ``stop()``."""
        self._running = True
        try:
            async with httpx.AsyncClient() as client:
                while not self._stop_event.is_set():
                    await self._poll_markets(client)

                    try:
                        await asyncio.wait_for(
                            self._stop_event.wait(),
                            timeout=self._poll_interval_s,
                        )
                    except TimeoutError:
                        pass
        finally:
            self._running = False

    async def _poll_markets(self, client: httpx.AsyncClient) -> None:
        """Fetch markets for all categories and emit data."""
        for category in self._categories:
            if self._stop_event.is_set():
                break

            markets = await fetch_polymarket_markets(client=client, category=category)
            if markets is None:
                self._errors += 1
                continue

            for market in markets:
                if self._stop_event.is_set():
                    break

                market_data = parse_polymarket_market(market, ts_ns=self._clock_ns(), venue=self._venue)
                if market_data is None:
                    self._errors += 1
                    continue

                self._markets_received += 1
                self._last_tick_ts_ns = market_data["ts_ns"]
                try:
                    self._sink(market_data)
                except Exception:  # noqa: BLE001
                    self._errors += 1
                    LOG.exception("polymarket_http: sink failed")


__all__ = [
    "POLYMARKET_URL",
    "DEFAULT_POLL_INTERVAL_S",
    "DEFAULT_CATEGORIES",
    "VENUE_TAG",
    "parse_polymarket_market",
    "fetch_polymarket_markets",
    "FeedStatus",
    "PolymarketHTTPPoller",
]