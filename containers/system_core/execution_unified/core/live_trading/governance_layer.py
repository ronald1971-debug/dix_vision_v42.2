"""
Execution Unified Core Live Trading - Governance Layer
Provides governance approval for live trading
NO LAZY LOADING - All components load directly
"""

import logging
from dataclasses import dataclass
from enum import Enum
from typing import Optional

logger = logging.getLogger(__name__)


class GovernanceDecisionType(Enum):
    """Governance decision types"""

    APPROVED = "APPROVED"
    REJECTED = "REJECTED"
    MODIFIED = "MODIFIED"


@dataclass
class LiveTradeGovernanceContext:
    """Context for live trade governance decisions"""

    trade_id: str
    venue: str
    symbol: str
    side: str
    size_usd: float
    portfolio_usd: float
    strategy: str
    timestamp_ns: int
    mode: str = "LIVE"


@dataclass
class GovernanceApprovalDecision:
    """Governance approval decision"""

    decision: GovernanceDecisionType
    context: LiveTradeGovernanceContext
    reason: str
    approver: str = ""
    approved_by: str = ""


class LiveTradingGovernanceLayer:
    """Live trading governance layer"""

    def __init__(self):
        self._live_trading_enabled = False

    def is_live_trading_enabled(self) -> bool:
        """Check if live trading is enabled"""
        return self._live_trading_enabled

    def enable_live_trading(self, approver: str, ts_ns: int, mode: str = "LIVE") -> bool:
        """Enable live trading"""
        self._live_trading_enabled = True
        return True

    def request_approval(
        self, context: LiveTradeGovernanceContext
    ) -> Optional[GovernanceApprovalDecision]:
        """Request governance approval for a trade"""
        if not self._live_trading_enabled:
            return GovernanceApprovalDecision(
                decision=GovernanceDecisionType.REJECTED,
                context=context,
                reason="Live trading not enabled",
            )
        return GovernanceApprovalDecision(
            decision=GovernanceDecisionType.APPROVED,
            context=context,
            reason="Governance approved",
            approver="governance_layer",
        )


_governance_layer = None


def get_live_trading_governance_layer() -> LiveTradingGovernanceLayer:
    """Get live trading governance layer instance"""
    global _governance_layer
    if _governance_layer is None:
        _governance_layer = LiveTradingGovernanceLayer()
    return _governance_layer


__all__ = [
    "GovernanceDecisionType",
    "LiveTradeGovernanceContext",
    "GovernanceApprovalDecision",
    "LiveTradingGovernanceLayer",
    "get_live_trading_governance_layer",
]
