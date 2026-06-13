#!/bin/bash
set -e
echo "Starting Scrapy Container for DIX VISION..."
echo "Version: 42.2"
mkdir -p /app/logs /app/data /app/config /app/spiders
python3 -c "
from scrapy_governance_wrapper import ScrapyGovernanceWrapper
from scrapy_domain_adapter import ScrapyDomainAdapter
import logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger('scrapy_container')
try:
    wrapper = ScrapyGovernanceWrapper(PermissionLevel.READ_ONLY)
    wrapper.initialize_scrapy({})
    logger.info('Scrapy Governance Wrapper initialized successfully')
    import time
    while True:
        time.sleep(3600)
except Exception as e:
    logger.error(f'Scrapy Container error: {str(e)}')
    raise
" || exit 1
