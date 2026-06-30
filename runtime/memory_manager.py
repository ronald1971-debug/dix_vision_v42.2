"""
DIX VISION Unified Memory Manager

Centralized memory management system that consolidates all memory-related
functionality across the DIX VISION system.

Usage:
    from runtime.memory_manager import UnifiedMemoryManager, get_memory_manager
    
    memory_manager = get_memory_manager()
    memory_manager.start_monitoring()
    status = memory_manager.check_memory()
"""

from __future__ import annotations

import gc
import logging
import os
import platform
import subprocess
import sys
import threading
import time
from abc import ABC, abstractmethod
from dataclasses import dataclass
from enum import Enum
from pathlib import Path
from typing import Any, Callable, Optional

logger = logging.getLogger(__name__)


class Platform(Enum):
    """Supported platforms for memory management."""
    WINDOWS = "windows"
    LINUX = "linux"
    MACOS = "macos"
    WSL = "wsl"
    DOCKER = "docker"


@dataclass
class MemoryStatus:
    """Current memory status snapshot."""
    rss_mb: float
    vms_mb: float
    percent: float
    available_mb: float
    system_percent: float
    timestamp: float
    safe: bool


@dataclass
class MemoryLimits:
    """Memory limits for the system."""
    warning_threshold: float  # percent
    critical_threshold: float  # percent
    process_limit: float  # MB
    disk_space_warning: float  # GB


class MemoryPolicy(ABC):
    """Base class for memory policies."""
    
    @abstractmethod
    def evaluate(self, status: MemoryStatus) -> bool:
        """Evaluate if policy is violated."""
        pass
    
    @abstractmethod
    def get_action(self) -> str:
        """Get recommended action."""
        pass


class WarningThresholdPolicy(MemoryPolicy):
    """Policy for warning threshold."""
    
    def __init__(self, threshold: float = 70.0):
        self.threshold = threshold
    
    def evaluate(self, status: MemoryStatus) -> bool:
        return status.system_percent > self.threshold
    
    def get_action(self) -> str:
        return "warning"


class CriticalThresholdPolicy(MemoryPolicy):
    """Policy for critical threshold."""
    
    def __init__(self, threshold: float = 85.0):
        self.threshold = threshold
    
    def evaluate(self, status: MemoryStatus) -> bool:
        return status.system_percent > self.threshold
    
    def get_action(self) -> str:
        return "critical"


class ProcessLimitPolicy(MemoryPolicy):
    """Policy for process memory limit."""
    
    def __init__(self, limit_mb: float = 1024.0):
        self.limit_mb = limit_mb
    
    def evaluate(self, status: MemoryStatus) -> bool:
        return status.rss_mb > self.limit_mb
    
    def get_action(self) -> str:
        return "terminate"


class PlatformMemoryAdapter(ABC):
    """Abstract base class for platform-specific memory operations."""
    
    @abstractmethod
    def detect_platform(self) -> Platform:
        """Detect the current platform."""
        pass
    
    @abstractmethod
    def get_memory_limits(self) -> MemoryLimits:
        """Get memory limits for the platform."""
        pass
    
    @abstractmethod
    def optimize_memory(self) -> bool:
        """Optimize memory for the platform."""
        pass


class WindowsMemoryAdapter(PlatformMemoryAdapter):
    """Windows-specific memory operations."""
    
    def detect_platform(self) -> Platform:
        return Platform.WINDOWS
    
    def get_memory_limits(self) -> MemoryLimits:
        return MemoryLimits(
            warning_threshold=70.0,
            critical_threshold=85.0,
            process_limit=1024.0,
            disk_space_warning=5.0
        )
    
    def optimize_memory(self) -> bool:
        try:
            # Empty working sets for Windows processes
            import ctypes
            kernel32 = ctypes.windll.kernel32
            process = kernel32.GetCurrentProcess()
            kernel32.SetProcessWorkingSetSize(process, -1, -1)
            logger.info("Windows memory optimization completed")
            return True
        except Exception as e:
            logger.warning(f"Windows memory optimization failed: {e}")
            return False


class LinuxMemoryAdapter(PlatformMemoryAdapter):
    """Linux-specific memory operations."""
    
    def detect_platform(self) -> Platform:
        if "microsoft" in platform.uname().release.lower():
            return Platform.WSL
        return Platform.LINUX
    
    def get_memory_limits(self) -> MemoryLimits:
        return MemoryLimits(
            warning_threshold=70.0,
            critical_threshold=85.0,
            process_limit=1024.0,
            disk_space_warning=5.0
        )
    
    def optimize_memory(self) -> bool:
        try:
            # Call malloc_trim for Linux
            import ctypes
            libc = ctypes.CDLL("libc.so.6")
            libc.malloc_trim(0)
            logger.info("Linux memory optimization completed")
            return True
        except Exception as e:
            logger.warning(f"Linux memory optimization failed: {e}")
            return False


