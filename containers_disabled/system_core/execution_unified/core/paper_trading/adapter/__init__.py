"""
Execution Unified Core Paper Trading Adapter - Paper Trading Adapter
Provides paper trading adapter capabilities
NO LAZY LOADING - All components load directly
"""

import logging
from typing import Any, Dict

logger = logging.getLogger(__name__)


class PaperTradingAdapter:
    """Paper trading adapter for simulation"""

    def __init__(self):
        self._active = False
        self._paper_balance = 1000000.0

    async def connect(self) -> bool:
        """Connect to paper trading"""
        self._active = True
        return True

    async def disconnect(self):
        """Disconnect from paper trading"""
        self._active = False

    def get_balance(self) -> float:
        """Get paper trading balance"""
        return self._paper_balance


class PaperVenueAdapter(PaperTradingAdapter):
    """Paper venue adapter with venue-specific functionality"""

    def __init__(self, venue: str = "default"):
        super().__init__()
        self._venue = venue
        self._venue_config = {}

    def configure_venue(self, venue_config: Dict[str, Any]):
        """Configure venue-specific settings"""
        self._venue_config = venue_config

    def get_venue(self) -> str:
        """Get current venue"""
        return self._venue


__all__ = ["PaperTradingAdapter", "PaperVenueAdapter"]
