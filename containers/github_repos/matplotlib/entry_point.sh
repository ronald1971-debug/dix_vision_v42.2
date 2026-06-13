#!/bin/bash
set -e
echo "Starting Matplotlib Container for DIX VISION..."
echo "Version: 42.2"
mkdir -p /app/logs /app/data /app/config /app/visualizations
python3 -c "
from matplotlib_governance_wrapper import MatplotlibGovernanceWrapper
from matplotlib_domain_adapter import MatplotlibDomainAdapter
import logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger('matplotlib_container')
try:
    wrapper = MatplotlibGovernanceWrapper(PermissionLevel.READ_ONLY)
    wrapper.initialize_matplotlib({'backend': 'Agg', 'style': 'seaborn'})
    logger.info('Matplotlib Governance Wrapper initialized successfully')
    import time
    while True:
        time.sleep(3600)
except Exception as e:
    logger.error(f'Matplotlib Container error: {str(e)}')
    raise
" || exit 1
