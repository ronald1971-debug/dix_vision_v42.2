#!/bin/bash
# Playwright Container Entry Point Script

set -e

echo "Starting Playwright Container for DIX VISION..."
echo "Version: 42.2"
echo "Timestamp: $(date)"

# Load environment variables if .env file exists
if [ -f /app/config/.env ]; then
    echo "Loading environment variables from .env file"
    export $(cat /app/config/.env | grep -v '^#' | xargs)
fi

# Install Playwright browsers if not already installed
echo "Installing Playwright browsers..."
playwright install chromium firefox webkit

# Create necessary directories
mkdir -p /app/logs
mkdir -p /app/data
mkdir -p /app/config
mkdir -p /app/screenshots
mkdir -p /app/sessions

# Start the Playwright governance wrapper
echo "Starting Playwright Governance Wrapper..."
python3 -c "
from playwright_governance_wrapper import PlaywrightGovernanceWrapper
from playwright_domain_adapter import PlaywrightDomainAdapter
import logging

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger('playwright_container')

try:
    # Initialize Playwright with governance oversight
    wrapper = PlaywrightGovernanceWrapper(PermissionLevel.READ_ONLY)
    
    # Configure Playwright
    # wrapper.initialize_playwright({
    #     'browser_type': 'chromium',
    #     'headless': True,
    #     'viewport': {'width': 1920, 'height': 1080}
    # })
    
    logger.info('Playwright Governance Wrapper initialized successfully')
    logger.info('Ready to perform browser automation with governance oversight')
    
    # Keep container running
    import time
    while True:
        time.sleep(3600)
        
except Exception as e:
    logger.error(f'Playwright Container error: {str(e)}')
    raise
" || {
    echo "Playwright container failed to start"
    exit 1
}
