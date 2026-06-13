#!/bin/bash
set -e
echo "Starting Etcd Container for DIX VISION..."
echo "Version: 42.2"
mkdir -p /app/logs /app/data /app/config /app/kv
python3 -c "
from etcd_governance_wrapper import EtcdGovernanceWrapper
from etcd_domain_adapter import EtcdDomainAdapter
import logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger('etcd_container')
try:
    wrapper = EtcdGovernanceWrapper(PermissionLevel.READ_ONLY)
    wrapper.initialize_etcd({})
    logger.info('Etcd Governance Wrapper initialized successfully')
    import time
    while True:
        time.sleep(3600)
except Exception as e:
    logger.error(f'Etcd Container error: {str(e)}')
    raise
" || exit 1
