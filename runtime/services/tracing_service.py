"""
DIX VISION Distributed Tracing Service

Provides end-to-end request tracing, service dependency mapping, 
performance bottleneck identification, and root cause analysis.
"""

from __future__ import annotations

import logging
import threading
import time
import uuid
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Callable, Dict, List, Optional, Tuple
from collections import defaultdict, deque
from contextlib import contextmanager

from runtime.event_bus import EventBus, Event, EventType, get_event_bus
from runtime.service_manager import Service, ServiceState, ServiceHealth

logger = logging.getLogger(__name__)


class SpanStatus(Enum):
    """Span status."""
    OK = "ok"
    ERROR = "error"
    CANCELLED = "cancelled"


@dataclass
class Span:
    """Trace span representing a unit of work."""
    trace_id: str
    span_id: str
    parent_span_id: Optional[str]
    operation_name: str
    start_time: float
    end_time: Optional[float] = None
    duration: Optional[float] = None
    status: SpanStatus = SpanStatus.OK
    tags: Dict[str, str] = field(default_factory=dict)
    logs: List[Dict[str, Any]] = field(default_factory=list)
    service_name: str = ""
    
    def finish(self, status: SpanStatus = SpanStatus.OK) -> None:
        """Finish the span."""
        self.end_time = time.time()
        self.duration = self.end_time - self.start_time
        self.status = status


@dataclass
class Trace:
    """Complete trace containing multiple spans."""
    trace_id: str
    root_span_id: str
    spans: Dict[str, Span] = field(default_factory=dict)
    start_time: float = field(default_factory=time.time)
    end_time: Optional[float] = None
    duration: Optional[float] = None
    service_map: Dict[str, List[str]] = field(default_factory=dict)  # service -> dependent services
    
    def finish(self) -> None:
        """Finish the trace."""
        self.end_time = time.time()
        self.duration = self.end_time - self.start_time


@dataclass
class ServiceDependency:
    """Service dependency relationship."""
    service_a: str
    service_b: str
    call_count: int = 0
    avg_duration: float = 0.0
    error_rate: float = 0.0


