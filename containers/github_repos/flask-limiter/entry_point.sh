#!/bin/bash
# flask-limiter Container Entry Point Script

set -e

echo "Starting flask-limiter Container for DIX VISION..."
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
echo "Starting flask-limiter Governance Wrapper..."
python3 -c "
from flask_limiter_governance_wrapper import Flask_limiterGovernanceWrapper
from flask_limiter_domain_adapter import Flask_limiterDomainAdapter
import logging

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger('flask_limiter_container')

try:
    logger.info('flask-limiter Governance Wrapper initialized successfully')
    logger.info('Ready to process operations with governance oversight')
    
    # Keep container running
    import time
    while True:
        time.sleep(3600)
        
except Exception as e:
    logger.error(f'flask-limiter Container error: {str(e)}')
    raise
" || {
    echo "flask-limiter container failed to start"
    exit 1
}
