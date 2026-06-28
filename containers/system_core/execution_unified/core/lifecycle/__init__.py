"""
Execution Unified Core Lifecycle - Lifecycle Management Infrastructure
Provides lifecycle management for orders and positions
NO LAZY LOADING - All components load directly
"""

import asyncio
import logging
from datetime import datetime
from typing import Any, Dict, List, Optional

logger = logging.getLogger(__name__)


class FillHandler:
    """Handler for order fills and partial fills"""

    def __init__(self):
        self._fills: Dict[str, Dict[str, Any]] = {}

    async def handle_fill(self, order_id: str, fill_data: Dict[str, Any]) -> bool:
        """Handle order fill"""
        fill_id = f"fill_{datetime.now().timestamp_ns()}"
        self._fills[fill_id] = {
            "order_id": order_id,
            "fill_data": fill_data,
            "timestamp": datetime.now().timestamp_ns(),
        }
        logger.info(f"Handled fill {fill_id} for order {order_id}")
        return True

    async def handle_partial_fill(self, order_id: str, partial_fill_data: Dict[str, Any]) -> bool:
        """Handle partial order fill"""
        return await self.handle_fill(order_id, partial_fill_data)


class OrderStateMachine:
    """State machine for order lifecycle management"""

    def __init__(self):
        self._order_states: Dict[str, str] = {}
        self._state_transitions: Dict[str, List[str]] = {
            "pending": ["submitted", "cancelled"],
            "submitted": ["partial", "filled", "cancelled"],
            "partial": ["partial", "filled", "cancelled"],
            "filled": [],
            "cancelled": [],
        }

    async def transition_state(self, order_id: str, new_state: str) -> bool:
        """Transition order to new state"""
        current_state = self._order_states.get(order_id, "pending")

        if new_state in self._state_transitions.get(current_state, []):
            self._order_states[order_id] = new_state
            logger.info(f"Order {order_id} transitioned to {new_state}")
            return True
        else:
            logger.warning(f"Invalid state transition {current_state} -> {new_state}")
            return False

    def get_state(self, order_id: str) -> Optional[str]:
        """Get current order state"""
        return self._order_states.get(order_id)


class PartialFillResolver:
    """Resolver for partial fill situations"""

    def __init__(self):
        self._resolutions: Dict[str, Dict[str, Any]] = {}

    async def resolve_partial_fill(
        self, order_id: str, fill_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Resolve partial fill situation"""
        resolution = {
            "order_id": order_id,
            "action": "continue",
            "remaining_quantity": fill_data.get("remaining_quantity", 0),
            "strategy": "immediate",
        }
        self._resolutions[order_id] = resolution
        return resolution


class RetryLogic:
    """Retry logic for failed operations"""

    def __init__(self):
        self._retry_config: Dict[str, int] = {"max_retries": 3, "retry_delay_seconds": 1}

    async def retry_operation(self, operation: callable, *args, **kwargs) -> Any:
        """Retry an operation with exponential backoff"""
        for attempt in range(self._retry_config["max_retries"]):
            try:
                return await operation(*args, **kwargs)
            except Exception as e:
                if attempt == self._retry_config["max_retries"] - 1:
                    raise e
                await asyncio.sleep(self._retry_config["retry_delay_seconds"] * (2**attempt))


class SLTPManager:
    """Stop-loss and take-profit manager"""

    def __init__(self):
        self._sltp_orders: Dict[str, Dict[str, Any]] = {}

    async def set_stop_loss(self, position_id: str, stop_loss_price: float) -> bool:
        """Set stop loss for position"""
        self._sltp_orders[f"sl_{position_id}"] = {
            "position_id": position_id,
            "type": "stop_loss",
            "price": stop_loss_price,
            "active": True,
        }
        return True

    async def set_take_profit(self, position_id: str, take_profit_price: float) -> bool:
        """Set take profit for position"""
        self._sltp_orders[f"tp_{position_id}"] = {
            "position_id": position_id,
            "type": "take_profit",
            "price": take_profit_price,
            "active": True,
        }
        return True

    async def check_triggers(self, current_price: float) -> List[str]:
        """Check if any SL/TP orders should trigger"""
        triggered = []
        for order_id, order_data in self._sltp_orders.items():
            if order_data["active"]:
                if order_data["type"] == "stop_loss" and current_price <= order_data["price"]:
                    triggered.append(order_id)
                elif order_data["type"] == "take_profit" and current_price >= order_data["price"]:
                    triggered.append(order_id)
        return triggered


# Global instances
_fill_handler = None
_order_state_machine = None
_partial_fill_resolver = None
_retry_logic = None
_sltp_manager = None


def get_fill_handler() -> FillHandler:
    """Get fill handler instance"""
    global _fill_handler
    if _fill_handler is None:
        _fill_handler = FillHandler()
    return _fill_handler


def get_order_state_machine() -> OrderStateMachine:
    """Get order state machine instance"""
    global _order_state_machine
    if _order_state_machine is None:
        _order_state_machine = OrderStateMachine()
    return _order_state_machine


def get_partial_fill_resolver() -> PartialFillResolver:
    """Get partial fill resolver instance"""
    global _partial_fill_resolver
    if _partial_fill_resolver is None:
        _partial_fill_resolver = PartialFillResolver()
    return _partial_fill_resolver


def get_retry_logic() -> RetryLogic:
    """Get retry logic instance"""
    global _retry_logic
    if _retry_logic is None:
        _retry_logic = RetryLogic()
    return _retry_logic


def get_sltp_manager() -> SLTPManager:
    """Get SLTP manager instance"""
    global _sltp_manager
    if _sltp_manager is None:
        _sltp_manager = SLTPManager()
    return _sltp_manager


__all__ = [
    "FillHandler",
    "OrderStateMachine",
    "PartialFillResolver",
    "RetryLogic",
    "SLTPManager",
    "get_fill_handler",
    "get_order_state_machine",
    "get_partial_fill_resolver",
    "get_retry_logic",
    "get_sltp_manager",
]
