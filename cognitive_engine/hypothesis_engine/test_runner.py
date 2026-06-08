"""Test Runner - executes hypothesis tests."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from cognitive_engine.hypothesis_engine.hypothesis import Hypothesis, HypothesisResult


@dataclass
class TestResult:
    """Result from a single test."""

    test_name: str
    passed: bool
    p_value: float = 0.0
    effect_size: float = 0.0
    notes: str = ""


class TestRunner:
    """Runs tests against hypotheses.

    Executes statistical tests, backtests, or simulations to validate
    or invalidate hypotheses.
    """

    def __init__(self) -> None:
        self._test_history: list[TestResult] = []

    def run_statistical_test(
        self,
        hypothesis: Hypothesis,
        data: dict[str, Any],
        test_type: str = "t_test",
    ) -> TestResult:
        """Run a statistical test against hypothesis."""
        # Simplified implementation - real version would use scipy/stats
        passed = data.get("effect", 0) > 0.05
        p_value = data.get("p_value", 0.05)

        result = TestResult(
            test_name=f"{test_type}_{hypothesis.hypothesis_id[:8]}",
            passed=passed,
            p_value=p_value,
            effect_size=data.get("effect", 0),
            notes=f"Statistical test for: {hypothesis.statement[:50]}",
        )
        self._test_history.append(result)
        return result

    def run_backtest(
        self,
        hypothesis: Hypothesis,
        strategy_id: str,
        historical_data: list[dict[str, Any]],
    ) -> TestResult:
        """Run a backtest to validate hypothesis."""
        # Simplified - real implementation would run actual backtest
        passed = len(historical_data) > 10
        effect = sum(d.get("return", 0) for d in historical_data) / len(historical_data)

        result = TestResult(
            test_name=f"backtest_{strategy_id}",
            passed=passed and effect > 0,
            p_value=0.05,
            effect_size=effect,
            notes=f"Backtest validation for: {hypothesis.statement[:50]}",
        )
        self._test_history.append(result)
        return result

    def run(self, hypothesis: Hypothesis, test_config: dict[str, Any]) -> HypothesisResult:
        """Run appropriate tests and return hypothesis result."""
        test_type = test_config.get("test_type", "statistical")
        data = test_config.get("data", {})

        if test_type == "backtest":
            test = self.run_backtest(hypothesis, test_config.get("strategy_id", ""), list(data.values()))
        else:
            test = self.run_statistical_test(hypothesis, data, test_type)

        validated = test.passed and test.p_value < 0.05

        return HypothesisResult(
            hypothesis_id=hypothesis.hypothesis_id,
            validated=validated,
            confidence=test.effect_size,
            evidence_gathered=(test.notes,),
            insights=(f"Test: {test.test_name}, Passed: {validated}",),
        )

    def get_history(self, limit: int = 100) -> list[TestResult]:
        """Get test history."""
        return self._test_history[-limit:]

    def test_summary(self) -> dict[str, int]:
        """Get summary of test results."""
        passed = sum(1 for t in self._test_history if t.passed)
        total = len(self._test_history)
        return {"passed": passed, "failed": total - passed, "total": total}