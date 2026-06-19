"""
execution_unified.resilience.distributed_resilience
DIX VISION v42.2 — Distributed Execution Resilience (Priority 1)

Provides comprehensive fault tolerance for distributed execution by combining
circuit breaking, adaptive retry, checkpointing, and failover capabilities.
"""

from __future__ import annotations

import logging
import threading
import time
from datetime import datetime
from typing import Any, Dict, List, Optional, Callable, TypeVar
from dataclasses import dataclass, field

from .circuit_breaker import CircuitBreaker, get_circuit_breaker, CircuitBreakerConfig
from .adaptive_retry import AdaptiveRetryStrategy, RetryConfig, RetryResult
from .checkpoint_manager import CheckpointManager, get_checkpoint_manager

logger = logging.getLogger(__name__)

T = TypeVar('T')


@dataclass
class ExecutionResult:
    """Result of resilient execution."""
    
    success: bool
    result: Optional[T] = None
    error: Optional[Exception] = None
    resilience_layers_used: List[str] = field(default_factory=list)
    execution_time_ms: float = 0.0
    fallback_used: bool = False
    checkpoint_restored: bool = False
    circuit_state: Optional[str] = None
    retry_attempts: int = 0


class DistributedExecutionResilience:
    """
    Comprehensive distributed execution resilience system.
    
    Combines multiple resilience layers:
    1. Circuit breaking
    2. Adaptive retry
    3. State checkpointing
    4. Health monitoring
    5. Graceful degradation
    6. Failover capability
    """
    
    def __init__(
        self,
        service_name: str,
        checkpoint_dir: str = "checkpoints"
    ):
        self._service_name = service_name
        self._lock = threading.Lock()
        
        # Resilience components
        self._circuit_breaker = get_circuit_breaker(
            f"{service_name}_circuit",
            CircuitBreakerConfig(failure_threshold=5, timeout_ms=30000)
        )
        self._retry_strategy = AdaptiveRetryStrategy(RetryConfig(max_attempts=3))
        self._checkpoint_manager = get_checkpoint_manager(checkpoint_dir)
        
        # Failover state
        self._primary_active = True
        self._fallback_function: Optional[Callable[[], T]] = None
        
        # Metrics
        self._total_executions = 0
        self._successful_executions = 0
        self._circuit_trips = 0
        self._retry_usage = 0
        self._checkpoint_usage = 0
        
        logger.info(f"[DISTRIBUTED_RESILIENCE] Initialized for {service_name}")
    
    def execute_with_resilience(
        self,
        func: Callable[[], T],
        component: str = "default",
        fallback: Optional[Callable[[], T]] = None,
        enable_checkpoint: bool = True,
        enable_retry: bool = True,
        enable_circuit_breaker: bool = True
    ) -> ExecutionResult:
        """
        Execute function with full resilience protection.
        
        Args:
            func: Function to execute
            component: Component name for checkpointing
            fallback: Fallback function
            enable_checkpoint: Enable checkpointing
            enable_retry: Enable retry
            enable_circuit_breaker: Enable circuit breaking
            
        Returns:
            Execution result with resilience metadata
        """
        self._total_executions += 1
        start_time = time.time()
        resilience_layers = []
        
        # Set fallback
        if fallback:
            self._fallback_function = fallback
        
        # Checkpoint before execution
        checkpoint_id = None
        if enable_checkpoint:
            try:
                # Create checkpoint for current state
                current_state = self._get_current_state()
                checkpoint = self._checkpoint_manager.create_checkpoint(
                    component=component,
                    state_data=current_state,
                    metadata={"service": self._service_name}
                )
                checkpoint_id = checkpoint.checkpoint_id
                resilience_layers.append("checkpoint_created")
                self._checkpoint_usage += 1
            except Exception as e:
                logger.warning(f"[DISTRIBUTED_RESILIENCE] Checkpoint creation failed: {e}")
        
        # Execute with circuit breaking and retry
        if enable_circuit_breaker:
            # Wrap function with circuit breaker
            def circuit_protected_func():
                if enable_retry:
                    retry_result = self._retry_strategy.execute_with_retry(func)
                    resilience_layers.append("retry")
                    self._retry_usage += retry_result.attempts
                    
                    if retry_result.success:
                        return retry_result.result
                    else:
                        raise retry_result.last_error or Exception("Retry failed")
                else:
                    return func()
            
            # Execute with circuit breaker
            circuit_result = self._circuit_breaker.execute(
                circuit_protected_func,
                fallback=self._fallback_function
            )
            
            resilience_layers.append("circuit_breaker")
            self._circuit_state = circuit_result.circuit_state.value
            
            if not circuit_result.success:
                self._circuit_trips += 1
                logger.warning(f"[DISTRIBUTED_RESILIENCE] Circuit breaker opened for {self._service_name}")
                
                # Try fallback
                if self._fallback_function and circuit_result.circuit_state.value == "OPEN":
                    try:
                        fallback_result = self._fallback_function()
                        resilience_layers.append("fallback_used")
                        
                        execution_time_ms = (time.time() - start_time) * 1000
                        return ExecutionResult(
                            success=True,
                            result=fallback_result,
                            resilience_layers_used=resilience_layers,
                            execution_time_ms=execution_time_ms,
                            fallback_used=True,
                            circuit_state=circuit_result.circuit_state.value
                        )
                    except Exception as e:
                        execution_time_ms = (time.time() - start_time) * 1000
                        return ExecutionResult(
                            success=False,
                            error=e,
                            resilience_layers_used=resilience_layers,
                            execution_time_ms=execution_time_ms,
                            fallback_used=True,
                            circuit_state=circuit_result.circuit_state.value
                        )
            
            result = circuit_result.result if hasattr(circuit_result, 'result') else None
            execution_time_ms = circuit_result.execution_time_ms
            
        else:
            # No circuit breaking, execute with retry only
            if enable_retry:
                retry_result = self._retry_strategy.execute_with_retry(func)
                resilience_layers.append("retry")
                self._retry_usage += retry_result.attempts
                
                if retry_result.success:
                    result = retry_result.result
                else:
                    result = None
                    execution_time_ms = retry_result.total_time_ms
                    return ExecutionResult(
                        success=False,
                        error=retry_result.last_error,
                        resilience_layers_used=resilience_layers,
                        execution_time_ms=execution_time_ms,
                        retry_attempts=retry_result.attempts
                    )
            else:
                try:
                    result = func()
                except Exception as e:
                    execution_time_ms = (time.time() - start_time) * 1000
                    return ExecutionResult(
                        success=False,
                        error=e,
                        resilience_layers_used=resilience_layers,
                        execution_time_ms=execution_time_ms
                    )
            
            execution_time_ms = (time.time() - start_time) * 1000
        
        # Update success metrics
        if result is not None:
            self._successful_executions += 1
        
        return ExecutionResult(
            success=True,
            result=result,
            resilience_layers_used=resilience_layers,
            execution_time_ms=execution_time_ms,
            circuit_state=self._circuit_breaker.get_state().value if enable_circuit_breaker else None
        )
    
    def restore_from_checkpoint(self, component: str) -> bool:
        """
        Restore state from latest checkpoint.
        
        Args:
            component: Component name
            
        Returns:
            Success status
        """
        checkpoint = self._checkpoint_manager.get_latest_checkpoint(component)
        if not checkpoint:
            logger.warning(f"[DISTRIBUTED_RESILIENCE] No checkpoint found for {component}")
            return False
        
        restore_result = self._checkpoint_manager.restore_checkpoint(checkpoint.checkpoint_id)
        
        if restore_result.success:
            logger.info(f"[DISTRIBUTED_RESILIENCE] Restored from checkpoint {checkpoint.checkpoint_id}")
            self._apply_restored_state(restore_result.restored_state)
            return True
        else:
            logger.error(f"[DISTRIBUTED_RESILIENCE] Checkpoint restore failed: {restore_result.error_message}")
            return False
    
    def _get_current_state(self) -> Dict[str, Any]:
        """Get current system state for checkpointing."""
        # Placeholder - override with actual state collection
        return {
            "timestamp": datetime.utcnow().isoformat(),
            "service": self._service_name,
            "circuit_state": self._circuit_breaker.get_state().value
        }
    
    def _apply_restored_state(self, state: Dict[str, Any]) -> None:
        """Apply restored state to system."""
        # Placeholder - override with actual state application
        logger.info(f"[DISTRIBUTED_RESILIENCE] Applied restored state from {state.get('timestamp')}")
    
    def get_resilience_statistics(self) -> Dict[str, Any]:
        """Get resilience system statistics."""
        with self._lock:
            circuit_stats = self._circuit_breaker.get_statistics()
            checkpoint_stats = self._checkpoint_manager.get_checkpoint_statistics()
            
            return {
                "service_name": self._service_name,
                "total_executions": self._total_executions,
                "successful_executions": self._successful_executions,
                "success_rate": self._successful_executions / self._total_executions if self._total_executions > 0 else 0.0,
                "circuit_trips": self._circuit_trips,
                "retry_usage": self._retry_usage,
                "checkpoint_usage": self._checkpoint_usage,
                "primary_active": self._primary_active,
                "circuit_breaker": circuit_stats,
                "checkpoint_manager": checkpoint_stats
            }
    
    def reset_circuit_breaker(self) -> None:
        """Reset circuit breaker to closed state."""
        self._circuit_breaker.reset()
        logger.info(f"[DISTRIBUTED_RESILIENCE] Circuit breaker reset for {self._service_name}")


# Singleton instances (per service)
_resilience_managers: Dict[str, DistributedExecutionResilience] = {}
_resilience_managers_lock = threading.Lock()

def get_distributed_resilience(service_name: str, checkpoint_dir: str = "checkpoints") -> DistributedExecutionResilience:
    """Get or create a distributed resilience manager for a service."""
    global _resilience_managers
    if service_name not in _resilience_managers:
        with _resilience_managers_lock:
            if service_name not in _resilience_managers:
                _resilience_managers[service_name] = DistributedExecutionResilience(service_name, checkpoint_dir)
    return _resilience_managers[service_name]


__all__ = [
    "ExecutionResult",
    "DistributedExecutionResilience",
    "get_distributed_resilience",
]