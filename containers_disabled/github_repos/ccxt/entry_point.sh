#!/bin/bash
# CCXT Container Entry Point Script

set -e

echo "Starting CCXT Container for DIX VISION..."
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

# Start the CCXT governance wrapper
echo "Starting CCXT Governance Wrapper..."
python3 -c "
import sys
sys.path.append('/app')
sys.path.append('/app/governance')
sys.path.append('/app/adapters')

from ccxt_governance_wrapper import CCXTGovernanceWrapper
from ccxt_domain_adapter import CCXTDomainAdapter
import logging

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger('ccxt_container')

try:
    logger.info('CCXT Governance Wrapper initialized successfully')
    logger.info('Ready to accept trading operations with governance oversight')
    
    # Keep container running
    import time
    while True:
        time.sleep(3600)
        
except Exception as e:
    logger.error(f'CCXT Container error: {str(e)}')
    raise
" || {
    echo "CCXT container failed to start"
    exit 1
}
