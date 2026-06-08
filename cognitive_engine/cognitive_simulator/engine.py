"""Cognitive Simulator Engine - runs scenario reasoning."""

from __future__ import annotations

from typing import Any

from cognitive_engine.cognitive_simulator.result import RiskLevel, SimulationResult
from cognitive_engine.cognitive_simulator.scenario import Scenario, ScenarioType


class CognitiveSimulator:
    """Runs 'what happens if' reasoning for INDIRA.

    Different from backtesting - this is forward-looking scenario reasoning.
    """

    def __init__(self) -> None:
        self._results: list[SimulationResult] = []

    def simulate(self, scenario: Scenario, knowledge: dict[str, Any] | None = None) -> SimulationResult:
        """Run simulation against a scenario."""
        risk_level = self._assess_risk(scenario)
        pnl_impact = self._estimate_pnl_impact(scenario, knowledge)
        recommendations = self._generate_recommendations(scenario, risk_level)

        result = SimulationResult(
            scenario_id=scenario.scenario_id,
            risk_level=risk_level,
            estimated_pnl_impact=pnl_impact,
            strategy_exposure=self._get_strategy_exposure(knowledge),
            recommendations=recommendations,
            confidence=self._calculate_confidence(scenario, knowledge),
        )
        self._results.append(result)
        return result

    def _assess_risk(self, scenario: Scenario) -> RiskLevel:
        """Assess risk level from scenario."""
        max_impact = max(scenario.impact_factors.values()) if scenario.impact_factors else 0.0

        if max_impact > 0.5:
            return RiskLevel.EXTREME
        if max_impact > 0.3:
            return RiskLevel.HIGH
        if max_impact > 0.1:
            return RiskLevel.MEDIUM
        return RiskLevel.LOW

    def _estimate_pnl_impact(self, scenario: Scenario, knowledge: dict[str, Any] | None) -> float:
        """Estimate PnL impact from scenario."""
        # Simplified - real implementation would use risk models
        base_impact = sum(
            abs(v) * 0.1 for v in scenario.impact_factors.values()
        )

        if knowledge:
            hedges = knowledge.get("hedges", {})
            hedge_impact = sum(hedges.values()) * 0.05
            return base_impact - hedge_impact

        return base_impact

    def _generate_recommendations(self, scenario: Scenario, risk_level: RiskLevel) -> tuple[str, ...]:
        """Generate recommendations based on scenario and risk."""
        recs = []

        if risk_level in (RiskLevel.HIGH, RiskLevel.EXTREME):
            recs.append("Consider reducing exposure")
            recs.append("Activate circuit breakers")

        if scenario.scenario_type == ScenarioType.LIQUIDITY_COLLAPSE:
            recs.append("Shift to limit orders")
            recs.append("Reduce position sizes")

        if scenario.scenario_type == ScenarioType.VOLATILITY_EXPLOSION:
            recs.append("Activate volatility hedges")
            recs.append("Widen stop losses")

        return tuple(recs) if recs else ("Monitor situation",)

    def _get_strategy_exposure(self, knowledge: dict[str, Any] | None) -> dict[str, float]:
        """Get strategy exposure from knowledge."""
        if knowledge:
            return knowledge.get("strategy_exposure", {})
        return {}

    def _calculate_confidence(self, scenario: Scenario, knowledge: dict[str, Any] | None) -> float:
        """Calculate confidence in simulation result."""
        # Base confidence on scenario completeness
        factor_count = len(scenario.impact_factors)
        asset_count = len(scenario.affected_assets)

        base_conf = min(1.0, factor_count * 0.2 + asset_count * 0.1)
        return max(0.3, base_conf)

    def run_fed_surprise(self, assets: tuple[str, ...] = ("SPY", "BTC", "ETH")) -> SimulationResult:
        """Run Fed surprise simulation."""
        scenario = Scenario(
            scenario_type=ScenarioType.FED_SURPRISE,
            description="Unexpected Fed policy change",
            affected_assets=assets,
        ).with_impact("equity_beta", 0.4).with_impact("bond_duration", 0.6)

        return self.simulate(scenario)

    def run_exchange_failure(self, exchange: str, assets: tuple[str, ...]) -> SimulationResult:
        """Run exchange failure simulation."""
        scenario = Scenario(
            scenario_type=ScenarioType.EXCHANGE_FAILURE,
            description=f"{exchange} exchange outage",
            affected_assets=assets,
        ).with_impact("correlation_spike", 0.8).with_impact("volume_drop", 0.9)

        return self.simulate(scenario)

    def run_liquidity_collapse(self, assets: tuple[str, ...] = ("BTC", "ETH")) -> SimulationResult:
        """Run liquidity collapse simulation."""
        scenario = Scenario(
            scenario_type=ScenarioType.LIQUIDITY_COLLAPSE,
            description="Market liquidity dries up",
            affected_assets=assets,
        ).with_impact("spread_widening", 0.7).with_impact("depth_depletion", 0.85)

        return self.simulate(scenario)

    def run_volatility_explosion(self, assets: tuple[str, ...] = ("ALL",)) -> SimulationResult:
        """Run volatility explosion simulation."""
        scenario = Scenario(
            scenario_type=ScenarioType.VOLATILITY_EXPLOSION,
            description="Volatility spikes across markets",
            affected_assets=assets,
        ).with_impact("volatility_mult", 3.0).with_impact("correlation_climb", 0.9)

        return self.simulate(scenario)

    def get_results(self, limit: int = 100) -> list[SimulationResult]:
        """Get simulation results."""
        return self._results[-limit:]

    def get_high_risk_results(self) -> list[SimulationResult]:
        """Get results with high risk levels."""
        return [
            r for r in self._results
            if r.risk_level in (RiskLevel.HIGH, RiskLevel.EXTREME)
        ]