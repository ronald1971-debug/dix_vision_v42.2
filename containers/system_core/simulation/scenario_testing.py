"""Scenario Testing – tests system behavior under defined conditions.

Covers:
  - Governance testing (policy enforcement under stress)
  - Evolution sandbox (safe environment for proposals)
  - Learning validation (verifying feedback loops)
"""

from __future__ import annotations

import time
import uuid
from dataclasses import dataclass, field
from enum import Enum, auto
from typing import Any


class ScenarioType(Enum):
    MARKET_CRASH = auto()
    VOLATILITY_SPIKE = auto()
    FEED_OUTAGE = auto()
    GOVERNANCE_STRESS = auto()
    EVOLUTION_SANDBOX = auto()
    LEARNING_VALIDATION = auto()
    LATENCY_SPIKE = auto()


class ScenarioResult(Enum):
    PASSED = auto()
    FAILED = auto()
    PARTIAL = auto()
    SKIPPED = auto()


@dataclass
class Scenario:
    scenario_id: str = field(default_factory=lambda: uuid.uuid4().hex[:12])
    name: str = ""
    scenario_type: ScenarioType = ScenarioType.MARKET_CRASH
    description: str = ""
    parameters: dict[str, Any] = field(default_factory=dict)
    expected_behavior: str = ""
    result: ScenarioResult = ScenarioResult.SKIPPED
    actual_behavior: str = ""
    duration_seconds: float = 0.0
    timestamp: float = field(default_factory=time.time)


class ScenarioRunner:
    """Runs predefined scenarios against the system."""

    def __init__(self) -> None:
        self._scenarios: list[Scenario] = []
        self._results: list[Scenario] = []

    def add_scenario(self, scenario: Scenario) -> None:
        self._scenarios.append(scenario)

    def create_scenario(
        self,
        name: str,
        scenario_type: ScenarioType,
        description: str = "",
        parameters: dict[str, Any] | None = None,
        expected_behavior: str = "",
    ) -> Scenario:
        scenario = Scenario(
            name=name,
            scenario_type=scenario_type,
            description=description,
            parameters=parameters or {},
            expected_behavior=expected_behavior,
        )
        self._scenarios.append(scenario)
        return scenario

    def run_scenario(self, scenario: Scenario, system_callback: Any = None) -> Scenario:
        start = time.time()

        if system_callback:
            try:
                actual = system_callback(scenario.parameters)
                scenario.actual_behavior = str(actual)
                scenario.result = ScenarioResult.PASSED
            except Exception as e:
                scenario.actual_behavior = f"Error: {e}"
                scenario.result = ScenarioResult.FAILED
        else:
            scenario.result = ScenarioResult.SKIPPED
            scenario.actual_behavior = "No callback provided"

        scenario.duration_seconds = time.time() - start
        self._results.append(scenario)
        return scenario

    def run_all(self, system_callback: Any = None) -> list[Scenario]:
        results: list[Scenario] = []
        for scenario in self._scenarios:
            result = self.run_scenario(scenario, system_callback)
            results.append(result)
        return results

    def get_results(self) -> list[Scenario]:
        return list(self._results)

    def get_pass_rate(self) -> float:
        if not self._results:
            return 0.0
        passed = sum(1 for r in self._results if r.result == ScenarioResult.PASSED)
        return passed / len(self._results)

    @property
    def scenario_count(self) -> int:
        return len(self._scenarios)

    def build_default_scenarios(self) -> list[Scenario]:
        defaults = [
            self.create_scenario(
                name="Market Crash Response",
                scenario_type=ScenarioType.MARKET_CRASH,
                description="Simulate a 10% market drop in 5 minutes",
                parameters={"drop_pct": 10, "duration_minutes": 5},
                expected_behavior="Kill switch activates, positions closed",
            ),
            self.create_scenario(
                name="Feed Outage Handling",
                scenario_type=ScenarioType.FEED_OUTAGE,
                description="Simulate complete market data feed loss",
                parameters={"duration_seconds": 60},
                expected_behavior="Hazard detected, trading paused",
            ),
            self.create_scenario(
                name="Governance Under Stress",
                scenario_type=ScenarioType.GOVERNANCE_STRESS,
                description="Flood governance with 1000 rapid intents",
                parameters={"intent_count": 1000, "interval_ms": 10},
                expected_behavior="All intents evaluated, no policy bypass",
            ),
        ]
        return defaults
