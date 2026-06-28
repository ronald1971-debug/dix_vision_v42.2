"""Verification Artifacts.

Lean verification artifact generation and management.
"""

from .generator import LeanArtifactGenerator, get_artifact_generator

__all__ = [
    "LeanArtifactGenerator",
    "get_artifact_generator",
]
