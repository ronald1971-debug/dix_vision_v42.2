#!/bin/bash
set -e
echo "Starting AIOHTTP Container for DIX VISION..."
echo "Version: 42.2"
mkdir -p /app/logs /app/data /app/config /app/applications
python3 -c "
import sys
sys.path.append('/app')
sys.path.append('/app/governance')
sys.path.append('/app/adapters')

from aiohttp_governance_wrapper import AIOHTTPGovernanceWrapper
from aiohttp_domain_adapter import AIOHTTPDomainAdapter
import logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger('aiohttp_container')
try:
    wrapper = AIOHTTPGovernanceWrapper(PermissionLevel.READ_ONLY)
    wrapper.initialize_aiohttp({})
    logger.info('AIOHTTP Governance Wrapper initialized successfully')
    import time
    while True:
        time.sleep(3600)
except Exception as e:
    logger.error(f'AIOHTTP Container error: {str(e)}')
    raise
" || exit 1
