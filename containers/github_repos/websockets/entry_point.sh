#!/bin/bash
set -e
echo "Starting WebSockets Container for DIX VISION..."
echo "Version: 42.2"
mkdir -p /app/logs /app/data /app/config /app/connections
python3 -c "
from websockets_governance_wrapper import WebSocketsGovernanceWrapper
from websockets_domain_adapter import WebSocketsDomainAdapter
import logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger('websockets_container')
try:
    wrapper = WebSocketsGovernanceWrapper(PermissionLevel.READ_ONLY)
    wrapper.initialize_websockets({})
    logger.info('WebSockets Governance Wrapper initialized successfully')
    import time
    while True:
        time.sleep(3600)
except Exception as e:
    logger.error(f'WebSockets Container error: {str(e)}')
    raise
" || exit 1
