#!/usr/bin/env python
"""
Fix IDE Loading Errors (Not OOM)
Addresses the actual errors found in the error log
"""

import subprocess
import shutil
from pathlib import Path
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("fix_ide_errors")


def fix_ide_loading_errors():
    """Fix the IDE loading errors identified in the error log"""

    logger.info("=== Fixing IDE Loading Errors ===")

    # Issue 1: Missing Codeium Windsurf Pyright extension
    logger.info("1. Checking Codeium Windsurf Pyright extension...")
    ext_path = Path(r"C:\Users\prive\.devin\extensions\codeium.windsurfpyright-1.29.6-universal")
    if ext_path.exists():
        logger.info(f"Extension directory exists at {ext_path}")
        main_file = ext_path / "dist" / "extension.js"
        if not main_file.exists():
            logger.error(f"Main extension file missing: {main_file}")
            logger.info("Recommendation: Reinstall Windsurf or Codeium extension")
    else:
        logger.warning(f"Extension directory not found: {ext_path}")

    # Issue 2: Clear IDE cache
    logger.info("2. Clearing IDE cache...")
    devin_cache = Path(r"C:\Users\prive\AppData\Local\Temp\devin.exe-overflows")
    if devin_cache.exists():
        try:
            shutil.rmtree(devin_cache)
            logger.info("Cleared Devin overflow cache")
        except Exception as e:
            logger.warning(f"Could not clear cache: {e}")

    logger.info("=== Fix Complete ===")
    logger.info("Recommendations:")
    logger.info("1. Restart Windsurf IDE")
    logger.info("2. Disable Codeium extension if issues persist")
    logger.info("3. Use external terminal if terminal integration fails")
    logger.info("4. Check for Windsurf updates")


def main():
    fix_ide_loading_errors()


if __name__ == "__main__":
    main()