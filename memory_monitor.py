#!/usr/bin/env python
"""
Memory Monitor for DIX VISION
Provides memory profiling and leak detection utilities

This module now uses the unified memory manager for consistency.
"""

import logging

logger = logging.getLogger(__name__)

# Use unified memory manager
try:
    from memory_manager import (
        get_memory_manager,
        get_memory_status,
        force_memory_cleanup,
        MemoryStatus
    )
    UNIFIED_MEMORY_AVAILABLE = True
except ImportError:
    UNIFIED_MEMORY_AVAILABLE = False
    logger.warning("Unified memory manager not available, using fallback")


class MemoryMonitor:
    """Monitor memory usage and detect potential leaks"""
    
    def __init__(self):
        if UNIFIED_MEMORY_AVAILABLE:
            self.memory_manager = get_memory_manager()
        else:
            self.memory_manager = None
            logger.warning("Using fallback memory monitoring")
        
    def start_monitoring(self):
        """Start memory monitoring - establish baseline"""
        if self.memory_manager:
            self.memory_manager.start_monitoring()
        else:
            logger.warning("Memory monitoring not available without unified manager")
        
    def check_memory(self, label: str = "Current"):
        """Check current memory usage and log if significant change"""
        if self.memory_manager:
            status = self.memory_manager.get_memory_status()
            logger.info(f"{label} Memory: {status.rss_mb:.2f} MB (System: {status.system_percent:.1f}%)")
            return status.rss_mb
        else:
            logger.warning("Memory check not available without unified manager")
            return 0
    
    def detect_leak(self, threshold_mb: float = 200):
        """Check for potential memory leak based on threshold"""
        if self.memory_manager:
            status = self.memory_manager.get_memory_status()
            # Simple leak detection based on current memory
            if status.rss_mb > threshold_mb:
                logger.error(f"High memory usage detected: {status.rss_mb:.2f} MB")
                return True
        return False
    
    def force_garbage_collection(self):
        """Force garbage collection and report memory change"""
        if UNIFIED_MEMORY_AVAILABLE:
            return force_memory_cleanup()
        else:
            import gc
            gc.collect()
            logger.info("Fallback garbage collection completed")
            return 0


def profile_memory(func):
    """Decorator to profile memory usage of a function"""
    def wrapper(*args, **kwargs):
        monitor = MemoryMonitor()
        monitor.start_monitoring()
        
        try:
            result = func(*args, **kwargs)
            monitor.check_memory(f"After {func.__name__}")
            return result
        finally:
            pass
            
    return wrapper


def get_memory_summary():
    """Get comprehensive memory usage summary"""
    if UNIFIED_MEMORY_AVAILABLE:
        status = get_memory_status()
        return {
            'rss_mb': status.rss_mb,
            'vms_mb': status.vms_mb,
            'percent': status.percent,
            'available_mb': status.available_mb,
            'system_percent': status.system_percent
        }
    else:
        logger.warning("Memory summary not available without unified manager")
        return {
            'rss_mb': 0,
            'vms_mb': 0,
            'percent': 0,
            'available_mb': 0,
            'system_percent': 0
        }


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