"""
Execution Unified Core Hazard - Hazard Detection Infrastructure
Provides core hazard detection capabilities
NO LAZY LOADING - All components load directly
"""

from typing import Dict, List, Optional, Any
import logging
import sys
import os

logger = logging.getLogger(__name__)

# Import from the hazard file (not package)
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
from hazard import (
    HazardSeverity,
    HazardType,
    HazardEvent,
    HazardDetector,
    get_hazard_detector,
    detect_hazard
)

__all__ = [
    'HazardSeverity',
    'HazardType',
    'HazardEvent',
    'HazardDetector',
    'get_hazard_detector',
    'detect_hazard'
]