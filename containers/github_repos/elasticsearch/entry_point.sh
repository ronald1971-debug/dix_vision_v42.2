#!/bin/bash
set -e
echo "Starting Elasticsearch Container for DIX VISION..."
echo "Version: 42.2"
mkdir -p /app/logs /app/data /app/config /app/indices
python3 -c "
import sys
sys.path.append('/app')
sys.path.append('/app/governance')
sys.path.append('/app/adapters')

from elasticsearch_governance_wrapper import ElasticsearchGovernanceWrapper
from elasticsearch_domain_adapter import ElasticsearchDomainAdapter
import logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger('elasticsearch_container')
try:
    wrapper = ElasticsearchGovernanceWrapper(PermissionLevel.READ_ONLY)
    wrapper.initialize_elasticsearch({})
    logger.info('Elasticsearch Governance Wrapper initialized successfully')
    import time
    while True:
        time.sleep(3600)
except Exception as e:
    logger.error(f'Elasticsearch Container error: {str(e)}')
    raise
" || exit 1
