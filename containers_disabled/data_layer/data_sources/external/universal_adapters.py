"""Universal adapters for multiple data sources (Crypto, Forex, Stocks, Macro).

These adapters provide a unified interface for fetching data from multiple
providers with similar API patterns. This reduces code duplication and makes
it easier to add new sources.

Categories:
- Crypto: CoinGecko, CoinMarketCap, Binance, Kraken, Coinbase, etc.
- Forex: ExchangeRate-API, Frankfurter, Alpha Vantage, etc.
- Stocks: Tiingo, IEX, Polygon, FMP, Yahoo Finance, etc.
- Macro: FRED, World Bank, IMF, OECD, Eurostat, etc.
"""

from __future__ import annotations

import logging
from dataclasses import dataclass
from datetime import UTC, datetime
from typing import Any

LOG = logging.getLogger(__name__)


@dataclass(frozen=True, slots=True)
class UniversalCryptoObservation:
    """Unified crypto observation from any crypto provider."""

    provider: str
    symbol: str
    price: float
    volume_24h: float
    market_cap: float
    price_change_24h: float
    timestamp_ns: int


@dataclass(frozen=True, slots=True)
class UniversalForexObservation:
    """Unified forex observation from any forex provider."""

    provider: str
    from_currency: str
    to_currency: str
    rate: float
    timestamp_ns: int


@dataclass(frozen=True, slots=True)
class UniversalStockObservation:
    """Unified stock observation from any stock provider."""

    provider: str
    symbol: str
    price: float
    volume: float
    change: float
    change_percent: float
    timestamp_ns: int


@dataclass(frozen=True, slots=True)
class UniversalMacroObservation:
    """Unified macro observation from any macro provider."""

    provider: str
    indicator: str
    value: float
    timestamp_ns: int


class UniversalCryptoAdapter:
    """Universal adapter for crypto data sources."""

    def __init__(self):
        self.providers: dict[str, Any] = {}

    def fetch_price(self, provider: str, symbol: str) -> UniversalCryptoObservation:
        """Fetch crypto price from a provider."""
        # TODO: Implement actual API calls to providers
        # For now, return placeholder
        LOG.warning(f"UniversalCryptoAdapter.fetch_price not yet implemented for {provider}")
        return UniversalCryptoObservation(
            provider=provider,
            symbol=symbol,
            price=0.0,
            volume_24h=0.0,
            market_cap=0.0,
            price_change_24h=0.0,
            timestamp_ns=int(datetime.now(UTC).timestamp() * 1_000_000_000),
        )


class UniversalForexAdapter:
    """Universal adapter for forex data sources."""

    def __init__(self):
        self.providers: dict[str, Any] = {}

    def fetch_rate(self, provider: str, from_curr: str, to_curr: str) -> UniversalForexObservation:
        """Fetch forex rate from a provider."""
        # TODO: Implement actual API calls to providers
        LOG.warning(f"UniversalForexAdapter.fetch_rate not yet implemented for {provider}")
        return UniversalForexObservation(
            provider=provider,
            from_currency=from_curr,
            to_currency=to_curr,
            rate=0.0,
            timestamp_ns=int(datetime.now(UTC).timestamp() * 1_000_000_000),
        )


class UniversalStockAdapter:
    """Universal adapter for stock data sources."""

    def __init__(self):
        self.providers: dict[str, Any] = {}

    def fetch_quote(self, provider: str, symbol: str) -> UniversalStockObservation:
        """Fetch stock quote from a provider."""
        # TODO: Implement actual API calls to providers
        LOG.warning(f"UniversalStockAdapter.fetch_quote not yet implemented for {provider}")
        return UniversalStockObservation(
            provider=provider,
            symbol=symbol,
            price=0.0,
            volume=0.0,
            change=0.0,
            change_percent=0.0,
            timestamp_ns=int(datetime.now(UTC).timestamp() * 1_000_000_000),
        )


class UniversalMacroAdapter:
    """Universal adapter for macro data sources."""

    def __init__(self):
        self.providers: dict[str, Any] = {}

    def fetch_indicator(self, provider: str, indicator: str) -> UniversalMacroObservation:
        """Fetch macro indicator from a provider."""
        # TODO: Implement actual API calls to providers
        LOG.warning(f"UniversalMacroAdapter.fetch_indicator not yet implemented for {provider}")
        return UniversalMacroObservation(
            provider=provider,
            indicator=indicator,
            value=0.0,
            timestamp_ns=int(datetime.now(UTC).timestamp() * 1_000_000_000),
        )
