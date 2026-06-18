"""
execution_unified.adapters.adapter_wrappers
DIX VISION v42.2 — Unified Adapter Wrapper Functions

Wrapper functions for unified adapter system.
Phase 1: Execution Foundation - Day 1-2: Core Adapter Migration
"""

from __future__ import annotations

import sys
import logging
from typing import Any, Optional
from pathlib import Path

# Add parent directories to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent))
sys.path.insert(0, str(Path(__file__).parent.parent))

logger = logging.getLogger(__name__)

# Import the migrated adapters (they may need sys.path updates)
try:
    from execution_unified.adapters.binance import BinanceAdapter
    BINANCE_AVAILABLE = True
except ImportError:
    BINANCE_AVAILABLE = False
    logger.warning("Binance adapter not available")

try:
    from execution_unified.adapters.kraken import KrakenAdapter
    KRAKEN_AVAILABLE = True
except ImportError:
    KRAKEN_AVAILABLE = False
    logger.warning("Kraken adapter not available")

# NOTE: IBKR and Alpaca adapters require external infrastructure setup
# These are marked as requiring additional setup and are not immediately available
# They can be enabled when:
# - ib-insync library is installed (for IBKR)
# - alpaca-py library is installed (for Alpaca)  
# - Appropriate API credentials are configured
IBKR_AVAILABLE = False
ALPACA_AVAILABLE = False
logger.info("IBKR adapter requires external setup (ib-insync + credentials)")
logger.info("Alpaca adapter requires external setup (alpaca-py + credentials)")


def get_binance_adapter(config: Optional[dict] = None) -> Optional[Any]:
    """Get Binance adapter instance."""
    if not BINANCE_AVAILABLE:
        logger.error("Binance adapter is not available")
        return None
    
    try:
        if config:
            return BinanceAdapter(config=config)
        return BinanceAdapter()
    except Exception as e:
        logger.error(f"Failed to create Binance adapter: {e}")
        return None


def get_kraken_adapter(config: Optional[dict] = None) -> Optional[Any]:
    """Get Kraken adapter instance."""
    if not KRAKEN_AVAILABLE:
        logger.error("Kraken adapter is not available")
        return None
    
    try:
        if config:
            return KrakenAdapter(config=config)
        return KrakenAdapter()
    except Exception as e:
        logger.error(f"Failed to create Kraken adapter: {e}")
        return None


def get_alpaca_adapter(config: Optional[dict] = None) -> Optional[Any]:
    """Get Alpaca adapter instance.
    
    NOTE: This adapter requires:
    - alpaca-py library installation: pip install alpaca-py
    - Valid Alpaca API credentials configured
    - This is a Phase 2+ feature requiring additional setup
    """
    if not ALPACA_AVAILABLE:
        logger.error("Alpaca adapter requires external setup (alpaca-py + credentials)")
        logger.info("To enable: pip install alpaca-py and configure credentials")
        return None
    
    try:
        if config:
            return AlpacaAdapter(config=config)
        return AlpacaAdapter()
    except Exception as e:
        logger.error(f"Failed to create Alpaca adapter: {e}")
        return None


def get_ibkr_adapter(config: Optional[dict] = None) -> Optional[Any]:
    """Get IBKR adapter instance.
    
    NOTE: This adapter requires:
    - ib-insync library installation: pip install ib-insync
    - TWS or IB Gateway running on localhost:7497 (paper) or :4001 (live)
    - Valid IBKR credentials configured
    - This is a Phase 2+ feature requiring additional setup
    """
    if not IBKR_AVAILABLE:
        logger.error("IBKR adapter requires external setup (ib-insync + TWS/Gateway + credentials)")
        logger.info("To enable: pip install ib-insync, start TWS/Gateway, and configure credentials")
        return None
    
    try:
        if config:
            return IBKRAdapter(config=config)
        return IBKRAdapter()
    except Exception as e:
        logger.error(f"Failed to create IBKR adapter: {e}")
        return None


def get_all_available_adapters() -> dict[str, bool]:
    """Get status of all unified adapters."""
    return {
        "binance": BINANCE_AVAILABLE,
        "kraken": KRAKEN_AVAILABLE,
        "alpaca": ALPACA_AVAILABLE,
        "ibkr": IBKR_AVAILABLE,
    }


__all__ = [
    "get_binance_adapter",
    "get_kraken_adapter", 
    "get_alpaca_adapter",
    "get_ibkr_adapter",
    "get_all_available_adapters",
]