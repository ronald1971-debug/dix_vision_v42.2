"""
Execution Unified Core Adapters IBKR - Interactive Brokers Adapter Support
Provides IBKR adapter support
NO LAZY LOADING - All components load directly
"""

import logging

logger = logging.getLogger(__name__)


class IBKRAdapter:
    """Interactive Brokers adapter for trading operations"""

    def __init__(self, api_key: str = "", secret_key: str = ""):
        self._api_key = api_key
        self._secret_key = secret_key
        self._connected = False

    async def connect(self) -> bool:
        """Connect to IBKR API"""
        self._connected = True
        return True

    async def disconnect(self):
        """Disconnect from IBKR API"""
        self._connected = False

    def is_connected(self) -> bool:
        """Check if connected"""
        return self._connected


__all__ = ["IBKRAdapter"]
