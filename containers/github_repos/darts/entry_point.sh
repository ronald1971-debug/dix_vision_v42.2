#!/bin/bash
set -e
echo "Starting Darts Container for DIX VISION..."
echo "Version: 42.2"
mkdir -p /app/logs /app/data /app/config /app/forecasts
python3 -c "
from darts_governance_wrapper import DartsGovernanceWrapper
from darts_domain_adapter import DartsDomainAdapter
import logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger('darts_container')
try:
    wrapper = DartsGovernanceWrapper(PermissionLevel.READ_ONLY)
    wrapper.initialize_darts({})
    logger.info('Darts Governance Wrapper initialized successfully')
    import time
    while True:
        time.sleep(3600)
except Exception as e:
    logger.error(f'Darts Container error: {str(e)}')
    raise
" || exit 1
