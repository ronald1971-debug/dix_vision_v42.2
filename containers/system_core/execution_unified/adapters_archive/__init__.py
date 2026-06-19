"""
Execution Unified Adapters Archive - Exchange Adapter Components
Provides production-ready exchange adapters for various trading platforms
NO LAZY LOADING - All components load directly
"""

from typing import Dict, List, Optional, Any
import logging

logger = logging.getLogger(__name__)

# Export key adapter components
__all__ = [
    # Base adapter
    'base',
    
    # Exchange adapters
    'binance',
    'binance_ws',
    'coinbase',
    'kraken',
    'raydium',
    'uniswap_v3',
    'alpaca',
    'alphavantage',
    'helius',
    'hummingbot',
    'ibkr',
    'iex',
    'ig',
    'oanda',
    'polygon',
    'pumpfun',
    'solana_native',
    'uniswapx',
    
    # Support modules
    '_ccxt_backed',
    '_cache_mixin',
    '_hummingbot_gateway',
    '_live_base',
    '_retry_mixin',
    '_retry_mixin_tenacity',
    '_uniswapx_quote',
    '_uniswapx_signer',
    'vnpy_bridge'
]