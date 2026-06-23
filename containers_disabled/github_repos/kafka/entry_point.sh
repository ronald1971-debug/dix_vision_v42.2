#!/bin/bash
set -e
echo "Starting Apache Kafka Container for DIX VISION..."
echo "Version: 42.2"
mkdir -p /app/logs /app/data /app/config /app/topics
python3 -c "
import sys
sys.path.append('/app')
sys.path.append('/app/governance')
sys.path.append('/app/adapters')

from kafka_governance_wrapper import KafkaGovernanceWrapper
from kafka_domain_adapter import KafkaDomainAdapter
import logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger('kafka_container')
try:
    wrapper = KafkaGovernanceWrapper(PermissionLevel.READ_ONLY)
    wrapper.initialize_kafka({})
    logger.info('Apache Kafka Governance Wrapper initialized successfully')
    import time
    while True:
        time.sleep(3600)
except Exception as e:
    logger.error(f'Apache Kafka Container error: {str(e)}')
    raise
" || exit 1
