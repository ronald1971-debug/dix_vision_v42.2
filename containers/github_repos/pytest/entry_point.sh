#!/bin/bash
set -e
echo "Starting pytest Container for DIX VISION..."
echo "Version: 42.2"
mkdir -p /app/logs /app/data /app/config /app/tests
python3 -c "
from pytest_governance_wrapper import PytestGovernanceWrapper
from pytest_domain_adapter import PytestDomainAdapter
import logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger('pytest_container')
try:
    wrapper = PytestGovernanceWrapper(PermissionLevel.READ_ONLY)
    wrapper.initialize_pytest({})
    logger.info('pytest Governance Wrapper initialized successfully')
    import time
    while True:
        time.sleep(3600)
except Exception as e:
    logger.error(f'pytest Container error: {str(e)}')
    raise
" || exit 1
