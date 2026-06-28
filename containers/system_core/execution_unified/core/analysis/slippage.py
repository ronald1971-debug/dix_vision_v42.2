"""
Execution Unified Core Analysis Slippage - Slippage Analysis
Provides slippage analysis capabilities
NO LAZY LOADING - All components load directly
"""

import logging
from dataclasses import dataclass
from typing import Any, Dict

logger = logging.getLogger(__name__)


@dataclass
class SlippageResult:
    """Slippage analysis result"""

    slippage_percent: float
    exp_slippage_bps: float
    timestamp_ns: int = 0

    def __post_init__(self):
        if self.timestamp_ns == 0:
            self.timestamp_ns = __import__("datetime").datetime.now().timestamp_ns()


class SlippageAnalyzer:
    """Slippage analyzer for trading operations"""

    def __init__(self):
        self._slippage_history = []

    def analyze_slippage(self, execution_data: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze slippage from execution data"""
        slippage = {
            "expected_price": execution_data.get("expected_price", 0),
            "actual_price": execution_data.get("actual_price", 0),
            "slippage_percent": 0.01,  # Default
        }
        self._slippage_history.append(slippage)
        return slippage

    def get_average_slippage(self) -> float:
        """Get average slippage"""
        if not self._slippage_history:
            return 0.0
        return sum(s["slippage_percent"] for s in self._slippage_history) / len(
            self._slippage_history
        )

    def estimate(
        self,
        execution_data: Dict[str, Any] = None,
        qty: float = 0,
        adv_qty: float = 0,
        spread_bps: int = 0,
    ) -> SlippageResult:
        """Estimate slippage for upcoming execution"""
        # Support both calling conventions
        if execution_data is not None:
            # Original signature
            expected_slippage = 0.015  # 1.5% baseline
            volatility_adjustment = execution_data.get("volatility", 1.0) * 0.005
            total_slippage = expected_slippage + volatility_adjustment
        else:
            # New signature for MEV guard compatibility
            if qty <= 0 or adv_qty <= 0:
                total_slippage = 0.01  # Default 1% slippage

            # Calculate spread impact
            spread_impact = spread_bps / 10000  # Convert basis points to percentage

            # Calculate volume impact (simplified)
            volume_ratio = qty / adv_qty if adv_qty > 0 else 0
            volume_impact = min(volume_ratio * 0.02, 0.05)  # Max 5% volume impact

            total_slippage = spread_impact + volume_impact + 0.005  # Base 0.5% slippage

            total_slippage = max(total_slippage, 0.001)  # Minimum 0.1% slippage

        # Return SlippageResult with both percentage and basis points
        return SlippageResult(
            slippage_percent=total_slippage,
            exp_slippage_bps=int(total_slippage * 10000),  # Convert percentage to basis points
        )


__all__ = ["SlippageAnalyzer", "SlippageResult", "estimate"]
