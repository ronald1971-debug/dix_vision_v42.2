#!/bin/bash
set -e
echo "Starting ClickHouse Container for DIX VISION..."
echo "Version: 42.2"
mkdir -p /app/logs /app/data /app/config /app/queries
python3 -c "
import sys
sys.path.append('/app')
sys.path.append('/app/governance')
sys.path.append('/app/adapters')

from clickhouse_governance_wrapper import ClickHouseGovernanceWrapper
from clickhouse_domain_adapter import ClickHouseDomainAdapter
import logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger('clickhouse_container')
try:
    wrapper = ClickHouseGovernanceWrapper(PermissionLevel.READ_ONLY)
    wrapper.initialize_clickhouse({})
    logger.info('ClickHouse Governance Wrapper initialized successfully')
    import time
    while True:
        time.sleep(3600)
except Exception as e:
    logger.error(f'ClickHouse Container error: {str(e)}')
    raise
" || exit 1
