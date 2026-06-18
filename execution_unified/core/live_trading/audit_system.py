"""
Execution Unified Core Live Trading Audit System
Provides audit system for live trading
NO LAZY LOADING - All components load directly
"""

from typing import Dict, List, Optional, Any
import logging

logger = logging.getLogger(__name__)

class AuditSystem:
    """Audit system for live trading operations"""

    def __init__(self):
        self._audit_log = []
        self._active = True

    def log_execution(self, execution_data: Dict[str, Any]) -> str:
        """Log execution for audit"""
        audit_id = f"audit_{len(self._audit_log)}"
        audit_entry = {
            "audit_id": audit_id,
            "execution_data": execution_data,
            "timestamp": __import__('datetime').datetime.now().isoformat()
        }
        self._audit_log.append(audit_entry)
        return audit_id

    def get_audit_log(self) -> List[Dict[str, Any]]:
        """Get audit log"""
        return self._audit_log.copy()

    def is_active(self) -> bool:
        """Check if audit system is active"""
        return self._active

    def enable(self):
        """Enable audit system"""
        self._active = True

_audit_system = None

def get_live_trading_audit_system() -> AuditSystem:
    """Get live trading audit system instance"""
    global _audit_system
    if _audit_system is None:
        _audit_system = AuditSystem()
    return _audit_system

__all__ = ['AuditSystem', 'get_live_trading_audit_system']