#!/bin/bash
set -e
echo "Starting InfluxDB Container for DIX VISION..."
echo "Version: 42.2"
mkdir -p /app/logs /app/data /app/config /app/measurements
python3 -c "
from influxdb_governance_wrapper import InfluxDBGovernanceWrapper
from influxdb_domain_adapter import InfluxDBDomainAdapter
import logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger('influxdb_container')
try:
    wrapper = InfluxDBGovernanceWrapper(PermissionLevel.READ_ONLY)
    wrapper.initialize_influxdb({})
    logger.info('InfluxDB Governance Wrapper initialized successfully')
    import time
    while True:
        time.sleep(3600)
except Exception as e:
    logger.error(f'InfluxDB Container error: {str(e)}')
    raise
" || exit 1
