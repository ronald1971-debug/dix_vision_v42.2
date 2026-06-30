"""
DIX VISION Data Pipeline Optimization Service

Provides data pipeline optimization including parallel processing, streaming,
caching, and query optimization for enhanced data processing performance.
"""

from __future__ import annotations

import logging
import threading
import time
from concurrent.futures import ThreadPoolExecutor, ProcessPoolExecutor
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Callable, Dict, List, Optional, Tuple
from typing import AsyncIterator
import asyncio
from collections import deque

from runtime.event_bus import EventBus, Event, EventType, get_event_bus
from runtime.service_manager import Service, ServiceState, ServiceHealth

logger = logging.getLogger(__name__)


class ProcessingMode(Enum):
    """Data processing modes."""
    BATCH = "batch"
    STREAMING = "streaming"
    HYBRID = "hybrid"


class CacheStrategy(Enum):
    """Cache strategies."""
    LRU = "lru"
    FIFO = "fifo"
    LFU = "lfu"
    TTL = "ttl"


@dataclass
class PipelineConfig:
    """Configuration for data pipeline optimization."""
    mode: ProcessingMode = ProcessingMode.HYBRID
    parallel_workers: int = 4
    chunk_size: int = 1000
    cache_strategy: CacheStrategy = CacheStrategy.LRU
    cache_size: int = 1000
    cache_ttl: int = 3600  # seconds
    enable_query_caching: bool = True
    enable_streaming: bool = True
    enable_backpressure: bool = True


@dataclass
class PipelineMetrics:
    """Data pipeline performance metrics."""
    total_processed: int = 0
    processing_time_total: float = 0.0
    average_throughput: float = 0.0
    cache_hit_rate: float = 0.0
    cache_miss_rate: float = 0.0
    parallel_efficiency: float = 0.0
    queue_utilization: float = 0.0
    active_workers: int = 0
    timestamp: float = field(default_factory=time.time)


