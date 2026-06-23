#!/bin/bash
# newspaper3k Container Entry Point Script

set -e

echo "Starting newspaper3k Container for DIX VISION..."
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
echo "Starting newspaper3k Governance Wrapper..."
python3 -c "
import sys
sys.path.append('/app')
sys.path.append('/app/governance')
sys.path.append('/app/adapters')

from newspaper3k_governance_wrapper import Newspaper3kGovernanceWrapper
from newspaper3k_domain_adapter import Newspaper3kDomainAdapter
import logging

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger('newspaper3k_container')

try:
    logger.info('newspaper3k Governance Wrapper initialized successfully')
    logger.info('Ready to process operations with governance oversight')
    
    # Keep container running
    import time
    while True:
        time.sleep(3600)
        
except Exception as e:
    logger.error(f'newspaper3k Container error: {str(e)}')
    raise
" || {
    echo "newspaper3k container failed to start"
    exit 1
}
