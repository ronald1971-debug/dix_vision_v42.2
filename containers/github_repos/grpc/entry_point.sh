#!/bin/bash
set -e
echo "Starting gRPC Container for DIX VISION..."
echo "Version: 42.2"
mkdir -p /app/logs /app/data /app/config /app/services
python3 -c "
import sys
sys.path.append('/app')
sys.path.append('/app/governance')
sys.path.append('/app/adapters')

from grpc_governance_wrapper import GrpcGovernanceWrapper
from grpc_domain_adapter import GrpcDomainAdapter
import logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger('grpc_container')
try:
    wrapper = GrpcGovernanceWrapper(PermissionLevel.READ_ONLY)
    wrapper.initialize_grpc({})
    logger.info('gRPC Governance Wrapper initialized successfully')
    import time
    while True:
        time.sleep(3600)
except Exception as e:
    logger.error(f'gRPC Container error: {str(e)}')
    raise
" || exit 1
