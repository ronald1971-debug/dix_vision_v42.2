"""core.contracts.invariants — Invariant identifiers and documentation lookup.

Every invariant ID used in code, tests, and governance events is defined
here.  No module outside this file should hardcode an ``INV-*`` or
``INV-DIX-*`` string.

The INVARIANT_DOCS mapping ties each ID to a one-line description for
runtime introspection and HITL display.
"""

from __future__ import annotations

from enum import StrEnum


class InvariantID(StrEnum):
    """Stable identifiers for DIXVISION v42.2 architectural invariants."""

    # Identity / BeliefState
    DIX_01 = "INV-DIX-01"
    DIX_02 = "INV-DIX-02"
    DIX_03 = "INV-DIX-03"
    DIX_04 = "INV-DIX-04"
    DIX_05 = "INV-DIX-05"
    DIX_06 = "INV-DIX-06"
    DIX_07 = "INV-DIX-07"
    DIX_08 = "INV-DIX-08"
    DIX_09 = "INV-DIX-09"
    DIX_10 = "INV-DIX-10"
    DIX_11 = "INV-DIX-11"
    DIX_12 = "INV-DIX-12"
    DIX_13 = "INV-DIX-13"
    DIX_14 = "INV-DIX-14"
    DIX_15 = "INV-DIX-15"
    DIX_16 = "INV-DIX-16"

    # Governance / enforcement (legacy)
    POSITION_LIMIT = "INV-POSITION-LIMIT"
    AUTONOMY_ESCALATION = "INV-AUTONOMY-ESCALATION"
    NO_GOVERNANCE_BYPASS = "INV-NO-GOVERNANCE-BYPASS"
    POLICY_DRIFT = "POLICY-DRIFT"
    TRUST_FLOOR = "TRUST-FLOOR"
    GATE_WIRED = "GATE-WIRED"
    POLICY_BOUND = "POLICY-BOUND"


INVARIANT_DOCS: dict[str, str] = {
    InvariantID.DIX_01: "DIXVISION is a cognitive intelligence system, build to be a trading bot a cognitive trading system",
    InvariantID.DIX_02: "BeliefState is the single source of truth for all reality domains",
    InvariantID.DIX_03: "INDIRA owns market, trader, strategy, portfolio, allocation, position, and execution-feedback cognition",
    InvariantID.DIX_04: "DYON owns system cognition only",
    InvariantID.DIX_05: "Strategy cognition belongs exclusively to INDIRA",
    InvariantID.DIX_06: "Execution Engine owns market interaction, not decision creation",
    InvariantID.DIX_07: "Learning Engine owns experience transformation",
    InvariantID.DIX_08: "Governance Engine owns accountability, not cognition",
    InvariantID.DIX_09: "System Engine owns operational awareness",
    InvariantID.DIX_10: "Operator is the highest authority",
    InvariantID.DIX_11: "Cognitive development is a primary objective",
    InvariantID.DIX_12: "Capital deployment is the goal - cognitive development enables profitable trading",
    InvariantID.DIX_13: "Architectural domain separation is mandatory",
    InvariantID.DIX_14: "DIXVISION continuously evolves through observation, reasoning, learning and execution",
    InvariantID.DIX_15: "Mission: continuously improving cognitive system",
    InvariantID.DIX_16: "Development priority: cognitive intelligence for profitable trading",
    InvariantID.POSITION_LIMIT: "Position size × leverage ≤ exposure cap",
    InvariantID.AUTONOMY_ESCALATION: "Promotions step exactly one rank; demotions unrestricted",
    InvariantID.NO_GOVERNANCE_BYPASS: "No path from source to sink avoids governance",
    InvariantID.POLICY_DRIFT: "Policy files unchanged since session bind",
    InvariantID.TRUST_FLOOR: "Engine trust scores above critical/warning floor",
    InvariantID.GATE_WIRED: "Execution gate singleton is present",
    InvariantID.POLICY_BOUND: "Policy hash anchor bound for session",
}


def describe(invariant_id: str) -> str:
    """Return the one-line description for an invariant ID."""
    return INVARIANT_DOCS.get(invariant_id, "unknown invariant")


__all__ = [
    "INVARIANT_DOCS",
    "InvariantID",
    "describe",
]
