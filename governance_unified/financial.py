"""Financial Governance Domain.

Governs capital allocation, position sizing, drawdown limits,
and risk budgets.
"""

from __future__ import annotations

from dataclasses import dataclass

from governance_unified.mcos_kernel import PolicyRule


@dataclass
class FinancialGovernancePolicy:
    max_portfolio_risk_pct: float = 0.02
    max_single_position_pct: float = 0.05
    max_daily_loss_pct: float = 0.03
    max_drawdown_pct: float = 0.10
    min_cash_reserve_pct: float = 0.20

    def to_rules(self) -> list[PolicyRule]:
        return [
            PolicyRule(
                name="max_position_size",
                domain="financial",
                description="Maximum single position as % of portfolio",
                max_position_pct=self.max_single_position_pct,
            ),
            PolicyRule(
                name="max_daily_loss",
                domain="financial",
                description="Maximum daily loss before halt",
                max_loss_pct=self.max_daily_loss_pct,
            ),
            PolicyRule(
                name="max_drawdown",
                domain="financial",
                description="Maximum drawdown before emergency halt",
                max_loss_pct=self.max_drawdown_pct,
            ),
        ]
