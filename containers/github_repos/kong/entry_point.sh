#!/bin/bash
set -e
echo "Starting Kong Container for DIX VISION..."
echo "Version: 42.2"
mkdir -p /app/logs /app/data /app/config /app/routes
python3 -c "
import sys
sys.path.append('/app')
sys.path.append('/app/governance')
sys.path.append('/app/adapters')

from kong_governance_wrapper import KongGovernanceWrapper
from kong_domain_adapter import KongDomainAdapter
import logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger('kong_container')
try:
    wrapper = KongGovernanceWrapper(PermissionLevel.READ_ONLY)
    wrapper.initialize_kong({})
    logger.info('Kong Governance Wrapper initialized successfully')
    import time
    while True:
        time.sleep(3600)
except Exception as e:
    logger.error(f'Kong Container error: {str(e)}')
    raise
" || exit 1
