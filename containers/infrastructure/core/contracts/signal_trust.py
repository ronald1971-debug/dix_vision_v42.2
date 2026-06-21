"""
Core Contracts Signal Trust
Real implementation for signal trust management
"""

from dataclasses import dataclass, field
from enum import Enum
from typing import Dict, Any
import time

class TrustLevel(Enum):
    """Signal trust levels"""
    VERIFIED = "verified"
    TRUSTED = "trusted"
    SUSPICIOUS = "suspicious"
    UNVERIFIED = "unverified"
    BLOCKED = "blocked"

@dataclass
class SignalTrust:
    """Signal trust information"""
    signal_id: str
    source: str
    trust_level: TrustLevel
    confidence_score: float
    last_verified: float = field(default_factory=time.time)
    verification_count: int = 0
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def is_trusted(self) -> bool:
        """Check if signal is considered trusted"""
        return self.trust_level in [TrustLevel.VERIFIED, TrustLevel.TRUSTED]
    
    def requires_approval(self) -> bool:
        """Check if signal requires approval"""
        return self.trust_level in [TrustLevel.SUSPICIOUS, TrustLevel.UNVERIFIED]

# Default trust level for signals without explicit trust configuration
default_cap_for = TrustLevel.UNVERIFIED

def default_signal_trust(signal_id: str, source: str) -> SignalTrust:
    """Create default signal trust configuration"""
    return SignalTrust(
        signal_id=signal_id,
        source=source,
        trust_level=default_cap_for,
        confidence_score=0.5,
        metadata={"configured": False}
)

def verify_signal(signal_trust: SignalTrust) -> bool:
    """Verify and potentially upgrade signal trust"""
    if signal_trust.trust_level == TrustLevel.UNVERIFIED:
        signal_trust.trust_level = TrustLevel.SUSPICIOUS
    return signal_trust.is_trusted()

def clamp_confidence(confidence: float, min_val: float = 0.0, max_val: float = 1.0) -> float:
    """Clamp confidence score to a valid range"""
    return max(min_val, min(max_val, confidence))

def normalize_confidence(confidence: float) -> float:
    """Normalize confidence score to [0, 1] range"""
    return clamp_confidence(confidence, 0.0, 1.0)

__all__ = [
    "TrustLevel",
    "SignalTrust",
    "default_cap_for",
    "default_signal_trust",
    "verify_signal",
    "clamp_confidence",
    "normalize_confidence"
]