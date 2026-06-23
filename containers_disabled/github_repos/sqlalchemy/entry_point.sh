#!/bin/bash
set -e
echo "Starting SQLAlchemy Container for DIX VISION..."
echo "Version: 42.2"
mkdir -p /app/logs /app/data /app/config /app/migrations
python3 -c "
import sys
sys.path.append('/app')
sys.path.append('/app/governance')
sys.path.append('/app/adapters')

from sqlalchemy_governance_wrapper import SQLAlchemyGovernanceWrapper
from sqlalchemy_domain_adapter import SQLAlchemyDomainAdapter
import logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger('sqlalchemy_container')
try:
    wrapper = SQLAlchemyGovernanceWrapper(PermissionLevel.READ_ONLY)
    wrapper.initialize_sqlalchemy({})
    logger.info('SQLAlchemy Governance Wrapper initialized successfully')
    import time
    while True:
        time.sleep(3600)
except Exception as e:
    logger.error(f'SQLAlchemy Container error: {str(e)}')
    raise
" || exit 1
