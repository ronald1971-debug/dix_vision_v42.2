"""
Governance Layer - Policy, risk, and compliance management
"""

import logging
from typing import Dict, List, Any, Optional
from dataclasses import dataclass
from enum import Enum


class PolicyType(Enum):
    """Types of governance policies."""
    SAFETY = "safety"
    PRIVACY = "privacy"
    SECURITY = "security"
    COMPLIANCE = "compliance"
    ETHICS = "ethics"


@dataclass
class Policy:
    """Governance policy."""
    id: str
    name: str
    type: PolicyType
    description: str
    rules: List[Dict[str, Any]]
    enabled: bool = True


class GovernanceLayer:
    """
    Governance layer for policy enforcement.
    
    Manages policies, risk assessment, compliance checking,
    and audit logging for all agent activities.
    """
    
    def __init__(self, config: Dict[str, Any] = None):
        """
        Initialize governance layer.
        
        Args:
            config: Governance configuration
        """
        self.config = config or {}
        self.policies: Dict[str, Policy] = {}
        self.audit_log: List[Dict[str, Any]] = []
        
        self.logger = logging.getLogger(__name__)
        
    async def initialize(self) -> None:
        """Initialize governance layer."""
        # Load default policies
        await self._load_default_policies()
        self.logger.info("Governance Layer initialized")
        
    async def _load_default_policies(self) -> None:
        """Load default governance policies."""
        # Safety policy
        safety_policy = Policy(
            id="safety-001",
            name="Agent Safety",
            type=PolicyType.SAFETY,
            description="Ensure agents operate within safe bounds",
            rules=[
                {"rule": "no_self_modification", "enabled": True},
                {"rule": "no_unauthorized_access", "enabled": True},
                {"rule": "human_approval_required", "enabled": True},
            ],
        )
        self.policies[safety_policy.id] = safety_policy
        
        # Privacy policy
        privacy_policy = Policy(
            id="privacy-001",
            name="Data Privacy",
            type=PolicyType.PRIVACY,
            description="Protect user privacy and data",
            rules=[
                {"rule": "no_data_exfiltration", "enabled": True},
                {"rule": "encrypt_sensitive_data", "enabled": True},
                {"rule": "user_consent_required", "enabled": True},
            ],
        )
        self.policies[privacy_policy.id] = privacy_policy
        
    async def add_policy(self, policy: Policy) -> None:
        """
        Add a governance policy.
        
        Args:
            policy: Policy to add
        """
        self.policies[policy.id] = policy
        self.logger.info(f"Added policy: {policy.name}")
        
    async def remove_policy(self, policy_id: str) -> None:
        """
        Remove a governance policy.
        
        Args:
            policy_id: Policy identifier
        """
        if policy_id in self.policies:
            del self.policies[policy_id]
            self.logger.info(f"Removed policy: {policy_id}")
            
    async def check_compliance(
        self,
        action: Dict[str, Any],
    ) -> tuple[bool, List[str]]:
        """
        Check if an action complies with all policies.
        
        Args:
            action: Action to check
            
        Returns:
            Tuple of (is_compliant, violations)
        """
        violations = []
        
        for policy in self.policies.values():
            if not policy.enabled:
                continue
                
            for rule in policy.rules:
                if not rule.get("enabled", True):
                    continue
                    
                # Check rule compliance
                if not await self._check_rule(rule, action):
                    violations.append(f"{policy.name}: {rule['rule']}")
                    
        is_compliant = len(violations) == 0
        return is_compliant, violations
        
    async def _check_rule(self, rule: Dict[str, Any], action: Dict[str, Any]) -> bool:
        """
        Check if an action complies with a rule.
        
        Args:
            rule: Rule to check
            action: Action to check
            
        Returns:
            True if compliant, False otherwise
        """
        # Simplified rule checking
        # In real implementation, this would be more sophisticated
        return True
        
    async def log_audit(self, entry: Dict[str, Any]) -> None:
        """
        Log an audit entry.
        
        Args:
            entry: Audit entry data
        """
        self.audit_log.append(entry)
        
    async def get_audit_log(self, limit: int = 100) -> List[Dict[str, Any]]:
        """
        Get audit log entries.
        
        Args:
            limit: Maximum number of entries
            
        Returns:
            List of audit entries
        """
        return self.audit_log[-limit:]
        
    def get_status(self) -> Dict[str, Any]:
        """
        Get governance status.
        
        Returns:
            Status dictionary
        """
        return {
            "total_policies": len(self.policies),
            "enabled_policies": sum(1 for p in self.policies.values() if p.enabled),
            "audit_entries": len(self.audit_log),
        }
