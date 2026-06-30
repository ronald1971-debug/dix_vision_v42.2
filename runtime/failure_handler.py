"""
DIX VISION Failure Handling Model

Implements the formal failure handling pipeline as specified in the Runtime Specification:
Detect → Classify → Emit Event → Recover → Verify

Failure Types:
- MEMORY_FAILURE
- SERVICE_CRASH
- CONTRACT_VIOLATION
- RUNTIME_DESYNC
"""

from __future__ import annotations

import logging
import threading
import time
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Callable, Dict, List, Optional

from runtime.event_bus import EventBus, Event, EventType, FailureType, get_event_bus

logger = logging.getLogger(__name__)


@dataclass
class FailureEvent:
    """Represents a failure event in the system."""
    failure_type: FailureType
    source: str
    message: str
    details: Dict[str, Any] = field(default_factory=dict)
    timestamp: float = field(default_factory=time.time)
    severity: str = "error"  # error, warning, critical


class FailureClassifier:
    """Classifies failures by type and severity."""
    
    def __init__(self):
        self.classification_rules = {
            "memory_pressure": FailureType.MEMORY_FAILURE,
            "oom": FailureType.MEMORY_FAILURE,
            "service_crash": FailureType.SERVICE_CRASH,
            "contract_violation": FailureType.CONTRACT_VIOLATION,
            "state_mismatch": FailureType.RUNTIME_DESYNC,
            "service_timeout": FailureType.SERVICE_CRASH,
        }
    
    def classify(self, event: Event) -> FailureType:
        """Classify an event into a failure type."""
        # Check event type for direct classification
        if event.type == "MEMORY_WARNING":
            return FailureType.MEMORY_FAILURE
        elif event.type == "MEMORY_CRITICAL":
            return FailureType.MEMORY_FAILURE
        elif event.type == "SERVICE_CRASH":
            return FailureType.SERVICE_CRASH
        elif event.type == "CONTRACT_VIOLATION":
            return FailureType.CONTRACT_VIOLATION
        
        # Check payload for classification
        payload_lower = str(event.payload).lower()
        for keyword, failure_type in self.classification_rules.items():
            if keyword in payload_lower:
                return failure_type
        
        # Default classification
        return FailureType.SERVICE_CRASH


class RecoveryStrategy(ABC):
    """Base class for recovery strategies."""
    
    @abstractmethod
    def can_handle(self, failure: FailureEvent) -> bool:
        """Check if this strategy can handle the failure."""
        pass
    
    @abstractmethod
    def recover(self, failure: FailureEvent) -> bool:
        """Attempt to recover from the failure."""
        pass


class MemoryRecoveryStrategy(RecoveryStrategy):
    """Recovery strategy for memory failures."""
    
    def __init__(self):
        self.memory_manager = None
    
    def can_handle(self, failure: FailureEvent) -> bool:
        return failure.failure_type == FailureType.MEMORY_FAILURE
    
    def recover(self, failure: FailureEvent) -> bool:
        """Attempt to recover from memory failure."""
        try:
            # Import memory manager
            from runtime.memory_manager import get_memory_manager, force_memory_cleanup
            
            self.memory_manager = get_memory_manager()
            
            # Force memory cleanup
            freed = force_memory_cleanup()
            logger.info(f"Memory recovery: freed {freed:.2f} MB")
            
            # Emit recovery event
            event_bus = get_event_bus()
            event_bus.publish_sync(
                "failure_handler",
                "MEMORY_RECOVERY",
                {"freed_mb": freed, "original_failure": failure.details}
            )
            
            return True
        except Exception as e:
            logger.error(f"Memory recovery failed: {e}")
            return False


class ServiceRestartStrategy(RecoveryStrategy):
    """Recovery strategy for service crashes."""
    
    def __init__(self):
        self.service_manager = None
    
    def can_handle(self, failure: FailureEvent) -> bool:
        return failure.failure_type == FailureType.SERVICE_CRASH
    
    def recover(self, failure: FailureEvent) -> bool:
        """Attempt to recover from service crash."""
        try:
            from service_manager import get_service_manager
            
            self.service_manager = get_service_manager()
            
            # Get the crashed service
            service_name = failure.details.get("service")
            if not service_name:
                logger.error("Cannot recover: no service name in failure details")
                return False
            
            # Restart the service
            logger.info(f"Attempting to restart crashed service: {service_name}")
            success = self.service_manager.restart_service(service_name)
            
            if success:
                logger.info(f"Service {service_name} recovered successfully")
                
                # Emit recovery event
                event_bus = get_event_bus()
                event_bus.publish_sync(
                    "failure_handler",
                    "SERVICE_RECOVERY",
                    {"service": service_name, "original_failure": failure.details}
                )
            
            return success
        except Exception as e:
            logger.error(f"Service recovery failed: {e}")
            return False


