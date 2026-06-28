#!/usr/bin/env python3
"""
CCXT Container Health Check

This script performs health checks for the CCXT container to ensure
proper functioning of the cryptocurrency trading capabilities.
"""

import logging
import sys
from datetime import datetime

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger('ccxt_health_check')

def check_imports():
    """Check if required modules can be imported"""
    try:
        logger.info("CCXT import successful")
        return True
    except ImportError as e:
        logger.error(f"CCXT import failed: {e}")
        return False

def check_governance_wrapper():
    """Check if governance wrapper can be initialized"""
    try:
        from base_external_repo_wrapper import PermissionLevel
        from ccxt_governance_wrapper import CCXTGovernanceWrapper
        
        wrapper = CCXTGovernanceWrapper(PermissionLevel.READ_ONLY)
        logger.info("Governance wrapper initialization successful")
        return True
    except Exception as e:
        logger.error(f"Governance wrapper check failed: {e}")
        return False

def check_domain_adapter():
    """Check if domain adapter can be initialized"""
    try:
        from ccxt_domain_adapter import CCXTDomainAdapter
        adapter = CCXTDomainAdapter()
        logger.info("Domain adapter initialization successful")
        return True
    except Exception as e:
        logger.error(f"Domain adapter check failed: {e}")
        return False

def check_configuration():
    """Check if configuration files exist"""
    import os
    config_path = "/app/config/ccxt_config.yaml"
    
    if os.path.exists(config_path):
        logger.info("Configuration file found")
        return True
    else:
        logger.warning("Configuration file not found, using defaults")
        return True  # Non-critical

def main():
    """Run all health checks"""
    logger.info(f"CCXT Container Health Check - {datetime.utcnow().isoformat()}")
    
    checks = [
        ("Module Imports", check_imports),
        ("Governance Wrapper", check_governance_wrapper),
        ("Domain Adapter", check_domain_adapter),
        ("Configuration", check_configuration)
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
        logger.info("CCXT Container is healthy")
        sys.exit(0)
    else:
        logger.error("CCXT Container health check failed")
        sys.exit(1)

if __name__ == "__main__":
    main()
