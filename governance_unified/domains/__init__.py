"""
governance_engine.domains
Unified domain-specific governance guards for the consolidated governance engine.

This package contains all domain-specific guards migrated from the separate
governance systems:
- cognitive: Cognitive integrity and AI safety guards
- financial: Financial risk management and capital protection guards  
- operator: Operator sovereignty and human-in-the-loop guards
- system: System integrity and structural consistency guards
"""

from __future__ import annotations

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
    invariants: List[str] = field(default_factory=list)
    constraints: Dict[str, Any] = field(default_factory=dict)
    status: PolicyStatus = PolicyStatus.ACTIVE
    updated_at: int = 0
    
    def __post_init__(self):
        if self.updated_at == 0:
            self.updated_at = int(datetime.now().timestamp() * 1_000_000_000)

__all__ = []