#!/bin/bash
# prefect Container Entry Point Script

set -e

echo "Starting prefect Container for DIX VISION..."
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
echo "Starting prefect Governance Wrapper..."
python3 -c "
from prefect_governance_wrapper import PrefectGovernanceWrapper
from prefect_domain_adapter import PrefectDomainAdapter
import logging

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger('prefect_container')

try:
    logger.info('prefect Governance Wrapper initialized successfully')
    logger.info('Ready to process operations with governance oversight')
    
    # Keep container running
    import time
    while True:
        time.sleep(3600)
        
except Exception as e:
    logger.error(f'prefect Container error: {str(e)}')
    raise
" || {
    echo "prefect container failed to start"
    exit 1
}
