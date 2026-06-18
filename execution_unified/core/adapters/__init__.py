"""
Execution Unified Core Adapters - Adapter Infrastructure
Provides adapter interfaces for external system integration
NO LAZY LOADING - All components load directly
"""

from typing import Dict, List, Optional, Any
from dataclasses import dataclass
from enum import Enum
import logging

logger = logging.getLogger(__name__)


class AdapterType(Enum):
    """Adapter type enumeration"""
    EXCHANGE = "exchange"
    DATA_SOURCE = "data_source"
    EXECUTION = "execution"
    MONITORING = "monitoring"
    GOVERNANCE = "governance"


@dataclass
class AdapterConfig:
    """Adapter configuration"""
    adapter_type: AdapterType
    name: str
    enabled: bool = True
    config_params: Dict[str, Any] = None


class BaseAdapter:
    """Base adapter class for all adapters"""
    
    def __init__(self, config: AdapterConfig):
        self._config = config
        self._connected = False
        
    async def connect(self) -> bool:
        """Connect adapter"""
        self._connected = True
        logger.info(f"Adapter {self._config.name} connected")
        return True
    
    async def disconnect(self) -> bool:
        """Disconnect adapter"""
        self._connected = False
        logger.info(f"Adapter {self._config.name} disconnected")
        return True
    
    def is_connected(self) -> bool:
        """Check if adapter is connected"""
        return self._connected


class AdapterRegistry:
    """Registry for managing adapters"""
    
    def __init__(self):
        self._adapters: Dict[str, BaseAdapter] = {}
        
    def register_adapter(self, adapter: BaseAdapter) -> bool:
        """Register an adapter"""
        self._adapters[adapter._config.name] = adapter
        logger.info(f"Registered adapter: {adapter._config.name}")
        return True
    
    def get_adapter(self, name: str) -> Optional[BaseAdapter]:
        """Get adapter by name"""
        return self._adapters.get(name)
    
    def get_all_adapters(self) -> List[BaseAdapter]:
        """Get all registered adapters"""
        return list(self._adapters.values())


# Global adapter registry
_adapter_registry = None

def get_adapter_registry() -> AdapterRegistry:
    """Get global adapter registry instance"""
    global _adapter_registry
    if _adapter_registry is None:
        _adapter_registry = AdapterRegistry()
    return _adapter_registry


__all__ = [
    'AdapterType',
    'AdapterConfig',
    'BaseAdapter',
    'AdapterRegistry',
    'get_adapter_registry'
]