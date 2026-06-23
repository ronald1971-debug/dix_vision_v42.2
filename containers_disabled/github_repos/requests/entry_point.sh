#!/bin/bash
# Requests Container Entry Point Script

set -e

echo "Starting Requests Container for DIX VISION..."
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
mkdir -p /app/sessions

# Start the Requests governance wrapper
echo "Starting Requests Governance Wrapper..."
python3 -c "
import sys
sys.path.append('/app')
sys.path.append('/app/governance')
sys.path.append('/app/adapters')

from base_external_repo_wrapper import PermissionLevel
from requests_governance_wrapper import RequestsGovernanceWrapper
from requests_domain_adapter import RequestsDomainAdapter
import logging

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger('requests_container')

try:
    # Initialize Requests with governance oversight
    wrapper = RequestsGovernanceWrapper(PermissionLevel.READ_ONLY)
    
    # Configure Requests
    # wrapper.initialize_requests({
    #     'headers': {'Accept': 'application/json'},
    #     'timeout': 30,
    #     'max_redirects': 5
    # })
    
    logger.info('Requests Governance Wrapper initialized successfully')
    logger.info('Ready to process HTTP requests with governance oversight')
    
    # Keep container running
    import time
    while True:
        time.sleep(3600)
        
except Exception as e:
    logger.error(f'Requests Container error: {str(e)}')
    raise
" || {
    echo "Requests container failed to start"
    exit 1
}