class DataPipelineService(Service):
    """Data pipeline optimization service as per Runtime Specification."""
    
    # Service dependencies
    DEPENDENCIES = ["memory_service"]
    
    def __init__(self):
        super().__init__("data_pipeline_service")
        self.config: Optional[PipelineConfig] = None
        self.metrics = PipelineMetrics()
        self._lock = threading.Lock()
        self._thread_pool: Optional[ThreadPoolExecutor] = None
        self._process_pool: Optional[ProcessPoolExecutor] = None
        self._cache: Dict[str, Any] = {}
        self._cache_stats = {"hits": 0, "misses": 0}
        self._processing_queue: deque = deque(maxlen=10000)
        self._backpressure_state = "NORMAL"
        self._backpressure_thresholds = {
            "elevated": 0.60,
            "high": 0.80,
            "critical": 0.95
        }
        
    def init(self, event_bus: EventBus, config: Dict[str, Any]) -> bool:
        """Initialize the data pipeline service."""
        try:
            self.event_bus = event_bus
            self.config = PipelineConfig(**config.get("data_pipeline", {}))
            self.state = ServiceState.INITIALIZING
            
            # Initialize thread pool for I/O-bound tasks
            self._thread_pool = ThreadPoolExecutor(
                max_workers=self.config.parallel_workers,
                thread_name_prefix="pipeline_"
            )
            
            # Initialize process pool for CPU-bound tasks
            self._process_pool = ProcessPoolExecutor(
                max_workers=max(1, self.config.parallel_workers // 2),
            )
            
            logger.info("Data Pipeline Service initialized")
            return True
        except Exception as e:
            logger.error(f"Data Pipeline Service initialization failed: {e}")
            self.state = ServiceState.ERROR
            return False
    
    def start(self) -> bool:
        """Start the data pipeline service."""
        try:
            self.state = ServiceState.STARTING
            
            # Start background metrics collector
            self._start_metrics_collector()
            
            self.state = ServiceState.RUNNING
            self.emit_event(str(EventType.SERVICE_START), {"service": self.name})
            logger.info("Data Pipeline Service started")
            return True
        except Exception as e:
            logger.error(f"Data Pipeline Service start failed: {e}")
            self.state = ServiceState.ERROR
            self.emit_event(str(EventType.SERVICE_CRASH), {"service": self.name, "error": str(e)})
            return False
    
    def stop(self) -> bool:
        """Stop the data pipeline service."""
        try:
            self.state = ServiceState.STOPPING
            
            # Shutdown thread pool
            if self._thread_pool:
                self._thread_pool.shutdown(wait=True)
            
            # Shutdown process pool
            if self._process_pool:
                self._process_pool.shutdown(wait=True)
            
            self.state = ServiceState.STOPPED
            self.emit_event(str(EventType.SERVICE_STOP), {"service": self.name})
            logger.info("Data Pipeline Service stopped")
            return True
        except Exception as e:
            logger.error(f"Data Pipeline Service stop failed: {e}")
            self.state = ServiceState.ERROR
            return False
    
    def health(self) -> ServiceHealth:
        """Get data pipeline service health."""
        return ServiceHealth(
            service=self.name,
            state=self.state,
            healthy=self.state == ServiceState.RUNNING,
            message=f"Data Pipeline Service - Mode: {self.config.mode.value}",
            details={
                "processing_mode": self.config.mode.value,
                "parallel_workers": self.config.parallel_workers,
                "cache_strategy": self.config.cache_strategy.value,
                "cache_hit_rate": self.metrics.cache_hit_rate,
                "average_throughput": self.metrics.average_throughput,
                "backpressure_state": self._backpressure_state,
                "queue_size": len(self._processing_queue)
            },
            timestamp=time.time()
        )
    
    def process_parallel(self, data: List[Any], processor: Callable[[Any], Any]) -> List[Any]:
        """Process data in parallel using thread pool."""
        self._update_backpressure()
        
        if self._backpressure_state == "CRITICAL":
            logger.warning("Backpressure CRITICAL - using serial processing")
            return [processor(item) for item in data]
        
        try:
            results = list(self._thread_pool.map(processor, data))
            self._update_metrics(len(data), time.time())
            return results
        except Exception as e:
            logger.error(f"Parallel processing failed: {e}")
            return [processor(item) for item in data]
    
    def process_streaming(self, data_stream: AsyncIterator[Any], processor: Callable[[Any], Any]) -> AsyncIterator[Any]:
        """Process data in streaming mode."""
        async def process_stream():
            async for item in data_stream:
                if self._should_backpressure():
                    logger.warning("Backpressure - dropping stream item")
                    continue
                result = processor(item)
                yield result
        
        return process_stream()
    
    def get_cached(self, key: str) -> Optional[Any]:
        """Get data from cache."""
        with self._lock:
            if key in self._cache:
                self._cache_stats["hits"] += 1
                return self._cache[key]
            self._cache_stats["misses"] += 1
            return None
    
    def set_cached(self, key: str, value: Any) -> None:
        """Set data in cache."""
        with self._lock:
            if len(self._cache) >= self.config.cache_size:
                self._evict_cache()
            self._cache[key] = value
    
    def _evict_cache(self) -> None:
        """Evict items from cache based on strategy."""
        if self.config.cache_strategy == CacheStrategy.LRU:
            # Simple LRU - remove oldest item
            if self._cache:
                oldest_key = next(iter(self._cache))
                del self._cache[oldest_key]
        elif self.config.cache_strategy == CacheStrategy.FIFO:
            # FIFO - remove first item
            if self._cache:
                first_key = next(iter(self._cache))
                del self._cache[first_key]
        elif self.config.cache_strategy == CacheStrategy.LFU:
            # LFU - remove least frequently used
            if self._cache:
                lfu_key = min(self._cache_stats, key=lambda k: self._cache_stats.get(k, 0))
                if lfu_key in self._cache:
                    del self._cache[lfu_key]
    
    def _update_backpressure(self) -> None:
        """Update backpressure state based on queue utilization."""
        queue_utilization = len(self._processing_queue) / self._processing_queue.maxlen
        
        if queue_utilization >= self._backpressure_thresholds["critical"]:
            self._backpressure_state = "CRITICAL"
        elif queue_utilization >= self._backpressure_thresholds["high"]:
            self._backpressure_state = "HIGH"
        elif queue_utilization >= self._backpressure_thresholds["elevated"]:
            self._backpressure_state = "ELEVATED"
        else:
            self._backpressure_state = "NORMAL"
    
    def _should_backpressure(self) -> bool:
        """Check if backpressure should be applied."""
        return self._backpressure_state in ["HIGH", "CRITICAL"]
    
    def _update_metrics(self, processed_count: int, processing_time: float) -> None:
        """Update pipeline metrics."""
        with self._lock:
            self.metrics.total_processed += processed_count
            self.metrics.processing_time_total += processing_time
            
            if self.metrics.total_processed > 0:
                self.metrics.average_throughput = self.metrics.total_processed / self.metrics.processing_time_total
            
            if self._cache_stats["hits"] + self._cache_stats["misses"] > 0:
                self.metrics.cache_hit_rate = self._cache_stats["hits"] / (
                    self._cache_stats["hits"] + self._cache_stats["misses"]
                )
                self.metrics.cache_miss_rate = 1.0 - self.metrics.cache_hit_rate
    
    def _start_metrics_collector(self) -> None:
        """Start background metrics collector."""
        def collect_metrics():
            while self.state == ServiceState.RUNNING:
                try:
                    self.metrics.active_workers = len(self._thread_pool._threads) if self._thread_pool else 0
                    self.metrics.queue_utilization = len(self._processing_queue) / self._processing_queue.maxlen
                    time.sleep(5)  # Collect every 5 seconds
                except Exception as e:
                    logger.error(f"Metrics collection error: {e}")
                    time.sleep(10)
        
        thread = threading.Thread(target=collect_metrics, daemon=True)
        thread.start()
        logger.info("Metrics collector started")
    
    def get_pipeline_stats(self) -> Dict[str, Any]:
        """Get pipeline statistics."""
        with self._lock:
            return {
                "total_processed": self.metrics.total_processed,
                "processing_time_total": self.metrics.processing_time_total,
                "average_throughput": self.metrics.average_throughput,
                "cache_hit_rate": self.metrics.cache_hit_rate,
                "cache_miss_rate": self.metrics.cache_miss_rate,
                "cache_size": len(self._cache),
                "cache_max_size": self.config.cache_size,
                "backpressure_state": self._backpressure_state,
                "queue_size": len(self._processing_queue),
                "active_workers": self.metrics.active_workers
            }


# Global instance
_data_pipeline_service: Optional[DataPipelineService] = None


def get_data_pipeline_service() -> DataPipelineService:
    """Get global data pipeline service instance."""
    global _data_pipeline_service
    if _data_pipeline_service is None:
        _data_pipeline_service = DataPipelineService()
    return _data_pipeline_service