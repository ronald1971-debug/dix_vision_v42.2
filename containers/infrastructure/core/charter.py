"""
Core Charter
Real implementation for charter management
"""

from dataclasses import dataclass, field
from enum import Enum
from typing import Dict, Any, List, Optional, Callable
import time

class VoiceKind(Enum):
    """Voice kind enumeration"""
    AUTHORITATIVE = "authoritative"
    COLLABORATIVE = "collaborative"
    ADVISORY = "advisory"
    INFORMATIVE = "informative"
    CRITICAL = "critical"
    EMERGENCY = "emergency"

class CharterStatus(Enum):
    """Charter status enumeration"""
    ACTIVE = "active"
    INACTIVE = "inactive"
    DRAFT = "draft"
    PROPOSED = "proposed"
    APPROVED = "approved"
    REVOKED = "revoked"
    EXPIRED = "expired"
    SUSPENDED = "suspended"

@dataclass
class Voice:
    """Voice information"""
    voice_id: str
    name: str
    kind: VoiceKind
    authority_level: str
    domain: str
    description: str = ""
    priority: int = 0
    enabled: bool = True
    
    def is_authoritative(self) -> bool:
        """Check if voice is authoritative"""
        return self.kind == VoiceKind.AUTHORITATIVE
    
    def is_critical(self) -> bool:
        """Check if voice is critical"""
        return self.kind == VoiceKind.CRITICAL
    
    # Predefined voices as class attributes
    GOVERNANCE = None  # Will be set after class definition
    OPERATOR = None
    TRADER = None
    RISK_MANAGER = None
    SYSTEM = None
    AUDIT = None
    COMPLIANCE = None
    SAFETY = None
    EMERGENCY = None
    OPERATIONS = None
    DYON = None

# Set the class attributes after class definition
Voice.GOVERNANCE = Voice("governance", "Governance Voice", VoiceKind.AUTHORITATIVE, "critical", "governance")
Voice.OPERATOR = Voice("operator", "Operator Voice", VoiceKind.AUTHORITATIVE, "high", "operations")
Voice.TRADER = Voice("trader", "Trader Voice", VoiceKind.COLLABORATIVE, "medium", "trading")
Voice.RISK_MANAGER = Voice("risk_manager", "Risk Manager Voice", VoiceKind.AUTHORITATIVE, "high", "risk")
Voice.SYSTEM = Voice("system", "System Voice", VoiceKind.INFORMATIVE, "medium", "system")
Voice.AUDIT = Voice("audit", "Audit Voice", VoiceKind.CRITICAL, "critical", "governance")
Voice.COMPLIANCE = Voice("compliance", "Compliance Voice", VoiceKind.AUTHORITATIVE, "high", "governance")
Voice.SAFETY = Voice("safety", "Safety Voice", VoiceKind.CRITICAL, "critical", "governance")
Voice.EMERGENCY = Voice("emergency", "Emergency Voice", VoiceKind.EMERGENCY, "critical", "governance")
Voice.OPERATIONS = Voice("operations", "Operations Voice", VoiceKind.COLLABORATIVE, "medium", "operations")
Voice.DYON = Voice("dyon", "DYON Voice", VoiceKind.AUTHORITATIVE, "critical", "evolution")

