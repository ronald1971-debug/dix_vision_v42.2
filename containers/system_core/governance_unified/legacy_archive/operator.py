"""Operator Governance Domain.

Manages operator-level overrides, session controls,
and human-in-the-loop approval requirements.
"""

from __future__ import annotations

from dataclasses import dataclass, field

from governance_unified.policy_rule import PolicyRule


@dataclass
class OperatorGovernancePolicy:
    require_operator_approval_above: float = 100_000.0
    session_timeout_seconds: float = 28800.0  # 8 hours
    allowed_symbols: list[str] = field(default_factory=list)
    blocked_symbols: list[str] = field(default_factory=list)
    max_trades_per_session: int = 1000

    def to_rules(self) -> list[PolicyRule]:
        rules = [
            PolicyRule(
                name="operator_trade_limit",
                domain="operator",
                description="Maximum trades per session",
            ),
        ]
        if self.allowed_symbols:
            rules.append(
                PolicyRule(
                    name="operator_symbol_whitelist",
                    domain="operator",
                    description=f"Allowed symbols: {', '.join(self.allowed_symbols)}",
                )
            )
        return rules
