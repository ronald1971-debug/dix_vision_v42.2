#!/bin/bash
set -e
echo "Starting FastAPI Enhanced Container for DIX VISION..."
echo "Version: 42.2"
mkdir -p /app/logs /app/data /app/config /app/apis
python3 -c "
from fastapi_enhanced_governance_wrapper import FastAPIEnhancedGovernanceWrapper
from fastapi_enhanced_domain_adapter import FastAPIEnhancedDomainAdapter
import logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger('fastapi_enhanced_container')
try:
    wrapper = FastAPIEnhancedGovernanceWrapper(PermissionLevel.READ_ONLY)
    wrapper.initialize_fastapi({})
    logger.info('FastAPI Enhanced Governance Wrapper initialized successfully')
    import time
    while True:
        time.sleep(3600)
except Exception as e:
    logger.error(f'FastAPI Enhanced Container error: {str(e)}')
    raise
" || exit 1
