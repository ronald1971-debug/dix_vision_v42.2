"""
Governance Unified Domains - Domain-Specific Governance
Provides domain-specific governance policies and components
NO LAZY LOADING - All components load directly
"""

import time
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum

class GovernanceDomain(Enum):
    """Governance domain types"""
    COGNITIVE = "cognitive"
    FINANCIAL = "financial"
    OPERATOR = "operator"
    SYSTEM = "system"
    OPERATIONAL = "operational"

class PolicyStatus(Enum):
    """Policy status"""
    ACTIVE = "active"
    INACTIVE = "inactive"
    PENDING = "pending"
    REVOKED = "revoked"

@dataclass
class CognitiveGovernancePolicy:
    """Cognitive governance policy data structure"""
    policy_id: str = "cognitive_default"
    domain: GovernanceDomain = GovernanceDomain.COGNITIVE
    title: str = "Cognitive Governance"
    description: str = "Default cognitive governance policy"
    constitution_principles: List[str] = field(default_factory=list)
    constraints: Dict[str, Any] = field(default_factory=dict)
    status: PolicyStatus = PolicyStatus.ACTIVE
    created_at: int = 0
    updated_at: int = 0

    def __post_init__(self):
        if self.created_at == 0:
            self.created_at = int(datetime.now().timestamp())
        if self.updated_at == 0:
            self.updated_at = int(datetime.now().timestamp())

    def update_description(self, new_description: str):
        """Update policy description"""
        self.description = new_description
        self.updated_at = int(datetime.now().timestamp())

    def to_rules(self) -> List[Any]:
        """Convert policy to rules list"""
        return []

@dataclass
class FinancialGovernancePolicy:
    """Financial governance policy data structure"""
    policy_id: str = "financial_default"
    domain: GovernanceDomain = GovernanceDomain.FINANCIAL
    title: str = "Financial Governance"
    description: str = "Default financial governance policy"
    constitution_principles: List[str] = field(default_factory=list)
    constraints: Dict[str, Any] = field(default_factory=dict)
    status: PolicyStatus = PolicyStatus.ACTIVE
    created_at: int = 0
    updated_at: int = 0

    def __post_init__(self):
        if self.created_at == 0:
            self.created_at = int(datetime.now().timestamp())
        if self.updated_at == 0:
            self.updated_at = int(datetime.now().timestamp())

    def to_rules(self) -> List[Any]:
        """Convert policy to rules list"""
        return []

@dataclass
class OperatorGovernancePolicy:
    """Operator governance policy data structure"""
    policy_id: str = "operator_default"
    domain: GovernanceDomain = GovernanceDomain.OPERATOR
    title: str = "Operator Governance"
    description: str = "Default operator governance policy"
    constitution_principles: List[str] = field(default_factory=list)
    constraints: Dict[str, Any] = field(default_factory=dict)
    status: PolicyStatus = PolicyStatus.ACTIVE
    created_at: int = 0
    updated_at: int = 0

    def __post_init__(self):
        if self.created_at == 0:
            self.created_at = int(datetime.now().timestamp())
        if self.updated_at == 0:
            self.updated_at = int(datetime.now().timestamp())

    def to_rules(self) -> List[Any]:
        """Convert policy to rules list"""
        return []

@dataclass
class SystemGovernancePolicy:
    """System governance policy data structure"""
    policy_id: str = "system_default"
    domain: GovernanceDomain = GovernanceDomain.SYSTEM
    title: str = "System Governance"
    description: str = "Default system governance policy"
    constitution_principles: List[str] = field(default_factory=list)
    constraints: Dict[str, Any] = field(default_factory=dict)
    status: PolicyStatus = PolicyStatus.ACTIVE
    created_at: int = 0
    updated_at: int = 0

    def __post_init__(self):
        if self.created_at == 0:
            self.created_at = int(datetime.now().timestamp())
        if self.updated_at == 0:
            self.updated_at = int(datetime.now().timestamp())

    def to_rules(self) -> List[Any]:
        """Convert policy to rules list"""
        return []
    
    def add_constraint(self, key: str, value: Any):
        """Add policy constraint"""
        self.constraints[key] = value
        self.updated_at = datetime.now().timestamp_ns()
    
    def activate(self):
        """Activate policy"""
        self.status = PolicyStatus.ACTIVE
        self.updated_at = datetime.now().timestamp_ns()
    
    def deactivate(self):
        """Deactivate policy"""
        self.status = PolicyStatus.INACTIVE
        self.updated_at = datetime.now().timestamp_ns()

class DomainGovernanceManager:
    """Manager for domain-specific governance policies"""
    
    def __init__(self):
        self._policies: Dict[str, CognitiveGovernancePolicy] = {}
        self._active = True
        
    def create_policy(self, policy_id: str, domain: GovernanceDomain, title: str, 
                    description: str) -> CognitiveGovernancePolicy:
        """Create new governance policy"""
        policy = CognitiveGovernancePolicy(
            policy_id=policy_id,
            domain=domain,
            title=title,
            description=description
        )
        
        self._policies[policy_id] = policy
        return policy
    
    def get_policy(self, policy_id: str) -> Optional[CognitiveGovernancePolicy]:
        """Get policy by ID"""
        return self._policies.get(policy_id)
    
    def get_policies_by_domain(self, domain: GovernanceDomain) -> List[CognitiveGovernancePolicy]:
        """Get policies by domain"""
        return [p for p in self._policies.values() if p.domain == domain]
    
    def get_active_policies(self) -> List[CognitiveGovernancePolicy]:
        """Get all active policies"""
        return [p for p in self._policies.values() if p.status == PolicyStatus.ACTIVE]

# Global instance
_domain_governance_manager = None

def get_domain_governance_manager() -> DomainGovernanceManager:
    """Get global domain governance manager instance"""
    global _domain_governance_manager
    if _domain_governance_manager is None:
        _domain_governance_manager = DomainGovernanceManager()
    return _domain_governance_manager

def create_cognitive_policy(policy_id: str, title: str, description: str) -> CognitiveGovernancePolicy:
    """Create cognitive governance policy (convenience function)"""
    manager = get_domain_governance_manager()
    return manager.create_policy(policy_id, GovernanceDomain.COGNITIVE, title, description)

__all__ = [
    'GovernanceDomain',
    'PolicyStatus',
    'CognitiveGovernancePolicy',
    'DomainGovernanceManager',
    'get_domain_governance_manager',
    'create_cognitive_policy'
]