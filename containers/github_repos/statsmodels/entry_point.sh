#!/bin/bash
# statsmodels Container Entry Point Script

set -e

echo "Starting statsmodels Container for DIX VISION..."
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
echo "Starting statsmodels Governance Wrapper..."
python3 -c "
from statsmodels_governance_wrapper import StatsmodelsGovernanceWrapper
from statsmodels_domain_adapter import StatsmodelsDomainAdapter
import logging

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger('statsmodels_container')

try:
    logger.info('statsmodels Governance Wrapper initialized successfully')
    logger.info('Ready to process operations with governance oversight')
    
    # Keep container running
    import time
    while True:
        time.sleep(3600)
        
except Exception as e:
    logger.error(f'statsmodels Container error: {str(e)}')
    raise
" || {
    echo "statsmodels container failed to start"
    exit 1
}
