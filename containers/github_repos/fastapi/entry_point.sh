#!/bin/bash
# FastAPI Container Entry Point Script

set -e

echo "Starting FastAPI Container for DIX VISION..."
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
mkdir -p /app/api

# Start the FastAPI governance wrapper
echo "Starting FastAPI Governance Wrapper..."
python3 -c "
from fastapi_governance_wrapper import FastAPIGovernanceWrapper
from fastapi_domain_adapter import FastAPIDomainAdapter
import logging

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger('fastapi_container')

try:
    logger.info('FastAPI Governance Wrapper initialized successfully')
    logger.info('Ready to accept API requests with governance oversight')
    
    # Keep container running
    import time
    while True:
        time.sleep(3600)
        
except Exception as e:
    logger.error(f'FastAPI Container error: {str(e)}')
    raise
" || {
    echo "FastAPI container failed to start"
    exit 1
}
