#!/bin/bash
set -e
echo "Starting Consul Container for DIX VISION..."
echo "Version: 42.2"
mkdir -p /app/logs /app/data /app/config /app/services
python3 -c "
import sys
sys.path.append('/app')
sys.path.append('/app/governance')
sys.path.append('/app/adapters')

from consul_governance_wrapper import ConsulGovernanceWrapper
from consul_domain_adapter import ConsulDomainAdapter
import logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger('consul_container')
try:
    wrapper = ConsulGovernanceWrapper(PermissionLevel.READ_ONLY)
    wrapper.initialize_consul({})
    logger.info('Consul Governance Wrapper initialized successfully')
    import time
    while True:
        time.sleep(3600)
except Exception as e:
    logger.error(f'Consul Container error: {str(e)}')
    raise
" || exit 1
