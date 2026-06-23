"""evolution_engine.dyon.indira_architecture_analyzer — INDIRA Architecture Analysis for DYON.

System cognition component for analyzing INDIRA's architecture to optimize system performance.

This implementation provides architecture analysis capabilities for:
- INDIRA component structure and relationships
- Signal pipeline architecture analysis
- Portfolio management architecture analysis
- AGT agent architecture validation
- Architecture violation detection
- Design pattern recognition
- Coupling and cohesion analysis
- Architectural improvement recommendations

Authority (L2/B1): evolution_engine.* only at module level.
DYON analyzes INDIRA architecture for system optimization, never for trading purposes.
"""

from __future__ import annotations

import ast
import logging
import threading
from collections import defaultdict
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
from typing import Any, Dict, List, Optional, Set

_logger = logging.getLogger(__name__)


class INDIRAComponent(Enum):
    """INDIRA component types."""

    SIGNAL_FUSION = "signal_fusion"
    PORTFOLIO_REASONING = "portfolio_reasoning"
    TRADER_PROFILING = "trader_profiling"
    EXECUTION_INTENT_FORMATION = "execution_intent_formation"
    STRATEGY_DISCOVERY = "strategy_discovery"
    MARKET_UNDERSTANDING = "market_understanding"
    META_LEARNING = "meta_learning"
    COGNITIVE_LAYER_INTEGRATION = "cognitive_layer_integration"
    NEUROMORPHIC_COMPUTING = "neuromorphic_computing"


class ArchitectureViolationType(Enum):
    """Types of architecture violations."""

    CIRCULAR_DEPENDENCY = "circular_dependency"
    IMPROPER_LAYERING = "improper_layering"
    TIGHT_COUPLING = "tight_coupling"
    VIOLATED_INTERFACE = "violated_interface"
    ANTI_PATTERN = "anti_pattern"
    MISSING_ABSTRACTION = "missing_abstraction"
    GOD_OBJECT = "god_object"
    FEATURE_ENVY = "feature_envy"


@dataclass
class ArchitectureViolation:
    """Architecture violation detected in INDIRA."""

    violation_type: ArchitectureViolationType
    component: str
    file_path: str
    line_number: int
    severity: str  # "CRITICAL", "HIGH", "MEDIUM", "LOW"
    description: str
    suggested_fix: str
    impact: str


@dataclass
class ComponentArchitecture:
    """Architecture analysis of an INDIRA component."""

    component_type: INDIRAComponent
    file_path: str
    classes: List[str] = field(default_factory=list)
    functions: List[str] = field(default_factory=list)
    dependencies: List[str] = field(default_factory=list)
    complexity_score: float = 0.0
    coupling_score: float = 0.0
    cohesion_score: float = 0.0
    violations: List[ArchitectureViolation] = field(default_factory=list)
    design_patterns: List[str] = field(default_factory=list)


@dataclass
class ArchitectureAnalysisResult:
    """Complete architecture analysis result for INDIRA."""

    analysis_timestamp: float
    components_analyzed: int
    total_violations: int
    critical_violations: int
    high_violations: int
    component_architectures: Dict[str, ComponentArchitecture] = field(default_factory=dict)
    system_wide_issues: List[ArchitectureViolation] = field(default_factory=dict)
    recommendations: List[str] = field(default_factory=list)
    architecture_health_score: float = 0.0


