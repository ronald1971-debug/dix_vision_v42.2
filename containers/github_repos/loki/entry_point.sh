#!/bin/bash
set -e
echo "Starting Loki Container for DIX VISION..."
echo "Version: 42.2"
mkdir -p /app/logs /app/data /app/config /app/streams
python3 -c "
from loki_governance_wrapper import LokiGovernanceWrapper
from loki_domain_adapter import LokiDomainAdapter
import logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger('loki_container')
try:
    wrapper = LokiGovernanceWrapper(PermissionLevel.READ_ONLY)
    wrapper.initialize_loki({})
    logger.info('Loki Governance Wrapper initialized successfully')
    import time
    while True:
        time.sleep(3600)
except Exception as e:
    logger.error(f'Loki Container error: {str(e)}')
    raise
" || exit 1
