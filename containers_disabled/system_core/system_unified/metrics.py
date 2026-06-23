"""
System Unified Metrics - Metrics Infrastructure
Provides system metrics capabilities
NO LAZY LOADING - All components load directly
"""

import logging
from typing import Any, Dict, Optional

logger = logging.getLogger(__name__)


class SystemMetrics:
    """System metrics collector"""

    def __init__(self):
        self._metrics = {}
        self._counters = {}

    def record_metric(self, metric_name: str, value: float):
        """Record a metric value"""
        if metric_name not in self._metrics:
            self._metrics[metric_name] = []
        self._metrics[metric_name].append(value)

    def increment_counter(self, counter_name: str):
        """Increment a counter"""
        self._counters[counter_name] = self._counters.get(counter_name, 0) + 1

    def get_metric(self, metric_name: str) -> Optional[float]:
        """Get latest metric value"""
        if metric_name in self._metrics and self._metrics[metric_name]:
            return self._metrics[metric_name][-1]
        return None

    def get_counter(self, counter_name: str) -> int:
        """Get counter value"""
        return self._counters.get(counter_name, 0)

    def get_metrics(self) -> Dict[str, Any]:
        """Get all metrics"""
        return {"metrics": self._metrics, "counters": self._counters}


# Global instance
_system_metrics = None


def get_system_metrics() -> SystemMetrics:
    """Get system metrics instance"""
    global _system_metrics
    if _system_metrics is None:
        _system_metrics = SystemMetrics()
    return _system_metrics


def get_metrics() -> Dict[str, Any]:
    """Get metrics dictionary"""
    return get_system_metrics().get_metrics()


__all__ = ["SystemMetrics", "get_system_metrics", "get_metrics"]
