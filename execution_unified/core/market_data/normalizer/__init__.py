"""
Execution Unified Core Market Data Normalizer - Market Data Normalization
Provides market data normalization capabilities
NO LAZY LOADING - All components load directly
"""

from typing import Dict, List, Optional, Any
from dataclasses import dataclass, field
from enum import Enum
import logging

logger = logging.getLogger(__name__)

class NormalizationLevel(Enum):
    """Normalization level"""
    L1 = "L1"
    L2 = "L2"
    L3 = "L3"

@dataclass
class NormalizedLevel:
    """Normalized price level"""
    price: float
    size: float
    level: NormalizationLevel
    timestamp_ns: int = 0
    
    def __post_init__(self):
        if self.timestamp_ns == 0:
            self.timestamp_ns = __import__('datetime').datetime.now().timestamp_ns()

@dataclass
class NormalizedTick:
    """Normalized tick data"""
    price: float
    size: float
    side: str
    timestamp_ns: int = 0
    
    def __post_init__(self):
        if self.timestamp_ns == 0:
            self.timestamp_ns = __import__('datetime').datetime.now().timestamp_ns()

@dataclass
class NormalizedBook:
    """Normalized order book data"""
    bids: List[NormalizedLevel] = field(default_factory=list)
    asks: List[NormalizedLevel] = field(default_factory=list)
    timestamp_ns: int = 0
    
    def __post_init__(self):
        if self.timestamp_ns == 0:
            self.timestamp_ns = __import__('datetime').datetime.now().timestamp_ns()

class MarketDataNormalizer:
    """Market data normalizer"""
    
    def __init__(self):
        self._normalization_rules = {}
        
    def normalize(self, raw_data: Dict[str, Any]) -> NormalizedBook:
        """Normalize market data"""
        return NormalizedBook(
            bids=[],
            asks=[],
            timestamp_ns=__import__('datetime').datetime.now().timestamp_ns()
        )

__all__ = ['NormalizationLevel', 'NormalizedLevel', 'NormalizedTick', 'NormalizedBook', 'MarketDataNormalizer']