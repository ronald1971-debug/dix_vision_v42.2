"""
Core Coherence System Intent
Real implementation for system intent management
"""

import time
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Dict, List, Optional

# Intent key constants
INTENT_KEY_FOCUS = "focus"
INTENT_KEY_PRIORITY = "priority"
INTENT_KEY_HORIZON = "horizon"
INTENT_KEY_OBJECTIVE = "objective"
INTENT_KEY_SCOPE = "scope"
INTENT_KEY_REASON = "reason"
INTENT_KEY_REQUESTOR = "requestor"
INTENT_KEY_CONDITIONS = "conditions"
INTENT_KEY_RISK_MODE = "risk_mode"
INTENT_KEY_VERSION = "version"
INTENT_TRANSITION_KIND = "transition_kind"
INTENT_KIND_FOCUS = "focus"

# System intent constants
SYSTEM_INTENT_VERSION = "1.0.0"


class IntentKind(Enum):
    """System intent kinds"""

    MARKET_OPERATION = "market_operation"
    SYSTEM_MAINTENANCE = "system_maintenance"
    LEARNING_OPERATION = "learning_operation"
    EVOLUTION_CHANGE = "evolution_change"
    GOVERNANCE_ACTION = "governance_action"


@dataclass
class SystemIntent:
    """System intent definition"""

    intent_id: str
    kind: IntentKind
    priority: int
    description: str
    parameters: Dict[str, Any] = field(default_factory=dict)
    created_at: float = field(default_factory=time.time)
    expires_at: float = 0.0

    def is_expired(self) -> bool:
        """Check if intent has expired"""
        return self.expires_at > 0 and time.time() > self.expires_at

    def is_valid(self) -> bool:
        """Check if intent is valid"""
        return not self.is_expired()


@dataclass
class IntentConflict:
    """Intent conflict information"""

    intent_id_1: str
    intent_id_2: str
    conflict_type: str
    severity: str = "medium"
    resolution: str = ""

    def is_resolved(self) -> bool:
        """Check if conflict is resolved"""
        return bool(self.resolution)


class IntentManager:
    """Manager for system intents and conflict resolution"""

    def __init__(self):
        self._intents: Dict[str, SystemIntent] = {}
        self._conflicts: List[IntentConflict] = []

    def register_intent(self, intent: SystemIntent) -> bool:
        """Register a system intent"""
        self._intents[intent.intent_id] = intent
        return True

    def get_intent(self, intent_id: str) -> SystemIntent:
        """Get a specific intent"""
        return self._intents.get(intent_id)

    def resolve_conflicts(self) -> List[IntentConflict]:
        """Resolve intent conflicts"""
        return self._conflicts.copy()

    def get_active_intents(self) -> List[SystemIntent]:
        """Get all active non-expired intents"""
        return [intent for intent in self._intents.values() if intent.is_valid()]


# Global intent manager
_intent_manager: Optional[IntentManager] = None


def get_intent_manager() -> IntentManager:
    """Get the global intent manager"""
    global _intent_manager
    if _intent_manager is None:
        _intent_manager = IntentManager()
    return _intent_manager


def encode_focus(focus_value: str) -> str:
    """Encode a focus value for system intent"""
    return f"focus:{focus_value}"


def decode_focus(encoded_focus: str) -> str:
    """Decode a focus value from system intent"""
    if encoded_focus.startswith("focus:"):
        return encoded_focus[6:]  # Remove "focus:" prefix
    return encoded_focus


__all__ = [
    "INTENT_KEY_FOCUS",
    "INTENT_KEY_PRIORITY",
    "INTENT_KEY_HORIZON",
    "INTENT_KEY_OBJECTIVE",
    "INTENT_KEY_SCOPE",
    "INTENT_KEY_REASON",
    "INTENT_KEY_REQUESTOR",
    "INTENT_KEY_CONDITIONS",
    "INTENT_KEY_RISK_MODE",
    "INTENT_KEY_VERSION",
    "INTENT_TRANSITION_KIND",
    "INTENT_KIND_FOCUS",
    "SYSTEM_INTENT_VERSION",
    "IntentKind",
    "SystemIntent",
    "IntentConflict",
    "IntentManager",
    "get_intent_manager",
    "encode_focus",
    "decode_focus",
]
