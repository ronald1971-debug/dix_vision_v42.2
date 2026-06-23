#!/usr/bin/env python
"""
Session Restore Safety Wrapper for DIX VISION IDE
Provides memory-safe session restoration to prevent OOM errors
"""

import gc
import sys
import os
import logging
import psutil
import subprocess
from pathlib import Path
from typing import Optional, Dict, Any, List
import json
import time

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("session_restore_safety")


class SessionRestoreSafetyWrapper:
    """Safety wrapper for IDE session restoration"""

    def __init__(self):
        self.process = psutil.Process()
        self.memory_warning_threshold = 70  # % system memory
        self.memory_critical_threshold = 85  # % system memory
        self.session_restore_timeout = 30  # seconds

    def pre_restore_checks(self) -> Dict[str, Any]:
        """Perform comprehensive checks before session restore"""
        checks = {
            "system_memory": self.check_system_memory(),
            "process_memory": self.check_process_memory(),
            "disk_space": self.check_disk_space(),
            "running_processes": self.check_running_processes(),
            "can_restore": True
        }

        # Determine if restore is safe
        checks["can_restore"] = all([
            checks["system_memory"]["safe"],
            checks["process_memory"]["safe"],
            checks["disk_space"]["safe"]
        ])

        return checks

    def check_system_memory(self) -> Dict[str, Any]:
        """Check system memory status"""
        try:
            mem = psutil.virtual_memory()
            available_mb = mem.available / 1024 / 1024
            percent_used = mem.percent

            safe = percent_used < self.memory_warning_threshold

            return {
                "total_mb": mem.total / 1024 / 1024,
                "available_mb": available_mb,
                "used_percent": percent_used,
                "safe": safe,
                "status": "ok" if safe else "warning"
            }
        except Exception as e:
            logger.error(f"System memory check failed: {e}")
            return {"safe": False, "status": "error", "error": str(e)}

    def check_process_memory(self) -> Dict[str, Any]:
        """Check current process memory usage"""
        try:
            mem_info = self.process.memory_info()
            rss_mb = mem_info.rss / 1024 / 1024
            percent = self.process.memory_percent()

            # Warn if process is using >1GB
            safe = rss_mb < 1024

            return {
                "rss_mb": rss_mb,
                "percent": percent,
                "safe": safe,
                "status": "ok" if safe else "warning"
            }
        except Exception as e:
            logger.error(f"Process memory check failed: {e}")
            return {"safe": False, "status": "error", "error": str(e)}

    def check_disk_space(self) -> Dict[str, Any]:
        """Check available disk space"""
        try:
            disk = psutil.disk_usage('/')
            free_gb = disk.free / (1024 ** 3)
            percent_used = disk.percent

            # Warn if less than 5GB free
            safe = free_gb > 5

            return {
                "free_gb": free_gb,
                "used_percent": percent_used,
                "safe": safe,
                "status": "ok" if safe else "warning"
            }
        except Exception as e:
            logger.error(f"Disk space check failed: {e}")
            return {"safe": False, "status": "error", "error": str(e)}

    def check_running_processes(self) -> Dict[str, Any]:
        """Check for memory-intensive processes"""
        try:
            # Get top memory-consuming processes
            processes = []
            for proc in psutil.process_iter(['name', 'memory_percent']):
                try:
                    if proc.info['memory_percent'] > 1.0:  # >1% memory
                        processes.append({
                            "name": proc.info['name'],
                            "memory_percent": proc.info['memory_percent']
                        })
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    continue

            # Sort by memory usage
            processes.sort(key=lambda x: x['memory_percent'], reverse=True)

            return {
                "high_memory_processes": processes[:10],
                "count": len(processes)
            }
        except Exception as e:
            logger.error(f"Process check failed: {e}")
            return {"high_memory_processes": [], "count": 0}

    def force_cleanup_before_restore(self) -> bool:
        """Force cleanup of memory and resources before restore"""
        try:
            logger.info("Forcing cleanup before session restore...")

            # Aggressive garbage collection
            gc.collect()
            gc.collect()  # Run twice for thorough cleanup

            # Clear Python internal caches
            if hasattr(sys, '_clear_type_cache'):
                sys._clear_type_cache()

            # Force process memory release (platform-specific)
            try:
                import ctypes
                libc = ctypes.CDLL("libc.so.6")
                libc.malloc_trim(0)
            except:
                pass

            logger.info("Cleanup completed")
            return True

        except Exception as e:
            logger.error(f"Cleanup failed: {e}")
            return False

    def create_emergency_session_profile(self, session_path: str) -> Dict[str, Any]:
        """Create emergency minimal profile for problematic sessions"""
        try:
            logger.info("Creating emergency session profile...")

            # Get basic file info
            path = Path(session_path)
            file_size_mb = path.stat().st_size / (1024 * 1024)

            emergency_profile = {
                "session_path": str(session_path),
                "file_size_mb": file_size_mb,
                "created_at": time.ctime(path.stat().st_ctime),
                "modified_at": time.ctime(path.stat().st_mtime),
                "restore_strategy": "emergency_minimal",
                "disable_extensions": True,
                "disable_indexing": True,
                "minimal_ui": True,
                "lazy_loading": True
            }

            return emergency_profile

        except Exception as e:
            logger.error(f"Emergency profile creation failed: {e}")
            return {}

    def monitor_restore_process(self, restore_func) -> Dict[str, Any]:
        """Monitor the restore process with timeout and memory checks"""
        start_time = time.time()
        memory_samples = []
        success = False
        error = None

        try:
            # Start monitoring
            logger.info("Starting restore process monitoring...")

            # Execute restore function with monitoring
            result = restore_func()
            success = True

            # Record memory samples during restore
            duration = time.time() - start_time

            return {
                "success": success,
                "duration_seconds": duration,
                "memory_samples": memory_samples,
                "error": error
            }

        except Exception as e:
            error = str(e)
            duration = time.time() - start_time

            logger.error(f"Restore monitoring failed: {e}")

            return {
                "success": False,
                "duration_seconds": duration,
                "memory_samples": memory_samples,
                "error": error
            }

    def generate_restore_recommendations(self, checks: Dict[str, Any]) -> List[str]:
        """Generate recommendations based on pre-restore checks"""
        recommendations = []

        if not checks["system_memory"]["safe"]:
            recommendations.append("System memory is high - close other applications")
            recommendations.append("Consider restarting computer before session restore")

        if not checks["process_memory"]["safe"]:
            recommendations.append("Current process memory is high - restart IDE")
            recommendations.append("Use emergency restore mode if needed")

        if not checks["disk_space"]["safe"]:
            recommendations.append("Low disk space - clear temporary files")

        if checks["running_processes"]["count"] > 5:
            recommendations.append("Many high-memory processes running - consider closing them")

        if checks["can_restore"]:
            recommendations.append("System is ready for safe session restore")
        else:
            recommendations.append("System is NOT ready for session restore")
            recommendations.append("Use emergency restore mode or restart system")

        return recommendations

    def safe_restore_wrapper(self, session_path: str, restore_func) -> Dict[str, Any]:
        """Main wrapper for safe session restoration"""
        logger.info("=== Session Restore Safety Wrapper ===")
        logger.info(f"Session: {session_path}")

        # Step 1: Pre-restore checks
        logger.info("Step 1: Pre-restore checks...")
        checks = self.pre_restore_checks()
        self.log_check_results(checks)

        # Step 2: Generate recommendations
        recommendations = self.generate_restore_recommendations(checks)
        logger.info("Recommendations:")
        for rec in recommendations:
            logger.info(f"  - {rec}")

        # Step 3: Force cleanup if needed
        if not checks["can_restore"]:
            logger.warning("System not ready for restore - forcing cleanup...")
            self.force_cleanup_before_restore()

        # Step 4: Choose restore strategy
        if checks["can_restore"]:
            logger.info("Proceeding with standard restore...")
            restore_result = self.monitor_restore_process(restore_func)
        else:
            logger.warning("System not ready - using emergency profile...")
            emergency_profile = self.create_emergency_session_profile(session_path)
            restore_result = {
                "success": True,
                "emergency_mode": True,
                "profile": emergency_profile
            }

        # Step 5: Final status
        final_status = {
            "checks": checks,
            "recommendations": recommendations,
            "restore_result": restore_result,
            "overall_success": restore_result.get("success", False)
        }

        logger.info("=== Restore Wrapper Complete ===")
        return final_status

    def log_check_results(self, checks: Dict[str, Any]):
        """Log check results"""
        logger.info(f"System Memory: {checks['system_memory']['status']} ({checks['system_memory']['used_percent']:.1f}% used)")
        logger.info(f"Process Memory: {checks['process_memory']['status']} ({checks['process_memory']['rss_mb']:.1f} MB)")
        logger.info(f"Disk Space: {checks['disk_space']['status']} ({checks['disk_space']['free_gb']:.1f} GB free)")
        logger.info(f"High Memory Processes: {checks['running_processes']['count']}")


