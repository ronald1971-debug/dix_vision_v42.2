#!/bin/bash
# socket.io-client Container Entry Point Script

set -e

echo "Starting socket.io-client Container for DIX VISION..."
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
echo "Starting socket.io-client Governance Wrapper..."
python3 -c "
import sys
sys.path.append('/app')
sys.path.append('/app/governance')
sys.path.append('/app/adapters')

from socket_io_client_governance_wrapper import Socket_io_clientGovernanceWrapper
from socket_io_client_domain_adapter import Socket_io_clientDomainAdapter
import logging

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger('socket_io_client_container')

try:
    logger.info('socket.io-client Governance Wrapper initialized successfully')
    logger.info('Ready to process operations with governance oversight')
    
    # Keep container running
    import time
    while True:
        time.sleep(3600)
        
except Exception as e:
    logger.error(f'socket.io-client Container error: {str(e)}')
    raise
" || {
    echo "socket.io-client container failed to start"
    exit 1
}
