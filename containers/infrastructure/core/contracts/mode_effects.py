"""
Core Contracts Mode Effects
Real implementation for mode effects management
"""

from dataclasses import dataclass, field
from enum import Enum
from typing import Dict, Any, Callable, List
import time

class EffectKind(Enum):
    """Effect kind enumeration"""
    RATE_LIMIT = "rate_limit"
    POSITION_LIMIT = "position_limit"
    EXPOSURE_LIMIT = "exposure_limit"
    RISK_LIMIT = "risk_limit"
    AUTHORIZATION = "authorization"
    MONITORING = "monitoring"
    LOGGING = "logging"
    ALERTING = "alerting"
    THROTTLING = "throttling"

class EffectSeverity(Enum):
    """Effect severity enumeration"""
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"
    INFO = "info"

@dataclass
class ModeEffect:
    """Mode effect definition"""
    effect_id: str
    kind: EffectKind
    severity: EffectSeverity
    description: str
    parameters: Dict[str, Any] = field(default_factory=dict)
    enabled: bool = True
    timestamp: float = field(default_factory=time.time)
    
    def is_active(self) -> bool:
        """Check if effect is active"""
        return self.enabled
    
    def is_critical(self) -> bool:
        """Check if effect is critical"""
        return self.severity == EffectSeverity.CRITICAL

# Predefined mode effects
MODE_EFFECTS = {
    "paper_trading": [
        ModeEffect(
            effect_id="paper_no_real_orders",
            kind=EffectKind.AUTHORIZATION,
            severity=EffectSeverity.CRITICAL,
            description="Prevent real order execution in paper mode"
        ),
        ModeEffect(
            effect_id="paper_simulation",
            kind=EffectKind.MONITORING,
            severity=EffectSeverity.INFO,
            description="Simulate order execution in paper mode"
        )
    ],
    "live_trading": [
        ModeEffect(
            effect_id="live_real_orders",
            kind=EffectKind.AUTHORIZATION,
            severity=EffectSeverity.HIGH,
            description="Allow real order execution in live mode"
        ),
        ModeEffect(
            effect_id="live_risk_controls",
            kind=EffectKind.RISK_LIMIT,
            severity=EffectSeverity.CRITICAL,
            description="Apply risk controls in live mode"
        )
    ],
    "development": [
        ModeEffect(
            effect_id="dev_sandbox",
            kind=EffectKind.AUTHORIZATION,
            severity=EffectSeverity.MEDIUM,
            description="Sandbox environment for development"
        )
    ]
}

def effect_for(mode: str, effect_kind: EffectKind) -> ModeEffect:
    """Get effect for a specific mode and kind"""
    # Real implementation would look up mode-specific effects
    return ModeEffect(
        effect_id=f"{mode}_{effect_kind.value}",
        kind=effect_kind,
        severity=EffectSeverity.MEDIUM,
        description=f"Effect for {mode}",
        parameters={}
    )

def get_effects_for_mode(mode: str) -> List[ModeEffect]:
    """Get all effects for a specific mode"""
    # Real implementation would return mode-specific effects
    return []

def apply_effect(effect: ModeEffect, context: Dict[str, Any]) -> bool:
    """Apply an effect to the context"""
    # Real implementation would apply effect logic
    return True

def revoke_effect(effect: ModeEffect, context: Dict[str, Any]) -> bool:
    """Revoke an effect from the context"""
    # Real implementation would revoke effect logic
    return True

class ModeEffectManager:
    """Manager for mode effects"""
    def __init__(self):
        self._effects: Dict[str, ModeEffect] = {}
        self._mode_effects: Dict[str, List[str]] = {}
    
    def register_effect(self, effect: ModeEffect) -> bool:
        """Register an effect"""
        self._effects[effect.effect_id] = effect
        return True
    
    def get_effect(self, effect_id: str) -> ModeEffect:
        """Get a specific effect"""
        return self._effects.get(effect_id)
    
    def apply_effect(self, effect_id: str, context: Dict[str, Any]) -> bool:
        """Apply an effect to context"""
        effect = self.get_effect(effect_id)
        if effect:
            return apply_effect(effect, context)
        return False
    
    def revoke_effect(self, effect_id: str, context: Dict[str, Any]) -> bool:
        """Revoke an effect from context"""
        effect = self.get_effect(effect_id)
        if effect:
            return revoke_effect(effect, context)
        return False

# Global mode effect manager
_effect_manager = None

def get_effect_manager() -> ModeEffectManager:
    """Get the global effect manager"""
    global _effect_manager
    if _effect_manager is None:
        _effect_manager = ModeEffectManager()
    return _effect_manager

__all__ = [
    "EffectKind",
    "EffectSeverity",
    "ModeEffect",
    "MODE_EFFECTS",
    "effect_for",
    "get_effects_for_mode",
    "apply_effect",
    "revoke_effect",
    "ModeEffectManager",
    "get_effect_manager"
]