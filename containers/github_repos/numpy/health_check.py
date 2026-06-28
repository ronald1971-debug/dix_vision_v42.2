#!/usr/bin/env python3
"""
NumPy Container Health Check

This script performs health checks for the NumPy container to ensure
proper functioning of the numerical computing capabilities.
"""

import logging
import sys
from datetime import datetime

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger('numpy_health_check')

def check_imports():
    """Check if required modules can be imported"""
    try:
        logger.info("NumPy import successful")
        return True
    except ImportError as e:
        logger.error(f"NumPy import failed: {e}")
        return False

def check_governance_wrapper():
    """Check if governance wrapper can be initialized"""
    try:
        from base_external_repo_wrapper import PermissionLevel
        from numpy_governance_wrapper import NumPyGovernanceWrapper
        
        wrapper = NumPyGovernanceWrapper(PermissionLevel.READ_ONLY)
        logger.info("Governance wrapper initialization successful")
        return True
    except Exception as e:
        logger.error(f"Governance wrapper check failed: {e}")
        return False

def check_domain_adapter():
    """Check if domain adapter can be initialized"""
    try:
        from numpy_domain_adapter import NumPyDomainAdapter
        adapter = NumPyDomainAdapter()
        logger.info("Domain adapter initialization successful")
        return True
    except Exception as e:
        logger.error(f"Domain adapter check failed: {e}")
        return False

def check_configuration():
    """Check if configuration files exist"""
    import os
    config_path = "/app/config/numpy_config.yaml"
    
    if os.path.exists(config_path):
        logger.info("Configuration file found")
        return True
    else:
        logger.warning("Configuration file not found, using defaults")
        return True

def check_computational_capability():
    """Check if NumPy computational capabilities work"""
    try:
        import numpy as np

        # Test basic operations
        test_array = np.array([1, 2, 3, 4, 5])
        result = np.mean(test_array)
        logger.info(f"NumPy computational check successful (mean test: {result})")
        return True
    except Exception as e:
        logger.error(f"NumPy computational check failed: {e}")
        return False

def main():
    """Run all health checks"""
    logger.info(f"NumPy Container Health Check - {datetime.utcnow().isoformat()}")
    
    checks = [
        ("Module Imports", check_imports),
        ("Governance Wrapper", check_governance_wrapper),
        ("Domain Adapter", check_domain_adapter),
        ("Configuration", check_configuration),
        ("Computational Capability", check_computational_capability)
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
        logger.info("NumPy Container is healthy")
        sys.exit(0)
    else:
        logger.error("NumPy Container health check failed")
        sys.exit(1)

if __name__ == "__main__":
    main()
