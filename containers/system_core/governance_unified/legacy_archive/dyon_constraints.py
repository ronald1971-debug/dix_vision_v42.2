"""DYON Constraints — INV-DIX-04 enforcement.

Stage 7 — DYON Constraints

DYON may:
  - refactor
  - optimize
  - test
  - improve infrastructure

DYON may not:
  - change governance
  - change invariants
  - change authority boundaries

without operator approval.
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum


class DyonError(StrEnum):
    """DYON constraint violation codes."""

    GOVERNANCE_MUTATION = "DYON-GOVERNANCE-MUTATION"
    INVARIANTS_MUTATION = "DYON-INVARIANTS-MUTATION"
    AUTHORITY_BOUNDARY = "DYON-AUTHORITY-BOUNDARY"
    STRATEGY_GENERATION = "DYON-STRATEGY-GENERATION"
    DIRECT_EXECUTION = "DYON-DIRECT-EXECUTION"


@dataclass(frozen=True, slots=True)
class DyonConstraintCheck:
    """Result of checking a DYON action against constraints."""

    allowed: bool
    constraint: DyonError | None
    reason: str
    ts_ns: int


# Capabilities DYON is allowed to perform autonomously
DYON_ALLOWED_CAPABILITIES: set[str] = {
    "refactor",
    "optimize",
    "test",
    "improve_infrastructure",
    "scan_architecture",
    "detect_drift",
    "emit_hazard",
    "propose_patch",  # Proposals must go through governance
}

# Capabilities DYON may NOT perform without operator approval
DYON_RESTRICTED_CAPABILITIES: set[str] = {
    "modify_governance",
    "change_invariants",
    "change_authority_boundaries",
    "strategy_generation",  # INV-DIX-05
    "direct_execution",  # INV-DIX-12
    "approve_patch",  # Only operator can approve
}

# Actions requiring explicit operator approval
DYON_OPERATOR_APPROVAL_REQUIRED: set[str] = {
    "propose_patch_merge",  # Patch proposals must be approved
    "change_invariants",
    "change_authority_boundaries",
    "modify_governance",
}


def check_dyon_action(
    capability: str,
    ts_ns: int,
    requires_approval: bool = False,
) -> DyonConstraintCheck:
    """Check if DYON may perform a capability.

    Args:
        capability: The action DYON wants to perform.
        ts_ns: Timestamp of the check.
        requires_approval: Whether this action must have prior operator approval.

    Returns:
        DyonConstraintCheck with allowed status and any violation reason.
    """
    if capability in DYON_ALLOWED_CAPABILITIES and not requires_approval:
        return DyonConstraintCheck(
            allowed=True,
            constraint=None,
            reason="autonomous_action_permitted",
            ts_ns=ts_ns,
        )

    if capability in DYON_RESTRICTED_CAPABILITIES:
        if requires_approval:
            return DyonConstraintCheck(
                allowed=True,
                constraint=None,
                reason="operator_approved",
                ts_ns=ts_ns,
            )
        return DyonConstraintCheck(
            allowed=False,
            constraint=_map_capability_to_error(capability),
            reason=f"DYON may not {capability} without operator approval (INV-DIX-04)",
            ts_ns=ts_ns,
        )

    return DyonConstraintCheck(
        allowed=False,
        constraint=DyonError.GOVERNANCE_MUTATION,
        reason=f"Unknown capability: {capability}",
        ts_ns=ts_ns,
    )


def _map_capability_to_error(capability: str) -> DyonError:
    """Map a restricted capability to its error code."""
    if capability in ("change_invariants", "modify_invariants"):
        return DyonError.INVARIANTS_MUTATION
    if capability in ("change_authority_boundaries", "modify_authority"):
        return DyonError.AUTHORITY_BOUNDARY
    if capability in ("modify_governance", "change_governance"):
        return DyonError.GOVERNANCE_MUTATION
    if capability == "strategy_generation":
        return DyonError.STRATEGY_GENERATION
    if capability == "direct_execution":
        return DyonError.DIRECT_EXECUTION
    return DyonError.GOVERNANCE_MUTATION


def require_operator_approval(capability: str) -> bool:
    """Check if a capability requires operator approval before DYON may act."""
    return capability in DYON_OPERATOR_APPROVAL_REQUIRED


__all__ = [
    "COMPILED_RULES",  # Re-export from policy_compiler
    "DYON_ALLOWED_CAPABILITIES",
    "DYON_OPERATOR_APPROVAL_REQUIRED",
    "DYON_RESTRICTED_CAPABILITIES",
    "DyonError",
    "DyonConstraintCheck",
    "check_dyon_action",
    "require_operator_approval",
]

# Import COMPILED_RULES from policy_compiler for module consumers
from governance_unified.policy_compiler import COMPILED_RULES
