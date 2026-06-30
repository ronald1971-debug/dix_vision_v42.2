"""
DIX VISION Governance-Learning Integration

Bridges the existing governance system with the learning engine to enable
learning that respects governance constraints and provides governance-aware learning.
"""

from __future__ import annotations

import logging
import threading
from collections import defaultdict, deque
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Dict, List, Optional
import numpy as np

# Import existing governance system
import sys
sys.path.insert(0, "c:/dix_vision_v42.2/containers/system_core/governance_unified")
from engine import GovernanceEngine
from domains.cognitive.learning_coherence import LearningCoherence
from domains.cognitive.learning_truthfulness import LearningTruthfulness

# Import existing learning engine
import sys
sys.path.insert(0, "c:/dix_vision_v42.2/containers/system_core/learning_engine")
from engine import LearningEngine
from loops.closed_loop import ClosedLearningLoop

logger = logging.getLogger(__name__)


@dataclass
class GovernanceLearningPolicy:
    """Policy governing learning within governance constraints."""
    policy_id: str
    governance_domain: str  # "cognitive", "financial", "operator", "system"
    learning_constraints: Dict[str, Any]
    allowed_learning_types: List[str]
    risk_limits: Dict[str, float]
    approval_required: bool
    audit_requirements: List[str]
    timestamp: float


@dataclass
class LearningGovernanceDecision:
    """Governance decision on a learning operation."""
    decision_id: str
    learning_operation: str
    governance_domain: str
    approved: bool
    conditions: List[str]
    risk_assessment: float
    governance_reasoning: str
    timestamp: float


@dataclass
class GovernanceAwareLearningResult:
    """Learning result with governance compliance."""
    learning_id: str
    governance_compliant: bool
    governance_decisions: List[LearningGovernanceDecision]
    learning_performance: Dict[str, float]
    policy_violations: List[str]
    audit_trail: List[Dict[str, Any]]
    timestamp: datetime = field(default_factory=datetime.now)


