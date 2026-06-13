#!/bin/bash
set -e
echo "Starting SQLAlchemy Enhanced Container for DIX VISION..."
echo "Version: 42.2"
mkdir -p /app/logs /app/data /app/config /app/models
python3 -c "
import sys
sys.path.append('/app')
sys.path.append('/app/governance')
sys.path.append('/app/adapters')

from sqlalchemy_enhanced_governance_wrapper import SQLAlchemyEnhancedGovernanceWrapper
from sqlalchemy_enhanced_domain_adapter import SQLAlchemyEnhancedDomainAdapter
import logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger('sqlalchemy_enhanced_container')
try:
    wrapper = SQLAlchemyEnhancedGovernanceWrapper(PermissionLevel.READ_ONLY)
    wrapper.initialize_sqlalchemy({})
    logger.info('SQLAlchemy Enhanced Governance Wrapper initialized successfully')
    import time
    while True:
        time.sleep(3600)
except Exception as e:
    logger.error(f'SQLAlchemy Enhanced Container error: {str(e)}')
    raise
" || exit 1
