"""
Execution Unified Core Paper Trading Venue Config - Venue Configuration
Provides venue configuration for paper trading
NO LAZY LOADING - All components load directly
"""

import logging
from typing import Any, Dict, Optional

logger = logging.getLogger(__name__)

# Default venue configurations
VENUE_CONFIGS = {
    "default": {
        "max_position_size": 1000000,
        "max_daily_volume": 10000000,
        "supported_assets": ["BTC", "ETH", "USD"],
        "paper_mode": True,
    },
    "binance": {
        "max_position_size": 5000000,
        "max_daily_volume": 50000000,
        "supported_assets": ["BTC", "ETH", "USDT", "BNB"],
        "paper_mode": True,
    },
    "kraken": {
        "max_position_size": 3000000,
        "max_daily_volume": 30000000,
        "supported_assets": ["BTC", "ETH", "USD", "EUR"],
        "paper_mode": True,
    },
}


class VenueConfig:
    """Venue configuration for paper trading"""

    def __init__(self):
        self._venue_configs = VENUE_CONFIGS.copy()
        self._active_venue = "default"

    def configure_venue(self, venue: str, config: Dict[str, Any]) -> bool:
        """Configure a specific venue"""
        self._venue_configs[venue] = config
        return True

    def get_venue_config(self, venue: str) -> Optional[Dict[str, Any]]:
        """Get venue configuration"""
        return self._venue_configs.get(venue)

    def set_active_venue(self, venue: str):
        """Set active venue"""
        self._active_venue = venue

    def get_active_venue(self) -> Optional[str]:
        """Get active venue"""
        return self._active_venue

    def get_all_venues(self) -> Dict[str, Dict[str, Any]]:
        """Get all venue configurations"""
        return self._venue_configs.copy()


# Global instance
_venue_config = None


def get_venue_config() -> VenueConfig:
    """Get venue config instance"""
    global _venue_config
    if _venue_config is None:
        _venue_config = VenueConfig()
    return _venue_config


__all__ = ["VenueConfig", "VENUE_CONFIGS", "get_venue_config"]
