#!/bin/bash
set -e
echo "Starting Tempo Container for DIX VISION..."
echo "Version: 42.2"
mkdir -p /app/logs /app/data /app/config /app/metrics
python3 -c "
from tempo_governance_wrapper import TempoGovernanceWrapper
from tempo_domain_adapter import TempoDomainAdapter
import logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger('tempo_container')
try:
    wrapper = TempoGovernanceWrapper(PermissionLevel.READ_ONLY)
    wrapper.initialize_tempo({})
    logger.info('Tempo Governance Wrapper initialized successfully')
    import time
    while True:
        time.sleep(3600)
except Exception as e:
    logger.error(f'Tempo Container error: {str(e)}')
    raise
" || exit 1
