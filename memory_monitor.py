#!/usr/bin/env python
"""
Memory Monitor for DIX VISION
Provides memory profiling and leak detection utilities
"""

import gc
import psutil
import tracemalloc
from functools import wraps
from typing import Callable, Any
import logging

logger = logging.getLogger(__name__)


class MemoryMonitor:
    """Monitor memory usage and detect potential leaks"""
    
    def __init__(self):
        self.process = psutil.Process()
        self.baseline_memory = None
        self.peak_memory = 0
        
    def start_monitoring(self):
        """Start memory monitoring - establish baseline"""
        gc.collect()  # Force garbage collection
        self.baseline_memory = self.process.memory_info().rss / 1024 / 1024  # MB
        self.peak_memory = self.baseline_memory
        logger.info(f"Memory monitoring started. Baseline: {self.baseline_memory:.2f} MB")
        
    def check_memory(self, label: str = "Current"):
        """Check current memory usage and log if significant change"""
        if self.baseline_memory is None:
            self.start_monitoring()
            
        current_memory = self.process.memory_info().rss / 1024 / 1024  # MB
        memory_increase = current_memory - self.baseline_memory
        
        if current_memory > self.peak_memory:
            self.peak_memory = current_memory
            
        logger.info(f"{label} Memory: {current_memory:.2f} MB (Increase: {memory_increase:+.2f} MB, Peak: {self.peak_memory:.2f} MB)")
        
        # Warn if memory increase is significant (>100MB)
        if memory_increase > 100:
            logger.warning(f"Significant memory increase detected: {memory_increase:.2f} MB")
            
        return current_memory
    
    def detect_leak(self, threshold_mb: float = 200):
        """Check for potential memory leak based on threshold"""
        current_memory = self.process.memory_info().rss / 1024 / 1024  # MB
        memory_increase = current_memory - self.baseline_memory
        
        if memory_increase > threshold_mb:
            logger.error(f"Potential memory leak detected! Memory increase: {memory_increase:.2f} MB")
            return True
        return False
    
    def force_garbage_collection(self):
        """Force garbage collection and report memory change"""
        before = self.process.memory_info().rss / 1024 / 1024
        gc.collect()
        after = self.process.memory_info().rss / 1024 / 1024
        freed = before - after
        logger.info(f"Garbage collection freed {freed:.2f} MB")
        return freed


def profile_memory(func: Callable) -> Callable:
    """Decorator to profile memory usage of a function"""
    @wraps(func)
    def wrapper(*args, **kwargs) -> Any:
        monitor = MemoryMonitor()
        monitor.start_monitoring()
        
        # Start tracemalloc for detailed tracking
        tracemalloc.start()
        
        try:
            result = func(*args, **kwargs)
            
            # Get memory statistics
            monitor.check_memory(f"After {func.__name__}")
            current, peak = tracemalloc.get_traced_memory()
            
            logger.info(f"Function {func.__name__} memory usage:")
            logger.info(f"  Current: {current / 1024 / 1024:.2f} MB")
            logger.info(f"  Peak: {peak / 1024 / 1024:.2f} MB")
            
            return result
            
        finally:
            tracemalloc.stop()
            
    return wrapper


def get_memory_summary():
    """Get comprehensive memory usage summary"""
    process = psutil.Process()
    mem_info = process.memory_info()
    
    summary = {
        'rss_mb': mem_info.rss / 1024 / 1024,
        'vms_mb': mem_info.vms / 1024 / 1024,
        'percent': process.memory_percent(),
        'available_mb': psutil.virtual_memory().available / 1024 / 1024,
        'system_percent': psutil.virtual_memory().percent
    }
    
    return summary


def print_memory_summary():
    """Print formatted memory summary"""
    summary = get_memory_summary()
    
    print("\n=== Memory Usage Summary ===")
    print(f"Process RSS Memory: {summary['rss_mb']:.2f} MB")
    print(f"Process VMS Memory: {summary['vms_mb']:.2f} MB")
    print(f"Process Memory %: {summary['percent']:.2f}%")
    print(f"System Available: {summary['available_mb']:.2f} MB")
    print(f"System Memory %: {summary['system_percent']:.2f}%")
    print("=========================\n")


if __name__ == "__main__":
    # Test the memory monitor
    print_memory_summary()
    
    monitor = MemoryMonitor()
    monitor.start_monitoring()
    
    # Simulate some memory usage
    data = []
    for i in range(100000):
        data.append([0] * 100)
    
    monitor.check_memory("After allocation")
    monitor.force_garbage_collection()
    
    print_memory_summary()