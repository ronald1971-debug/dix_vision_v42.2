"""
Execution Unified Core Adapters Base - Base Adapter Support
Provides base adapter support
NO LAZY LOADING - All components load directly
"""

import logging
from dataclasses import dataclass
from enum import Enum

logger = logging.getLogger(__name__)


class AdapterStatus(Enum):
    """Adapter status enumeration"""

    INITIALIZED = "initialized"
    CONNECTED = "connected"
    DISCONNECTED = "disconnected"
    ERROR = "error"


@dataclass
class AdapterState:
    """Adapter state data structure"""

    status: AdapterStatus = AdapterStatus.INITIALIZED
    error_message: str = ""
    last_activity: int = 0
    connection_attempts: int = 0

    def __post_init__(self):
        if self.last_activity == 0:
            self.last_activity = __import__("datetime").datetime.now().timestamp_ns() // 1_000_000


class BaseAdapter:
    """Base adapter class for all trading adapters"""

    def __init__(self, adapter_id: str = ""):
        self._adapter_id = adapter_id
        self._initialized = False
        self._state = AdapterState()

    def initialize(self) -> bool:
        """Initialize adapter"""
        self._initialized = True
        self._state.status = AdapterStatus.INITIALIZED
        return True

    def is_initialized(self) -> bool:
        """Check if initialized"""
        return self._initialized

    def get_state(self) -> AdapterState:
        """Get adapter state"""
        return self._state

    def set_state(self, state: AdapterState):
        """Set adapter state"""
        self._state = state

    @classmethod
    def register(cls, subclass):
        """Register a subclass for virtual inheritance"""
        return subclass


# BrokerAdapter alias for compatibility
BrokerAdapter = BaseAdapter

__all__ = ["AdapterStatus", "AdapterState", "BaseAdapter", "BrokerAdapter"]
