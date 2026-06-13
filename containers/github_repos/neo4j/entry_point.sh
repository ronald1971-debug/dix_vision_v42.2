#!/bin/bash
set -e
echo "Starting Neo4j Container for DIX VISION..."
echo "Version: 42.2"
mkdir -p /app/logs /app/data /app/config /app/graphs
python3 -c "
import sys
sys.path.append('/app')
sys.path.append('/app/governance')
sys.path.append('/app/adapters')

from neo4j_governance_wrapper import Neo4jGovernanceWrapper
from neo4j_domain_adapter import Neo4jDomainAdapter
import logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger('neo4j_container')
try:
    wrapper = Neo4jGovernanceWrapper(PermissionLevel.READ_ONLY)
    wrapper.initialize_neo4j({})
    logger.info('Neo4j Governance Wrapper initialized successfully')
    import time
    while True:
        time.sleep(3600)
except Exception as e:
    logger.error(f'Neo4j Container error: {str(e)}')
    raise
" || exit 1