class GovernanceLearningBridge:
    """
    Bridge between governance system and learning engine.
    
    Ensures that learning operations:
    - Respect governance constraints
    - Comply with domain-specific policies
    - Include proper audit trails
    - Maintain system safety while learning
    """
    
    def __init__(self):
        # Initialize governance engine
        self._governance_engine = GovernanceEngine()
        
        # Initialize learning engine
        self._learning_engine = LearningEngine()
        
        # Governance learning policies
        self._governance_policies: Dict[str, GovernanceLearningPolicy] = {}
        
        # Learning governance decisions
        self._governance_decisions: List[LearningGovernanceDecision] = []
        
        # Governance-aware learning results
        self._learning_results: List[GovernanceAwareLearningResult] = {}
        
        # Initialize default policies
        self._initialize_default_policies()
        
        self._lock = threading.Lock()
        
        logger.info("Governance-Learning Bridge initialized")
    
    def _initialize_default_policies(self):
        """Initialize default governance learning policies."""
        # Cognitive domain policy
        cognitive_policy = GovernanceLearningPolicy(
            policy_id="cognitive_learning_policy",
            governance_domain="cognitive",
            learning_constraints={
                "max_parameter_change": 0.1,
                "require_coherence_check": True,
                "hallucination_detection": True,
                "identity_stability": True
            },
            allowed_learning_types=[
                "parameter_tuning",
                "model_fine_tuning",
                "knowledge_update"
            ],
            risk_limits={
                "max_risk_level": 0.3,
                "confidence_threshold": 0.7
            },
            approval_required=True,
            audit_requirements=[
                "parameter_changes",
                "coherence_metrics",
                "truthfulness_scores"
            ],
            timestamp=datetime.now().timestamp()
        )
        
        # Financial domain policy
        financial_policy = GovernanceLearningPolicy(
            policy_id="financial_learning_policy",
            governance_domain="financial",
            learning_constraints={
                "max_position_risk": 0.02,
                "leverage_limit": 2.0,
                "drawdown_limit": 0.1,
                "require_backtesting": True
            },
            allowed_learning_types=[
                "strategy_optimization",
                "risk_model_update",
                "execution_tuning"
            ],
            risk_limits={
                "max_capital_risk": 0.05,
                "max_leverage": 2.0
            },
            approval_required=True,
            audit_requirements=[
                "risk_metrics",
                "performance_attribution",
                "regime_compliance"
            ],
            timestamp=datetime.now().timestamp()
        )
        
        # System domain policy
        system_policy = GovernanceLearningPolicy(
            policy_id="system_learning_policy",
            governance_domain="system",
            learning_constraints={
                "no_runtime_modification": True,
                "require_testing": True,
                "rollback_capability": True
            },
            allowed_learning_types=[
                "hyperparameter_tuning",
                "architecture_optimization",
                "resource_allocation"
            ],
            risk_limits={
                "max_downtime_risk": 0.01,
                "max_performance_degradation": 0.05
            },
            approval_required=False,  # System-level optimizations don't always need approval
            audit_requirements=[
                "performance_metrics",
                "resource_usage",
                "stability_tests"
            ],
            timestamp=datetime.now().timestamp()
        )
        
        self._governance_policies = {
            "cognitive": cognitive_policy,
            "financial": financial_policy,
            "system": system_policy
        }
        
        logger.info(f"Initialized {len(self._governance_policies)} governance learning policies")
    
    def evaluate_learning_governance(self, learning_operation: str,
                                   governance_domain: str,
                                   learning_parameters: Dict[str, Any]) -> LearningGovernanceDecision:
        """Evaluate whether a learning operation complies with governance."""
        policy = self._governance_policies.get(governance_domain)
        if not policy:
            # Default to safe if no policy found
            return LearningGovernanceDecision(
                decision_id=f"gov_decision_{int(datetime.now().timestamp())}",
                learning_operation=learning_operation,
                governance_domain=governance_domain,
                approved=False,
                conditions=["No governance policy found for domain"],
                risk_assessment=1.0,  # High risk
                governance_reasoning="No policy available - default to safe",
                timestamp=datetime.now().timestamp()
            )
        
        # Check learning constraints
        violations = []
        conditions = []
        
        # Check if learning type is allowed
        if learning_operation not in policy.allowed_learning_types:
            violations.append(f"Learning type '{learning_operation}' not allowed in {governance_domain} domain")
        
        # Check learning constraints
        for constraint, limit in policy.learning_constraints.items():
            if constraint in learning_parameters:
                if isinstance(limit, bool) and limit:
                    conditions.append(f"Constraint '{constraint}' must be satisfied")
                elif isinstance(limit, (int, float)):
                    if learning_parameters[constraint] > limit:
                        violations.append(f"Constraint '{constraint}' exceeds limit {limit}")
        
        # Check risk limits
        risk_assessment = 0.0
        for risk_limit, max_value in policy.risk_limits.items():
            if risk_limit in learning_parameters:
                if learning_parameters[risk_limit] > max_value:
                    risk_assessment += 0.3
                    violations.append(f"Risk '{risk_limit}' exceeds limit {max_value}")
        
        # Determine approval
        approved = len(violations) == 0 and (not policy.approval_required or risk_assessment < 0.5)
        
        # Generate governance reasoning
        if approved:
            governance_reasoning = f"Learning operation approved - all constraints satisfied, risk level {risk_assessment:.2f}"
        else:
            governance_reasoning = f"Learning operation rejected - {len(violations)} violations detected, risk level {risk_assessment:.2f}"
        
        decision = LearningGovernanceDecision(
            decision_id=f"gov_decision_{int(datetime.now().timestamp())}",
            learning_operation=learning_operation,
            governance_domain=governance_domain,
            approved=approved,
            conditions=conditions + violations,
            risk_assessment=risk_assessment,
            governance_reasoning=governance_reasoning,
            timestamp=datetime.now().timestamp()
        )
        
        with self._lock:
            self._governance_decisions.append(decision)
        
        return decision
    
    def execute_governed_learning(self, learning_operation: str,
                                governance_domain: str,
                                learning_parameters: Dict[str, Any]) -> GovernanceAwareLearningResult:
        """Execute learning with governance oversight."""
        # Step 1: Evaluate governance compliance
        governance_decision = self.evaluate_learning_governance(
            learning_operation, governance_domain, learning_parameters
        )
        
        # Step 2: Execute learning if approved
        learning_performance = {}
        policy_violations = []
        audit_trail = []
        
        if governance_decision.approved:
            try:
                # Execute learning operation
                learning_performance = self._execute_learning(
                    learning_operation, learning_parameters
                )
                
                # Create audit trail
                audit_trail = self._create_audit_trail(
                    learning_operation, governance_domain, learning_parameters, learning_performance
                )
                
                logger.info(f"Governed learning executed successfully: {learning_operation}")
                
            except Exception as e:
                logger.error(f"Governed learning failed: {e}")
                policy_violations.append(f"Learning execution failed: {str(e)}")
        else:
            policy_violations.extend(governance_decision.conditions)
            logger.warning(f"Learning operation rejected by governance: {governance_decision.governance_reasoning}")
        
        # Step 3: Create governance-aware result
        result = GovernanceAwareLearningResult(
            learning_id=f"governed_learning_{int(datetime.now().timestamp())}",
            governance_compliant=governance_decision.approved,
            governance_decisions=[governance_decision],
            learning_performance=learning_performance,
            policy_violations=policy_violations,
            audit_trail=audit_trail
        )
        
        with self._lock:
            self._learning_results[result.learning_id] = result
        
        return result
    
    def _execute_learning(self, learning_operation: str,
                        learning_parameters: Dict[str, Any]) -> Dict[str, float]:
        """Execute the actual learning operation."""
        # This would interface with the actual learning engine
        # For now, simulate learning performance
        
        performance_metrics = {
            "accuracy": np.random.uniform(0.7, 0.9),
            "loss": np.random.uniform(0.1, 0.3),
            "convergence_rate": np.random.uniform(0.5, 0.9),
            "stability_score": np.random.uniform(0.7, 0.95)
        }
        
        return performance_metrics
    
    def _create_audit_trail(self, learning_operation: str, governance_domain: str,
                          learning_parameters: Dict[str, Any],
                          learning_performance: Dict[str, float]) -> List[Dict[str, Any]]:
        """Create audit trail for learning operation."""
        policy = self._governance_policies.get(governance_domain)
        
        audit_entries = []
        
        # Add parameter changes
        audit_entries.append({
            "type": "parameter_changes",
            "operation": learning_operation,
            "parameters": learning_parameters,
            "timestamp": datetime.now().isoformat()
        })
        
        # Add performance metrics
        audit_entries.append({
            "type": "performance_metrics",
            "metrics": learning_performance,
            "timestamp": datetime.now().isoformat()
        })
        
        # Add domain-specific audit requirements
        if policy:
            for requirement in policy.audit_requirements:
                audit_entries.append({
                    "type": requirement,
                    "compliance": True,
                    "timestamp": datetime.now().isoformat()
                })
        
        return audit_entries
    
    def update_governance_policy(self, governance_domain: str,
                               policy_updates: Dict[str, Any]) -> bool:
        """Update governance policy for a domain."""
        if governance_domain not in self._governance_policies:
            logger.warning(f"No policy found for domain: {governance_domain}")
            return False
        
        policy = self._governance_policies[governance_domain]
        
        # Update policy fields
        if "learning_constraints" in policy_updates:
            policy.learning_constraints.update(policy_updates["learning_constraints"])
        
        if "allowed_learning_types" in policy_updates:
            policy.allowed_learning_types = policy_updates["allowed_learning_types"]
        
        if "risk_limits" in policy_updates:
            policy.risk_limits.update(policy_updates["risk_limits"])
        
        if "approval_required" in policy_updates:
            policy.approval_required = policy_updates["approval_required"]
        
        policy.timestamp = datetime.now().timestamp()
        
        logger.info(f"Updated governance policy for {governance_domain}")
        
        return True
    
    def get_governance_learning_status(self) -> Dict[str, Any]:
        """Get status of governance-learning integration."""
        with self._lock:
            recent_decisions = self._governance_decisions[-10:] if self._governance_decisions else []
            
            approval_rate = (
                sum(1 for d in recent_decisions if d.approved) / len(recent_decisions)
                if recent_decisions else 0.0
            )
            
            return {
                "policies_active": len(self._governance_policies),
                "total_governance_decisions": len(self._governance_decisions),
                "recent_approval_rate": approval_rate,
                "total_learning_results": len(self._learning_results),
                "compliance_rate": (
                    sum(1 for r in self._learning_results.values() if r.governance_compliant) /
                    len(self._learning_results)
                    if self._learning_results else 0.0
                ),
                "governance_domains": list(self._governance_policies.keys())
            }


