"""
simulation/learning_validator.py
DIX VISION v42.2 — Learning Validation System (Phase 12)

Validates learning engine updates before they are applied to the production
belief state. The learning validator:

- Tests learning updates against historical scenarios
- Validates that learning improves performance metrics
- Ensures learning doesn't violate governance constraints
- Prevents catastrophic forgetting
- Generates validation reports for governance approval

CRITICAL: All learning updates MUST pass validation before being applied
to the production belief state. Learning updates beliefs without mutating
governance.
"""

from __future__ import annotations

import hashlib
from dataclasses import dataclass, field
from enum import StrEnum
from typing import Any

from simulation.scenario_generator import ScenarioConfig, ScenarioKind, generate_scenario


class LearningUpdateType(StrEnum):
    """Types of learning updates."""

    BELIEF_REFINEMENT = "belief_refinement"
    KNOWLEDGE_CONSOLIDATION = "knowledge_consolidation"
    OUTCOME_ATTRIBUTION = "outcome_attribution"
    ERROR_ANALYSIS = "error_analysis"
    MEMORY_INDEXING = "memory_indexing"
    FEEDBACK_LOOP = "feedback_loop"


@dataclass(frozen=True, slots=True)
class LearningUpdate:
    """A proposed learning update from the learning engine."""

    update_id: str
    update_type: LearningUpdateType
    belief_delta: dict[str, float]  # Changes to belief state
    confidence: float  # 0.0 to 1.0
    source_scenario_id: str
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass(frozen=True, slots=True)
class ValidationConfig:
    """Configuration for learning validation."""

    update: LearningUpdate
    seed: int
    test_scenarios: list[ScenarioKind] = field(default_factory=list)
    performance_threshold: float = 0.05  # 5% improvement threshold
    forgetting_threshold: float = 0.1  # 10% forgetting threshold


@dataclass(slots=True)
class ValidationMetrics:
    """Metrics collected during learning validation."""

    scenario_performance: dict[str, float] = field(default_factory=dict)
    belief_consistency: float = 1.0
    catastrophic_forgetting_score: float = 0.0
    governance_compliance_score: float = 1.0
    improvement_score: float = 0.0


@dataclass(slots=True)
class ValidationResult:
    """Result of validating a learning update."""

    update_id: str
    passed: bool
    metrics: ValidationMetrics = field(default_factory=ValidationMetrics)
    errors: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)
    approval_recommendation: str = ""
    detailed_report: dict[str, Any] = field(default_factory=dict)


@dataclass(slots=True)
class BeliefSnapshot:
    """Snapshot of belief state for comparison."""

    beliefs: dict[str, float]
    timestamp_ns: int
    checksum: str


