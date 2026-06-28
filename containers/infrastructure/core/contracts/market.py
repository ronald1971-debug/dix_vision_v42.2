"""
Core Contracts Market
Real implementation for market data contracts
"""

import time
from dataclasses import dataclass


@dataclass
class MarketTick:
    """Market tick data"""

    symbol: str
    price: float
    timestamp: float = 0
    volume: float = 0.0
    bid: float = 0.0
    ask: float = 0.0

    def __post_init__(self):
        if self.timestamp == 0:
            self.timestamp = time.time()
        if self.bid == 0.0:
            self.bid = self.price
        if self.ask == 0.0:
            self.ask = self.price


__all__ = ["MarketTick"]
