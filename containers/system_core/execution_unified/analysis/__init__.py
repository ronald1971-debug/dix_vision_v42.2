"""execution_engine.analysis — Trade execution analysis and metrics.

This package contains post-trade and pre-trade analysis tools:
- slippage: Pre-trade slippage and market impact estimation
- tca: Post-trade Transaction Cost Analysis
"""

from .slippage import SlippageEstimate, estimate, worst_acceptable_price, min_acceptable_price
from .tca import Fill, TCAReport, analyze

__all__ = [
    "SlippageEstimate",
    "estimate",
    "worst_acceptable_price",
    "min_acceptable_price",
    "Fill",
    "TCAReport",
    "analyze",
]
