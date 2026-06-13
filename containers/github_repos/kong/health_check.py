#!/usr/bin/env python3
import sys
import logging
from datetime import datetime

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger('kong_health_check')

def check_imports():
    try:
        import kong
        logger.info("Kong import successful")
        return True
    except ImportError as e:
        logger.error(f"Kong import failed: {e}")
        return False

def check_governance_wrapper():
    try:
        from kong_governance_wrapper import KongGovernanceWrapper
        from base_external_repo_wrapper import PermissionLevel
        wrapper = KongGovernanceWrapper(PermissionLevel.READ_ONLY)
        logger.info("Governance wrapper initialization successful")
        return True
    except Exception as e:
        logger.error(f"Governance wrapper check failed: {e}")
        return False

def check_domain_adapter():
    try:
        from kong_domain_adapter import KongDomainAdapter
        adapter = KongDomainAdapter()
        logger.info("Domain adapter initialization successful")
        return True
    except Exception as e:
        logger.error(f"Domain adapter check failed: {e}")
        return False

def main():
    logger.info(f"Kong Container Health Check - {datetime.utcnow().isoformat()}")
    checks = [
        ("Module Imports", check_imports),
        ("Governance Wrapper", check_governance_wrapper),
        ("Domain Adapter", check_domain_adapter)
    ]
    results = [(name, func()) for name, func in checks]
    passed = sum(1 for _, result in results if result)
    total = len(results)
    logger.info(f"Health Check Summary: {passed}/{total} checks passed")
    if passed == total:
        logger.info("Kong Container is healthy")
        sys.exit(0)
    else:
        logger.error("Kong Container health check failed")
        sys.exit(1)

if __name__ == "__main__":
    main()
