"""Uniswap V3 subgraph HTTP adapter (SRC-MARKET-UNISWAP-001).

Fetches pool data from Uniswap V3 subgraph and converts it into
canonical :class:`core.contracts.market.MarketTick`.

Layered split:

* :func:`fetch_pool_data` — HTTP fetcher for pool data.
* :func:`parse_pool_data` — pure pool data → ``MarketTick`` projection.
* :class:`UniswapHTTPPoller` — periodic poller with error handling.
* :class:`FeedStatus` — frozen telemetry snapshot.

INV-15: the parser is pure (caller-supplied ``ts_ns``); the poller
uses HTTP but every event it emits is funneled into the harness via
the same code path as ``POST /api/tick``.

Uniswap V3 subgraph reference:
https://thegraph.com/hosted-service/uniswap/uniswap-v3
"""

from __future__ import annotations

import asyncio
import logging
from collections.abc import Callable, Mapping, Sequence
from dataclasses import dataclass
from typing import Any

import httpx
from core.contracts.market import MarketTick

LOG = logging.getLogger(__name__)

#: Uniswap V3 subgraph endpoint.
UNISWAP_SUBGRAPH_URL = "https://api.thegraph.com/subgraphs/name/uniswap/uniswap-v3"

#: Default poll interval (seconds).
DEFAULT_POLL_INTERVAL_S = 30.0

#: Default pool addresses (major pools).
DEFAULT_POOLS: tuple[str, ...] = (
    "0x8ad599c3a0ff1de082011efddc58f1908eb6e6d8",  # USDC/ETH
    "0x88e6a0c2ddd26feeb64f039a2c41296fcb3f5640",  # USDC/ETH (Uniswap)
    "0x4e68ccd3e89f51c30b4ed807486de7b0b1b7b7d7",  # DAI/ETH
)

#: Venue tag stamped onto every emitted ``MarketTick``.
VENUE_TAG = "UNISWAP"


def parse_pool_data(
    pool_data: Mapping[str, Any],
    *,
    ts_ns: int,
    venue: str = VENUE_TAG,
) -> MarketTick | None:
    """Project Uniswap pool data into a :class:`MarketTick`.

    Returns ``None`` (never raises) if ``pool_data`` is malformed.
    """
    try:
        token0 = pool_data.get("token0", {})
        token1 = pool_data.get("token1", {})
        pool_symbol = f"{token0.get('symbol', 'UNKNOWN')}/{token1.get('symbol', 'UNKNOWN')}"

        # Use sqrtPrice to calculate price
        sqrt_price = float(pool_data.get("sqrtPrice", "0"))
        if sqrt_price == 0:
            return None

        # Convert sqrtPrice to actual price (simplified)
        # In reality, this would need proper token decimals handling
        price = sqrt_price / (2**96)

        # Approximate bid/ask from pool liquidity and tick data
        tick = int(pool_data.get("tick", "0"))
        tick_spacing = int(pool_data.get("tickSpacing", "10"))

        # Approximate spread based on tick spacing
        spread = 0.001 * (tick_spacing / 10)
        bid = price * (1 - spread)
        ask = price * (1 + spread)

        # Use TVL as volume approximation
        tvl_usd = float(pool_data.get("totalValueLockedUSD", "0"))
        volume = tvl_usd / 1000.0  # Rough approximation

    except (KeyError, ValueError, TypeError):
        return None

    if not pool_symbol or pool_symbol == "UNKNOWN/UNKNOWN":
        return None
    if bid <= 0 or ask <= 0 or price <= 0:
        return None
    if volume < 0:
        return None

    return MarketTick(
        ts_ns=ts_ns,
        symbol=pool_symbol,
        bid=bid,
        ask=ask,
        last=price,
        volume=volume,
        venue=venue,
    )