class WSLMemoryAdapter(PlatformMemoryAdapter):
    """WSL-specific memory operations."""
    
    def detect_platform(self) -> Platform:
        return Platform.WSL
    
    def get_memory_limits(self) -> MemoryLimits:
        return MemoryLimits(
            warning_threshold=70.0,
            critical_threshold=85.0,
            process_limit=1024.0,
            disk_space_warning=5.0
        )
    
    def optimize_memory(self) -> bool:
        try:
            # WSL-specific optimization
            # Update .wslconfig if needed
            wsl_config = Path.home() / ".wslconfig"
            if not wsl_config.exists():
                config_content = "[wsl2]\nmemory=4GB\nprocessors=4\nswap=2GB\n"
                wsl_config.write_text(config_content)
                logger.info("Created .wslconfig with memory limits")
            return True
        except Exception as e:
            logger.warning(f"WSL memory optimization failed: {e}")
            return False


class MemoryMonitor:
    """Unified memory monitoring system."""
    
    def __init__(self):
        try:
            import psutil
            self.process = psutil.Process()
            self.psutil_available = True
        except ImportError:
            logger.warning("psutil not available, memory monitoring limited")
            self.process = None
            self.psutil_available = False
        
        self.baseline_memory = None
        self.peak_memory = 0
        self.samples = []
        self.monitoring = False
        self._lock = threading.Lock()
    
    def start_monitoring(self) -> None:
        """Start memory monitoring - establish baseline."""
        with self._lock:
            if not self.psutil_available:
                logger.warning("Cannot start monitoring without psutil")
                return
            
            gc.collect()
            self.baseline_memory = self._get_current_memory()
            self.peak_memory = self.baseline_memory
            self.monitoring = True
            logger.info(f"Memory monitoring started. Baseline: {self.baseline_memory:.2f} MB")
    
    def stop_monitoring(self) -> None:
        """Stop memory monitoring."""
        with self._lock:
            self.monitoring = False
            logger.info("Memory monitoring stopped")
    
    def check_memory(self, label: str = "Current") -> MemoryStatus:
        """Check current memory usage and log if significant change."""
        if not self.psutil_available:
            return MemoryStatus(0, 0, 0, 0, 0, time.time(), False)
        
        with self._lock:
            if self.baseline_memory is None:
                self.start_monitoring()
            
            current_memory = self._get_current_memory()
            memory_increase = current_memory - self.baseline_memory
            
            if current_memory > self.peak_memory:
                self.peak_memory = current_memory
            
            logger.info(f"{label} Memory: {current_memory:.2f} MB (Increase: {memory_increase:+.2f} MB, Peak: {self.peak_memory:.2f} MB)")
            
            # Warn if memory increase is significant (>100MB)
            if memory_increase > 100:
                logger.warning(f"Significant memory increase detected: {memory_increase:.2f} MB")
            
            status = self._get_memory_status()
            self.samples.append(status)
            
            return status
    
    def detect_leak(self, threshold_mb: float = 200) -> bool:
        """Check for potential memory leak based on threshold."""
        if not self.psutil_available:
            return False
        
        current_memory = self._get_current_memory()
        memory_increase = current_memory - self.baseline_memory
        
        if memory_increase > threshold_mb:
            logger.error(f"Potential memory leak detected! Memory increase: {memory_increase:.2f} MB")
            return True
        return False
    
    def force_garbage_collection(self) -> float:
        """Force garbage collection and report memory change."""
        if not self.psutil_available:
            return 0.0
        
        before = self._get_current_memory()
        gc.collect()
        gc.collect()  # Run twice for thorough cleanup
        after = self._get_current_memory()
        freed = before - after
        logger.info(f"Garbage collection freed {freed:.2f} MB")
        return freed
    
    def _get_current_memory(self) -> float:
        """Get current process memory in MB."""
        if self.process:
            return self.process.memory_info().rss / 1024 / 1024
        return 0.0
    
    def _get_memory_status(self) -> MemoryStatus:
        """Get comprehensive memory status."""
        if not self.psutil_available:
            return MemoryStatus(0, 0, 0, 0, 0, time.time(), False)
        
        mem_info = self.process.memory_info()
        rss_mb = mem_info.rss / 1024 / 1024
        vms_mb = mem_info.vms / 1024 / 1024
        percent = self.process.memory_percent()
        
        import psutil
        available_mb = psutil.virtual_memory().available / 1024 / 1024
        system_percent = psutil.virtual_memory().percent
        
        safe = system_percent < 70 and rss_mb < 1024
        
        return MemoryStatus(
            rss_mb=rss_mb,
            vms_mb=vms_mb,
            percent=percent,
            available_mb=available_mb,
            system_percent=system_percent,
            timestamp=time.time(),
            safe=safe
        )


