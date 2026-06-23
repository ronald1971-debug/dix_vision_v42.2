"""Belief validation — INV-DIX-02 enforcement.

Validates that belief updates conform to the BeliefState contract.
"""

from __future__ import annotations

from core.belief_engine.updates import BeliefUpdate


def validate_belief_state(update: BeliefUpdate) -> tuple[bool, str]:
    """Validate a belief update.

    Returns:
        (valid, error_message) tuple.
    """
    valid_domains = {
        "market_intelligence",
        "trader_intelligence",
        "strategy_intelligence",
        "portfolio_intelligence",
        "allocation_intelligence",
        "position_intelligence",
        "execution_feedback_intelligence",
        "repository_intelligence",
        "architecture_intelligence",
        "runtime_intelligence",
        "infrastructure_intelligence",
    }

    if update.domain not in valid_domains:
        return False, f"Invalid domain: {update.domain}"

    # INV-DIX-03: INDIRA owns market/trader/strategy/portfolio
    # INV-DIX-04: DYON owns system cognition
    indira_domains = {
        "market_intelligence",
        "trader_intelligence",
        "strategy_intelligence",
        "portfolio_intelligence",
        "allocation_intelligence",
        "position_intelligence",
        "execution_feedback_intelligence",
    }

    dyon_domains = {
        "repository_intelligence",
        "architecture_intelligence",
        "runtime_intelligence",
        "infrastructure_intelligence",
    }

    if update.engine == "dyon" and update.domain in indira_domains:
        return False, f"INV-DIX-05 violation: DYON may not publish to {update.domain}"

    if update.engine in ("indira", "intelligence_engine") and update.domain in dyon_domains:
        return False, f"INV-DIX-04 violation: INDIRA may not publish to {update.domain}"

    return True, ""


__all__ = [
    "validate_belief_state",
]
