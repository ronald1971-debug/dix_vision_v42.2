"""
DIX VISION AI Runtime Engine Service

Implements the AI Runtime Contract as specified in the Runtime Specification:
INIT → LOAD MEMORY → RESTORE SESSION → RUN LOOP → UPDATE MEMORY → REPORT STATE

AI Rules:
- AI cannot bypass memory system
- AI cannot directly write to disk state
- AI must emit events for all decisions
- AI must be stateless at computation level, stateful via memory layer
"""

from __future__ import annotations

import logging
import threading
import time
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Dict, List, Optional
from datetime import datetime, timedelta

from runtime.event_bus import EventBus, Event, EventType, get_event_bus
from runtime.service_manager import Service, ServiceState, ServiceHealth

logger = logging.getLogger(__name__)


class CircuitBreakerState(Enum):
    """Circuit breaker states."""
    CLOSED = "CLOSED"  # Normal operation
    OPEN = "OPEN"      # Circuit is open, blocking requests
    HALF_OPEN = "HALF_OPEN"  # Testing if circuit should close


class CircuitBreaker:
    """Circuit breaker pattern implementation for AI decision loop."""
    
    def __init__(self, 
                 failure_threshold: int = 5,
                 recovery_timeout: float = 60.0,
                 success_threshold: int = 2):
        """
        Initialize circuit breaker.
        
        Args:
            failure_threshold: Number of failures before opening circuit
            recovery_timeout: Seconds to wait before trying half-open state
            success_threshold: Number of successes needed to close circuit
        """
        self.failure_threshold = failure_threshold
        self.recovery_timeout = recovery_timeout
        self.success_threshold = success_threshold
        
        self.state = CircuitBreakerState.CLOSED
        self.failure_count = 0
        self.success_count = 0
        self.last_failure_time = None
        self.last_state_change = datetime.now()
        
    def record_success(self) -> None:
        """Record a successful operation."""
        if self.state == CircuitBreakerState.HALF_OPEN:
            self.success_count += 1
            if self.success_count >= self.success_threshold:
                self._close_circuit()
        elif self.state == CircuitBreakerState.CLOSED:
            self.failure_count = 0
            self.success_count = 0
    
    def record_failure(self) -> None:
        """Record a failed operation."""
        self.failure_count += 1
        self.last_failure_time = datetime.now()
        
        if self.state == CircuitBreakerState.CLOSED:
            if self.failure_count >= self.failure_threshold:
                self._open_circuit()
        elif self.state == CircuitBreakerState.HALF_OPEN:
            self._open_circuit()
    
    def allow_request(self) -> bool:
        """Check if requests should be allowed through the circuit."""
        if self.state == CircuitBreakerState.CLOSED:
            return True
        elif self.state == CircuitBreakerState.OPEN:
            # Check if recovery timeout has elapsed
            if self.last_failure_time and (datetime.now() - self.last_failure_time).total_seconds() >= self.recovery_timeout:
                self._transition_to_half_open()
                return True
            return False
        elif self.state == CircuitBreakerState.HALF_OPEN:
            return True
        return False
    
    def _open_circuit(self) -> None:
        """Open the circuit to block requests."""
        self.state = CircuitBreakerState.OPEN
        self.last_state_change = datetime.now()
        logger.warning(f"Circuit breaker OPENED after {self.failure_count} failures")
        
        # Emit circuit breaker event
        # This would be used by the AI Runtime Engine to notify the system
        # but we don't have direct access to event_bus here, so it's handled by the caller
    
    def _close_circuit(self) -> None:
        """Close the circuit to allow requests."""
        self.state = CircuitBreakerState.CLOSED
        self.failure_count = 0
        self.success_count = 0
        self.last_state_change = datetime.now()
        logger.info(f"Circuit breaker CLOSED after {self.success_count} successes")
    
    def _transition_to_half_open(self) -> None:
        """Transition to half-open state to test recovery."""
        self.state = CircuitBreakerState.HALF_OPEN
        self.success_count = 0
        self.last_state_change = datetime.now()
        logger.info("Circuit breaker transitioned to HALF_OPEN for testing")
    
    def get_state(self) -> CircuitBreakerState:
        """Get current circuit breaker state."""
        return self.state
    
    def get_stats(self) -> Dict[str, Any]:
        """Get circuit breaker statistics."""
        return {
            "state": self.state.value,
            "failure_count": self.failure_count,
            "success_count": self.success_count,
            "last_failure_time": self.last_failure_time.isoformat() if self.last_failure_time else None,
            "last_state_change": self.last_state_change.isoformat(),
            "time_in_current_state": (datetime.now() - self.last_state_change).total_seconds()
        }