class OOMHandler:
    """Out-of-memory handling system."""
    
    def __init__(self):
        self.emergency_procedures = []
        self.cleanup_handlers = []
        self._register_default_procedures()
    
    def _register_default_procedures(self):
        """Register default emergency procedures."""
        self.emergency_procedures.append(self._force_garbage_collection)
        self.emergency_procedures.append(self._clear_python_caches)
        self.emergency_procedures.append(self._optimize_platform_memory)
    
    def register_emergency_procedure(self, procedure: Callable[[], bool]) -> None:
        """Register a custom emergency procedure."""
        self.emergency_procedures.append(procedure)
    
    def register_cleanup_handler(self, handler: Callable[[], bool]) -> None:
        """Register a cleanup handler."""
        self.cleanup_handlers.append(handler)
    
    def detect_oom(self, status: MemoryStatus) -> bool:
        """Detect if system is in OOM condition."""
        return not status.safe or status.system_percent > 85
    
    def handle_oom(self) -> dict[str, Any]:
        """Handle OOM condition with emergency procedures."""
        logger.warning("OOM condition detected, executing emergency procedures")
        
        results = []
        for procedure in self.emergency_procedures:
            try:
                result = procedure()
                results.append({"procedure": procedure.__name__, "success": result})
            except Exception as e:
                logger.error(f"Emergency procedure failed: {e}")
                results.append({"procedure": procedure.__name__, "success": False, "error": str(e)})
        
        # Run cleanup handlers
        for handler in self.cleanup_handlers:
            try:
                handler()
            except Exception as e:
                logger.error(f"Cleanup handler failed: {e}")
        
        return {"procedures_executed": len(results), "results": results}
    
    def _force_garbage_collection(self) -> bool:
        """Force garbage collection."""
        try:
            gc.collect()
            gc.collect()
            logger.info("Emergency garbage collection completed")
            return True
        except Exception as e:
            logger.error(f"Emergency garbage collection failed: {e}")
            return False
    
    def _clear_python_caches(self) -> bool:
        """Clear Python internal caches."""
        try:
            if hasattr(sys, '_clear_type_cache'):
                sys._clear_type_cache()
            logger.info("Python cache clearing completed")
            return True
        except Exception as e:
            logger.error(f"Python cache clearing failed: {e}")
            return False
    
    def _optimize_platform_memory(self) -> bool:
        """Optimize platform-specific memory."""
        try:
            adapter = self._get_platform_adapter()
            return adapter.optimize_memory()
        except Exception as e:
            logger.error(f"Platform memory optimization failed: {e}")
            return False
    
    def _get_platform_adapter(self) -> PlatformMemoryAdapter:
        """Get appropriate platform adapter."""
        system = platform.system().lower()
        if system == "windows":
            return WindowsMemoryAdapter()
        elif system == "linux":
            return LinuxMemoryAdapter()
        else:
            return LinuxMemoryAdapter()  # Fallback


