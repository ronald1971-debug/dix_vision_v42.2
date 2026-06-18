"""Broker adapters for the Execution Engine.

Two adapter hierarchies:

* **LiveAdapterBase** track (submit/reject pattern, AdapterState FSM):
  PaperBroker, HummingbotAdapter, PumpFunAdapter, UniswapXAdapter,
  BinanceAdapter, AlpacaAdapter, IBKRAdapter.

* **BaseAdapter** track (async submit_order → FillReport, BaseAdapter ABC):
  CoinbaseAdapter, KrakenAdapter, OandaAdapter, IGAdapter.

All adapters are re-exported here so import paths stay stable regardless
of which hierarchy a caller needs.
"""

from execution_unified.core.adapters._live_base import (
    AdapterState,
    AdapterStatus,
    LiveAdapterBase,
)
from execution_unified.core.adapters.alpaca import AlpacaAdapter
from execution_unified.core.adapters.base import (
    AdapterConfig,
    AdapterHealth,
    BrokerAdapter,
    FillReport,
)
from execution_unified.core.adapters.binance import BinanceAdapter
from execution_unified.core.adapters.coinbase import CoinbaseAdapter
from execution_unified.core.adapters.hummingbot import HummingbotAdapter
from execution_unified.core.adapters.ibkr import IBKRAdapter
from execution_unified.core.adapters.ig import IGAdapter
from execution_unified.core.adapters.kraken import KrakenAdapter
from execution_unified.core.adapters.oanda import OandaAdapter
from execution_unified.core.adapters.paper import PaperBroker
from execution_unified.core.adapters.pumpfun import PumpFunAdapter
from execution_unified.core.adapters.registry import (
    AdapterRegistry,
    default_registry,
)
from execution_unified.core.adapters.simple_router import (
    AdapterEntry,
    SimpleAdapterRouter,
    get_adapter_router,
    get_simple_adapter_router,
)

# UniswapX needs ``eth-account`` for EIP-712 signing. That dep lives in
# the optional ``[evm]`` / ``[dev]`` extras so the base launcher can
# boot without it. Re-export ``UniswapXAdapter`` only when its
# dependency chain imports cleanly; otherwise ``UniswapXAdapter`` is
# ``None`` and ``default_registry()`` skips registering it.
try:
    from execution_unified.core.adapters.uniswapx import UniswapXAdapter
except ImportError:
    UniswapXAdapter = None  # type: ignore[assignment,misc]

__all__ = [
    # Base contracts
    "AdapterConfig",
    "AdapterHealth",
    "AdapterRegistry",
    "AdapterState",
    "AdapterStatus",
    "BrokerAdapter",
    "FillReport",
    "LiveAdapterBase",
    # Registry
    "default_registry",
    # LiveAdapterBase track
    "AlpacaAdapter",
    "BinanceAdapter",
    "HummingbotAdapter",
    "IBKRAdapter",
    "PaperBroker",
    "PumpFunAdapter",
    "UniswapXAdapter",
    # BaseAdapter track
    "CoinbaseAdapter",
    "IGAdapter",
    "KrakenAdapter",
    "OandaAdapter",
    # Simple router (legacy compatibility)
    "AdapterEntry",
    "SimpleAdapterRouter",
    "get_adapter_router",
    "get_simple_adapter_router",
]
