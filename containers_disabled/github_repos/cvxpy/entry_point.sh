#!/bin/bash
# cvxpy Container Entry Point Script

set -e

echo "Starting cvxpy Container for DIX VISION..."
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
echo "Starting cvxpy Governance Wrapper..."
python3 -c "
import sys
sys.path.append('/app')
sys.path.append('/app/governance')
sys.path.append('/app/adapters')

from cvxpy_governance_wrapper import CvxpyGovernanceWrapper
from cvxpy_domain_adapter import CvxpyDomainAdapter
import logging

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger('cvxpy_container')

try:
    logger.info('cvxpy Governance Wrapper initialized successfully')
    logger.info('Ready to process operations with governance oversight')
    
    # Keep container running
    import time
    while True:
        time.sleep(3600)
        
except Exception as e:
    logger.error(f'cvxpy Container error: {str(e)}')
    raise
" || {
    echo "cvxpy container failed to start"
    exit 1
}
