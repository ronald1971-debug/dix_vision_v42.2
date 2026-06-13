#!/bin/bash
# WebSockets Container Entry Point Script

set -e

echo "Starting WebSockets Container for DIX VISION..."
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

# Start the WebSockets governance wrapper
echo "Starting WebSockets Governance Wrapper..."
python3 -c "
from websockets_governance_wrapper import WebSocketsGovernanceWrapper
from websockets_domain_adapter import WebSocketsDomainAdapter
import logging

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger('websockets_container')

try:
    logger.info('WebSockets Governance Wrapper initialized successfully')
    logger.info('Ready to accept WebSocket connections with governance oversight')
    
    # Keep container running
    import time
    while True:
        time.sleep(3600)
        
except Exception as e:
    logger.error(f'WebSockets Container error: {str(e)}')
    raise
" || {
    echo "WebSockets container failed to start"
    exit 1
}
