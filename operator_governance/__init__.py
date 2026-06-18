"""
Operator Governance - Operator-Specific Governance Module
NO LAZY LOADING - All components load directly
"""

from typing import Dict, List, Optional, Any
import logging

from .authority_escalation import AuthorityEscalation

logger = logging.getLogger(__name__)

__all__ = ['AuthorityEscalation']