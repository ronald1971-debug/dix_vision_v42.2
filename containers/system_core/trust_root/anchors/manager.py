"""Cryptographic Trust Anchors Management.

Manages trust anchors for cryptographic operations and system security.
"""

from __future__ import annotations

import dataclasses
import logging
import threading
from collections.abc import Mapping
from types import MappingProxyType
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from trust_root.core.kernel import TrustAnchor, TrustStatus

_logger = logging.getLogger(__name__)


class TrustAnchorManager:
    """Manages cryptographic trust anchors for the system.

    This component provides:
    - Trust anchor registration and management
    - Key lifecycle management
    - Trust level validation
    - Anchor revocation and rotation
    """

    def __init__(self) -> None:
        self._lock: threading.Lock = threading.Lock()
        self._anchors: dict[str, TrustAnchor] = {}
        self._anchor_purposes: dict[str, list[str]] = {}  # purpose -> anchor_ids
        self._total_anchors_registered: int = 0

    def register_anchor(self, anchor: TrustAnchor) -> bool:
        """Register a trust anchor.

        Args:
            anchor: Trust anchor to register

        Returns:
            True if registration successful, False otherwise
        """
        with self._lock:
            if anchor.anchor_id in self._anchors:
                _logger.warning(f"Anchor {anchor.anchor_id} already registered")
                return False

            self._anchors[anchor.anchor_id] = anchor

            # Update purpose index
            if anchor.purpose not in self._anchor_purposes:
                self._anchor_purposes[anchor.purpose] = []
            self._anchor_purposes[anchor.purpose].append(anchor.anchor_id)

            self._total_anchors_registered += 1

        _logger.info(
            "Registered trust anchor %s for purpose %s (trust level: %.2f)",
            anchor.anchor_id,
            anchor.purpose,
            anchor.trust_level,
        )

        return True

    def revoke_anchor(self, anchor_id: str) -> bool:
        """Revoke a trust anchor.

        Args:
            anchor_id: Anchor ID to revoke

        Returns:
            True if revocation successful, False otherwise
        """
        with self._lock:
            if anchor_id not in self._anchors:
                return False

            anchor = self._anchors[anchor_id]
            purpose = anchor.purpose

            # Remove from anchors
            del self._anchors[anchor_id]

            # Remove from purpose index
            if purpose in self._anchor_purposes and anchor_id in self._anchor_purposes[purpose]:
                self._anchor_purposes[purpose].remove(anchor_id)

            if not self._anchor_purposes[purpose]:
                del self._anchor_purposes[purpose]

        _logger.info("Revoked trust anchor %s", anchor_id)
        return True

    def get_anchor(self, anchor_id: str) -> TrustAnchor | None:
        """Get a trust anchor by ID.

        Args:
            anchor_id: Anchor ID to retrieve

        Returns:
            TrustAnchor if found, None otherwise
        """
        with self._lock:
            return self._anchors.get(anchor_id)

    def get_anchors_by_purpose(self, purpose: str) -> list[TrustAnchor]:
        """Get all anchors for a specific purpose.

        Args:
            purpose: Purpose to filter by

        Returns:
            List of TrustAnchor objects
        """
        with self._lock:
            anchor_ids = self._anchor_purposes.get(purpose, [])
            return [
                self._anchors[anchor_id]
                for anchor_id in anchor_ids
                if anchor_id in self._anchors
            ]

    def validate_trust_level(self, anchor_id: str, required_level: float) -> bool:
        """Validate that an anchor meets required trust level.

        Args:
            anchor_id: Anchor to validate
            required_level: Required trust level (0.0-1.0)

        Returns:
            True if anchor meets or exceeds required level, False otherwise
        """
        with self._lock:
            anchor = self._anchors.get(anchor_id)
            if not anchor:
                return False

            return anchor.trust_level >= required_level

    def check_anchor_expiry(self) -> list[str]:
        """Check for expired anchors and return their IDs.

        Returns:
            List of expired anchor IDs
        """
        current_ns = self._get_timestamp()
        expired_anchors: list[str] = []

        with self._lock:
            for anchor_id, anchor in self._anchors.items():
                if anchor.expiry_ns < current_ns:
                    expired_anchors.append(anchor_id)

        if expired_anchors:
            _logger.warning(
                "Found %d expired trust anchors: %s",
                len(expired_anchors),
                expired_anchors,
            )

        return expired_anchors

    def get_statistics(self) -> dict[str, int]:
        """Get trust anchor statistics."""
        with self._lock:
            return {
                "total_anchors_registered": self._total_anchors_registered,
                "active_anchors": len(self._anchors),
                "purposes_supported": len(self._anchor_purposes),
            }

    # ------------------------------------------------------------------
    # Private methods
    # ------------------------------------------------------------------

    def _get_timestamp(self) -> int:
        """Get current timestamp in nanoseconds."""
        # In production, this would use the system time source
        return 0  # TODO: Integrate with proper time source


# Singleton instance
_singleton: TrustAnchorManager | None = None
_lock = threading.Lock()


def get_trust_anchor_manager() -> TrustAnchorManager:
    """Get the singleton trust anchor manager instance."""
    global _singleton
    if _singleton is None:
        with _lock:
            if _singleton is None:
                _singleton = TrustAnchorManager()
    return _singleton


__all__ = [
    "TrustAnchorManager",
    "get_trust_anchor_manager",
]