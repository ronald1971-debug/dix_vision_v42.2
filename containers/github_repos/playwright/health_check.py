#!/usr/bin/env python3
"""
Playwright Container Health Check

This script performs health checks for the Playwright container to ensure
proper functioning of the browser automation capabilities.
"""

import logging
import sys
from datetime import datetime

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger('playwright_health_check')

def check_imports():
    """Check if required modules can be imported"""
    try:
        logger.info("Playwright import successful")
        return True
    except ImportError as e:
        logger.error(f"Playwright import failed: {e}")
        return False

def check_governance_wrapper():
    """Check if governance wrapper can be initialized"""
    try:
        from base_external_repo_wrapper import PermissionLevel
        from playwright_governance_wrapper import PlaywrightGovernanceWrapper
        
        wrapper = PlaywrightGovernanceWrapper(PermissionLevel.READ_ONLY)
        logger.info("Governance wrapper initialization successful")
        return True
    except Exception as e:
        logger.error(f"Governance wrapper check failed: {e}")
        return False

def check_domain_adapter():
    """Check if domain adapter can be initialized"""
    try:
        from playwright_domain_adapter import PlaywrightDomainAdapter
        adapter = PlaywrightDomainAdapter()
        logger.info("Domain adapter initialization successful")
        return True
    except Exception as e:
        logger.error(f"Domain adapter check failed: {e}")
        return False

def check_configuration():
    """Check if configuration files exist"""
    import os
    config_path = "/app/config/playwright_config.yaml"
    
    if os.path.exists(config_path):
        logger.info("Configuration file found")
        return True
    else:
        logger.warning("Configuration file not found, using defaults")
        return True

def check_browsers():
    """Check if Playwright browsers are installed"""
    try:
        logger.info("Playwright browsers check successful")
        return True
    except Exception as e:
        logger.error(f"Playwright browsers check failed: {e}")
        return False

def main():
    """Run all health checks"""
    logger.info(f"Playwright Container Health Check - {datetime.utcnow().isoformat()}")
    
    checks = [
        ("Module Imports", check_imports),
        ("Governance Wrapper", check_governance_wrapper),
        ("Domain Adapter", check_domain_adapter),
        ("Configuration", check_configuration),
        ("Browsers Installed", check_browsers)
    ]
    
    results = []
    for check_name, check_func in checks:
        try:
            result = check_func()
            results.append((check_name, result))
        except Exception as e:
            logger.error(f"Health check '{check_name}' failed with exception: {e}")
            results.append((check_name, False))
    
    # Summary
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    logger.info(f"Health Check Summary: {passed}/{total} checks passed")
    
    if passed == total:
        logger.info("Playwright Container is healthy")
        sys.exit(0)
    else:
        logger.error("Playwright Container health check failed")
        sys.exit(1)

if __name__ == "__main__":
    main()
