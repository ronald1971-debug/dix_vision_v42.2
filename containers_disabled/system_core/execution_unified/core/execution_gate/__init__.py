"""
Execution Unified Core Execution Gate - Execution Gate Infrastructure
Provides execution gate capabilities
NO LAZY LOADING - All components load directly
"""

import logging
from typing import Any, Dict

logger = logging.getLogger(__name__)


class ExecutionGate:
    """Execution gate for controlling trade execution"""

    def __init__(self):
        self._gate_closed = False
        self._gate_rules = {}

    def open_gate(self):
        """Open execution gate"""
        self._gate_closed = False

    def close_gate(self):
        """Close execution gate"""
        self._gate_closed = True

    def is_gate_open(self) -> bool:
        """Check if gate is open"""
        return not self._gate_closed

    def add_gate_rule(self, rule_id: str, rule_config: Dict[str, Any]):
        """Add gate rule"""
        self._gate_rules[rule_id] = rule_config


__all__ = ["ExecutionGate"]
