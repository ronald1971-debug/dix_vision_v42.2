"""
Execution Unified Core Market Data Aggregator - Market Data Aggregation
Provides market data aggregation capabilities
NO LAZY LOADING - All components load directly
"""

from typing import Dict, List, Optional, Any
from dataclasses import dataclass, field
import logging

logger = logging.getLogger(__name__)

@dataclass
class OrderBookLevel:
    """Order book level data structure"""
    price: float
    size: float
    orders: int = 0
    timestamp_ns: int = 0
    
    def __post_init__(self):
        if self.timestamp_ns == 0:
            self.timestamp_ns = __import__('datetime').datetime.now().timestamp_ns()

@dataclass
class OrderBookSnapshot:
    """Order book snapshot data structure"""
    bids: List[OrderBookLevel] = field(default_factory=list)
    asks: List[OrderBookLevel] = field(default_factory=list)
    sequence_number: int = 0
    timestamp_ns: int = 0
    
    def __post_init__(self):
        if self.timestamp_ns == 0:
            self.timestamp_ns = __import__('datetime').datetime.now().timestamp_ns()

@dataclass
class BookDelta:
    """Order book delta change"""
    bid_changes: List[Dict[str, Any]] = field(default_factory=list)
    ask_changes: List[Dict[str, Any]] = field(default_factory=list)
    sequence_number: int = 0
    timestamp_ns: int = 0
    
    def __post_init__(self):
        if self.timestamp_ns == 0:
            self.timestamp_ns = __import__('datetime').datetime.now().timestamp_ns()

class MarketDataAggregator:
    """Market data aggregator"""
    
    def __init__(self):
        self._aggregated_data = {}
        self._sequence_number = 0
        
    def aggregate(self, data_sources: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Aggregate market data from multiple sources"""
        self._sequence_number += 1
        return {"aggregated": True, "sources": len(data_sources), "sequence": self._sequence_number}
    
    def create_book_delta(self, bid_changes: List[Dict[str, Any]], ask_changes: List[Dict[str, Any]]) -> BookDelta:
        """Create order book delta"""
        return BookDelta(
            bid_changes=bid_changes,
            ask_changes=ask_changes,
            sequence_number=self._sequence_number,
            timestamp_ns=__import__('datetime').datetime.now().timestamp_ns()
        )
    
    def create_order_book_level(self, price: float, size: float, orders: int = 0) -> OrderBookLevel:
        """Create order book level"""
        return OrderBookLevel(
            price=price,
            size=size,
            orders=orders,
            timestamp_ns=__import__('datetime').datetime.now().timestamp_ns()
        )
    
    def create_order_book_snapshot(self, bids: List[OrderBookLevel], asks: List[OrderBookLevel]) -> OrderBookSnapshot:
        """Create order book snapshot"""
        return OrderBookSnapshot(
            bids=bids,
            asks=asks,
            sequence_number=self._sequence_number,
            timestamp_ns=__import__('datetime').datetime.now().timestamp_ns()
        )

__all__ = ['OrderBookLevel', 'OrderBookSnapshot', 'BookDelta', 'MarketDataAggregator']