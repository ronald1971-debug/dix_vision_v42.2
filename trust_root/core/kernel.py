"""Trust Root Core - Foundation Hash Lifecycle Management.

This component provides the cryptographic foundation for system trust,
including hash lifecycle management, verification artifacts, and trust anchors.

Design Principles:
- INV-15: No external dependencies where possible
- INV-08: Pure trust logic where possible
- Thread-safe operations
- Cryptographic security best practices
- Lean verification artifacts
"""

from __future__ import annotations

import dataclasses
import enum
import hashlib
import logging
import threading
from collections.abc import Mapping
from types import MappingProxyType
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    pass

_logger = logging.getLogger(__name__)


class HashAlgorithm(str, enum.Enum):
    """Cryptographic hash algorithms supported."""

    SHA256 = "SHA256"
    SHA512 = "SHA512"
    SHA3_256 = "SHA3_256"
    BLAKE2B = "BLAKE2B"


class TrustStatus(str, enum.Enum):
    """Status of trust verification."""

    VERIFIED = "VERIFIED"
    UNVERIFIED = "UNVERIFIED"
    REVOKED = "REVOKED"
    PENDING = "PENDING"
    COMPROMISED = "COMPROMISED"


@dataclasses.dataclass(frozen=True, slots=True)
class FoundationHash:
    """A foundation hash for system trust.

    Fields:
        hash_id: Unique identifier for this hash
        hash_value: The cryptographic hash value
        hash_algorithm: Algorithm used to generate the hash
        component: Component this hash represents
        version: Component version
        timestamp_ns: Hash creation timestamp
        previous_hash: Previous hash in the chain (for integrity)
        metadata: Additional metadata
    """

    hash_id: str
    hash_value: str
    hash_algorithm: HashAlgorithm
    component: str
    version: str
    timestamp_ns: int
    previous_hash: str | None = None
    metadata: Mapping[str, str] = dataclasses.field(default_factory=lambda: MappingProxyType({}))

    def __post_init__(self) -> None:
        if not self.hash_id:
            raise ValueError("FoundationHash.hash_id must be non-empty")
        if not self.hash_value:
            raise ValueError("FoundationHash.hash_value must be non-empty")
        if not isinstance(self.metadata, MappingProxyType):
            object.__setattr__(self, "metadata", MappingProxyType(dict(self.metadata)))


@dataclasses.dataclass(frozen=True, slots=True)
class VerificationArtifact:
    """A lean verification artifact for trust validation.

    Fields:
        artifact_id: Unique identifier for this artifact
        hash_id: Associated foundation hash
        verification_method: Method used for verification
        verification_data: Verification-specific data
        signature: Digital signature (if applicable)
        timestamp_ns: Verification timestamp
        status: Verification status
    """

    artifact_id: str
    hash_id: str
    verification_method: str
    verification_data: Mapping[str, str] = dataclasses.field(default_factory=lambda: MappingProxyType({}))
    signature: str | None = None
    timestamp_ns: int = 0
    status: TrustStatus = TrustStatus.VERIFIED

    def __post_init__(self) -> None:
        if not self.artifact_id:
            raise ValueError("VerificationArtifact.artifact_id must be non-empty")
        if not isinstance(self.verification_data, MappingProxyType):
            object.__setattr__(
                self, "verification_data", MappingProxyType(dict(self.verification_data))
            )


@dataclasses.dataclass(frozen=True, slots=True)
class TrustAnchor:
    """A cryptographic trust anchor for the system.

    Fields:
        anchor_id: Unique identifier for this anchor
        public_key: The public key material
        key_type: Type of cryptographic key
        trust_level: Trust level (0.0-1.0)
        expiry_ns: Expiration timestamp
        purpose: Purpose of this trust anchor
        metadata: Additional metadata
    """

    anchor_id: str
    public_key: str
    key_type: str
    trust_level: float
    expiry_ns: int
    purpose: str
    metadata: Mapping[str, str] = dataclasses.field(default_factory=lambda: MappingProxyType({}))

    def __post_init__(self) -> None:
        if not self.anchor_id:
            raise ValueError("TrustAnchor.anchor_id must be non-empty")
        if not self.public_key:
            raise ValueError("TrustAnchor.public_key must be non-empty")
        if not 0.0 <= self.trust_level <= 1.0:
            raise ValueError(f"TrustAnchor.trust_level must be 0.0-1.0, got {self.trust_level}")
        if not isinstance(self.metadata, MappingProxyType):
            object.__setattr__(self, "metadata", MappingProxyType(dict(self.metadata)))


