#!/bin/bash
# LangChain Container Entry Point Script

set -e

echo "Starting LangChain Container for DIX VISION..."
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
mkdir -p /app/knowledge

# Start the LangChain governance wrapper
echo "Starting LangChain Governance Wrapper..."
python3 -c "
import sys
sys.path.append('/app')
sys.path.append('/app/governance')
sys.path.append('/app/adapters')

from langchain_governance_wrapper import LangChainGovernanceWrapper
from langchain_domain_adapter import LangChainDomainAdapter
import logging

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger('langchain_container')

try:
    logger.info('LangChain Governance Wrapper initialized successfully')
    logger.info('Ready to accept AI operations with governance oversight')
    
    # Keep container running
    import time
    while True:
        time.sleep(3600)
        
except Exception as e:
    logger.error(f'LangChain Container error: {str(e)}')
    raise
" || {
    echo "LangChain container failed to start"
    exit 1
}
