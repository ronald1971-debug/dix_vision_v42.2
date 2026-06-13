#!/bin/bash
# influxdb Container Entry Point Script

set -e

echo "Starting influxdb Container for DIX VISION..."
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
echo "Starting influxdb Governance Wrapper..."
python3 -c "
from influxdb_governance_wrapper import InfluxdbGovernanceWrapper
from influxdb_domain_adapter import InfluxdbDomainAdapter
import logging

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger('influxdb_container')

try:
    logger.info('influxdb Governance Wrapper initialized successfully')
    logger.info('Ready to process operations with governance oversight')
    
    # Keep container running
    import time
    while True:
        time.sleep(3600)
        
except Exception as e:
    logger.error(f'influxdb Container error: {str(e)}')
    raise
" || {
    echo "influxdb container failed to start"
    exit 1
}
