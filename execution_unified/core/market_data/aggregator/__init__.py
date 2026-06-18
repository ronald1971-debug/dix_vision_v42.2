"""
Execution Unified Core Market Data Aggregator - Market Data Aggregation
Provides market data aggregation capabilities
NO LAZY LOADING - All components load directly
"""

from typing import Dict, List, Optional, Any
import logging

logger = logging.getLogger(__name__)

class MarketDataAggregator:
    """Market data aggregator"""
    
    def __init__(self):
        self._aggregated_data = {}
        
    def aggregate(self, data_sources: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Aggregate market data from multiple sources"""
        return {"aggregated": True, "sources": len(data_sources)}

__all__ = ['MarketDataAggregator']