@dataclass
class Charter:
    """Charter definition"""
    charter_id: str = ""
    name: str = ""
    domain: str = ""
    voices: List[Voice] = field(default_factory=list)
    status: CharterStatus = CharterStatus.ACTIVE
    version: str = "1.0.0"
    created_at: float = field(default_factory=time.time)
    updated_at: float = field(default_factory=time.time)
    metadata: Dict[str, Any] = field(default_factory=dict)
    # Additional fields for governance charter interface
    voice: Optional[Voice] = None
    what: str = ""
    how: List[str] = field(default_factory=list)
    why: List[str] = field(default_factory=list)
    not_do: List[str] = field(default_factory=list)
    accountability: List[str] = field(default_factory=list)
    tools: List[str] = field(default_factory=list)
    
    def __post_init__(self):
        """Post-initialization to set charter_id if not provided"""
        if not self.charter_id:
            if self.domain:
                domain_name = self.domain.domain_id if hasattr(self.domain, 'domain_id') else str(self.domain)
                self.charter_id = f"{domain_name}_charter"
            elif self.voice:
                self.charter_id = f"{self.voice.domain}_charter"
        if self.voice and not self.voices:
            self.voices = [self.voice]
        if not self.name and self.voice:
            self.name = f"Charter for {self.voice.name}"
    
    def is_active(self) -> bool:
        """Check if charter is active"""
        return self.status == CharterStatus.ACTIVE
    
    def has_voice(self, voice_id: str) -> bool:
        """Check if charter has a voice"""
        return any(v.voice_id == voice_id for v in self.voices)
    
    def add_voice(self, voice: Voice) -> None:
        """Add a voice to the charter"""
        if not self.has_voice(voice.voice_id):
            self.voices.append(voice)
            self.updated_at = time.time()
    
    def remove_voice(self, voice_id: str) -> bool:
        """Remove a voice from the charter"""
        original_length = len(self.voices)
        self.voices = [v for v in self.voices if v.voice_id != voice_id]
        if len(self.voices) < original_length:
            self.updated_at = time.time()
            return True
        return False
    
    def get_authoritative_voices(self) -> List[Voice]:
        """Get all authoritative voices"""
        return [v for v in self.voices if v.is_authoritative()]
    
    def get_critical_voices(self) -> List[Voice]:
        """Get all critical voices"""
        return [v for v in self.voices if v.is_critical()]

class CharterRegistry:
    """Registry for charters"""
    def __init__(self):
        self._charters: Dict[str, Charter] = {}
        self._domain_charters: Dict[str, List[str]] = {}
    
    def register_charter(self, charter: Charter) -> bool:
        """Register a charter"""
        # If charter doesn't have charter_id, generate one
        if not charter.charter_id:
            domain_value = charter.domain
            domain_name = domain_value.domain_id if hasattr(domain_value, 'domain_id') else str(domain_value) if domain_value else (charter.voice.domain if charter.voice else "unknown")
            charter.charter_id = f"{domain_name}_charter_{int(time.time())}"
        
        self._charters[charter.charter_id] = charter
        domain_value = charter.domain
        domain_name = domain_value.domain_id if hasattr(domain_value, 'domain_id') else str(domain_value) if domain_value else (charter.voice.domain if charter.voice else "unknown")
        if domain_name not in self._domain_charters:
            self._domain_charters[domain_name] = []
        if charter.charter_id not in self._domain_charters[domain_name]:
            self._domain_charters[domain_name].append(charter.charter_id)
        return True
    
    def get_charter(self, charter_id: str) -> Optional[Charter]:
        """Get a specific charter"""
        return self._charters.get(charter_id)
    
    def get_domain_charters(self, domain: str) -> List[Charter]:
        """Get all charters for a domain"""
        charter_ids = self._domain_charters.get(domain, [])
        return [self._charters[cid] for cid in charter_ids if cid in self._charters]
    
    def get_active_charters(self) -> List[Charter]:
        """Get all active charters"""
        return [c for c in self._charters.values() if c.is_active()]
    
    def revoke_charter(self, charter_id: str) -> bool:
        """Revoke a charter"""
        charter = self.get_charter(charter_id)
        if charter:
            charter.status = CharterStatus.REVOKED
            charter.updated_at = time.time()
            return True
        return False

# Global charter registry
_charter_registry: Optional[CharterRegistry] = None

def get_charter_registry() -> CharterRegistry:
    """Get the global charter registry"""
    global _charter_registry
    if _charter_registry is None:
        _charter_registry = CharterRegistry()
    return _charter_registry

def register_charter(charter: Charter) -> bool:
    """Register a charter in the global registry"""
    return get_charter_registry().register_charter(charter)

def create_charter(charter_id: str, name: str, domain: str) -> Charter:
    """Create a new charter"""
    return Charter(
        charter_id=charter_id,
        name=name,
        domain=domain
    )

def create_voice(voice_id: str, name: str, kind: VoiceKind, authority_level: str, domain: str) -> Voice:
    """Create a new voice"""
    return Voice(
        voice_id=voice_id,
        name=name,
        kind=kind,
        authority_level=authority_level,
        domain=domain
    )

def all_charters() -> List[Charter]:
    """Get all registered charters"""
    return list(get_charter_registry()._charters.values())

__all__ = [
    "VoiceKind",
    "CharterStatus",
    "Voice",
    "Charter",
    "CharterRegistry",
    "get_charter_registry",
    "register_charter",
    "create_charter",
    "create_voice",
    "all_charters"
]