@dataclasses.dataclass(frozen=True, slots=True)
class IntegrityResult:
    """Result of system integrity verification.

    Fields:
        verification_id: Unique identifier for this verification
        component: Component verified
        integrity_score: Overall integrity score (0.0-1.0)
        hash_valid: Whether the foundation hash is valid
        chain_intact: Whether the hash chain is intact
        verified_artifacts: Number of verified artifacts
        issues_found: List of issues found
        timestamp_ns: Verification timestamp
    """

    verification_id: str
    component: str
    integrity_score: float
    hash_valid: bool
    chain_intact: bool
    verified_artifacts: int
    issues_found: tuple[str, ...] = ()
    timestamp_ns: int = 0

    def __post_init__(self) -> None:
        if not 0.0 <= self.integrity_score <= 1.0:
            raise ValueError(
                f"IntegrityResult.integrity_score must be 0.0-1.0, got {self.integrity_score}"
            )


class FoundationHashLifecycle:
    """Manages the lifecycle of foundation hashes for system trust.

    This component provides:
    - Hash generation for system components
    - Hash chain management for integrity
    - Hash rotation and lifecycle management
    - Rollback validation
    """

    def __init__(self) -> None:
        self._lock: threading.Lock = threading.Lock()
        self._hashes: dict[str, FoundationHash] = {}
        self._hash_chains: dict[str, list[str]] = {}  # component -> chain of hash_ids
        self._current_hashes: dict[str, str] = {}  # component -> current hash_id
        self._total_hashes_generated: int = 0

    def generate_foundation_hash(
        self,
        component: str,
        version: str,
        data: bytes,
        algorithm: HashAlgorithm = HashAlgorithm.SHA256,
        previous_hash: str | None = None,
    ) -> FoundationHash:
        """Generate a foundation hash for a component.

        Args:
            component: Component to hash
            version: Component version
            data: Component data to hash
            algorithm: Hash algorithm to use
            previous_hash: Previous hash for chain integrity

        Returns:
            FoundationHash for the component
        """
        # Generate hash
        hash_value = self._compute_hash(data, algorithm)

        # Create hash ID
        hash_id = self._generate_hash_id(component, version, algorithm)

        # Create foundation hash
        timestamp_ns = self._get_timestamp()
        foundation_hash = FoundationHash(
            hash_id=hash_id,
            hash_value=hash_value,
            hash_algorithm=algorithm,
            component=component,
            version=version,
            timestamp_ns=timestamp_ns,
            previous_hash=previous_hash,
        )

        # Store hash
        with self._lock:
            self._hashes[hash_id] = foundation_hash
            self._current_hashes[component] = hash_id
            self._total_hashes_generated += 1

            # Update hash chain
            if component not in self._hash_chains:
                self._hash_chains[component] = []
            self._hash_chains[component].append(hash_id)

        _logger.info(
            "Generated foundation hash for %s@%s using %s: %s",
            component,
            version,
            algorithm.value,
            hash_id,
        )

        return foundation_hash

    def verify_system_integrity(self, component: str) -> IntegrityResult:
        """Verify the integrity of a system component.

        Args:
            component: Component to verify

        Returns:
            IntegrityResult with verification details
        """
        verification_id = f"verify_{component}_{self._get_timestamp()}"

        with self._lock:
            # Get current hash for component
            current_hash_id = self._current_hashes.get(component)
            if not current_hash_id:
                return IntegrityResult(
                    verification_id=verification_id,
                    component=component,
                    integrity_score=0.0,
                    hash_valid=False,
                    chain_intact=False,
                    verified_artifacts=0,
                    issues_found=(f"No hash found for component {component}",),
                    timestamp_ns=self._get_timestamp(),
                )

            current_hash = self._hashes.get(current_hash_id)
            if not current_hash:
                return IntegrityResult(
                    verification_id=verification_id,
                    component=component,
                    integrity_score=0.0,
                    hash_valid=False,
                    chain_intact=False,
                    verified_artifacts=0,
                    issues_found=(f"Hash {current_hash_id} not found in storage",),
                    timestamp_ns=self._get_timestamp(),
                )

            # Verify hash chain integrity
            chain_intact = self._verify_hash_chain(component)

            # Check hash validity (placeholder - would verify against component data)
            hash_valid = True  # TODO: Implement actual hash verification

            # Calculate integrity score
            integrity_score = self._calculate_integrity_score(hash_valid, chain_intact)

            return IntegrityResult(
                verification_id=verification_id,
                component=component,
                integrity_score=integrity_score,
                hash_valid=hash_valid,
                chain_intact=chain_intact,
                verified_artifacts=len(self._hash_chains.get(component, [])),
                timestamp_ns=self._get_timestamp(),
            )

    def rollback_validation(
        self,
        old_hash: str,
        new_hash: str,
    ) -> bool:
        """Validate whether a rollback is safe.

        Args:
            old_hash: Previous hash to roll back to
            new_hash: Current hash to roll back from

        Returns:
            True if rollback is safe, False otherwise
        """
        with self._lock:
            # Check if both hashes exist
            if old_hash not in self._hashes or new_hash not in self._hashes:
                return False

            # Verify rollback would maintain integrity
            # TODO: Implement sophisticated rollback validation
            return True

    def get_hash_chain(self, component: str) -> list[FoundationHash]:
        """Get the hash chain for a component.

        Args:
            component: Component to get chain for

        Returns:
            List of FoundationHash objects in chain order
        """
        with self._lock:
            hash_ids = self._hash_chains.get(component, [])
            return [self._hashes[hash_id] for hash_id in hash_ids if hash_id in self._hashes]

    def get_trust_statistics(self) -> dict[str, int]:
        """Get trust root statistics."""
        with self._lock:
            return {
                "total_hashes_generated": self._total_hashes_generated,
                "active_hashes": len(self._hashes),
                "components_with_hashes": len(self._current_hashes),
                "total_hash_chains": len(self._hash_chains),
            }

    # ------------------------------------------------------------------
    # Private methods
    # ------------------------------------------------------------------

    def _compute_hash(self, data: bytes, algorithm: HashAlgorithm) -> str:
        """Compute cryptographic hash of data."""
        if algorithm == HashAlgorithm.SHA256:
            return hashlib.sha256(data).hexdigest()
        elif algorithm == HashAlgorithm.SHA512:
            return hashlib.sha512(data).hexdigest()
        elif algorithm == HashAlgorithm.SHA3_256:
            return hashlib.sha3_256(data).hexdigest()
        elif algorithm == HashAlgorithm.BLAKE2B:
            return hashlib.blake2b(data).hexdigest()
        else:
            raise ValueError(f"Unsupported hash algorithm: {algorithm}")

    def _generate_hash_id(self, component: str, version: str, algorithm: HashAlgorithm) -> str:
        """Generate unique hash ID."""
        timestamp = self._get_timestamp()
        return f"hash_{component}_{version}_{algorithm.value}_{timestamp}"

    def _verify_hash_chain(self, component: str) -> bool:
        """Verify that the hash chain is intact."""
        hash_ids = self._hash_chains.get(component, [])
        if len(hash_ids) < 2:
            return True  # Chain too short to verify

        # Verify each hash links to the previous one
        for i in range(1, len(hash_ids)):
            current = self._hashes.get(hash_ids[i])
            previous = self._hashes.get(hash_ids[i - 1])

            if not current or not previous:
                return False

            if current.previous_hash != previous.hash_value:
                _logger.warning(
                    "Hash chain broken for %s at position %d", component, i
                )
                return False

        return True

    def _calculate_integrity_score(self, hash_valid: bool, chain_intact: bool) -> float:
        """Calculate overall integrity score."""
        base_score = 1.0

        if not hash_valid:
            base_score -= 0.4

        if not chain_intact:
            base_score -= 0.3

        return max(0.0, min(1.0, base_score))

    def _get_timestamp(self) -> int:
        """Get current timestamp in nanoseconds."""
        # In production, this would use the system time source
        return 0  # TODO: Integrate with proper time source


# Singleton instance
_singleton: FoundationHashLifecycle | None = None
_lock = threading.Lock()


def get_foundation_hash_lifecycle() -> FoundationHashLifecycle:
    """Get the singleton foundation hash lifecycle instance."""
    global _singleton
    if _singleton is None:
        with _lock:
            if _singleton is None:
                _singleton = FoundationHashLifecycle()
    return _singleton


__all__ = [
    "FoundationHashLifecycle",
    "get_foundation_hash_lifecycle",
    "FoundationHash",
    "VerificationArtifact",
    "TrustAnchor",
    "IntegrityResult",
    "HashAlgorithm",
    "TrustStatus",
]