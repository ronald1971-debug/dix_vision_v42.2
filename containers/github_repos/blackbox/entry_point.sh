#!/bin/bash
set -e
echo "Starting Blackbox Container for DIX VISION..."
echo "Version: 42.2"
mkdir -p /app/logs /app/data /app/config /app/probes
python3 -c "
from blackbox_governance_wrapper import BlackboxGovernanceWrapper
from blackbox_domain_adapter import BlackboxDomainAdapter
import logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger('blackbox_container')
try:
    wrapper = BlackboxGovernanceWrapper(PermissionLevel.READ_ONLY)
    wrapper.initialize_blackbox({})
    logger.info('Blackbox Governance Wrapper initialized successfully')
    import time
    while True:
        time.sleep(3600)
except Exception as e:
    logger.error(f'Blackbox Container error: {str(e)}')
    raise
" || exit 1
