"""
Execution Unified Live Trading - Live Trading Infrastructure
Provides live trading capabilities required by archival components
NO LAZY LOADING - All components load directly
"""

import asyncio
import logging
from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from typing import Any, Callable, Dict, List, Optional

logger = logging.getLogger(__name__)


class LiveTradingStatus(Enum):
    """Live trading status"""

    DISABLED = "disabled"
    PENDING_APPROVAL = "pending_approval"
    ENABLED = "enabled"
    PAUSED = "paused"
    SUSPENDED = "suspended"


class TradingMode(Enum):
    """Trading mode"""

    AUTO = "auto"
    SEMI_AUTO = "semi_auto"
    MANUAL = "manual"


class RiskConstraint(Enum):
    """Risk constraint type"""

    MAX_POSITION_SIZE = "max_position_size"
    MAX_DAILY_LOSS = "max_daily_loss"
    MAX_DRAWDOWN = "max_drawdown"
    MAX_EXPOSURE = "max_exposure"
    MAX_LEVERAGE = "max_leverage"


@dataclass
class LiveTradingConfig:
    """Live trading configuration"""

    status: LiveTradingStatus = LiveTradingStatus.DISABLED
    mode: TradingMode = TradingMode.SEMI_AUTO
    require_governance_approval: bool = True
    enable_risk_constraints: bool = True
    enable_ledger_backup: bool = True
    audit_system_enabled: bool = True
    max_position_size_pct: float = 0.1  # 10% of portfolio
    max_daily_loss_pct: float = 0.05  # 5% daily loss
    max_drawdown_pct: float = 0.1  # 10% max drawdown


@dataclass
class RiskConstraints:
    """Risk constraints configuration"""

    max_position_size: float = 0.1
    max_daily_loss: float = 0.05
    max_drawdown: float = 0.1
    max_exposure: float = 0.8
    max_leverage: float = 2.0
    position_timeout_seconds: int = 300
    enabled: bool = True


@dataclass
class LiveTradingMetrics:
    """Live trading metrics"""

    total_trades: int = 0
    winning_trades: int = 0
    losing_trades: int = 0
    total_pnl: float = 0.0
    daily_pnl: float = 0.0
    max_drawdown: float = 0.0
    sharpe_ratio: float = 0.0
    win_rate: float = 0.0
    last_trade_ns: int = 0
    last_update_ns: int = 0

    def __post_init__(self):
        if self.last_trade_ns == 0:
            self.last_trade_ns = datetime.now().timestamp_ns()
        if self.last_update_ns == 0:
            self.last_update_ns = datetime.now().timestamp_ns()


