#!/bin/bash
set -e
echo "Starting Redis Cluster Container for DIX VISION..."
echo "Version: 42.2"
mkdir -p /app/logs /app/data /app/config /app/cluster
python3 -c "
import sys
sys.path.append('/app')
sys.path.append('/app/governance')
sys.path.append('/app/adapters')

from redis_cluster_governance_wrapper import RedisClusterGovernanceWrapper
from redis_cluster_domain_adapter import RedisClusterDomainAdapter
import logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger('redis_cluster_container')
try:
    wrapper = RedisClusterGovernanceWrapper(PermissionLevel.READ_ONLY)
    wrapper.initialize_redis_cluster({})
    logger.info('Redis Cluster Governance Wrapper initialized successfully')
    import time
    while True:
        time.sleep(3600)
except Exception as e:
    logger.error(f'Redis Cluster Container error: {str(e)}')
    raise
" || exit 1
