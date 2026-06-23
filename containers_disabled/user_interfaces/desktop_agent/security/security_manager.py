"""
DIX VISION v42.2+ Desktop Agent - Security Manager with World Context Integration
Security management and access control with world understanding
"""

from __future__ import annotations

import logging
import os
import sys
from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional

# Try to import world model components for world context integration
try:
    sys.path.append(os.path.join(os.path.dirname(__file__), "..", "..", ".."))
    from world_model.indicator_integration import get_integration_bridge

    WORLD_MODEL_AVAILABLE = True
except ImportError:
    WORLD_MODEL_AVAILABLE = False


@dataclass
class WorldContext:
    """World model context for security decisions."""

    market_regime: str  # bullish, bearish, sideways, high_volatility
    market_trend: str  # trending, mean_reverting
    volatility_regime: str  # high, normal, low
    liquidity_state: str  # high, normal, low
    agent_activity: Dict[str, float]  # agent_type -> activity_level
    causal_factors: List[str]  # relevant causal factors
    prediction_confidence: float  # world model prediction confidence
    timestamp: datetime

    def to_dict(self) -> dict:
        """Convert to dictionary for processing."""
        return {
            "market_regime": self.market_regime,
            "market_trend": self.market_trend,
            "volatility_regime": self.volatility_regime,
            "liquidity_state": self.liquidity_state,
            "agent_activity": self.agent_activity,
            "causal_factors": self.causal_factors,
            "prediction_confidence": self.prediction_confidence,
            "timestamp": self.timestamp.isoformat(),
        }


class SecurityLevel(Enum):
    """Security clearance levels."""

    GUEST = "guest"
    USER = "user"
    ADMIN = "admin"
    SUPER_ADMIN = "super_admin"


class SecurityManager:
    """Manager for security policies and access control with world context integration."""

    def __init__(self):
        """Initialize the Security Manager."""
        self.logger = logging.getLogger("security_manager")
        self.logger.setLevel(logging.INFO)

        self._security_policies: Dict[str, Dict[str, Any]] = {}
        self._user_permissions: Dict[str, List[str]] = {}
        self._world_integration_bridge = None
        self._world_context_cache: Optional[WorldContext] = None
        self._world_context_cache_time: Optional[datetime] = None

        self.logger.info("Security Manager initialized")

    async def initialize(self, config: Optional[Dict[str, Any]] = None) -> bool:
        """Initialize the security manager."""
        try:
            # Initialize world model integration
            if WORLD_MODEL_AVAILABLE:
                try:
                    self._world_integration_bridge = get_integration_bridge()
                    self.logger.info("World context integration initialized for security")
                except Exception as e:
                    self.logger.warning(f"Failed to initialize world context integration: {e}")

            self.logger.info("Security Manager initialized successfully")
            return True
        except Exception as e:
            self.logger.error(f"Failed to initialize Security Manager: {e}")
            return False

    def get_status(self) -> Dict[str, Any]:
        """Get the current status of the security manager."""
        return {
            "total_policies": len(self._security_policies),
            "total_permissions": len(self._user_permissions),
            "world_integration_enabled": self._world_integration_bridge is not None,
        }

    # World Context Integration Methods

    def get_world_context(self) -> Optional[WorldContext]:
        """Get current world context from world model integration."""
        if not WORLD_MODEL_AVAILABLE or not self._world_integration_bridge:
            return None

        # Check cache validity (30 seconds)
        if (
            self._world_context_cache
            and self._world_context_cache_time
            and (datetime.utcnow() - self._world_context_cache_time).total_seconds() < 30
        ):
            return self._world_context_cache

        try:
            # Get world model predictions and state
            bridge = self._world_integration_bridge

            if bridge:
                # Build world context from bridge metrics
                # For now, return a default context
                context = WorldContext(
                    market_regime="sideways",
                    market_trend="neutral",
                    volatility_regime="normal",
                    liquidity_state="high",
                    agent_activity={},
                    causal_factors=[],
                    prediction_confidence=0.75,
                    timestamp=datetime.utcnow(),
                )

                # Update cache
                self._world_context_cache = context
                self._world_context_cache_time = datetime.utcnow()

                return context

        except Exception as e:
            self.logger.error(f"Error getting world context: {e}")

        return None

    def evaluate_security_policy_with_world_context(
        self,
        policy_id: str,
        user_id: str,
        action: str,
        world_context: Optional[WorldContext] = None,
    ) -> Dict[str, Any]:
        """
        Evaluate security policy with world context enhancement.

        ENHANCED: World context integration for intelligent security decisions
        """
        # Get world context if not provided
        if not world_context:
            world_context = self.get_world_context()

        # Evaluate standard security policy
        result = self._evaluate_standard_security_policy(policy_id, user_id, action)

        # Enhance with world context if available
        if world_context:
            result["world_context_applied"] = True
            result["world_context"] = world_context.to_dict()

            # Apply world-aware security adjustments
            if world_context.volatility_regime == "high":
                result["security_level"] = "elevated"
                result["additional_factors"] = ["high_volatility_regime"]

            if world_context.agent_activity.get("anomalous", 0) > 0.7:
                result["security_level"] = "strict"
                result["additional_factors"].append("anomalous_agent_activity")

        return result

    def _evaluate_standard_security_policy(
        self, policy_id: str, user_id: str, action: str
    ) -> Dict[str, Any]:
        """Evaluate standard security policy without world context."""
        # Placeholder for standard policy evaluation
        # In production, this would evaluate against actual security policies
        return {
            "allowed": True,
            "policy_id": policy_id,
            "user_id": user_id,
            "action": action,
            "security_level": "standard",
            "additional_factors": [],
        }


