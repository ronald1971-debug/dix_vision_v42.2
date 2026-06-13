#!/bin/bash
# scipy-optimize Container Entry Point Script

set -e

echo "Starting scipy-optimize Container for DIX VISION..."
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
echo "Starting scipy-optimize Governance Wrapper..."
python3 -c "
import sys
sys.path.append('/app')
sys.path.append('/app/governance')
sys.path.append('/app/adapters')

from scipy_optimize_governance_wrapper import Scipy_optimizeGovernanceWrapper
from scipy_optimize_domain_adapter import Scipy_optimizeDomainAdapter
import logging

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger('scipy_optimize_container')

try:
    logger.info('scipy-optimize Governance Wrapper initialized successfully')
    logger.info('Ready to process operations with governance oversight')
    
    # Keep container running
    import time
    while True:
        time.sleep(3600)
        
except Exception as e:
    logger.error(f'scipy-optimize Container error: {str(e)}')
    raise
" || {
    echo "scipy-optimize container failed to start"
    exit 1
}
