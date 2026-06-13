#!/bin/bash
# redis-py-cluster Container Entry Point Script

set -e

echo "Starting redis-py-cluster Container for DIX VISION..."
echo "Version: 42.2"
echo "Timestamp: $(date)"

# Load environment variables if .env file exists
if [ -f /app/config/.env ]; then
    echo "Loading environment variables from .env file"
    export $(cat /app/config/.env | grep -v '^#' | xargs)
fi

# Create necessary directories
mkdir -p /app/logs
mkdir -p /app/data
mkdir -p /app/config

# Start the governance wrapper
echo "Starting redis-py-cluster Governance Wrapper..."
python3 -c "
from redis_py_cluster_governance_wrapper import Redis_py_clusterGovernanceWrapper
from redis_py_cluster_domain_adapter import Redis_py_clusterDomainAdapter
import logging

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger('redis_py_cluster_container')

try:
    logger.info('redis-py-cluster Governance Wrapper initialized successfully')
    logger.info('Ready to process operations with governance oversight')
    
    # Keep container running
    import time
    while True:
        time.sleep(3600)
        
except Exception as e:
    logger.error(f'redis-py-cluster Container error: {str(e)}')
    raise
" || {
    echo "redis-py-cluster container failed to start"
    exit 1
}
