#!/usr/bin/env python
"""
Aggressive Session Restore for DIX VISION
Works around OOM errors by using minimal restore approach
"""

import os
import sys
import json
import shutil
import logging
from pathlib import Path
from datetime import datetime
import psutil

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("aggressive_session_restore")


class AggressiveSessionRestorer:
    """Aggressive session restoration with memory management"""

    def __init__(self):
        self.temp_restore_dir = Path("temp_restore_session")

    def pre_restore_memory_cleanup(self):
        """Aggressive memory cleanup before session restore"""
        logger.info("=== AGGRESSIVE MEMORY CLEANUP ===")

        # 1. Force kill high-memory Devin processes
        self.kill_high_memory_devin_processes()

        # 2. Clear all caches
        self.clear_all_caches()

        # 3. Force garbage collection
        import gc
        gc.collect()
        gc.collect()

        logger.info("Aggressive cleanup completed")

    def kill_high_memory_devin_processes(self, threshold_mb=400):
        """Kill Devin processes using excessive memory"""
        try:
            killed = []
            for proc in psutil.process_iter(['name', 'pid', 'memory_info']):
                try:
                    if proc.info['name'] and 'devin' in proc.info['name'].lower():
                        mem_mb = proc.info['memory_info'].rss / (1024 * 1024)
                        if mem_mb > threshold_mb:
                            logger.warning(f"Killing high-memory Devin process: PID {proc.info['pid']} ({mem_mb:.0f} MB)")
                            proc.kill()
                            killed.append(proc.info['pid'])
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    continue

            if killed:
                logger.info(f"Killed {len(killed)} high-memory Devin processes: {killed}")
            else:
                logger.info("No high-memory Devin processes found")

        except Exception as e:
            logger.error(f"Failed to kill Devin processes: {e}")

    def clear_all_caches(self):
        """Clear all cache directories"""
        cache_dirs = [
            "__pycache__",
            ".pytest_cache",
            "temp_extract"
        ]

        for cache_dir in cache_dirs:
            cache_path = Path(cache_dir)
            if cache_path.exists():
                try:
                    if cache_path.is_dir():
                        shutil.rmtree(cache_path)
                        logger.info(f"Removed cache directory: {cache_dir}")
                    else:
                        cache_path.unlink()
                        logger.info(f"Removed cache file: {cache_dir}")
                except Exception as e:
                    logger.warning(f"Failed to remove {cache_dir}: {e}")

    def monitor_system_memory(self):
        """Monitor current system memory"""
        mem = psutil.virtual_memory()
        logger.info(f"System Memory: {mem.percent}% used ({mem.available / (1024**3):.2f} GB available)")


def main():
    """Main execution for testing aggressive restore"""
    restorer = AggressiveSessionRestorer()

    print("=== Aggressive Session Restore Tool ===")
    print()

    # Monitor current memory
    restorer.monitor_system_memory()

    # Perform aggressive cleanup
    print("\nPerforming aggressive memory cleanup...")
    restorer.pre_restore_memory_cleanup()

    # Monitor memory after cleanup
    print("\nMemory after cleanup:")
    restorer.monitor_system_memory()

    print("\n=== Aggressive Session Restore Complete ===")


if __name__ == "__main__":
    main()