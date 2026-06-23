"""
Execution Unified Core - Core Infrastructure for Execution System
Provides core execution capabilities required by archival components
NO LAZY LOADING - All components load directly
"""

import asyncio
import logging
from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from typing import Any, Callable, Dict, List, Optional

logger = logging.getLogger(__name__)


class ExecutionMode(Enum):
    """Execution mode enumeration"""

    PAPER = "paper"
    LIVE = "live"
    SIMULATION = "simulation"
    BACKTEST = "backtest"


class OrderPriority(Enum):
    """Order priority enumeration"""

    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    URGENT = "urgent"


class OrderRouting(Enum):
    """Order routing strategy"""

    DIRECT = "direct"
    SMART = "smart"
    BEST_PRICE = "best_price"
    FASTEST = "fastest"


@dataclass
class ExecutionConfig:
    """Execution system configuration"""

    mode: ExecutionMode = ExecutionMode.PAPER
    default_priority: OrderPriority = OrderPriority.MEDIUM
    default_routing: OrderRouting = OrderRouting.SMART
    max_order_size: float = 1000000.0
    max_order_rate: int = 100  # orders per minute
    enable_slippage_protection: bool = True
    enable_mev_protection: bool = True
    timeout_seconds: int = 30
    retry_attempts: int = 3


@dataclass
class ExecutionMetrics:
    """Execution performance metrics"""

    total_orders: int = 0
    successful_orders: int = 0
    failed_orders: int = 0
    average_fill_time_ms: float = 0.0
    average_slippage_bps: float = 0.0
    total_volume: float = 0.0
    total_pnl: float = 0.0
    last_update_ns: int = 0

    def __post_init__(self):
        if self.last_update_ns == 0:
            self.last_update_ns = datetime.now().timestamp_ns()


class ExecutionEngine:
    """
    Execution Engine - Core execution infrastructure

    Provides core execution capabilities required by archival components
    """

    def __init__(self, config: Optional[ExecutionConfig] = None):
        self._config = config or ExecutionConfig()
        self._metrics = ExecutionMetrics()
        self._active_orders: Dict[str, Dict[str, Any]] = {}
        self._order_queue: asyncio.Queue = asyncio.Queue()
        self._processing = False
        self._callbacks: Dict[str, List[Callable]] = {}
        self._lock = asyncio.Lock()

    async def initialize(self) -> bool:
        """Initialize execution engine"""
        logger.info(f"Initializing execution engine in {self._config.mode.value} mode")
        return True

    async def start(self) -> bool:
        """Start execution engine"""
        if self._processing:
            logger.warning("Execution engine already running")
            return True

        self._processing = True
        asyncio.create_task(self._process_orders())
        logger.info("Execution engine started")

        # Trigger callbacks
        await self._trigger_callbacks("engine_started")

        return True

    async def stop(self) -> bool:
        """Stop execution engine"""
        self._processing = False
        logger.info("Execution engine stopped")

        # Trigger callbacks
        await self._trigger_callbacks("engine_stopped")

        return True

    async def submit_order(self, order_data: Dict[str, Any]) -> str:
        """Submit order for execution"""
        order_id = f"exec_order_{datetime.now().timestamp_ns()}"

        order = {
            "order_id": order_id,
            "order_data": order_data,
            "submitted_at": datetime.now().timestamp_ns(),
            "status": "pending",
        }

        async with self._lock:
            self._active_orders[order_id] = order
            self._metrics.total_orders += 1

        # Queue order for processing
        await self._order_queue.put(order_id)

        logger.info(f"Submitted order: {order_id}")

        # Trigger callbacks
        await self._trigger_callbacks(f"order_submitted_{order_id}")

        return order_id

    async def cancel_order(self, order_id: str) -> bool:
        """Cancel order"""
        if order_id not in self._active_orders:
            logger.error(f"Order {order_id} not found")
            return False

        async with self._lock:
            self._active_orders[order_id]["status"] = "cancelled"

        logger.info(f"Cancelled order: {order_id}")

        # Trigger callbacks
        await self._trigger_callbacks(f"order_cancelled_{order_id}")

        return True

    async def get_order_status(self, order_id: str) -> Optional[str]:
        """Get order status"""
        order = self._active_orders.get(order_id)
        return order["status"] if order else None

    async def get_metrics(self) -> ExecutionMetrics:
        """Get execution metrics"""
        return self._metrics

    async def _process_orders(self):
        """Process orders from queue"""
        while self._processing:
            try:
                order_id = await asyncio.wait_for(self._order_queue.get(), timeout=1.0)
                await self._execute_order(order_id)
            except asyncio.TimeoutError:
                continue
            except Exception as e:
                logger.error(f"Order processing error: {e}")

    async def _execute_order(self, order_id: str):
        """Execute a single order"""
        logger.debug(f"Executing order {order_id}")

        # Placeholder for actual execution logic
        # In real implementation, this would interface with exchanges
        # and execute the order based on the execution mode

        async with self._lock:
            if order_id in self._active_orders:
                self._active_orders[order_id]["status"] = "executed"
                self._metrics.successful_orders += 1

        # Trigger callbacks
        await self._trigger_callbacks(f"order_executed_{order_id}")

    async def register_callback(self, event: str, callback: Callable):
        """Register callback for execution events"""
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


# Global execution engine instance
_execution_engine = None


def get_execution_engine() -> ExecutionEngine:
    """Get global execution engine instance"""
    global _execution_engine
    if _execution_engine is None:
        _execution_engine = ExecutionEngine()
    return _execution_engine


__all__ = [
    "ExecutionMode",
    "OrderPriority",
    "OrderRouting",
    "ExecutionConfig",
    "ExecutionMetrics",
    "ExecutionEngine",
    "get_execution_engine",
]
