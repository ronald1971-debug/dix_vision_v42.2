"""
Execution Unified Core Paper Trading Paper Only Enforcer - Paper Trading Constraints
Provides paper-only enforcement for trading operations
NO LAZY LOADING - All components load directly
"""

import logging

logger = logging.getLogger(__name__)


class PaperOnlyEnforcer:
    """Paper only enforcement for trading operations"""

    def __init__(self):
        self._paper_only_mode = False
        self._allowed_operations = []

    def enable_paper_only_mode(self):
        """Enable paper-only trading mode"""
        self._paper_only_mode = True

    def disable_paper_only_mode(self):
        """Disable paper-only trading mode"""
        self._paper_only_mode = False

    def is_paper_only_mode(self) -> bool:
        """Check if paper-only mode is enabled"""
        return self._paper_only_mode

    def check_operation_allowed(self, operation_type: str) -> bool:
        """Check if operation is allowed in current mode"""
        if self._paper_only_mode:
            return operation_type in self._allowed_operations
        return True

    def add_allowed_operation(self, operation_type: str):
        """Add operation to allowed list"""
        self._allowed_operations.append(operation_type)


# Global instance
_paper_only_enforcer = None


def get_paper_only_enforcer() -> PaperOnlyEnforcer:
    """Get paper only enforcer instance"""
    global _paper_only_enforcer
    if _paper_only_enforcer is None:
        _paper_only_enforcer = PaperOnlyEnforcer()
    return _paper_only_enforcer


__all__ = ["PaperOnlyEnforcer", "get_paper_only_enforcer"]
