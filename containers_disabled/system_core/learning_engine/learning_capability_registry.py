"""
Learning Capability Registry - Catalog Without Consolidation

Production-Grade Implementation for DIX VISION v42.2+ Phase 2
Catalogs all learning capabilities across domains while maintaining domain separation

Signal-First Architecture: 85/15 universal baseline maintained
Zero-Loss Guarantee: No consolidation, only cataloging
Contract Compliance: Tier-0 Production Implementation
"""

from __future__ import annotations

import logging
import threading
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional, Set

logger = logging.getLogger(__name__)


class LearningDomain(Enum):
    """Learning domains following canonical architecture."""

    INFRASTRUCTURE = "infrastructure"  # Core learning engine
    MARKET = "market"  # INDIRA learning
    RUNTIME_COGNITIVE = "runtime_cognitive"  # Intelligence engine learning
    CONTROL = "control"  # Governance learning
    RESEARCH_EXPERIMENTAL = "research_experimental"  # Development/alternatives
    INDEPENDENT = "independent"  # Standalone ML systems


class LearningCapabilityType(Enum):
    """Types of learning capabilities."""

    SUPERVISED_LEARNING = "supervised_learning"
    UNSUPERVISED_LEARNING = "unsupervised_learning"
    REINFORCEMENT_LEARNING = "reinforcement_learning"
    META_LEARNING = "meta_learning"
    TRANSFER_LEARNING = "transfer_learning"
    CONTINUAL_LEARNING = "continual_learning"
    FEDERATED_LEARNING = "federated_learning"
    DEEP_LEARNING = "deep_learning"
    BAYESIAN_LEARNING = "bayesian_learning"
    CAUSAL_LEARNING = "causal_learning"
    ONLINE_LEARNING = "online_learning"
    POLICY_LEARNING = "policy_learning"


class CapabilityStatus(Enum):
    """Status of learning capability."""

    PRODUCTION = "production"
    DEVELOPMENT = "development"
    EXPERIMENTAL = "experimental"
    ARCHIVED = "archived"
    STUB = "stub"


@dataclass
class LearningCapability:
    """Individual learning capability."""

    name: str
    domain: LearningDomain
    capability_type: LearningCapabilityType
    location: str  # File path
    status: CapabilityStatus
    description: str
    dependencies: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)
    registered_at: datetime = field(default_factory=datetime.now)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for catalog."""
        return {
            "name": self.name,
            "domain": self.domain.value,
            "capability_type": self.capability_type.value,
            "location": self.location,
            "status": self.status.value,
            "description": self.description,
            "dependencies": self.dependencies,
            "metadata": self.metadata,
            "registered_at": self.registered_at.isoformat(),
        }


@dataclass
class DomainLearningProfile:
    """Learning profile for a specific domain."""

    domain: LearningDomain
    total_capabilities: int = 0
    capability_types: Dict[LearningCapabilityType, int] = field(default_factory=dict)
    production_capabilities: int = 0
    development_capabilities: int = 0
    experimental_capabilities: int = 0
    last_updated: datetime = field(default_factory=datetime.now)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for reporting."""
        return {
            "domain": self.domain.value,
            "total_capabilities": self.total_capabilities,
            "capability_types": {ct.value: count for ct, count in self.capability_types.items()},
            "production_capabilities": self.production_capabilities,
            "development_capabilities": self.development_capabilities,
            "experimental_capabilities": self.experimental_capabilities,
            "last_updated": self.last_updated.isoformat(),
        }


