#!/bin/bash
set -e
echo "Starting Pydantic Container for DIX VISION..."
echo "Version: 42.2"
mkdir -p /app/logs /app/data /app/config /app/schemas
python3 -c "
from pydantic_governance_wrapper import PydanticGovernanceWrapper
from pydantic_domain_adapter import PydanticDomainAdapter
import logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger('pydantic_container')
try:
    wrapper = PydanticGovernanceWrapper(PermissionLevel.READ_ONLY)
    wrapper.initialize_pydantic({})
    logger.info('Pydantic Governance Wrapper initialized successfully')
    import time
    while True:
        time.sleep(3600)
except Exception as e:
    logger.error(f'Pydantic Container error: {str(e)}')
    raise
" || exit 1
