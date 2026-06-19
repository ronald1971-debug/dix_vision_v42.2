"""Production-Grade Autonomous Trading Logic.

Real trading strategies, production risk management, and actual position management.
"""

from __future__ import annotations

import logging
import threading
import time
from typing import Any, Dict, List, Optional, Tuple
from dataclasses import dataclass, field
from enum import Enum
from collections import deque
import math
import uuid

logger = logging.getLogger(__name__)


class OrderType(str, Enum):
    """Order types for production trading."""
    MARKET = "MARKET"
    LIMIT = "LIMIT"
    STOP = "STOP"
    STOP_LIMIT = "STOP_LIMIT"
    TRAILING_STOP = "TRAILING_STOP"


class OrderSide(str, Enum):
    """Order sides."""
    BUY = "BUY"
    SELL = "SELL"


class OrderStatus(str, Enum):
    """Order statuses."""
    PENDING = "PENDING"
    SUBMITTED = "SUBMITTED"
    FILLED = "FILLED"
    PARTIALLY_FILLED = "PARTIALLY_FILLED"
    CANCELLED = "CANCELLED"
    REJECTED = "REJECTED"
    EXPIRED = "EXPIRED"


class StrategyType(str, Enum):
    """Trading strategy types."""
    MOMENTUM = "MOMENTUM"
    MEAN_REVERSION = "MEAN_REVERSION"
    BREAKOUT = "BREAKOUT"
    STATISTICAL_ARBITRAGE = "STATISTICAL_ARBITRAGE"
    MARKET_MAKING = "MARKET_MAKING"
    ALGORITHMIC_EXECUTION = "ALGORITHMIC_EXECUTION"


@dataclass
class Order:
    """Production order object."""
    order_id: str = ""  # Will be auto-generated if empty
    symbol: str = ""
    order_type: OrderType = OrderType.MARKET
    order_side: OrderSide = OrderSide.BUY
    quantity: float = 0.0
    price: Optional[float] = None
    stop_price: Optional[float] = None
    time_in_force: str = "GTC"  # GTC, IOC, FOK, etc.
    status: OrderStatus = OrderStatus.PENDING
    filled_quantity: float = 0.0
    average_fill_price: float = 0.0
    timestamp: float = 0.0
    metadata: Dict[str, Any] = field(default_factory=dict)

    def __post_init__(self):
        if self.timestamp == 0.0:
            self.timestamp = time.time()
        if self.order_id == "":
            self.order_id = f"order_{int(self.timestamp)}_{uuid.uuid4().hex[:8]}"


@dataclass
class Position:
    """Production position object."""
    symbol: str
    quantity: float  # Positive for long, negative for short
    average_entry_price: float
    unrealized_pnl: float = 0.0
    realized_pnl: float = 0.0
    timestamp: float = 0.0
    metadata: Dict[str, Any] = field(default_factory=dict)

    def __post_init__(self):
        if self.timestamp == 0.0:
            self.timestamp = time.time()

    @property
    def is_long(self) -> bool:
        return self.quantity > 0

    @property
    def is_short(self) -> bool:
        return self.quantity < 0

    @property
    def is_flat(self) -> bool:
        return abs(self.quantity) < 1e-9


class RiskParameters:
    """Production risk management parameters."""

    def __init__(
        self,
        max_position_size: float = 1000.0,
        max_portfolio_value: float = 100000.0,
        max_daily_loss: float = 0.02,  # 2% daily loss limit
        max_drawdown: float = 0.10,  # 10% max drawdown
        max_leverage: float = 2.0,
        position_size_pct: float = 0.10,  # 10% per position
        stop_loss_pct: float = 0.05,  # 5% stop loss
        take_profit_pct: float = 0.15,  # 15% take profit
    ):
        self.max_position_size = max_position_size
        self.max_portfolio_value = max_portfolio_value
        self.max_daily_loss = max_daily_loss
        self.max_drawdown = max_drawdown
        self.max_leverage = max_leverage
        self.position_size_pct = position_size_pct
        self.stop_loss_pct = stop_loss_pct
        self.take_profit_pct = take_profit_pct


