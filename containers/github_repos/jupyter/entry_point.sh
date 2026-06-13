#!/bin/bash
set -e
echo "Starting Jupyter Container for DIX VISION..."
echo "Version: 42.2"
mkdir -p /app/logs /app/data /app/config /app/notebooks
python3 -c "
from jupyter_governance_wrapper import JupyterGovernanceWrapper
from jupyter_domain_adapter import JupyterDomainAdapter
import logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger('jupyter_container')
try:
    wrapper = JupyterGovernanceWrapper(PermissionLevel.READ_ONLY)
    wrapper.initialize_jupyter({})
    logger.info('Jupyter Governance Wrapper initialized successfully')
    import time
    while True:
        time.sleep(3600)
except Exception as e:
    logger.error(f'Jupyter Container error: {str(e)}')
    raise
" || exit 1