class AIState(Enum):
    """AI engine states."""
    INITIALIZING = "INITIALIZING"
    LOADING_MEMORY = "LOADING_MEMORY"
    RESTORING_SESSION = "RESTORING_SESSION"
    RUNNING = "RUNNING"
    PROCESSING = "PROCESSING"
    UPDATING_MEMORY = "UPDATING_MEMORY"
    ERROR = "ERROR"
    STOPPED = "STOPPED"


@dataclass
class AIDecision:
    """Represents an AI decision."""
    decision_type: str
    confidence: float
    reasoning: str
    metadata: Dict[str, Any] = field(default_factory=dict)
    timestamp: float = field(default_factory=time.time)


@dataclass
class AIContext:
    """AI execution context."""
    session_id: str
    memory_state: Dict[str, Any]
    current_input: Any
    context_window: List[Any]
    timestamp: float = field(default_factory=time.time)


class AIMemoryInterface(ABC):
    """Abstract interface for AI memory operations."""
    
    @abstractmethod
    def load_memory(self, session_id: str) -> Dict[str, Any]:
        """Load memory for a session."""
        pass
    
    @abstractmethod
    def update_memory(self, session_id: str, updates: Dict[str, Any]) -> bool:
        """Update memory for a session."""
        pass
    
    @abstractmethod
    def save_state(self, session_id: str, state: Dict[str, Any]) -> bool:
        """Save AI state to memory."""
        pass


class StateComputation(ABC):
    """Abstract interface for stateless AI computation."""
    
    @abstractmethod
    def compute(self, context: AIContext) -> AIDecision:
        """Perform stateless computation on context."""
        pass


class SimpleAIMemory(AIMemoryInterface):
    """Simple in-memory implementation of AI memory interface."""
    
    def __init__(self):
        self.memory_store: Dict[str, Dict[str, Any]] = {}
        self._lock = threading.Lock()
    
    def load_memory(self, session_id: str) -> Dict[str, Any]:
        """Load memory for a session."""
        with self._lock:
            return self.memory_store.get(session_id, {})
    
    def update_memory(self, session_id: str, updates: Dict[str, Any]) -> bool:
        """Update memory for a session."""
        with self._lock:
            if session_id not in self.memory_store:
                self.memory_store[session_id] = {}
            self.memory_store[session_id].update(updates)
            return True
    
    def save_state(self, session_id: str, state: Dict[str, Any]) -> bool:
        """Save AI state to memory."""
        return self.update_memory(session_id, {"ai_state": state})


class SimpleComputation(StateComputation):
    """Simple stateless computation implementation."""
    
    def compute(self, context: AIContext) -> AIDecision:
        """Perform simple computation on context."""
        # Basic computation framework - can be extended with actual AI models
        return AIDecision(
            decision_type="basic_computation",
            confidence=0.5,
            reasoning="Basic computation framework - ready for AI model integration",
            metadata={"context_size": len(context.context_window)}
        )


