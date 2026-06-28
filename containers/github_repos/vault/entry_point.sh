#!/bin/bash
set -e
echo "Starting Vault Container for DIX VISION..."
echo "Version: 42.2"
mkdir -p /app/logs /app/data /app/config /app/secrets
python3 -c "
import sys
sys.path.append('/app')
sys.path.append('/app/governance')
sys.path.append('/app/adapters')

from vault_governance_wrapper import VaultGovernanceWrapper
from vault_domain_adapter import VaultDomainAdapter
import logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger('vault_container')
try:
    wrapper = VaultGovernanceWrapper(PermissionLevel.READ_ONLY)
    wrapper.initialize_vault({})
    logger.info('Vault Governance Wrapper initialized successfully')
    import time
    while True:
        time.sleep(3600)
except Exception as e:
    logger.error(f'Vault Container error: {str(e)}')
    raise
" || exit 1
