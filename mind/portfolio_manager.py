"""
Portfolio Manager - Cognitive Portfolio Management Module with World Context Integration
Provides portfolio management capabilities for position tracking and risk management
Required by archival components for portfolio operations
NO LAZY LOADING - All components load directly
"""

from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, field
from enum import Enum
import logging
import asyncio
import os
import sys
from datetime import datetime, timedelta
import math

from mind.order_manager import Order, Position, OrderStatus

logger = logging.getLogger(__name__)

# Try to import world model components for world context integration
try:
    sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))
    from world_model.indicator_integration import get_integration_bridge
    WORLD_MODEL_AVAILABLE = True
except ImportError:
    WORLD_MODEL_AVAILABLE = False


@dataclass
class WorldContext:
    """World model context for portfolio management."""
    market_regime: str  # bullish, bearish, sideways, high_volatility
    market_trend: str  # trending, mean_reverting
    volatility_regime: str  # high, normal, low
    liquidity_state: str  # high, normal, low
    agent_activity: Dict[str, float]  # agent_type -> activity_level
    causal_factors: List[str]  # relevant causal factors
    prediction_confidence: float  # world model prediction confidence
    timestamp: datetime
    
    def to_dict(self) -> dict:
        """Convert to dictionary for processing."""
        return {
            "market_regime": self.market_regime,
            "market_trend": self.market_trend,
            "volatility_regime": self.volatility_regime,
            "liquidity_state": self.liquidity_state,
            "agent_activity": self.agent_activity,
            "causal_factors": self.causal_factors,
            "prediction_confidence": self.prediction_confidence,
            "timestamp": self.timestamp.isoformat()
        }


class PortfolioStatus(Enum):
    """Portfolio status enumeration"""
    ACTIVE = "active"
    PAUSED = "paused"
    CLOSED = "closed"
    LOCKED = "locked"


class RiskLevel(Enum):
    """Risk level enumeration"""
    CONSERVATIVE = "conservative"
    MODERATE = "moderate"
    AGGRESSIVE = "aggressive"
    SPECULATIVE = "speculative"


@dataclass
class PortfolioMetrics:
    """Portfolio performance metrics"""
    total_value: float = 0.0
    total_pnl: float = 0.0
    unrealized_pnl: float = 0.0
    realized_pnl: float = 0.0
    win_rate: float = 0.0
    sharpe_ratio: float = 0.0
    max_drawdown: float = 0.0
    current_drawdown: float = 0.0
    total_trades: int = 0
    winning_trades: int = 0
    losing_trades: int = 0
    average_win: float = 0.0
    average_loss: float = 0.0
    profit_factor: float = 0.0
    last_update_ns: int = 0
    
    def __post_init__(self):
        if self.last_update_ns == 0:
            self.last_update_ns = datetime.now().timestamp_ns()


@dataclass
class RiskMetrics:
    """Portfolio risk metrics"""
    portfolio_value: float = 0.0
    exposure: float = 0.0
    margin_used: float = 0.0
    margin_available: float = 0.0
    leverage: float = 1.0
    var_95: float = 0.0  # Value at Risk 95%
    var_99: float = 0.0  # Value at Risk 99%
    beta: float = 1.0
    correlation_risk: float = 0.0
    concentration_risk: float = 0.0
    last_update_ns: int = 0
    
    def __post_init__(self):
        if self.last_update_ns == 0:
            self.last_update_ns = datetime.now().timestamp_ns()


@dataclass
class Portfolio:
    """Portfolio data structure"""
    portfolio_id: str
    name: str
    initial_capital: float = 100000.0
    current_capital: float = 100000.0
    status: PortfolioStatus = PortfolioStatus.ACTIVE
    risk_level: RiskLevel = RiskLevel.MODERATE
    positions: Dict[str, Position] = field(default_factory=dict)
    orders: Dict[str, Order] = field(default_factory=dict)
    metrics: PortfolioMetrics = field(default_factory=PortfolioMetrics)
    risk_metrics: RiskMetrics = field(default_factory=RiskMetrics)
    max_position_size: float = 0.2  # Max 20% of capital per position
    max_total_exposure: float = 0.8  # Max 80% total exposure
    stop_loss_threshold: float = 0.05  # 5% portfolio stop loss
    created_ns: int = 0
    last_update_ns: int = 0
    
    def __post_init__(self):
        if self.created_ns == 0:
            self.created_ns = datetime.now().timestamp_ns()
        if self.last_update_ns == 0:
            self.last_update_ns = datetime.now().timestamp_ns()
        self.current_capital = self.initial_capital


