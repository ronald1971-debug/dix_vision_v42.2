"""governance_engine.hardening.invariants_state — canonical runtime registry.

Single source of truth for the active DIXVISION v42.2 architectural
invariant set.  Re-exports the authoritative definitions from
``core.contracts.invariants`` and adds lightweight policy-table helpers
so every enforcement layer (monitor, verifier, authority, docs) reads
from the same identifier set.

Rule:
  *Every new invariant is added to*
  ``core.contracts.invariants.InvariantID``
  *and documented in*
  ``docs/invariants_dixvision_v42.2.md``.
  No other form of ID registration is accepted.
"""

from __future__ import annotations

from dataclasses import dataclass

from core.contracts.invariants import INVARIANT_DOCS, InvariantID, describe

__all__ = [
    "InvariantID",
    "INVARIANT_DOCS",
    "describe",
    "InvariantDescription",
    "get_all_descriptions",
    "ids_to_check",
    "required_reality_domains",
]


@dataclass(frozen=True, slots=True)
class InvariantDescription:
    """Typed descriptor for an active invariant."""

    invariant_id: InvariantID
    severity: str = "MANDATORY"
    enforcement: str = "REVIEW"
    documented_in: str = "docs/invariants_dixvision_v42.2.md"

    def __post_init__(self) -> None:
        if self.severity not in ("MANDATORY", "ADVISORY", "DEPRECATED"):
            raise ValueError(
                f"InvariantDescription.severity must be MANDATORY|ADVISORY|DEPRECATED, "
                f"got {self.severity!r}"
            )
        if not self.documented_in:
            raise ValueError("InvariantDescription.documented_in must be non-empty")


# ---------------------------------------------------------------------------
# Policy tables (enrich core.contracts.invariants with enforcement taxonomy)
# ---------------------------------------------------------------------------

_ARCHITECTURAL: tuple[InvariantID, ...] = (
    InvariantID.DIX_01,
    InvariantID.DIX_02,
    InvariantID.DIX_03,
    InvariantID.DIX_04,
    InvariantID.DIX_05,
    InvariantID.DIX_10,
    InvariantID.DIX_13,
)

_COGNITIVE: tuple[InvariantID, ...] = (
    InvariantID.DIX_02,
    InvariantID.DIX_03,
    InvariantID.DIX_11,
    InvariantID.DIX_14,
    InvariantID.DIX_15,
    InvariantID.DIX_16,
)

_RUNTIME_AUTO: tuple[InvariantID, ...] = (
    InvariantID.DIX_02,
    InvariantID.DIX_06,
    InvariantID.DIX_08,
    InvariantID.DIX_12,
)

_ALL_IDS: tuple[InvariantID, ...] = tuple(InvariantID)


def get_all_descriptions() -> tuple[InvariantDescription, ...]:
    """Return metadata for every registered invariant."""
    out: list[InvariantDescription] = []
    for inv in _ALL_IDS:
        if inv in _ARCHITECTURAL:
            enforcement = "CODE + DRIFT-KILLER"
        elif inv in _RUNTIME_AUTO:
            enforcement = "CODE"
        else:
            enforcement = "DOC + REVIEW"
        out.append(
            InvariantDescription(
                invariant_id=inv,
                severity="MANDATORY",
                enforcement=enforcement,
            )
        )
    return tuple(out)


def ids_to_check() -> tuple[InvariantID, ...]:
    """Return invariant IDs that must be exercised by tests / docs diff."""
    return (
        InvariantID.DIX_01,
        InvariantID.DIX_02,
        InvariantID.DIX_03,
        InvariantID.DIX_16,
    )


def required_reality_domains() -> tuple[str, ...]:
    """Reality domains defined by INV-DIX-02 / BeliefState."""
    return (
        "market_reality",
        "trader_reality",
        "strategy_reality",
        "portfolio_reality",
        "execution_reality",
        "regime_reality",
        "system_reality",
    )
