"""
Runtime - Runtime Infrastructure Module
NO LAZY LOADING - All components load directly
"""

from typing import Dict, List, Optional, Any
import logging

from .contracts import RuntimeContract

logger = logging.getLogger(__name__)

__all__ = ['RuntimeContract']