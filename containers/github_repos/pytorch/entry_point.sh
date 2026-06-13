#!/bin/bash
set -e
echo "Starting PyTorch Container for DIX VISION..."
echo "Version: 42.2"
mkdir -p /app/logs /app/data /app/config /app/models
python3 -c "
from pytorch_governance_wrapper import PyTorchGovernanceWrapper
from pytorch_domain_adapter import PyTorchDomainAdapter
import logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger('pytorch_container')
try:
    wrapper = PyTorchGovernanceWrapper(PermissionLevel.READ_ONLY)
    wrapper.initialize_pytorch({})
    logger.info('PyTorch Governance Wrapper initialized successfully')
    import time
    while True:
        time.sleep(3600)
except Exception as e:
    logger.error(f'PyTorch Container error: {str(e)}')
    raise
" || exit 1