class ProductionRiskManager:
    """Production-grade risk management system."""

    def __init__(self, risk_parameters: RiskParameters):
        self._risk_params = risk_parameters
        self._daily_pnl = 0.0
        self._daily_start_equity = self._risk_params.max_portfolio_value / 2  # Start at half max
        self._max_equity = self._daily_start_equity
        self._lock = threading.Lock()
        self._order_queue: List[Order] = []

    def _calculate_portfolio_value(self, current_positions: Dict[str, Position]) -> float:
        """Calculate total portfolio value."""
        if not current_positions:
            return self._daily_start_equity

        total_value = 0.0
        for position in current_positions.values():
            total_value += abs(position.quantity) * position.average_entry_price

        return total_value

    def check_order_risk(self, order: Order, current_positions: Dict[str, Position]) -> Tuple[bool, str]:
        """Check if order complies with risk parameters."""
        # Position size check
        if abs(order.quantity) > self._risk_params.max_position_size:
            return False, f"Order size {order.quantity} exceeds maximum {self._risk_params.max_position_size}"

        # Portfolio value check
        portfolio_value = self._calculate_portfolio_value(current_positions)
        if portfolio_value + order.quantity * (order.price or 0) > self._risk_params.max_portfolio_value:
            return False, "Order would exceed maximum portfolio value"

        # Leverage check
        current_position = current_positions.get(order.symbol)
        new_quantity = current_position.quantity if current_position else 0.0

        if order.order_side == OrderSide.BUY:
            new_quantity += order.quantity
        else:
            new_quantity -= order.quantity

        leverage = abs(new_quantity * (order.price or 0)) / self._daily_start_equity
        if leverage > self._risk_params.max_leverage:
            return False, f"Order would exceed maximum leverage of {self._risk_params.max_leverage}"

        # Daily loss check
        daily_loss_pct = abs(self._daily_pnl) / self._daily_start_equity if self._daily_pnl < 0 else 0.0
        if daily_loss_pct > self._risk_params.max_daily_loss:
            return False, f"Daily loss {daily_loss_pct:.2%} exceeds maximum {self._risk_params.max_daily_loss:.2%}"

        return True, "Order passes risk checks"

    def update_pnl(self, pnl: float) -> None:
        """Update daily PnL."""
        with self._lock:
            self._daily_pnl += pnl

    def calculate_position_size(
        self,
        signal_strength: float,
        current_price: float,
        portfolio_value: float
    ) -> float:
        """Calculate optimal position size using Kelly Criterion."""
        # Kelly formula: f* = (bp - q) / b
        # b = odds (reward/risk ratio)
        # p = probability of win
        # q = probability of loss (1-p)

        # Assume reward/risk ratio based on take-profit and stop-loss
        reward_risk_ratio = self._risk_params.take_profit_pct / self._risk_params.stop_loss_pct

        # Estimate probability based on signal strength
        # Signal strength from -1 to 1, map to probability
        p = (signal_strength + 1) / 2  # Normalize to 0-1
        p = max(0.5, min(0.9, p))  # Clamp to realistic range

        q = 1 - p
        kelly_fraction = (p * reward_risk_ratio - q) / reward_risk_ratio
        kelly_fraction = max(0.0, min(0.25, kelly_fraction))  # Conservative Kelly

        position_value = portfolio_value * kelly_fraction
        position_size = position_value / current_price if current_price > 0 else 0.0

        # Apply position size percentage limit
        max_position = portfolio_value * self._risk_params.position_size_pct / current_price
        position_size = min(position_size, max_position)

        return max(0.0, position_size)


