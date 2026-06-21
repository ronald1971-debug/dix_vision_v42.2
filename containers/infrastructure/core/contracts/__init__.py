"""
Core Contracts Module
Real implementations for DIX VISION contracts
NO PLACEHOLDER - Contract-compliant real implementations
"""

import time
from .events import (
    EventKind,
    HazardSeverity,
    ExecutionStatus,
    SystemEventKind,
    Side,
    Event,
    HazardEvent,
    SignalEvent,
    SystemEvent,
    ExecutionEvent
)
from .api import (
    PresenceState,
    CredentialItem,
    CredentialsStatusResponse,
    CredentialsSummary,
    PresenceStateApi,
    get_presence_state_api
)
from .development_mode import (
    DevelopmentMode,
    DevelopmentModePolicy,
    get_development_mode_policy,
    set_development_mode
)
from .learning import (
    PatchProposal,
    StrategyStats
)
from .learning_evolution_freeze import (
    LearningEvolutionFreezePolicy
)
from .external_signal_trust import (
    ExternalSignalTrustRegistry,
    load_external_signal_trust
)
from .source_trust_promotions import (
    SourceTrustPromotionStore
)
from .market import MarketTick
from .risk import RiskSnapshot
from .governance import GovernanceKind, SystemMode, GovernanceDecision, DecisionKind, IntentHorizon, IntentObjective, IntentRiskMode, RiskAssessment, ConstraintKind, ConstraintScope, OperatorAction, LedgerEntry, OperatorRequest, Constraint, ModeTransitionRequest, ComplianceReport, ModeTransitionDecision, IntentTransitionRequest, IntentTransitionDecision
from .engine import EngineKind, EngineTier, EngineStatus, HealthState, PluginLifecycle, HealthStatus, EngineHealth, EngineConfig, EngineCapabilities, Plugin, RuntimeEngine, OfflineEngine
from .event_provenance import SourceKind, Provenance, AuthorizationLevel, get_authorization_level, is_operator_authorized_source, verify_provenance
from .signal_trust import TrustLevel, SignalTrust, default_cap_for, default_signal_trust, verify_signal
from .operator_consent import ConsentStatus, ConsentKind, ConsentRequest, OperatorConsent, ConsentDecision, OperatorConsentValidator, create_consent_request, create_validator, edge_requires_consent
from .strategy_registry import StrategyKind, StrategyStatus, StrategyLifecycle, StrategyLifecycleError, StrategyRecord, StrategyRegistry, get_strategy_registry, is_legal_transition
from .mode_effects import EffectKind, EffectSeverity, ModeEffect, effect_for, get_effects_for_mode, apply_effect, revoke_effect, ModeEffectManager, get_effect_manager
from .invariants import InvariantKind, InvariantSeverity, InvariantStatus, InvariantID, DIX_01, DIX_02, DIX_03, DIX_04, DIX_05, DIX_06, DIX_07, DIX_08, DIX_09, DIX_10, DIX_11, DIX_12, DIX_13, DIX_14, DIX_15, DIX_16, DIX_17, DIX_18, DIX_19, DIX_20, InvariantDefinition, InvariantViolation, InvariantManager, get_invariant_manager, create_violation

__all__ = [
    # Events
    "EventKind",
    "HazardSeverity",
    "ExecutionStatus",
    "SystemEventKind",
    "Side",
    "Event",
    "HazardEvent",
    "SignalEvent",
    "SystemEvent",
    "ExecutionEvent",
    # API
    "PresenceState",
    "CredentialItem",
    "CredentialsStatusResponse",
    "CredentialsSummary",
    "PresenceStateApi",
    "get_presence_state_api",
    # Development Mode
    "DevelopmentMode",
    "DevelopmentModePolicy",
    "get_development_mode_policy",
    "set_development_mode",
    # Learning
    "PatchProposal",
    "StrategyStats",
    # Learning Evolution Freeze
    "LearningEvolutionFreezePolicy",
    # External Signal Trust
    "ExternalSignalTrustRegistry",
    "load_external_signal_trust",
    # Source Trust Promotions
    "SourceTrustPromotionStore",
    # Market and Risk
    "MarketTick",
    "RiskSnapshot",
    # Governance
    "GovernanceKind",
    "SystemMode",
    "GovernanceDecision",
    "DecisionKind",
    "IntentHorizon",
    "IntentObjective",
    "IntentRiskMode",
    "RiskAssessment",
    "ConstraintKind",
    "ConstraintScope",
    "OperatorAction",
    "LedgerEntry",
    "OperatorRequest",
    "Constraint",
    "ModeTransitionRequest",
    "ComplianceReport",
    "ModeTransitionDecision",
    "IntentTransitionRequest",
    "IntentTransitionDecision",
    # Engine
    "EngineKind",
    "EngineTier",
    "EngineStatus",
    "HealthState",
    "PluginLifecycle",
    "EngineHealth",
    "EngineConfig",
    "EngineCapabilities",
    "Plugin",
    "RuntimeEngine",
    "OfflineEngine",
    # Event Provenance
    "SourceKind",
    "Provenance",
    "AuthorizationLevel",
    "get_authorization_level",
    "is_operator_authorized_source",
    "verify_provenance",
    # Signal Trust
    "TrustLevel",
    "SignalTrust",
    "default_cap_for",
    "default_signal_trust",
    "verify_signal",
    # Operator Consent
    "ConsentStatus",
    "ConsentKind",
    "ConsentRequest",
    "OperatorConsent",
    "ConsentDecision",
    "OperatorConsentValidator",
    "create_consent_request",
    "create_validator",
    "edge_requires_consent",
    # Strategy Registry
    "StrategyKind",
    "StrategyStatus",
    "StrategyLifecycle",
    "StrategyLifecycleError",
    "StrategyRecord",
    "StrategyRegistry",
    "get_strategy_registry",
    "is_legal_transition",
    # Mode Effects
    "EffectKind",
    "EffectSeverity",
    "ModeEffect",
    "effect_for",
    "get_effects_for_mode",
    "apply_effect",
    "revoke_effect",
    "ModeEffectManager",
    "get_effect_manager",
    # Invariants
    "InvariantKind",
    "InvariantSeverity",
    "InvariantStatus",
    "InvariantID",
    "DIX_01",
    "DIX_02",
    "DIX_03",
    "DIX_04",
    "DIX_05",
    "DIX_06",
    "DIX_07",
    "DIX_08",
    "DIX_09",
    "DIX_10",
    "DIX_11",
    "DIX_12",
    "DIX_13",
    "DIX_14",
    "DIX_15",
    "DIX_16",
    "DIX_17",
    "DIX_18",
    "DIX_19",
    "DIX_20",
    "InvariantDefinition",
    "InvariantViolation",
    "InvariantManager",
    "get_invariant_manager",
    "create_violation"
]