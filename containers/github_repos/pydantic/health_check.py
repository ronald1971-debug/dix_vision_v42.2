#!/usr/bin/env python3
import sys
import logging
from datetime import datetime

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger('pydantic_health_check')

def check_imports():
    try:
        import pydantic
        logger.info("Pydantic import successful")
        return True
    except ImportError as e:
        logger.error(f"Pydantic import failed: {e}")
        return False

def check_governance_wrapper():
    try:
        from pydantic_governance_wrapper import PydanticGovernanceWrapper
        from base_external_repo_wrapper import PermissionLevel
        wrapper = PydanticGovernanceWrapper(PermissionLevel.READ_ONLY)
        logger.info("Governance wrapper initialization successful")
        return True
    except Exception as e:
        logger.error(f"Governance wrapper check failed: {e}")
        return False

def check_domain_adapter():
    try:
        from pydantic_domain_adapter import PydanticDomainAdapter
        adapter = PydanticDomainAdapter()
        logger.info("Domain adapter initialization successful")
        return True
    except Exception as e:
        logger.error(f"Domain adapter check failed: {e}")
        return False

def main():
    logger.info(f"Pydantic Container Health Check - {datetime.utcnow().isoformat()}")
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
        logger.info("Pydantic Container is healthy")
        sys.exit(0)
    else:
        logger.error("Pydantic Container health check failed")
        sys.exit(1)

if __name__ == "__main__":
    main()
