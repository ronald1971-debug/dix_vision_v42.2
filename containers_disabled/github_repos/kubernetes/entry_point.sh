#!/bin/bash
set -e
echo "Starting Kubernetes Container for DIX VISION..."
echo "Version: 42.2"
mkdir -p /app/logs /app/data /app/config /app/deployments
python3 -c "
from kubernetes_governance_wrapper import KubernetesGovernanceWrapper
from kubernetes_domain_adapter import KubernetesDomainAdapter
import logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger('kubernetes_container')
try:
    wrapper = KubernetesGovernanceWrapper(PermissionLevel.READ_ONLY)
    wrapper.initialize_kubernetes({})
    logger.info('Kubernetes Governance Wrapper initialized successfully')
    import time
    while True:
        time.sleep(3600)
except Exception as e:
    logger.error(f'Kubernetes Container error: {str(e)}')
    raise
" || exit 1
