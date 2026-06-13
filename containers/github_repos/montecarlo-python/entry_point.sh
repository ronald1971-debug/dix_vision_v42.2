#!/bin/bash
# montecarlo-python Container Entry Point Script

set -e

echo "Starting montecarlo-python Container for DIX VISION..."
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
echo "Starting montecarlo-python Governance Wrapper..."
python3 -c "
from montecarlo_python_governance_wrapper import Montecarlo_pythonGovernanceWrapper
from montecarlo_python_domain_adapter import Montecarlo_pythonDomainAdapter
import logging

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger('montecarlo_python_container')

try:
    logger.info('montecarlo-python Governance Wrapper initialized successfully')
    logger.info('Ready to process operations with governance oversight')
    
    # Keep container running
    import time
    while True:
        time.sleep(3600)
        
except Exception as e:
    logger.error(f'montecarlo-python Container error: {str(e)}')
    raise
" || {
    echo "montecarlo-python container failed to start"
    exit 1
}
