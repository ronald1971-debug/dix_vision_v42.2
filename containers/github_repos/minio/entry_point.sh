#!/bin/bash
set -e
echo "Starting MinIO Container for DIX VISION..."
echo "Version: 42.2"
mkdir -p /app/logs /app/data /app/config /app/buckets
python3 -c "
from minio_governance_wrapper import MinIOGovernanceWrapper
from minio_domain_adapter import MinIODomainAdapter
import logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger('minio_container')
try:
    wrapper = MinIOGovernanceWrapper(PermissionLevel.READ_ONLY)
    wrapper.initialize_minio({})
    logger.info('MinIO Governance Wrapper initialized successfully')
    import time
    while True:
        time.sleep(3600)
except Exception as e:
    logger.error(f'MinIO Container error: {str(e)}')
    raise
" || exit 1
