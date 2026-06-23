"""
Execution Unified Core Adapters Uniswap - Uniswap Adapter Support
Provides uniswap adapter support
NO LAZY LOADING - All components load directly
"""

import logging

logger = logging.getLogger(__name__)

# Default Uniswap API URL
DEFAULT_API_URL = "https://api.uniswap.org/v1"


class UniswapConfig:
    """Uniswap configuration"""

    def __init__(self, api_url: str = DEFAULT_API_URL):
        self.api_url = api_url
        self.timeout = 30

    def get_api_url(self) -> str:
        """Get API URL"""
        return self.api_url


# Default Uniswap API URL
DEFAULT_API_URL = "https://api.uniswap.org/v1"
__all__ = ["DEFAULT_API_URL", "UniswapConfig"]
