#!/bin/bash
set -e
echo "Starting Pytest Enhanced Container for DIX VISION..."
echo "Version: 42.2"
mkdir -p /app/logs /app/data /app/config /app/tests
python3 -c "
import sys
sys.path.append('/app')
sys.path.append('/app/governance')
sys.path.append('/app/adapters')

from pytest_enhanced_governance_wrapper import PytestEnhancedGovernanceWrapper
from pytest_enhanced_domain_adapter import PytestEnhancedDomainAdapter
import logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger('pytest_enhanced_container')
try:
    wrapper = PytestEnhancedGovernanceWrapper(PermissionLevel.READ_ONLY)
    wrapper.initialize_pytest({})
    logger.info('Pytest Enhanced Governance Wrapper initialized successfully')
    import time
    while True:
        time.sleep(3600)
except Exception as e:
    logger.error(f'Pytest Enhanced Container error: {str(e)}')
    raise
" || exit 1
