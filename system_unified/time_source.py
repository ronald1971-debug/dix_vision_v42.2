"""
System Unified Time Source - Time Management Infrastructure
Provides time authority and source management
NO LAZY LOADING - All components load directly
"""

import time
import asyncio
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta

class TimeSource:
    """Time source for synchronized time management"""
    
    def __init__(self):
        self._offset_ns = 0
        self._synchronized = False
        
    def get_time_ns(self) -> int:
        """Get current time in nanoseconds"""
        return time.perf_counter_ns() + self._offset_ns
    
    def get_time_s(self) -> float:
        """Get current time in seconds"""
        return time.time()
    
    def now(self) -> datetime:
        """Get current datetime"""
        return datetime.now()
    
    def synchronize(self, reference_time_ns: int):
        """Synchronize with reference time"""
        current_time = time.perf_counter_ns()
        self._offset_ns = reference_time_ns - current_time
        self._synchronized = True
    
    def set_offset(self, offset_ns: int):
        """Set time offset"""
        self._offset_ns = offset_ns

# Global instance
_time_source = None

def get_time_source() -> TimeSource:
    """Get global time source instance"""
    global _time_source
    if _time_source is None:
        _time_source = TimeSource()
    return _time_source

def get_current_time_ns() -> int:
    """Get current time in nanoseconds"""
    return get_time_source().get_time_ns()

def get_current_time_s() -> float:
    """Get current time in seconds"""
    return get_time_source().get_time_s()

def now() -> datetime:
    """Get current datetime"""
    return get_time_source().now()

# Export now as a module-level function
def __getattr__(name):
    """Allow import of 'now' from this module"""
    if name == 'now':
        return now
    raise AttributeError(f"module '{__name__}' has no attribute '{name}'")

__all__ = [
    'TimeSource',
    'get_time_source',
    'get_current_time_ns',
    'get_current_time_s'
]