"""Governance services — adjacent (non-control-plane) modules."""

from __future__ import annotations

from governance_unified.services.patch_pipeline_bridge import (
    PatchApprovalBridge,
    PatchApprovalDecision,
)

__all__ = ["PatchApprovalBridge", "PatchApprovalDecision"]
