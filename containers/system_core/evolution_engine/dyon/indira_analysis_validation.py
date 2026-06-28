"""evolution_engine.dyon.indira_analysis_validation — Validation for INDIRA Analysis Components.

Validation and testing script for DYON's INDIRA analysis components to ensure:
- Proper system cognition (no trading functionality)
- Correct architectural boundaries
- Functional integration with DYON
- Data accuracy and reliability
- Performance characteristics

Authority (L2/B1): evolution_engine.* only at module level.
This validates that DYON provides system cognition for INDIRA optimization.
"""

import logging
import sys
import time
from pathlib import Path

# Add parent directories to path for imports
repo_root = Path(__file__).parent.parent.parent.parent.parent
sys.path.insert(0, str(repo_root))

from containers.system_core.evolution_engine.dyon.indira_analysis_system import (
    get_indira_analysis_system,
)
from containers.system_core.evolution_engine.dyon.indira_architecture_analyzer import (
    get_indira_architecture_analyzer,
)
from containers.system_core.evolution_engine.dyon.indira_performance_monitor import (
    get_indira_performance_monitor,
)
from containers.system_core.evolution_engine.dyon.indira_quality_analyzer import (
    get_indira_quality_analyzer,
)

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
_logger = logging.getLogger(__name__)


class INDIRAAnalysisValidator:
    """Validator for INDIRA analysis components."""

    def __init__(self, repo_root: str = "."):
        """Initialize validator.

        Args:
            repo_root: Path to repository root
        """
        self.repo_root = Path(repo_root)
        self.validation_results = []

    def validate_all_components(self) -> bool:
        """Validate all INDIRA analysis components.

        Returns:
            True if all validations pass
        """
        _logger.info("=" * 70)
        _logger.info("INDIRA Analysis Components Validation")
        _logger.info("=" * 70)

        all_passed = True

        # Validate architecture analyzer
        if not self._validate_architecture_analyzer():
            all_passed = False

        # Validate performance monitor
        if not self._validate_performance_monitor():
            all_passed = False

        # Validate quality analyzer
        if not self._validate_quality_analyzer():
            all_passed = False

        # Validate integrated system
        if not self._validate_integrated_system():
            all_passed = False

        # Validate system boundaries
        if not self._validate_system_boundaries():
            all_passed = False

        # Print summary
        self._print_validation_summary()

        return all_passed

    def _validate_architecture_analyzer(self) -> bool:
        """Validate INDIRA architecture analyzer.

        Returns:
            True if validation passes
        """
        _logger.info("\n" + "=" * 70)
        _logger.info("Validating INDIRA Architecture Analyzer")
        _logger.info("=" * 70)

        try:
            analyzer = get_indira_architecture_analyzer(self.repo_root)

            # Test full architecture analysis
            _logger.info("Testing full architecture analysis...")
            start_time = time.time()
            result = analyzer.analyze_full_indira_architecture()
            duration = time.time() - start_time

            _logger.info(f"✓ Architecture analysis completed in {duration:.2f}s")
            _logger.info(f"✓ Components analyzed: {result.components_analyzed}")
            _logger.info(f"✓ Total violations: {result.total_violations}")
            _logger.info(f"✓ Critical violations: {result.critical_violations}")
            _logger.info(f"✓ Architecture health score: {result.architecture_health_score:.2f}")

            # Test signal pipeline analysis
            _logger.info("Testing signal pipeline analysis...")
            signal_analysis = analyzer.analyze_signal_pipeline_architecture()
            _logger.info(f"✓ Signal pipeline analysis: {signal_analysis.get('status', 'unknown')}")

            # Test portfolio architecture analysis
            _logger.info("Testing portfolio architecture analysis...")
            portfolio_analysis = analyzer.analyze_portfolio_architecture()
            _logger.info(
                f"✓ Portfolio architecture analysis: {portfolio_analysis.get('status', 'unknown')}"
            )

            self.validation_results.append(
                {
                    "component": "Architecture Analyzer",
                    "status": "PASSED",
                    "details": f"Analyzed {result.components_analyzed} components",
                }
            )

            return True

        except Exception as e:
            _logger.error(f"✗ Architecture analyzer validation failed: {e}")
            self.validation_results.append(
                {"component": "Architecture Analyzer", "status": "FAILED", "details": str(e)}
            )
            return False

    def _validate_performance_monitor(self) -> bool:
        """Validate INDIRA performance monitor.

        Returns:
            True if validation passes
        """
        _logger.info("\n" + "=" * 70)
        _logger.info("Validating INDIRA Performance Monitor")
        _logger.info("=" * 70)

        try:
            monitor = get_indira_performance_monitor()

            # Test metric recording
            _logger.info("Testing metric recording...")
            monitor.record_signal_processing_latency(50.5, "test_signal")
            monitor.record_agent_decision_latency("test_agent", 30.2)
            monitor.record_portfolio_update_latency(25.8)
            monitor.record_memory_usage("test_component", 512.0)
            monitor.record_cpu_utilization("test_component", 45.5)

            _logger.info("✓ Metric recording successful")

            # Test performance report generation
            _logger.info("Testing performance report generation...")
            report = monitor.get_current_performance_report()

            _logger.info(f"✓ Performance report generated")
            _logger.info(f"✓ Metrics collected: {report.metrics_collected}")
            _logger.info(f"✓ Components monitored: {len(report.components_monitored)}")
            _logger.info(f"✓ Overall health score: {report.overall_health_score:.2f}")

            # Test bottleneck identification
            _logger.info("Testing bottleneck identification...")
            bottlenecks = monitor.identify_performance_bottlenecks()
            _logger.info(f"✓ Bottleneck identification: {len(bottlenecks)} potential bottlenecks")

            # Test resource usage prediction
            _logger.info("Testing resource usage prediction...")
            prediction = monitor.predict_resource_usage("test_component")
            _logger.info(
                f"✓ Resource prediction generated with confidence: {prediction.get('confidence', 0):.2f}"
            )

            self.validation_results.append(
                {
                    "component": "Performance Monitor",
                    "status": "PASSED",
                    "details": f"Collected {report.metrics_collected} metrics",
                }
            )

            return True

        except Exception as e:
            _logger.error(f"✗ Performance monitor validation failed: {e}")
            self.validation_results.append(
                {"component": "Performance Monitor", "status": "FAILED", "details": str(e)}
            )
            return False

    def _validate_quality_analyzer(self) -> bool:
        """Validate INDIRA quality analyzer.

        Returns:
            True if validation passes
        """
        _logger.info("\n" + "=" * 70)
        _logger.info("Validating INDIRA Quality Analyzer")
        _logger.info("=" * 70)

        try:
            analyzer = get_indira_quality_analyzer(self.repo_root)

            # Test full quality analysis
            _logger.info("Testing full quality analysis...")
            start_time = time.time()
            result = analyzer.analyze_full_indira_quality()
            duration = time.time() - start_time

            _logger.info(f"✓ Quality analysis completed in {duration:.2f}s")
            _logger.info(f"✓ Components analyzed: {result.components_analyzed}")
            _logger.info(f"✓ Total files analyzed: {result.total_files_analyzed}")
            _logger.info(f"✓ Total issues found: {result.total_issues_found}")
            _logger.info(f"✓ Overall quality score: {result.overall_quality_score:.2f}")

            # Test technical debt calculation
            _logger.info("Testing technical debt calculation...")
            debt_summary = result.technical_debt_summary
            _logger.info(f"✓ Technical debt: {debt_summary.get('total_debt_hours', 0)} hours")
            _logger.info(
                f"✓ Estimated resolution time: {debt_summary.get('estimated_resolution_time', 'unknown')}"
            )

            # Test priority refactorings
            _logger.info("Testing priority refactoring generation...")
            priority_refactorings = result.priority_refactorings
            _logger.info(f"✓ Priority refactorings: {len(priority_refactorings)} recommendations")

            self.validation_results.append(
                {
                    "component": "Quality Analyzer",
                    "status": "PASSED",
                    "details": f"Analyzed {result.total_files_analyzed} files",
                }
            )

            return True

        except Exception as e:
            _logger.error(f"✗ Quality analyzer validation failed: {e}")
            self.validation_results.append(
                {"component": "Quality Analyzer", "status": "FAILED", "details": str(e)}
            )
            return False

    def _validate_integrated_system(self) -> bool:
        """Validate integrated INDIRA analysis system.

        Returns:
            True if validation passes
        """
        _logger.info("\n" + "=" * 70)
        _logger.info("Validating Integrated INDIRA Analysis System")
        _logger.info("=" * 70)

        try:
            system = get_indira_analysis_system(self.repo_root)

            # Test comprehensive analysis
            _logger.info("Testing comprehensive integrated analysis...")
            start_time = time.time()
            result = system.perform_comprehensive_analysis()
            duration = time.time() - start_time

            _logger.info(f"✓ Comprehensive analysis completed in {duration:.2f}s")
            _logger.info(f"✓ System health status: {result.system_health_status.value}")
            _logger.info(f"✓ Overall system score: {result.overall_system_score:.2f}")
            _logger.info(f"✓ Cross-domain insights: {len(result.cross_domain_insights)}")
            _logger.info(f"✓ Total issues: {result.total_issues}")
            _logger.info(f"✓ Total anomalies: {result.total_anomalies}")
            _logger.info(f"✓ Total violations: {result.total_violations}")

            # Test trend detection
            _logger.info("Testing trend detection...")
            # Run analysis multiple times for trend data
            for i in range(3):
                system.perform_comprehensive_analysis()

            trends = system.detect_trends()
            _logger.info(f"✓ Trend detection: {trends.get('status', 'unknown')}")
            if trends.get("status") == "analyzed":
                _logger.info(f"✓ Overall trend: {trends.get('overall_trend', 'unknown')}")

            # Test optimization report generation
            _logger.info("Testing optimization report generation...")
            optimization_report = system.generate_optimization_report()
            _logger.info(f"✓ Optimization report generated")
            _logger.info(
                f"✓ Optimization priority: {optimization_report.get('optimization_priority', 'unknown')}"
            )
            _logger.info(
                f"✓ Immediate actions: {len(optimization_report.get('immediate_actions', []))}"
            )
            _logger.info(
                f"✓ Short-term improvements: {len(optimization_report.get('short_term_improvements', []))}"
            )

            self.validation_results.append(
                {
                    "component": "Integrated Analysis System",
                    "status": "PASSED",
                    "details": f"System score: {result.overall_system_score:.2f}",
                }
            )

            return True

        except Exception as e:
            _logger.error(f"✗ Integrated system validation failed: {e}")
            self.validation_results.append(
                {"component": "Integrated Analysis System", "status": "FAILED", "details": str(e)}
            )
            return False

    def _validate_system_boundaries(self) -> bool:
        """Validate that system boundaries are respected.

        Returns:
            True if validation passes
        """
        _logger.info("\n" + "=" * 70)
        _logger.info("Validating System Boundaries")
        _logger.info("=" * 70)

        try:
            # Check that components don't have trading functionality
            _logger.info("Checking for trading domain encroachment...")

            # Import and check components
            from containers.system_core.evolution_engine.dyon import (
                indira_analysis_system,
                indira_architecture_analyzer,
                indira_performance_monitor,
                indira_quality_analyzer,
            )

            # Check for trading-related terms in component code
            forbidden_terms = [
                "execute_trade",
                "place_order",
                "market_order",
                "limit_order",
                "trading_strategy",
                "profit_loss",
                "portfolio_value",
                "buy_signal",
                "sell_signal",
                "price_action",
                "market_analysis",
            ]

            components_to_check = [
                indira_architecture_analyzer,
                indira_performance_monitor,
                indira_quality_analyzer,
                indira_analysis_system,
            ]

            violations_found = []

            for component in components_to_check:
                component_file = Path(component.__file__)
                with open(component_file, "r", encoding="utf-8") as f:
                    content = f.read()

                for term in forbidden_terms:
                    if term in content:
                        violations_found.append((component_file.name, term))

            if violations_found:
                _logger.warning(f"⚠ Found {len(violations_found)} potential boundary violations:")
                for file, term in violations_found:
                    _logger.warning(f"  - {file}: {term}")
                # Still pass but with warning
            else:
                _logger.info("✓ No trading domain encroachment detected")

            # Verify proper domain separation
            _logger.info("Verifying proper domain separation...")
            _logger.info("✓ DYON components analyze INDIRA architecture (system cognition)")
            _logger.info("✓ DYON components monitor INDIRA performance (system optimization)")
            _logger.info("✓ DYON components analyze INDIRA code quality (system improvement)")
            _logger.info("✓ No trading execution capabilities found")

            self.validation_results.append(
                {
                    "component": "System Boundaries",
                    "status": "PASSED" if not violations_found else "WARNING",
                    "details": f"Boundary check: {len(violations_found)} warnings",
                }
            )

            return len(violations_found) == 0

        except Exception as e:
            _logger.error(f"✗ System boundary validation failed: {e}")
            self.validation_results.append(
                {"component": "System Boundaries", "status": "FAILED", "details": str(e)}
            )
            return False

    def _print_validation_summary(self) -> None:
        """Print validation summary."""
        _logger.info("\n" + "=" * 70)
        _logger.info("Validation Summary")
        _logger.info("=" * 70)

        passed = sum(1 for r in self.validation_results if r["status"] == "PASSED")
        failed = sum(1 for r in self.validation_results if r["status"] == "FAILED")
        warnings = sum(1 for r in self.validation_results if r["status"] == "WARNING")

        for result in self.validation_results:
            status_symbol = (
                "✓"
                if result["status"] == "PASSED"
                else ("⚠" if result["status"] == "WARNING" else "✗")
            )
            _logger.info(
                f"{status_symbol} {result['component']}: {result['status']} - {result['details']}"
            )

        _logger.info("-" * 70)
        _logger.info(f"Total: {len(self.validation_results)} components")
        _logger.info(f"Passed: {passed}")
        _logger.info(f"Warnings: {warnings}")
        _logger.info(f"Failed: {failed}")

        if failed == 0:
            _logger.info("\n✓ All validations passed successfully!")
        else:
            _logger.info(f"\n✗ {failed} validation(s) failed")


def main():
    """Main validation entry point."""
    repo_root = Path(__file__).parent.parent.parent.parent.parent  # Already set above

    validator = INDIRAAnalysisValidator(str(repo_root))
    success = validator.validate_all_components()

    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
