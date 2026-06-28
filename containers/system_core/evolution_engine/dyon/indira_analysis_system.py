"""evolution_engine.dyon.indira_analysis_system — Integrated DYON→INDIRA Analysis System.

Comprehensive system cognition for DYON to understand and optimize INDIRA's system performance.

This implementation provides integrated analysis capabilities:
- Unified architecture, performance, and quality analysis
- Cross-domain insight generation
- System health scoring and monitoring
- Comprehensive optimization recommendations
- Real-time anomaly detection across domains
- Predictive system analysis
- Automated improvement suggestion generation
- Integration with DYON's cognitive architecture

Authority (L2/B1): evolution_engine.* only at module level.
DYON provides comprehensive system cognition for INDIRA optimization, never for trading purposes.
"""

from __future__ import annotations

import logging
import threading
import time
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

# Import the analysis components
from .indira_architecture_analyzer import (
    ArchitectureAnalysisResult,
    get_indira_architecture_analyzer,
)
from .indira_performance_monitor import (
    PerformanceReport,
    get_indira_performance_monitor,
)
from .indira_quality_analyzer import (
    INDIRAQualityAnalysisResult,
    get_indira_quality_analyzer,
)

_logger = logging.getLogger(__name__)


class AnalysisDomain(Enum):
    """Analysis domains in the integrated system."""

    ARCHITECTURE = "architecture"
    PERFORMANCE = "performance"
    QUALITY = "quality"


class SystemHealthStatus(Enum):
    """Overall system health status."""

    EXCELLENT = "EXCELLENT"
    GOOD = "GOOD"
    WARNING = "WARNING"
    CRITICAL = "CRITICAL"


@dataclass
class CrossDomainInsight:
    """Insight that spans multiple analysis domains."""

    insight_type: str
    related_domains: List[AnalysisDomain]
    components_affected: List[str]
    description: str
    severity: str
    recommended_actions: List[str]
    expected_impact: str
    confidence: float


@dataclass
class IntegratedAnalysisResult:
    """Complete integrated analysis result for INDIRA."""

    analysis_timestamp: float
    analysis_duration_seconds: float

    # Individual domain results
    architecture_result: Optional[ArchitectureAnalysisResult] = None
    performance_result: Optional[PerformanceReport] = None
    quality_result: Optional[INDIRAQualityAnalysisResult] = None

    # Integrated insights
    cross_domain_insights: List[CrossDomainInsight] = field(default_factory=list)
    system_health_status: SystemHealthStatus = SystemHealthStatus.GOOD
    overall_system_score: float = 0.0

    # Recommendations
    immediate_actions: List[str] = field(default_factory=list)
    short_term_improvements: List[str] = field(default_factory=list)
    long_term_strategies: List[str] = field(default_factory=list)

    # Metrics summary
    total_issues: int = 0
    total_anomalies: int = 0
    total_violations: int = 0
    critical_items: int = 0


