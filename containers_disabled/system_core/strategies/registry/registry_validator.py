"""
DIXVISION INDIRA Strategy Registry Validator
Validates strategy registry entries and ensures INDIRA integration compatibility
"""

import logging
from dataclasses import dataclass
from typing import Any, Dict, List

import yaml

logger = logging.getLogger(__name__)


@dataclass
class ValidationResult:
    """Result of strategy registry validation"""

    is_valid: bool
    strategy_id: str
    errors: List[str]
    warnings: List[str]
    validation_timestamp: str


class StrategyRegistryValidator:
    """Validator for strategy registry entries"""

    def __init__(self, registry_path: str):
        self.registry_path = registry_path
        self.indira_cognitive_systems = [
            "artificial_consciousness",
            "causal_reasoning",
            "theory_of_mind",
            "explainable_ai",
            "temporal_reasoning",
            "transfer_learning",
            "self_improving_architecture",
            "meta_learning",
            "continual_learning",
            "world_model_simulation",
            "multi_agent_collaboration",
            "game_theoretic_reasoning",
            "analogical_reasoning",
            "intentional_stance",
            "abductive_reasoning",
            "neuromorphic_computing",
            "quantum_algorithms",
            "advanced_attention",
        ]

        logger.info("StrategyRegistryValidator initialized")

    def load_registry(self) -> Dict[str, Any]:
        """Load strategy registry YAML"""
        try:
            with open(self.registry_path, "r") as f:
                registry = yaml.safe_load(f)
            return registry
        except Exception as e:
            logger.error(f"Failed to load registry: {e}")
            raise

    def validate_registry(self) -> List[ValidationResult]:
        """Validate entire strategy registry"""
        registry = self.load_registry()
        results = []

        # Validate individual strategies
        if "strategies" in registry:
            for strategy_id, strategy_data in registry["strategies"].items():
                result = self.validate_strategy(strategy_id, strategy_data)
                results.append(result)

        # Validate ensemble strategies
        if "ensemble_strategies" in registry:
            for ensemble_id, ensemble_data in registry["ensemble_strategies"].items():
                result = self.validate_ensemble(ensemble_id, ensemble_data, registry)
                results.append(result)

        return results

    def validate_strategy(
        self, strategy_id: str, strategy_data: Dict[str, Any]
    ) -> ValidationResult:
        """Validate individual strategy entry"""
        errors = []
        warnings = []

        # Required fields
        required_fields = [
            "id",
            "name",
            "category",
            "base_trader",
            "philosophy",
            "timeframe",
            "risk",
            "execution",
            "regime_bias",
        ]

        for field in required_fields:
            if field not in strategy_data:
                errors.append(f"Missing required field: {field}")

        # Validate INDIRA cognitive systems
        if "cognitive_systems_required" in strategy_data:
            invalid_systems = []
            for system in strategy_data["cognitive_systems_required"]:
                if system not in self.indira_cognitive_systems:
                    invalid_systems.append(system)

            if invalid_systems:
                errors.append(f"Invalid cognitive systems: {invalid_systems}")

        # Validate performance metrics
        if "historical_performance" in strategy_data:
            performance = strategy_data["historical_performance"]
            for metric in ["win_rate", "sharpe_ratio", "max_drawdown"]:
                if metric in performance:
                    if not isinstance(performance[metric], (int, float)):
                        # Allow string values like "variable"
                        if isinstance(performance[metric], str):
                            continue
                        errors.append(f"Invalid {metric} type: must be numeric")
                    elif metric == "win_rate" and isinstance(performance[metric], (int, float)):
                        if not 0 <= performance[metric] <= 1:
                            warnings.append(f"{metric} should be between 0 and 1")

        # Check for AI enhancement readiness
        if strategy_data.get("ai_enhancement_ready") and not strategy_data.get(
            "learning_capability"
        ):
            warnings.append("AI enhancement ready but learning capability not enabled")

        return ValidationResult(
            is_valid=len(errors) == 0,
            strategy_id=strategy_id,
            errors=errors,
            warnings=warnings,
            validation_timestamp="2026-06-21",
        )

    def validate_ensemble(
        self, ensemble_id: str, ensemble_data: Dict[str, Any], registry: Dict[str, Any]
    ) -> ValidationResult:
        """Validate ensemble strategy entry"""
        errors = []
        warnings = []

        # Required fields
        required_fields = ["id", "name", "components", "composition_logic"]
        for field in required_fields:
            if field not in ensemble_data:
                errors.append(f"Missing required field: {field}")

        # Validate component strategies exist
        if "components" in ensemble_data:
            available_strategies = registry.get("strategies", {}).keys()
            for component in ensemble_data["components"]:
                if isinstance(component, dict):
                    strategy_name = component.get("strategy")
                    if strategy_name and strategy_name not in available_strategies:
                        errors.append(f"Component strategy not found: {strategy_name}")

        # Validate weight distribution
        if "components" in ensemble_data:
            weights = [
                comp.get("weight", 0)
                for comp in ensemble_data["components"]
                if isinstance(comp, dict)
            ]
            if abs(sum(weights) - 1.0) > 0.01:
                warnings.append(f"Component weights do not sum to 1.0: {sum(weights)}")

        return ValidationResult(
            is_valid=len(errors) == 0,
            strategy_id=ensemble_id,
            errors=errors,
            warnings=warnings,
            validation_timestamp="2026-06-21",
        )

    def validate_indira_integration(self) -> ValidationResult:
        """Validate INDIRA integration configuration"""
        registry = self.load_registry()
        errors = []
        warnings = []

        if "indira_integration" not in registry:
            errors.append("Missing INDIRA integration configuration")
            return ValidationResult(False, "INDIRA_INTEGRATION", errors, warnings, "2026-06-21")

        integration = registry["indira_integration"]

        # Validate cognitive system mapping
        if "cognitive_system_mapping" in integration:
            invalid_mappings = []
            for system, strategies in integration["cognitive_system_mapping"].items():
                if system not in self.indira_cognitive_systems:
                    invalid_mappings.append(system)

            if invalid_mappings:
                errors.append(f"Invalid cognitive systems in mapping: {invalid_mappings}")

        return ValidationResult(
            is_valid=len(errors) == 0,
            strategy_id="INDIRA_INTEGRATION",
            errors=errors,
            warnings=warnings,
            validation_timestamp="2026-06-21",
        )

    def generate_validation_report(self) -> str:
        """Generate comprehensive validation report"""
        results = self.validate_registry()
        indira_result = self.validate_indira_integration()
        results.append(indira_result)

        report = []
        report.append("=" * 80)
        report.append("DIXVISION INDIRA Strategy Registry Validation Report")
        report.append("=" * 80)
        report.append("")

        valid_count = sum(1 for r in results if r.is_valid)
        report.append(f"Total Strategies Validated: {len(results)}")
        report.append(f"Valid Strategies: {valid_count}")
        report.append(f"Invalid Strategies: {len(results) - valid_count}")
        report.append("")

        for result in results:
            status = "VALID" if result.is_valid else "INVALID"
            report.append(f"Strategy: {result.strategy_id} - {status}")

            if result.errors:
                report.append("  Errors:")
                for error in result.errors:
                    report.append(f"    - {error}")

            if result.warnings:
                report.append("  Warnings:")
                for warning in result.warnings:
                    report.append(f"    - {warning}")

            report.append("")

        report.append("=" * 80)
        report.append("Validation Summary")
        report.append("=" * 80)

        if all(r.is_valid for r in results):
            report.append("ALL STRATEGIES PASSED VALIDATION")
            report.append("Registry is ready for INDIRA integration")
        else:
            report.append("SOME STRATEGIES FAILED VALIDATION")
            report.append("Please review errors and warnings above")

        return "\n".join(report)


def main():
    """Main validation function"""
    registry_path = (
        "c:/dix_vision_v42.2/containers/system_core/strategies/registry/strategy_registry.yaml"
    )

    validator = StrategyRegistryValidator(registry_path)
    report = validator.generate_validation_report()

    print(report)

    # Save report to file
    report_path = (
        "c:/dix_vision_v42.2/containers/system_core/strategies/registry/validation_report.txt"
    )
    with open(report_path, "w") as f:
        f.write(report)

    logger.info(f"Validation report saved to {report_path}")


if __name__ == "__main__":
    main()
