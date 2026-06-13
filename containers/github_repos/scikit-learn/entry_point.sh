#!/bin/bash
set -e
echo "Starting Scikit-Learn Container for DIX VISION..."
echo "Version: 42.2"
mkdir -p /app/logs /app/data /app/config /app/models
python3 -c "
import sys
sys.path.append('/app')
sys.path.append('/app/governance')
sys.path.append('/app/adapters')

from scikit_learn_governance_wrapper import ScikitLearnGovernanceWrapper
from scikit_learn_domain_adapter import ScikitLearnDomainAdapter
import logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger('sklearn_container')
try:
    wrapper = ScikitLearnGovernanceWrapper(PermissionLevel.READ_ONLY)
    wrapper.initialize_sklearn({'random_seed': 42})
    logger.info('Scikit-Learn Governance Wrapper initialized successfully')
    import time
    while True:
        time.sleep(3600)
except Exception as e:
    logger.error(f'Scikit-Learn Container error: {str(e)}')
    raise
" || exit 1
