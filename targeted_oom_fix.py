#!/usr/bin/env python
"""
Targeted OOM Fix for Session Restoration
Addresses the specific memory pressure during archived session opening
"""

import os
import sys
import psutil
import subprocess
import logging
from pathlib import Path

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("targeted_oom_fix")


class TargetedOOMFix:
    """Targeted fix for session restoration OOM"""

    def __init__(self):
        self.emergency_cleanup_done = False

    def emergency_memory_cleanup(self):
        """Emergency memory cleanup before session restoration"""
        if self.emergency_cleanup_done:
            return

        logger.info("=== EMERGENCY MEMORY CLEANUP ===")

        # 1. Kill high-memory Devin processes (>500 MB)
        self.kill_high_memory_devin_processes(threshold_mb=500)

        # 2. Clear all Python caches
        self.clear_python_caches()

        # 3. Clear temp directories
        self.clear_temp_directories()

        # 4. Force garbage collection
        import gc
        gc.collect()
        gc.collect()

        # 5. Compact memory
        try:
            import ctypes
            libc = ctypes.CDLL("libc.so.6")
            libc.malloc_trim(0)
        except:
            pass

        self.emergency_cleanup_done = True
        logger.info("Emergency cleanup completed")

    def kill_high_memory_devin_processes(self, threshold_mb=500):
        """Kill high-memory Devin processes"""
        try:
            killed = []
            for proc in psutil.process_iter(['name', 'pid', 'memory_info']):
                try:
                    if proc.info['name'] and 'devin' in proc.info['name'].lower():
                        mem_mb = proc.info['memory_info'].rss / (1024 * 1024)
                        if mem_mb > threshold_mb:
                            logger.warning(f"Killing Devin PID {proc.info['pid']} ({mem_mb:.0f} MB)")
                            proc.kill()
                            killed.append(proc.info['pid'])
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    continue

            if killed:
                logger.info(f"Killed {len(killed)} high-memory Devin processes")
            else:
                logger.info("No high-memory Devin processes found")

        except Exception as e:
            logger.error(f"Failed to kill Devin processes: {e}")

    def clear_python_caches(self):
        """Clear Python cache directories"""
        cache_patterns = [
            "__pycache__",
            ".pytest_cache",
            "*.pyc",
            ".pyc"
        ]

        for pattern in cache_patterns:
            if pattern.startswith("*"):
                # File pattern
                import glob
                for file in glob.glob(pattern, recursive=True):
                    try:
                        os.remove(file)
                        logger.info(f"Removed: {file}")
                    except:
                        pass
            else:
                # Directory pattern
                for root, dirs, files in os.walk("."):
                    if pattern in dirs:
                        cache_path = os.path.join(root, pattern)
                        try:
                            shutil.rmtree(cache_path)
                            logger.info(f"Removed cache directory: {cache_path}")
                        except:
                            pass

    def clear_temp_directories(self):
        """Clear temporary directories"""
        temp_dirs = [
            "temp_extract",
            "containers/system_core/state/cache"
        ]

        for temp_dir in temp_dirs:
            path = Path(temp_dir)
            if path.exists():
                try:
                    shutil.rmtree(path)
                    logger.info(f"Removed temp directory: {temp_dir}")
                except Exception as e:
                    logger.warning(f"Could not remove {temp_dir}: {e}")

    def monitor_memory_pressure(self):
        """Monitor current memory pressure"""
        mem = psutil.virtual_memory()
        logger.info(f"System memory: {mem.percent}% used ({mem.available / (1024**3):.2f} GB available)")

        # Check Devin memory
        devin_mem = 0
        try:
            for proc in psutil.process_iter(['name', 'memory_info']):
                try:
                    if proc.info['name'] and 'devin' in proc.info['name'].lower():
                        devin_mem += proc.info['memory_info'].rss
                except:
                    pass
            logger.info(f"Devin memory: {devin_mem / (1024**3):.2f} GB")
        except:
            pass

        return mem.percent

    def safe_session_restore_preparation(self):
        """Prepare system for safe session restoration"""
        logger.info("=== PREPARING FOR SAFE SESSION RESTORATION ===")

        # Monitor current state
        current_pressure = self.monitor_memory_pressure()

        # If memory pressure is high, do emergency cleanup
        if current_pressure > 70:
            logger.warning("High memory pressure detected - performing emergency cleanup")
            self.emergency_memory_cleanup()

        # Re-check after cleanup
        logger.info("Memory status after preparation:")
        self.monitor_memory_pressure()

        logger.info("=== PREPARATION COMPLETE ===")
        logger.info("Now you can safely attempt to open the archived session")

    def auto_cleanup_and_retry(self):
        """Automatic cleanup and retry mechanism"""
        logger.info("=== AUTO CLEANUP AND RETRY ===")

        # First attempt: emergency cleanup
        self.emergency_memory_cleanup()

        # Check if memory is now sufficient
        mem = psutil.virtual_memory()
        if mem.percent < 60:
            logger.info("Memory pressure acceptable - should be safe now")
            return True
        else:
            logger.warning("Memory pressure still high - may need system restart")
            return False


def main():
    """Main execution"""
    fixer = TargetedOOMFix()

    print("=== Targeted OOM Fix for Session Restoration ===")
    print()

    print("Current memory status:")
    fixer.monitor_memory_pressure()

    print("\nOptions:")
    print("1. Emergency memory cleanup (kill high-memory Devin, clear caches)")
    print("2. Prepare for safe session restoration")
    print("3. Auto cleanup and retry")
    print("4. Just check memory status")

    try:
        choice = input("Choose option (1-4): ")

        if choice == '1':
            fixer.emergency_memory_cleanup()
            print("\nMemory after cleanup:")
            fixer.monitor_memory_pressure()
        elif choice == '2':
            fixer.safe_session_restore_preparation()
        elif choice == '3':
            success = fixer.auto_cleanup_and_retry()
            if success:
                print("\n✅ Memory pressure reduced - safe to proceed")
            else:
                print("\n⚠️ Memory still high - consider system restart")
        elif choice == '4':
            fixer.monitor_memory_pressure()
        else:
            print("Invalid choice")

    except KeyboardInterrupt:
        print("\nOperation cancelled")
    except Exception as e:
        print(f"Error: {e}")


if __name__ == "__main__":
    import shutil  # Import here to avoid issues
    main()
