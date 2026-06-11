"""data_sources.external — Read-only external data source adapters (BUILD-DIRECTIVE §14).

These adapters provide market data, news, social sentiment, economic
data, geopolitical events, and universal adapters for multiple providers.
They are feeder streams only — they provide data to the intelligence pipeline
but never directly influence execution decisions.

B-FETCH lint rule applies: only fetch_* public methods permitted.

Available adapters:
- news_feed: News and sentiment from various sources
- gdelt_events: GDELT Project global events database
- universal_adapters: Universal adapters for crypto, forex, stocks, macro data
- api_implementations: Actual API implementations for 60+ sources
"""

from data_sources.external.gdelt_events import GDELTAdapter, GDELTEventObservation
from data_sources.external.universal_adapters import (
    UniversalCryptoAdapter,
    UniversalCryptoObservation,
    UniversalForexAdapter,
    UniversalForexObservation,
    UniversalMacroAdapter,
    UniversalMacroObservation,
    UniversalStockAdapter,
    UniversalStockObservation,
)

__all__ = [
    "GDELTAdapter",
    "GDELTEventObservation",
    "UniversalCryptoAdapter",
    "UniversalCryptoObservation",
    "UniversalForexAdapter",
    "UniversalForexObservation",
    "UniversalMacroAdapter",
    "UniversalMacroObservation",
    "UniversalStockAdapter",
    "UniversalStockObservation",
]
