"""
DIX VISION Execution Engine Service

Implements the Execution Engine service as specified in the Runtime Specification.
Handles trade execution, order management, and risk enforcement.
"""

from __future__ import annotations

import logging
import threading
import time
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Dict, List, Optional

from runtime.event_bus import EventBus, Event, EventType, get_event_bus
from runtime.service_manager import Service, ServiceState, ServiceHealth

logger = logging.getLogger(__name__)


class ExecutionState(Enum):
    """Execution engine states."""
    IDLE = "IDLE"
    PROCESSING = "PROCESSING"
    EXECUTING = "EXECUTING"
    ERROR = "ERROR"
    STOPPED = "STOPPED"


@dataclass
class Order:
    """Represents a trading order."""
    order_id: str
    symbol: str
    side: str  # "buy" or "sell"
    quantity: float
    price: float
    timestamp: float = field(default_factory=time.time)
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class ExecutionResult:
    """Result of an order execution."""
    order_id: str
    success: bool
    executed_price: Optional[float]
    executed_quantity: Optional[float]
    error_message: Optional[str]
    execution_time: float = 0.0  # Execution time in seconds
    timestamp: float = field(default_factory=time.time)


class RiskEnforcer:
    """Risk enforcement as per Runtime Specification."""
    
    def __init__(self):
        self.max_position_size = 1000.0
        self.max_daily_loss = 10000.0
        self.current_daily_loss = 0.0
    
    def check_order(self, order: Order) -> tuple[bool, str]:
        """Check if order complies with risk rules."""
        # Check position size
        if order.quantity > self.max_position_size:
            return False, f"Order quantity {order.quantity} exceeds max position size {self.max_position_size}"
        
        # Check daily loss
        if self.current_daily_loss >= self.max_daily_loss:
            return False, f"Daily loss {self.current_daily_loss} exceeds max daily loss {self.max_daily_loss}"
        
        return True, "Order approved by risk enforcer"
    
    def update_daily_loss(self, loss: float) -> None:
        """Update daily loss tracking."""
        self.current_daily_loss += loss


class OrderQueue:
    """Order queue for execution engine."""
    
    def __init__(self):
        self.queue: List[Order] = []
        self._lock = threading.Lock()
    
    def add_order(self, order: Order) -> None:
        """Add order to queue."""
        with self._lock:
            self.queue.append(order)
            logger.info(f"Order added to queue: {order.order_id}")
    
    def get_next_order(self) -> Optional[Order]:
        """Get next order from queue."""
        with self._lock:
            if self.queue:
                return self.queue.pop(0)
            return None
    
    def size(self) -> int:
        """Get queue size."""
        with self._lock:
            return len(self.queue)


