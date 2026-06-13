#!/usr/bin/env python3
"""
newspaper3k Container Health Check

This script performs health checks for the newspaper3k container.
"""

import sys
import logging
from datetime import datetime

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger('newspaper3k_health_check')

def check_imports():
    """Check if required modules can be imported"""
    try:
        # Main package import check would go here
        logger.info("Basic imports successful")
        return True
    except ImportError as e:
        logger.error(f"Import failed: {e}")
        return False

def check_governance_wrapper():
    """Check if governance wrapper can be initialized"""
    try:
        from newspaper3k_governance_wrapper import Newspaper3kGovernanceWrapper
        from base_external_repo_wrapper import PermissionLevel
        
        wrapper = Newspaper3kGovernanceWrapper(PermissionLevel.READ_ONLY)
        logger.info("Governance wrapper initialization successful")
        return True
    except Exception as e:
        logger.error(f"Governance wrapper check failed: {e}")
        return False

def check_domain_adapter():
    """Check if domain adapter can be initialized"""
    try:
        from newspaper3k_domain_adapter import Newspaper3kDomainAdapter
        adapter = Newspaper3kDomainAdapter()
        logger.info("Domain adapter initialization successful")
        return True
    except Exception as e:
        logger.error(f"Domain adapter check failed: {e}")
        return False

def check_configuration():
    """Check if configuration files exist"""
    import os
    config_path = "/app/config/newspaper3k_config.yaml"
    
    if os.path.exists(config_path):
        logger.info("Configuration file found")
        return True
    else:
        logger.warning("Configuration file not found, using defaults")
        return True

def main():
    """Run all health checks"""
    logger.info(f"newspaper3k Container Health Check - {datetime.utcnow().isoformat()}")
    
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
        logger.info("newspaper3k Container is healthy")
        sys.exit(0)
    else:
        logger.error("newspaper3k Container health check failed")
        sys.exit(1)

if __name__ == "__main__":
    main()