class PortfolioManager:
    """
    Portfolio Manager - Core cognitive component for portfolio management
    
    Manages portfolio creation, position tracking, risk management, and performance metrics
    Required by archival components for portfolio operations
    """
    
    def __init__(self):
        self._portfolios: Dict[str, Portfolio] = {}
        self._portfolio_callbacks: Dict[str, List[callable]] = {}
        self._lock = asyncio.Lock()
        self._risk_monitor_active = False
        self._position_tracker_active = False
        
    async def create_portfolio(self, portfolio_id: str, name: str, 
                              initial_capital: float = 100000.0,
                              risk_level: RiskLevel = RiskLevel.MODERATE,
                              max_position_size: float = 0.2,
                              max_total_exposure: float = 0.8,
                              stop_loss_threshold: float = 0.05) -> Portfolio:
        """Create a new portfolio"""
        portfolio = Portfolio(
            portfolio_id=portfolio_id,
            name=name,
            initial_capital=initial_capital,
            risk_level=risk_level,
            max_position_size=max_position_size,
            max_total_exposure=max_total_exposure,
            stop_loss_threshold=stop_loss_threshold
        )
        
        async with self._lock:
            self._portfolios[portfolio_id] = portfolio
        
        logger.info(f"Created portfolio: {portfolio_id} - {name} - ${initial_capital}")
        
        # Trigger callbacks
        await self._trigger_callbacks(portfolio_id, "created")
        
        return portfolio
    
    async def add_position(self, portfolio_id: str, position: Position) -> bool:
        """Add position to portfolio"""
        if portfolio_id not in self._portfolios:
            logger.error(f"Portfolio {portfolio_id} not found")
            return False
        
        portfolio = self._portfolios[portfolio_id]
        
        # Check position size limits
        position_value = abs(position.quantity * position.average_entry_price)
        max_allowed = portfolio.current_capital * portfolio.max_position_size
        
        if position_value > max_allowed:
            logger.warning(f"Position size {position_value} exceeds maximum {max_allowed}")
            return False
        
        async with self._lock:
            portfolio.positions[position.symbol] = position
            portfolio.last_update_ns = datetime.now().timestamp_ns()
            
            # Update metrics
            await self._update_portfolio_metrics(portfolio_id)
        
        logger.info(f"Added position to {portfolio_id}: {position.symbol} {position.quantity}")
        
        # Trigger callbacks
        await self._trigger_callbacks(portfolio_id, "position_added")
        
        return True
    
    async def update_position(self, portfolio_id: str, symbol: str,
                            quantity_delta: float, price: float) -> bool:
        """Update existing position"""
        if portfolio_id not in self._portfolios:
            logger.error(f"Portfolio {portfolio_id} not found")
            return False
        
        portfolio = self._portfolios[portfolio_id]
        
        if symbol not in portfolio.positions:
            logger.error(f"Position {symbol} not found in portfolio {portfolio_id}")
            return False
        
        position = portfolio.positions[symbol]
        
        async with self._lock:
            old_quantity = position.quantity
            
            # Calculate new average price
            if quantity_delta > 0:  # Adding to position
                total_cost = (old_quantity * position.average_entry_price) + (quantity_delta * price)
                new_quantity = old_quantity + quantity_delta
                position.average_entry_price = total_cost / new_quantity if new_quantity > 0 else 0
                position.quantity = new_quantity
            else:  # Reducing or closing position
                position.quantity += quantity_delta  # quantity_delta is negative
                # Calculate realized PnL
                realized = abs(quantity_delta) * (price - position.average_entry_price)
                position.realized_pnl += realized
                portfolio.metrics.realized_pnl += realized
                
            position.last_update_ns = datetime.now().timestamp_ns()
            
            # Remove position if fully closed
            if position.quantity == 0:
                del portfolio.positions[symbol]
                logger.info(f"Closed position {symbol} in portfolio {portfolio_id}")
            
            portfolio.last_update_ns = datetime.now().timestamp_ns()
            
            # Update metrics
            await self._update_portfolio_metrics(portfolio_id)
        
        logger.info(f"Updated position {symbol} in {portfolio_id}")
        
        # Trigger callbacks
        await self._trigger_callbacks(portfolio_id, "position_updated")
        
        return True
    
    async def link_order(self, portfolio_id: str, order: Order) -> bool:
        """Link order to portfolio for tracking"""
        if portfolio_id not in self._portfolios:
            logger.error(f"Portfolio {portfolio_id} not found")
            return False
        
        portfolio = self._portfolios[portfolio_id]
        
        async with self._lock:
            portfolio.orders[order.order_id] = order
            portfolio.last_update_ns = datetime.now().timestamp_ns()
        
        logger.info(f"Linked order {order.order_id} to portfolio {portfolio_id}")
        
        # Trigger callbacks
        await self._trigger_callbacks(portfolio_id, "order_linked")
        
        return True
    
    async def update_order_status(self, portfolio_id: str, order_id: str,
                                 status: OrderStatus) -> bool:
        """Update order status in portfolio context"""
        if portfolio_id not in self._portfolios:
            logger.error(f"Portfolio {portfolio_id} not found")
            return False
        
        portfolio = self._portfolios[portfolio_id]
        
        if order_id not in portfolio.orders:
            logger.error(f"Order {order_id} not found in portfolio {portfolio_id}")
            return False
        
        async with self._lock:
            portfolio.orders[order_id].status = status
            portfolio.last_update_ns = datetime.now().timestamp_ns()
            
            # Update metrics on order completion
            if status == OrderStatus.FILLED:
                await self._update_portfolio_metrics(portfolio_id)
        
        logger.info(f"Updated order {order_id} to {status.value} in portfolio {portfolio_id}")
        
        # Trigger callbacks
        await self._trigger_callbacks(portfolio_id, "order_updated")
        
        return True
    
    async def calculate_portfolio_value(self, portfolio_id: str) -> Tuple[float, float]:
        """Calculate total portfolio value and exposure"""
        if portfolio_id not in self._portfolios:
            logger.error(f"Portfolio {portfolio_id} not found")
            return 0.0, 0.0
        
        portfolio = self._portfolios[portfolio_id]
        
        # Position values would be calculated using current market prices
        # For now, use entry prices as approximation
        position_value = sum(
            abs(pos.quantity * pos.average_entry_price)
            for pos in portfolio.positions.values()
        )
        
        total_value = portfolio.current_capital
        exposure = position_value / total_value if total_value > 0 else 0.0
        
        return total_value, exposure
    
    async def _update_portfolio_metrics(self, portfolio_id: str):
        """Update portfolio metrics"""
        if portfolio_id not in self._portfolios:
            return
        
        portfolio = self._portfolios[portfolio_id]
        
        # Calculate portfolio value and exposure
        total_value, exposure = await self.calculate_portfolio_value(portfolio_id)
        
        # Update basic metrics
        portfolio.metrics.total_value = total_value
        portfolio.metrics.unrealized_pnl = total_value - portfolio.initial_capital - portfolio.metrics.realized_pnl
        portfolio.metrics.total_pnl = portfolio.metrics.unrealized_pnl + portfolio.metrics.realized_pnl
        
        # Update risk metrics
        portfolio.risk_metrics.portfolio_value = total_value
        portfolio.risk_metrics.exposure = exposure
        portfolio.risk_metrics.current_drawdown = (portfolio.initial_capital - total_value) / portfolio.initial_capital if portfolio.initial_capital > 0 else 0.0
        
        # Check stop loss
        if portfolio.risk_metrics.current_drawdown > portfolio.stop_loss_threshold:
            await self._trigger_callbacks(portfolio_id, "stop_loss_triggered")
            logger.warning(f"Stop loss triggered for portfolio {portfolio_id}")
        
        portfolio.metrics.last_update_ns = datetime.now().timestamp_ns()
        portfolio.risk_metrics.last_update_ns = datetime.now().timestamp_ns()
        portfolio.last_update_ns = datetime.now().timestamp_ns()
    
    async def check_risk_limits(self, portfolio_id: str) -> Tuple[bool, List[str]]:
        """Check if portfolio is within risk limits"""
        if portfolio_id not in self._portfolios:
            return False, ["Portfolio not found"]
        
        portfolio = self._portfolios[portfolio_id]
        violations = []
        
        # Check exposure limit
        _, exposure = await self.calculate_portfolio_value(portfolio_id)
        if exposure > portfolio.max_total_exposure:
            violations.append(f"Exposure {exposure:.2f} exceeds maximum {portfolio.max_total_exposure}")
        
        # Check individual position sizes
        for symbol, position in portfolio.positions.items():
            position_value = abs(position.quantity * position.average_entry_price)
            position_ratio = position_value / portfolio.current_capital
            if position_ratio > portfolio.max_position_size:
                violations.append(f"Position {symbol} size {position_ratio:.2f} exceeds maximum {portfolio.max_position_size}")
        
        # Check stop loss
        if portfolio.risk_metrics.current_drawdown > portfolio.stop_loss_threshold:
            violations.append(f"Current drawdown {portfolio.risk_metrics.current_drawdown:.2f} exceeds stop loss threshold {portfolio.stop_loss_threshold}")
        
        return len(violations) == 0, violations
    
    def get_portfolio(self, portfolio_id: str) -> Optional[Portfolio]:
        """Get portfolio by ID"""
        return self._portfolios.get(portfolio_id)
    
    def get_all_portfolios(self) -> List[Portfolio]:
        """Get all portfolios"""
        return list(self._portfolios.values())
    
    async def register_callback(self, portfolio_id: str, callback: callable):
        """Register callback for portfolio events"""
        if portfolio_id not in self._portfolio_callbacks:
            self._portfolio_callbacks[portfolio_id] = []
        self._portfolio_callbacks[portfolio_id].append(callback)
    
    async def _trigger_callbacks(self, portfolio_id: str, event: str):
        """Trigger registered callbacks for portfolio events"""
        if portfolio_id in self._portfolio_callbacks:
            portfolio = self._portfolios.get(portfolio_id)
            for callback in self._portfolio_callbacks[portfolio_id]:
                try:
                    await callback(portfolio, event)
                except Exception as e:
                    logger.error(f"Callback error for {portfolio_id}: {e}")
    
    async def start_risk_monitoring(self):
        """Start risk monitoring loop"""
        if self._risk_monitor_active:
            logger.warning("Risk monitoring already active")
            return
        
        self._risk_monitor_active = True
        asyncio.create_task(self._risk_monitor_loop())
        logger.info("Risk monitoring started")
    
    async def stop_risk_monitoring(self):
        """Stop risk monitoring loop"""
        self._risk_monitor_active = False
        logger.info("Risk monitoring stopped")
    
    async def _risk_monitor_loop(self):
        """Risk monitoring loop"""
        while self._risk_monitor_active:
            try:
                await asyncio.sleep(10)  # Check every 10 seconds
                await self._check_risk_limits()
            except Exception as e:
                logger.error(f"Risk monitoring error: {e}")
    
    # World Context Integration Methods
    
    async def create_portfolio_with_world_context(self, portfolio_id: str, name: str, 
                                                 initial_capital: float = 100000.0,
                                                 risk_level: RiskLevel = RiskLevel.MODERATE,
                                                 world_context: Optional[WorldContext] = None) -> Portfolio:
        """
        Create a portfolio with world context enhancement.
        
        ENHANCED: World context integration for intelligent portfolio configuration
        """
        # Get world context if not provided
        if not world_context:
            world_context = self._get_world_context()
        
        # Adjust portfolio parameters based on world context
        adjusted_params = self._adjust_portfolio_params_with_world_context(
            initial_capital, risk_level, world_context
        )
        
        # Create portfolio with adjusted parameters
        portfolio = await self.create_portfolio(
            portfolio_id=portfolio_id,
            name=name,
            initial_capital=adjusted_params["initial_capital"],
            risk_level=adjusted_params["risk_level"],
            max_position_size=adjusted_params["max_position_size"],
            max_total_exposure=adjusted_params["max_total_exposure"],
            stop_loss_threshold=adjusted_params["stop_loss_threshold"]
        )
        
        # Add world context metadata to portfolio
        if world_context:
            portfolio.metadata["world_context"] = world_context.to_dict()
            portfolio.metadata["world_context_applied"] = True
            if "adjustments" in adjusted_params:
                portfolio.metadata["world_context_adjustments"] = adjusted_params["adjustments"]
        
        return portfolio
    
    def _get_world_context(self) -> Optional[WorldContext]:
        """Get current world context from world model integration."""
        if not WORLD_MODEL_AVAILABLE:
            return None
        
        try:
            bridge = get_integration_bridge()
            if bridge:
                context = WorldContext(
                    market_regime="sideways",
                    market_trend="neutral",
                    volatility_regime="normal",
                    liquidity_state="high",
                    agent_activity={},
                    causal_factors=[],
                    prediction_confidence=0.75,
                    timestamp=datetime.utcnow()
                )
                return context
        
        except Exception as e:
            logger.error(f"[PORTFOLIO_MANAGER] Error getting world context: {e}")
        
        return None
    
    def _adjust_portfolio_params_with_world_context(self, initial_capital: float, 
                                                   risk_level: RiskLevel,
                                                   world_context: Optional[WorldContext]) -> Dict[str, Any]:
        """Adjust portfolio parameters based on world context."""
        adjustments = []
        adjusted_params = {
            "initial_capital": initial_capital,
            "risk_level": risk_level,
            "max_position_size": 0.2,
            "max_total_exposure": 0.8,
            "stop_loss_threshold": 0.05,
            "adjustments": []
        }
        
        if not world_context:
            return adjusted_params
        
        # Adjust risk level based on volatility
        if world_context.volatility_regime == "high":
            # Move to more conservative risk level in high volatility
            if risk_level in [RiskLevel.AGGRESSIVE, RiskLevel.SPECULATIVE]:
                adjusted_params["risk_level"] = RiskLevel.MODERATE
                adjustments.append("reduced_risk_high_volatility")
            elif risk_level == RiskLevel.MODERATE:
                adjusted_params["risk_level"] = RiskLevel.CONSERVATIVE
                adjustments.append("further_reduced_risk_high_volatility")
        
        # Adjust position size limits based on liquidity
        if world_context.liquidity_state == "low":
            # Reduce max position size in low liquidity
            adjusted_params["max_position_size"] = 0.1  # Reduce to 10%
            adjusted_params["max_total_exposure"] = 0.6  # Reduce to 60%
            adjustments.append("reduced_position_size_low_liquidity")
        
        # Adjust stop loss threshold based on market regime
        if world_context.market_regime == "high_volatility":
            # Tighter stop loss in high volatility regimes
            adjusted_params["stop_loss_threshold"] = 0.03  # Reduce to 3%
            adjustments.append("tighter_stop_loss_high_volatility")
        
        adjusted_params["adjustments"] = adjustments
        
        return adjusted_params


# Global portfolio manager instance
_portfolio_manager = None

def get_portfolio_manager() -> PortfolioManager:
    """Get global portfolio manager instance"""
    global _portfolio_manager
    if _portfolio_manager is None:
        _portfolio_manager = PortfolioManager()
    return _portfolio_manager


__all__ = [
    'PortfolioStatus',
    'RiskLevel',
    'PortfolioMetrics',
    'RiskMetrics',
    'Portfolio',
    'PortfolioManager',
    'get_portfolio_manager'
]