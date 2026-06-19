"""
Operator Governance Constitution - Operator Constitution Support
Provides operator constitution capabilities
NO LAZY LOADING - All components load directly
"""

from typing import Dict, List, Optional, Any
import logging

logger = logging.getLogger(__name__)

class OperatorConstitution:
    """Operator constitution for governance operations"""
    
    def __init__(self):
        self._principles = []
        self._rules = {}
        
    def add_principle(self, principle: str):
        """Add constitutional principle"""
        self._principles.append(principle)
        
    def add_rule(self, rule_id: str, rule_text: str):
        """Add constitutional rule"""
        self._rules[rule_id] = rule_text

def get_operator_constitution() -> OperatorConstitution:
    """Get operator constitution instance"""
    return OperatorConstitution()

__all__ = ['OperatorConstitution', 'get_operator_constitution']