class LearningCapabilityRegistry:
    """Registry of all learning capabilities across domains.

    This registry CATALOGS capabilities without requiring consolidation.
    Each domain maintains its learning systems and domain separation is preserved.
    """

    def __init__(self):
        """Initialize the learning capability registry."""
        self._lock = threading.Lock()
        self._capabilities: Dict[str, LearningCapability] = {}
        self._domain_profiles: Dict[LearningDomain, DomainLearningProfile] = {}
        self._initialize_registry()

    def _initialize_registry(self):
        """Initialize registry with known learning capabilities from analysis."""
        # Infrastructure (Core Learning Engine)
        self._register_infrastructure_capabilities()

        # Market (INDIRA Learning)
        self._register_market_capabilities()

        # Runtime Cognitive (Intelligence Engine Learning)
        self._register_runtime_cognitive_capabilities()

        # Control (Governance Learning)
        self._register_control_capabilities()

        # Research/Experimental (Development/Alternatives)
        self._register_research_capabilities()

        # Independent (Machine Learning)
        self._register_independent_capabilities()

        # Initialize domain profiles
        self._update_domain_profiles()

        logger.info("[LEARNING_REGISTRY] Learning Capability Registry initialized with catalog entries")

    def _register_infrastructure_capabilities(self):
        """Register infrastructure learning capabilities (Core Learning Engine)."""
        # Analytics
        self._register_capability(
            LearningCapability(
                name="backtest_scorer",
                domain=LearningDomain.INFRASTRUCTURE,
                capability_type=LearningCapabilityType.SUPERVISED_LEARNING,
                location="system_core/learning_engine/analytics/backtest_scorer.py",
                status=CapabilityStatus.PRODUCTION,
                description="Backtest scoring and evaluation for learning systems"
            )
        )
        self._register_capability(
            LearningCapability(
                name="feature_importance",
                domain=LearningDomain.INFRASTRUCTURE,
                capability_type=LearningCapabilityType.SUPERVISED_LEARNING,
                location="system_core/learning_engine/analytics/feature_importance.py",
                status=CapabilityStatus.PRODUCTION,
                description="Feature importance analysis for model interpretability"
            )
        )
        self._register_capability(
            LearningCapability(
                name="pnl_attribution",
                domain=LearningDomain.INFRASTRUCTURE,
                capability_type=LearningCapabilityType.SUPERVISED_LEARNING,
                location="system_core/learning_engine/analytics/pnl_attribution.py",
                status=CapabilityStatus.PRODUCTION,
                description="P&L attribution analysis for trading performance"
            )
        )
        self._register_capability(
            LearningCapability(
                name="regime_stats",
                domain=LearningDomain.INFRASTRUCTURE,
                capability_type=LearningCapabilityType.SUPERVISED_LEARNING,
                location="system_core/learning_engine/analytics/regime_stats.py",
                status=CapabilityStatus.PRODUCTION,
                description="Regime-based statistics for market analysis"
            )
        )

        # Attribution
        self._register_capability(
            LearningCapability(
                name="decision_attributor",
                domain=LearningDomain.INFRASTRUCTURE,
                capability_type=LearningCapabilityType.SUPERVISED_LEARNING,
                location="system_core/learning_engine/attribution/decision_attributor.py",
                status=CapabilityStatus.PRODUCTION,
                description="Decision attribution logic for learning from decisions"
            )
        )
        self._register_capability(
            LearningCapability(
                name="mistake_classifier",
                domain=LearningDomain.INFRASTRUCTURE,
                capability_type=LearningCapabilityType.SUPERVISED_LEARNING,
                location="system_core/learning_engine/attribution/mistake_classifier.py",
                status=CapabilityStatus.PRODUCTION,
                description="Mistake classification for learning from errors"
            )
        )

        # Federated Learning
        self._register_capability(
            LearningCapability(
                name="federated_learning",
                domain=LearningDomain.INFRASTRUCTURE,
                capability_type=LearningCapabilityType.FEDERATED_LEARNING,
                location="system_core/learning_engine/lanes/federated.py",
                status=CapabilityStatus.PRODUCTION,
                description="Federated learning coordinator for distributed learning"
            )
        )
        self._register_capability(
            LearningCapability(
                name="continual_learning",
                domain=LearningDomain.INFRASTRUCTURE,
                capability_type=LearningCapabilityType.CONTINUAL_LEARNING,
                location="system_core/learning_engine/lanes/continual_learner.py",
                status=CapabilityStatus.PRODUCTION,
                description="Continual learning for continuous model improvement"
            )
        )
        self._register_capability(
            LearningCapability(
                name="reinforcement_learning",
                domain=LearningDomain.INFRASTRUCTURE,
                capability_type=LearningCapabilityType.REINFORCEMENT_LEARNING,
                location="system_core/learning_engine/lanes/ral.py",
                status=CapabilityStatus.PRODUCTION,
                description="Reinforcement learning agent for decision optimization"
            )
        )

        # Core Learning
        self._register_capability(
            LearningCapability(
                name="adaptive_learning",
                domain=LearningDomain.INFRASTRUCTURE,
                capability_type=LearningCapabilityType.ONLINE_LEARNING,
                location="system_core/learning_engine/adaptive_learning.py",
                status=CapabilityStatus.PRODUCTION,
                description="Adaptive learning algorithms for dynamic environments"
            )
        )
        self._register_capability(
            LearningCapability(
                name="bayesian_updating",
                domain=LearningDomain.INFRASTRUCTURE,
                capability_type=LearningCapabilityType.BAYESIAN_LEARNING,
                location="system_core/learning_engine/bayesian_updating.py",
                status=CapabilityStatus.PRODUCTION,
                description="Bayesian updating for probabilistic learning"
            )
        )
        self._register_capability(
            LearningCapability(
                name="deep_learning",
                domain=LearningDomain.INFRASTRUCTURE,
                capability_type=LearningCapabilityType.DEEP_LEARNING,
                location="system_core/learning_engine/deep_learning.py",
                status=CapabilityStatus.PRODUCTION,
                description="Deep learning integration for neural networks"
            )
        )
        self._register_capability(
            LearningCapability(
                name="causal_learning",
                domain=LearningDomain.INFRASTRUCTURE,
                capability_type=LearningCapabilityType.CAUSAL_LEARNING,
                location="system_core/learning_engine/causal/probabilistic_model.py",
                status=CapabilityStatus.PRODUCTION,
                description="Causal learning for understanding cause-effect relationships"
            )
        )

    def _register_market_capabilities(self):
        """Register market learning capabilities (INDIRA)."""
        self._register_capability(
            LearningCapability(
                name="continual_learning_market",
                domain=LearningDomain.MARKET,
                capability_type=LearningCapabilityType.CONTINUAL_LEARNING,
                location="system_core/indira_cognitive/indira_brain/continual_learning/continual_learning.py",
                status=CapabilityStatus.PRODUCTION,
                description="Continual learning for market data and trading signals"
            )
        )
        self._register_capability(
            LearningCapability(
                name="meta_learning_market",
                domain=LearningDomain.MARKET,
                capability_type=LearningCapabilityType.META_LEARNING,
                location="system_core/indira_cognitive/indira_brain/meta_learning/meta_learning.py",
                status=CapabilityStatus.PRODUCTION,
                description="Meta-learning for learning market trading strategies"
            )
        )
        self._register_capability(
            LearningCapability(
                name="transfer_learning_market",
                domain=LearningDomain.MARKET,
                capability_type=LearningCapabilityType.TRANSFER_LEARNING,
                location="system_core/indira_cognitive/indira_brain/transfer_learning/transfer_learning.py",
                status=CapabilityStatus.PRODUCTION,
                description="Transfer learning for applying knowledge across market domains"
            )
        )

    def _register_runtime_cognitive_capabilities(self):
        """Register runtime cognitive learning capabilities (Intelligence Engine)."""
        self._register_capability(
            LearningCapability(
                name="reinforcement_learning_engine",
                domain=LearningDomain.RUNTIME_COGNITIVE,
                capability_type=LearningCapabilityType.REINFORCEMENT_LEARNING,
                location="system_core/intelligence_engine/learning/reinforcement_engine.py",
                status=CapabilityStatus.PRODUCTION,
                description="Reinforcement learning engine for runtime cognitive processing"
            )
        )
        self._register_capability(
            LearningCapability(
                name="slow_loop_learning",
                domain=LearningDomain.RUNTIME_COGNITIVE,
                capability_type=LearningCapabilityType.ONLINE_LEARNING,
                location="system_core/intelligence_engine/learning/slow_loop.py",
                status=CapabilityStatus.PRODUCTION,
                description="Slow loop learning for gradual cognitive improvement"
            )
        )
        self._register_capability(
            LearningCapability(
                name="cognitive_governance_learning",
                domain=LearningDomain.RUNTIME_COGNITIVE,
                capability_type=LearningCapabilityType.SUPERVISED_LEARNING,
                location="system_core/intelligence_engine/learning/cognitive_governance.py",
                status=CapabilityStatus.PRODUCTION,
                description="Cognitive governance learning for runtime decision control"
            )
        )

    def _register_control_capabilities(self):
        """Register control learning capabilities (Governance)."""
        self._register_capability(
            LearningCapability(
                name="learning_evolution_loop",
                domain=LearningDomain.CONTROL,
                capability_type=LearningCapabilityType.META_LEARNING,
                location="system_core/governance_unified/control_plane/learning_evolution_loop.py",
                status=CapabilityStatus.PRODUCTION,
                description="Learning evolution loop in governance control plane"
            )
        )
        self._register_capability(
            LearningCapability(
                name="learning_coherence",
                domain=LearningDomain.CONTROL,
                capability_type=LearningCapabilityType.SUPERVISED_LEARNING,
                location="system_core/governance_unified/domains/cognitive/learning_coherence.py",
                status=CapabilityStatus.PRODUCTION,
                description="Learning coherence for cognitive governance"
            )
        )
        self._register_capability(
            LearningCapability(
                name="learning_truthfulness",
                domain=LearningDomain.CONTROL,
                capability_type=LearningCapabilityType.SUPERVISED_LEARNING,
                location="system_core/governance_unified/domains/cognitive/learning_truthfulness.py",
                status=CapabilityStatus.PRODUCTION,
                description="Learning truthfulness for cognitive governance"
            )
        )

    def _register_research_capabilities(self):
        """Register research/experimental learning capabilities (Development/Alternatives)."""
        # Cognitive Engine Meta-Learning
        self._register_capability(
            LearningCapability(
                name="meta_learner_alternative",
                domain=LearningDomain.RESEARCH_EXPERIMENTAL,
                capability_type=LearningCapabilityType.META_LEARNING,
                location="development/alternatives/cognitive_engine/meta_learning/meta_learner.py",
                status=CapabilityStatus.EXPERIMENTAL,
                description="Alternative meta-learning implementation for cognitive engine"
            )
        )

        # Intelligence Engine Learning
        self._register_capability(
            LearningCapability(
                name="lightweight_rl_alternative",
                domain=LearningDomain.RESEARCH_EXPERIMENTAL,
                capability_type=LearningCapabilityType.REINFORCEMENT_LEARNING,
                location="development/alternatives/intelligence_engine/learning/lightweight_rl.py",
                status=CapabilityStatus.EXPERIMENTAL,
                description="Alternative lightweight reinforcement learning implementation"
            )
        )
        self._register_capability(
            LearningCapability(
                name="performance_attribution_alternative",
                domain=LearningDomain.RESEARCH_EXPERIMENTAL,
                capability_type=LearningCapabilityType.SUPERVISED_LEARNING,
                location="development/alternatives/intelligence_engine/learning/performance_attribution.py",
                status=CapabilityStatus.EXPERIMENTAL,
                description="Alternative performance attribution implementation"
            )
        )

        # Stubs
        self._register_capability(
            LearningCapability(
                name="stub_learning",
                domain=LearningDomain.RESEARCH_EXPERIMENTAL,
                capability_type=LearningCapabilityType.SUPERVISED_LEARNING,
                location="development/stub_learning.py",
                status=CapabilityStatus.STUB,
                description="Stub learning implementation for development"
            )
        )

    def _register_independent_capabilities(self):
        """Register independent learning capabilities (Machine Learning)."""
        self._register_capability(
            LearningCapability(
                name="ml_trading_system",
                domain=LearningDomain.INDEPENDENT,
                capability_type=LearningCapabilityType.SUPERVISED_LEARNING,
                location="containers/machine_learning/ml_trading_system.py",
                status=CapabilityStatus.PRODUCTION,
                description="Standalone ML trading system"
            )
        )

    def _register_capability(self, capability: LearningCapability):
        """Register a learning capability in the catalog."""
        with self._lock:
            key = f"{capability.domain.value}:{capability.name}"
            self._capabilities[key] = capability
            logger.debug(f"[LEARNING_REGISTRY] Registered capability: {key}")

    def _update_domain_profiles(self):
        """Update domain learning profiles based on registered capabilities."""
        with self._lock:
            for domain in LearningDomain:
                profile = DomainLearningProfile(domain=domain)

                for capability in self._capabilities.values():
                    if capability.domain == domain:
                        profile.total_capabilities += 1

                        # Count capability types
                        if capability.capability_type not in profile.capability_types:
                            profile.capability_types[capability.capability_type] = 0
                        profile.capability_types[capability.capability_type] += 1

                        # Count by status
                        if capability.status == CapabilityStatus.PRODUCTION:
                            profile.production_capabilities += 1
                        elif capability.status == CapabilityStatus.DEVELOPMENT:
                            profile.development_capabilities += 1
                        elif capability.status == CapabilityStatus.EXPERIMENTAL:
                            profile.experimental_capabilities += 1

                self._domain_profiles[domain] = profile

    def discover_capabilities(self, domain: Optional[LearningDomain] = None) -> List[LearningCapability]:
        """Discover all available learning capabilities for a domain.

        Args:
            domain: Optional domain filter. If None, returns all capabilities.

        Returns:
            List of learning capabilities
        """
        with self._lock:
            if domain is None:
                return list(self._capabilities.values())
            return [cap for cap in self._capabilities.values() if cap.domain == domain]

    def get_capability(self, name: str, domain: LearningDomain) -> Optional[LearningCapability]:
        """Get a specific learning capability.

        Args:
            name: Capability name
            domain: Capability domain

        Returns:
            Learning capability if found, None otherwise
        """
        with self._lock:
            key = f"{domain.value}:{name}"
            return self._capabilities.get(key)

    def get_domain_profile(self, domain: LearningDomain) -> DomainLearningProfile:
        """Get learning profile for a specific domain.

        Args:
            domain: Domain to get profile for

        Returns:
            Domain learning profile
        """
        with self._lock:
            return self._domain_profiles.get(domain, DomainLearningProfile(domain))

    def get_all_domain_profiles(self) -> Dict[LearningDomain, DomainLearningProfile]:
        """Get all domain learning profiles.

        Returns:
            Dictionary mapping domains to their learning profiles
        """
        with self._lock:
            return self._domain_profiles.copy()

    def get_registry_summary(self) -> Dict[str, Any]:
        """Get comprehensive registry summary.

        Returns:
            Registry summary with statistics
        """
        with self._lock:
            total_capabilities = len(self._capabilities)

            by_status = {}
            for capability in self._capabilities.values():
                status = capability.status.value
                if status not in by_status:
                    by_status[status] = 0
                by_status[status] += 1

            by_type = {}
            for capability in self._capabilities.values():
                cap_type = capability.capability_type.value
                if cap_type not in by_type:
                    by_type[cap_type] = 0
                by_type[cap_type] += 1

            return {
                "total_capabilities": total_capabilities,
                "by_status": by_status,
                "by_type": by_type,
                "by_domain": {domain.value: profile.to_dict() for domain, profile in self._domain_profiles.items()},
                "last_updated": datetime.now().isoformat(),
            }


# Global registry instance
_learning_capability_registry: Optional[LearningCapabilityRegistry] = None


def get_learning_capability_registry() -> LearningCapabilityRegistry:
    """Get the global learning capability registry instance."""
    global _learning_capability_registry
    if _learning_capability_registry is None:
        _learning_capability_registry = LearningCapabilityRegistry()
    return _learning_capability_registry


__all__ = [
    "LearningDomain",
    "LearningCapabilityType",
    "CapabilityStatus",
    "LearningCapability",
    "DomainLearningProfile",
    "LearningCapabilityRegistry",
    "get_learning_capability_registry",
]