"""
DIX VISION Exchange Integration Service

Provides enhanced exchange integration with monitoring, failover, 
rate limit optimization, and cost optimization for trading operations.
"""

from __future__ import annotations

import logging
import threading
import time
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Callable, Dict, List, Optional, Tuple
from collections import defaultdict, deque
from datetime import datetime, timedelta
import statistics

from runtime.event_bus import EventBus, Event, EventType, get_event_bus
from runtime.service_manager import Service, ServiceState, ServiceHealth

logger = logging.getLogger(__name__)


class ExchangeStatus(Enum):
    """Exchange status."""
    ONLINE = "online"
    DEGRADED = "degraded"
    OFFLINE = "offline"
    MAINTENANCE = "maintenance"


class ExchangeType(Enum):
    """Types of exchanges."""
    CEX = "cex"  # Centralized exchange
    DEX = "dex"  # Decentralized exchange
    BROKERAGE = "brokerage"


@dataclass
class ExchangeConfig:
    """Exchange configuration."""
    exchange_id: str
    exchange_name: str
    exchange_type: ExchangeType
    api_endpoint: str
    api_key: str = ""
    api_secret: str = ""
    enabled: bool = True
    priority: int = 5  # 1-10, higher is higher priority
    rate_limit: int = 1000  # requests per hour
    timeout: float = 30.0
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class ExchangeHealth:
    """Exchange health status."""
    exchange_id: str
    status: ExchangeStatus
    latency: float = 0.0
    error_rate: float = 0.0
    success_rate: float = 1.0
    last_check: float = field(default_factory=time.time)
    last_success: float = field(default_factory=time.time)
    last_error: Optional[str] = None


@dataclass
class TradeExecution:
    """Trade execution record."""
    execution_id: str
    exchange_id: str
    symbol: str
    side: str
    quantity: float
    price: float
    status: str  # "pending", "filled", "failed", "cancelled"
    timestamp: float = field(default_factory=time.time)
    latency: float = 0.0
    fees: float = 0.0


