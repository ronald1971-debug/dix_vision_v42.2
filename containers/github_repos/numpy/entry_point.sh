#!/bin/bash
# NumPy Container Entry Point Script

set -e

echo "Starting NumPy Container for DIX VISION..."
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
mkdir -p /app/computations

# Start the NumPy governance wrapper
echo "Starting NumPy Governance Wrapper..."
python3 -c "
import sys
sys.path.append('/app')
sys.path.append('/app/governance')
sys.path.append('/app/adapters')

from numpy_governance_wrapper import NumPyGovernanceWrapper
from numpy_domain_adapter import NumPyDomainAdapter
import logging

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger('numpy_container')

try:
    # Initialize NumPy with governance oversight
    wrapper = NumPyGovernanceWrapper(PermissionLevel.READ_ONLY)
    
    # Configure NumPy
    wrapper.initialize_numpy({
        'invalid': 'warn',
        'divide': 'warn',
        'overflow': 'warn',
        'underflow': 'ignore'
    })
    
    logger.info('NumPy Governance Wrapper initialized successfully')
    logger.info('Ready to perform numerical computations with governance oversight')
    
    # Keep container running
    import time
    while True:
        time.sleep(3600)
        
except Exception as e:
    logger.error(f'NumPy Container error: {str(e)}')
    raise
" || {
    echo "NumPy container failed to start"
    exit 1
}
