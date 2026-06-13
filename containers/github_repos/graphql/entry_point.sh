#!/bin/bash
set -e
echo "Starting GraphQL Container for DIX VISION..."
echo "Version: 42.2"
mkdir -p /app/logs /app/data /app/config /app/schemas
python3 -c "
from graphql_governance_wrapper import GraphQLGovernanceWrapper
from graphql_domain_adapter import GraphQLDomainAdapter
import logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger('graphql_container')
try:
    wrapper = GraphQLGovernanceWrapper(PermissionLevel.READ_ONLY)
    wrapper.initialize_graphql({})
    logger.info('GraphQL Governance Wrapper initialized successfully')
    import time
    while True:
        time.sleep(3600)
except Exception as e:
    logger.error(f'GraphQL Container error: {str(e)}')
    raise
" || exit 1
