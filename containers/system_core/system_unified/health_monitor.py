"""
System Unified Health Monitor - System Health Monitoring Infrastructure
Provides health monitoring capabilities
NO LAZY LOADING - All components load directly
"""

import time
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum

class HealthStatus(Enum):
    """Health status enumeration"""
    HEALTHY = "healthy"
    DEGRADED = "degraded"
    UNHEALTHY = "unhealthy"
    CRITICAL = "critical"

@dataclass
class HealthMetric:
    """Health metric data structure"""
    metric_id: str
    value: float
    status: HealthStatus
    threshold: float
    timestamp_ns: int = 0
    
    def __post_init__(self):
        if self.timestamp_ns == 0:
            self.timestamp_ns = datetime.now().timestamp_ns()

class HealthMonitor:
    """Health monitor for system health operations"""
    
    def __init__(self):
        self._metrics: Dict[str, HealthMetric] = {}
        self._overall_status = HealthStatus.HEALTHY
        self._last_check = time.time()
        
    def record_metric(self, metric_id: str, value: float, threshold: float):
        """Record health metric"""
        # Determine status based on threshold
        if value > threshold:
            status = HealthStatus.CRITICAL
        elif value > threshold * 0.8:
            status = HealthStatus.UNHEALTHY
        elif value > threshold * 0.6:
            status = HealthStatus.DEGRADED
        else:
            status = HealthStatus.HEALTHY
        
        metric = HealthMetric(
            metric_id=metric_id,
            value=value,
            status=status,
            threshold=threshold
        )
        
        self._metrics[metric_id] = metric
        self._last_check = time.time()
        self._update_overall_status()
        
    def get_metric(self, metric_id: str) -> Optional[HealthMetric]:
        """Get metric by ID"""
        return self._metrics.get(metric_id)
    
    def get_overall_status(self) -> HealthStatus:
        """Get overall system health status"""
        return self._overall_status
    
    def get_all_metrics(self) -> Dict[str, HealthMetric]:
        """Get all metrics"""
        return self._metrics.copy()
    
    def _update_overall_status(self):
        """Update overall health status based on metrics"""
        if not self._metrics:
            self._overall_status = HealthStatus.HEALTHY
            return
        
        # Determine worst status
        worst_status = HealthStatus.HEALTHY
        for metric in self._metrics.values():
            if metric.status == HealthStatus.CRITICAL:
                worst_status = HealthStatus.CRITICAL
                break
            elif metric.status == HealthStatus.UNHEALTHY and worst_status != HealthStatus.CRITICAL:
                worst_status = HealthStatus.UNHEALTHY
            elif metric.status == HealthStatus.DEGRADED and worst_status not in [HealthStatus.CRITICAL, HealthStatus.UNHEALTHY]:
                worst_status = HealthStatus.DEGRADED
        
        self._overall_status = worst_status

# Global instance
_health_monitor = None

def get_health_monitor() -> HealthMonitor:
    """Get global health monitor instance"""
    global _health_monitor
    if _health_monitor is None:
        _health_monitor = HealthMonitor()
    return _health_monitor

def record_health_metric(metric_id: str, value: float, threshold: float):
    """Record health metric (convenience function)"""
    monitor = get_health_monitor()
    monitor.record_metric(metric_id, value, threshold)

def get_health_status() -> HealthStatus:
    """Get overall health status (convenience function)"""
    monitor = get_health_monitor()
    return monitor.get_overall_status()

def check_health() -> bool:
    """Check if system is healthy (convenience function)"""
    monitor = get_health_monitor()
    return monitor.get_overall_status() in [HealthStatus.HEALTHY, HealthStatus.DEGRADED]

__all__ = [
    'HealthStatus',
    'HealthMetric',
    'HealthMonitor',
    'get_health_monitor',
    'record_health_metric',
    'get_health_status',
    'check_health'
]