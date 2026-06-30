"""
Memory Service implementation for DIX VISION Runtime.

Conforms to the Service interface from runtime/service_manager.py.
Provides memory monitoring and management capabilities.
"""

from typing import Any, Dict, Optional
from runtime.service_manager import Service, ServiceState, ServiceHealth
from runtime.event_bus import EventBus, EventType
from runtime.memory_manager import get_memory_manager
import logging
import time
from enum import Enum

logger = logging.getLogger(__name__)


class MemoryPressure(Enum):
    """Memory pressure levels."""
    NORMAL = "NORMAL"
    WARNING = "WARNING"
    CRITICAL = "CRITICAL"
    SEVERE = "SEVERE"


class MemoryService(Service):
    """Memory monitoring service as per Runtime Specification."""
    
    # Service dependencies
    DEPENDENCIES = []  # No dependencies, uses memory_manager directly
    
    # Memory pressure thresholds
    WARNING_THRESHOLD = 70.0  # percent
    CRITICAL_THRESHOLD = 85.0  # percent
    SEVERE_THRESHOLD = 95.0   # percent
    
    def __init__(self):
        super().__init__("memory_service")
        self.memory_manager = None
        self.memory_pressure = MemoryPressure.NORMAL
        self.backpressure_active = False
        self.last_memory_check = 0.0
        self.memory_trend = []  # Track memory usage trend
        
    def init(self, event_bus: EventBus, config: Dict[str, Any]) -> bool:
        """Initialize memory service."""
        try:
            self.event_bus = event_bus
            self.config = config
            self.state = ServiceState.INITIALIZING
            
            self.memory_manager = get_memory_manager()
            
            logger.info("Memory service initialized")
            return True
        except Exception as e:
            logger.error(f"Memory service initialization failed: {e}")
            self.state = ServiceState.ERROR
            return False
        
    def start(self) -> bool:
        """Start the memory service."""
        try:
            self.state = ServiceState.STARTING
            
            if self.memory_manager:
                self.memory_manager.start_monitoring()
            
            self.state = ServiceState.RUNNING
            self.emit_event(str(EventType.SERVICE_START), {"service": self.name})
            logger.info("Memory service started")
            return True
        except Exception as e:
            logger.error(f"Memory service start failed: {e}")
            self.state = ServiceState.ERROR
            self.emit_event(str(EventType.SERVICE_CRASH), {"service": self.name, "error": str(e)})
            return False
    
    def stop(self) -> bool:
        """Stop the memory service."""
        try:
            self.state = ServiceState.STOPPING
            
            if self.memory_manager:
                self.memory_manager.stop_monitoring()
            
            self.state = ServiceState.STOPPED
            self.emit_event(str(EventType.SERVICE_STOP), {"service": self.name})
            logger.info("Memory service stopped")
            return True
        except Exception as e:
            logger.error(f"Memory service stop failed: {e}")
            self.state = ServiceState.ERROR
            self.emit_event(str(EventType.SERVICE_CRASH), {"service": self.name, "error": str(e)})
            return False
    
    def health(self) -> ServiceHealth:
        """Check memory service health."""
        try:
            if not self.memory_manager:
                return ServiceHealth(
                    service=self.name,
                    state=self.state,
                    healthy=False,
                    message="Memory manager not initialized",
                    details={},
                    timestamp=time.time()
                )
            
            status = self.memory_manager.get_memory_status()
            current_time = time.time()
            
            # Track memory trend
            self._track_memory_trend(status)
            
            # Update memory pressure state
            self._update_memory_pressure(status)
            
            # Emit memory pressure events based on thresholds
            self._emit_memory_pressure_events(status)
            
            # Emit backpressure signal if needed
            self._handle_backpressure(status)
            
            self.last_memory_check = current_time
            
            return ServiceHealth(
                service=self.name,
                state=self.state,
                healthy=status.safe and not self.backpressure_active,
                message=f"Memory: {status.rss_mb:.2f}MB ({status.system_percent:.1f}%) - Pressure: {self.memory_pressure.value}",
                details={
                    "rss_mb": status.rss_mb,
                    "system_percent": status.system_percent,
                    "safe": status.safe,
                    "memory_pressure": self.memory_pressure.value,
                    "backpressure_active": self.backpressure_active,
                    "memory_trend": self.memory_trend[-5:] if self.memory_trend else []
                },
                timestamp=time.time()
            )
        except Exception as e:
            return ServiceHealth(
                service=self.name,
                state=self.state,
                healthy=False,
                message=f"Health check failed: {e}",
                details={},
                timestamp=time.time()
            )
    
    def _track_memory_trend(self, status) -> None:
        """Track memory usage trend over time."""
        self.memory_trend.append({
            "timestamp": time.time(),
            "rss_mb": status.rss_mb,
            "system_percent": status.system_percent
        })
        # Keep only last 100 data points
        if len(self.memory_trend) > 100:
            self.memory_trend.pop(0)
    
    def _update_memory_pressure(self, status) -> None:
        """Update memory pressure state based on current usage."""
        if status.system_percent >= self.SEVERE_THRESHOLD:
            self.memory_pressure = MemoryPressure.SEVERE
        elif status.system_percent >= self.CRITICAL_THRESHOLD:
            self.memory_pressure = MemoryPressure.CRITICAL
        elif status.system_percent >= self.WARNING_THRESHOLD:
            self.memory_pressure = MemoryPressure.WARNING
        else:
            self.memory_pressure = MemoryPressure.NORMAL
    
    def _emit_memory_pressure_events(self, status) -> None:
        """Emit memory pressure events based on current state."""
        # Only emit events when state changes to avoid spam
        if self.memory_pressure == MemoryPressure.SEVERE:
            self.emit_event(str(EventType.MEMORY_CRITICAL), {
                "service": self.name,
                "usage_percent": status.system_percent,
                "rss_mb": status.rss_mb,
                "pressure_level": "SEVERE",
                "backpressure_recommended": True
            })
        elif self.memory_pressure == MemoryPressure.CRITICAL:
            self.emit_event(str(EventType.MEMORY_CRITICAL), {
                "service": self.name,
                "usage_percent": status.system_percent,
                "rss_mb": status.rss_mb,
                "pressure_level": "CRITICAL",
                "backpressure_recommended": True
            })
        elif self.memory_pressure == MemoryPressure.WARNING:
            self.emit_event(str(EventType.MEMORY_WARNING), {
                "service": self.name,
                "usage_percent": status.system_percent,
                "rss_mb": status.rss_mb,
                "pressure_level": "WARNING",
                "backpressure_recommended": False
            })
    
    def _handle_backpressure(self, status) -> None:
        """Handle backpressure signals based on memory pressure."""
        if self.memory_pressure in [MemoryPressure.CRITICAL, MemoryPressure.SEVERE]:
            if not self.backpressure_active:
                self.backpressure_active = True
                self.emit_event("MEMORY_BACKPRESSURE_ACTIVE", {
                    "service": self.name,
                    "usage_percent": status.system_percent,
                    "pressure_level": self.memory_pressure.value,
                    "reason": "Memory pressure above critical threshold"
                })
                logger.warning(f"Memory backpressure activated at {status.system_percent:.1f}%")
        else:
            if self.backpressure_active:
                self.backpressure_active = False
                self.emit_event("MEMORY_BACKPRESSURE_RELEASED", {
                    "service": self.name,
                    "usage_percent": status.system_percent,
                    "pressure_level": self.memory_pressure.value,
                    "reason": "Memory pressure below critical threshold"
                })
                logger.info(f"Memory backpressure released at {status.system_percent:.1f}%")
    
    def get_memory_pressure(self) -> MemoryPressure:
        """Get current memory pressure state."""
        return self.memory_pressure
    
    def is_backpressure_active(self) -> bool:
        """Check if backpressure is currently active."""
        return self.backpressure_active
    
    def get_memory_trend(self, limit: int = 10) -> list:
        """Get recent memory usage trend."""
        return self.memory_trend[-limit:] if self.memory_trend else []