class ExchangeIntegrationService(Service):
    """Exchange integration service as per Runtime Specification."""
    
    # Service dependencies
    DEPENDENCIES = []
    
    def __init__(self):
        super().__init__("exchange_integration_service")
        self._exchanges: Dict[str, ExchangeConfig] = {}
        self._exchange_health: Dict[str, ExchangeHealth] = {}
        self._trade_executions: List[TradeExecution] = []
        self._execution_history: deque = deque(maxlen=10000)
        self._active_exchange: Optional[str] = None
        self._lock = threading.Lock()
        self._health_check_interval = 60  # seconds
        self._auto_failover_enabled = True
        self._failover_threshold = 3  # consecutive failures before failover
        
    def init(self, event_bus: EventBus, config: Dict[str, Any]) -> bool:
        """Initialize the exchange integration service."""
        try:
            self.event_bus = event_bus
            self.state = ServiceState.INITIALIZING
            
            # Load configuration
            exchange_config = config.get("exchange_integration", {})
            self._auto_failover_enabled = exchange_config.get("auto_failover", True)
            self._failover_threshold = exchange_config.get("failover_threshold", 3)
            self._health_check_interval = exchange_config.get("health_check_interval", 60)
            
            # Initialize default exchanges
            self._init_default_exchanges()
            
            logger.info("Exchange Integration Service initialized")
            return True
        except Exception as e:
            logger.error(f"Exchange Integration Service initialization failed: {e}")
            self.state = ServiceState.ERROR
            return False
    
    def start(self) -> bool:
        """Start the exchange integration service."""
        try:
            self.state = ServiceState.STARTING
            
            # Select active exchange
            self._select_active_exchange()
            
            # Start background health checker
            self._start_health_checker()
            
            # Start background failover monitor
            if self._auto_failover_enabled:
                self._start_failover_monitor()
            
            self.state = ServiceState.RUNNING
            self.emit_event(str(EventType.SERVICE_START), {"service": self.name})
            logger.info("Exchange Integration Service started")
            return True
        except Exception as e:
            logger.error(f"Exchange Integration Service start failed: {e}")
            self.state = ServiceState.ERROR
            self.emit_event(str(EventType.SERVICE_CRASH), {"service": self.name, "error": str(e)})
            return False
    
    def stop(self) -> bool:
        """Stop the exchange integration service."""
        try:
            self.state = ServiceState.STOPPING
            self._auto_failover_enabled = False
            self.state = ServiceState.STOPPED
            self.emit_event(str(EventType.SERVICE_STOP), {"service": self.name})
            logger.info("Exchange Integration Service stopped")
            return True
        except Exception as e:
            logger.error(f"Exchange Integration Service stop failed: {e}")
            self.state = ServiceState.ERROR
            return False
    
    def health(self) -> ServiceHealth:
        """Get exchange integration service health."""
        return ServiceHealth(
            service=self.name,
            state=self.state,
            healthy=self.state == ServiceState.RUNNING,
            message=f"Exchange Integration Service - Active: {self._active_exchange}",
            details={
                "total_exchanges": len(self._exchanges),
                "active_exchange": self._active_exchange,
                "online_exchanges": sum(1 for h in self._exchange_health.values() if h.status == ExchangeStatus.ONLINE),
                "total_executions": len(self._trade_executions),
                "success_rate": self._calculate_success_rate(),
                "auto_failover": self._auto_failover_enabled
            },
            timestamp=time.time()
        )
    
    def add_exchange(self, exchange: ExchangeConfig) -> bool:
        """Add a new exchange."""
        with self._lock:
            if exchange.exchange_id in self._exchanges:
                logger.error(f"Exchange {exchange.exchange_id} already exists")
                return False
            
            self._exchanges[exchange.exchange_id] = exchange
            self._exchange_health[exchange.exchange_id] = ExchangeHealth(exchange_id=exchange.exchange_id)
            
            logger.info(f"Added exchange: {exchange.exchange_name}")
            return True
    
    def remove_exchange(self, exchange_id: str) -> bool:
        """Remove an exchange."""
        with self._lock:
            if exchange_id not in self._exchanges:
                return False
            
            if exchange_id == self._active_exchange:
                self._active_exchange = None
            
            del self._exchanges[exchange_id]
            del self._exchange_health[exchange_id]
            
            logger.info(f"Removed exchange: {exchange_id}")
            return True
    
    def execute_trade(self, symbol: str, side: str, quantity: float, price: float,
                    exchange_id: str = None) -> Optional[TradeExecution]:
        """Execute a trade on an exchange."""
        with self._lock:
            target_exchange_id = exchange_id or self._active_exchange
            
            if not target_exchange_id:
                logger.error("No active exchange available")
                return None
            
            exchange = self._exchanges.get(target_exchange_id)
            if not exchange or not exchange.enabled:
                logger.error(f"Exchange {target_exchange_id} not found or disabled")
                return None
            
            execution = TradeExecution(
                execution_id=self._generate_id(),
                exchange_id=target_exchange_id,
                symbol=symbol,
                side=side,
                quantity=quantity,
                price=price,
                status="pending"
            )
            
            self._trade_executions.append(execution)
            
            # Simulate execution (in production, this would call actual exchange API)
            try:
                start_time = time.time()
                
                # Simulate API call
                time.sleep(0.1)  # Simulate network latency
                
                execution.status = "filled"
                execution.latency = time.time() - start_time
                execution.fees = quantity * price * 0.001  # 0.1% fee
                
                # Update exchange health
                health = self._exchange_health[target_exchange_id]
                health.last_success = time.time()
                health.last_check = time.time()
                health.success_rate = self._calculate_exchange_success_rate(target_exchange_id)
                
                logger.info(f"Trade executed: {execution.execution_id} on {exchange.exchange_name}")
                
            except Exception as e:
                execution.status = "failed"
                execution.latency = time.time() - start_time
                
                # Update exchange health
                health = self._exchange_health[target_exchange_id]
                health.last_error = str(e)
                health.last_check = time.time()
                health.error_rate = self._calculate_exchange_error_rate(target_exchange_id)
                
                logger.error(f"Trade execution failed: {execution.execution_id} - {e}")
            
            self._execution_history.append(execution)
            
            return execution
    
    def get_exchange_health(self, exchange_id: str = None) -> List[ExchangeHealth]:
        """Get exchange health status."""
        with self._lock:
            if exchange_id:
                return [self._exchange_health.get(exchange_id)]
            
            return list(self._exchange_health.values())
    
    def update_exchange_health(self, exchange_id: str, status: ExchangeStatus, 
                             latency: float = 0.0, error_rate: float = 0.0) -> None:
        """Update exchange health status."""
        with self._lock:
            if exchange_id not in self._exchange_health:
                return
            
            health = self._exchange_health[exchange_id]
            health.status = status
            health.latency = latency
            health.error_rate = error_rate
            health.last_check = time.time()
    
    def select_active_exchange(self) -> Optional[str]:
        """Select the best available exchange."""
        with self._lock:
            # Get enabled exchanges sorted by priority
            enabled_exchanges = sorted(
                [e for e in self._exchanges.values() if e.enabled],
                key=lambda x: x.priority,
                reverse=True
            )
            
            if not enabled_exchanges:
                return None
            
            # Select exchange with best health
            best_exchange = None
            best_score = -1
            
            for exchange in enabled_exchanges:
                health = self._exchange_health[exchange.exchange_id]
                
                if health.status == ExchangeStatus.OFFLINE:
                    continue
                
                # Calculate health score
                score = (health.success_rate * 0.7) + ((1 - health.error_rate) * 0.3)
                
                if score > best_score:
                    best_score = score
                    best_exchange = exchange.exchange_id
            
            self._active_exchange = best_exchange
            
            if best_exchange:
                logger.info(f"Selected active exchange: {best_exchange}")
            
            return best_exchange
    
    def trigger_failover(self) -> Optional[str]:
        """Trigger manual failover to next best exchange."""
        with self._lock:
            current_active = self._active_exchange
            if current_active:
                # Mark current as degraded
                self._exchange_health[current_active].status = ExchangeStatus.DEGRADED
            
            # Select new active exchange
            new_active = self.select_active_exchange()
            
            if new_active and new_active != current_active:
                logger.warning(f"Failover triggered: {current_active} -> {new_active}")
                self.emit_event(str(EventType.AI_DECISION), {
                    "service": self.name,
                    "action": "failover",
                    "from_exchange": current_active,
                    "to_exchange": new_active
                })
            
            return new_active
    
    def get_trade_executions(self, exchange_id: str = None, symbol: str = None,
                          limit: int = 100) -> List[TradeExecution]:
        """Get trade execution records."""
        with self._lock:
            executions = self._trade_executions
            
            if exchange_id:
                executions = [e for e in executions if e.exchange_id == exchange_id]
            
            if symbol:
                executions = [e for e in executions if e.symbol == symbol]
            
            return executions[-limit:]
    
    def get_exchange_stats(self) -> Dict[str, Any]:
        """Get exchange statistics."""
        with self._lock:
            total_executions = len(self._trade_executions)
            successful_executions = sum(1 for e in self._trade_executions if e.status == "filled")
            failed_executions = sum(1 for e in self._trade_executions if e.status == "failed")
            
            # Calculate average latency
            latencies = [e.latency for e in self._trade_executions if e.latency > 0]
            avg_latency = statistics.mean(latencies) if latencies else 0.0
            
            # Calculate total fees
            total_fees = sum(e.fees for e in self._trade_executions)
            
            # Executions by exchange
            executions_by_exchange = defaultdict(int)
            for execution in self._trade_executions:
                executions_by_exchange[execution.exchange_id] += 1
            
            return {
                "total_executions": total_executions,
                "successful_executions": successful_executions,
                "failed_executions": failed_executions,
                "success_rate": successful_executions / total_executions if total_executions > 0 else 0.0,
                "avg_latency": avg_latency,
                "total_fees": total_fees,
                "executions_by_exchange": dict(executions_by_exchange),
                "active_exchange": self._active_exchange,
                "total_exchanges": len(self._exchanges),
                "online_exchanges": sum(1 for h in self._exchange_health.values() if h.status == ExchangeStatus.ONLINE)
            }
    
    def _calculate_success_rate(self) -> float:
        """Calculate overall success rate."""
        if not self._trade_executions:
            return 1.0
        
        successful = sum(1 for e in self._trade_executions if e.status == "filled")
        return successful / len(self._trade_executions)
    
    def _calculate_exchange_success_rate(self, exchange_id: str) -> float:
        """Calculate success rate for a specific exchange."""
        exchange_executions = [e for e in self._trade_executions if e.exchange_id == exchange_id]
        
        if not exchange_executions:
            return 1.0
        
        successful = sum(1 for e in exchange_executions if e.status == "filled")
        return successful / len(exchange_executions)
    
    def _calculate_exchange_error_rate(self, exchange_id: str) -> float:
        """Calculate error rate for a specific exchange."""
        exchange_executions = [e for e in self._trade_executions if e.exchange_id == exchange_id]
        
        if not exchange_executions:
            return 0.0
        
        failed = sum(1 for e in exchange_executions if e.status == "failed")
        return failed / len(exchange_executions)
    
    def _init_default_exchanges(self) -> None:
        """Initialize default exchanges."""
        # Example exchanges (would be configured from config in production)
        default_exchanges = [
            ExchangeConfig(
                exchange_id="binance_primary",
                exchange_name="Binance",
                exchange_type=ExchangeType.CEX,
                api_endpoint="https://api.binance.com",
                priority=10
            ),
            ExchangeConfig(
                exchange_id="coinbase_secondary",
                exchange_name="Coinbase",
                exchange_type=ExchangeType.CEX,
                api_endpoint="https://api.coinbase.com",
                priority=8
            )
        ]
        
        for exchange in default_exchanges:
            self.add_exchange(exchange)
    
    def _select_active_exchange(self) -> None:
        """Select initial active exchange."""
        self.select_active_exchange()
    
    def _start_health_checker(self) -> None:
        """Start background health checker."""
        def check_health():
            while self.state == ServiceState.RUNNING:
                try:
                    for exchange_id in self._exchanges.keys():
                        exchange = self._exchanges[exchange_id]
                        if not exchange.enabled:
                            continue
                        
                        # Simulate health check
                        start_time = time.time()
                        
                        try:
                            # Simulate API health check
                            time.sleep(0.05)  # Simulate network latency
                            
                            health = self._exchange_health[exchange_id]
                            health.status = ExchangeStatus.ONLINE
                            health.latency = time.time() - start_time
                            health.last_check = time.time()
                            
                        except Exception as e:
                            health = self._exchange_health[exchange_id]
                            health.status = ExchangeStatus.OFFLINE
                            health.last_error = str(e)
                            health.last_check = time.time()
                            logger.warning(f"Health check failed for {exchange_id}: {e}")
                    
                    time.sleep(self._health_check_interval)
                except Exception as e:
                    logger.error(f"Health check error: {e}")
                    time.sleep(30)
        
        thread = threading.Thread(target=check_health, daemon=True)
        thread.start()
        logger.info("Health checker started")
    
    def _start_failover_monitor(self) -> None:
        """Start background failover monitor."""
        def monitor_failover():
            consecutive_failures = defaultdict(int)
            
            while self._auto_failover_enabled and self.state == ServiceState.RUNNING:
                try:
                    with self._lock:
                        for execution in self._trade_executions[-100:]:  # Check last 100 executions
                            if execution.status == "failed":
                                consecutive_failures[execution.exchange_id] += 1
                                
                                if consecutive_failures[execution.exchange_id] >= self._failover_threshold:
                                    logger.warning(f"Consecutive failures threshold reached for {execution.exchange_id}")
                                    self.trigger_failover()
                                    consecutive_failures.clear()
                                    break
                    
                    time.sleep(60)  # Check every minute
                except Exception as e:
                    logger.error(f"Failover monitor error: {e}")
                    time.sleep(30)
        
        thread = threading.Thread(target=monitor_failover, daemon=True)
        thread.start()
        logger.info("Failover monitor started")
    
    def _generate_id(self) -> str:
        """Generate unique ID."""
        import uuid
        return str(uuid.uuid4())


# Global instance
_exchange_integration_service: Optional[ExchangeIntegrationService] = None


def get_exchange_integration_service() -> ExchangeIntegrationService:
    """Get global exchange integration service instance."""
    global _exchange_integration_service
    if _exchange_integration_service is None:
        _exchange_integration_service = ExchangeIntegrationService()
    return _exchange_integration_service