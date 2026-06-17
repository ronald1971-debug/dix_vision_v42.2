"""
execution_unified.health.health_monitor
DIX VISION v42.2 — Comprehensive Health Monitor (Quick Win)

Provides comprehensive health monitoring for all system components.
This is a quick win implementation for system resilience.
"""

from __future__ import annotations

import logging
import threading
import time
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional, Callable
from dataclasses import dataclass, field
from enum import Enum

logger = logging.getLogger(__name__)


class HealthStatus(Enum):
    """Health status levels."""
    HEALTHY = "HEALTHY"
    DEGRADED = "DEGRADED"
    UNHEALTHY = "UNHEALTHY"
    CRITICAL = "CRITICAL"
    UNKNOWN = "UNKNOWN"


@dataclass
class HealthCheck:
    """Individual health check result."""
    
    component: str
    status: HealthStatus
    message: str
    timestamp: datetime
    metrics: Dict[str, float] = field(default_factory=dict)
    details: Dict[str, Any] = field(default_factory=dict)
    
    @property
    def is_healthy(self) -> bool:
        return self.status in [HealthStatus.HEALTHY, HealthStatus.DEGRADED]


@dataclass
class SystemHealthReport:
    """Comprehensive system health report."""
    
    overall_status: HealthStatus
    component_checks: Dict[str, HealthCheck]
    timestamp: datetime
    total_components: int
    healthy_components: int
    degraded_components: int
    unhealthy_components: int
    critical_components: int
    overall_health_score: float  # 0.0 - 1.0
    
    @property
    def is_healthy(self) -> bool:
        return self.overall_status in [HealthStatus.HEALTHY, HealthStatus.DEGRADED]
    
    @property
    def health_percentage(self) -> float:
        if self.total_components == 0:
            return 100.0
        return (self.healthy_components / self.total_components) * 100


class HealthCheckProvider:
    """Base class for health check providers."""
    
    def __init__(self, component_name: str):
        self.component_name = component_name
    
    def check_health(self) -> HealthCheck:
        """Perform health check for the component."""
        raise NotImplementedError


