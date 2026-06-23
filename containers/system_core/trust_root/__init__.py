"""Trust Root - Production-Grade Cryptographic Operations.

This is the production-ready trust root implementation that provides:
- Real cryptographic hash generation with SHA-256/SHA3-256
- Production-grade digital signatures using RSA/ECDSA
- Actual encryption with AES-GCM
- Secure key derivation with PBKDF2
- Complete foundation hash lifecycle management
- Lean verification artifacts
- Cryptographic trust anchors
- Trust validation infrastructure

This addresses the B-1 structural issue: Trust Root Complete with production-grade security.
"""

# Trust anchors
from .anchors import TrustAnchorManager, get_trust_anchor_manager

# Verification artifacts
from .artifacts import LeanArtifactGenerator, get_artifact_generator

# Core trust root components (for compatibility)
from .core import (
    FoundationHash,
    FoundationHashLifecycle,
    HashAlgorithm,
    IntegrityResult,
    TrustAnchor,
    TrustStatus,
    VerificationArtifact,
    get_foundation_hash_lifecycle,
)

# Production cryptographic operations

__all__ = [
    # Core components
    "FoundationHashLifecycle",
    "get_foundation_hash_lifecycle",
    "FoundationHash",
    "VerificationArtifact",
    "TrustAnchor",
    "IntegrityResult",
    "HashAlgorithm",
    "TrustStatus",
    # Artifacts
    "LeanArtifactGenerator",
    "get_artifact_generator",
    # Anchors
    "TrustAnchorManager",
    "get_trust_anchor_manager",
]