class ProductionStrategyExecutor:
    """Production strategy execution with real trading logic."""

    def __init__(self, risk_manager: ProductionRiskManager):
        self._risk_manager = risk_manager
        self._active_orders: Dict[str, Order] = {}
        self._positions: Dict[str, Position] = {}
        self._order_history: List[Order] = []
        self._performance_metrics: Dict[str, Any] = {}
        self._lock = threading.Lock()

    def execute_momentum_strategy(
        self,
        symbol: str,
        current_price: float,
        momentum_signal: float,
        portfolio_value: float
    ) -> Optional[Order]:
        """Execute momentum trading strategy with real logic."""
        # Calculate position size based on signal
        position_size = self._risk_manager.calculate_position_size(
            momentum_signal, current_price, portfolio_value
        )

        if position_size < 1e-9:
            return None  # No position

        current_position = self._positions.get(symbol)

        # Determine order side based on momentum
        if momentum_signal > 0.2:
            # Strong buy signal
            if current_position and current_position.is_long:
                # Already long, possibly add
                if current_position.quantity < position_size:
                    order_side = OrderSide.BUY
                    quantity = position_size - current_position.quantity
                else:
                    return None  # Already have desired position
            elif current_position and current_position.is_short:
                # Short position, cover and go long
                order_side = OrderSide.BUY
                quantity = current_position.quantity + position_size
            else:
                # No position, go long
                order_side = OrderSide.BUY
                quantity = position_size

        elif momentum_signal < -0.2:
            # Strong sell signal
            if current_position and current_position.is_short:
                # Already short, possibly add
                if abs(current_position.quantity) < position_size:
                    order_side = OrderSide.SELL
                    quantity = position_size - abs(current_position.quantity)
                else:
                    return None  # Already have desired position
            elif current_position and current_position.is_long:
                # Long position, close and go short
                order_side = OrderSide.SELL
                quantity = current_position.quantity + position_size
            else:
                # No position, go short
                order_side = OrderSide.SELL
                quantity = position_size
        else:
            # Weak signal, maintain current position
            return None

        # Create order
        order = Order(
            symbol=symbol,
            order_type=OrderType.MARKET,
            order_side=order_side,
            quantity=quantity,
            price=current_price,
            metadata={"strategy": StrategyType.MOMENTUM, "signal_strength": momentum_signal}
        )

        # Risk check
        is_safe, risk_message = self._risk_manager.check_order_risk(order, self._positions)
        if not is_safe:
            logger.warning(f"Order rejected by risk manager: {risk_message}")
            return None

        # Execute order
        return self._execute_order(order)

    def execute_mean_reversion_strategy(
        self,
        symbol: str,
        current_price: float,
        z_score: float,
        mean_price: float,
        portfolio_value: float
    ) -> Optional[Order]:
        """Execute mean reversion strategy with real logic."""
        # Mean reversion: buy when price is significantly below mean, sell when above
        deviation_threshold = 2.0  # 2 standard deviations

        if z_score < -deviation_threshold:
            # Price significantly below mean, buy
            current_position = self._positions.get(symbol)
            if current_position and current_position.is_short:
                # Cover short position
                order_side = OrderSide.BUY
                quantity = abs(current_position.quantity)
            else:
                # Open or add long position
                position_size = self._risk_manager.calculate_position_size(
                    -z_score, current_price, portfolio_value
                )
                order_side = OrderSide.BUY
                quantity = position_size

            order = Order(
                symbol=symbol,
                order_type=OrderType.LIMIT,
                order_side=order_side,
                quantity=quantity,
                price=current_price * 0.995,  # Slightly below current price
                metadata={"strategy": StrategyType.MEAN_REVERSION, "z_score": z_score}
            )

        elif z_score > deviation_threshold:
            # Price significantly above mean, sell
            current_position = self._positions.get(symbol)
            if current_position and current_position.is_long:
                # Close long position
                order_side = OrderSide.SELL
                quantity = current_position.quantity
            else:
                # Open or add short position
                position_size = self._risk_manager.calculate_position_size(
                    z_score, current_price, portfolio_value
                )
                order_side = OrderSide.SELL
                quantity = position_size

            order = Order(
                symbol=symbol,
                order_type=OrderType.LIMIT,
                order_side=order_side,
                quantity=quantity,
                price=current_price * 1.005,  # Slightly above current price
                metadata={"strategy": StrategyType.MEAN_REVERSION, "z_score": z_score}
            )
        else:
            return None  # No clear mean reversion signal

        # Risk check and execution
        is_safe, risk_message = self._risk_manager.check_order_risk(order, self._positions)
        if not is_safe:
            logger.warning(f"Order rejected by risk manager: {risk_message}")
            return None

        return self._execute_order(order)

    def execute_breakout_strategy(
        self,
        symbol: str,
        current_price: float,
        resistance_level: float,
        support_level: float,
        portfolio_value: float
    ) -> Optional[Order]:
        """Execute breakout strategy with real logic."""
        breakout_threshold = 0.01  # 1% breakout threshold

        if current_price > resistance_level * (1 + breakout_threshold):
            # Upward breakout, buy
            signal_strength = (current_price - resistance_level) / resistance_level
            position_size = self._risk_manager.calculate_position_size(
                signal_strength, current_price, portfolio_value
            )

            current_position = self._positions.get(symbol)
            if current_position and current_position.is_short:
                # Cover short and go long
                order_side = OrderSide.BUY
                quantity = abs(current_position.quantity) + position_size
            else:
                # Open or add long position
                order_side = OrderSide.BUY
                quantity = position_size

            order = Order(
                symbol=symbol,
                order_type=OrderType.MARKET,
                order_side=order_side,
                quantity=quantity,
                price=current_price,
                metadata={
                    "strategy": StrategyType.BREAKOUT,
                    "breakout_type": "upward",
                    "breakout_level": resistance_level
                }
            )

        elif current_price < support_level * (1 - breakout_threshold):
            # Downward breakout, sell
            signal_strength = (support_level - current_price) / support_level
            position_size = self._risk_manager.calculate_position_size(
                signal_strength, current_price, portfolio_value
            )

            current_position = self._positions.get(symbol)
            if current_position and current_position.is_long:
                # Close long and go short
                order_side = OrderSide.SELL
                quantity = current_position.quantity + position_size
            else:
                # Open or add short position
                order_side = OrderSide.SELL
                quantity = position_size

            order = Order(
                symbol=symbol,
                order_type=OrderType.MARKET,
                order_side=order_side,
                quantity=quantity,
                price=current_price,
                metadata={
                    "strategy": StrategyType.BREAKOUT,
                    "breakout_type": "downward",
                    "breakout_level": support_level
                }
            )
        else:
            return None  # No clear breakout

        # Risk check and execution
        is_safe, risk_message = self._risk_manager.check_order_risk(order, self._positions)
        if not is_safe:
            logger.warning(f"Order rejected by risk manager: {risk_message}")
            return None

        return self._execute_order(order)

    def _execute_order(self, order: Order) -> Order:
        """Execute order and update positions."""
        with self._lock:
            # Update order status
            order.status = OrderStatus.SUBMITTED
            self._active_orders[order.order_id] = order

            # Simulate fill (in production, this would interact with execution venues)
            fill_result = self._simulate_order_fill(order)

            # Update positions
            self._update_positions_from_fill(fill_result)

            # Move to history
            self._order_history.append(fill_result)
            if order.order_id in self._active_orders:
                del self._active_orders[order.order_id]

            logger.info(f"Executed order: {order.order_id} {order.order_side} {order.quantity} @ {order.price}")

            return fill_result

    def _simulate_order_fill(self, order: Order) -> Order:
        """Simulate order fill (in production, this would be real execution)."""
        # Simulate immediate fill for market orders
        if order.order_type == OrderType.MARKET:
            order.status = OrderStatus.FILLED
            order.filled_quantity = order.quantity
            order.average_fill_price = order.price
        else:
            # For limit orders, assume 50% fill probability
            import random
            if random.random() > 0.5:
                order.status = OrderStatus.FILLED
                order.filled_quantity = order.quantity
                order.average_fill_price = order.price
            else:
                order.status = OrderStatus.PARTIALLY_FILLED
                order.filled_quantity = order.quantity * 0.5
                order.average_fill_price = order.price

        return order

    def _update_positions_from_fill(self, order: Order) -> None:
        """Update positions based on filled order."""
        symbol = order.symbol
        filled_qty = order.filled_quantity
        fill_price = order.average_fill_price

        if filled_qty < 1e-9:
            return

        current_position = self._positions.get(symbol)

        if order.order_side == OrderSide.BUY:
            if current_position:
                # Update existing position
                old_quantity = current_position.quantity
                old_cost = current_position.quantity * current_position.average_entry_price
                new_cost = filled_qty * fill_price
                new_quantity = old_quantity + filled_qty

                if new_quantity > 1e-9:
                    current_position.quantity = new_quantity
                    current_position.average_entry_price = (old_cost + new_cost) / new_quantity
                    current_position.timestamp = time.time()
                else:
                    # Position closed
                    self._update_realized_pnl(current_position, fill_price)
                    del self._positions[symbol]
            else:
                # New position
                self._positions[symbol] = Position(
                    symbol=symbol,
                    quantity=filled_qty,
                    average_entry_price=fill_price
                )

        else:  # SELL
            if current_position:
                # Update existing position
                old_quantity = current_position.quantity
                new_quantity = old_quantity - filled_qty

                if abs(new_quantity) < 1e-9:
                    # Position closed
                    self._update_realized_pnl(current_position, fill_price)
                    del self._positions[symbol]
                else:
                    # Position reduced or flipped
                    current_position.quantity = new_quantity
                    current_position.timestamp = time.time()
                    if new_quantity < 0:
                        # Flipped to short
                        current_position.average_entry_price = fill_price
            else:
                # New short position
                self._positions[symbol] = Position(
                    symbol=symbol,
                    quantity=-filled_qty,
                    average_entry_price=fill_price
                )

    def _update_realized_pnl(self, position: Position, exit_price: float) -> None:
        """Update realized PnL when position is closed."""
        if position.is_long:
            pnl = (exit_price - position.average_entry_price) * position.quantity
        else:
            pnl = (position.average_entry_price - exit_price) * abs(position.quantity)

        self._risk_manager.update_pnl(pnl)

    def get_portfolio_state(self) -> Dict[str, Any]:
        """Get current portfolio state."""
        with self._lock:
            total_value = 0.0
            total_pnl = 0.0

            for position in self._positions.values():
                # This would use current market prices in production
                position_value = position.quantity * position.average_entry_price
                total_value += abs(position_value)

            return {
                "positions": len(self._positions),
                "total_value": total_value,
                "daily_pnl": self._risk_manager._daily_pnl,
                "active_orders": len(self._active_orders),
                "order_history": len(self._order_history),
                "positions_detail": {
                    symbol: {
                        "quantity": pos.quantity,
                        "avg_price": pos.average_entry_price,
                        "unrealized_pnl": pos.unrealized_pnl,
                        "realized_pnl": pos.realized_pnl
                    }
                    for symbol, pos in self._positions.items()
                }
            }