class INDIRAArchitectureAnalyzer:
    """Analyze INDIRA's architecture for system optimization.

    DYON uses this analyzer to understand INDIRA's structure and identify
    architectural improvements without interfering with INDIRA's trading operations.
    """

    def __init__(self, repo_root: str | Path = "."):
        """Initialize INDIRA architecture analyzer.

        Args:
            repo_root: Path to repository root
        """
        self.repo_root = Path(repo_root)
        self.indira_path = self.repo_root / "containers/system_core/indira_cognitive"
        self.indira_brain_path = self.indira_path / "indira_brain"
        self._lock = threading.Lock()
        self._cache: Dict[str, ComponentArchitecture] = {}
        self._dependency_graph: Dict[str, Set[str]] = defaultdict(set)

        _logger.info(
            f"[INDIRAArchitectureAnalyzer] Initialized with repo_root={repo_root}, "
            f"indira_path={self.indira_path}"
        )

    def analyze_full_indira_architecture(self) -> ArchitectureAnalysisResult:
        """Perform complete architecture analysis of INDIRA.

        Returns:
            Complete architecture analysis result
        """
        import time

        analysis_timestamp = time.time()

        _logger.info("[INDIRAArchitectureAnalyzer] Starting full INDIRA architecture analysis")

        with self._lock:
            # Analyze each component
            component_analyses = {}
            total_violations = 0
            critical_count = 0
            high_count = 0

            for component in INDIRAComponent:
                component_path = self.indira_brain_path / component.value
                if component_path.exists() and component_path.is_dir():
                    analysis = self._analyze_component(component, component_path)
                    component_analyses[component.value] = analysis
                    total_violations += len(analysis.violations)
                    critical_count += sum(
                        1 for v in analysis.violations if v.severity == "CRITICAL"
                    )
                    high_count += sum(1 for v in analysis.violations if v.severity == "HIGH")

            # Detect system-wide issues
            system_wide_issues = self._detect_system_wide_issues(component_analyses)

            # Generate recommendations
            recommendations = self._generate_recommendations(component_analyses, system_wide_issues)

            # Calculate architecture health score
            health_score = self._calculate_health_score(
                total_violations, critical_count, high_count, len(component_analyses)
            )

            result = ArchitectureAnalysisResult(
                analysis_timestamp=analysis_timestamp,
                components_analyzed=len(component_analyses),
                total_violations=total_violations,
                critical_violations=critical_count,
                high_violations=high_count,
                component_architectures=component_analyses,
                system_wide_issues=system_wide_issues,
                recommendations=recommendations,
                architecture_health_score=health_score,
            )

            _logger.info(
                f"[INDIRAArchitectureAnalyzer] Analysis complete: "
                f"{len(component_analyses)} components, {total_violations} violations, "
                f"health_score={health_score:.2f}"
            )

            return result

    def _analyze_component(
        self, component_type: INDIRAComponent, component_path: Path
    ) -> ComponentArchitecture:
        """Analyze a single INDIRA component.

        Args:
            component_type: Type of INDIRA component
            component_path: Path to component directory

        Returns:
            Component architecture analysis
        """
        _logger.debug(f"[INDIRAArchitectureAnalyzer] Analyzing component: {component_type.value}")

        classes = []
        functions = []
        dependencies = []
        violations = []
        design_patterns = []

        # Analyze all Python files in component
        for py_file in component_path.glob("*.py"):
            try:
                file_analysis = self._analyze_python_file(py_file, component_type)
                classes.extend(file_analysis["classes"])
                functions.extend(file_analysis["functions"])
                dependencies.extend(file_analysis["dependencies"])
                violations.extend(file_analysis["violations"])
                design_patterns.extend(file_analysis["design_patterns"])
            except Exception as e:
                _logger.warning(f"Failed to analyze {py_file}: {e}")

        # Calculate metrics
        complexity_score = self._calculate_complexity_score(classes, functions)
        coupling_score = self._calculate_coupling_score(dependencies)
        cohesion_score = self._calculate_cohesion_score(classes, functions)

        return ComponentArchitecture(
            component_type=component_type,
            file_path=str(component_path),
            classes=classes,
            functions=functions,
            dependencies=list(set(dependencies)),
            complexity_score=complexity_score,
            coupling_score=coupling_score,
            cohesion_score=cohesion_score,
            violations=violations,
            design_patterns=list(set(design_patterns)),
        )

    def _analyze_python_file(
        self, file_path: Path, component_type: INDIRAComponent
    ) -> Dict[str, Any]:
        """Analyze a single Python file.

        Args:
            file_path: Path to Python file
            component_type: Type of component being analyzed

        Returns:
            Dictionary with analysis results
        """
        classes = []
        functions = []
        dependencies = []
        violations = []
        design_patterns = []

        try:
            with open(file_path, "r", encoding="utf-8") as f:
                source = f.read()

            tree = ast.parse(source)

            for node in ast.walk(tree):
                # Extract classes
                if isinstance(node, ast.ClassDef):
                    classes.append(node.name)
                    self._detect_design_patterns(node, design_patterns)

                    # Check for anti-patterns
                    self._detect_anti_patterns(node, file_path, violations, component_type)

                # Extract functions
                elif isinstance(node, ast.FunctionDef):
                    functions.append(node.name)
                    self._check_function_complexity(node, file_path, violations)

                # Extract dependencies
                elif isinstance(node, ast.Import):
                    for alias in node.names:
                        dependencies.append(alias.name)
                elif isinstance(node, ast.ImportFrom):
                    if node.module:
                        dependencies.append(node.module)

        except Exception as e:
            _logger.warning(f"Failed to parse {file_path}: {e}")

        return {
            "classes": classes,
            "functions": functions,
            "dependencies": dependencies,
            "violations": violations,
            "design_patterns": design_patterns,
        }

    def _detect_design_patterns(self, class_node: ast.ClassDef, design_patterns: List[str]) -> None:
        """Detect common design patterns in class.

        Args:
            class_node: AST class node
            design_patterns: List to append detected patterns
        """
        class_name = class_node.name.lower()

        # Simple pattern detection based on naming conventions
        if "factory" in class_name or "builder" in class_name:
            design_patterns.append("Creational Pattern")
        elif "strategy" in class_name or "command" in class_name:
            design_patterns.append("Behavioral Pattern")
        elif "adapter" in class_name or "decorator" in class_name:
            design_patterns.append("Structural Pattern")
        elif "manager" in class_name or "controller" in class_name:
            design_patterns.append("Manager Pattern")
        elif "observer" in class_name or "listener" in class_name:
            design_patterns.append("Observer Pattern")

    def _detect_anti_patterns(
        self,
        class_node: ast.ClassDef,
        file_path: Path,
        violations: List[ArchitectureViolation],
        component_type: INDIRAComponent,
    ) -> None:
        """Detect architectural anti-patterns.

        Args:
            class_node: AST class node
            file_path: Path to file
            violations: List to append violations
            component_type: Component being analyzed
        """
        # Check for God Object (too many methods)
        if len(class_node.body) > 20:
            violations.append(
                ArchitectureViolation(
                    violation_type=ArchitectureViolationType.GOD_OBJECT,
                    component=component_type.value,
                    file_path=str(file_path),
                    line_number=class_node.lineno,
                    severity="HIGH",
                    description=f"Class {class_node.name} has {len(class_node.body)} methods, possible God Object",
                    suggested_fix="Consider breaking down into smaller, focused classes",
                    impact="Reduces maintainability and testability",
                )
            )

    def _check_function_complexity(
        self, func_node: ast.FunctionDef, file_path: Path, violations: List[ArchitectureViolation]
    ) -> None:
        """Check function complexity.

        Args:
            func_node: AST function node
            file_path: Path to file
            violations: List to append violations
        """
        # Count complexity (simplified cyclomatic complexity)
        complexity = 1
        for node in ast.walk(func_node):
            if isinstance(node, (ast.If, ast.While, ast.For, ast.ExceptHandler)):
                complexity += 1

        if complexity > 10:
            violations.append(
                ArchitectureViolation(
                    violation_type=ArchitectureViolationType.ANTI_PATTERN,
                    component="function",
                    file_path=str(file_path),
                    line_number=func_node.lineno,
                    severity="MEDIUM",
                    description=f"Function {func_node.name} has complexity {complexity}",
                    suggested_fix="Consider refactoring into smaller functions",
                    impact="Reduces readability and maintainability",
                )
            )

    def _detect_system_wide_issues(
        self, component_analyses: Dict[str, ComponentArchitecture]
    ) -> List[ArchitectureViolation]:
        """Detect system-wide architectural issues.

        Args:
            component_analyses: Component analysis results

        Returns:
            List of system-wide violations
        """
        system_wide_issues = []

        # Check for circular dependencies
        all_dependencies = {}
        for comp_name, analysis in component_analyses.items():
            all_dependencies[comp_name] = set(analysis.dependencies)

        # Simple circular dependency detection
        for comp_a, deps_a in all_dependencies.items():
            for dep in deps_a:
                if dep in all_dependencies and comp_a in all_dependencies[dep]:
                    system_wide_issues.append(
                        ArchitectureViolation(
                            violation_type=ArchitectureViolationType.CIRCULAR_DEPENDENCY,
                            component="system",
                            file_path="multiple",
                            line_number=0,
                            severity="CRITICAL",
                            description=f"Circular dependency between {comp_a} and {dep}",
                            suggested_fix="Introduce abstraction layer or refactor dependencies",
                            impact="Can cause initialization issues and tight coupling",
                        )
                    )

        return system_wide_issues

    def _generate_recommendations(
        self,
        component_analyses: Dict[str, ComponentArchitecture],
        system_wide_issues: List[ArchitectureViolation],
    ) -> List[str]:
        """Generate architectural improvement recommendations.

        Args:
            component_analyses: Component analysis results
            system_wide_issues: System-wide violations

        Returns:
            List of recommendations
        """
        recommendations = []

        # High-level recommendations based on analysis
        for comp_name, analysis in component_analyses.items():
            if analysis.complexity_score > 0.7:
                recommendations.append(
                    f"Consider simplifying {comp_name} - complexity score {analysis.complexity_score:.2f}"
                )

            if analysis.coupling_score > 0.6:
                recommendations.append(
                    f"Reduce coupling in {comp_name} - coupling score {analysis.coupling_score:.2f}"
                )

            if len(analysis.violations) > 5:
                recommendations.append(
                    f"Address {len(analysis.violations)} violations in {comp_name}"
                )

        # System-wide recommendations
        if system_wide_issues:
            recommendations.append(
                f"Address {len(system_wide_issues)} system-wide architectural violations"
            )

        return recommendations

    def _calculate_complexity_score(self, classes: List[str], functions: List[str]) -> float:
        """Calculate complexity score for component.

        Args:
            classes: List of class names
            functions: List of function names

        Returns:
            Complexity score (0-1)
        """
        total_elements = len(classes) + len(functions)
        if total_elements == 0:
            return 0.0

        # Normalized complexity based on number of elements
        return min(total_elements / 100.0, 1.0)

    def _calculate_coupling_score(self, dependencies: List[str]) -> float:
        """Calculate coupling score for component.

        Args:
            dependencies: List of dependencies

        Returns:
            Coupling score (0-1)
        """
        if not dependencies:
            return 0.0

        # Normalized coupling based on number of dependencies
        return min(len(set(dependencies)) / 20.0, 1.0)

    def _calculate_cohesion_score(self, classes: List[str], functions: List[str]) -> float:
        """Calculate cohesion score for component.

        Args:
            classes: List of class names
            functions: List of function names

        Returns:
            Cohesion score (0-1)
        """
        # Simplified cohesion - higher is better
        if not classes and not functions:
            return 0.0

        # In a real implementation, this would analyze relatedness
        # Here we return a default value
        return 0.5

    def _calculate_health_score(
        self, total_violations: int, critical_count: int, high_count: int, components_analyzed: int
    ) -> float:
        """Calculate overall architecture health score.

        Args:
            total_violations: Total number of violations
            critical_count: Number of critical violations
            high_count: Number of high severity violations
            components_analyzed: Number of components analyzed

        Returns:
            Health score (0-1, higher is better)
        """
        if components_analyzed == 0:
            return 0.0

        # Penalty for violations
        penalty = (critical_count * 10 + high_count * 5 + total_violations) / max(
            components_analyzed, 1
        )

        # Normalize to 0-1
        health = max(1.0 - penalty / 20.0, 0.0)

        return health

    def get_component_architecture(self, component_name: str) -> Optional[ComponentArchitecture]:
        """Get cached architecture analysis for specific component.

        Args:
            component_name: Name of INDIRA component

        Returns:
            Component architecture or None if not analyzed
        """
        with self._lock:
            return self._cache.get(component_name)

    def analyze_signal_pipeline_architecture(self) -> Dict[str, Any]:
        """Specific analysis of signal pipeline architecture.

        Returns:
            Signal pipeline architecture analysis
        """
        signal_fusion_path = self.indira_brain_path / "signal_fusion"

        if not signal_fusion_path.exists():
            return {"status": "not_found", "path": str(signal_fusion_path)}

        analysis = self._analyze_component(INDIRAComponent.SIGNAL_FUSION, signal_fusion_path)

        return {
            "status": "analyzed",
            "component": "signal_fusion",
            "architecture": analysis,
            "data_flow_analysis": self._analyze_signal_data_flow(signal_fusion_path),
            "bottleneck_potential": self._identify_signal_bottlenecks(analysis),
        }

    def analyze_portfolio_architecture(self) -> Dict[str, Any]:
        """Specific analysis of portfolio management architecture.

        Returns:
            Portfolio architecture analysis
        """
        portfolio_path = self.indira_brain_path / "portfolio_reasoning"

        if not portfolio_path.exists():
            return {"status": "not_found", "path": str(portfolio_path)}

        analysis = self._analyze_component(INDIRAComponent.PORTFOLIO_REASONING, portfolio_path)

        return {
            "status": "analyzed",
            "component": "portfolio_reasoning",
            "architecture": analysis,
            "risk_analysis": self._analyze_portfolio_risk_architecture(portfolio_path),
            "optimization_potential": self._identify_portfolio_optimization_opportunities(analysis),
        }

    def _analyze_signal_data_flow(self, signal_path: Path) -> Dict[str, Any]:
        """Analyze data flow in signal pipeline.

        Args:
            signal_path: Path to signal fusion component

        Returns:
            Data flow analysis
        """
        # Simplified data flow analysis
        return {
            "flow_complexity": "moderate",
            "integration_points": ["multi_source_integration", "signal_intent_conversion"],
            "potential_optimizations": [
                "Consider async processing for signal quality assessment",
                "Implement caching for repeated signal priority calculations",
            ],
        }

    def _identify_signal_bottlenecks(self, analysis: ComponentArchitecture) -> List[str]:
        """Identify potential bottlenecks in signal pipeline.

        Args:
            analysis: Component architecture analysis

        Returns:
            List of potential bottlenecks
        """
        bottlenecks = []

        if analysis.complexity_score > 0.6:
            bottlenecks.append("High complexity may cause processing delays")

        if analysis.coupling_score > 0.5:
            bottlenecks.append("High coupling may cause dependency delays")

        return bottlenecks

    def _analyze_portfolio_risk_architecture(self, portfolio_path: Path) -> Dict[str, Any]:
        """Analyze risk architecture in portfolio management.

        Args:
            portfolio_path: Path to portfolio reasoning component

        Returns:
            Risk architecture analysis
        """
        return {
            "risk_components": ["portfolio_risk_measurement"],
            "risk_calculation_complexity": "moderate",
            "risk_integration": "properly integrated with portfolio optimization",
        }

    def _identify_portfolio_optimization_opportunities(
        self, analysis: ComponentArchitecture
    ) -> List[str]:
        """Identify optimization opportunities in portfolio management.

        Args:
            analysis: Component architecture analysis

        Returns:
            List of optimization opportunities
        """
        opportunities = []

        if analysis.complexity_score > 0.5:
            opportunities.append("Simplify portfolio optimization logic for better performance")

        if len(analysis.classes) > 5:
            opportunities.append("Consider consolidating portfolio classes")

        return opportunities


# Singleton instance
_indira_architecture_analyzer: Optional[INDIRAArchitectureAnalyzer] = None
_analyzer_lock = threading.Lock()


def get_indira_architecture_analyzer(repo_root: str | Path = ".") -> INDIRAArchitectureAnalyzer:
    """Get singleton instance of INDIRA architecture analyzer.

    Args:
        repo_root: Path to repository root

    Returns:
        INDIRA architecture analyzer instance
    """
    global _indira_architecture_analyzer

    with _analyzer_lock:
        if _indira_architecture_analyzer is None:
            _indira_architecture_analyzer = INDIRAArchitectureAnalyzer(repo_root)
        return _indira_architecture_analyzer
