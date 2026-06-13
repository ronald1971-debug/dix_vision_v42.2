#!/bin/bash
set -e
echo "Starting Ray Container for DIX VISION..."
echo "Version: 42.2"
mkdir -p /app/logs /app/data /app/config /app/tasks
python3 -c "
import sys
sys.path.append('/app')
sys.path.append('/app/governance')
sys.path.append('/app/adapters')

from ray_governance_wrapper import RayGovernanceWrapper
from ray_domain_adapter import RayDomainAdapter
import logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger('ray_container')
try:
    wrapper = RayGovernanceWrapper(PermissionLevel.READ_ONLY)
    wrapper.initialize_ray({})
    logger.info('Ray Governance Wrapper initialized successfully')
    import time
    while True:
        time.sleep(3600)
except Exception as e:
    logger.error(f'Ray Container error: {str(e)}')
    raise
" || exit 1
