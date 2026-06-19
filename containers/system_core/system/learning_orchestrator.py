"""
system.learning_orchestrator
DIX VISION v42.2 — System Learning Orchestrator

Central coordination for system learning, insight generation, and
dynamic capability management. Enables the system to learn and autonomously
decide which components to enable/disable.
"""

from __future__ import annotations

import logging
import time
from dataclasses import dataclass
from typing import Any

from system.time_source import now

logger = logging.getLogger(__name__)


@dataclass
class CapabilityInsight:
    """Insight about a system capability."""
    
    capability_name: str
    insight_type: str  # "performance" | "utility" | "dependency" | "cost"
    insight_value: float  # Normalized 0.0-1.0
    confidence: float  # 0.0-1.0
    timestamp: str
    metadata: dict[str, Any] = None

    def __post_init__(self):
        if self.metadata is None:
            self.metadata = {}


@dataclass
class CapabilityDecision:
    """Decision about enabling/disabling a capability."""
    
    capability_name: str
    decision: str  # "enable" | "disable" | "maintain"
    confidence: float  # 0.0-1.0
    reasoning: str
    timestamp: str
    metadata: dict[str, Any] = None

    def __post_init__(self):
        if self.metadata is None:
            self.metadata = {}


class LearningOrchestrator:
    """Orchestrates system learning and dynamic capability management.
    
    Enables the system to:
    - Learn from its own operations
    - Generate insights about capabilities
    - Make decisions about which capabilities to enable/disable
    - Adapt its configuration based on learning
    """
    
    def __init__(self) -> None:
        self._insights: list[CapabilityInsight] = []
        self._decisions: list[CapabilityDecision] = []
        self._capability_performance: dict[str, dict[str, float]] = {}
        self._capability_utility: dict[str, float] = {}
        self._capability_dependencies: dict[str, set[str]] = {}
        self._capability_costs: dict[str, float] = {}
        self._learning_enabled = True
        self._auto_decision_enabled = True
        self._decision_threshold = 0.7  # Confidence threshold for auto-decisions
        
    def start_learning(self) -> bool:
        """Start the learning process."""
        try:
            self._learning_enabled = True
            logger.info("[LEARNING] Learning orchestrator started")
            return True
        except Exception as e:
            logger.error(f"[LEARNING] Failed to start learning: {e}")
            return False
    
    def stop_learning(self) -> bool:
        """Stop the learning process."""
        try:
            self._learning_enabled = False
            logger.info("[LEARNING] Learning orchestrator stopped")
            return True
        except Exception as e:
            logger.error(f"[LEARNING] Failed to stop learning: {e}")
            return False
    
    def enable_auto_decision(self) -> None:
        """Enable automatic decision-making."""
        self._auto_decision_enabled = True
        logger.info("[LEARNING] Auto decision enabled")
    
    def disable_auto_decision(self) -> None:
        """Disable automatic decision-making."""
        self._auto_decision_enabled = False
        logger.info("[LEARNING] Auto decision disabled")
    
    def record_capability_performance(
        self, 
        capability_name: str, 
        metrics: dict[str, float]
    ) -> None:
        """Record performance metrics for a capability."""
        if not self._learning_enabled:
            return
        
        try:
            self._capability_performance[capability_name] = metrics.copy()
            
            # Generate insight from performance
            insight = self._generate_performance_insight(capability_name, metrics)
            self._insights.append(insight)
            
            logger.debug(f"[LEARNING] Recorded performance for {capability_name}")
            
        except Exception as e:
            logger.error(f"[LEARNING] Failed to record performance: {e}")
    
    def record_capability_utility(
        self, 
        capability_name: str, 
        utility_score: float
    ) -> None:
        """Record utility score for a capability."""
        if not self._learning_enabled:
            return
        
        try:
            self._capability_utility[capability_name] = utility_score
            
            # Generate insight from utility
            insight = self._generate_utility_insight(capability_name, utility_score)
            self._insights.append(insight)
            
            logger.debug(f"[LEARNING] Recorded utility {utility_score:.2f} for {capability_name}")
            
        except Exception as e:
            logger.error(f"[LEARNING] Failed to record utility: {e}")
    
    def record_capability_cost(
        self, 
        capability_name: str, 
        cost: float
    ) -> None:
        """Record resource cost for a capability."""
        if not self._learning_enabled:
            return
        
        try:
            self._capability_costs[capability_name] = cost
            
            logger.debug(f"[LEARNING] Recorded cost {cost:.2f} for {capability_name}")
            
        except Exception as e:
            logger.error(f"[LEARNING] Failed to record cost: {e}")
    
    def record_capability_dependency(
        self, 
        capability_name: str, 
        depends_on: str
    ) -> None:
        """Record a dependency between capabilities."""
        if capability_name not in self._capability_dependencies:
            self._capability_dependencies[capability_name] = set()
        
        self._capability_dependencies[capability_name].add(depends_on)
        
        logger.debug(f"[LEARNING] Recorded dependency: {capability_name} depends on {depends_on}")
    
    def generate_insights(self) -> list[CapabilityInsight]:
        """Generate insights from collected data."""
        insights = []
        
        try:
            # Generate performance insights
            for capability, metrics in self._capability_performance.items():
                insight = self._generate_performance_insight(capability, metrics)
                insights.append(insight)
            
            # Generate utility insights
            for capability, utility in self._capability_utility.items():
                insight = self._generate_utility_insight(capability, utility)
                insights.append(insight)
            
            # Generate dependency insights
            for capability, dependencies in self._capability_dependencies.items():
                insight = self._generate_dependency_insight(capability, dependencies)
                insights.append(insight)
            
            # Generate cost insights
            for capability, cost in self._capability_costs.items():
                insight = self._generate_cost_insight(capability, cost)
                insights.append(insight)
            
            self._insights.extend(insights)
            logger.info(f"[LEARNING] Generated {len(insights)} insights")
            
        except Exception as e:
            logger.error(f"[LEARNING] Failed to generate insights: {e}")
        
        return insights
    
    def make_capability_decisions(self) -> list[CapabilityDecision]:
        """Make decisions about enabling/disabling capabilities."""
        decisions = []
        
        if not self._auto_decision_enabled:
            logger.info("[LEARNING] Auto decision disabled, skipping")
            return decisions
        
        try:
            # Get current insights
            recent_insights = self._insights[-100:] if len(self._insights) > 100 else self._insights
            
            # Evaluate each capability
            for capability in self._capability_performance.keys():
                decision = self._evaluate_capability(capability, recent_insights)
                
                # Only apply decision if confidence is above threshold
                if decision.confidence >= self._decision_threshold:
                    decisions.append(decision)
                    self._decisions.append(decision)
                    
                    logger.info(
                        f"[LEARNING] Decision: {decision.decision} {capability} "
                        f"(confidence: {decision.confidence:.2f})"
                    )
            
            logger.info(f"[LEARNING] Made {len(decisions)} capability decisions")
            
        except Exception as e:
            logger.error(f"[LEARNING] Failed to make decisions: {e}")
        
        return decisions
    
    def _generate_performance_insight(
        self, 
        capability_name: str, 
        metrics: dict[str, float]
    ) -> CapabilityInsight:
        """Generate insight from performance metrics."""
        # Calculate overall performance score
        if not metrics:
            performance_score = 0.0
        else:
            # Average of all metrics (simple approach)
            performance_score = sum(metrics.values()) / len(metrics) if metrics else 0.0
        
        return CapabilityInsight(
            capability_name=capability_name,
            insight_type="performance",
            insight_value=performance_score,
            confidence=0.8,
            timestamp=now().utc_time.isoformat(),
            metadata={"raw_metrics": metrics}
        )
    
    def _generate_utility_insight(
        self, 
        capability_name: str, 
        utility_score: float
    ) -> CapabilityInsight:
        """Generate insight from utility score."""
        return CapabilityInsight(
            capability_name=capability_name,
            insight_type="utility",
            insight_value=utility_score,
            confidence=0.7,
            timestamp=now().utc_time.isoformat()
        )
    
    def _generate_dependency_insight(
        self, 
        capability_name: str, 
        dependencies: set[str]
    ) -> CapabilityInsight:
        """Generate insight from dependencies."""
        # Higher dependency count means more critical
        dependency_score = min(len(dependencies) / 10.0, 1.0)
        
        return CapabilityInsight(
            capability_name=capability_name,
            insight_type="dependency",
            insight_value=dependency_score,
            confidence=0.9,
            timestamp=now().utc_time.isoformat(),
            metadata={"dependencies": list(dependencies)}
        )
    
    def _generate_cost_insight(
        self, 
        capability_name: str, 
        cost: float
    ) -> CapabilityInsight:
        """Generate insight from cost."""
        # Lower cost is better, so invert
        cost_score = max(1.0 - (cost / 100.0), 0.0)
        
        return CapabilityInsight(
            capability_name=capability_name,
            insight_type="cost",
            insight_value=cost_score,
            confidence=0.8,
            timestamp=now().utc_time.isoformat(),
            metadata={"raw_cost": cost}
        )
    
    def _evaluate_capability(
        self, 
        capability_name: str, 
        insights: list[CapabilityInsight]
    ) -> CapabilityDecision:
        """Evaluate a capability and make a decision."""
        # Get relevant insights for this capability
        capability_insights = [i for i in insights if i.capability_name == capability_name]
        
        if not capability_insights:
            # No insights, maintain current state
            return CapabilityDecision(
                capability_name=capability_name,
                decision="maintain",
                confidence=0.5,
                reasoning="No insights available",
                timestamp=now().utc_time.isoformat()
            )
        
        # Calculate overall score
        performance_insights = [i for i in capability_insights if i.insight_type == "performance"]
        utility_insights = [i for i in capability_insights if i.insight_type == "utility"]
        cost_insights = [i for i in capability_insights if i.insight_type == "cost"]
        
        # Weighted score
        performance_score = sum(i.insight_value for i in performance_insights) / len(performance_insights) if performance_insights else 0.5
        utility_score = sum(i.insight_value for i in utility_insights) / len(utility_insights) if utility_insights else 0.5
        cost_score = sum(i.insight_value for i in cost_insights) / len(cost_insights) if cost_insights else 0.5
        
        # Overall score (performance: 40%, utility: 40%, cost: 20%)
        overall_score = (performance_score * 0.4) + (utility_score * 0.4) + (cost_score * 0.2)
        
        # Make decision based on score
        if overall_score >= 0.7:
            decision = "enable"
            reasoning = f"High performance/utility/efficiency (score: {overall_score:.2f})"
        elif overall_score <= 0.3:
            decision = "disable"
            reasoning = f"Low performance/utility/efficiency (score: {overall_score:.2f})"
        else:
            decision = "maintain"
            reasoning = f"Moderate performance/utility/efficiency (score: {overall_score:.2f})"
        
        # Confidence based on number of insights
        confidence = min(len(capability_insights) / 10.0, 1.0)
        
        return CapabilityDecision(
            capability_name=capability_name,
            decision=decision,
            confidence=confidence,
            reasoning=reasoning,
            timestamp=now().utc_time.isoformat(),
            metadata={
                "overall_score": overall_score,
                "performance_score": performance_score,
                "utility_score": utility_score,
                "cost_score": cost_score,
                "insight_count": len(capability_insights)
            }
        )
    
    def get_insights(self) -> list[CapabilityInsight]:
        """Get all recorded insights."""
        return self._insights.copy()
    
    def get_decisions(self) -> list[CapabilityDecision]:
        """Get all made decisions."""
        return self._decisions.copy()
    
    def get_capability_status(self) -> dict[str, dict[str, float]]:
        """Get current status of all capabilities."""
        return {
            "performance": self._capability_performance.copy(),
            "utility": self._capability_utility.copy(),
            "costs": self._capability_costs.copy()
        }


# Global instance
_learning_orchestrator: LearningOrchestrator | None = None


def get_learning_orchestrator() -> LearningOrchestrator:
    """Get the global learning orchestrator instance."""
    global _learning_orchestrator
    if _learning_orchestrator is None:
        _learning_orchestrator = LearningOrchestrator()
    return _learning_orchestrator


__all__ = [
    "CapabilityInsight",
    "CapabilityDecision",
    "LearningOrchestrator",
    "get_learning_orchestrator",
]