class HealthMonitor:
    """
    Comprehensive health monitoring system.
    
    Monitors all system components and provides unified health reports.
    """
    
    def __init__(self, check_interval_ms: int = 5000):
        self._lock = threading.Lock()
        self._check_interval_ms = check_interval_ms
        self._health_check_providers: Dict[str, HealthCheckProvider] = {}
        
        # Health check results cache
        self._health_cache: Dict[str, HealthCheck] = {}
        self._last_health_report: Optional[SystemHealthReport] = None
        
        # Background monitoring
        self._monitoring_active = False
        self._monitor_thread: Optional[threading.Thread] = None
        
        # Metrics
        self._total_checks = 0
        self._total_alerts = 0
        
        logger.info("[HEALTH_MONITOR] Initialized with check interval: {check_interval_ms}ms")
    
    def register_provider(self, provider: HealthCheckProvider) -> None:
        """Register a health check provider."""
        with self._lock:
            self._health_check_providers[provider.component_name] = provider
            logger.info(f"[HEALTH_MONITOR] Registered health check provider: {provider.component_name}")
    
    def check_component_health(self, component: str) -> HealthCheck:
        """Check health of a specific component."""
        provider = self._health_check_providers.get(component)
        if provider:
            try:
                health_check = provider.check_health()
                self._health_cache[component] = health_check
                self._total_checks += 1
                return health_check
            except Exception as e:
                logger.error(f"[HEALTH_MONITOR] Health check failed for {component}: {e}")
                return HealthCheck(
                    component=component,
                    status=HealthStatus.UNKNOWN,
                    message=f"Health check failed: {str(e)}",
                    timestamp=datetime.utcnow()
                )
        else:
            return HealthCheck(
                component=component,
                status=HealthStatus.UNKNOWN,
                message="No health check provider registered",
                timestamp=datetime.utcnow()
            )
    
    def check_system_health(self) -> SystemHealthReport:
        """Check health of all registered components."""
        component_checks = {}
        
        with self._lock:
            for component in self._health_check_providers.keys():
                try:
                    health_check = self.check_component_health(component)
                    component_checks[component] = health_check
                except Exception as e:
                    logger.error(f"[HEALTH_MONITOR] Failed to check {component}: {e}")
                    component_checks[component] = HealthCheck(
                        component=component,
                        status=HealthStatus.UNKNOWN,
                        message=f"Check failed: {str(e)}",
                        timestamp=datetime.utcnow()
                    )
        
        # Calculate overall health
        total_components = len(component_checks)
        healthy = sum(1 for hc in component_checks.values() if hc.status == HealthStatus.HEALTHY)
        degraded = sum(1 for hc in component_checks.values() if hc.status == HealthStatus.DEGRADED)
        unhealthy = sum(1 for hc in component_checks.values() if hc.status == HealthStatus.UNHEALTHY)
        critical = sum(1 for hc in component_checks.values() if hc.status == HealthStatus.CRITICAL)
        
        # Determine overall status
        if critical > 0:
            overall_status = HealthStatus.CRITICAL
        elif unhealthy > 0:
            overall_status = HealthStatus.UNHEALTHY
        elif degraded > 0:
            overall_status = HealthStatus.DEGRADED
        elif healthy == total_components:
            overall_status = HealthStatus.HEALTHY
        else:
            overall_status = HealthStatus.UNKNOWN
        
        # Calculate health score
        health_score = (healthy + degraded * 0.5) / total_components if total_components > 0 else 0.0
        
        report = SystemHealthReport(
            overall_status=overall_status,
            component_checks=component_checks,
            timestamp=datetime.utcnow(),
            total_components=total_components,
            healthy_components=healthy,
            degraded_components=degraded,
            unhealthy_components=unhealthy,
            critical_components=critical,
            overall_health_score=health_score
        )
        
        self._last_health_report = report
        
        # Log if not healthy
        if not report.is_healthy:
            self._total_alerts += 1
            logger.warning(
                f"[HEALTH_MONITOR] System not healthy: {overall_status.value}, "
                f"score={health_score:.2f}, "
                f"critical={critical}, unhealthy={unhealthy}, degraded={degraded}"
            )
        
        return report
    
    def start_monitoring(self) -> None:
        """Start background health monitoring."""
        if self._monitoring_active:
            logger.warning("[HEALTH_MONITOR] Monitoring already active")
            return
        
        self._monitoring_active = True
        self._monitor_thread = threading.Thread(target=self._monitor_loop, daemon=True)
        self._monitor_thread.start()
        
        logger.info("[HEALTH_MONITOR] Started background health monitoring")
    
    def stop_monitoring(self) -> None:
        """Stop background health monitoring."""
        self._monitoring_active = False
        if self._monitor_thread:
            self._monitor_thread.join(timeout=5.0)
            logger.info("[HEALTH_MONITOR] Stopped background health monitoring")
    
    def _monitor_loop(self) -> None:
        """Background monitoring loop."""
        while self._monitoring_active:
            try:
                self.check_system_health()
                time.sleep(self._check_interval_ms / 1000)
            except Exception as e:
                logger.error(f"[HEALTH_MONITOR] Monitoring loop error: {e}")
                time.sleep(self._check_interval_ms / 1000)
    
    def get_last_report(self) -> Optional[SystemHealthReport]:
        """Get the last health report."""
        return self._last_health_report
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get health monitoring statistics."""
        with self._lock:
            return {
                "monitoring_active": self._monitoring_active,
                "total_checks": self._total_checks,
                "total_alerts": self._total_alerts,
                "registered_providers": len(self._health_check_providers),
                "check_interval_ms": self._check_interval_ms,
                "last_report": self._last_health_report.overall_status.value if self._last_health_report else None
            }


# Built-in health check providers

class ExecutionKernelHealthCheck(HealthCheckProvider):
    """Health check for execution kernel."""
    
    def __init__(self):
        super().__init__("execution_kernel")
    
    def check_health(self) -> HealthCheck:
        try:
            from execution_unified import get_unified_execution_kernel
            kernel = get_unified_execution_kernel()
            
            metrics = kernel.get_metrics() if hasattr(kernel, 'get_metrics') else {}
            
            # Determine health based on metrics
            if metrics.get('health_score', 1.0) > 0.8:
                status = HealthStatus.HEALTHY
                message = "Execution kernel healthy"
            elif metrics.get('health_score', 0.0) > 0.5:
                status = HealthStatus.DEGRADED
                message = "Execution kernel degraded"
            else:
                status = HealthStatus.UNHEALTHY
                message = "Execution kernel unhealthy"
            
            return HealthCheck(
                component=self.component_name,
                status=status,
                message=message,
                timestamp=datetime.utcnow(),
                metrics=metrics
            )
        except Exception as e:
            return HealthCheck(
                component=self.component_name,
                status=HealthStatus.UNKNOWN,
                message=f"Health check failed: {str(e)}",
                timestamp=datetime.utcnow()
            )


class CognitiveOSHealthCheck(HealthCheckProvider):
    """Health check for Cognitive OS."""
    
    def __init__(self):
        super().__init__("cognitive_os")
    
    def check_health(self) -> HealthCheck:
        try:
            from cognitive_os.core import get_cognitive_os_kernel
            kernel = get_cognitive_os_kernel()
            
            metrics = kernel.get_system_metrics()
            
            health_score = metrics.health_score
            
            if health_score > 0.8:
                status = HealthStatus.HEALTHY
                message = "Cognitive OS healthy"
            elif health_score > 0.6:
                status = HealthStatus.DEGRADED
                message = "Cognitive OS degraded"
            elif health_score > 0.4:
                status = HealthStatus.UNHEALTHY
                message = "Cognitive OS unhealthy"
            else:
                status = HealthStatus.CRITICAL
                message = "Cognitive OS critical"
            
            return HealthCheck(
                component=self.component_name,
                status=status,
                message=message,
                timestamp=datetime.utcnow(),
                metrics={
                    "health_score": health_score,
                    "performance_score": metrics.performance_score,
                    "active_layers": len(metrics.active_layers)
                }
            )
        except Exception as e:
            return HealthCheck(
                component=self.component_name,
                status=HealthStatus.UNKNOWN,
                message=f"Health check failed: {str(e)}",
                timestamp=datetime.utcnow()
            )


# Singleton instance
_health_monitor: Optional[HealthMonitor] = None
_health_monitor_lock = threading.Lock()

def get_health_monitor(check_interval_ms: int = 5000) -> HealthMonitor:
    """Get the singleton health monitor instance."""
    global _health_monitor
    if _health_monitor is None:
        with _health_monitor_lock:
            if _health_monitor is None:
                _health_monitor = HealthMonitor(check_interval_ms)
                
                # Register built-in health check providers
                _health_monitor.register_provider(ExecutionKernelHealthCheck())
                _health_monitor.register_provider(CognitiveOSHealthCheck())
                
    return _health_monitor


__all__ = [
    "HealthStatus",
    "HealthCheck",
    "SystemHealthReport",
    "HealthCheckProvider",
    "HealthMonitor",
    "get_health_monitor",
    "ExecutionKernelHealthCheck",
    "CognitiveOSHealthCheck",
]