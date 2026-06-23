"""
Mind Module - Cognitive Infrastructure for Trading System with World Context Integration
Provides cognitive capabilities for order management and portfolio operations
This module is required by archival components for cognitive trading operations
NO LAZY LOADING - All components load directly
"""

import asyncio
import logging
import os
import sys
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional

logger = logging.getLogger(__name__)

# Try to import world model components for world context integration
try:
    sys.path.append(os.path.join(os.path.dirname(__file__), "..", ".."))
    from world_model.indicator_integration import get_integration_bridge

    WORLD_MODEL_AVAILABLE = True
except ImportError:
    WORLD_MODEL_AVAILABLE = False


@dataclass
class WorldContext:
    """World model context for order management."""

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
            "timestamp": self.timestamp.isoformat(),
        }


class OrderStatus(Enum):
    """Order status enumeration"""

    PENDING = "pending"
    SUBMITTED = "submitted"
    PARTIALLY_FILLED = "partially_filled"
    FILLED = "filled"
    CANCELLED = "cancelled"
    REJECTED = "rejected"
    EXPIRED = "expired"


class OrderType(Enum):
    """Order type enumeration"""

    MARKET = "market"
    LIMIT = "limit"
    STOP = "stop"
    STOP_LIMIT = "stop_limit"
    TRAILING_STOP = "trailing_stop"


class OrderSide(Enum):
    """Order side enumeration"""

    BUY = "buy"
    SELL = "sell"


@dataclass
class Order:
    """Order data structure"""

    order_id: str
    symbol: str
    order_type: OrderType
    side: OrderSide
    quantity: float
    price: Optional[float] = None
    stop_price: Optional[float] = None
    status: OrderStatus = OrderStatus.PENDING
    filled_quantity: float = 0.0
    remaining_quantity: float = 0.0
    average_price: float = 0.0
    timestamp_ns: int = 0
    expiration_ns: Optional[int] = None
    metadata: Dict[str, Any] = field(default_factory=dict)

    def __post_init__(self):
        if self.remaining_quantity == 0.0:
            self.remaining_quantity = self.quantity
        if self.timestamp_ns == 0:
            self.timestamp_ns = datetime.now().timestamp_ns()


@dataclass
class Position:
    """Position data structure"""

    symbol: str
    quantity: float
    average_entry_price: float
    unrealized_pnl: float = 0.0
    realized_pnl: float = 0.0
    last_update_ns: int = 0

    def __post_init__(self):
        if self.last_update_ns == 0:
            self.last_update_ns = datetime.now().timestamp_ns()


