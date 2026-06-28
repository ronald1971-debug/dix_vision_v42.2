#!/bin/bash
set -e
echo "Starting Jinja2 Container for DIX VISION..."
echo "Version: 42.2"
mkdir -p /app/logs /app/data /app/config /app/templates
python3 -c "
import sys
sys.path.append('/app')
sys.path.append('/app/governance')
sys.path.append('/app/adapters')

from jinja2_governance_wrapper import Jinja2GovernanceWrapper
from jinja2_domain_adapter import Jinja2DomainAdapter
import logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger('jinja2_container')
try:
    wrapper = Jinja2GovernanceWrapper(PermissionLevel.READ_ONLY)
    wrapper.initialize_jinja2({})
    logger.info('Jinja2 Governance Wrapper initialized successfully')
    import time
    while True:
        time.sleep(3600)
except Exception as e:
    logger.error(f'Jinja2 Container error: {str(e)}')
    raise
" || exit 1
