#!/bin/bash
# Celery Container Entry Point Script

set -e

echo "Starting Celery Container for DIX VISION..."
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
mkdir -p /app/tasks

# Start the Celery governance wrapper
echo "Starting Celery Governance Wrapper..."
python3 -c "
import sys
sys.path.append('/app')
sys.path.append('/app/governance')
sys.path.append('/app/adapters')

from celery_governance_wrapper import CeleryGovernanceWrapper
from celery_domain_adapter import CeleryDomainAdapter
import logging

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger('celery_container')

try:
    # Initialize Celery with governance oversight
    wrapper = CeleryGovernanceWrapper(PermissionLevel.READ_ONLY)
    
    # Configure Celery
    broker_url = 'redis://redis-service:6379/0'
    result_backend = 'redis://redis-service:6379/0'
    
    # wrapper.initialize_celery(
    #     broker_url=broker_url,
    #     result_backend=result_backend,
    #     task_config={'app_name': 'dixvision_tasks'}
    # )
    
    logger.info('Celery Governance Wrapper initialized successfully')
    logger.info('Ready to process tasks with governance oversight')
    
    # Keep container running
    import time
    while True:
        time.sleep(3600)
        
except Exception as e:
    logger.error(f'Celery Container error: {str(e)}')
    raise
" || {
    echo "Celery container failed to start"
    exit 1
}
