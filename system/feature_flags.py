"""
system.feature_flags
DIX VISION v42.2 — System Feature Flags

Feature flags for enabling/disabling system components at runtime.
This provides safety mechanisms for gradual rollout and emergency disabling.
"""

from __future__ import annotations

import os
from dataclasses import dataclass
from enum import Enum


class FeatureStatus(Enum):
    """Status of a feature flag."""
    ENABLED = "enabled"
    DISABLED = "disabled"
    READ_ONLY = "read_only"
    SHADOW_MODE = "shadow_mode"


@dataclass
class FeatureFlag:
    """A feature flag with its current status."""
    name: str
    status: FeatureStatus
    description: str
    requires_restart: bool = False


class CognitiveFeatureFlags:
    """Feature flags for cognitive subsystems - ALL FEATURES ENABLED AND ACTIVE."""
    
    # Core cognitive features
    COGNITIVE_ENRICHMENT = FeatureFlag(
        name="COGNITIVE_ENRICHMENT",
        status=FeatureStatus.ENABLED,
        description="Enrich market data with cognitive insights",
        requires_restart=False
    )
    
    COGNITIVE_RISK_ASSESSMENT = FeatureFlag(
        name="COGNITIVE_RISK_ASSESSMENT", 
        status=FeatureStatus.ENABLED,
        description="Use cognitive simulation for risk assessment",
        requires_restart=False
    )
    
    # Hypothesis engine
    HYPOTHESIS_AUTO_GENERATION = FeatureFlag(
        name="HYPOTHESIS_AUTO_GENERATION",
        status=FeatureStatus.ENABLED,
        description="Automatically generate hypotheses from patterns",
        requires_restart=False
    )
    
    HYPOTHESIS_VALIDATION = FeatureFlag(
        name="HYPOTHESIS_VALIDATION",
        status=FeatureStatus.ENABLED,
        description="Validate hypotheses using backtesting",
        requires_restart=False
    )
    
    # Knowledge graph
    KNOWLEDGE_GRAPH_AUTO_POPULATION = FeatureFlag(
        name="KNOWLEDGE_GRAPH_AUTO_POPULATION",
        status=FeatureStatus.ENABLED,
        description="Automatically populate knowledge graph from trading data",
        requires_restart=False
    )
    
    KNOWLEDGE_GRAPH_QUERIES = FeatureFlag(
        name="KNOWLEDGE_GRAPH_QUERIES",
        status=FeatureStatus.ENABLED,
        description="Query knowledge graph for trading context",
        requires_restart=False
    )
    
    # Narrative engine
    NARRATIVE_DETECTION = FeatureFlag(
        name="NARRATIVE_DETECTION",
        status=FeatureStatus.ENABLED,
        description="Detect market narratives from news and social media",
        requires_restart=False
    )
    
    NARRATIVE_IMPACT_ASSESSMENT = FeatureFlag(
        name="NARRATIVE_IMPACT_ASSESSMENT",
        status=FeatureStatus.ENABLED,
        description="Assess narrative impact on trading decisions",
        requires_restart=False
    )
    
    # Curiosity engine
    CURIOSITY_INVESTIGATION = FeatureFlag(
        name="CURIOSITY_INVESTIGATION",
        status=FeatureStatus.ENABLED,
        description="Enable curiosity-driven investigation automation",
        requires_restart=False
    )
    
    INVESTIGATION_AUTO_SUBMIT = FeatureFlag(
        name="INVESTIGATION_AUTO_SUBMIT",
        status=FeatureStatus.ENABLED,
        description="Automatically submit high-priority investigations",
        requires_restart=False
    )
    
    # Meta-governance
    META_GOVERNANCE_OVERSIGHT = FeatureFlag(
        name="META_GOVERNANCE_OVERSIGHT",
        status=FeatureStatus.ENABLED,
        description="Enable meta-governance oversight of decisions",
        requires_restart=False
    )
    
    META_GOVERNANCE_OVERRIDE = FeatureFlag(
        name="META_GOVERNANCE_OVERRIDE",
        status=FeatureStatus.ENABLED,
        description="Allow meta-governance to override trading decisions",
        requires_restart=False
    )
    
    # Attention engine
    ATTENTION_RESOURCE_ALLOCATION = FeatureFlag(
        name="ATTENTION_RESOURCE_ALLOCATION",
        status=FeatureStatus.ENABLED,
        description="Enable attention-based resource allocation",
        requires_restart=False
    )
    
    # Cognitive health
    COGNITIVE_HEALTH_MONITORING = FeatureFlag(
        name="COGNITIVE_HEALTH_MONITORING",
        status=FeatureStatus.ENABLED,
        description="Monitor cognitive system health and drift",
        requires_restart=False
    )
    
    COGNITIVE_DRIFT_CORRECTION = FeatureFlag(
        name="COGNITIVE_DRIFT_CORRECTION",
        status=FeatureStatus.ENABLED,
        description="Enable automatic correction of cognitive drift",
        requires_restart=False
    )


