"""
Execution Unified Core Adapters - Adapter Infrastructure
Provides adapter infrastructure and base classes
NO LAZY LOADING - All components load directly
"""

from typing import Dict, List, Optional, Any
import logging

logger = logging.getLogger(__name__)

# Re-export from core.offline for backward compatibility
from execution_unified.core.offline import (
    AdapterState,
    AdapterStatus,
    AdapterConfig,
    LiveAdapterBase,
    BrokerAdapter
)

__all__ = [
    'AdapterState',
    'AdapterStatus', 
    'AdapterConfig',
    'LiveAdapterBase',
    'BrokerAdapter'
]