class LiveTradingManager:
    """
    Live Trading Manager - Core live trading infrastructure

    Manages live trading operations, risk constraints, and governance integration
    Required by archival components for live trading operations
    """

    def __init__(self, config: Optional[LiveTradingConfig] = None):
        self._config = config or LiveTradingConfig()
        self._risk_constraints = RiskConstraints()
        self._metrics = LiveTradingMetrics()
        self._active_trades: Dict[str, Dict[str, Any]] = {}
        self._approvals: Dict[str, Dict[str, Any]] = {}
        self._callbacks: Dict[str, List[Callable]] = {}
        self._lock = asyncio.Lock()
        self._governance_enabled = True

    async def enable_live_trading(self, approver_id: str, reason: Optional[str] = None) -> bool:
        """Enable live trading with governance approval"""
        if self._config.status == LiveTradingStatus.ENABLED:
            logger.warning("Live trading already enabled")
            return True

        if self._config.require_governance_approval:
            # Request governance approval
            approval_id = f"approval_{datetime.now().timestamp_ns()}"
            self._approvals[approval_id] = {
                "approver_id": approver_id,
                "reason": reason,
                "status": "pending",
                "requested_at": datetime.now().timestamp_ns(),
            }

            # In real implementation, would interface with governance system
            self._approvals[approval_id]["status"] = "approved"

        async with self._lock:
            self._config.status = LiveTradingStatus.ENABLED

        logger.info(f"Live trading enabled by {approver_id}")

        # Trigger callbacks
        await self._trigger_callbacks("live_trading_enabled")

        return True

    async def disable_live_trading(self, approver_id: str, reason: Optional[str] = None) -> bool:
        """Disable live trading"""
        async with self._lock:
            self._config.status = LiveTradingStatus.DISABLED

        logger.info(f"Live trading disabled by {approver_id}")

        # Trigger callbacks
        await self._trigger_callbacks("live_trading_disabled")

        return True

    async def pause_live_trading(self, approver_id: str, reason: Optional[str] = None) -> bool:
        """Pause live trading temporarily"""
        async with self._lock:
            self._config.status = LiveTradingStatus.PAUSED

        logger.info(f"Live trading paused by {approver_id}")

        # Trigger callbacks
        await self._trigger_callbacks("live_trading_paused")

        return True

    async def execute_trade(self, trade_data: Dict[str, Any]) -> Optional[str]:
        """Execute a trade in live trading mode"""
        if self._config.status != LiveTradingStatus.ENABLED:
            logger.error(f"Live trading not enabled (status: {self._config.status.value})")
            return None

        # Check risk constraints
        if self._config.enable_risk_constraints:
            if not await self._check_risk_constraints(trade_data):
                logger.error("Trade violates risk constraints")
                return None

        # Execute trade
        trade_id = f"trade_{datetime.now().timestamp_ns()}"

        trade = {
            "trade_id": trade_id,
            "trade_data": trade_data,
            "status": "executing",
            "submitted_at": datetime.now().timestamp_ns(),
        }

        async with self._lock:
            self._active_trades[trade_id] = trade
            self._metrics.total_trades += 1

        logger.info(f"Executing trade: {trade_id}")

        # Trigger callbacks
        await self._trigger_callbacks(f"trade_executed_{trade_id}")

        return trade_id

    async def update_risk_constraints(self, constraints: RiskConstraints) -> bool:
        """Update risk constraints"""
        async with self._lock:
            self._risk_constraints = constraints

        logger.info("Risk constraints updated")

        # Trigger callbacks
        await self._trigger_callbacks("risk_constraints_updated")

        return True

    async def check_risk_limits(self) -> Tuple[bool, List[str]]:
        """Check current risk limits"""
        violations = []

        if not self._risk_constraints.enabled:
            return True, violations

        # Check drawdown
        if self._metrics.max_drawdown > self._risk_constraints.max_drawdown:
            violations.append(
                f"Max drawdown {self._metrics.max_drawdown} exceeds limit {self._risk_constraints.max_drawdown}"
            )

        # Check daily loss
        if self._metrics.daily_pnl < -self._risk_constraints.max_daily_loss:
            violations.append(
                f"Daily loss {self._metrics.daily_pnl} exceeds limit {self._risk_constraints.max_daily_loss}"
            )

        # Check exposure
        current_exposure = len(self._active_trades) / 100.0  # Placeholder calculation
        if current_exposure > self._risk_constraints.max_exposure:
            violations.append(
                f"Current exposure {current_exposure} exceeds limit {self._risk_constraints.max_exposure}"
            )

        return len(violations) == 0, violations

    async def get_status(self) -> LiveTradingStatus:
        """Get current live trading status"""
        return self._config.status

    async def get_metrics(self) -> LiveTradingMetrics:
        """Get live trading metrics"""
        return self._metrics

    async def _check_risk_constraints(self, trade_data: Dict[str, Any]) -> bool:
        """Check if trade satisfies risk constraints"""
        if not self._risk_constraints.enabled:
            return True

        # Check position size
        position_size = trade_data.get("size", 0)
        max_size = self._risk_constraints.max_position_size
        if position_size > max_size:
            logger.error(f"Position size {position_size} exceeds maximum {max_size}")
            return False

        return True

    async def register_callback(self, event: str, callback: Callable):
        """Register callback for live trading events"""
        if event not in self._callbacks:
            self._callbacks[event] = []
        self._callbacks[event].append(callback)

    async def _trigger_callbacks(self, event: str):
        """Trigger registered callbacks"""
        if event in self._callbacks:
            for callback in self._callbacks[event]:
                try:
                    await callback(event)
                except Exception as e:
                    logger.error(f"Callback error for {event}: {e}")


# Global live trading manager instance
_live_trading_manager = None


def get_live_trading_manager() -> LiveTradingManager:
    """Get global live trading manager instance"""
    global _live_trading_manager
    if _live_trading_manager is None:
        _live_trading_manager = LiveTradingManager()
    return _live_trading_manager


__all__ = [
    "LiveTradingStatus",
    "TradingMode",
    "RiskConstraint",
    "LiveTradingConfig",
    "RiskConstraints",
    "LiveTradingMetrics",
    "LiveTradingManager",
    "get_live_trading_manager",
]
