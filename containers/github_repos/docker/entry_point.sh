#!/bin/bash
set -e
echo "Starting Docker Container for DIX VISION..."
echo "Version: 42.2"
mkdir -p /app/logs /app/data /app/config /app/containers
python3 -c "
from docker_governance_wrapper import DockerGovernanceWrapper
from docker_domain_adapter import DockerDomainAdapter
import logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger('docker_container')
try:
    wrapper = DockerGovernanceWrapper(PermissionLevel.READ_ONLY)
    wrapper.initialize_docker({})
    logger.info('Docker Governance Wrapper initialized successfully')
    import time
    while True:
        time.sleep(3600)
except Exception as e:
    logger.error(f'Docker Container error: {str(e)}')
    raise
" || exit 1
