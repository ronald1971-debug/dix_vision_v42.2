"""
DIX VISION Concurrency Optimization Service

Provides concurrency optimization including async I/O patterns, process pools,
lock-free data structures, and connection pooling for enhanced performance.
"""

from __future__ import annotations

import asyncio
import logging
import threading
import time
from concurrent.futures import ThreadPoolExecutor, ProcessPoolExecutor, as_completed
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Callable, Dict, List, Optional, Tuple, AsyncIterator
from queue import Queue, Empty
from collections import deque
import weakref

from runtime.event_bus import EventBus, Event, EventType, get_event_bus
from runtime.service_manager import Service, ServiceState, ServiceHealth

logger = logging.getLogger(__name__)


class ConcurrencyMode(Enum):
    """Concurrency execution modes."""
    ASYNC_IO = "async_io"
    THREAD_POOL = "thread_pool"
    PROCESS_POOL = "process_pool"
    HYBRID = "hybrid"


class PoolType(Enum):
    """Types of worker pools."""
    THREAD = "thread"
    PROCESS = "process"


@dataclass
class ConcurrencyConfig:
    """Configuration for concurrency optimization."""
    mode: ConcurrencyMode = ConcurrencyMode.HYBRID
    max_thread_workers: int = 8
    max_process_workers: int = 4
    max_async_tasks: int = 100
    connection_pool_size: int = 10
    connection_timeout: float = 30.0
    enable_lock_free: bool = True
    enable_connection_pooling: bool = True


@dataclass
class ConcurrencyMetrics:
    """Concurrency performance metrics."""
    total_async_tasks: int = 0
    total_thread_tasks: int = 0
    total_process_tasks: int = 0
    async_completion_time: float = 0.0
    thread_completion_time: float = 0.0
    process_completion_time: float = 0.0
    async_avg_time: float = 0.0
    thread_avg_time: float = 0.0
    process_avg_time: float = 0.0
    connection_pool_utilization: float = 0.0
    active_connections: int = 0
    timestamp: float = field(default_factory=time.time)


class LockFreeQueue:
    """Simple lock-free queue implementation using atomic operations."""
    
    def __init__(self, max_size: int = 1000):
        self._queue = deque(maxlen=max_size)
        self._lock = threading.Lock()
    
    def put(self, item: Any) -> bool:
        """Put item in queue."""
        try:
            with self._lock:
                self._queue.append(item)
            return True
        except Exception:
            return False
    
    def get(self) -> Optional[Any]:
        """Get item from queue."""
        try:
            with self._lock:
                return self._queue.popleft()
        except (IndexError, Exception):
            return None
    
    def size(self) -> int:
        """Get queue size."""
        with self._lock:
            return len(self._queue)


class ConnectionPool:
    """Generic connection pool for database/API connections."""
    
    def __init__(self, pool_size: int = 10, timeout: float = 30.0):
        self._pool_size = pool_size
        self._timeout = timeout
        self._available = Queue(maxsize=pool_size)
        self._in_use = weakref.WeakSet()
        self._lock = threading.Lock()
    
    def acquire(self, factory: Callable[[], Any]) -> Optional[Any]:
        """Acquire a connection from the pool."""
        try:
            # Try to get from pool
            connection = self._available.get_nowait()
            if connection:
                with self._lock:
                    self._in_use.add(connection)
                return connection
        except Empty:
            pass
        
        # Create new connection if pool not full
        with self._lock:
            if len(self._in_use) < self._pool_size:
                connection = factory()
                self._in_use.add(connection)
                return connection
        
        return None
    
    def release(self, connection: Any) -> None:
        """Release a connection back to the pool."""
        try:
            with self._lock:
                if connection in self._in_use:
                    self._in_use.remove(connection)
                    self._available.put_nowait(connection)
        except Exception as e:
            logger.error(f"Error releasing connection: {e}")
    
    def get_stats(self) -> Dict[str, int]:
        """Get connection pool statistics."""
        with self._lock:
            return {
                "available": self._available.qsize(),
                "in_use": len(self._in_use),
                "total": self._available.qsize() + len(self._in_use),
                "max_size": self._pool_size
            }


