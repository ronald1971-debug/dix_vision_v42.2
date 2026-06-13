#!/bin/bash
set -e
echo "Starting Celery Enhanced Container for DIX VISION..."
echo "Version: 42.2"
mkdir -p /app/logs /app/data /app/config /app/tasks
python3 -c "
import sys
sys.path.append('/app')
sys.path.append('/app/governance')
sys.path.append('/app/adapters')

from celery_enhanced_governance_wrapper import CeleryEnhancedGovernanceWrapper
from celery_enhanced_domain_adapter import CeleryEnhancedDomainAdapter
import logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger('celery_enhanced_container')
try:
    wrapper = CeleryEnhancedGovernanceWrapper(PermissionLevel.READ_ONLY)
    wrapper.initialize_celery({})
    logger.info('Celery Enhanced Governance Wrapper initialized successfully')
    import time
    while True:
        time.sleep(3600)
except Exception as e:
    logger.error(f'Celery Enhanced Container error: {str(e)}')
    raise
" || exit 1
