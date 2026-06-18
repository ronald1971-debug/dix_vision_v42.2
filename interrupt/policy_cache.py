"""
Interrupt Policy Cache - Policy Caching for Interrupts
Provides policy caching capabilities
NO LAZY LOADING - All components load directly
"""

from typing import Dict, List, Optional, Any
from dataclasses import dataclass, field
from enum import Enum
import datetime
import logging

logger = logging.getLogger(__name__)

class RuleAction(Enum):
    """Rule action types"""
    ALLOW = "allow"
    DENY = "deny"
    ESCALATE = "escalate"
    QUARANTINE = "quarantine"

@dataclass
class EmergencyRule:
    """Emergency rule data structure"""
    rule_id: str
    condition: str
    action: RuleAction
    priority: int = 0
    active: bool = True
    timestamp_ns: int = 0
    
    def __post_init__(self):
        if self.timestamp_ns == 0:
            self.timestamp_ns = int(__import__('datetime').datetime.now().timestamp() * 1_000_000_000)

@dataclass
class EmergencyPolicySnapshot:
    """Emergency policy snapshot data structure"""
    policy_id: str
    state: str
    active_rules: List[str] = field(default_factory=list)
    constraints: Dict[str, Any] = field(default_factory=dict)
    timestamp_ns: int = 0
    
    def __post_init__(self):
        if self.timestamp_ns == 0:
            self.timestamp_ns = int(__import__('datetime').datetime.now().timestamp() * 1_000_000_000)

class PolicyCache:
    """Policy cache for interrupt operations"""
    
    def __init__(self):
        self._cached_policies = {}
        self._policy_snapshots = {}
        self._emergency_rules = {}
        
    def cache_policy(self, policy_id: str, policy_data: Dict[str, Any]):
        """Cache policy data"""
        self._cached_policies[policy_id] = policy_data
        
    def get_policy(self, policy_id: str) -> Optional[Dict[str, Any]]:
        """Get cached policy"""
        return self._cached_policies.get(policy_id)
        
    def create_snapshot(self, policy_id: str, state: str) -> EmergencyPolicySnapshot:
        """Create emergency policy snapshot"""
        snapshot = EmergencyPolicySnapshot(
            policy_id=policy_id,
            state=state,
            active_rules=list(self._cached_policies.get(policy_id, {}).get("rules", [])),
            constraints=self._cached_policies.get(policy_id, {}).get("constraints", {})
        )
        self._policy_snapshots[policy_id] = snapshot
        return snapshot
    
    def get_snapshot(self, policy_id: str) -> Optional[EmergencyPolicySnapshot]:
        """Get policy snapshot"""
        return self._policy_snapshots.get(policy_id)
    
    def add_emergency_rule(self, rule: EmergencyRule):
        """Add emergency rule"""
        self._emergency_rules[rule.rule_id] = rule
        
    def get_emergency_rule(self, rule_id: str) -> Optional[EmergencyRule]:
        """Get emergency rule"""
        return self._emergency_rules.get(rule_id)
        
    def clear_cache(self):
        """Clear all cached policies"""
        self._cached_policies.clear()
        self._policy_snapshots.clear()
        self._emergency_rules.clear()

# Global instance
_policy_cache = None

def get_policy_cache() -> PolicyCache:
    """Get policy cache instance"""
    global _policy_cache
    if _policy_cache is None:
        _policy_cache = PolicyCache()
    return _policy_cache

def get_snapshot(policy_id: str) -> Optional[EmergencyPolicySnapshot]:
    """Get policy snapshot"""
    return get_policy_cache().get_snapshot(policy_id)

__all__ = ['EmergencyRule', 'EmergencyPolicySnapshot', 'PolicyCache', 'get_policy_cache', 'get_snapshot']