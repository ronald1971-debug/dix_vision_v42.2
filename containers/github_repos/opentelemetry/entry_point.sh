#!/bin/bash
set -e
echo "Starting OpenTelemetry Container for DIX VISION..."
echo "Version: 42.2"
mkdir -p /app/logs /app/data /app/config /app/traces
python3 -c "
from opentelemetry_governance_wrapper import OpenTelemetryGovernanceWrapper
from opentelemetry_domain_adapter import OpenTelemetryDomainAdapter
import logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger('opentelemetry_container')
try:
    wrapper = OpenTelemetryGovernanceWrapper(PermissionLevel.READ_ONLY)
    wrapper.initialize_opentelemetry({})
    logger.info('OpenTelemetry Governance Wrapper initialized successfully')
    import time
    while True:
        time.sleep(3600)
except Exception as e:
    logger.error(f'OpenTelemetry Container error: {str(e)}')
    raise
" || exit 1
