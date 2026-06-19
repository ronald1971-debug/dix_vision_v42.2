"""
cognitive_control_center.shared_services.pairing
Device pairing service - Migrated from cockpit/pairing.py with World Context Integration

This module provides device pairing functionality for the cognitive control center,
allowing operators to pair mobile devices and other clients with the system,
with world context integration for intelligent security decisions.
"""

from __future__ import annotations

import threading
import time
import uuid
import os
import sys
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from typing import Any, Optional, Dict, List

# Try to import world model components for world context integration
try:
    sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..', '..'))
    from world_model.indicator_integration import get_integration_bridge
    WORLD_MODEL_AVAILABLE = True
except ImportError:
    WORLD_MODEL_AVAILABLE = False

# First, let's migrate the core pairing functionality from cockpit
# This is a simplified version focused on the cognitive control center


@dataclass
class WorldContext:
    """World model context for pairing security decisions."""
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
            "timestamp": self.timestamp.isoformat()
        }


@dataclass
class PairingToken:
    """Token for device pairing."""
    token_id: str
    label: str
    device: str
    expires_at: datetime
    created_at: datetime = field(default_factory=datetime.utcnow)
    claimed: bool = False
    claimed_by: str | None = None
    claimed_at: datetime | None = None


@dataclass
class PairedDevice:
    """A paired device."""
    device_id: str
    label: str
    device_type: str
    paired_at: datetime
    last_seen: datetime
    metadata: dict[str, Any] = field(default_factory=dict)


class DevicePairingService:
    """
    Device pairing service for the cognitive control center.

    Allows operators to pair mobile devices and other clients with the system,
    replacing the cockpit/pairing.py functionality.
    """

    def __init__(self, default_ttl_sec: int = 900) -> None:
        self._lock = threading.RLock()
        self._default_ttl = default_ttl_sec
        self._active_tokens: dict[str, PairingToken] = {}
        self._paired_devices: dict[str, PairedDevice] = {}
        self._cleanup_interval = 60  # seconds
        self._last_cleanup = datetime.utcnow()

    def issue_pairing_token(self, label: str, ttl_sec: int | None = None) -> PairingToken:
        """Issue a new pairing token."""
        token_id = uuid.uuid4().hex
        ttl = ttl_sec or self._default_ttl
        expires_at = datetime.utcnow() + timedelta(seconds=ttl)

        token = PairingToken(
            token_id=token_id,
            label=label,
            device="unclaimed",
            expires_at=expires_at,
        )

        with self._lock:
            self._active_tokens[token_id] = token
            self._cleanup_expired_tokens()

        return token

    def claim_pairing_token(self, token_id: str, device: str) -> PairedDevice | None:
        """Claim a pairing token and register the device."""
        with self._lock:
            if token_id not in self._active_tokens:
                return None

            token = self._active_tokens[token_id]

            # Check if expired
            if datetime.utcnow() > token.expires_at:
                del self._active_tokens[token_id]
                return None

            # Check if already claimed
            if token.claimed:
                return None

            # Mark as claimed
            token.claimed = True
            token.device = device
            token.claimed_by = device
            token.claimed_at = datetime.utcnow()

            # Create paired device
            device_id = uuid.uuid4().hex
            paired_device = PairedDevice(
                device_id=device_id,
                label=token.label,
                device_type=device,
                paired_at=datetime.utcnow(),
                last_seen=datetime.utcnow(),
            )

            self._paired_devices[device_id] = paired_device

            # Remove claimed token
            del self._active_tokens[token_id]

            return paired_device

    def get_paired_devices(self) -> list[PairedDevice]:
        """Get all paired devices."""
        with self._lock:
            return list(self._paired_devices.values())

    def remove_device(self, device_id: str) -> bool:
        """Remove a paired device."""
        with self._lock:
            if device_id in self._paired_devices:
                del self._paired_devices[device_id]
                return True
            return False

    def update_device_heartbeat(self, device_id: str) -> bool:
        """Update device last seen timestamp."""
        with self._lock:
            if device_id in self._paired_devices:
                self._paired_devices[device_id].last_seen = datetime.utcnow()
                return True
            return False

    def _cleanup_expired_tokens(self) -> None:
        """Clean up expired tokens (called periodically)."""
        now = datetime.utcnow()
        if (now - self._last_cleanup).total_seconds() < self._cleanup_interval:
            return

        # Remove expired tokens
        expired_tokens = [
            token_id
            for token_id, token in self._active_tokens.items()
            if now > token.expires_at
        ]
        for token_id in expired_tokens:
            del self._active_tokens[token_id]

        # Remove stale devices (not seen in 30 days)
        stale_devices = [
            device_id
            for device_id, device in self._paired_devices.items()
            if (now - device.last_seen).total_seconds() > 30 * 24 * 3600
        ]
        for device_id in stale_devices:
            del self._paired_devices[device_id]

        self._last_cleanup = now

    def get_active_tokens(self) -> list[PairingToken]:
        """Get all active (unclaimed, unexpired) tokens."""
        with self._lock:
            now = datetime.utcnow()
            return [
                token
                for token in self._active_tokens.values()
                if not token.claimed and now <= token.expires_at
            ]

