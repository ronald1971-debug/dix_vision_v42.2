"""
Execution Unified Core Adapters Hummingbot - Hummingbot Adapter Support
Provides hummingbot adapter support
NO LAZY LOADING - All components load directly
"""

from typing import Dict, List, Optional, Any
import logging

logger = logging.getLogger(__name__)

class GatewayError(Exception):
    """Gateway error for hummingbot operations"""
    
    def __init__(self, message: str, status_code: Optional[int] = None):
        super().__init__(message)
        self.message = message
        self.status_code = status_code
        
    def __str__(self) -> str:
        status_str = f" (status {self.status_code})" if self.status_code else ""
        return f"GatewayError: {self.message}{status_str}"

__all__ = ['GatewayError']