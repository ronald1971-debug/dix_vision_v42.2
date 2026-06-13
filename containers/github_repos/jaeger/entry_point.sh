#!/bin/bash
set -e
echo "Starting Jaeger Container for DIX VISION..."
echo "Version: 42.2"
mkdir -p /app/logs /app/data /app/config /app/traces
python3 -c "
from jaeger_governance_wrapper import JaegerGovernanceWrapper
from jaeger_domain_adapter import JaegerDomainAdapter
import logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger('jaeger_container')
try:
    wrapper = JaegerGovernanceWrapper(PermissionLevel.READ_ONLY)
    wrapper.initialize_jaeger({})
    logger.info('Jaeger Governance Wrapper initialized successfully')
    import time
    while True:
        time.sleep(3600)
except Exception as e:
    logger.error(f'Jaeger Container error: {str(e)}')
    raise
" || exit 1