class ExecutionEngine(Service):
    """Execution Engine service as per Runtime Specification."""
    
    # Service dependencies
    DEPENDENCIES = ["ai_runtime_engine"]
    
    # Execution timeout configuration
    DEFAULT_EXECUTION_TIMEOUT = 10.0  # seconds
    ORDER_QUEUE_TIMEOUT = 30.0  # seconds for orders waiting in queue
    
    def __init__(self):
        super().__init__("execution_engine")
        self.execution_state = ExecutionState.IDLE
        self.risk_enforcer = RiskEnforcer()
        self.order_queue = OrderQueue()
        self._execution_thread: Optional[threading.Thread] = None
        self._stop_event = threading.Event()
        self.executed_orders: Dict[str, ExecutionResult] = {}
        self.execution_timeout = self.DEFAULT_EXECUTION_TIMEOUT
        self.order_queue_timeout = self.ORDER_QUEUE_TIMEOUT
        self.order_start_times: Dict[str, float] = {}  # Track when orders started
        
    def init(self, event_bus: EventBus, config: Dict[str, Any]) -> bool:
        """Initialize the execution engine."""
        try:
            self.event_bus = event_bus
            self.config = config
            self.state = ServiceState.INITIALIZING
            
            # Load timeout configuration from config
            if config:
                self.execution_timeout = config.get("execution_timeout", self.DEFAULT_EXECUTION_TIMEOUT)
                self.order_queue_timeout = config.get("order_queue_timeout", self.ORDER_QUEUE_TIMEOUT)
            
            # Subscribe to AI decision events for trade execution
            event_bus.subscribe(str(EventType.AI_DECISION), self._handle_ai_decision, self.name)
            
            logger.info("Execution Engine initialized")
            return True
        except Exception as e:
            logger.error(f"Execution Engine initialization failed: {e}")
            self.state = ServiceState.ERROR
            return False
    
    def _handle_ai_decision(self, event: Event) -> None:
        """Handle AI decision events for trade execution."""
        try:
            decision_type = event.payload.get("decision_type")
            
            # If AI decision is a trade, create order
            if decision_type in ["buy", "sell"]:
                order = Order(
                    order_id=f"order_{int(time.time() * 1000)}",
                    symbol="BTCUSDT",  # Placeholder symbol
                    side=decision_type,
                    quantity=1.0,  # Placeholder quantity
                    price=50000.0,  # Placeholder price
                    metadata={"source": "ai_decision", "confidence": event.payload.get("confidence")}
                )
                self.order_queue.add_order(order)
                logger.info(f"Order created from AI decision: {order.order_id}")
        except Exception as e:
            logger.error(f"Error handling AI decision: {e}")
    
    def start(self) -> bool:
        """Start the execution engine."""
        try:
            self.state = ServiceState.STARTING
            self.execution_state = ExecutionState.IDLE
            
            # Emit start event
            self.emit_event(str(EventType.EXECUTION_START), {"state": self.execution_state.value})
            
            # Start execution thread
            self._stop_event.clear()
            self._execution_thread = threading.Thread(target=self._execution_loop, daemon=True)
            self._execution_thread.start()
            
            self.state = ServiceState.RUNNING
            logger.info("Execution Engine started")
            return True
        except Exception as e:
            logger.error(f"Execution Engine start failed: {e}")
            self.state = ServiceState.ERROR
            self.execution_state = ExecutionState.ERROR
            self.emit_event(str(EventType.EXECUTION_ERROR), {"error": str(e)})
            return False
    
    def stop(self) -> bool:
        """Stop the execution engine."""
        try:
            self.state = ServiceState.STOPPING
            self.execution_state = ExecutionState.STOPPED
            
            # Signal stop to execution thread
            self._stop_event.set()
            
            # Wait for execution thread to stop
            if self._execution_thread and self._execution_thread.is_alive():
                self._execution_thread.join(timeout=5)
            
            self.state = ServiceState.STOPPED
            logger.info("Execution Engine stopped")
            return True
        except Exception as e:
            logger.error(f"Execution Engine stop failed: {e}")
            self.state = ServiceState.ERROR
            return False
    
    def health(self) -> ServiceHealth:
        """Get execution engine health."""
        return ServiceHealth(
            service=self.name,
            state=self.state,
            healthy=self.state == ServiceState.RUNNING,
            message=f"Execution State: {self.execution_state.value}",
            details={
                "execution_state": self.execution_state.value,
                "queue_size": self.order_queue.size(),
                "executed_orders": len(self.executed_orders),
                "daily_loss": self.risk_enforcer.current_daily_loss
            },
            timestamp=time.time()
        )
    
    def _execution_loop(self) -> None:
        """Main execution loop with timeout handling."""
        try:
            while not self._stop_event.is_set():
                try:
                    # Check for timeout orders
                    self._check_order_timeouts()
                    
                    # Get next order from queue
                    order = self.order_queue.get_next_order()
                    
                    if order:
                        self.execution_state = ExecutionState.PROCESSING
                        self.order_start_times[order.order_id] = time.time()
                        
                        # Risk check
                        approved, reason = self.risk_enforcer.check_order(order)
                        
                        if not approved:
                            logger.warning(f"Order rejected by risk enforcer: {reason}")
                            result = ExecutionResult(
                                order_id=order.order_id,
                                success=False,
                                executed_price=None,
                                executed_quantity=None,
                                error_message=reason,
                                execution_time=0.0
                            )
                            self.executed_orders[order.order_id] = result
                            self.order_start_times.pop(order.order_id, None)
                            self.emit_event(str(EventType.EXECUTION_ERROR), {
                                "order_id": order.order_id,
                                "reason": reason
                            })
                            continue
                        
                        # Execute order with timeout protection
                        self.execution_state = ExecutionState.EXECUTING
                        logger.info(f"Executing order: {order.order_id}")
                        
                        # Execute with timeout
                        result = self._execute_order_with_timeout(order)
                        
                        self.executed_orders[order.order_id] = result
                        self.order_start_times.pop(order.order_id, None)
                        
                        if result.success:
                            logger.info(f"Order executed successfully: {order.order_id}")
                            # Emit execution complete event
                            self.emit_event(str(EventType.EXECUTION_COMPLETE), {
                                "order_id": order.order_id,
                                "success": True,
                                "executed_price": result.executed_price,
                                "executed_quantity": result.executed_quantity,
                                "execution_time": result.execution_time
                            })
                        else:
                            logger.error(f"Order execution failed: {order.order_id} - {result.error_message}")
                            self.emit_event(str(EventType.EXECUTION_ERROR), {
                                "order_id": order.order_id,
                                "error": result.error_message,
                                "timeout": result.error_message == "Execution timeout"
                            })
                        
                        self.execution_state = ExecutionState.IDLE
                    else:
                        # No orders, wait
                        self._stop_event.wait(1.0)
                        
                except Exception as e:
                    logger.error(f"Execution loop error: {e}")
                    self.execution_state = ExecutionState.ERROR
                    self.emit_event(str(EventType.EXECUTION_ERROR), {"error": str(e)})
                    self._stop_event.wait(5.0)
            
        except Exception as e:
            logger.error(f"Execution loop failed: {e}")
            self.execution_state = ExecutionState.ERROR
            self.emit_event(str(EventType.EXECUTION_ERROR), {"error": str(e)})
    
    def _execute_order_with_timeout(self, order: Order) -> ExecutionResult:
        """Execute order with timeout protection."""
        import threading
        result_container = {"result": None, "exception": None}
        
        def execute():
            try:
                # Simulate execution (replace with actual execution logic)
                time.sleep(0.5)
                
                # Simulate successful execution
                result_container["result"] = ExecutionResult(
                    order_id=order.order_id,
                    success=True,
                    executed_price=order.price,
                    executed_quantity=order.quantity,
                    error_message=None,
                    execution_time=0.5
                )
            except Exception as e:
                result_container["exception"] = e
        
        # Create execution thread
        execution_thread = threading.Thread(target=execute)
        execution_thread.start()
        execution_thread.join(timeout=self.execution_timeout)
        
        if execution_thread.is_alive():
            # Timeout occurred
            logger.error(f"Order execution timeout: {order.order_id}")
            return ExecutionResult(
                order_id=order.order_id,
                success=False,
                executed_price=None,
                executed_quantity=None,
                error_message="Execution timeout",
                execution_time=self.execution_timeout
            )
        
        if result_container["exception"]:
            logger.error(f"Order execution exception: {order.order_id} - {result_container['exception']}")
            return ExecutionResult(
                order_id=order.order_id,
                success=False,
                executed_price=None,
                executed_quantity=None,
                error_message=str(result_container["exception"]),
                execution_time=0.0
            )
        
        return result_container["result"]
    
    def _check_order_timeouts(self) -> None:
        """Check for orders that have been in queue too long."""
        current_time = time.time()
        timed_out_orders = []
        
        for order_id, start_time in list(self.order_start_times.items()):
            if current_time - start_time > self.order_queue_timeout:
                timed_out_orders.append(order_id)
        
        for order_id in timed_out_orders:
            logger.warning(f"Order queue timeout: {order_id}")
            result = ExecutionResult(
                order_id=order_id,
                success=False,
                executed_price=None,
                executed_quantity=None,
                error_message="Order queue timeout"
            )
            self.executed_orders[order_id] = result
            self.order_start_times.pop(order_id, None)
            self.emit_event(str(EventType.EXECUTION_ERROR), {
                "order_id": order_id,
                "error": "Order queue timeout",
                "timeout": True
            })


