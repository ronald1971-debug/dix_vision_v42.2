"""
Core Contracts API Source Trust
Real implementation for source trust API contracts
"""

from dataclasses import dataclass, field
from enum import Enum
from typing import Dict, Any, List, Optional
import time

class TrustLevel(Enum):
    """Trust level enumeration"""
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"
    UNKNOWN = "unknown"
    BLOCKED = "blocked"

class SourceKind(Enum):
    """Source kind enumeration"""
    MARKET_DATA = "market_data"
    NEWS = "news"
    SOCIAL = "social"
    ONCHAIN = "onchain"
    EXTERNAL_API = "external_api"
    INTERNAL = "internal"

@dataclass
class SourceTrust:
    """Source trust information"""
    source_id: str
    source_name: str
    source_kind: SourceKind
    trust_level: TrustLevel
    score: float = 0.0
    timestamp: float = field(default_factory=time.time)
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def is_trusted(self) -> bool:
        """Check if source is trusted"""
        return self.trust_level in [TrustLevel.HIGH, TrustLevel.MEDIUM]
    
    def is_blocked(self) -> bool:
        """Check if source is blocked"""
        return self.trust_level == TrustLevel.BLOCKED
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            "source_id": self.source_id,
            "source_name": self.source_name,
            "source_kind": self.source_kind.value,
            "trust_level": self.trust_level.value,
            "score": self.score,
            "timestamp": self.timestamp,
            "metadata": self.metadata
        }

@dataclass
class SourceTrustDemotionRequest:
    """Source trust demotion request information"""
    request_id: str
    source_id: str
    new_level: TrustLevel
    reason: str = ""
    requester: str = ""
    timestamp: float = field(default_factory=time.time)
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            "request_id": self.request_id,
            "source_id": self.source_id,
            "new_level": self.new_level.value,
            "reason": self.reason,
            "requester": self.requester,
            "timestamp": self.timestamp,
            "metadata": self.metadata
        }

@dataclass
class SourceTrustListResponse:
    """Source trust list response information"""
    response_id: str
    sources: List[SourceTrust] = field(default_factory=list)
    total_count: int = 0
    timestamp: float = field(default_factory=time.time)
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            "response_id": self.response_id,
            "sources": [s.to_dict() for s in self.sources],
            "total_count": self.total_count,
            "timestamp": self.timestamp,
            "metadata": self.metadata
        }

@dataclass
class SourceTrustPromotionRequest:
    """Source trust promotion request information"""
    request_id: str
    source_id: str
    new_level: TrustLevel
    reason: str = ""
    requester: str = ""
    timestamp: float = field(default_factory=time.time)
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            "request_id": self.request_id,
            "source_id": self.source_id,
            "new_level": self.new_level.value,
            "reason": self.reason,
            "requester": self.requester,
            "timestamp": self.timestamp,
            "metadata": self.metadata
        }

@dataclass
class SourceTrustPromotionResponse:
    """Source trust promotion response information"""
    response_id: str
    request_id: str
    status: str
    message: str = ""
    timestamp: float = field(default_factory=time.time)
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            "response_id": self.response_id,
            "request_id": self.request_id,
            "status": self.status,
            "message": self.message,
            "timestamp": self.timestamp,
            "metadata": self.metadata
        }

@dataclass
class SourceTrustRow:
    """Source trust row information"""
    source_id: str
    source_name: str
    trust_level: str
    score: float
    status: str
    timestamp: float = field(default_factory=time.time)
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            "source_id": self.source_id,
            "source_name": self.source_name,
            "trust_level": self.trust_level,
            "score": self.score,
            "status": self.status,
            "timestamp": self.timestamp,
            "metadata": self.metadata
        }

class TrustRegistry:
    """Registry for source trust"""
    def __init__(self):
        self._sources: Dict[str, SourceTrust] = {}
        self._sources_by_level: Dict[TrustLevel, List[str]] = {
            level: [] for level in TrustLevel
        }
    
    def register_source(self, source: SourceTrust) -> bool:
        """Register a source"""
        self._sources[source.source_id] = source
        self._sources_by_level[source.trust_level].append(source.source_id)
        return True
    
    def get_source(self, source_id: str) -> Optional[SourceTrust]:
        """Get a specific source"""
        return self._sources.get(source_id)
    
    def get_sources_by_level(self, level: TrustLevel) -> List[SourceTrust]:
        """Get sources by trust level"""
        source_ids = self._sources_by_level.get(level, [])
        return [self._sources[sid] for sid in source_ids if sid in self._sources]
    
    def get_trusted_sources(self) -> List[SourceTrust]:
        """Get all trusted sources"""
        return [s for s in self._sources.values() if s.is_trusted()]

# Global trust registry
_trust_registry: Optional[TrustRegistry] = None

def get_trust_registry() -> TrustRegistry:
    """Get the global trust registry"""
    global _trust_registry
    if _trust_registry is None:
        _trust_registry = TrustRegistry()
    return _trust_registry

__all__ = [
    "TrustLevel",
    "SourceKind",
    "SourceTrust",
    "SourceTrustDemotionRequest",
    "SourceTrustListResponse",
    "SourceTrustPromotionRequest",
    "SourceTrustPromotionResponse",
    "SourceTrustRow",
    "TrustRegistry",
    "get_trust_registry"
]