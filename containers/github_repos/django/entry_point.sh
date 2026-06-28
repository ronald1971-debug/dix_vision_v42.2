#!/bin/bash
set -e
echo "Starting Django Container for DIX VISION..."
echo "Version: 42.2"
mkdir -p /app/logs /app/data /app/config /app/projects
python3 -c "
import sys
sys.path.append('/app')
sys.path.append('/app/governance')
sys.path.append('/app/adapters')

from django_governance_wrapper import DjangoGovernanceWrapper
from django_domain_adapter import DjangoDomainAdapter
import logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger('django_container')
try:
    wrapper = DjangoGovernanceWrapper(PermissionLevel.READ_ONLY)
    wrapper.initialize_django({})
    logger.info('Django Governance Wrapper initialized successfully')
    import time
    while True:
        time.sleep(3600)
except Exception as e:
    logger.error(f'Django Container error: {str(e)}')
    raise
" || exit 1
