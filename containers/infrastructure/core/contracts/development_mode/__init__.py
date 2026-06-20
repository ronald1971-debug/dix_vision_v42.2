"""
Core Contracts Development Mode
Real implementation for development mode policy
"""

from dataclasses import dataclass
from enum import Enum
from typing import Dict, Any

class DevelopmentMode(Enum):
    """Development mode settings"""
    PRODUCTION = "production"
    DEVELOPMENT = "development"
    TESTING = "testing"

@dataclass
class DevelopmentModePolicy:
    """Policy for development mode"""
    mode: DevelopmentMode = DevelopmentMode.DEVELOPMENT
    allow_placeholders: bool = False
    require_real_implementations: bool = True
    strict_validation: bool = False
    
    def is_production(self) -> bool:
        """Check if in production mode"""
        return self.mode == DevelopmentMode.PRODUCTION

# Global policy instance
_global_policy = DevelopmentModePolicy()

def get_development_mode_policy() -> DevelopmentModePolicy:
    """Get the global development mode policy"""
    return _global_policy

def set_development_mode(mode: DevelopmentMode) -> None:
    """Set the development mode"""
    _global_policy.mode = mode

__all__ = [
    "DevelopmentMode",
    "DevelopmentModePolicy",
    "get_development_mode_policy",
    "set_development_mode"
]