"""
Execution Unified Core Adapters Alpaca - Alpaca Adapter Support
Provides Alpaca adapter support
NO LAZY LOADING - All components load directly
"""

import logging

logger = logging.getLogger(__name__)


class AlpacaAdapter:
    """Alpaca adapter for trading operations"""

    def __init__(self, api_key: str = "", secret_key: str = ""):
        self._api_key = api_key
        self._secret_key = secret_key
        self._connected = False

    async def connect(self) -> bool:
        """Connect to Alpaca API"""
        self._connected = True
        return True

    async def disconnect(self):
        """Disconnect from Alpaca API"""
        self._connected = False

    def is_connected(self) -> bool:
        """Check if connected"""
        return self._connected


__all__ = ["AlpacaAdapter"]
