#!/usr/bin/env python
"""
Lightweight Session Restore for DIX VISION
Prevents OOM errors during session restoration by using minimal loading strategy
"""

import gc
import sys
import logging
import json
from pathlib import Path
from typing import Optional, Dict, Any, List
import psutil

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("lightweight_session_restore")


class LightweightSessionRestorer:
    """Lightweight session restoration to prevent OOM errors"""

    def __init__(self):
        self.process = psutil.Process()
        self.memory_limit_mb = 1000  # Conservative 1GB limit for session restore
        self.max_file_size_mb = 10    # Max file size to load in lightweight mode

    def check_system_memory(self) -> bool:
        """Check if system has sufficient memory for session restore"""
        try:
            available_mb = psutil.virtual_memory().available / 1024 / 1024
            process_mb = self.process.memory_info().rss / 1024 / 1024

            logger.info(f"System available memory: {available_mb:.2f} MB")
            logger.info(f"Process memory: {process_mb:.2f} MB")

            # Require at least 2GB available for safe session restore
            if available_mb < 2048:
                logger.warning("Insufficient system memory for full session restore")
                return False

            return True

        except Exception as e:
            logger.error(f"Memory check failed: {e}")
            return False

    def create_minimal_session_snapshot(self, session_path: str) -> Dict[str, Any]:
        """Create minimal snapshot of session with only essential data"""
        try:
            session_file = Path(session_path)
            if not session_file.exists():
                logger.warning(f"Session file not found: {session_path}")
                return {}

            file_size_mb = session_file.stat().st_size / (1024 * 1024)

            # For large files, create minimal metadata-only snapshot
            if file_size_mb > self.max_file_size_mb:
                logger.warning(f"Large session file ({file_size_mb:.2f} MB) - creating minimal snapshot")
                return {
                    "session_path": str(session_path),
                    "file_size_mb": file_size_mb,
                    "status": "deferred_loading",
                    "message": "Large session file - use selective loading",
                    "load_strategy": "on_demand"
                }

            # Load full session for smaller files
            with open(session_file, 'r', encoding='utf-8') as f:
                session_data = json.load(f)

            # Create minimal snapshot with only essential fields
            minimal_snapshot = {
                "session_id": session_data.get("session_id", "unknown"),
                "created_at": session_data.get("created_at", "unknown"),
                "session_type": session_data.get("session_type", "unknown"),
                "status": session_data.get("status", "unknown"),
                "metadata_keys": list(session_data.keys()),
                "total_keys": len(session_data),
                "source_file": str(session_path),
                "load_strategy": "full"
            }

            return minimal_snapshot

        except Exception as e:
            logger.error(f"Failed to create session snapshot: {e}")
            return {}

    def implement_selective_loading(self, session_data: Dict[str, Any], required_keys: List[str]) -> Dict[str, Any]:
        """Load only required keys from session data"""
        try:
            selective_data = {}
            for key in required_keys:
                if key in session_data:
                    selective_data[key] = session_data[key]

            logger.info(f"Selective loading: {len(selective_data)} keys loaded out of {len(session_data)} total")
            return selective_data

        except Exception as e:
            logger.error(f"Selective loading failed: {e}")
            return {}

    def paginate_large_data(self, data: Any, page_size: int = 100) -> List[Any]:
        """Paginate large data structures to reduce memory usage"""
        try:
            if isinstance(data, list):
                pages = [data[i:i + page_size] for i in range(0, len(data), page_size)]
                logger.info(f"Paginated {len(data)} items into {len(pages)} pages")
                return pages
            elif isinstance(data, dict):
                # For dictionaries, paginate keys
                keys = list(data.keys())
                pages = [keys[i:i + page_size] for i in range(0, len(keys), page_size)]
                logger.info(f"Paginated {len(data)} dict items into {len(pages)} key pages")
                return pages
            else:
                return [data]

        except Exception as e:
            logger.error(f"Pagination failed: {e}")
            return []

    def cleanup_before_restore(self) -> bool:
        """Clean up memory before session restore"""
        try:
            logger.info("Cleaning up memory before session restore...")

            # Force garbage collection
            before_mem = self.process.memory_info().rss / 1024 / 1024
            gc.collect()
            after_mem = self.process.memory_info().rss / 1024 / 1024
            freed = before_mem - after_mem

            logger.info(f"Garbage collection freed: {freed:.2f} MB")

            # Clear large caches if they exist (placeholder)
            logger.info("Clearing caches...")
            # Add specific cache clearing logic here

            return True

        except Exception as e:
            logger.error(f"Cleanup failed: {e}")
            return False

    def restore_session_with_safety(self, session_path: str, mode: str = "safe") -> Optional[Dict[str, Any]]:
        """Restore session with memory safety checks"""
        try:
            logger.info(f"Restoring session: {session_path} (mode: {mode})")

            # Check system memory first
            if not self.check_system_memory():
                logger.warning("Insufficient memory - switching to safe mode")
                mode = "safe"

            # Cleanup before restore
            if not self.cleanup_before_restore():
                logger.warning("Cleanup failed - proceeding with caution")

            # Get session info
            session_file = Path(session_path)
            file_size_mb = session_file.stat().st_size / (1024 * 1024)

            # Mode-specific restoration
            if mode == "minimal":
                logger.info("Using minimal restoration mode")
                return self.create_minimal_session_snapshot(session_path)

            elif mode == "safe" and file_size_mb > self.max_file_size_mb:
                logger.info("File too large for safe mode - using minimal snapshot")
                return self.create_minimal_session_snapshot(session_path)

            else:
                # Full restoration with monitoring
                logger.info("Performing full restoration with monitoring")
                return self.load_session_with_monitoring(session_path)

        except Exception as e:
            logger.error(f"Session restore failed: {e}")
            return None

    def load_session_with_monitoring(self, session_path: str) -> Optional[Dict[str, Any]]:
        """Load session with continuous memory monitoring"""
        try:
            # Monitor before load
            before_mem = self.process.memory_info().rss / 1024 / 1024
            logger.info(f"Memory before load: {before_mem:.2f} MB")

            # Load session
            with open(session_path, 'r', encoding='utf-8') as f:
                session_data = json.load(f)

            # Monitor after load
            after_mem = self.process.memory_info().rss / 1024 / 1024
            mem_increase = after_mem - before_mem

            logger.info(f"Memory after load: {after_mem:.2f} MB")
            logger.info(f"Memory increase: {mem_increase:.2f} MB")

            # Check for memory threshold breach
            if after_mem > self.memory_limit_mb:
                logger.warning(f"Memory limit exceeded: {after_mem:.2f} MB > {self.memory_limit_mb} MB")
                logger.warning("Consider using minimal restoration mode")

            return session_data

        except Exception as e:
            logger.error(f"Monitored session load failed: {e}")
            return None

    def get_session_restore_strategy(self, session_path: str) -> str:
        """Determine optimal restore strategy based on session characteristics"""
        try:
            session_file = Path(session_path)
            if not session_file.exists():
                return "error"

            file_size_mb = session_file.stat().st_size / (1024 * 1024)
            available_mb = psutil.virtual_memory().available / 1024 / 1024

            # Strategy decision matrix
            if file_size_mb > self.max_file_size_mb:
                return "minimal"

            elif available_mb < 3072:  # Less than 3GB available
                return "safe"

            else:
                return "full"

        except Exception as e:
            logger.error(f"Strategy determination failed: {e}")
            return "safe"  # Default to safe mode


def main():
    """Main execution for testing"""
    restorer = LightweightSessionRestorer()

    print("=== Lightweight Session Restore ===")
    print()

    # Test with session files
    session_dir = Path("containers/development/checkpoints")
    if session_dir.exists():
        session_files = list(session_dir.rglob("*.json"))
        print(f"Found {len(session_files)} session files")

        if session_files:
            # Test with first session file
            test_session = session_files[0]
            print(f"\nTesting with: {test_session.name}")

            strategy = restorer.get_session_restore_strategy(str(test_session))
            print(f"Restore strategy: {strategy}")

            result = restorer.restore_session_with_safety(str(test_session), mode=strategy)
            print(f"Restore result: {'Success' if result else 'Failed'}")

            if result:
                print(f"Session keys: {list(result.keys())}")
    else:
        print("Session directory not found")

    print("\n=== Lightweight Session Restore Complete ===")


if __name__ == "__main__":
    main()