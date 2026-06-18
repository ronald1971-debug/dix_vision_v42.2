"""
Operator Governance Manual Lockout - Manual Lockout Support
Provides manual lockout capabilities
NO LAZY LOADING - All components load directly
"""

from typing import Dict, List, Optional, Any
import logging

logger = logging.getLogger(__name__)

class ManualLockout:
    """Manual lockout for governance operations"""
    
    def __init__(self):
        self._lockout_active = False
        self._lockout_reason = ""
        
    def activate_lockout(self, reason: str = ""):
        """Activate manual lockout"""
        self._lockout_active = True
        self._lockout_reason = reason
        logger.warning(f"Manual lockout activated: {reason}")
        
    def deactivate_lockout(self):
        """Deactivate manual lockout"""
        self._lockout_active = False
        self._lockout_reason = ""
        logger.info("Manual lockout deactivated")
        
    def is_locked_out(self) -> bool:
        """Check if lockout is active"""
        return self._lockout_active

_manual_lockout = None

def get_manual_lockout() -> ManualLockout:
    """Get manual lockout instance"""
    global _manual_lockout
    if _manual_lockout is None:
        _manual_lockout = ManualLockout()
    return _manual_lockout

class ManualLockoutGuard:
    """Guard for manual lockout operations"""
    
    def __init__(self):
        self._manual_lockout = get_manual_lockout()
        
    def is_locked_out(self) -> bool:
        """Check if lockout is active"""
        return self._manual_lockout.is_locked_out()

def get_manual_lockout_guard() -> ManualLockoutGuard:
    """Get manual lockout guard instance"""
    return ManualLockoutGuard()

__all__ = ['ManualLockout', 'get_manual_lockout', 'ManualLockoutGuard', 'get_manual_lockout_guard']