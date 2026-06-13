#!/bin/bash
set -e
echo "Starting Marshmallow Container for DIX VISION..."
echo "Version: 42.2"
mkdir -p /app/logs /app/data /app/config /app/schemas
python3 -c "
from marshmallow_governance_wrapper import MarshmallowGovernanceWrapper
from marshmallow_domain_adapter import MarshmallowDomainAdapter
import logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger('marshmallow_container')
try:
    wrapper = MarshmallowGovernanceWrapper(PermissionLevel.READ_ONLY)
    wrapper.initialize_marshmallow({})
    logger.info('Marshmallow Governance Wrapper initialized successfully')
    import time
    while True:
        time.sleep(3600)
except Exception as e:
    logger.error(f'Marshmallow Container error: {str(e)}')
    raise
" || exit 1
