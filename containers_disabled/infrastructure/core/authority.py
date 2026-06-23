"""
Core Authority
Real implementation for domain authority management
"""

import time
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Dict, List, Optional


class DomainKind(Enum):
    """Domain kind enumeration"""

    SYSTEM = "system"
    GOVERNANCE = "governance"
    TRADING = "trading"
    RISK = "risk"
    MARKET_DATA = "market_data"
    EXECUTION = "execution"
    INFRASTRUCTURE = "infrastructure"
    UI = "ui"
    ANALYTICS = "analytics"
    OPERATIONS = "operations"


class AuthorityLevel(Enum):
    """Authority level enumeration"""

    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"
    ADVISORY = "advisory"


@dataclass
class Domain:
    """Domain authority information"""

    domain_id: str
    name: str
    kind: DomainKind
    authority_level: AuthorityLevel
    description: str = ""
    owners: List[str] = field(default_factory=list)
    stewards: List[str] = field(default_factory=list)
    boundaries: Dict[str, Any] = field(default_factory=dict)
    constraints: List[str] = field(default_factory=list)
    capabilities: List[str] = field(default_factory=list)
    created_at: float = field(default_factory=time.time)
    updated_at: float = field(default_factory=time.time)

    def is_critical(self) -> bool:
        """Check if domain is critical"""
        return self.authority_level == AuthorityLevel.CRITICAL

    def has_capability(self, capability: str) -> bool:
        """Check if domain has a capability"""
        return capability in self.capabilities

    def add_capability(self, capability: str) -> None:
        """Add a capability to the domain"""
        if capability not in self.capabilities:
            self.capabilities.append(capability)
            self.updated_at = time.time()

    # Predefined domains as class attributes
    CONTROL = None  # Will be set after class definition
    GOVERNANCE = None
    TRADING = None
    RISK = None
    OPERATIONS = None
    SYSTEM = None
    INFRASTRUCTURE = None
    DATA = None
    ANALYTICS = None
    UI = None


# Set the class attributes after class definition
Domain.CONTROL = Domain("control", "Control Domain", DomainKind.GOVERNANCE, AuthorityLevel.CRITICAL)
Domain.GOVERNANCE = Domain(
    "governance", "Governance Domain", DomainKind.GOVERNANCE, AuthorityLevel.CRITICAL
)
Domain.TRADING = Domain("trading", "Trading Domain", DomainKind.TRADING, AuthorityLevel.HIGH)
Domain.RISK = Domain("risk", "Risk Domain", DomainKind.RISK, AuthorityLevel.CRITICAL)
Domain.OPERATIONS = Domain(
    "operations", "Operations Domain", DomainKind.OPERATIONS, AuthorityLevel.HIGH
)
Domain.SYSTEM = Domain("system", "System Domain", DomainKind.SYSTEM, AuthorityLevel.CRITICAL)
Domain.INFRASTRUCTURE = Domain(
    "infrastructure", "Infrastructure Domain", DomainKind.INFRASTRUCTURE, AuthorityLevel.HIGH
)
Domain.DATA = Domain("data", "Data Domain", DomainKind.MARKET_DATA, AuthorityLevel.HIGH)
Domain.ANALYTICS = Domain(
    "analytics", "Analytics Domain", DomainKind.ANALYTICS, AuthorityLevel.MEDIUM
)
Domain.UI = Domain("ui", "UI Domain", DomainKind.UI, AuthorityLevel.MEDIUM)


@dataclass
class AuthorityRecord:
    """Authority record for tracking"""

    record_id: str
    domain_id: str
    action: str
    actor: str
    timestamp: float = field(default_factory=time.time)
    justification: str = ""
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            "record_id": self.record_id,
            "domain_id": self.domain_id,
            "action": self.action,
            "actor": self.actor,
            "timestamp": self.timestamp,
            "justification": self.justification,
            "metadata": self.metadata,
        }


class AuthorityRegistry:
    """Registry for domain authorities"""

    def __init__(self):
        self._domains: Dict[str, Domain] = {}
        self._records: List[AuthorityRecord] = []

    def register_domain(self, domain: Domain) -> bool:
        """Register a domain"""
        self._domains[domain.domain_id] = domain
        return True

    def get_domain(self, domain_id: str) -> Optional[Domain]:
        """Get a specific domain"""
        return self._domains.get(domain_id)

    def get_domains_by_kind(self, kind: DomainKind) -> List[Domain]:
        """Get all domains of a kind"""
        return [d for d in self._domains.values() if d.kind == kind]

    def get_critical_domains(self) -> List[Domain]:
        """Get all critical domains"""
        return [d for d in self._domains.values() if d.is_critical()]

    def record_authority_action(self, record: AuthorityRecord) -> bool:
        """Record an authority action"""
        self._records.append(record)
        return True

    def get_domain_records(self, domain_id: str) -> List[AuthorityRecord]:
        """Get all records for a domain"""
        return [r for r in self._records if r.domain_id == domain_id]


# Global authority registry
_authority_registry: Optional[AuthorityRegistry] = None


def get_authority_registry() -> AuthorityRegistry:
    """Get the global authority registry"""
    global _authority_registry
    if _authority_registry is None:
        _authority_registry = AuthorityRegistry()
    return _authority_registry


def create_domain(
    domain_id: str, name: str, kind: DomainKind, authority_level: AuthorityLevel
) -> Domain:
    """Create a new domain"""
    return Domain(domain_id=domain_id, name=name, kind=kind, authority_level=authority_level)


def create_authority_record(domain_id: str, action: str, actor: str) -> AuthorityRecord:
    """Create a new authority record"""
    return AuthorityRecord(
        record_id=f"{domain_id}_{int(time.time())}", domain_id=domain_id, action=action, actor=actor
    )


__all__ = [
    "DomainKind",
    "AuthorityLevel",
    "Domain",
    "AuthorityRecord",
    "AuthorityRegistry",
    "get_authority_registry",
    "create_domain",
    "create_authority_record",
]
