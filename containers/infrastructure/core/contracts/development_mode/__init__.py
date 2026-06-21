"""
Core Contracts Development Mode
Real implementation for development mode management
"""

from dataclasses import dataclass, field
from enum import Enum
from typing import Dict, Any, List, Optional
import time

class DevelopmentMode(Enum):
    """Development mode enumeration"""
    OFF = "off"
    TRADING_BLOCKED = "trading_blocked"
    TRADING_ALLOWED = "trading_allowed"
    FULL_ACCESS = "full_access"
    DEBUG = "debug"
    TESTING = "testing"
    EXPERIMENTAL = "experimental"

class ModeRestriction(Enum):
    """Mode restriction enumeration"""
    TRADING = "trading"
    EXECUTION = "execution"
    MODIFICATION = "modification"
    CONFIGURATION = "configuration"
    DATA_ACCESS = "data_access"
    NETWORK = "network"
    SYSTEM = "system"
    OPERATIONS = "operations"

# Development mode constants
DEVELOPMENT_MODE_TRADING_BLOCKED = DevelopmentMode.TRADING_BLOCKED
DEVELOPMENT_MODE_TRADING_ALLOWED = DevelopmentMode.TRADING_ALLOWED
DEVELOPMENT_MODE_OFF = DevelopmentMode.OFF
DEVELOPMENT_MODE_DEBUG = DevelopmentMode.DEBUG
DEVELOPMENT_MODE_TESTING = DevelopmentMode.TESTING
DEVELOPMENT_MODE_EXPERIMENTAL = DevelopmentMode.EXPERIMENTAL
DEVELOPMENT_MODE_FULL_ACCESS = DevelopmentMode.FULL_ACCESS

# Policy version
POLICY_VERSION = "1.0.0"

@dataclass
class DevelopmentModePolicy:
    """Development mode policy"""
    policy_id: str = "default"
    mode: DevelopmentMode = None
    restrictions: List[ModeRestriction] = field(default_factory=list)
    enabled: bool = False
    development_enabled: bool = False  # Alias for enabled
    trading_allowed: bool = False  # Trading permission flag
    timestamp: float = field(default_factory=time.time)
    context: Dict[str, Any] = field(default_factory=dict)
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def is_trading_blocked(self) -> bool:
        """Check if trading is blocked"""
        return self.mode == DevelopmentMode.TRADING_BLOCKED
    
    def is_trading_allowed(self) -> bool:
        """Check if trading is allowed"""
        return self.mode == DevelopmentMode.TRADING_ALLOWED
    
    def is_learning_unblocked(self) -> bool:
        """Check if learning is unblocked (for compatibility with operator routes)"""
        return self.mode != DevelopmentMode.TRADING_BLOCKED
    
    def is_trading_unblocked(self) -> bool:
        """Check if trading is unblocked"""
        return self.mode != DevelopmentMode.TRADING_BLOCKED
    
    def has_restriction(self, restriction: ModeRestriction) -> bool:
        """Check if has a specific restriction"""
        return restriction in self.restrictions
    
    def add_restriction(self, restriction: ModeRestriction) -> None:
        """Add a restriction"""
        if restriction not in self.restrictions:
            self.restrictions.append(restriction)
    
    def remove_restriction(self, restriction: ModeRestriction) -> bool:
        """Remove a restriction"""
        if restriction in self.restrictions:
            self.restrictions.remove(restriction)
            return True
        return False
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            "policy_id": self.policy_id,
            "mode": self.mode.value,
            "restrictions": [r.value for r in self.restrictions],
            "enabled": self.enabled,
            "timestamp": self.timestamp,
            "context": self.context,
            "metadata": self.metadata
        }

class DevelopmentModeManager:
    """Manager for development mode"""
    def __init__(self):
        self._policies: Dict[str, DevelopmentModePolicy] = {}
        self._current_mode = DevelopmentMode.OFF
    
    def set_mode(self, mode: DevelopmentMode, justification: str = "") -> bool:
        """Set the development mode"""
        self._current_mode = mode
        return True
    
    def get_current_mode(self) -> DevelopmentMode:
        """Get the current development mode"""
        return self._current_mode
    
    def register_policy(self, policy: DevelopmentModePolicy) -> bool:
        """Register a development mode policy"""
        self._policies[policy.policy_id] = policy
        return True
    
    def get_policy(self, policy_id: str) -> Optional[DevelopmentModePolicy]:
        """Get a specific policy"""
        return self._policies.get(policy_id)
    
    def is_trading_blocked(self) -> bool:
        """Check if trading is blocked in current mode"""
        return self._current_mode == DevelopmentMode.TRADING_BLOCKED

# Global development mode manager
_development_mode_manager: Optional[DevelopmentModeManager] = None

def get_development_mode_manager() -> DevelopmentModeManager:
    """Get the global development mode manager"""
    global _development_mode_manager
    if _development_mode_manager is None:
        _development_mode_manager = DevelopmentModeManager()
    return _development_mode_manager

def set_development_mode(mode: DevelopmentMode, justification: str = "") -> bool:
    """Set the development mode"""
    return get_development_mode_manager().set_mode(mode, justification)

def get_development_mode() -> DevelopmentMode:
    """Get the current development mode"""
    return get_development_mode_manager().get_current_mode()

def get_development_mode_policy() -> Optional[DevelopmentModePolicy]:
    """Get the current development mode policy"""
    manager = get_development_mode_manager()
    # Return the policy matching the current mode, or None if not found
    current_mode = manager.get_current_mode()
    for policy_id, policy in manager._policies.items():
        if policy.mode == current_mode and policy.enabled:
            return policy
    return None

def is_trading_unblocked() -> bool:
    """Check if trading is unblocked in current mode"""
    return get_development_mode_manager().is_trading_allowed()

def is_trading_blocked() -> bool:
    """Check if trading is blocked in current mode"""
    return get_development_mode_manager().is_trading_blocked()

__all__ = [
    "DevelopmentMode",
    "ModeRestriction",
    "POLICY_VERSION",
    "DEVELOPMENT_MODE_TRADING_BLOCKED",
    "DEVELOPMENT_MODE_TRADING_ALLOWED",
    "DEVELOPMENT_MODE_OFF",
    "DEVELOPMENT_MODE_DEBUG",
    "DEVELOPMENT_MODE_TESTING",
    "DEVELOPMENT_MODE_EXPERIMENTAL",
    "DEVELOPMENT_MODE_FULL_ACCESS",
    "DevelopmentModePolicy",
    "DevelopmentModeManager",
    "get_development_mode_manager",
    "set_development_mode",
    "get_development_mode",
    "get_development_mode_policy",
    "is_trading_unblocked",
    "is_trading_blocked"
]