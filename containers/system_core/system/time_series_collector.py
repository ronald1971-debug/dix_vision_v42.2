"""
system/time_series_collector.py
DIX VISION v42.2 — Time-Series Data Collector

Collects and stores time-series metrics for historical analysis and trend visualization.
Provides in-memory storage that can be extended to use time-series databases (InfluxDB, TimescaleDB).
"""

from __future__ import annotations

import threading
from collections import deque
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from typing import Any
import time

from system.time_source import utc_now


@dataclass
class TimeSeriesPoint:
    """Single time-series data point."""
    timestamp: datetime
    value: float
    metadata: dict[str, Any] = field(default_factory=dict)


class TimeSeriesBuffer:
    """Fixed-size circular buffer for time-series data."""
    
    def __init__(self, max_size: int = 1000):
        self._buffer: deque[TimeSeriesPoint] = deque(maxlen=max_size)
        self._lock = threading.Lock()
        self._max_size = max_size
    
    def add(self, point: TimeSeriesPoint) -> None:
        """Add a data point to the buffer."""
        with self._lock:
            self._buffer.append(point)
    
    def get_latest(self, count: int = 10) -> list[TimeSeriesPoint]:
        """Get the latest N data points."""
        with self._lock:
            return list(self._buffer)[-count:]
    
    def get_range(self, start: datetime, end: datetime) -> list[TimeSeriesPoint]:
        """Get data points within a time range."""
        with self._lock:
            return [
                point for point in self._buffer
                if start <= point.timestamp <= end
            ]
    
    def get_stats(self) -> dict[str, float]:
        """Get basic statistics from the buffer."""
        with self._lock:
            if not self._buffer:
                return {"count": 0, "min": 0.0, "max": 0.0, "avg": 0.0, "latest": 0.0}
            
            values = [point.value for point in self._buffer]
            return {
                "count": len(values),
                "min": min(values),
                "max": max(values),
                "avg": sum(values) / len(values),
                "latest": values[-1] if values else 0.0
            }
    
    def clear_old(self, before: datetime) -> int:
        """Remove data points older than the given timestamp."""
        with self._lock:
            initial_count = len(self._buffer)
            self._buffer = deque(
                [point for point in self._buffer if point.timestamp >= before],
                maxlen=self._max_size
            )
            return initial_count - len(self._buffer)


class TimeSeriesCollector:
    """Manages multiple time-series buffers for different metrics."""
    
    def __init__(self):
        self._buffers: dict[str, TimeSeriesBuffer] = {}
        self._lock = threading.Lock()
        self._collection_interval = 5.0  # seconds
        self._stop_event = threading.Event()
        self._collector_thread: threading.Thread | None = None
        
    def register_metric(self, metric_name: str, max_points: int = 1000) -> None:
        """Register a new metric for collection."""
        with self._lock:
            if metric_name not in self._buffers:
                self._buffers[metric_name] = TimeSeriesBuffer(max_size=max_points)
    
    def collect(self, metric_name: str, value: float, metadata: dict[str, Any] | None = None) -> None:
        """Collect a data point for a metric."""
        with self._lock:
            if metric_name not in self._buffers:
                self.register_metric(metric_name)
            
            point = TimeSeriesPoint(
                timestamp=utc_now(),
                value=value,
                metadata=metadata or {}
            )
            self._buffers[metric_name].add(point)
    
    def get_metric_data(self, metric_name: str, count: int = 100) -> list[TimeSeriesPoint]:
        """Get the latest data points for a metric."""
        with self._lock:
            if metric_name in self._buffers:
                return self._buffers[metric_name].get_latest(count)
            return []
    
    def get_metric_stats(self, metric_name: str) -> dict[str, float]:
        """Get statistics for a metric."""
        with self._lock:
            if metric_name in self._buffers:
                return self._buffers[metric_name].get_stats()
            return {"count": 0, "min": 0.0, "max": 0.0, "avg": 0.0, "latest": 0.0}
    
    def get_all_metrics(self) -> dict[str, dict[str, float]]:
        """Get statistics for all metrics."""
        with self._lock:
            return {name: buffer.get_stats() for name, buffer in self._buffers.items()}
    
    def start_auto_collection(self, collection_func, interval: float = 5.0) -> None:
        """Start automatic collection with a custom collection function."""
        self._collection_interval = interval
        self._stop_event.clear()
        self._collector_thread = threading.Thread(
            target=self._auto_collect_loop,
            args=(collection_func,),
            daemon=True,
            name="TimeSeriesCollector"
        )
        self._collector_thread.start()
    
    def stop_auto_collection(self) -> None:
        """Stop automatic collection."""
        self._stop_event.set()
        if self._collector_thread:
            self._collector_thread.join(timeout=5.0)
    
    def _auto_collect_loop(self, collection_func) -> None:
        """Internal loop for automatic collection."""
        while not self._stop_event.is_set():
            try:
                collection_func(self)
            except Exception as e:
                print(f"Error in auto collection: {e}")
            time.sleep(self._collection_interval)
    
    def cleanup_old_data(self, older_than_hours: int = 24) -> int:
        """Remove data older than the specified number of hours."""
        cutoff = utc_now() - timedelta(hours=older_than_hours)
        total_removed = 0
        with self._lock:
            for buffer in self._buffers.values():
                total_removed += buffer.clear_old(cutoff)
        return total_removed


# Singleton instance
_collector: TimeSeriesCollector | None = None
_lock = threading.Lock()


def get_time_series_collector() -> TimeSeriesCollector:
    """Get the global time-series collector instance."""
    global _collector
    if _collector is None:
        with _lock:
            if _collector is None:
                _collector = TimeSeriesCollector()
    return _collector


__all__ = [
    "TimeSeriesPoint",
    "TimeSeriesBuffer",
    "TimeSeriesCollector",
    "get_time_series_collector",
]
