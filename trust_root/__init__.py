"""Trust Root - Complete Foundation Hash Lifecycle and Verification.

This is the comprehensive trust root implementation that provides:
- Foundation hash lifecycle management
- Lean verification artifacts
- Cryptographic trust anchors
- Trust validation infrastructure

This addresses the B-1 structural issue: Trust Root Incomplete from the analysis.
"""

# Core trust root components
from .core import (
    FoundationHashLifecycle,
    get_foundation_hash_lifecycle,
    FoundationHash,
    VerificationArtifact,
    TrustAnchor,
    IntegrityResult,
    HashAlgorithm,
    TrustStatus,
)

# Verification artifacts
from .artifacts import LeanArtifactGenerator, get_artifact_generator

# Trust anchors
from .anchors import TrustAnchorManager, get_trust_anchor_manager

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