class INDIRAAnalysisSystem:
    """Integrated analysis system for comprehensive INDIRA system cognition.

    DYON uses this system to combine architecture, performance, and quality
    analysis to provide holistic system understanding and optimization guidance.
    """

    def __init__(self, repo_root: str | Path = "."):
        """Initialize integrated INDIRA analysis system.

        Args:
            repo_root: Path to repository root
        """
        self.repo_root = Path(repo_root)

        # Initialize individual analyzers
        self.architecture_analyzer = get_indira_architecture_analyzer(repo_root)
        self.performance_monitor = get_indira_performance_monitor()
        self.quality_analyzer = get_indira_quality_analyzer(repo_root)

        self._lock = threading.Lock()
        self._analysis_history: List[IntegratedAnalysisResult] = []
        self._max_history_size = 100

        _logger.info(
            f"[INDIRAAnalysisSystem] Initialized integrated analysis system "
            f"with repo_root={repo_root}"
        )

    def perform_comprehensive_analysis(self) -> IntegratedAnalysisResult:
        """Perform comprehensive integrated analysis of INDIRA.

        Returns:
            Complete integrated analysis result
        """
        start_time = time.time()

        _logger.info("[INDIRAAnalysisSystem] Starting comprehensive INDIRA analysis")

        with self._lock:
            # Perform individual domain analyses
            architecture_result = self.architecture_analyzer.analyze_full_indira_architecture()
            performance_result = self.performance_monitor.get_current_performance_report()
            quality_result = self.quality_analyzer.analyze_full_indira_quality()

            # Generate cross-domain insights
            cross_domain_insights = self._generate_cross_domain_insights(
                architecture_result, performance_result, quality_result
            )

            # Calculate overall system health
            system_health_status, overall_system_score = self._calculate_system_health(
                architecture_result, performance_result, quality_result
            )

            # Generate recommendations
            immediate_actions, short_term_improvements, long_term_strategies = (
                self._generate_integrated_recommendations(
                    architecture_result, performance_result, quality_result, cross_domain_insights
                )
            )

            # Calculate summary metrics
            total_issues = quality_result.total_issues_found if quality_result else 0
            total_anomalies = performance_result.anomalies_detected if performance_result else 0
            total_violations = architecture_result.total_violations if architecture_result else 0
            critical_items = (
                (quality_result.total_issues_found if quality_result else 0)
                + (performance_result.anomalies_detected if performance_result else 0)
                + (architecture_result.critical_violations if architecture_result else 0)
            )

            result = IntegratedAnalysisResult(
                analysis_timestamp=time.time(),
                analysis_duration_seconds=time.time() - start_time,
                architecture_result=architecture_result,
                performance_result=performance_result,
                quality_result=quality_result,
                cross_domain_insights=cross_domain_insights,
                system_health_status=system_health_status,
                overall_system_score=overall_system_score,
                immediate_actions=immediate_actions,
                short_term_improvements=short_term_improvements,
                long_term_strategies=long_term_strategies,
                total_issues=total_issues,
                total_anomalies=total_anomalies,
                total_violations=total_violations,
                critical_items=critical_items,
            )

            # Store in history
            self._analysis_history.append(result)
            if len(self._analysis_history) > self._max_history_size:
                self._analysis_history.pop(0)

            _logger.info(
                f"[INDIRAAnalysisSystem] Comprehensive analysis complete: "
                f"duration={time.time() - start_time:.2f}s, "
                f"health={system_health_status.value}, score={overall_system_score:.2f}"
            )

            return result

    def _generate_cross_domain_insights(
        self,
        architecture_result: Optional[ArchitectureAnalysisResult],
        performance_result: Optional[PerformanceReport],
        quality_result: Optional[INDIRAQualityAnalysisResult],
    ) -> List[CrossDomainInsight]:
        """Generate insights that span multiple analysis domains.

        Args:
            architecture_result: Architecture analysis result
            performance_result: Performance analysis result
            quality_result: Quality analysis result

        Returns:
            List of cross-domain insights
        """
        insights = []

        # Architecture + Performance insights
        if architecture_result and performance_result:
            arch_perf_insights = self._analyze_architecture_performance_correlation(
                architecture_result, performance_result
            )
            insights.extend(arch_perf_insights)

        # Quality + Performance insights
        if quality_result and performance_result:
            qual_perf_insights = self._analyze_quality_performance_correlation(
                quality_result, performance_result
            )
            insights.extend(qual_perf_insights)

        # Architecture + Quality insights
        if architecture_result and quality_result:
            arch_qual_insights = self._analyze_architecture_quality_correlation(
                architecture_result, quality_result
            )
            insights.extend(arch_qual_insights)

        return insights

    def _analyze_architecture_performance_correlation(
        self, architecture_result: ArchitectureAnalysisResult, performance_result: PerformanceReport
    ) -> List[CrossDomainInsight]:
        """Analyze correlation between architecture and performance.

        Args:
            architecture_result: Architecture analysis result
            performance_result: Performance analysis result

        Returns:
            List of cross-domain insights
        """
        insights = []

        # Check if high complexity correlates with performance issues
        for component_name, arch_data in architecture_result.component_architectures.items():
            if arch_data.complexity_score > 0.7:
                # Check if this component has performance issues
                comp_report = performance_result.component_reports.get(component_name)
                if comp_report:
                    latency_data = comp_report.get("latency", {})
                    if latency_data and latency_data.get("mean", 0) > 100:
                        insights.append(
                            CrossDomainInsight(
                                insight_type="complexity_performance_impact",
                                related_domains=[
                                    AnalysisDomain.ARCHITECTURE,
                                    AnalysisDomain.PERFORMANCE,
                                ],
                                components_affected=[component_name],
                                description=f"High architecture complexity ({arch_data.complexity_score:.2f}) correlates with high latency ({latency_data['mean']:.2f}ms)",
                                severity="HIGH",
                                recommended_actions=[
                                    "Refactor complex components to reduce architectural complexity",
                                    "Consider breaking down high-complexity components",
                                    "Implement performance profiling to identify bottlenecks",
                                ],
                                expected_impact="Improved system performance and maintainability",
                                confidence=0.75,
                            )
                        )

        return insights

    def _analyze_quality_performance_correlation(
        self, quality_result: INDIRAQualityAnalysisResult, performance_result: PerformanceReport
    ) -> List[CrossDomainInsight]:
        """Analyze correlation between code quality and performance.

        Args:
            quality_result: Quality analysis result
            performance_result: Performance analysis result

        Returns:
            List of cross-domain insights
        """
        insights = []

        # Check if low quality correlates with performance anomalies
        for component_name, quality_report in quality_result.component_reports.items():
            if quality_report.overall_quality_score < 0.6:
                # Check if this component has performance anomalies
                component_anomalies = [
                    a for a in performance_result.anomalies if a.component == component_name
                ]

                if component_anomalies:
                    insights.append(
                        CrossDomainInsight(
                            insight_type="quality_performance_correlation",
                            related_domains=[AnalysisDomain.QUALITY, AnalysisDomain.PERFORMANCE],
                            components_affected=[component_name],
                            description=f"Low code quality ({quality_report.overall_quality_score:.2f}) correlates with {len(component_anomalies)} performance anomalies",
                            severity="MEDIUM",
                            recommended_actions=[
                                "Address code quality issues to improve performance",
                                "Refactor low-quality components before performance optimization",
                                "Implement code quality gates in CI/CD pipeline",
                            ],
                            expected_impact="Improved performance and reduced maintenance burden",
                            confidence=0.65,
                        )
                    )

        return insights

    def _analyze_architecture_quality_correlation(
        self,
        architecture_result: ArchitectureAnalysisResult,
        quality_result: INDIRAQualityAnalysisResult,
    ) -> List[CrossDomainInsight]:
        """Analyze correlation between architecture and code quality.

        Args:
            architecture_result: Architecture analysis result
            quality_result: Quality analysis result

        Returns:
            List of cross-domain insights
        """
        insights = []

        # Check if architectural violations correlate with quality issues
        for component_name, arch_data in architecture_result.component_architectures.items():
            if len(arch_data.violations) > 3:
                # Check if this component has quality issues
                quality_report = quality_result.component_reports.get(component_name)
                if quality_report and quality_report.total_issues > 5:
                    insights.append(
                        CrossDomainInsight(
                            insight_type="architecture_quality_correlation",
                            related_domains=[AnalysisDomain.ARCHITECTURE, AnalysisDomain.QUALITY],
                            components_affected=[component_name],
                            description=f"Architectural violations ({len(arch_data.violations)}) correlate with code quality issues ({quality_report.total_issues})",
                            severity="HIGH",
                            recommended_actions=[
                                "Address architectural violations to improve code quality",
                                "Refactor to align with proper architectural patterns",
                                "Implement architectural compliance checks",
                            ],
                            expected_impact="Improved code quality and architectural integrity",
                            confidence=0.8,
                        )
                    )

        return insights

    def _calculate_system_health(
        self,
        architecture_result: Optional[ArchitectureAnalysisResult],
        performance_result: Optional[PerformanceReport],
        quality_result: Optional[INDIRAQualityAnalysisResult],
    ) -> Tuple[SystemHealthStatus, float]:
        """Calculate overall system health status and score.

        Args:
            architecture_result: Architecture analysis result
            performance_result: Performance analysis result
            quality_result: Quality analysis result

        Returns:
            Tuple of (health status, overall score)
        """
        scores = []

        if architecture_result:
            scores.append(architecture_result.architecture_health_score)

        if performance_result:
            scores.append(performance_result.overall_health_score)

        if quality_result:
            scores.append(quality_result.overall_quality_score)

        if not scores:
            return SystemHealthStatus.GOOD, 0.5

        overall_score = sum(scores) / len(scores)

        # Determine health status
        if overall_score >= 0.9:
            return SystemHealthStatus.EXCELLENT, overall_score
        elif overall_score >= 0.7:
            return SystemHealthStatus.GOOD, overall_score
        elif overall_score >= 0.5:
            return SystemHealthStatus.WARNING, overall_score
        else:
            return SystemHealthStatus.CRITICAL, overall_score

    def _generate_integrated_recommendations(
        self,
        architecture_result: Optional[ArchitectureAnalysisResult],
        performance_result: Optional[PerformanceReport],
        quality_result: Optional[INDIRAQualityAnalysisResult],
        cross_domain_insights: List[CrossDomainInsight],
    ) -> Tuple[List[str], List[str], List[str]]:
        """Generate integrated recommendations across all domains.

        Args:
            architecture_result: Architecture analysis result
            performance_result: Performance analysis result
            quality_result: Quality analysis result
            cross_domain_insights: Cross-domain insights

        Returns:
            Tuple of (immediate actions, short-term improvements, long-term strategies)
        """
        immediate_actions = []
        short_term_improvements = []
        long_term_strategies = []

        # Critical issues from all domains
        if architecture_result and architecture_result.critical_violations > 0:
            immediate_actions.append(
                f"Address {architecture_result.critical_violations} critical architecture violations"
            )

        if performance_result:
            critical_anomalies = [
                a for a in performance_result.anomalies if a.severity.value == "CRITICAL"
            ]
            if critical_anomalies:
                immediate_actions.append(
                    f"Resolve {len(critical_anomalies)} critical performance anomalies"
                )

        if quality_result:
            critical_issues = sum(
                r.critical_issues for r in quality_result.component_reports.values()
            )
            if critical_issues > 0:
                immediate_actions.append(f"Fix {critical_issues} critical code quality issues")

        # Cross-domain insights
        for insight in cross_domain_insights:
            if insight.severity == "HIGH":
                immediate_actions.extend(insight.recommended_actions[:2])
            elif insight.severity == "MEDIUM":
                short_term_improvements.extend(insight.recommended_actions[:2])
            else:
                long_term_strategies.extend(insight.recommended_actions[:2])

        # Domain-specific recommendations
        if architecture_result:
            short_term_improvements.extend(architecture_result.recommendations[:3])

        if performance_result:
            short_term_improvements.extend(performance_result.recommendations[:3])

        if quality_result:
            long_term_strategies.extend(quality_result.priority_refactorings[:3])

        # Deduplicate and limit
        immediate_actions = list(set(immediate_actions))[:5]
        short_term_improvements = list(set(short_term_improvements))[:7]
        long_term_strategies = list(set(long_term_strategies))[:10]

        return immediate_actions, short_term_improvements, long_term_strategies

    def get_historical_analysis(self, limit: int = 10) -> List[IntegratedAnalysisResult]:
        """Get historical analysis results.

        Args:
            limit: Maximum number of historical results to return

        Returns:
            List of historical analysis results
        """
        with self._lock:
            return list(self._analysis_history[-limit:])

    def detect_trends(self) -> Dict[str, Any]:
        """Detect trends in INDIRA system metrics over time.

        Returns:
            Dictionary with trend analysis results
        """
        if len(self._analysis_history) < 3:
            return {"status": "insufficient_data", "message": "Need at least 3 analysis points"}

        with self._lock:
            recent_analyses = self._analysis_history[-10:]

            # Extract scores over time
            architecture_scores = []
            performance_scores = []
            quality_scores = []
            overall_scores = []

            for analysis in recent_analyses:
                if analysis.architecture_result:
                    architecture_scores.append(
                        analysis.architecture_result.architecture_health_score
                    )
                if analysis.performance_result:
                    performance_scores.append(analysis.performance_result.overall_health_score)
                if analysis.quality_result:
                    quality_scores.append(analysis.quality_result.overall_quality_score)
                overall_scores.append(analysis.overall_system_score)

            # Calculate trends
            def calculate_trend(scores: List[float]) -> str:
                if len(scores) < 2:
                    return "STABLE"

                recent = scores[-3:] if len(scores) >= 3 else scores
                trend = recent[-1] - recent[0]

                if trend > 0.05:
                    return "IMPROVING"
                elif trend < -0.05:
                    return "DECLINING"
                else:
                    return "STABLE"

            return {
                "status": "analyzed",
                "architecture_trend": calculate_trend(architecture_scores),
                "performance_trend": calculate_trend(performance_scores),
                "quality_trend": calculate_trend(quality_scores),
                "overall_trend": calculate_trend(overall_scores),
                "analysis_count": len(recent_analyses),
                "time_span_days": (
                    recent_analyses[-1].analysis_timestamp - recent_analyses[0].analysis_timestamp
                )
                / 86400,
            }

    def generate_optimization_report(self) -> Dict[str, Any]:
        """Generate comprehensive optimization report.

        Returns:
            Optimization report with prioritized actions
        """
        latest_analysis = self.perform_comprehensive_analysis()

        return {
            "report_timestamp": latest_analysis.analysis_timestamp,
            "system_health": latest_analysis.system_health_status.value,
            "overall_score": latest_analysis.overall_system_score,
            "optimimization_priority": self._calculate_optimization_priority(latest_analysis),
            "immediate_actions": latest_analysis.immediate_actions,
            "short_term_improvements": latest_analysis.short_term_improvements,
            "long_term_strategies": latest_analysis.long_term_strategies,
            "cross_domain_insights": [
                {
                    "type": insight.insight_type,
                    "severity": insight.severity,
                    "components": insight.components_affected,
                    "description": insight.description,
                    "impact": insight.expected_impact,
                }
                for insight in latest_analysis.cross_domain_insights
            ],
            "resource_allocation": self._suggest_resource_allocation(latest_analysis),
        }

    def _calculate_optimization_priority(self, analysis: IntegratedAnalysisResult) -> str:
        """Calculate overall optimization priority.

        Args:
            analysis: Integrated analysis result

        Returns:
            Priority level
        """
        if analysis.critical_items > 5:
            return "CRITICAL"
        elif analysis.critical_items > 2 or analysis.total_anomalies > 10:
            return "HIGH"
        elif analysis.total_issues > 20:
            return "MEDIUM"
        else:
            return "LOW"

    def _suggest_resource_allocation(self, analysis: IntegratedAnalysisResult) -> Dict[str, str]:
        """Suggest resource allocation for optimization efforts.

        Args:
            analysis: Integrated analysis result

        Returns:
            Resource allocation suggestions
        """
        priority = self._calculate_optimization_priority(analysis)

        allocation_suggestions = {
            "CRITICAL": "Dedicate full-time resources to immediate critical issues",
            "HIGH": "Allocate 60% of development resources to optimization",
            "MEDIUM": "Allocate 30% of development resources to optimization",
            "LOW": "Allocate 10% of development resources to maintenance",
        }

        return {
            "priority": priority,
            "allocation": allocation_suggestions.get(priority, "Standard allocation"),
            "estimated_effort": self._estimate_optimization_effort(analysis),
        }

    def _estimate_optimization_effort(self, analysis: IntegratedAnalysisResult) -> str:
        """Estimate effort required for optimization.

        Args:
            analysis: Integrated analysis result

        Returns:
            Effort estimate string
        """
        total_items = analysis.total_issues + analysis.total_anomalies + analysis.total_violations

        if total_items > 50:
            return "3-6 months with dedicated team"
        elif total_items > 20:
            return "1-3 months with dedicated resources"
        elif total_items > 10:
            return "2-4 weeks with part-time allocation"
        else:
            return "1-2 weeks with minimal allocation"


# Singleton instance
_analysis_system: Optional[INDIRAAnalysisSystem] = None
_system_lock = threading.Lock()


def get_indira_analysis_system(repo_root: str | Path = ".") -> INDIRAAnalysisSystem:
    """Get singleton instance of integrated INDIRA analysis system.

    Args:
        repo_root: Path to repository root

    Returns:
        INDIRA analysis system instance
    """
    global _analysis_system

    with _system_lock:
        if _analysis_system is None:
            _analysis_system = INDIRAAnalysisSystem(repo_root)
        return _analysis_system