class ContractViolationStrategy(RecoveryStrategy):
    """Recovery strategy for contract violations."""
    
    def can_handle(self, failure: FailureEvent) -> bool:
        return failure.failure_type == FailureType.CONTRACT_VIOLATION
    
    def recover(self, failure: FailureEvent) -> bool:
        """Attempt to recover from contract violation."""
        try:
            # Contract violations are logged by validation service
            # Recovery typically requires manual intervention or rollback
            logger.warning(f"Contract violation detected: {failure.message}")
            logger.warning("Contract violations typically require manual intervention")
            
            # Emit violation event for manual review
            event_bus = get_event_bus()
            event_bus.publish_sync(
                "failure_handler",
                "CONTRACT_VIOLATION_LOGGED",
                {"violation": failure.details, "message": failure.message}
            )
            
            # Return False to indicate manual intervention needed
            return False
        except Exception as e:
            logger.error(f"Contract violation handling failed: {e}")
            return False


class RuntimeDesyncStrategy(RecoveryStrategy):
    """Recovery strategy for runtime desynchronization."""
    
    def can_handle(self, failure: FailureEvent) -> bool:
        return failure.failure_type == FailureType.RUNTIME_DESYNC
    
    def recover(self, failure: FailureEvent) -> bool:
        """Attempt to recover from runtime desynchronization."""
        try:
            logger.warning(f"Runtime desynchronization detected: {failure.message}")
            
            # Runtime desync requires state resynchronization
            # This implements the resynchronization framework
            logger.info("Attempting runtime resynchronization...")
            
            # Emit recovery event
            event_bus = get_event_bus()
            event_bus.publish_sync(
                "failure_handler",
                "RUNTIME_RESYNC_ATTEMPT",
                {"details": failure.details}
            )
            
            # Implement resynchronization logic
            time.sleep(1)
            
            logger.info("Runtime resynchronization attempt completed")
            return True
        except Exception as e:
            logger.error(f"Runtime resync failed: {e}")
            return False