class AccessControl:
    """Access control for system resources with world context integration."""

    def __init__(self):
        """Initialize Access Control."""
        self.logger = logging.getLogger("access_control")
        self.logger.setLevel(logging.INFO)

        self._access_rules: Dict[str, Dict[str, Any]] = {}
        self._world_integration_bridge = None
        self._world_context_cache: Optional[WorldContext] = None
        self._world_context_cache_time: Optional[datetime] = None

        self.logger.info("Access Control initialized")

    async def initialize(self, config: Optional[Dict[str, Any]] = None) -> bool:
        """Initialize access control."""
        try:
            # Initialize world model integration
            if WORLD_MODEL_AVAILABLE:
                try:
                    self._world_integration_bridge = get_integration_bridge()
                    self.logger.info("World context integration initialized for access control")
                except Exception as e:
                    self.logger.warning(f"Failed to initialize world context integration: {e}")

            self.logger.info("Access Control initialized successfully")
            return True
        except Exception as e:
            self.logger.error(f"Failed to initialize Access Control: {e}")
            return False

    def get_status(self) -> Dict[str, Any]:
        """Get the current status of access control."""
        return {
            "total_rules": len(self._access_rules),
            "world_integration_enabled": self._world_integration_bridge is not None,
        }

    # World Context Integration Methods

    def check_access_with_world_context(
        self, user_id: str, resource: str, action: str, world_context: Optional[WorldContext] = None
    ) -> Dict[str, Any]:
        """
        Check access permissions with world context enhancement.

        ENHANCED: World context integration for intelligent access control
        """
        # Get world context if not provided
        if not world_context:
            world_context = self._get_world_context()

        # Check standard access rules
        result = self._check_standard_access(user_id, resource, action)

        # Enhance with world context if available
        if world_context:
            result["world_context_applied"] = True
            result["world_context"] = world_context.to_dict()

            # Apply world-aware access restrictions
            if world_context.volatility_regime == "high" and action in ["write", "delete"]:
                result["allowed"] = False
                result["reason"] = "high_volatility_restriction"
                result["additional_factors"] = ["high_volatility_regime"]

            if world_context.liquidity_state == "low" and resource == "trading":
                result["allowed"] = False
                result["reason"] = "low_liquidity_restriction"
                if "additional_factors" not in result:
                    result["additional_factors"] = []
                result["additional_factors"].append("low_liquidity_state")

        return result

    def _get_world_context(self) -> Optional[WorldContext]:
        """Get current world context from world model integration."""
        if not WORLD_MODEL_AVAILABLE or not self._world_integration_bridge:
            return None

        # Check cache validity (30 seconds)
        if (
            self._world_context_cache
            and self._world_context_cache_time
            and (datetime.utcnow() - self._world_context_cache_time).total_seconds() < 30
        ):
            return self._world_context_cache

        try:
            bridge = self._world_integration_bridge
            if bridge:
                context = WorldContext(
                    market_regime="sideways",
                    market_trend="neutral",
                    volatility_regime="normal",
                    liquidity_state="high",
                    agent_activity={},
                    causal_factors=[],
                    prediction_confidence=0.75,
                    timestamp=datetime.utcnow(),
                )

                # Update cache
                self._world_context_cache = context
                self._world_context_cache_time = datetime.utcnow()

                return context

        except Exception as e:
            self.logger.error(f"Error getting world context: {e}")

        return None

    def _check_standard_access(self, user_id: str, resource: str, action: str) -> Dict[str, Any]:
        """Check standard access rules without world context."""
        # Placeholder for standard access check
        # In production, this would check against actual access rules
        return {
            "allowed": True,
            "user_id": user_id,
            "resource": resource,
            "action": action,
            "access_level": "standard",
            "reason": "standard_access_granted",
        }


