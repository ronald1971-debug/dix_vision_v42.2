"""
Execution Unified Core Live Trading - Live Trading Infrastructure
Provides core live trading capabilities
NO LAZY LOADING - All components load directly
"""

from typing import Dict, List, Optional, Any
import logging

logger = logging.getLogger(__name__)

class LiveTradingManager:
    """Live trading manager"""
    
    def __init__(self):
        self._active = False
        self._orders = {}
        
    async def start(self) -> bool:
        """Start live trading"""
        self._active = True
        return True
    
    async def stop(self):
        """Stop live trading"""
        self._active = False
    
    def is_active(self) -> bool:
        """Check if live trading is active"""
        return self._active

__all__ = ['LiveTradingManager']