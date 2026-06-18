"""execution_engine.analysis — Trade execution analysis and metrics.

This package contains post-trade and pre-trade analysis tools:
- slippage: Pre-trade slippage and market impact estimation
- tca: Post-trade Transaction Cost Analysis
"""

from execution_unified.core.analysis.slippage import SlippageEstimate, estimate, worst_acceptable_price, min_acceptable_price
from execution_unified.core.analysis.tca import Fill, TCAReport, analyze

__all__ = [
    "SlippageEstimate",
    "estimate",
    "worst_acceptable_price",
    "min_acceptable_price",
    "Fill",
    "TCAReport",
    "analyze",
]
