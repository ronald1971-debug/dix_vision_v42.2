"""
Execution Unified Core Paper Trading Promotion Gate Integration - Promotion Gate Integration
Provides promotion gate integration capabilities
NO LAZY LOADING - All components load directly
"""

import logging
from enum import Enum
from typing import Any, Dict

logger = logging.getLogger(__name__)


class TradingMode(Enum):
    """Trading mode enumeration"""

    PAPER = "paper"
    LIVE = "live"
    SIMULATION = "simulation"
    HYBRID = "hybrid"


class PromotionGate:
    """Promotion gate for trading operations"""

    def __init__(self):
        self._current_mode = TradingMode.PAPER
        self._promotion_rules = {}

    def set_trading_mode(self, mode: TradingMode):
        """Set current trading mode"""
        self._current_mode = mode

    def get_trading_mode(self) -> TradingMode:
        """Get current trading mode"""
        return self._current_mode

    def check_promotion_eligibility(self, criteria: Dict[str, Any]) -> bool:
        """Check eligibility for promotion to next mode"""
        return True  # Simplified for now


__all__ = ["TradingMode", "PromotionGate"]
