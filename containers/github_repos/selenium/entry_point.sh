#!/bin/bash
set -e
echo "Starting Selenium Container for DIX VISION..."
echo "Version: 42.2"
mkdir -p /app/logs /app/data /app/config /app/browsers
python3 -c "
from selenium_governance_wrapper import SeleniumGovernanceWrapper
from selenium_domain_adapter import SeleniumDomainAdapter
import logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger('selenium_container')
try:
    wrapper = SeleniumGovernanceWrapper(PermissionLevel.READ_ONLY)
    wrapper.initialize_selenium({})
    logger.info('Selenium Governance Wrapper initialized successfully')
    import time
    while True:
        time.sleep(3600)
except Exception as e:
    logger.error(f'Selenium Container error: {str(e)}')
    raise
" || exit 1
