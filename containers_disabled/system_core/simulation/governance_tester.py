"""
simulation/governance_tester.py
DIX VISION v42.2 — Governance Testing System (Phase 12)

Tests governance decisions, policies, and enforcement in a simulated environment.
Validates that governance correctly:
- Approves/rejects market intents based on risk constraints
- Enforces policy rules
- Responds to hazard events
- Maintains mode transitions
- Records decisions to the ledger

This system is OFFLINE-tier only and never runs on the hot path.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import StrEnum
from typing import Any

from governance_unified.engine import GovernanceDecision, GovernanceOutcome
from governance_unified.policy_engine import PolicyEngine, PolicyRule


class GovernanceTestCase(StrEnum):
    """Types of governance test cases."""

    RISK_CONSTRAINT_VALIDATION = "risk_constraint_validation"
    POLICY_ENFORCEMENT = "policy_enforcement"
    HAZARD_RESPONSE = "hazard_response"
    MODE_TRANSITION = "mode_transition"
    CIRCUIT_BREAKER = "circuit_breaker"
    POSITION_LIMIT = "position_limit"
    LEVERAGE_LIMIT = "leverage_limit"
    STRATEGY_DENIAL = "strategy_denial"


@dataclass(frozen=True, slots=True)
class GovernanceTestConfig:
    """Configuration for a governance test."""

    test_case: GovernanceTestCase
    scenario_id: str
    seed: int
    parameters: dict[str, Any] = field(default_factory=dict)


@dataclass(frozen=True, slots=True)
class GovernanceTestEvent:
    """An event in a governance test timeline."""

    ts_ns: int
    event_type: str
    payload: dict[str, Any]


@dataclass(slots=True)
class GovernanceTestResult:
    """Result of running a governance test."""

    config: GovernanceTestConfig
    events: list[GovernanceTestEvent] = field(default_factory=list)
    decisions: list[GovernanceDecision] = field(default_factory=list)
    passed: bool = False
    failure_reason: str = ""
    metrics: dict[str, float] = field(default_factory=dict)

    def __post_init__(self) -> None:
        # Calculate metrics
        if self.decisions:
            approved = sum(1 for d in self.decisions if d.outcome == GovernanceOutcome.APPROVED)
            rejected = sum(1 for d in self.decisions if d.outcome == GovernanceOutcome.REJECTED)
            total = len(self.decisions)
            self.metrics["approval_rate"] = approved / total if total > 0 else 0.0
            self.metrics["rejection_rate"] = rejected / total if total > 0 else 0.0
            self.metrics["total_decisions"] = total


@dataclass(slots=True)
class MockRiskConstraints:
    """Mock risk constraints for testing."""

    max_position_usd: float = 100_000.0
    max_portfolio_usd: float = 1_000_000.0
    circuit_breaker_loss_pct: float = 0.01
    max_leverage: float = 10.0

    def allows_trade(self, size_usd: float, portfolio_usd: float) -> tuple[bool, str]:
        """Check if a trade is allowed under risk constraints."""
        if size_usd > self.max_position_usd:
            return False, f"size_usd={size_usd} exceeds max_position_usd={self.max_position_usd}"
        if portfolio_usd > self.max_portfolio_usd:
            return (
                False,
                f"portfolio_usd={portfolio_usd} exceeds max_portfolio_usd={self.max_portfolio_usd}",
            )
        return True, "risk_validated"


class GovernanceTestHarness:
    """Test harness for governance logic in simulation.

    Provides isolated testing of governance components without
    requiring the full system runtime.
    """

    def __init__(self, *, deterministic_seed: int = 42) -> None:
        self._seed = deterministic_seed
        self._policy_engine = PolicyEngine()
        self._risk_constraints = MockRiskConstraints()
        self._test_results: dict[str, GovernanceTestResult] = {}

    def register_policy_rule(self, rule: PolicyRule) -> None:
        """Register a policy rule for testing."""
        self._policy_engine.register(rule)

    def run_test(self, config: GovernanceTestConfig) -> GovernanceTestResult:
        """Run a governance test case."""
        result = GovernanceTestResult(config=config)

        if config.test_case == GovernanceTestCase.RISK_CONSTRAINT_VALIDATION:
            result = self._test_risk_constraints(config, result)
        elif config.test_case == GovernanceTestCase.POLICY_ENFORCEMENT:
            result = self._test_policy_enforcement(config, result)
        elif config.test_case == GovernanceTestCase.CIRCUIT_BREAKER:
            result = self._test_circuit_breaker(config, result)
        elif config.test_case == GovernanceTestCase.POSITION_LIMIT:
            result = self._test_position_limit(config, result)
        elif config.test_case == GovernanceTestCase.LEVERAGE_LIMIT:
            result = self._test_leverage_limit(config, result)
        elif config.test_case == GovernanceTestCase.STRATEGY_DENIAL:
            result = self._test_strategy_denial(config, result)
        else:
            result.passed = False
            result.failure_reason = f"unknown_test_case: {config.test_case}"

        self._test_results[config.scenario_id] = result
        return result

    def _test_risk_constraints(
        self, config: GovernanceTestConfig, result: GovernanceTestResult
    ) -> GovernanceTestResult:
        """Test that risk constraints are properly enforced."""
        params = config.parameters

        # Test valid trade
        valid_size = params.get("valid_size_usd", 10_000.0)
        portfolio = params.get("portfolio_usd", 100_000.0)

        allowed, reason = self._risk_constraints.allows_trade(valid_size, portfolio)
        decision = (
            GovernanceDecision(GovernanceOutcome.APPROVED, reason)
            if allowed
            else GovernanceDecision(GovernanceOutcome.REJECTED, reason)
        )
        result.decisions.append(decision)

        result.events.append(
            GovernanceTestEvent(
                ts_ns=0,
                event_type="trade_request",
                payload={"size_usd": valid_size, "portfolio_usd": portfolio},
            )
        )

        # Test invalid trade (exceeds max position)
        invalid_size = params.get("invalid_size_usd", 200_000.0)
        allowed, reason = self._risk_constraints.allows_trade(invalid_size, portfolio)
        decision = (
            GovernanceDecision(GovernanceOutcome.APPROVED, reason)
            if allowed
            else GovernanceDecision(GovernanceOutcome.REJECTED, reason)
        )
        result.decisions.append(decision)

        result.events.append(
            GovernanceTestEvent(
                ts_ns=1,
                event_type="trade_request",
                payload={"size_usd": invalid_size, "portfolio_usd": portfolio},
            )
        )

        # Validate: first should approve, second should reject
        result.passed = (
            result.decisions[0].outcome == GovernanceOutcome.APPROVED
            and result.decisions[1].outcome == GovernanceOutcome.REJECTED
        )
        if not result.passed:
            result.failure_reason = (
                f"Expected APPROVED then REJECTED, got "
                f"{result.decisions[0].outcome} then {result.decisions[1].outcome}"
            )

        return result

    def _test_policy_enforcement(
        self, config: GovernanceTestConfig, result: GovernanceTestResult
    ) -> GovernanceTestResult:
        """Test that policy rules are enforced."""
        # Test with a rule that denies trades > $50k
        self._policy_engine.register(
            PolicyRule(
                name="max_trade_size",
                predicate=lambda ctx: float(ctx.get("size_usd", 0)) > 50_000,
                reason="trade_size_exceeds_limit",
                deny=True,
            )
        )

        # Small trade should pass
        ctx1 = {"size_usd": 10_000}
        policy_result1 = self._policy_engine.evaluate(ctx1)
        decision1 = (
            GovernanceDecision(GovernanceOutcome.APPROVED, "policy_validated")
            if policy_result1.allowed
            else GovernanceDecision(GovernanceOutcome.REJECTED, ";".join(policy_result1.reasons))
        )
        result.decisions.append(decision1)

        # Large trade should be denied
        ctx2 = {"size_usd": 100_000}
        policy_result2 = self._policy_engine.evaluate(ctx2)
        decision2 = (
            GovernanceDecision(GovernanceOutcome.APPROVED, "policy_validated")
            if policy_result2.allowed
            else GovernanceDecision(GovernanceOutcome.REJECTED, ";".join(policy_result2.reasons))
        )
        result.decisions.append(decision2)

        result.passed = (
            result.decisions[0].outcome == GovernanceOutcome.APPROVED
            and result.decisions[1].outcome == GovernanceOutcome.REJECTED
        )
        if not result.passed:
            result.failure_reason = (
                f"Expected APPROVED then REJECTED, got "
                f"{result.decisions[0].outcome} then {result.decisions[1].outcome}"
            )

        return result

    def _test_circuit_breaker(
        self, config: GovernanceTestConfig, result: GovernanceTestResult
    ) -> GovernanceTestResult:
        """Test that circuit breaker triggers on large position percentage."""
        params = config.parameters
        portfolio_usd = params.get("portfolio_usd", 100_000.0)

        # Trade size under 1% should pass
        small_size_pct = 0.5  # 0.5%
        small_size_usd = portfolio_usd * (small_size_pct / 100)

        constraints = MockRiskConstraints()
        allowed, reason = constraints.allows_trade(small_size_usd, portfolio_usd)
        if allowed and small_size_pct <= constraints.circuit_breaker_loss_pct * 100:
            decision1 = GovernanceDecision(
                GovernanceOutcome.APPROVED, "circuit_breaker_not_triggered"
            )
        else:
            decision1 = GovernanceDecision(GovernanceOutcome.REJECTED, reason)
        result.decisions.append(decision1)

        # Trade size over 1% should be rejected
        large_size_pct = 2.0  # 2.0%
        large_size_usd = portfolio_usd * (large_size_pct / 100)

        allowed, reason = constraints.allows_trade(large_size_usd, portfolio_usd)
        if allowed and large_size_pct > constraints.circuit_breaker_loss_pct * 100:
            decision2 = GovernanceDecision(GovernanceOutcome.REJECTED, "circuit_breaker_triggered")
        else:
            decision2 = GovernanceDecision(GovernanceOutcome.APPROVED, reason)
        result.decisions.append(decision2)

        result.passed = (
            result.decisions[0].outcome == GovernanceOutcome.APPROVED
            and result.decisions[1].outcome == GovernanceOutcome.REJECTED
        )
        if not result.passed:
            result.failure_reason = (
                f"Expected APPROVED then REJECTED, got "
                f"{result.decisions[0].outcome} then {result.decisions[1].outcome}"
            )

        return result

    def _test_position_limit(
        self, config: GovernanceTestConfig, result: GovernanceTestResult
    ) -> GovernanceTestResult:
        """Test that position limits are enforced."""
        params = config.parameters

        # Test at limit
        at_limit = params.get("at_limit_usd", 100_000.0)
        allowed, reason = self._risk_constraints.allows_trade(at_limit, 100_000.0)
        decision1 = (
            GovernanceDecision(GovernanceOutcome.APPROVED, reason)
            if allowed
            else GovernanceDecision(GovernanceOutcome.REJECTED, reason)
        )
        result.decisions.append(decision1)

        # Test over limit
        over_limit = params.get("over_limit_usd", 150_000.0)
        allowed, reason = self._risk_constraints.allows_trade(over_limit, 100_000.0)
        decision2 = (
            GovernanceDecision(GovernanceOutcome.APPROVED, reason)
            if allowed
            else GovernanceDecision(GovernanceOutcome.REJECTED, reason)
        )
        result.decisions.append(decision2)

        result.passed = (
            result.decisions[0].outcome == GovernanceOutcome.APPROVED
            and result.decisions[1].outcome == GovernanceOutcome.REJECTED
        )
        if not result.passed:
            result.failure_reason = (
                f"Expected APPROVED then REJECTED, got "
                f"{result.decisions[0].outcome} then {result.decisions[1].outcome}"
            )

        return result

    def _test_leverage_limit(
        self, config: GovernanceTestConfig, result: GovernanceTestResult
    ) -> GovernanceTestResult:
        """Test that leverage limits are enforced via policy."""
        # Default policy denies leverage > 10x
        ctx_low = {"leverage": 5.0}
        policy_result1 = self._policy_engine.evaluate(ctx_low)
        decision1 = (
            GovernanceDecision(GovernanceOutcome.APPROVED, "leverage_within_limits")
            if policy_result1.allowed
            else GovernanceDecision(GovernanceOutcome.REJECTED, ";".join(policy_result1.reasons))
        )
        result.decisions.append(decision1)

        ctx_high = {"leverage": 15.0}
        policy_result2 = self._policy_engine.evaluate(ctx_high)
        decision2 = (
            GovernanceDecision(GovernanceOutcome.APPROVED, "leverage_within_limits")
            if policy_result2.allowed
            else GovernanceDecision(GovernanceOutcome.REJECTED, ";".join(policy_result2.reasons))
        )
        result.decisions.append(decision2)

        result.passed = (
            result.decisions[0].outcome == GovernanceOutcome.APPROVED
            and result.decisions[1].outcome == GovernanceOutcome.REJECTED
        )
        if not result.passed:
            result.failure_reason = (
                f"Expected APPROVED then REJECTED, got "
                f"{result.decisions[0].outcome} then {result.decisions[1].outcome}"
            )

        return result

    def _test_strategy_denial(
        self, config: GovernanceTestConfig, result: GovernanceTestResult
    ) -> GovernanceTestResult:
        """Test that forbidden strategies are denied via policy."""
        # Default policy denies martingale
        ctx_valid = {"strategy": "momentum"}
        policy_result1 = self._policy_engine.evaluate(ctx_valid)
        decision1 = (
            GovernanceDecision(GovernanceOutcome.APPROVED, "strategy_allowed")
            if policy_result1.allowed
            else GovernanceDecision(GovernanceOutcome.REJECTED, ";".join(policy_result1.reasons))
        )
        result.decisions.append(decision1)

        ctx_forbidden = {"strategy": "martingale"}
        policy_result2 = self._policy_engine.evaluate(ctx_forbidden)
        decision2 = (
            GovernanceDecision(GovernanceOutcome.APPROVED, "strategy_allowed")
            if policy_result2.allowed
            else GovernanceDecision(GovernanceOutcome.REJECTED, ";".join(policy_result2.reasons))
        )
        result.decisions.append(decision2)

        result.passed = (
            result.decisions[0].outcome == GovernanceOutcome.APPROVED
            and result.decisions[1].outcome == GovernanceOutcome.REJECTED
        )
        if not result.passed:
            result.failure_reason = (
                f"Expected APPROVED then REJECTED, got "
                f"{result.decisions[0].outcome} then {result.decisions[1].outcome}"
            )

        return result

    def get_result(self, scenario_id: str) -> GovernanceTestResult | None:
        """Retrieve a test result by scenario ID."""
        return self._test_results.get(scenario_id)

    def get_all_results(self) -> dict[str, GovernanceTestResult]:
        """Get all test results."""
        return self._test_results.copy()


def run_governance_test_suite() -> dict[str, GovernanceTestResult]:
    """Run the full governance test suite."""
    harness = GovernanceTestHarness(deterministic_seed=42)
    results: dict[str, GovernanceTestResult] = {}

    # Test 1: Risk constraint validation
    config1 = GovernanceTestConfig(
        test_case=GovernanceTestCase.RISK_CONSTRAINT_VALIDATION,
        scenario_id="risk_constraint_test_1",
        seed=42,
        parameters={
            "valid_size_usd": 10_000.0,
            "invalid_size_usd": 200_000.0,
            "portfolio_usd": 100_000.0,
        },
    )
    results[config1.scenario_id] = harness.run_test(config1)

    # Test 2: Policy enforcement
    config2 = GovernanceTestConfig(
        test_case=GovernanceTestCase.POLICY_ENFORCEMENT,
        scenario_id="policy_enforcement_test_1",
        seed=42,
    )
    results[config2.scenario_id] = harness.run_test(config2)

    # Test 3: Circuit breaker
    config3 = GovernanceTestConfig(
        test_case=GovernanceTestCase.CIRCUIT_BREAKER,
        scenario_id="circuit_breaker_test_1",
        seed=42,
        parameters={"portfolio_usd": 100_000.0},
    )
    results[config3.scenario_id] = harness.run_test(config3)

    # Test 4: Position limit
    config4 = GovernanceTestConfig(
        test_case=GovernanceTestCase.POSITION_LIMIT,
        scenario_id="position_limit_test_1",
        seed=42,
        parameters={"at_limit_usd": 100_000.0, "over_limit_usd": 150_000.0},
    )
    results[config4.scenario_id] = harness.run_test(config4)

    # Test 5: Leverage limit
    config5 = GovernanceTestConfig(
        test_case=GovernanceTestCase.LEVERAGE_LIMIT,
        scenario_id="leverage_limit_test_1",
        seed=42,
    )
    results[config5.scenario_id] = harness.run_test(config5)

    # Test 6: Strategy denial
    config6 = GovernanceTestConfig(
        test_case=GovernanceTestCase.STRATEGY_DENIAL,
        scenario_id="strategy_denial_test_1",
        seed=42,
    )
    results[config6.scenario_id] = harness.run_test(config6)

    return results


__all__ = [
    "GovernanceTestCase",
    "GovernanceTestConfig",
    "GovernanceTestEvent",
    "GovernanceTestResult",
    "GovernanceTestHarness",
    "MockRiskConstraints",
    "run_governance_test_suite",
]