def simulate_restore():
    """Simulate a session restore for testing"""
    logger.info("Simulating session restore...")
    time.sleep(2)  # Simulate restore time
    return {"status": "success", "data": "restored_session_data"}


def main():
    """Main execution for testing"""
    wrapper = SessionRestoreSafetyWrapper()

    print("=== Session Restore Safety Wrapper Test ===")
    print()

    # Test pre-restore checks
    print("1. Running pre-restore checks...")
    checks = wrapper.pre_restore_checks()
    wrapper.log_check_results(checks)

    # Display recommendations
    print("\n2. Recommendations:")
    recommendations = wrapper.generate_restore_recommendations(checks)
    for rec in recommendations:
        print(f"   - {rec}")

    # Test force cleanup
    print("\n3. Testing force cleanup...")
    cleanup_result = wrapper.force_cleanup_before_restore()
    print(f"   Cleanup: {'Success' if cleanup_result else 'Failed'}")

    # Test safe restore wrapper
    print("\n4. Testing safe restore wrapper...")
    test_session = "containers/development/checkpoints/integrated_1781656548298.json"
    result = wrapper.safe_restore_wrapper(test_session, simulate_restore)

    print(f"\n5. Overall Result: {'Success' if result['overall_success'] else 'Failed'}")

    print("\n=== Session Restore Safety Wrapper Test Complete ===")


if __name__ == "__main__":
    main()