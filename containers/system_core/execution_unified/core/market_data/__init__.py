"""
Execution Unified Core Market Data - Market Data Infrastructure
Provides market data handling capabilities
NO LAZY LOADING - All components load directly
"""

from typing import Dict, List, Optional, Any
import logging
import asyncio
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)


class Aggregator:
    """Market data aggregator"""
    
    def __init__(self):
        self._data_sources: Dict[str, Any] = {}
        self._aggregated_data: Dict[str, Dict[str, Any]] = {}
        
    async def aggregate_data(self, symbol: str, sources: List[str]) -> Dict[str, Any]:
        """Aggregate market data from multiple sources"""
        aggregated = {
            'symbol': symbol,
            'sources': sources,
            'timestamp': datetime.now().timestamp_ns(),
            'data': {}
        }
        
        for source in sources:
            if source in self._data_sources:
                aggregated['data'][source] = self._data_sources[source].get(symbol, {})
        
        return aggregated
    
    async def add_data_source(self, source_id: str, source: Any):
        """Add a data source"""
        self._data_sources[source_id] = source


class BookBuilder:
    """Order book builder"""
    
    def __init__(self):
        self._order_books: Dict[str, Dict[str, Any]] = {}
        
    async def build_book(self, symbol: str, raw_data: Dict[str, Any]) -> Dict[str, Any]:
        """Build order book from raw market data"""
        book = {
            'symbol': symbol,
            'bids': raw_data.get('bids', []),
            'asks': raw_data.get('asks', []),
            'spread': 0.0,
            'timestamp': datetime.now().timestamp_ns()
        }
        
        if book['bids'] and book['asks']:
            book['spread'] = book['asks'][0][0] - book['bids'][0][0]
        
        self._order_books[symbol] = book
        return book
    
    def get_book(self, symbol: str) -> Optional[Dict[str, Any]]:
        """Get order book for symbol"""
        return self._order_books.get(symbol)


class Normalizer:
    """Market data normalizer"""
    
    def __init__(self):
        self._normalization_rules: Dict[str, Any] = {}
        
    async def normalize_data(self, raw_data: Dict[str, Any], source_id: str) -> Dict[str, Any]:
        """Normalize market data to standard format"""
        normalized = {
            'symbol': raw_data.get('symbol'),
            'price': raw_data.get('price'),
            'volume': raw_data.get('volume'),
            'timestamp': raw_data.get('timestamp', datetime.now().timestamp_ns()),
            'source': source_id
        }
        return normalized


class OrderBook:
    """Order book data structure"""
    
    def __init__(self, symbol: str):
        self._symbol = symbol
        self._bids: List[tuple] = []
        self._asks: List[tuple] = []
        self._last_update_ns = 0
        
    async def update(self, bids: List[tuple], asks: List[tuple]):
        """Update order book"""
        self._bids = sorted(bids, key=lambda x: x[0], reverse=True)
        self._asks = sorted(asks, key=lambda x: x[0])
        self._last_update_ns = datetime.now().timestamp_ns()
    
    def get_best_bid(self) -> Optional[tuple]:
        """Get best bid"""
        return self._bids[0] if self._bids else None
    
    def get_best_ask(self) -> Optional[tuple]:
        """Get best ask"""
        return self._asks[0] if self._asks else None
    
    def get_spread(self) -> float:
        """Get bid-ask spread"""
        best_bid = self.get_best_bid()
        best_ask = self.get_best_ask()
        if best_bid and best_ask:
            return best_ask[0] - best_bid[0]
        return 0.0


# Global instances
_aggregator = None
_book_builder = None
_normalizer = None
_order_books: Dict[str, OrderBook] = {}


def get_aggregator() -> Aggregator:
    """Get aggregator instance"""
    global _aggregator
    if _aggregator is None:
        _aggregator = Aggregator()
    return _aggregator


def get_book_builder() -> BookBuilder:
    """Get book builder instance"""
    global _book_builder
    if _book_builder is None:
        _book_builder = BookBuilder()
    return _book_builder


def get_normalizer() -> Normalizer:
    """Get normalizer instance"""
    global _normalizer
    if _normalizer is None:
        _normalizer = Normalizer()
    return _normalizer


def get_order_book(symbol: str) -> OrderBook:
    """Get or create order book for symbol"""
    global _order_books
    if symbol not in _order_books:
        _order_books[symbol] = OrderBook(symbol)
    return _order_books[symbol]


__all__ = [
    'Aggregator',
    'BookBuilder',
    'Normalizer',
    'OrderBook',
    'get_aggregator',
    'get_book_builder',
    'get_normalizer',
    'get_order_book'
]