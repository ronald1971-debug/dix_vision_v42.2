#!/bin/bash
# Pandas Container Entry Point Script

set -e

echo "Starting Pandas Container for DIX VISION..."
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
mkdir -p /app/datasets

# Start the Pandas governance wrapper
echo "Starting Pandas Governance Wrapper..."
python3 -c "
import sys
sys.path.append('/app')
sys.path.append('/app/governance')
sys.path.append('/app/adapters')

from pandas_governance_wrapper import PandasGovernanceWrapper
from pandas_domain_adapter import PandasDomainAdapter
import logging

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger('pandas_container')

try:
    # Initialize Pandas with governance oversight
    wrapper = PandasGovernanceWrapper(PermissionLevel.READ_ONLY)
    
    # Configure Pandas
    wrapper.initialize_pandas({
        'max_rows': 100,
        'max_columns': 20,
        'precision': 6,
        'chained_assignment': 'warn'
    })
    
    logger.info('Pandas Governance Wrapper initialized successfully')
    logger.info('Ready to perform data analysis with governance oversight')
    
    # Keep container running
    import time
    while True:
        time.sleep(3600)
        
except Exception as e:
    logger.error(f'Pandas Container error: {str(e)}')
    raise
" || {
    echo "Pandas container failed to start"
    exit 1
}