class RuntimeFeatureFlags:
    """Feature flags for runtime system."""
    
    # Runtime convergence
    RUNTIME_CONVERGENCE_ENABLED = FeatureFlag(
        name="RUNTIME_CONVERGENCE_ENABLED",
        status=FeatureStatus.ENABLED,
        description="Enable runtime convergence layer",
        requires_restart=True
    )
    
    SESSION_RECORDING = FeatureFlag(
        name="SESSION_RECORDING",
        status=FeatureStatus.ENABLED,
        description="Record sessions for deterministic replay",
        requires_restart=False
    )
    
    REPLAY_VALIDATION = FeatureFlag(
        name="REPLAY_VALIDATION",
        status=FeatureStatus.ENABLED,
        description="Enable replay validation",
        requires_restart=False
    )
    
    # Market feed
    WEBSOCKET_FEED = FeatureFlag(
        name="WEBSOCKET_FEED",
        status=FeatureStatus.ENABLED,
        description="Use WebSocket market feeds when available",
        requires_restart=False
    )
    
    SOURCE_REGISTRY = FeatureFlag(
        name="SOURCE_REGISTRY",
        status=FeatureStatus.ENABLED,
        description="Enable unified source registry for all data feeds",
        requires_restart=False
    )
    
    # Enforcement
    ENFORCEMENT_GATE = FeatureFlag(
        name="ENFORCEMENT_GATE",
        status=FeatureStatus.ENABLED,
        description="Enable enforcement gate with blocking policies",
        requires_restart=False
    )
    
    KILL_SWITCH = FeatureFlag(
        name="KILL_SWITCH",
        status=FeatureStatus.ENABLED,
        description="Enable kill switch mechanism",
        requires_restart=False
    )


class FeatureFlagManager:
    """Manages feature flags with environment variable override support."""
    
    @staticmethod
    def get_status(flag: FeatureFlag) -> FeatureStatus:
        """Get the current status of a feature flag with environment override."""
        # Check for environment variable override
        env_var = f"DIX_{flag.name}"
        env_value = os.environ.get(env_var, "").upper()
        
        if env_value:
            try:
                return FeatureStatus(env_value)
            except ValueError:
                # Invalid environment value, use default
                pass
        
        return flag.status
    
    @staticmethod
    def is_enabled(flag: FeatureFlag) -> bool:
        """Check if a feature flag is enabled."""
        status = FeatureFlagManager.get_status(flag)
        return status in (FeatureStatus.ENABLED, FeatureStatus.SHADOW_MODE, FeatureStatus.READ_ONLY)
    
    @staticmethod
    def is_active(flag: FeatureFlag) -> bool:
        """Check if a feature flag is active (not disabled)."""
        status = FeatureFlagManager.get_status(flag)
        return status != FeatureStatus.DISABLED
    
    @staticmethod
    def can_modify(flag: FeatureFlag) -> bool:
        """Check if a feature can modify system behavior."""
        status = FeatureFlagManager.get_status(flag)
        return status == FeatureStatus.ENABLED
    
    @staticmethod
    def set_status(flag: FeatureFlag, status: FeatureStatus) -> None:
        """Set the status of a feature flag (runtime modification only)."""
        if flag.requires_restart:
            raise RuntimeError(f"Cannot modify flag {flag.name} at runtime (requires restart)")
        
        flag.status = status
    
    @staticmethod
    def get_all_flags() -> dict[str, FeatureFlag]:
        """Get all feature flags."""
        flags = {}
        
        # Cognitive flags
        for attr_name in dir(CognitiveFeatureFlags):
            if not attr_name.startswith("_"):
                attr = getattr(CognitiveFeatureFlags, attr_name)
                if isinstance(attr, FeatureFlag):
                    flags[f"COGNITIVE_{attr_name}"] = attr
        
        # Runtime flags
        for attr_name in dir(RuntimeFeatureFlags):
            if not attr_name.startswith("_"):
                attr = getattr(RuntimeFeatureFlags, attr_name)
                if isinstance(attr, FeatureFlag):
                    flags[f"RUNTIME_{attr_name}"] = attr
        
        return flags
    
    @staticmethod
    def get_flag_report() -> str:
        """Generate a report of all feature flags and their status."""
        flags = FeatureFlagManager.get_all_flags()
        
        report_lines = ["=== FEATURE FLAG REPORT ===", ""]
        
        for flag_name, flag in sorted(flags.items()):
            status = FeatureFlagManager.get_status(flag)
            active_indicator = "✓" if FeatureFlagManager.is_active(flag) else "✗"
            modify_indicator = "→" if FeatureFlagManager.can_modify(flag) else "→"
            
            report_lines.append(
                f"{active_indicator} {modify_indicator} {flag_name}: {status.value}"
            )
            report_lines.append(f"    Description: {flag.description}")
            if flag.requires_restart:
                report_lines.append(f"    ⚠ Requires restart to change")
            report_lines.append("")
        
        return "\n".join(report_lines)


def get_feature_flag_manager() -> FeatureFlagManager:
    """Get the feature flag manager instance."""
    return FeatureFlagManager()


__all__ = [
    "CognitiveFeatureFlags",
    "FeatureFlag",
    "FeatureFlagManager", 
    "FeatureStatus",
    "RuntimeFeatureFlags",
    "get_feature_flag_manager",
]