"""
Execution Unified Core Paper Trading Adapter - Paper Trading Adapter
Provides paper trading adapter capabilities
NO LAZY LOADING - All components load directly
"""

from typing import Dict, List, Optional, Any
import logging

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

__all__ = ['PaperTradingAdapter']