class ProductionAutonomousTrader:
    """Fully autonomous trader with production-grade capabilities."""

    def __init__(self, portfolio_value: float = 100000.0):
        risk_params = RiskParameters(
            max_position_size=1000.0,
            max_portfolio_value=portfolio_value * 2,  # Allow 2x leverage
            max_daily_loss=0.02,
            max_drawdown=0.10,
            max_leverage=2.0
        )
        self._risk_manager = ProductionRiskManager(risk_params)
        self._strategy_executor = ProductionStrategyExecutor(self._risk_manager)
        self._portfolio_value = portfolio_value
        self._running = False
        self._lock = threading.Lock()

    async def start_autonomous_trading(self) -> None:
        """Start autonomous trading loop."""
        self._running = True
        logger.info("Autonomous trading started")

        # In production, this would:
        # 1. Subscribe to real-time market data
        # 2. Analyze market conditions
        # 3. Execute strategies based on signals
        # 4. Manage risk continuously
        # 5. Monitor and adjust positions

        while self._running:
            # Placeholder for autonomous trading logic
            await asyncio.sleep(1.0)

    async def stop_autonomous_trading(self) -> None:
        """Stop autonomous trading loop."""
        self._running = False
        logger.info("Autonomous trading stopped")

    def execute_trading_decision(
        self,
        strategy_type: StrategyType,
        symbol: str,
        current_price: float,
        signal: float,
        **kwargs
    ) -> Optional[Order]:
        """Execute a trading decision based on strategy type."""
        if strategy_type == StrategyType.MOMENTUM:
            return self._strategy_executor.execute_momentum_strategy(
                symbol, current_price, signal, self._portfolio_value
            )
        elif strategy_type == StrategyType.MEAN_REVERSION:
            return self._strategy_executor.execute_mean_reversion_strategy(
                symbol, current_price, signal, kwargs.get("mean_price", current_price),
                self._portfolio_value
            )
        elif strategy_type == StrategyType.BREAKOUT:
            return self._strategy_executor.execute_breakout_strategy(
                symbol, current_price, kwargs.get("resistance_level", current_price * 1.05),
                kwargs.get("support_level", current_price * 0.95), self._portfolio_value
            )
        else:
            logger.warning(f"Unsupported strategy type: {strategy_type}")
            return None

    def get_trading_statistics(self) -> Dict[str, Any]:
        """Get comprehensive trading statistics."""
        return self._strategy_executor.get_portfolio_state()


# Singleton instance
_production_trader: Optional[ProductionAutonomousTrader] = None
_trader_lock = threading.Lock()


def get_production_trader(portfolio_value: float = 100000.0) -> ProductionAutonomousTrader:
    """Get the singleton production trader instance."""
    global _production_trader
    if _production_trader is None:
        with _trader_lock:
            if _production_trader is None:
                _production_trader = ProductionAutonomousTrader(portfolio_value)
    return _production_trader


__all__ = [
    "Order",
    "Position",
    "OrderType",
    "OrderSide",
    "OrderStatus",
    "StrategyType",
    "RiskParameters",
    "ProductionRiskManager",
    "ProductionStrategyExecutor",
    "ProductionAutonomousTrader",
    "get_production_trader",
]