"""
Execution Unified Core Live Trading - Risk Constraints
Provides risk constraint checking for live trading
NO LAZY LOADING - All components load directly
"""

from typing import Dict, List, Optional, Any
from dataclasses import dataclass, field
from enum import Enum
import logging

logger = logging.getLogger(__name__)

class RiskConstraintType(Enum):
    """Risk constraint types"""
    MAX_POSITION = "MAX_POSITION"
    MAX_LEVERAGE = "MAX_LEVERAGE"
    MAX_DAILY_LOSS = "MAX_DAILY_LOSS"
    CONCENTRATION_LIMIT = "CONCENTRATION_LIMIT"

@dataclass
class RiskConstraintConfig:
    """Configuration for risk constraints"""
    max_position_usd: float = 100000.0
    max_leverage: float = 3.0
    max_daily_loss_pct: float = 5.0
    concentration_limit_pct: float = 20.0

@dataclass
class LiveTradeRiskContext:
    """Context for live trade risk checking"""
    trade_id: str
    venue: str
    symbol: str
    side: str
    size_usd: float
    price: float
    portfolio_usd: float
    current_positions: Dict[str, Any] = field(default_factory=dict)
    daily_pnl_usd: float = 0.0

@dataclass
class RiskCheckResult:
    """Result of a risk constraint check"""
    constraint_type: RiskConstraintType
    passed: bool
    constraint_value: float
    actual_value: float
    reason: str = ""
    metadata: Dict[str, Any] = field(default_factory=dict)

class RiskConstraints:
    """Risk constraints manager"""

    def __init__(self):
        self._enabled = False
        self._config = RiskConstraintConfig()

    def enable(self):
        """Enable risk constraints"""
        self._enabled = True

    def configure(self, config: RiskConstraintConfig):
        """Configure risk constraints"""
        self._config = config

    def check_risk_constraints(self, context: LiveTradeRiskContext) -> tuple[bool, List[RiskCheckResult]]:
        """Check all risk constraints for a trade"""
        results = []

        # Check max position
        position_check = RiskCheckResult(
            constraint_type=RiskConstraintType.MAX_POSITION,
            passed=context.size_usd <= self._config.max_position_usd,
            constraint_value=self._config.max_position_usd,
            actual_value=context.size_usd,
            reason="Position size within limit" if context.size_usd <= self._config.max_position_usd else "Position size exceeds limit",
        )
        results.append(position_check)

        # Check max leverage
        leverage = context.size_usd / context.portfolio_usd if context.portfolio_usd > 0 else 0
        leverage_check = RiskCheckResult(
            constraint_type=RiskConstraintType.MAX_LEVERAGE,
            passed=leverage <= self._config.max_leverage,
            constraint_value=self._config.max_leverage,
            actual_value=leverage,
            reason="Leverage within limit" if leverage <= self._config.max_leverage else "Leverage exceeds limit",
        )
        results.append(leverage_check)

        all_passed = all(r.passed for r in results)
        return all_passed, results

    def get_statistics(self) -> Dict[str, Any]:
        """Get risk constraint statistics"""
        return {
            "enabled": self._enabled,
            "config": {
                "max_position_usd": self._config.max_position_usd,
                "max_leverage": self._config.max_leverage,
                "max_daily_loss_pct": self._config.max_daily_loss_pct,
                "concentration_limit_pct": self._config.concentration_limit_pct,
            },
        }

_risk_constraints = None

def get_live_trading_risk_constraints() -> RiskConstraints:
    """Get risk constraints instance"""
    global _risk_constraints
    if _risk_constraints is None:
        _risk_constraints = RiskConstraints()
    return _risk_constraints

__all__ = [
    'RiskConstraintType',
    'RiskConstraintConfig',
    'LiveTradeRiskContext',
    'RiskCheckResult',
    'RiskConstraints',
    'get_live_trading_risk_constraints',
]
