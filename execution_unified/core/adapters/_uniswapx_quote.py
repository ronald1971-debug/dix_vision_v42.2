"""
Execution Unified Core Adapters UniswapX Quote
Provides UniswapX quote functionality
NO LAZY LOADING - All components load directly
"""

from typing import Dict, List, Optional, Any
import logging

logger = logging.getLogger(__name__)

class UniswapXQuote:
    """UniswapX quote handler"""
    
    def __init__(self):
        self._quotes = {}
        
    def get_quote(self, token_pair: str, amount: float) -> Optional[Dict[str, Any]]:
        """Get quote for token pair"""
        return self._quotes.get(token_pair)
    
    def set_quote(self, token_pair: str, quote_data: Dict[str, Any]):
        """Set quote for token pair"""
        self._quotes[token_pair] = quote_data

__all__ = ['UniswapXQuote']