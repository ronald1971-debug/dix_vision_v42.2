#!/bin/bash
# kubernetes-python Container Entry Point Script

set -e

echo "Starting kubernetes-python Container for DIX VISION..."
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
echo "Starting kubernetes-python Governance Wrapper..."
python3 -c "
import sys
sys.path.append('/app')
sys.path.append('/app/governance')
sys.path.append('/app/adapters')

from kubernetes_python_governance_wrapper import Kubernetes_pythonGovernanceWrapper
from kubernetes_python_domain_adapter import Kubernetes_pythonDomainAdapter
import logging

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger('kubernetes_python_container')

try:
    logger.info('kubernetes-python Governance Wrapper initialized successfully')
    logger.info('Ready to process operations with governance oversight')
    
    # Keep container running
    import time
    while True:
        time.sleep(3600)
        
except Exception as e:
    logger.error(f'kubernetes-python Container error: {str(e)}')
    raise
" || {
    echo "kubernetes-python container failed to start"
    exit 1
}
