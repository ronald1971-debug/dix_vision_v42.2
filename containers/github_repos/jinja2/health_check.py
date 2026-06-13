#!/usr/bin/env python3
import sys
import logging
from datetime import datetime

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger('jinja2_health_check')

def check_imports():
    try:
        import jinja2
        logger.info("Jinja2 import successful")
        return True
    except ImportError as e:
        logger.error(f"Jinja2 import failed: {e}")
        return False

def check_governance_wrapper():
    try:
        from jinja2_governance_wrapper import Jinja2GovernanceWrapper
        from base_external_repo_wrapper import PermissionLevel
        wrapper = Jinja2GovernanceWrapper(PermissionLevel.READ_ONLY)
        logger.info("Governance wrapper initialization successful")
        return True
    except Exception as e:
        logger.error(f"Governance wrapper check failed: {e}")
        return False

def check_domain_adapter():
    try:
        from jinja2_domain_adapter import Jinja2DomainAdapter
        adapter = Jinja2DomainAdapter()
        logger.info("Domain adapter initialization successful")
        return True
    except Exception as e:
        logger.error(f"Domain adapter check failed: {e}")
        return False

def main():
    logger.info(f"Jinja2 Container Health Check - {datetime.utcnow().isoformat()}")
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
        logger.info("Jinja2 Container is healthy")
        sys.exit(0)
    else:
        logger.error("Jinja2 Container health check failed")
        sys.exit(1)

if __name__ == "__main__":
    main()