class AdvancedExecutionEngine(ExecutionEngine):
    """Advanced execution engine with enhanced capabilities."""
    
    def __init__(self):
        super().__init__()
        self.name = "execution_engine_advanced"
        self.slippage_tolerance = 0.01  # 1% slippage tolerance
        self.order_timeout = 30.0  # 30 second order timeout
        
    def _execution_loop(self) -> None:
        """Enhanced execution loop with advanced features."""
        try:
            while not self._stop_event.is_set():
                try:
                    order = self.order_queue.get_next_order()
                    
                    if order:
                        self.execution_state = ExecutionState.PROCESSING
                        
                        # Enhanced risk check
                        approved, reason = self.risk_enforcer.check_order(order)
                        
                        if not approved:
                            logger.warning(f"Order rejected: {reason}")
                            result = ExecutionResult(
                                order_id=order.order_id,
                                success=False,
                                executed_price=None,
                                executed_quantity=None,
                                error_message=reason,
                                execution_time=0.0
                            )
                            self.executed_orders[order.order_id] = result
                            self.emit_event(str(EventType.EXECUTION_ERROR), {
                                "order_id": order.order_id,
                                "reason": reason,
                                "advanced_mode": True
                            })
                            continue
                        
                        # Enhanced execution with slippage check
                        self.execution_state = ExecutionState.EXECUTING
                        logger.info(f"Advanced execution: {order.order_id}")
                        
                        # Simulate execution with slippage
                        time.sleep(0.5)
                        
                        # Apply slippage
                        slippage = order.price * self.slippage_tolerance
                        executed_price = order.price + slippage if order.side == "buy" else order.price - slippage
                        
                        result = ExecutionResult(
                            order_id=order.order_id,
                            success=True,
                            executed_price=executed_price,
                            executed_quantity=order.quantity,
                            error_message=None
                        )
                        
                        self.executed_orders[order.order_id] = result
                        logger.info(f"Advanced order executed: {order.order_id} @ {executed_price}")
                        
                        self.emit_event(str(EventType.EXECUTION_COMPLETE), {
                            "order_id": order.order_id,
                            "success": True,
                            "executed_price": result.executed_price,
                            "executed_quantity": result.executed_quantity,
                            "slippage": slippage,
                            "advanced_mode": True
                        })
                        
                        self.execution_state = ExecutionState.IDLE
                    else:
                        self._stop_event.wait(1.0)
                        
                except Exception as e:
                    logger.error(f"Advanced execution loop error: {e}")
                    self.execution_state = ExecutionState.ERROR
                    self.emit_event(str(EventType.EXECUTION_ERROR), {"error": str(e)})
                    self._stop_event.wait(5.0)
            
        except Exception as e:
            logger.error(f"Advanced execution loop failed: {e}")
            self.execution_state = ExecutionState.ERROR
            self.emit_event(str(EventType.EXECUTION_ERROR), {"error": str(e)})


__all__ = [
    "ExecutionEngine",
    "AdvancedExecutionEngine",
    "ExecutionState",
    "Order",
    "ExecutionResult",
    "RiskEnforcer",
    "OrderQueue",
]