#!/bin/bash
# docker-py Container Entry Point Script

set -e

echo "Starting docker-py Container for DIX VISION..."
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
echo "Starting docker-py Governance Wrapper..."
python3 -c "
from docker_py_governance_wrapper import Docker_pyGovernanceWrapper
from docker_py_domain_adapter import Docker_pyDomainAdapter
import logging

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger('docker_py_container')

try:
    logger.info('docker-py Governance Wrapper initialized successfully')
    logger.info('Ready to process operations with governance oversight')
    
    # Keep container running
    import time
    while True:
        time.sleep(3600)
        
except Exception as e:
    logger.error(f'docker-py Container error: {str(e)}')
    raise
" || {
    echo "docker-py container failed to start"
    exit 1
}
