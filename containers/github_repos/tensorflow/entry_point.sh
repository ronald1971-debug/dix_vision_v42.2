#!/bin/bash
set -e
echo "Starting TensorFlow Container for DIX VISION..."
echo "Version: 42.2"
mkdir -p /app/logs /app/data /app/config /app/models
python3 -c "
from tensorflow_governance_wrapper import TensorFlowGovernanceWrapper
from tensorflow_domain_adapter import TensorFlowDomainAdapter
import logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger('tensorflow_container')
try:
    wrapper = TensorFlowGovernanceWrapper(PermissionLevel.READ_ONLY)
    wrapper.initialize_tensorflow({'thread_count': 4})
    logger.info('TensorFlow Governance Wrapper initialized successfully')
    import time
    while True:
        time.sleep(3600)
except Exception as e:
    logger.error(f'TensorFlow Container error: {str(e)}')
    raise
" || exit 1