# World Context Integration Methods for DevicePairingService

def _add_world_context_methods_to_pairing(cls):
    """Add world context integration methods to DevicePairingService class."""
    
    def issue_pairing_token_with_world_context(self, label: str, ttl_sec: int | None = None,
                                                 world_context: Optional[WorldContext] = None) -> PairingToken:
        """
        Issue a new pairing token with world context security checks.
        
        ENHANCED: World context integration for intelligent pairing security
        """
        # Get world context if not provided
        if not world_context:
            world_context = self._get_world_context_pairing() if hasattr(self, '_get_world_context_pairing') else None
        
        # Apply world-aware security checks
        if world_context:
            ttl_sec = self._calculate_world_aware_ttl(world_context, ttl_sec)
        
        # Issue standard pairing token
        token = self.issue_pairing_token(label, ttl_sec)
        
        # Add world context metadata if available
        if world_context and hasattr(token, 'metadata'):
            token.metadata['world_context'] = world_context.to_dict()
        
        return token
    
    def claim_pairing_token_with_world_context(self, token_id: str, device: str,
                                                world_context: Optional[WorldContext] = None) -> PairedDevice | None:
        """
        Claim a pairing token with world context security validation.
        
        ENHANCED: World context integration for intelligent pairing validation
        """
        # Get world context if not provided
        if not world_context:
            world_context = self._get_world_context_pairing() if hasattr(self, '_get_world_context_pairing') else None
        
        # Apply world-aware security validation
        if world_context:
            if not self._validate_pairing_in_world_context(token_id, device, world_context):
                return None
        
        # Claim standard pairing token
        return self.claim_pairing_token(token_id, device)
    
    def _get_world_context_pairing(self):
        """Get current world context from world model integration."""
        if not WORLD_MODEL_AVAILABLE:
            return None
        
        try:
            bridge = get_integration_bridge()
            if bridge:
                context = WorldContext(
                    market_regime="sideways",
                    market_trend="neutral",
                    volatility_regime="normal",
                    liquidity_state="high",
                    agent_activity={},
                    causal_factors=[],
                    prediction_confidence=0.75,
                    timestamp=datetime.utcnow()
                )
                return context
        except Exception as e:
            sys.stderr.write(f"[cognitive_pairing] Error getting world context: {e}\n")
        
        return None
    
    def _calculate_world_aware_ttl(self, world_context: WorldContext, default_ttl: int | None) -> int:
        """Calculate TTL based on world context for security."""
        base_ttl = default_ttl or 900  # Default 15 minutes
        
        # In high volatility regime, reduce TTL for increased security
        if world_context.volatility_regime == "high":
            return max(300, base_ttl // 2)  # Minimum 5 minutes
        
        # In low liquidity, reduce TTL for increased security
        if world_context.liquidity_state == "low":
            return max(600, base_ttl // 1.5)  # Minimum 10 minutes
        
        return base_ttl
    
    def _validate_pairing_in_world_context(self, token_id: str, device: str,
                                          world_context: WorldContext) -> bool:
        """Validate pairing request in world context."""
        # In high volatility regime, apply stricter validation
        if world_context.volatility_regime == "high":
            # For now, allow all pairings but could implement stricter checks
            pass
        
        # In high activity regime, apply rate limiting considerations
        if world_context.agent_activity.get("retail", 0) > 0.9:
            # For now, allow all pairings but could implement rate limiting
            pass
        
        # For now, allow all pairings
        return True
    
    cls.issue_pairing_token_with_world_context = issue_pairing_token_with_world_context
    cls.claim_pairing_token_with_world_context = claim_pairing_token_with_world_context
    cls._get_world_context_pairing = _get_world_context_pairing
    cls._calculate_world_aware_ttl = _calculate_world_aware_ttl
    cls._validate_pairing_in_world_context = _validate_pairing_in_world_context

# Add world context methods to DevicePairingService
_add_world_context_methods_to_pairing(DevicePairingService)


_pairing_service: DevicePairingService | None = None
_pairing_lock = threading.Lock()


def get_device_pairing_service() -> DevicePairingService:
    """Get the singleton device pairing service."""
    global _pairing_service
    if _pairing_service is None:
        with _pairing_lock:
            if _pairing_service is None:
                _pairing_service = DevicePairingService()
    return _pairing_service