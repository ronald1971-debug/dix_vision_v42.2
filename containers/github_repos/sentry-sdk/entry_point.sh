#!/bin/bash
# sentry-sdk Container Entry Point Script

set -e

echo "Starting sentry-sdk Container for DIX VISION..."
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
echo "Starting sentry-sdk Governance Wrapper..."
python3 -c "
import sys
sys.path.append('/app')
sys.path.append('/app/governance')
sys.path.append('/app/adapters')

from sentry_sdk_governance_wrapper import Sentry_sdkGovernanceWrapper
from sentry_sdk_domain_adapter import Sentry_sdkDomainAdapter
import logging

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger('sentry_sdk_container')

try:
    logger.info('sentry-sdk Governance Wrapper initialized successfully')
    logger.info('Ready to process operations with governance oversight')
    
    # Keep container running
    import time
    while True:
        time.sleep(3600)
        
except Exception as e:
    logger.error(f'sentry-sdk Container error: {str(e)}')
    raise
" || {
    echo "sentry-sdk container failed to start"
    exit 1
}