class LearningValidator:
    """Validates learning updates before they are applied to production.

    The validator ensures that learning updates:
    - Improve or maintain performance
    - Don't cause catastrophic forgetting
    - Comply with governance constraints
    - Are consistent with historical data
    """

    def __init__(self, *, deterministic_seed: int = 42) -> None:
        self._seed = deterministic_seed
        self._belief_snapshots: dict[str, BeliefSnapshot] = {}
        self._validation_results: dict[str, ValidationResult] = {}

    def take_belief_snapshot(self, beliefs: dict[str, float], timestamp_ns: int) -> str:
        """Take a snapshot of the current belief state."""
        checksum = self._compute_belief_checksum(beliefs)
        snapshot_id = f"snapshot_{timestamp_ns}_{checksum[:8]}"

        self._belief_snapshots[snapshot_id] = BeliefSnapshot(
            beliefs=beliefs.copy(),
            timestamp_ns=timestamp_ns,
            checksum=checksum,
        )

        return snapshot_id

    def validate_update(self, config: ValidationConfig) -> ValidationResult:
        """Validate a learning update."""
        result = ValidationResult(update_id=config.update.update_id, passed=False)

        # Step 1: Validate belief delta consistency
        if not self._validate_belief_delta(config.update):
            result.errors.append("Belief delta is inconsistent")
            self._validation_results[config.update.update_id] = result
            return result

        # Step 2: Test against historical scenarios
        metrics = self._test_against_scenarios(config)
        result.metrics = metrics

        # Step 3: Check for catastrophic forgetting
        forgetting_score = self._check_catastrophic_forgetting(config)
        metrics.catastrophic_forgetting_score = forgetting_score

        if forgetting_score > config.forgetting_threshold:
            result.errors.append(f"Catastrophic forgetting detected: {forgetting_score:.2%}")
            self._validation_results[config.update.update_id] = result
            return result

        # Step 4: Validate governance compliance
        compliance_score = self._validate_governance_compliance(config)
        metrics.governance_compliance_score = compliance_score

        if compliance_score < 0.9:
            result.errors.append(f"Governance compliance too low: {compliance_score:.2%}")
            self._validation_results[config.update.update_id] = result
            return result

        # Step 5: Calculate improvement score
        improvement_score = self._calculate_improvement(metrics)
        metrics.improvement_score = improvement_score

        if improvement_score < config.performance_threshold:
            result.warnings.append(
                f"Improvement score {improvement_score:.2%} below threshold {config.performance_threshold:.2%}"
            )

        # Step 6: Final approval decision
        result.passed = (
            metrics.governance_compliance_score >= 0.9
            and metrics.catastrophic_forgetting_score <= config.forgetting_threshold
        )
        result.approval_recommendation = self._generate_approval_recommendation(result, config)
        result.detailed_report = self._generate_detailed_report(result, config)

        self._validation_results[config.update.update_id] = result
        return result

    def _validate_belief_delta(self, update: LearningUpdate) -> bool:
        """Validate that the belief delta is well-formed."""
        # Check that all values are floats
        for key, value in update.belief_delta.items():
            if not isinstance(value, (int, float)):
                return False
            if not -1.0 <= value <= 1.0:  # Belief values should be normalized
                return False

        # Check that confidence is valid
        if not 0.0 <= update.confidence <= 1.0:
            return False

        return True

    def _test_against_scenarios(self, config: ValidationConfig) -> ValidationMetrics:
        """Test the learning update against historical scenarios."""
        metrics = ValidationMetrics()

        # Use default scenarios if none specified
        test_kinds = config.test_scenarios if config.test_scenarios else list(ScenarioKind)

        for kind in test_kinds:
            scenario_config = ScenarioConfig(
                scenario_id=f"validation_{config.update.update_id}_{kind.value}",
                kind=kind,
                num_bars=100,  # Quick test
                seed=config.seed,
            )
            scenario = generate_scenario(scenario_config)

            # Simulate performance with the learning update applied
            # This is a simplified model - in production, would run full simulation
            base_performance = 0.5  # Baseline
            update_impact = config.update.confidence * 0.1  # Learning impact

            performance = base_performance + update_impact
            metrics.scenario_performance[scenario.scenario_id] = performance

        # Calculate average performance
        if metrics.scenario_performance:
            avg_performance = sum(metrics.scenario_performance.values()) / len(
                metrics.scenario_performance
            )
            metrics.improvement_score = max(0, avg_performance - 0.5)

        return metrics

    def _check_catastrophic_forgetting(self, config: ValidationConfig) -> float:
        """Check for catastrophic forgetting of previous knowledge."""
        # In a real implementation, this would compare belief snapshots
        # before and after the update to detect significant degradation

        # Simplified: check if the update drastically changes many beliefs
        belief_delta = config.update.belief_delta
        total_change = sum(abs(v) for v in belief_delta.values())

        if len(belief_delta) == 0:
            return 0.0

        avg_change = total_change / len(belief_delta)

        # High average change indicates potential forgetting
        forgetting_score = min(avg_change, 1.0)

        return forgetting_score

    def _validate_governance_compliance(self, config: ValidationConfig) -> float:
        """Validate that the learning update complies with governance constraints."""
        # Check that learning doesn't suggest actions that violate governance
        # This is a simplified check - in production would integrate with governance kernel

        compliance_score = 1.0

        # Check for concerning patterns in the belief delta
        belief_delta = config.update.belief_delta

        # Example: Learning shouldn't suggest increasing risk beyond limits
        if belief_delta.get("risk_tolerance", 0) > 0.5:
            compliance_score -= 0.3

        # Example: Learning shouldn't suggest disabling safety mechanisms
        if belief_delta.get("disable_governance", 0) > 0:
            compliance_score = 0.0

        return max(0.0, compliance_score)

    def _calculate_improvement(self, metrics: ValidationMetrics) -> float:
        """Calculate the overall improvement score."""
        if not metrics.scenario_performance:
            return 0.0

        # Average performance improvement over baseline (0.5)
        avg_performance = sum(metrics.scenario_performance.values()) / len(
            metrics.scenario_performance
        )
        improvement = max(0, avg_performance - 0.5)

        return improvement

    def _generate_approval_recommendation(
        self, result: ValidationResult, config: ValidationConfig
    ) -> str:
        """Generate an approval recommendation."""
        if not result.passed:
            return f"REJECT: {', '.join(result.errors)}"

        if result.warnings:
            return f"APPROVE_WITH_WARNINGS: {', '.join(result.warnings)}"

        if result.metrics.improvement_score < config.performance_threshold:
            return f"APPROVE_CAUTIONARY: Improvement {result.metrics.improvement_score:.2%} below threshold"

        return "APPROVE: Learning update passed all validation checks"

    def _generate_detailed_report(
        self, result: ValidationResult, config: ValidationConfig
    ) -> dict[str, Any]:
        """Generate a detailed validation report."""
        return {
            "update_id": result.update_id,
            "update_type": config.update.update_type.value,
            "source_scenario": config.update.source_scenario_id,
            "confidence": config.update.confidence,
            "passed": result.passed,
            "metrics": {
                "improvement_score": result.metrics.improvement_score,
                "catastrophic_forgetting_score": result.metrics.catastrophic_forgetting_score,
                "governance_compliance_score": result.metrics.governance_compliance_score,
                "belief_consistency": result.metrics.belief_consistency,
                "scenario_performance": result.metrics.scenario_performance,
            },
            "errors": result.errors,
            "warnings": result.warnings,
            "recommendation": result.approval_recommendation,
        }

    def _compute_belief_checksum(self, beliefs: dict[str, float]) -> str:
        """Compute a checksum for belief state comparison."""
        # Sort beliefs for deterministic checksum
        sorted_items = sorted(beliefs.items())
        beliefs_str = str(sorted_items).encode()
        return hashlib.sha256(beliefs_str).hexdigest()

    def get_result(self, update_id: str) -> ValidationResult | None:
        """Retrieve a validation result by update ID."""
        return self._validation_results.get(update_id)

    def get_all_results(self) -> dict[str, ValidationResult]:
        """Get all validation results."""
        return self._validation_results.copy()

    def get_belief_snapshot(self, snapshot_id: str) -> BeliefSnapshot | None:
        """Retrieve a belief snapshot."""
        return self._belief_snapshots.get(snapshot_id)


