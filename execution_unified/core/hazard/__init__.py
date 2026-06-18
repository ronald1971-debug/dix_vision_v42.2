"""
Execution Unified Core Hazard - Hazard Detection Infrastructure
Provides core hazard detection capabilities
NO LAZY LOADING - All components load directly
"""

from typing import Dict, List, Optional, Any
import logging

logger = logging.getLogger(__name__)

# Import from async_bus module
from .async_bus import (
    HazardSeverity,
    HazardType,
    HazardEvent,
    get_hazard_bus,
)

__all__ = [
    'HazardSeverity',
    'HazardType',
    'HazardEvent',
    'get_hazard_bus',
]