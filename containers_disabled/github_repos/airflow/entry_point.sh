#!/bin/bash
set -e
echo "Starting Airflow Container for DIX VISION..."
echo "Version: 42.2"
mkdir -p /app/logs /app/data /app/config /app/dags /app/plugins
python3 -c "
import sys
sys.path.append('/app')
sys.path.append('/app/governance')
sys.path.append('/app/adapters')

from airflow_governance_wrapper import AirflowGovernanceWrapper
from airflow_domain_adapter import AirflowDomainAdapter
import logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger('airflow_container')
try:
    wrapper = AirflowGovernanceWrapper(PermissionLevel.READ_ONLY)
    wrapper.initialize_airflow({})
    logger.info('Airflow Governance Wrapper initialized successfully')
    import time
    while True:
        time.sleep(3600)
except Exception as e:
    logger.error(f'Airflow Container error: {str(e)}')
    raise
" || exit 1