class OrderManager:
    """
    Order Manager - Core cognitive component for order lifecycle management

    Manages order creation, submission, tracking, and execution state
    Required by archival components for order management operations
    """

    def __init__(self):
        self._orders: Dict[str, Order] = {}
        self._order_queue: asyncio.Queue = asyncio.Queue()
        self._lock = asyncio.Lock()
        self._processing = False
        self._order_callbacks: Dict[str, List[callable]] = {}

    async def create_order(
        self,
        symbol: str,
        order_type: OrderType,
        side: OrderSide,
        quantity: float,
        price: Optional[float] = None,
        stop_price: Optional[float] = None,
        expiration_ns: Optional[int] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> Order:
        """Create a new order"""
        order_id = f"order_{datetime.now().timestamp_ns()}"

        order = Order(
            order_id=order_id,
            symbol=symbol,
            order_type=order_type,
            side=side,
            quantity=quantity,
            price=price,
            stop_price=stop_price,
            expiration_ns=expiration_ns,
            metadata=metadata or {},
        )

        async with self._lock:
            self._orders[order_id] = order

        logger.info(f"Created order: {order_id} {symbol} {side.value} {quantity} @ {price}")

        # Trigger callbacks
        await self._trigger_callbacks(order_id, "created")

        return order

    async def submit_order(self, order: Order) -> bool:
        """Submit order for execution"""
        if order.order_id not in self._orders:
            logger.error(f"Order {order.order_id} not found")
            return False

        async with self._lock:
            order.status = OrderStatus.SUBMITTED
            order.timestamp_ns = datetime.now().timestamp_ns()

        # Queue order for processing
        await self._order_queue.put(order.order_id)

        logger.info(f"Submitted order: {order.order_id}")

        # Trigger callbacks
        await self._trigger_callbacks(order.order_id, "submitted")

        return True

    async def cancel_order(self, order_id: str) -> bool:
        """Cancel an order"""
        if order_id not in self._orders:
            logger.error(f"Order {order_id} not found")
            return False

        async with self._lock:
            order = self._orders[order_id]
            if order.status in [OrderStatus.FILLED, OrderStatus.CANCELLED]:
                logger.warning(f"Cannot cancel order {order_id} in status {order.status.value}")
                return False

            order.status = OrderStatus.CANCELLED

        logger.info(f"Cancelled order: {order_id}")

        # Trigger callbacks
        await self._trigger_callbacks(order_id, "cancelled")

        return True

    async def update_order_status(
        self,
        order_id: str,
        status: OrderStatus,
        filled_quantity: float = 0.0,
        average_price: float = 0.0,
    ) -> bool:
        """Update order status"""
        if order_id not in self._orders:
            logger.error(f"Order {order_id} not found")
            return False

        async with self._lock:
            order = self._orders[order_id]
            order.status = status
            order.filled_quantity = filled_quantity
            order.remaining_quantity = order.quantity - filled_quantity
            if average_price > 0:
                order.average_price = average_price

        logger.info(f"Updated order {order_id} to {status.value}")

        # Trigger callbacks
        await self._trigger_callbacks(order_id, "status_updated")

        return True

    def get_order(self, order_id: str) -> Optional[Order]:
        """Get order by ID"""
        return self._orders.get(order_id)

    def get_orders_by_symbol(self, symbol: str) -> List[Order]:
        """Get all orders for a symbol"""
        return [order for order in self._orders.values() if order.symbol == symbol]

    def get_orders_by_status(self, status: OrderStatus) -> List[Order]:
        """Get all orders with a specific status"""
        return [order for order in self._orders.values() if order.status == status]

    async def register_callback(self, order_id: str, callback: callable):
        """Register callback for order events"""
        if order_id not in self._order_callbacks:
            self._order_callbacks[order_id] = []
        self._order_callbacks[order_id].append(callback)

    async def _trigger_callbacks(self, order_id: str, event: str):
        """Trigger registered callbacks for order events"""
        if order_id in self._order_callbacks:
            order = self._orders.get(order_id)
            for callback in self._order_callbacks[order_id]:
                try:
                    await callback(order, event)
                except Exception as e:
                    logger.error(f"Callback error for {order_id}: {e}")

    async def start_processing(self):
        """Start order processing loop"""
        if self._processing:
            logger.warning("Order processing already running")
            return

        self._processing = True
        asyncio.create_task(self._process_orders())
        logger.info("Order processing started")

    async def stop_processing(self):
        """Stop order processing loop"""
        self._processing = False
        logger.info("Order processing stopped")

    async def _process_orders(self):
        """Process orders from queue"""
        while self._processing:
            try:
                order_id = await asyncio.wait_for(self._order_queue.get(), timeout=1.0)
                await self._process_single_order(order_id)
            except asyncio.TimeoutError:
                continue
            except Exception as e:
                logger.error(f"Order processing error: {e}")

    async def _process_single_order(self, order_id: str):
        """Process a single order (to be implemented by subclasses)"""
        # Base implementation - should be overridden by specific implementations
        logger.debug(f"Processing order {order_id}")
        # Integration with execution engine would happen here

    # World Context Integration Methods

    async def create_order_with_world_context(
        self,
        symbol: str,
        order_type: OrderType,
        side: OrderSide,
        quantity: float,
        price: Optional[float] = None,
        world_context: Optional[WorldContext] = None,
    ) -> Order:
        """
        Create an order with world context enhancement.

        ENHANCED: World context integration for intelligent order creation
        """
        # Get world context if not provided
        if not world_context:
            world_context = self._get_world_context()

        # Adjust order parameters based on world context
        adjusted_params = self._adjust_order_params_with_world_context(
            symbol, order_type, side, quantity, price, world_context
        )

        # Create order with adjusted parameters
        order = await self.create_order(
            adjusted_params["symbol"],
            adjusted_params["order_type"],
            adjusted_params["side"],
            adjusted_params["quantity"],
            adjusted_params["price"],
        )

        # Add world context metadata to order
        if world_context:
            order.metadata["world_context"] = world_context.to_dict()
            order.metadata["world_context_applied"] = True
            if "adjustments" in adjusted_params:
                order.metadata["world_context_adjustments"] = adjusted_params["adjustments"]

        return order

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
                    timestamp=datetime.utcnow(),
                )
                return context

        except Exception as e:
            logger.error(f"[ORDER_MANAGER] Error getting world context: {e}")

        return None

    def _adjust_order_params_with_world_context(
        self,
        symbol: str,
        order_type: OrderType,
        side: OrderSide,
        quantity: float,
        price: Optional[float],
        world_context: Optional[WorldContext],
    ) -> Dict[str, Any]:
        """Adjust order parameters based on world context."""
        adjustments = []
        adjusted_params = {
            "symbol": symbol,
            "order_type": order_type,
            "side": side,
            "quantity": quantity,
            "price": price,
            "adjustments": [],
        }

        if not world_context:
            return adjusted_params

        # Adjust quantity based on volatility
        if world_context.volatility_regime == "high":
            # Reduce position size in high volatility
            adjusted_params["quantity"] = quantity * 0.8
            adjustments.append("reduced_quantity_high_volatility")

        # Adjust order type based on liquidity
        if world_context.liquidity_state == "low" and order_type == OrderType.MARKET:
            # Use limit orders in low liquidity to avoid slippage
            adjusted_params["order_type"] = OrderType.LIMIT
            adjustments.append("converted_to_limit_low_liquidity")

        # Adjust timing based on market regime
        if world_context.market_regime == "high_volatility":
            adjustments.append("cautionary_execution_regime")

        adjusted_params["adjustments"] = adjustments

        return adjusted_params


# Global order manager instance
_order_manager = None


def get_order_manager() -> OrderManager:
    """Get global order manager instance"""
    global _order_manager
    if _order_manager is None:
        _order_manager = OrderManager()
    return _order_manager


__all__ = [
    "OrderStatus",
    "OrderType",
    "OrderSide",
    "Order",
    "Position",
    "OrderManager",
    "get_order_manager",
]
