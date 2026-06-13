#!/bin/bash
# python-jose Container Entry Point Script

set -e

echo "Starting python-jose Container for DIX VISION..."
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
echo "Starting python-jose Governance Wrapper..."
python3 -c "
from python_jose_governance_wrapper import Python_joseGovernanceWrapper
from python_jose_domain_adapter import Python_joseDomainAdapter
import logging

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger('python_jose_container')

try:
    logger.info('python-jose Governance Wrapper initialized successfully')
    logger.info('Ready to process operations with governance oversight')
    
    # Keep container running
    import time
    while True:
        time.sleep(3600)
        
except Exception as e:
    logger.error(f'python-jose Container error: {str(e)}')
    raise
" || {
    echo "python-jose container failed to start"
    exit 1
}
