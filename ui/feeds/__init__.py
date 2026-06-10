"""Live data-feed adapters for the operator harness.

These modules sit *outside* the engine bus — they convert non-deterministic
external inputs (Binance public WebSocket, public REST polls, etc.) into
typed :class:`core.contracts.market.MarketTick` instances and feed them
into the harness state via the same code path used by ``POST /api/tick``.

INV-15 (replay determinism) is preserved because the engines see the
same canonical ``MarketTick`` regardless of whether the tick came from
HTTP or a WebSocket pump — the ledger is the single deterministic
projection. SCVS (INV-57..59) declares each feed in
``registry/data_source_registry.yaml`` and binds it to a consumer via
``consumes.yaml`` in this package.
"""

from ui.feeds.binance_public_ws import (
    BINANCE_PUBLIC_WS_BASE,
    BinancePublicWSPump,
    FeedStatus,
    make_combined_stream_url,
    parse_24hr_ticker,
)

from ui.feeds.coinbase_public_ws import (
    COINBASE_PUBLIC_WS_BASE,
    CoinbasePublicWSPump,
)

from ui.feeds.kraken_public_ws import (
    KRAKEN_PUBLIC_WS_BASE,
    KrakenPublicWSPump,
)

from ui.feeds.uniswap_http import (
    UNISWAP_SUBGRAPH_URL,
    UniswapHTTPPoller,
)

from ui.feeds.reddit_http import (
    REDDIT_API_URL,
    RedditHTTPPoller,
)

from ui.feeds.sec_edgar_http import (
    SEC_EDGAR_URL,
    SECEDGARHTTPPoller,
)

from ui.feeds.polymarket_http import (
    POLYMARKET_URL,
    PolymarketHTTPPoller,
)

__all__ = [
    "BINANCE_PUBLIC_WS_BASE",
    "BinancePublicWSPump",
    "FeedStatus",
    "make_combined_stream_url",
    "parse_24hr_ticker",
    "COINBASE_PUBLIC_WS_BASE",
    "CoinbasePublicWSPump",
    "KRAKEN_PUBLIC_WS_BASE",
    "KrakenPublicWSPump",
    "UNISWAP_SUBGRAPH_URL",
    "UniswapHTTPPoller",
    "REDDIT_API_URL",
    "RedditHTTPPoller",
    "SEC_EDGAR_URL",
    "SECEDGARHTTPPoller",
    "POLYMARKET_URL",
    "PolymarketHTTPPoller",
]
