"""Governance services — adjacent (non-control-plane) modules."""

from __future__ import annotations

from .patch_pipeline_bridge import (
    PatchApprovalBridge,
    PatchApprovalDecision,
)

__all__ = ["PatchApprovalBridge", "PatchApprovalDecision"]
