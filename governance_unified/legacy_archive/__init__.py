"""
Governance Unified Legacy Archive - Governance Infrastructure Components
Provides production-ready governance and policy components
NO LAZY LOADING - All components load directly
"""

from typing import Dict, List, Optional, Any
import logging

logger = logging.getLogger(__name__)

__all__ = [
    # Core governance
    'capital_throttle',
    'execution_hazard',
    'exposure_guard',
    'leverage_monitor',
    'liquidation_sentinel',
    'charter',
    'constraint_compiler',
    'coordination_adapter',
    'emergency_policy',
    'kernel',
    'mcos_constraint_compiler',
    'mcos_kernel',
    'patch_pipeline',
    'policy_engine',
    'risk_engine',
    'unified_graph',
    
    # Operating modes
    'cognitive',
    'financial',
    'operator',
    'system',
    'degraded_mode',
    'halted_mode',
    'safe_mode',
    'tier_l1_fast',
    'tier_l2_balanced',
    'tier_l3_deep',
    
    # Risk and safety
    'neuromorphic_risk',
    'base_wrapper',
    'dyon_constraints',
    'base_external_repo_wrapper',
    
    # Policy and governance
    'compliance_validator',
    'decision_signer',
    'drift_oracle',
    'event_classifier',
    'exposure_store',
    'external_signal_policy',
    'invariant_verifier',
    'learning_evolution_loop',
    'ledger_authority_writer',
    'operator_attention',
    'operator_interface_bridge',
    'patch_signer',
    'policy_drift_sentry',
    'policy_hash_anchor',
    'promotion_gates',
    'risk_evaluator',
    'state_transition_manager',
    'update_applier',
    'update_validator',
    
    # Cognitive safety
    'belief_integrity',
    'causal_consistency',
    'cognitive_constitution',
    'cognitive_maturity',
    'cognitive_physics',
    'epistemic_drift',
    'hallucination_guard',
    'identity_stability',
    'knowledge_lifecycle',
    'learning_coherence',
    'learning_truthfulness',
    'long_horizon_memory',
    'memory_contamination',
    'mutation_validator',
    'reward_hacking_detector',
    'strategy_lineage_guard',
    'synthetic_feedback_detection',
    
    # Authority and escalation
    'authority_escalation',
    'consent_router',
    'governance_visibility',
    'manual_lockout',
    'operator_constitution',
    'override_priority',
    
    # System integrity
    'contract_integrity',
    'convergence_monitor',
    'dependency_validator',
    'replay_integrity',
    'runtime_consistency',
    'topology_guard',
    
    # Evaluation and validation
    'quantitative_evaluator',
    'rulegraph_patch_evaluator',
    'coordinator',
    'execution_auditor',
    'invariants_state',
    'invariant_monitor',
    'isolation_boundary',
    'mutation_firewall',
    'policy_lock',
    'replay_engine',
    'trust_scorer',
    
    # Lifecycle and activation
    'activation_gate',
    'hot_reload_signal',
    'lifecycle_emitter',
    'manager',
    'registry_loader',
    
    # Risk limits
    'drawdown_guard',
    'exposure_limits',
    'kill_conditions',
    'position_limits',
    'real_time_risk',
    'risk_tracker',
    
    # Audit and compliance
    'audit_replay',
    'liveness_watchdog',
    'opa_policy',
    'overconfidence_guardrail',
    'patch_pipeline_bridge',
    'triple_window_dry_run',
    'trust_engine',
    'approval_workflow',
    
    # Archived versions (conflict resolution)
    'escalation_matrix_archived',
    'hazard_classifier_archived',
    'hazard_router_archived',
    'mode_manager_archived',
    'engine_archived',
    'harness_approver_archived',
    'kill_switch_archived',
    'policy_compiler_archived',
    'strategy_registry_archived'
]