class AuditLogger:
    """Logger for security audit events with world context integration."""

    def __init__(self):
        """Initialize Audit Logger."""
        self.logger = logging.getLogger("audit_logger")
        self.logger.setLevel(logging.INFO)

        self._audit_events: List[Dict[str, Any]] = []
        self._world_integration_bridge = None
        self._world_context_cache: Optional[WorldContext] = None
        self._world_context_cache_time: Optional[datetime] = None

        self.logger.info("Audit Logger initialized")

    async def initialize(self, config: Optional[Dict[str, Any]] = None) -> bool:
        """Initialize audit logger."""
        try:
            # Initialize world model integration
            if WORLD_MODEL_AVAILABLE:
                try:
                    self._world_integration_bridge = get_integration_bridge()
                    self.logger.info("World context integration initialized for audit logging")
                except Exception as e:
                    self.logger.warning(f"Failed to initialize world context integration: {e}")

            self.logger.info("Audit Logger initialized successfully")
            return True
        except Exception as e:
            self.logger.error(f"Failed to initialize Audit Logger: {e}")
            return False

    def get_status(self) -> Dict[str, Any]:
        """Get the current status of the audit logger."""
        return {
            "total_events": len(self._audit_events),
            "world_integration_enabled": self._world_integration_bridge is not None,
        }

    # World Context Integration Methods

    def log_security_event_with_world_context(
        self,
        event_type: str,
        user_id: str,
        details: Dict[str, Any],
        world_context: Optional[WorldContext] = None,
    ) -> str:
        """
        Log a security event with world context enhancement.

        ENHANCED: World context integration for intelligent audit logging
        """
        # Get world context if not provided
        if not world_context:
            world_context = self._get_world_context()

        # Create enhanced audit event
        event = {
            "event_id": self._generate_event_id(),
            "event_type": event_type,
            "user_id": user_id,
            "timestamp": datetime.utcnow().isoformat(),
            "details": details,
            "world_context_applied": world_context is not None,
        }

        # Add world context if available
        if world_context:
            event["world_context"] = world_context.to_dict()
            event["security_assessment"] = self._assess_security_risk(world_context, event_type)

        # Store the event
        self._audit_events.append(event)

        self.logger.info(f"Security event logged: {event_type} by user {user_id}")

        return event["event_id"]

    def _get_world_context(self) -> Optional[WorldContext]:
        """Get current world context from world model integration."""
        if not WORLD_MODEL_AVAILABLE or not self._world_integration_bridge:
            return None

        # Check cache validity (30 seconds)
        if (
            self._world_context_cache
            and self._world_context_cache_time
            and (datetime.utcnow() - self._world_context_cache_time).total_seconds() < 30
        ):
            return self._world_context_cache

        try:
            bridge = self._world_integration_bridge
            if bridge:
                context = WorldContext(
                    market_regime="sideways",
                    market_trend="neutral",
                    volatility_regime="normal",
                    liquidity_state="high",
                    agent_activity={},
                    causal_factors=[],
                    prediction_confidence=0.75,
                    timestamp=datetime.utcnow(),
                )

                # Update cache
                self._world_context_cache = context
                self._world_context_cache_time = datetime.utcnow()

                return context

        except Exception as e:
            self.logger.error(f"Error getting world context: {e}")

        return None

    def _assess_security_risk(self, world_context: WorldContext, event_type: str) -> Dict[str, Any]:
        """Assess security risk based on world context and event type."""
        risk_level = "low"
        risk_factors = []

        # Assess based on volatility
        if world_context.volatility_regime == "high":
            risk_level = "elevated"
            risk_factors.append("high_volatility_regime")

        # Assess based on event type
        if event_type in ["authentication", "access_grant", "privilege_escalation"]:
            if world_context.agent_activity.get("anomalous", 0) > 0.7:
                risk_level = "high"
                risk_factors.append("anomalous_agent_activity")

        # Assess based on liquidity
        if world_context.liquidity_state == "low" and event_type == "trading_action":
            risk_level = "elevated"
            risk_factors.append("low_liquidity_state")

        return {
            "risk_level": risk_level,
            "risk_factors": risk_factors,
            "assessment_timestamp": datetime.utcnow().isoformat(),
        }

    def _generate_event_id(self) -> str:
        """Generate a unique event ID."""
        import uuid

        return f"audit_{uuid.uuid4().hex[:16]}"

    def get_audit_events(self, limit: int = 100) -> List[Dict[str, Any]]:
        """Get recent audit events."""
        return self._audit_events[-limit:]
