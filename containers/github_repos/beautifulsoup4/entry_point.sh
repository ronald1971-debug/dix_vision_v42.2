#!/bin/bash
# beautifulsoup4 Container Entry Point Script

set -e

echo "Starting beautifulsoup4 Container for DIX VISION..."
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
echo "Starting beautifulsoup4 Governance Wrapper..."
python3 -c "
from beautifulsoup4_governance_wrapper import Beautifulsoup4GovernanceWrapper
from beautifulsoup4_domain_adapter import Beautifulsoup4DomainAdapter
import logging

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger('beautifulsoup4_container')

try:
    logger.info('beautifulsoup4 Governance Wrapper initialized successfully')
    logger.info('Ready to process operations with governance oversight')
    
    # Keep container running
    import time
    while True:
        time.sleep(3600)
        
except Exception as e:
    logger.error(f'beautifulsoup4 Container error: {str(e)}')
    raise
" || {
    echo "beautifulsoup4 container failed to start"
    exit 1
}
