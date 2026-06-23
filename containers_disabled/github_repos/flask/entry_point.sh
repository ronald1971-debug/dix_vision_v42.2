#!/bin/bash
set -e
echo "Starting Flask Container for DIX VISION..."
echo "Version: 42.2"
mkdir -p /app/logs /app/data /app/config /app/applications
python3 -c "
import sys
sys.path.append('/app')
sys.path.append('/app/governance')
sys.path.append('/app/adapters')

from flask_governance_wrapper import FlaskGovernanceWrapper
from flask_domain_adapter import FlaskDomainAdapter
import logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger('flask_container')
try:
    wrapper = FlaskGovernanceWrapper(PermissionLevel.READ_ONLY)
    wrapper.initialize_flask({})
    logger.info('Flask Governance Wrapper initialized successfully')
    import time
    while True:
        time.sleep(3600)
except Exception as e:
    logger.error(f'Flask Container error: {str(e)}')
    raise
" || exit 1
