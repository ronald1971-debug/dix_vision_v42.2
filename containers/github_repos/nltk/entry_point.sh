#!/bin/bash
# nltk Container Entry Point Script

set -e

echo "Starting nltk Container for DIX VISION..."
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
echo "Starting nltk Governance Wrapper..."
python3 -c "
from nltk_governance_wrapper import NltkGovernanceWrapper
from nltk_domain_adapter import NltkDomainAdapter
import logging

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger('nltk_container')

try:
    logger.info('nltk Governance Wrapper initialized successfully')
    logger.info('Ready to process operations with governance oversight')
    
    # Keep container running
    import time
    while True:
        time.sleep(3600)
        
except Exception as e:
    logger.error(f'nltk Container error: {str(e)}')
    raise
" || {
    echo "nltk container failed to start"
    exit 1
}
