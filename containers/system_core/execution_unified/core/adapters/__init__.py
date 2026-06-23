"""
Execution Unified Core Adapters - Adapter Infrastructure
Provides adapter infrastructure and base classes
NO LAZY LOADING - All components load directly
"""

import logging

logger = logging.getLogger(__name__)

# Re-export from core.offline for backward compatibility
from execution_unified.core.offline import (
    AdapterConfig,
    AdapterState,
    AdapterStatus,
    BrokerAdapter,
    LiveAdapterBase,
)

__all__ = ["AdapterState", "AdapterStatus", "AdapterConfig", "LiveAdapterBase", "BrokerAdapter"]
