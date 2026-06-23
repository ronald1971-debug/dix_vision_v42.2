"""Policy Compiler — Converts architectural invariants to executable rules.

Stage 6 — Governance Policy Compiler

Converts INV-DIX-01..05 into executable rules that Governance Engine
understands and enforces at runtime.

Domain ownership is loaded from contracts/ownership_registry.yaml via
ownership_registry_loader.py to ensure consistent enforcement.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Literal

from core.contracts.invariants import InvariantID

# Lazy-load domain definitions from registry
_POLICY_REGISTRY_CACHE: dict | None = None


def _load_registry() -> dict:
    """Load ownership registry."""
    global _POLICY_REGISTRY_CACHE
    if _POLICY_REGISTRY_CACHE is None:
        try:
            from tools.ownership_registry_loader import load_registry

            _POLICY_REGISTRY_CACHE = load_registry()
        except Exception:
            _POLICY_REGISTRY_CACHE = {}
    return _POLICY_REGISTRY_CACHE


@dataclass(frozen=True, slots=True)
class PolicyRule:
    """Executable rule derived from an invariant."""

    invariant_id: str
    action: Literal["deny", "allow", "require", "warn"]
    target_engine: str
    target_capability: str
    rationale: str


def _build_policy_rules() -> tuple[PolicyRule, ...]:
    """Build COMPILED_RULES from registry with hardcoded fallback."""
    registry = _load_registry()
    engines = registry.get("engines", {})

    indira_domains = tuple(
        engines.get("indira", {}).get(
            "owns",
            [
                "market_intelligence",
                "trader_intelligence",
                "strategy_intelligence",
                "portfolio_intelligence",
                "allocation_intelligence",
                "position_intelligence",
                "execution_feedback_intelligence",
            ],
        )
    )

    dyon_domains = tuple(
        engines.get("dyon", {}).get(
            "owns",
            [
                "repository_intelligence",
                "architecture_intelligence",
                "runtime_intelligence",
                "infrastructure_intelligence",
            ],
        )
    )

    rules: list[PolicyRule] = [
        PolicyRule(
            invariant_id=InvariantID.DIX_01,
            action="deny",
            target_engine="any",
            target_capability="direct_capital_movement",
            rationale="DIXVISION is cognitive, not trading. Capital paths must route through governance.",
        ),
        PolicyRule(
            invariant_id=InvariantID.DIX_02,
            action="require",
            target_engine="any",
            target_capability="belief_state_publish",
            rationale="All reality domains must publish through BeliefState contract. No hidden realities.",
        ),
    ]

    # Add domain ownership rules from registry
    for domain in indira_domains:
        rules.append(
            PolicyRule(
                invariant_id=InvariantID.DIX_03,
                action="deny",
                target_engine="dyon",
                target_capability=domain,
                rationale=f"DYON owns system cognition only. INV-DIX-03 violation (domain: {domain}).",
            )
        )

    for domain in dyon_domains:
        rules.append(
            PolicyRule(
                invariant_id=InvariantID.DIX_04,
                action="deny",
                target_engine="indira",
                target_capability=domain,
                rationale=f"INDIRA owns market cognition only. INV-DIX-04 violation (domain: {domain}).",
            )
        )

    rules.extend(
        [
            PolicyRule(
                invariant_id=InvariantID.DIX_05,
                action="deny",
                target_engine="dyon",
                target_capability="strategy_generation",
                rationale="Strategy cognition belongs exclusively to INDIRA. INV-DIX-05 violation.",
            ),
            PolicyRule(
                invariant_id=InvariantID.DIX_06,
                action="deny",
                target_engine="execution_engine",
                target_capability="decision_creation",
                rationale="Execution owns interaction, not decisions. INV-DIX-06 violation.",
            ),
            PolicyRule(
                invariant_id=InvariantID.DIX_12,
                action="deny",
                target_engine="any",
                target_capability="cognitive_to_capital_direct",
                rationale="Capital deployment is separate from cognitive development. INV-DIX-12 violation.",
            ),
            PolicyRule(
                invariant_id=InvariantID.DIX_13,
                action="deny",
                target_engine="any",
                target_capability="cross_domain_bypass",
                rationale="Architectural domain separation is mandatory. INV-DIX-13 violation.",
            ),
        ]
    )

    return tuple(rules)


COMPILED_RULES: tuple[PolicyRule, ...] = _build_policy_rules()


def compile_invariant(invariant_id: str) -> tuple[PolicyRule, ...]:
    """Return executable rules for an invariant ID."""
    return tuple(r for r in COMPILED_RULES if r.invariant_id == invariant_id)


def check_policy_violation(engine: str, capability: str, ts_ns: int) -> tuple[bool, str | None]:
    """Check if an engine/capability pair violates any invariant.

    Returns:
        (allowed, violation_reason) tuple.
        allowed=False if any rule denies the action.
    """
    for rule in COMPILED_RULES:
        if rule.action == "deny":
            if rule.target_engine == "any" or rule.target_engine == engine:
                if rule.target_capability == capability:
                    return False, f"{rule.invariant_id}: {rule.rationale}"
    return True, None


__all__ = [
    "COMPILED_RULES",
    "PolicyRule",
    "check_policy_violation",
    "compile_invariant",
]