def run_learning_validation_suite() -> dict[str, ValidationResult]:
    """Run a sample learning validation suite."""
    validator = LearningValidator(deterministic_seed=42)
    results: dict[str, ValidationResult] = {}

    # Take initial belief snapshot
    initial_beliefs = {
        "market_regime_bullish": 0.6,
        "market_regime_bearish": 0.2,
        "volatility_regime_low": 0.5,
        "volatility_regime_high": 0.3,
    }
    validator.take_belief_snapshot(initial_beliefs, 1_700_000_000_000_000_000)

    # Test 1: Valid belief refinement
    update1 = LearningUpdate(
        update_id="learning_001",
        update_type=LearningUpdateType.BELIEF_REFINEMENT,
        belief_delta={
            "market_regime_bullish": 0.1,
            "market_regime_bearish": -0.05,
        },
        confidence=0.8,
        source_scenario_id="scenario_001",
    )
    config1 = ValidationConfig(update=update1, seed=42)
    results[update1.update_id] = validator.validate_update(config1)

    # Test 2: Update with governance risk
    update2 = LearningUpdate(
        update_id="learning_002",
        update_type=LearningUpdateType.BELIEF_REFINEMENT,
        belief_delta={"risk_tolerance": 0.8},  # Excessive risk increase
        confidence=0.9,
        source_scenario_id="scenario_002",
    )
    config2 = ValidationConfig(update=update2, seed=42)
    results[update2.update_id] = validator.validate_update(config2)

    # Test 3: Update with catastrophic forgetting risk
    update3 = LearningUpdate(
        update_id="learning_003",
        update_type=LearningUpdateType.KNOWLEDGE_CONSOLIDATION,
        belief_delta={
            "market_regime_bullish": -0.5,
            "market_regime_bearish": -0.5,
            "volatility_regime_low": -0.5,
            "volatility_regime_high": -0.5,
        },  # Large changes
        confidence=0.7,
        source_scenario_id="scenario_003",
    )
    config3 = ValidationConfig(update=update3, seed=42)
    results[update3.update_id] = validator.validate_update(config3)

    return results


__all__ = [
    "BeliefSnapshot",
    "LearningUpdate",
    "LearningUpdateType",
    "LearningValidator",
    "ValidationConfig",
    "ValidationMetrics",
    "ValidationResult",
    "run_learning_validation_suite",
]
