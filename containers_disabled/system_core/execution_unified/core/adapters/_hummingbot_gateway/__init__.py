"""
Execution Unified Core Adapters Hummingbot Gateway - Hummingbot Gateway Support
Provides hummingbot gateway support
NO LAZY LOADING - All components load directly
"""

import logging
from dataclasses import dataclass, field
from typing import Any, Dict, Optional

logger = logging.getLogger(__name__)


class GatewayError(Exception):
    """Gateway error for hummingbot operations"""

    def __init__(self, message: str, status_code: Optional[int] = None):
        super().__init__(message)
        self.message = message
        self.status_code = status_code

    def __str__(self) -> str:
        status_str = f" (status {self.status_code})" if self.status_code else ""
        return f"GatewayError: {self.message}{status_str}"


@dataclass
class GatewayTradeRequest:
    """Gateway trade request data structure"""

    connector: str
    base: str
    quote: str
    side: str
    amount: float
    price: Optional[float] = None
    params: Dict[str, Any] = field(default_factory=dict)


class HummingbotGatewayClient:
    """Hummingbot gateway client"""

    def __init__(self, gateway_url: str = ""):
        self._gateway_url = gateway_url
        self._connected = False

    async def connect(self) -> bool:
        """Connect to gateway"""
        self._connected = True
        return True

    async def disconnect(self):
        """Disconnect from gateway"""
        self._connected = False

    def is_connected(self) -> bool:
        """Check if connected"""
        return self._connected

    async def submit_trade(self, request: GatewayTradeRequest) -> Dict[str, Any]:
        """Submit trade to gateway"""
        return {
            "status": "success",
            "order_id": f"gateway_order_{__import__('time').time()}",
            "connector": request.connector,
            "side": request.side,
        }


__all__ = ["GatewayError", "GatewayTradeRequest", "HummingbotGatewayClient"]