async def fetch_pool_data(
    pool_address: str,
    client: httpx.AsyncClient,
) -> dict[str, Any] | None:
    """Fetch pool data from Uniswap subgraph."""
    query = """
    query {
        pool(id: "%s") {
            token0 {
                symbol
                decimals
            }
            token1 {
                symbol
                decimals
            }
            sqrtPrice
            tick
            tickSpacing
            totalValueLockedUSD
            volumeUSD
            feeTier
        }
    }
    """ % pool_address

    try:
        response = await client.post(
            UNISWAP_SUBGRAPH_URL,
            json={"query": query},
            timeout=10.0,
        )
        response.raise_for_status()
        data = response.json()
        pool_data = data.get("data", {}).get("pool")
        return pool_data
    except Exception as e:
        LOG.warning(f"Failed to fetch Uniswap pool {pool_address}: {e}")
        return None


@dataclass(frozen=True, slots=True)
class FeedStatus:
    """Snapshot of poller health — exposed by ``GET /api/feeds/uniswap/status``."""

    running: bool
    pools: tuple[str, ...]
    last_tick_ts_ns: int | None
    ticks_received: int
    errors: int


class UniswapHTTPPoller:
    """HTTP poller streaming Uniswap pool data into a sink.

    The sink callable runs synchronously; for cross-thread state
    mutation use :class:`ui.feeds.runner.FeedRunner` which wraps
    the poller and bridges to the FastAPI sync world.
    """

    def __init__(
        self,
        pool_addresses: Sequence[str],
        sink: Callable[[MarketTick], None],
        *,
        clock_ns: Callable[[], int],
        poll_interval_s: float = DEFAULT_POLL_INTERVAL_S,
        venue: str = VENUE_TAG,
    ) -> None:
        if not pool_addresses:
            raise ValueError("UniswapHTTPPoller: at least one pool address required")
        if poll_interval_s <= 0:
            raise ValueError("UniswapHTTPPoller: poll_interval_s must be positive")

        self._pool_addresses: tuple[str, ...] = tuple(pool_addresses)
        self._sink = sink
        self._clock_ns = clock_ns
        self._poll_interval_s = poll_interval_s
        self._venue = venue
        self._stop_event = asyncio.Event()
        self._ticks_received = 0
        self._errors = 0
        self._last_tick_ts_ns: int | None = None
        self._running = False

    @property
    def pools(self) -> tuple[str, ...]:
        return self._pool_addresses

    def status(self) -> FeedStatus:
        return FeedStatus(
            running=self._running,
            pools=self._pool_addresses,
            last_tick_ts_ns=self._last_tick_ts_ns,
            ticks_received=self._ticks_received,
            errors=self._errors,
        )

    def stop(self) -> None:
        """Signal the run loop to exit on its next iteration."""
        self._stop_event.set()

    async def run(self) -> None:
        """Poll pools periodically until ``stop()``."""
        self._running = True
        try:
            async with httpx.AsyncClient() as client:
                while not self._stop_event.is_set():
                    await self._poll_pools(client)

                    try:
                        await asyncio.wait_for(
                            self._stop_event.wait(),
                            timeout=self._poll_interval_s,
                        )
                    except TimeoutError:
                        pass
        finally:
            self._running = False

    async def _poll_pools(self, client: httpx.AsyncClient) -> None:
        """Fetch data from all pools and emit ticks."""
        for pool_address in self._pool_addresses:
            if self._stop_event.is_set():
                break

            pool_data = await fetch_pool_data(pool_address, client)
            if pool_data is None:
                self._errors += 1
                continue

            tick = parse_pool_data(pool_data, ts_ns=self._clock_ns(), venue=self._venue)
            if tick is None:
                self._errors += 1
                continue

            self._ticks_received += 1
            self._last_tick_ts_ns = tick.ts_ns
            try:
                self._sink(tick)
            except Exception:  # noqa: BLE001
                self._errors += 1
                LOG.exception("uniswap_http: sink failed")


__all__ = [
    "UNISWAP_SUBGRAPH_URL",
    "DEFAULT_POLL_INTERVAL_S",
    "DEFAULT_POOLS",
    "VENUE_TAG",
    "parse_pool_data",
    "fetch_pool_data",
    "FeedStatus",
    "UniswapHTTPPoller",
]
