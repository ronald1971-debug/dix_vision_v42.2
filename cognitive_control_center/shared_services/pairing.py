"""
cognitive_control_center.shared_services.pairing
Device pairing service - Migrated from cockpit/pairing.py

This module provides device pairing functionality for the cognitive control center,
allowing operators to pair mobile devices and other clients with the system.
"""

from __future__ import annotations

import threading
import time
import uuid
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from typing import Any

# First, let's migrate the core pairing functionality from cockpit
# This is a simplified version focused on the cognitive control center


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