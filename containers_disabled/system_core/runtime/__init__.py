"""
Runtime - Runtime Infrastructure Module
NO LAZY LOADING - All components load directly
"""

import logging

from .contracts import RuntimeContract

logger = logging.getLogger(__name__)

__all__ = ["RuntimeContract"]
