#!/bin/bash
set -e
echo "Starting RabbitMQ Container for DIX VISION..."
echo "Version: 42.2"
mkdir -p /app/logs /app/data /app/config /app/queues
python3 -c "
from rabbitmq_governance_wrapper import RabbitMQGovernanceWrapper
from rabbitmq_domain_adapter import RabbitMQDomainAdapter
import logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger('rabbitmq_container')
try:
    wrapper = RabbitMQGovernanceWrapper(PermissionLevel.READ_ONLY)
    wrapper.initialize_rabbitmq({})
    logger.info('RabbitMQ Governance Wrapper initialized successfully')
    import time
    while True:
        time.sleep(3600)
except Exception as e:
    logger.error(f'RabbitMQ Container error: {str(e)}')
    raise
" || exit 1
