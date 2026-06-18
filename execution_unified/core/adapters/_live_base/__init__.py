"""
Execution Unified Core Adapters Live Base - Live Base Adapter Support
Provides live base adapter support
NO LAZY LOADING - All components load directly
"""

from typing import Dict, List, Optional, Any
from dataclasses import dataclass
import logging

# Import from base module
from execution_unified.core.adapters.base import AdapterState

logger = logging.getLogger(__name__)

@dataclass
class LiveAdapterConfig:
    """Configuration for live adapters"""
    api_key: str = ""
    secret_key: str = ""
    sandbox: bool = True
    rate_limit: int = 100
    timeout: int = 30

class LiveAdapterBase:
    """Base class for live trading adapters"""
    
    def __init__(self, config: LiveAdapterConfig = None):
        self._config = config or LiveAdapterConfig()
        self._connected = False
        self._last_activity = 0
        
    async def connect(self) -> bool:
        """Connect to live trading service"""
        self._connected = True
        self._last_activity = __import__('datetime').datetime.now().timestamp_ns() // 1_000_000
        return True
        
    async def disconnect(self):
        """Disconnect from live trading service"""
        self._connected = False
        
    def is_connected(self) -> bool:
        """Check if connected"""
        return self._connected
        
    def get_last_activity(self) -> int:
        """Get last activity timestamp"""
        return self._last_activity

__all__ = ['LiveAdapterConfig', 'LiveAdapterBase', 'AdapterState']