class TracingService(Service):
    """Distributed tracing service as per Runtime Specification."""
    
    # Service dependencies
    DEPENDENCIES = []
    
    def __init__(self):
        super().__init__("tracing_service")
        self._active_traces: Dict[str, Trace] = {}
        self._completed_traces: deque = deque(maxlen=10000)
        self._active_spans: Dict[str, Span] = {}
        self._service_dependencies: Dict[Tuple[str, str], ServiceDependency] = {}
        self._service_graph: Dict[str, List[str]] = defaultdict(list)
        self._lock = threading.Lock()
        self._sampling_rate = 1.0  # Sample all traces by default
        self._max_trace_duration = 60.0  # seconds
        
    def init(self, event_bus: EventBus, config: Dict[str, Any]) -> bool:
        """Initialize the tracing service."""
        try:
            self.event_bus = event_bus
            self.state = ServiceState.INITIALIZING
            
            # Load configuration
            tracing_config = config.get("tracing", {})
            self._sampling_rate = tracing_config.get("sampling_rate", 1.0)
            self._max_trace_duration = tracing_config.get("max_trace_duration", 60.0)
            
            logger.info("Tracing Service initialized")
            return True
        except Exception as e:
            logger.error(f"Tracing Service initialization failed: {e}")
            self.state = ServiceState.ERROR
            return False
    
    def start(self) -> bool:
        """Start the tracing service."""
        try:
            self.state = ServiceState.STARTING
            
            # Start background trace cleanup
            self._start_trace_cleanup()
            
            # Start background dependency analyzer
            self._start_dependency_analyzer()
            
            self.state = ServiceState.RUNNING
            self.emit_event(str(EventType.SERVICE_START), {"service": self.name})
            logger.info("Tracing Service started")
            return True
        except Exception as e:
            logger.error(f"Tracing Service start failed: {e}")
            self.state = ServiceState.ERROR
            self.emit_event(str(EventType.SERVICE_CRASH), {"service": self.name, "error": str(e)})
            return False
    
    def stop(self) -> bool:
        """Stop the tracing service."""
        try:
            self.state = ServiceState.STOPPING
            
            # Finish all active traces
            with self._lock:
                for trace in self._active_traces.values():
                    trace.finish()
                    self._completed_traces.append(trace)
                self._active_traces.clear()
            
            self.state = ServiceState.STOPPED
            self.emit_event(str(EventType.SERVICE_STOP), {"service": self.name})
            logger.info("Tracing Service stopped")
            return True
        except Exception as e:
            logger.error(f"Tracing Service stop failed: {e}")
            self.state = ServiceState.ERROR
            return False
    
    def health(self) -> ServiceHealth:
        """Get tracing service health."""
        return ServiceHealth(
            service=self.name,
            state=self.state,
            healthy=self.state == ServiceState.RUNNING,
            message=f"Tracing Service - {len(self._active_traces)} active traces",
            details={
                "active_traces": len(self._active_traces),
                "completed_traces": len(self._completed_traces),
                "active_spans": len(self._active_spans),
                "service_dependencies": len(self._service_dependencies),
                "sampling_rate": self._sampling_rate
            },
            timestamp=time.time()
        )
    
    def start_trace(self, operation_name: str, service_name: str = "") -> Span:
        """Start a new trace."""
        if not self._should_sample():
            # Return a no-op span if not sampled
            return Span(
                trace_id="",
                span_id="",
                parent_span_id=None,
                operation_name=operation_name,
                start_time=time.time()
            )
        
        trace_id = str(uuid.uuid4())
        span_id = str(uuid.uuid4())
        
        span = Span(
            trace_id=trace_id,
            span_id=span_id,
            parent_span_id=None,
            operation_name=operation_name,
            start_time=time.time(),
            service_name=service_name
        )
        
        trace = Trace(
            trace_id=trace_id,
            root_span_id=span_id
        )
        trace.spans[span_id] = span
        
        with self._lock:
            self._active_traces[trace_id] = trace
            self._active_spans[span_id] = span
        
        return span
    
    def start_span(self, operation_name: str, parent_span: Span, service_name: str = "") -> Span:
        """Start a child span."""
        if parent_span.trace_id == "":
            # Parent was not sampled, don't sample child
            return Span(
                trace_id="",
                span_id="",
                parent_span_id=None,
                operation_name=operation_name,
                start_time=time.time()
            )
        
        span_id = str(uuid.uuid4())
        
        span = Span(
            trace_id=parent_span.trace_id,
            span_id=span_id,
            parent_span_id=parent_span.span_id,
            operation_name=operation_name,
            start_time=time.time(),
            service_name=service_name
        )
        
        with self._lock:
            if parent_span.trace_id in self._active_traces:
                self._active_traces[parent_span.trace_id].spans[span_id] = span
                self._active_spans[span_id] = span
                
                # Update service graph
                if parent_span.service_name and service_name:
                    self._update_service_dependency(parent_span.service_name, service_name)
        
        return span
    
    def finish_span(self, span: Span, status: SpanStatus = SpanStatus.OK) -> None:
        """Finish a span."""
        if span.trace_id == "":
            return  # Span was not sampled
        
        span.finish(status)
        
        with self._lock:
            if span.span_id in self._active_spans:
                del self._active_spans[span.span_id]
            
            # Check if this was the root span
            if span.trace_id in self._active_traces:
                trace = self._active_traces[span.trace_id]
                if span.span_id == trace.root_span_id:
                    trace.finish()
                    self._completed_traces.append(trace)
                    del self._active_traces[span.trace_id]
    
    @contextmanager
    def trace_context(self, operation_name: str, service_name: str = "") -> Span:
        """Context manager for automatic span management."""
        span = self.start_trace(operation_name, service_name)
        try:
            yield span
            self.finish_span(span, SpanStatus.OK)
        except Exception as e:
            span.tags["error"] = str(e)
            self.finish_span(span, SpanStatus.ERROR)
            raise
    
    @contextmanager
    def span_context(self, operation_name: str, parent_span: Span, service_name: str = "") -> Span:
        """Context manager for automatic child span management."""
        span = self.start_span(operation_name, parent_span, service_name)
        try:
            yield span
            self.finish_span(span, SpanStatus.OK)
        except Exception as e:
            span.tags["error"] = str(e)
            self.finish_span(span, SpanStatus.ERROR)
            raise
    
    def get_trace(self, trace_id: str) -> Optional[Trace]:
        """Get a trace by ID."""
        with self._lock:
            if trace_id in self._active_traces:
                return self._active_traces[trace_id]
            
            for trace in reversed(self._completed_traces):
                if trace.trace_id == trace_id:
                    return trace
        
        return None
    
    def get_service_graph(self) -> Dict[str, List[str]]:
        """Get the service dependency graph."""
        with self._lock:
            return dict(self._service_graph)
    
    def identify_bottlenecks(self, min_duration: float = 1.0) -> List[Dict[str, Any]]:
        """Identify performance bottlenecks in completed traces."""
        bottlenecks = []
        
        with self._lock:
            for trace in list(self._completed_traces):
                if trace.duration and trace.duration > min_duration:
                    # Find slowest spans
                    slow_spans = sorted(
                        trace.spans.values(),
                        key=lambda s: s.duration or 0,
                        reverse=True
                    )[:5]
                    
                    bottlenecks.append({
                        "trace_id": trace.trace_id,
                        "total_duration": trace.duration,
                        "slow_spans": [
                            {
                                "operation": span.operation_name,
                                "service": span.service_name,
                                "duration": span.duration,
                                "percentage": (span.duration / trace.duration * 100) if trace.duration else 0
                            }
                            for span in slow_spans
                        ]
                    })
        
        return bottlenecks
    
    def get_trace_statistics(self) -> Dict[str, Any]:
        """Get trace statistics."""
        with self._lock:
            total_traces = len(self._completed_traces)
            if total_traces == 0:
                return {}
            
            durations = [trace.duration for trace in self._completed_traces if trace.duration]
            if not durations:
                return {}
            
            avg_duration = sum(durations) / len(durations)
            p50_duration = sorted(durations)[len(durations) // 2]
            p95_duration = sorted(durations)[int(len(durations) * 0.95)]
            p99_duration = sorted(durations)[int(len(durations) * 0.99)]
            
            return {
                "total_traces": total_traces,
                "avg_duration": avg_duration,
                "p50_duration": p50_duration,
                "p95_duration": p95_duration,
                "p99_duration": p99_duration,
                "active_traces": len(self._active_traces),
                "active_spans": len(self._active_spans)
            }
    
    def _should_sample(self) -> bool:
        """Determine if a trace should be sampled."""
        import random
        return random.random() < self._sampling_rate
    
    def _update_service_dependency(self, service_a: str, service_b: str) -> None:
        """Update service dependency tracking."""
        key = (service_a, service_b)
        
        if key not in self._service_dependencies:
            self._service_dependencies[key] = ServiceDependency(service_a, service_b)
        
        self._service_dependencies[key].call_count += 1
        
        # Update service graph
        if service_b not in self._service_graph[service_a]:
            self._service_graph[service_a].append(service_b)
    
    def _start_trace_cleanup(self) -> None:
        """Start background trace cleanup."""
        def cleanup_traces():
            while self.state == ServiceState.RUNNING:
                try:
                    current_time = time.time()
                    
                    with self._lock:
                        # Clean up old traces
                        self._completed_traces = deque(
                            [t for t in self._completed_traces 
                             if not t.end_time or current_time - t.end_time < 3600],
                            maxlen=10000
                        )
                    
                    time.sleep(300)  # Clean up every 5 minutes
                except Exception as e:
                    logger.error(f"Trace cleanup error: {e}")
                    time.sleep(60)
        
        thread = threading.Thread(target=cleanup_traces, daemon=True)
        thread.start()
        logger.info("Trace cleanup started")
    
    def _start_dependency_analyzer(self) -> None:
        """Start background dependency analyzer."""
        def analyze_dependencies():
            while self.state == ServiceState.RUNNING:
                try:
                    with self._lock:
                        # Update dependency statistics
                        for key, dep in self._service_dependencies.items():
                            # Calculate average duration and error rate from traces
                            # This is a simplified version
                            pass
                    
                    time.sleep(60)  # Analyze every minute
                except Exception as e:
                    logger.error(f"Dependency analysis error: {e}")
                    time.sleep(30)
        
        thread = threading.Thread(target=analyze_dependencies, daemon=True)
        thread.start()
        logger.info("Dependency analyzer started")


# Global instance
_tracing_service: Optional[TracingService] = None


def get_tracing_service() -> TracingService:
    """Get global tracing service instance."""
    global _tracing_service
    if _tracing_service is None:
        _tracing_service = TracingService()
    return _tracing_service