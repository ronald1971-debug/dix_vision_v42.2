"""Unified Governance Graph – Phase 9 consolidation.

Merges cognitive_governance, financial_governance, operator_governance,
system_governance into a single authority graph while retaining
domain-specific policies.

One authority graph. No duplicate kernels.
"""

from __future__ import annotations

from dataclasses import dataclass, field

from governance_unified.domains.cognitive import CognitiveGovernancePolicy
from governance_unified.domains.financial import FinancialGovernancePolicy
from governance_unified.domains.operator import OperatorGovernancePolicy
from governance_unified.domains.system import SystemGovernancePolicy
from governance_unified.mcos_kernel import GovernanceKernel, PolicyRule


@dataclass
class UnifiedGovernanceConfig:
    """Consolidated configuration for all governance domains."""
    cognitive: CognitiveGovernancePolicy = field(default_factory=CognitiveGovernancePolicy)
    financial: FinancialGovernancePolicy = field(default_factory=FinancialGovernancePolicy)
    operator: OperatorGovernancePolicy = field(default_factory=OperatorGovernancePolicy)
    system: SystemGovernancePolicy = field(default_factory=SystemGovernancePolicy)


class UnifiedGovernanceGraph:
    """Single authority that merges all domain governance.

    Retains domain-specific policies but routes through a single
    GovernanceKernel. No duplicate policy engines.
    """

    def __init__(self, config: UnifiedGovernanceConfig | None = None) -> None:
        self._config = config or UnifiedGovernanceConfig()
        self._kernel = GovernanceKernel()
        self._domain_rules: dict[str, list[PolicyRule]] = {}
        self._initialize_domains()

    @property
    def kernel(self) -> GovernanceKernel:
        return self._kernel

    def _initialize_domains(self) -> None:
        for domain_name, policy in [
            ("cognitive", self._config.cognitive),
            ("financial", self._config.financial),
            ("operator", self._config.operator),
            ("system", self._config.system),
        ]:
            rules = policy.to_rules()
            self._domain_rules[domain_name] = rules
            for rule in rules:
                self._kernel.register_policy(rule)

    def get_domain_rules(self, domain: str) -> list[PolicyRule]:
        return self._domain_rules.get(domain, [])

    def get_all_domains(self) -> list[str]:
        return list(self._domain_rules.keys())

    def get_total_rule_count(self) -> int:
        return sum(len(rules) for rules in self._domain_rules.values())

    def update_domain(self, domain: str, rules: list[PolicyRule]) -> None:
        for old_rule in self._domain_rules.get(domain, []):
            self._kernel.remove_policy(old_rule.rule_id)
        self._domain_rules[domain] = rules
        for rule in rules:
            self._kernel.register_policy(rule)