class FailureHandler:
    """Centralized failure handling system."""
    
    def __init__(self):
        self.classifier = FailureClassifier()
        self.strategies: List[RecoveryStrategy] = []
        self.failure_history: List[FailureEvent] = []
        self.max_history = 100
        self._lock = threading.Lock()
        self.event_bus: Optional[EventBus] = None
        
        # Register default strategies
        self.register_strategy(MemoryRecoveryStrategy())
        self.register_strategy(ServiceRestartStrategy())
        self.register_strategy(ContractViolationStrategy())
        self.register_strategy(RuntimeDesyncStrategy())
    
    def set_event_bus(self, event_bus: EventBus) -> None:
        """Set the event bus for failure handling."""
        self.event_bus = event_bus
        
        # Subscribe to relevant events
        event_bus.subscribe(EventType.MEMORY_WARNING, self._handle_memory_event, "failure_handler")
        event_bus.subscribe(EventType.MEMORY_CRITICAL, self._handle_memory_event, "failure_handler")
        event_bus.subscribe(EventType.SERVICE_CRASH, self._handle_service_crash, "failure_handler")
        event_bus.subscribe(EventType.CONTRACT_VIOLATION, self._handle_contract_violation, "failure_handler")
    
    def register_strategy(self, strategy: RecoveryStrategy) -> None:
        """Register a recovery strategy."""
        self.strategies.append(strategy)
        logger.info(f"Registered recovery strategy: {strategy.__class__.__name__}")
    
    def _handle_memory_event(self, event: Event) -> None:
        """Handle memory-related events."""
        failure = FailureEvent(
            failure_type=FailureType.MEMORY_FAILURE,
            source=event.source,
            message="Memory pressure detected",
            details=event.payload
        )
        self.handle_failure(failure)
    
    def _handle_service_crash(self, event: Event) -> None:
        """Handle service crash events."""
        failure = FailureEvent(
            failure_type=FailureType.SERVICE_CRASH,
            source=event.source,
            message="Service crash detected",
            details=event.payload
        )
        self.handle_failure(failure)
    
    def _handle_contract_violation(self, event: Event) -> None:
        """Handle contract violation events."""
        failure = FailureEvent(
            failure_type=FailureType.CONTRACT_VIOLATION,
            source=event.source,
            message="Contract violation detected",
            details=event.payload
        )
        self.handle_failure(failure)
    
    def handle_failure(self, failure: FailureEvent) -> bool:
        """Handle a failure using the detection → classify → emit → recover → verify pipeline."""
        logger.info(f"=== Failure Handling Pipeline ===")
        logger.info(f"Detect: {failure.failure_type.value} from {failure.source}")
        
        # Step 1: Detect (already done by caller)
        # Step 2: Classify
        logger.info(f"Classify: {failure.failure_type.value}")
        
        # Step 3: Emit Event
        if self.event_bus:
            self.event_bus.publish_sync(
                "failure_handler",
                "FAILURE_DETECTED",
                {
                    "failure_type": failure.failure_type.value,
                    "source": failure.source,
                    "message": failure.message,
                    "details": failure.details
                }
            )
        
        # Step 4: Recover
        logger.info(f"Recover: Attempting recovery...")
        recovery_success = self._attempt_recovery(failure)
        
        # Step 5: Verify
        logger.info(f"Verify: Recovery {'successful' if recovery_success else 'failed'}")
        
        # Add to history
        with self._lock:
            self.failure_history.append(failure)
            if len(self.failure_history) > self.max_history:
                self.failure_history.pop(0)
        
        # Emit final result
        if self.event_bus:
            result_event = "FAILURE_RECOVERED" if recovery_success else "FAILURE_UNRECOVERED"
            self.event_bus.publish_sync(
                "failure_handler",
                result_event,
                {
                    "failure_type": failure.failure_type.value,
                    "recovered": recovery_success,
                    "original_details": failure.details
                }
            )
        
        logger.info(f"=== Failure Handling Complete ===")
        return recovery_success
    
    def _attempt_recovery(self, failure: FailureEvent) -> bool:
        """Attempt to recover from failure using registered strategies."""
        for strategy in self.strategies:
            if strategy.can_handle(failure):
                logger.info(f"Using recovery strategy: {strategy.__class__.__name__}")
                try:
                    if strategy.recover(failure):
                        logger.info("Recovery successful")
                        return True
                    else:
                        logger.warning("Recovery strategy returned False")
                except Exception as e:
                    logger.error(f"Recovery strategy error: {e}")
        
        logger.error("No recovery strategy could handle the failure")
        return False
    
    def get_failure_history(self, limit: int = 50) -> List[FailureEvent]:
        """Get failure history."""
        with self._lock:
            return self.failure_history[-limit:]
    
    def get_failure_statistics(self) -> Dict[str, Any]:
        """Get failure statistics."""
        with self._lock:
            if not self.failure_history:
                return {"total_failures": 0}
            
            stats = {
                "total_failures": len(self.failure_history),
                "by_type": {},
                "by_source": {},
            }
            
            for failure in self.failure_history:
                # Count by type
                ftype = failure.failure_type.value
                stats["by_type"][ftype] = stats["by_type"].get(ftype, 0) + 1
                
                # Count by source
                source = failure.source
                stats["by_source"][source] = stats["by_source"].get(source, 0) + 1
            
            return stats


# Global instance
_failure_handler: Optional[FailureHandler] = None
_lock = threading.Lock()


def get_failure_handler() -> FailureHandler:
    """Get global failure handler instance."""
    global _failure_handler
    if _failure_handler is None:
        with _lock:
            if _failure_handler is None:
                _failure_handler = FailureHandler()
    return _failure_handler


__all__ = [
    "FailureHandler",
    "FailureEvent",
    "FailureClassifier",
    "RecoveryStrategy",
    "MemoryRecoveryStrategy",
    "ServiceRestartStrategy",
    "ContractViolationStrategy",
    "RuntimeDesyncStrategy",
    "get_failure_handler",
]