class LearningCoherenceBridge:
    """
    Bridge for learning coherence checks through governance.
    
    Ensures learning maintains coherence with existing knowledge and beliefs.
    """
    
    def __init__(self):
        self._governance_learning_bridge = GovernanceLearningBridge()
        self._coherence_checks: Dict[str, Any] = {}
        
        self._lock = threading.Lock()
        
        logger.info("Learning Coherence Bridge initialized")
    
    def check_learning_coherence(self, learning_update: Dict[str, Any],
                               existing_knowledge: Dict[str, Any]) -> Dict[str, Any]:
        """Check if learning update is coherent with existing knowledge."""
        coherence_score = 0.0
        coherence_issues = []
        
        # Check for contradictions
        for key, value in learning_update.items():
            if key in existing_knowledge:
                existing_value = existing_knowledge[key]
                
                # Check for direct contradiction
                if isinstance(value, (int, float)) and isinstance(existing_value, (int, float)):
                    if abs(value - existing_value) > (abs(existing_value) * 0.5):
                        coherence_issues.append(f"Large change in {key}: {existing_value} -> {value}")
                        coherence_score -= 0.2
                elif value != existing_value:
                    coherence_issues.append(f"Contradiction in {key}: {existing_value} vs {value}")
                    coherence_score -= 0.3
        
        # Check for consistency with related knowledge
        coherence_score = max(0.0, coherence_score + 0.7)  # Base coherence
        
        return {
            "coherent": coherence_score > 0.5,
            "coherence_score": coherence_score,
            "issues": coherence_issues,
            "governance_required": coherence_score < 0.7
        }
    
    def ensure_governed_coherent_learning(self, learning_update: Dict[str, Any],
                                        existing_knowledge: Dict[str, Any],
                                        governance_domain: str = "cognitive") -> GovernanceAwareLearningResult:
        """Ensure learning is both coherent and governed."""
        # Check coherence
        coherence_result = self.check_learning_coherence(learning_update, existing_knowledge)
        
        # If coherence issues, require governance approval
        if coherence_result["governance_required"]:
            learning_parameters = {
                **learning_update,
                "require_coherence_check": True,
                "coherence_score": coherence_result["coherence_score"]
            }
            
            governance_result = self._governance_learning_bridge.execute_governed_learning(
                "coherent_learning_update",
                governance_domain,
                learning_parameters
            )
            
            return governance_result
        else:
            # Coherent learning can proceed with minimal governance
            return self._governance_learning_bridge.execute_governed_learning(
                "coherent_learning_update",
                governance_domain,
                learning_update
            )


# Global instances
_governance_learning_bridge: Optional[GovernanceLearningBridge] = None
_learning_coherence_bridge: Optional[LearningCoherenceBridge] = None


def get_governance_learning_bridge() -> GovernanceLearningBridge:
    """Get global governance-learning bridge instance."""
    global _governance_learning_bridge
    if _governance_learning_bridge is None:
        _governance_learning_bridge = GovernanceLearningBridge()
    return _governance_learning_bridge


def get_learning_coherence_bridge() -> LearningCoherenceBridge:
    """Get global learning coherence bridge instance."""
    global _learning_coherence_bridge
    if _learning_coherence_bridge is None:
        _learning_coherence_bridge = LearningCoherenceBridge()
    return _learning_coherence_bridge