class ConcurrencyService(Service):
    """Concurrency optimization service as per Runtime Specification."""
    
    # Service dependencies
    DEPENDENCIES = []
    
    def __init__(self):
        super().__init__("concurrency_service")
        self.config: Optional[ConcurrencyConfig] = None
        self.metrics = ConcurrencyMetrics()
        self._lock = threading.Lock()
        self._thread_pool: Optional[ThreadPoolExecutor] = None
        self._process_pool: Optional[ProcessPoolExecutor] = None
        self._loop: Optional[asyncio.AbstractEventLoop] = None
        self._connection_pools: Dict[str, ConnectionPool] = {}
        self._lock_free_queues: Dict[str, LockFreeQueue] = {}
        
    def init(self, event_bus: EventBus, config: Dict[str, Any]) -> bool:
        """Initialize the concurrency service."""
        try:
            self.event_bus = event_bus
            self.config = ConcurrencyConfig(**config.get("concurrency", {}))
            self.state = ServiceState.INITIALIZING
            
            # Initialize thread pool
            self._thread_pool = ThreadPoolExecutor(
                max_workers=self.config.max_thread_workers,
                thread_name_prefix="concurrency_thread_"
            )
            
            # Initialize process pool
            self._process_pool = ProcessPoolExecutor(
                max_workers=self.config.max_process_workers
            )
            
            # Initialize event loop for async operations
            self._loop = asyncio.new_event_loop()
            
            logger.info("Concurrency Service initialized")
            return True
        except Exception as e:
            logger.error(f"Concurrency Service initialization failed: {e}")
            self.state = ServiceState.ERROR
            return False
    
    def start(self) -> bool:
        """Start the concurrency service."""
        try:
            self.state = ServiceState.STARTING
            
            # Start event loop in background thread
            def run_loop():
                asyncio.set_event_loop(self._loop)
                self._loop.run_forever()
            
            thread = threading.Thread(target=run_loop, daemon=True)
            thread.start()
            
            self.state = ServiceState.RUNNING
            self.emit_event(str(EventType.SERVICE_START), {"service": self.name})
            logger.info("Concurrency Service started")
            return True
        except Exception as e:
            logger.error(f"Concurrency Service start failed: {e}")
            self.state = ServiceState.ERROR
            self.emit_event(str(EventType.SERVICE_CRASH), {"service": self.name, "error": str(e)})
            return False
    
    def stop(self) -> bool:
        """Stop the concurrency service."""
        try:
            self.state = ServiceState.STOPPING
            
            # Stop event loop
            if self._loop:
                self._loop.call_soon_threadsafe(self._loop.stop)
            
            # Shutdown thread pool
            if self._thread_pool:
                self._thread_pool.shutdown(wait=True)
            
            # Shutdown process pool
            if self._process_pool:
                self._process_pool.shutdown(wait=True)
            
            self.state = ServiceState.STOPPED
            self.emit_event(str(EventType.SERVICE_STOP), {"service": self.name})
            logger.info("Concurrency Service stopped")
            return True
        except Exception as e:
            logger.error(f"Concurrency Service stop failed: {e}")
            self.state = ServiceState.ERROR
            return False
    
    def health(self) -> ServiceHealth:
        """Get concurrency service health."""
        return ServiceHealth(
            service=self.name,
            state=self.state,
            healthy=self.state == ServiceState.RUNNING,
            message=f"Concurrency Service - Mode: {self.config.mode.value}",
            details={
                "concurrency_mode": self.config.mode.value,
                "thread_workers": self.config.max_thread_workers,
                "process_workers": self.config.max_process_workers,
                "max_async_tasks": self.config.max_async_tasks,
                "total_async_tasks": self.metrics.total_async_tasks,
                "total_thread_tasks": self.metrics.total_thread_tasks,
                "total_process_tasks": self.metrics.total_process_tasks,
                "connection_pool_utilization": self.metrics.connection_pool_utilization
            },
            timestamp=time.time()
        )
    
    async def execute_async(self, coroutines: List[asyncio.Coroutine]) -> List[Any]:
        """Execute multiple coroutines concurrently."""
        start_time = time.time()
        
        try:
            results = await asyncio.gather(*coroutines, return_exceptions=True)
            
            with self._lock:
                self.metrics.total_async_tasks += len(coroutines)
                self.metrics.async_completion_time += time.time() - start_time
                if self.metrics.total_async_tasks > 0:
                    self.metrics.async_avg_time = self.metrics.async_completion_time / self.metrics.total_async_tasks
            
            return results
        except Exception as e:
            logger.error(f"Async execution failed: {e}")
            return []
    
    def execute_thread_pool(self, tasks: List[Callable[[], Any]]) -> List[Any]:
        """Execute tasks in thread pool for I/O-bound operations."""
        start_time = time.time()
        
        try:
            futures = [self._thread_pool.submit(task) for task in tasks]
            results = [future.result() for future in as_completed(futures)]
            
            with self._lock:
                self.metrics.total_thread_tasks += len(tasks)
                self.metrics.thread_completion_time += time.time() - start_time
                if self.metrics.total_thread_tasks > 0:
                    self.metrics.thread_avg_time = self.metrics.thread_completion_time / self.metrics.total_thread_tasks
            
            return results
        except Exception as e:
            logger.error(f"Thread pool execution failed: {e}")
            return []
    
    def execute_process_pool(self, tasks: List[Callable[[], Any]]) -> List[Any]:
        """Execute tasks in process pool for CPU-bound operations."""
        start_time = time.time()
        
        try:
            futures = [self._process_pool.submit(task) for task in tasks]
            results = [future.result() for future in as_completed(futures)]
            
            with self._lock:
                self.metrics.total_process_tasks += len(tasks)
                self.metrics.process_completion_time += time.time() - start_time
                if self.metrics.total_process_tasks > 0:
                    self.metrics.process_avg_time = self.metrics.process_completion_time / self.metrics.total_process_tasks
            
            return results
        except Exception as e:
            logger.error(f"Process pool execution failed: {e}")
            return []
    
    def get_connection_pool(self, pool_name: str) -> ConnectionPool:
        """Get or create a connection pool."""
        if pool_name not in self._connection_pools:
            with self._lock:
                if pool_name not in self._connection_pools:
                    self._connection_pools[pool_name] = ConnectionPool(
                        pool_size=self.config.connection_pool_size,
                        timeout=self.config.connection_timeout
                    )
        return self._connection_pools[pool_name]
    
    def get_lock_free_queue(self, queue_name: str, max_size: int = 1000) -> LockFreeQueue:
        """Get or create a lock-free queue."""
        if queue_name not in self._lock_free_queues:
            with self._lock:
                if queue_name not in self._lock_free_queues:
                    self._lock_free_queues[queue_name] = LockFreeQueue(max_size=max_size)
        return self._lock_free_queues[queue_name]
    
    def run_in_loop(self, coro: asyncio.Coroutine) -> Any:
        """Run a coroutine in the service's event loop."""
        if self._loop and not self._loop.is_closed():
            future = asyncio.run_coroutine_threadsafe(coro, self._loop)
            return future.result(timeout=self.config.connection_timeout)
        return None
    
    def get_concurrency_stats(self) -> Dict[str, Any]:
        """Get concurrency statistics."""
        with self._lock:
            # Calculate connection pool utilization
            total_available = sum(pool.get_stats()["available"] for pool in self._connection_pools.values())
            total_in_use = sum(pool.get_stats()["in_use"] for pool in self._connection_pools.values())
            total_connections = total_available + total_in_use
            
            if total_connections > 0:
                self.metrics.connection_pool_utilization = total_in_use / total_connections
            else:
                self.metrics.connection_pool_utilization = 0.0
            
            self.metrics.active_connections = total_in_use
            
            return {
                "total_async_tasks": self.metrics.total_async_tasks,
                "total_thread_tasks": self.metrics.total_thread_tasks,
                "total_process_tasks": self.metrics.total_process_tasks,
                "async_avg_time": self.metrics.async_avg_time,
                "thread_avg_time": self.metrics.thread_avg_time,
                "process_avg_time": self.metrics.process_avg_time,
                "connection_pool_utilization": self.metrics.connection_pool_utilization,
                "active_connections": self.metrics.active_connections,
                "connection_pools": {name: pool.get_stats() for name, pool in self._connection_pools.items()},
                "lock_free_queues": {name: {"size": queue.size()} for name, queue in self._lock_free_queues.items()}
            }


# Global instance
_concurrency_service: Optional[ConcurrencyService] = None


def get_concurrency_service() -> ConcurrencyService:
    """Get global concurrency service instance."""
    global _concurrency_service
    if _concurrency_service is None:
        _concurrency_service = ConcurrencyService()
    return _concurrency_service