class AIRuntimeEngine(Service):
    """AI Runtime Engine service as per Runtime Specification."""
    
    # Service dependencies
    DEPENDENCIES = ["memory_service", "session_restoration"]
    
    # Performance tracking
    PERFORMANCE_METRICS_INTERVAL = 60  # seconds between metrics events
    
    # Circuit breaker configuration
    CIRCUIT_BREAKER_FAILURE_THRESHOLD = 5
    CIRCUIT_BREAKER_RECOVERY_TIMEOUT = 60.0  # seconds
    CIRCUIT_BREAKER_SUCCESS_THRESHOLD = 2
    
    def __init__(self):
        super().__init__("ai_runtime_engine")
        self.ai_state = AIState.STOPPED
        self.memory_interface: Optional[AIMemoryInterface] = None
        self.computation_engine: Optional[StateComputation] = None
        self.current_session: Optional[str] = None
        self._processing_thread: Optional[threading.Thread] = None
        self._stop_event = threading.Event()
        
        # Performance metrics
        self.decision_count = 0
        self.total_computation_time = 0.0
        self.last_metrics_time = 0.0
        self.decision_latency_samples = []
        
        # Circuit breaker for error resilience
        self.circuit_breaker = CircuitBreaker(
            failure_threshold=self.CIRCUIT_BREAKER_FAILURE_THRESHOLD,
            recovery_timeout=self.CIRCUIT_BREAKER_RECOVERY_TIMEOUT,
            success_threshold=self.CIRCUIT_BREAKER_SUCCESS_THRESHOLD
        )
        
    def init(self, event_bus: EventBus, config: Dict[str, Any]) -> bool:
        """Initialize the AI runtime engine."""
        try:
            self.event_bus = event_bus
            self.config = config
            self.state = ServiceState.INITIALIZING
            
            # Initialize memory interface
            self.memory_interface = SimpleAIMemory()
            
            # Initialize computation engine
            self.computation_engine = SimpleComputation()
            
            logger.info("AI Runtime Engine initialized")
            return True
        except Exception as e:
            logger.error(f"AI Runtime Engine initialization failed: {e}")
            self.state = ServiceState.ERROR
            return False
    
    def start(self) -> bool:
        """Start the AI runtime engine."""
        try:
            self.state = ServiceState.STARTING
            self.ai_state = AIState.INITIALIZING
            
            # Emit initialization event
            self.emit_event(str(EventType.AI_INIT), {"state": self.ai_state.value})
            
            # Start processing thread
            self._stop_event.clear()
            self._processing_thread = threading.Thread(target=self._processing_loop, daemon=True)
            self._processing_thread.start()
            
            self.state = ServiceState.RUNNING
            self.emit_event(str(EventType.AI_START), {"state": self.ai_state.value})
            logger.info("AI Runtime Engine started")
            return True
        except Exception as e:
            logger.error(f"AI Runtime Engine start failed: {e}")
            self.state = ServiceState.ERROR
            self.ai_state = AIState.ERROR
            self.emit_event(str(EventType.AI_ERROR), {"error": str(e)})
            return False
    
    def stop(self) -> bool:
        """Stop the AI runtime engine."""
        try:
            self.state = ServiceState.STOPPING
            self.ai_state = AIState.STOPPED
            
            # Signal stop to processing thread
            self._stop_event.set()
            
            # Wait for processing thread to stop
            if self._processing_thread and self._processing_thread.is_alive():
                self._processing_thread.join(timeout=5)
            
            self.state = ServiceState.STOPPED
            self.emit_event(str(EventType.AI_STOP), {"state": self.ai_state.value})
            logger.info("AI Runtime Engine stopped")
            return True
        except Exception as e:
            logger.error(f"AI Runtime Engine stop failed: {e}")
            self.state = ServiceState.ERROR
            return False
    
    def health(self) -> ServiceHealth:
        """Get AI runtime engine health."""
        return ServiceHealth(
            service=self.name,
            state=self.state,
            healthy=self.state == ServiceState.RUNNING and self.circuit_breaker.get_state() == CircuitBreakerState.CLOSED,
            message=f"AI State: {self.ai_state.value} - Circuit: {self.circuit_breaker.get_state().value}",
            details={
                "ai_state": self.ai_state.value,
                "current_session": self.current_session,
                "thread_active": self._processing_thread and self._processing_thread.is_alive(),
                "circuit_breaker": self.circuit_breaker.get_stats(),
                "decision_count": self.decision_count,
                "avg_computation_time": self.total_computation_time / self.decision_count if self.decision_count > 0 else 0.0
            },
            timestamp=time.time()
        )
    
    def _processing_loop(self) -> None:
        """Main AI processing loop as per AI Runtime Contract."""
        try:
            # AI Lifecycle: INIT → LOAD MEMORY → RESTORE SESSION → RUN LOOP → UPDATE MEMORY → REPORT STATE
            
            # Step 1: INIT (already done in start())
            
            # Step 2: LOAD MEMORY
            self.ai_state = AIState.LOADING_MEMORY
            self.emit_event(str(EventType.AI_STATE_UPDATE), {"state": self.ai_state.value})
            
            # Load memory for default session
            session_id = "default_session"
            memory_data = self.memory_interface.load_memory(session_id)
            
            logger.info(f"AI Memory loaded for session: {session_id}")
            self.current_session = session_id
            
            # Step 3: RESTORE SESSION
            self.ai_state = AIState.RESTORING_SESSION
            self.emit_event(str(EventType.AI_STATE_UPDATE), {"state": self.ai_state.value})
            
            # Restore session state from memory
            session_state = memory_data.get("ai_state", {})
            logger.info(f"AI Session restored: {session_state}")
            
            # Step 4: RUN LOOP
            self.ai_state = AIState.RUNNING
            self.emit_event(str(EventType.AI_STATE_UPDATE), {"state": self.ai_state.value})
            
            processing_count = 0
            while not self._stop_event.is_set():
                try:
                    # Check circuit breaker before processing
                    if not self.circuit_breaker.allow_request():
                        logger.warning("Circuit breaker is OPEN, skipping AI processing")
                        self.ai_state = AIState.ERROR
                        self.emit_event(str(EventType.AI_ERROR), {
                            "error": "Circuit breaker OPEN - too many failures",
                            "circuit_breaker_state": self.circuit_breaker.get_state().value,
                            "circuit_breaker_stats": self.circuit_breaker.get_stats()
                        })
                        self._stop_event.wait(5.0)  # Wait before retry
                        continue
                    
                    # Step 4a: PROCESSING
                    self.ai_state = AIState.PROCESSING
                    computation_start_time = time.time()
                    
                    # Create AI context
                    context = AIContext(
                        session_id=session_id,
                        memory_state=memory_data,
                        current_input=None,  # Would come from actual input
                        context_window=[]
                    )
                    
                    # Step 4b: Stateless computation with circuit breaker protection
                    try:
                        decision = self.computation_engine.compute(context)
                        computation_time = time.time() - computation_start_time
                        
                        # Record success
                        self.circuit_breaker.record_success()
                        
                        # Track performance metrics
                        self.decision_count += 1
                        self.total_computation_time += computation_time
                        self.decision_latency_samples.append(computation_time)
                        if len(self.decision_latency_samples) > 100:
                            self.decision_latency_samples.pop(0)
                        
                        # Step 4c: Emit decision event (AI must emit events for all decisions)
                        self.emit_event(str(EventType.AI_DECISION), {
                            "decision_type": decision.decision_type,
                            "confidence": decision.confidence,
                            "reasoning": decision.reasoning,
                            "metadata": decision.metadata,
                            "performance": {
                                "computation_time": computation_time,
                                "decision_number": self.decision_count
                            },
                            "circuit_breaker_state": self.circuit_breaker.get_state().value
                        })
                        
                        logger.debug(f"AI Decision #{processing_count}: {decision.decision_type} (confidence: {decision.confidence}, time: {computation_time:.3f}s)")
                        
                    except Exception as e:
                        # Record failure and let circuit breaker handle it
                        self.circuit_breaker.record_failure()
                        logger.error(f"AI computation failed: {e}")
                        self.emit_event(str(EventType.AI_ERROR), {
                            "error": str(e),
                            "circuit_breaker_state": self.circuit_breaker.get_state().value,
                            "circuit_breaker_stats": self.circuit_breaker.get_stats()
                        })
                        raise
                    
                    # Emit performance metrics periodically
                    current_time = time.time()
                    if current_time - self.last_metrics_time >= self.PERFORMANCE_METRICS_INTERVAL:
                        self._emit_performance_metrics()
                        self.last_metrics_time = current_time
                    
                    # Step 5: UPDATE MEMORY (AI must be stateful via memory layer)
                    self.ai_state = AIState.UPDATING_MEMORY
                    self.emit_event(str(EventType.AI_STATE_UPDATE), {"state": self.ai_state.value})
                    
                    # Update memory with decision
                    self.memory_interface.save_state(session_id, {
                        "last_decision": decision.decision_type,
                        "last_decision_time": decision.timestamp,
                        "processing_count": processing_count
                    })
                    
                    # Step 6: REPORT STATE
                    self.ai_state = AIState.RUNNING
                    self.emit_event(str(EventType.AI_STATE_UPDATE), {
                        "state": self.ai_state.value,
                        "processing_count": processing_count,
                        "session_id": session_id
                    })
                    
                    processing_count += 1
                    
                    # Wait for next processing cycle
                    self._stop_event.wait(1.0)
                    
                except Exception as e:
                    logger.error(f"AI processing error: {e}")
                    self.ai_state = AIState.ERROR
                    self.emit_event(str(EventType.AI_ERROR), {"error": str(e)})
                    # Wait before retry
                    self._stop_event.wait(5.0)
            
        except Exception as e:
            logger.error(f"AI processing loop failed: {e}")
            self.ai_state = AIState.ERROR
            self.emit_event(str(EventType.AI_ERROR), {"error": str(e)})
    
    def _emit_performance_metrics(self) -> None:
        """Emit AI performance metrics event."""
        if self.decision_count == 0:
            return
        
        avg_computation_time = self.total_computation_time / self.decision_count if self.decision_count > 0 else 0.0
        
        # Calculate latency statistics
        if self.decision_latency_samples:
            sorted_latencies = sorted(self.decision_latency_samples)
            median_latency = sorted_latencies[len(sorted_latencies) // 2]
            p95_latency = sorted_latencies[int(len(sorted_latencies) * 0.95)] if len(sorted_latencies) > 1 else sorted_latencies[0]
            p99_latency = sorted_latencies[int(len(sorted_latencies) * 0.99)] if len(sorted_latencies) > 1 else sorted_latencies[0]
        else:
            median_latency = p95_latency = p99_latency = 0.0
        
        # Calculate decisions per second
        time_elapsed = time.time() - self.last_metrics_time if self.last_metrics_time > 0 else self.PERFORMANCE_METRICS_INTERVAL
        decisions_per_second = self.decision_count / max(time_elapsed, 1.0)
        
        performance_metrics = {
            "service": self.name,
            "ai_state": self.ai_state.value,
            "decision_count": self.decision_count,
            "avg_computation_time": avg_computation_time,
            "median_latency": median_latency,
            "p95_latency": p95_latency,
            "p99_latency": p99_latency,
            "decisions_per_second": decisions_per_second,
            "session_id": self.current_session,
            "measurement_period": time_elapsed
        }
        
        self.emit_event("AI_PERFORMANCE_METRICS", performance_metrics)
        logger.info(f"AI Performance Metrics: {performance_metrics['decisions_per_second']:.2f} decisions/sec, avg latency: {avg_computation_time:.3f}s")
        
        # Reset counters for next interval
        self.decision_count = 0
        self.total_computation_time = 0.0
    
    def _emit_circuit_breaker_events(self) -> None:
        """Emit circuit breaker state change events."""
        current_state = self.circuit_breaker.get_state()
        
        # Emit event when circuit breaker state changes
        if current_state == CircuitBreakerState.OPEN:
            self.emit_event("CIRCUIT_BREAKER_OPEN", {
                "service": self.name,
                "circuit_breaker_stats": self.circuit_breaker.get_stats(),
                "reason": "Failure threshold exceeded"
            })
        elif current_state == CircuitBreakerState.HALF_OPEN:
            self.emit_event("CIRCUIT_BREAKER_HALF_OPEN", {
                "service": self.name,
                "circuit_breaker_stats": self.circuit_breaker.get_stats(),
                "reason": "Testing recovery"
            })
        elif current_state == CircuitBreakerState.CLOSED:
            self.emit_event("CIRCUIT_BREAKER_CLOSED", {
                "service": self.name,
                "circuit_breaker_stats": self.circuit_breaker.get_stats(),
                "reason": "Recovery successful"
            })


class AIRuntimeEngineAdvanced(AIRuntimeEngine):
    """Advanced AI Runtime Engine with enhanced capabilities."""
    
    def __init__(self):
        super().__init__()
        self.name = "ai_runtime_engine_advanced"
        
    def _processing_loop(self) -> None:
        """Enhanced processing loop with advanced AI capabilities."""
        try:
            # Initialize advanced components
            self.ai_state = AIState.LOADING_MEMORY
            self.emit_event(str(EventType.AI_STATE_UPDATE), {"state": self.ai_state.value})
            
            session_id = "default_session"
            memory_data = self.memory_interface.load_memory(session_id)
            
            self.ai_state = AIState.RESTORING_SESSION
            self.emit_event(str(EventType.AI_STATE_UPDATE), {"state": self.ai_state.value})
            
            session_state = memory_data.get("ai_state", {})
            logger.info(f"Advanced AI Session restored: {session_state}")
            
            self.ai_state = AIState.RUNNING
            self.emit_event(str(EventType.AI_STATE_UPDATE), {"state": self.ai_state.value})
            
            processing_count = 0
            while not self._stop_event.is_set():
                try:
                    self.ai_state = AIState.PROCESSING
                    
                    # Enhanced context with more sophisticated data
                    context = AIContext(
                        session_id=session_id,
                        memory_state=memory_data,
                        current_input=f"input_{processing_count}",
                        context_window=list(range(min(10, processing_count)))
                    )
                    
                    # Enhanced computation
                    decision = self.computation_engine.compute(context)
                    
                    # Enhanced decision event with more metadata
                    self.emit_event(str(EventType.AI_DECISION), {
                        "decision_type": decision.decision_type,
                        "confidence": decision.confidence,
                        "reasoning": decision.reasoning,
                        "metadata": {
                            **decision.metadata,
                            "session_id": session_id,
                            "processing_count": processing_count,
                            "advanced_mode": True
                        }
                    })
                    
                    logger.info(f"Advanced AI Decision #{processing_count}: {decision.decision_type}")
                    
                    self.ai_state = AIState.UPDATING_MEMORY
                    self.emit_event(str(EventType.AI_STATE_UPDATE), {"state": self.ai_state.value})
                    
                    # Enhanced memory updates
                    self.memory_interface.save_state(session_id, {
                        "last_decision": decision.decision_type,
                        "last_decision_time": decision.timestamp,
                        "processing_count": processing_count,
                        "advanced_mode": True,
                        "decision_history": memory_data.get("decision_history", []) + [decision.decision_type]
                    })
                    
                    self.ai_state = AIState.RUNNING
                    self.emit_event(str(EventType.AI_STATE_UPDATE), {
                        "state": self.ai_state.value,
                        "processing_count": processing_count,
                        "session_id": session_id,
                        "advanced_mode": True
                    })
                    
                    processing_count += 1
                    self._stop_event.wait(2.0)  # Slower cycle for advanced processing
                    
                except Exception as e:
                    logger.error(f"Advanced AI processing error: {e}")
                    self.ai_state = AIState.ERROR
                    self.emit_event(str(EventType.AI_ERROR), {"error": str(e)})
                    self._stop_event.wait(5.0)
            
        except Exception as e:
            logger.error(f"Advanced AI processing loop failed: {e}")
            self.ai_state = AIState.ERROR
            self.emit_event(str(EventType.AI_ERROR), {"error": str(e)})


__all__ = [
    "AIRuntimeEngine",
    "AIRuntimeEngineAdvanced",
    "AIState",
    "AIDecision",
    "AIContext",
    "AIMemoryInterface",
    "SimpleAIMemory",
    "StateComputation",
    "SimpleComputation",
]