class UnifiedMemoryManager:
    """Centralized memory management for DIX VISION system."""
    
    def __init__(self):
        self.monitor = MemoryMonitor()
        self.policies = []
        self.oom_handler = OOMHandler()
        self.platform_adapter = self._get_platform_adapter()
        self.limits = self.platform_adapter.get_memory_limits()
        self._register_default_policies()
        self.monitoring_active = False
        self._monitor_thread = None
        self._stop_event = threading.Event()
    
    def _get_platform_adapter(self) -> PlatformMemoryAdapter:
        """Get appropriate platform adapter."""
        system = platform.system().lower()
        if system == "windows":
            return WindowsMemoryAdapter()
        elif system == "linux":
            return LinuxMemoryAdapter()
        else:
            return LinuxMemoryAdapter()  # Fallback
    
    def _register_default_policies(self):
        """Register default memory policies."""
        self.policies.append(WarningThresholdPolicy(self.limits.warning_threshold))
        self.policies.append(CriticalThresholdPolicy(self.limits.critical_threshold))
        self.policies.append(ProcessLimitPolicy(self.limits.process_limit))
    
    def register_policy(self, policy: MemoryPolicy) -> None:
        """Register a custom memory policy."""
        self.policies.append(policy)
    
    def register_emergency_handler(self, handler: Callable[[], bool]) -> None:
        """Register an emergency handler."""
        self.oom_handler.register_emergency_procedure(handler)
    
    def start_monitoring(self) -> None:
        """Start continuous memory monitoring."""
        if self.monitoring_active:
            logger.warning("Memory monitoring already active")
            return
        
        self.monitor.start_monitoring()
        self.monitoring_active = True
        self._stop_event.clear()
        
        # Start monitoring thread
        self._monitor_thread = threading.Thread(target=self._monitor_loop, daemon=True)
        self._monitor_thread.start()
        
        logger.info("Unified memory manager started monitoring")
    
    def stop_monitoring(self) -> None:
        """Stop continuous memory monitoring."""
        if not self.monitoring_active:
            return
        
        self._stop_event.set()
        if self._monitor_thread:
            self._monitor_thread.join(timeout=5)
        
        self.monitor.stop_monitoring()
        self.monitoring_active = False
        
        logger.info("Unified memory manager stopped monitoring")
    
    def _monitor_loop(self) -> None:
        """Continuous monitoring loop."""
        while not self._stop_event.is_set():
            try:
                status = self.monitor.check_memory()
                self._evaluate_policies(status)
                
                if self.oom_handler.detect_oom(status):
                    self.oom_handler.handle_oom()
                
                self._stop_event.wait(5)  # Check every 5 seconds
            except Exception as e:
                logger.error(f"Monitoring loop error: {e}")
                self._stop_event.wait(10)
    
    def _evaluate_policies(self, status: MemoryStatus) -> None:
        """Evaluate all registered policies."""
        for policy in self.policies:
            if policy.evaluate(status):
                action = policy.get_action()
                logger.warning(f"Memory policy violated: {action}")
                
                if action == "critical":
                    self.oom_handler.handle_oom()
    
    def get_memory_status(self) -> MemoryStatus:
        """Get current memory status."""
        return self.monitor.check_memory()
    
    def force_cleanup(self) -> float:
        """Force memory cleanup."""
        return self.monitor.force_garbage_collection()
    
    def optimize_memory(self) -> bool:
        """Optimize memory for current platform."""
        return self.platform_adapter.optimize_memory()
    
    def get_summary(self) -> dict[str, Any]:
        """Get comprehensive memory summary."""
        status = self.get_memory_status()
        return {
            "current_memory_mb": status.rss_mb,
            "peak_memory_mb": self.monitor.peak_memory,
            "baseline_memory_mb": self.monitor.baseline_memory,
            "system_percent": status.system_percent,
            "process_percent": status.percent,
            "available_mb": status.available_mb,
            "safe": status.safe,
            "monitoring_active": self.monitoring_active,
            "platform": self.platform_adapter.detect_platform().value,
            "limits": {
                "warning_threshold": self.limits.warning_threshold,
                "critical_threshold": self.limits.critical_threshold,
                "process_limit": self.limits.process_limit,
            }
        }


# Global instance
_memory_manager: Optional[UnifiedMemoryManager] = None
_lock = threading.Lock()


def get_memory_manager() -> UnifiedMemoryManager:
    """Get global memory manager instance."""
    global _memory_manager
    if _memory_manager is None:
        with _lock:
            if _memory_manager is None:
                _memory_manager = UnifiedMemoryManager()
    return _memory_manager


def start_memory_monitoring() -> None:
    """Start memory monitoring (convenience function)."""
    get_memory_manager().start_monitoring()


def stop_memory_monitoring() -> None:
    """Stop memory monitoring (convenience function)."""
    get_memory_manager().stop_monitoring()


def get_memory_status() -> MemoryStatus:
    """Get current memory status (convenience function)."""
    return get_memory_manager().get_memory_status()


def force_memory_cleanup() -> float:
    """Force memory cleanup (convenience function)."""
    return get_memory_manager().force_cleanup()


__all__ = [
    "UnifiedMemoryManager",
    "MemoryMonitor",
    "OOMHandler",
    "MemoryStatus",
    "MemoryLimits",
    "Platform",
    "get_memory_manager",
    "start_memory_monitoring",
    "stop_memory_monitoring",
    "get_memory_status",
    "force_memory_cleanup",
]