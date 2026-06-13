#!/bin/bash
set -e
echo "Starting PuLP Container for DIX VISION..."
echo "Version: 42.2"
mkdir -p /app/logs /app/data /app/config /app/problems
python3 -c "
from pulp_governance_wrapper import PuLPGovernanceWrapper
from pulp_domain_adapter import PuLPDomainAdapter
import logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger('pulp_container')
try:
    wrapper = PuLPGovernanceWrapper(PermissionLevel.READ_ONLY)
    wrapper.initialize_pulp({})
    logger.info('PuLP Governance Wrapper initialized successfully')
    import time
    while True:
        time.sleep(3600)
except Exception as e:
    logger.error(f'PuLP Container error: {str(e)}')
    raise
" || exit 1
