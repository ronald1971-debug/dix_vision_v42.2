"""
Execution Unified Core Adapters Paper - Paper Adapter Support
Provides paper adapter support
NO LAZY LOADING - All components load directly
"""

import logging
from typing import Any, Dict

logger = logging.getLogger(__name__)


class PaperBroker:
    """Paper broker for trading operations"""

    def __init__(self):
        self._paper_balance = 1000000.0
        self._orders = {}

    async def get_account_balance(self) -> float:
        """Get paper trading balance"""
        return self._paper_balance

    def set_paper_balance(self, balance: float):
        """Set paper trading balance"""
        self._paper_balance = balance

    async def place_order(self, order_data: Dict[str, Any]) -> str:
        """Place paper order"""
        order_id = f"paper_order_{len(self._orders)}"
        self._orders[order_id] = order_data
        return order_id


__all__ = ["PaperBroker"]
