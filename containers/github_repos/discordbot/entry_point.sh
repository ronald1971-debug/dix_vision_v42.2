#!/bin/bash
set -e
echo "Starting DiscordBot Container for DIX VISION..."
echo "Version: 42.2"
mkdir -p /app/logs /app/data /app/config /app/messages
python3 -c "
from discordbot_governance_wrapper import DiscordBotGovernanceWrapper
from discordbot_domain_adapter import DiscordBotDomainAdapter
import logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger('discordbot_container')
try:
    wrapper = DiscordBotGovernanceWrapper(PermissionLevel.READ_ONLY)
    wrapper.initialize_discordbot({})
    logger.info('DiscordBot Governance Wrapper initialized successfully')
    import time
    while True:
        time.sleep(3600)
except Exception as e:
    logger.error(f'DiscordBot Container error: {str(e)}')
    raise
" || exit 1
