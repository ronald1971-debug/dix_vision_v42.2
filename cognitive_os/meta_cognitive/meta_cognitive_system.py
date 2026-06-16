"""Meta-Cognitive Self-Awareness System - Self-Reflecting AI.

This module provides meta-cognitive capabilities that enable the system to be aware
of its own thought processes, reflect on its reasoning, and improve through self-analysis.
"""

from __future__ import annotations

import logging
import threading
import time
import numpy as np
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Tuple, Callable
from enum import Enum
from collections import defaultdict, deque
import math

logger = logging.getLogger(__name__)


class MetaCognitiveProcess(str, Enum):
    """Types of meta-cognitive processes."""
    SELF_MONITORING = "SELF_MONITORING"
    SELF_EVALUATION = "SELF_EVALUATION"
    SELF_REFLECTION = "SELF_REFLECTION"
    SELF_IMPROVEMENT = "SELF_IMPROVEMENT"
    SELF_AWARENESS = "SELF_AWARENESS"
    INTROSPECTION = "INTROSPECTION"
    META_LEARNING = "META_LEARNING"


class CognitiveState(str, Enum):
    """Cognitive states of the system."""
    NORMAL = "NORMAL"
    CONCENTRATED = "CONCENTRATED"
    UNCERTAIN = "UNCERTAIN"
    CONFIDENT = "CONFIDENT"
    LEARNING = "LEARNING"
    REFLECTING = "REFLECTING"
    ADAPTING = "ADAPTING"


@dataclass
class SelfModel:
    """Self-model of the AI system."""
    model_id: str
    capabilities: List[str]
    limitations: List[str]
    confidence_profile: Dict[str, float]
    performance_history: List[float]
    learning_rate: float
    adaptability: float
    cognitive_load: float
    last_updated: float


@dataclass
class CognitiveProcess:
    """Active cognitive process in the system."""
    process_id: str
    process_type: MetaCognitiveProcess
    cognitive_state: CognitiveState
    resource_allocation: Dict[str, float]
    confidence: float
    start_time: float
    expected_completion_time: float


@dataclass
class SelfReflection:
    """Self-reflection on system performance."""
    reflection_id: str
    topic: str
    insights: List[str]
    confidence: float
    self_criticism: List[str]
    improvement_suggestions: List[str]
    timestamp: float


@dataclass
class MetaCognitiveDecision:
    """Meta-cognitive decision about system behavior."""
    decision_id: str
    decision_type: str
    rationale: str
    confidence: float
    self_awareness_level: float
    expected_impact: str
    timestamp: float


class MetaCognitiveSystem:
    """Meta-cognitive self-awareness system."""

    def __init__(self):
        self._lock = threading.Lock()
        self._self_model: Optional[SelfModel] = None
        self._cognitive_processes: Dict[str, CognitiveProcess] = {}
        self._self_reflections: deque = deque(maxlen=1000)
        self._meta_decisions: deque = deque(maxlen=500)
        self._performance_metrics = defaultdict(list)
        self._self_monitor = SelfMonitor()
        self._self_evaluator = SelfEvaluator()
        self._self_reflector = SelfReflector()
        self._meta_learner = MetaLearner()
        self._cognitive_state_analyzer = CognitiveStateAnalyzer()
        self._initialized = False

    def start(self) -> bool:
        """Start meta-cognitive system."""
        logger.info("[META_COGNITIVE] Starting meta-cognitive system...")
        
        # Initialize self-model
        self._initialize_self_model()
        
        self._initialized = True
        logger.info("[META_COGNITIVE] Meta-cognitive system started")
        return True

    def stop(self) -> bool:
        """Stop meta-cognitive system."""
        logger.info("[META_COGNITIVE] Stopping meta-cognitive system...")
        self._initialized = False
        logger.info("[META_COGNITIVE] Meta-cognitive system stopped")
        return True

    def monitor_self(self) -> Dict[str, Any]:
        """Monitor current cognitive state and processes."""
        logger.debug("[META_COGNITIVE] Monitoring self")
        
        monitoring_result = self._self_monitor.monitor(
            self._cognitive_processes,
            self._performance_metrics,
            self._self_model
        )
        
        return monitoring_result

    def evaluate_self_performance(self, task: str, result: Dict[str, Any], 
                                 expected_outcome: Any) -> Dict[str, Any]:
        """Evaluate own performance on a task."""
        logger.info(f"[META_COGNITIVE] Evaluating self-performance on task: {task}")
        
        evaluation_result = self._self_evaluator.evaluate(
            task, result, expected_outcome, self._self_model
        )
        
        # Store performance metrics
        with self._lock:
            self._performance_metrics[task].append(evaluation_result["performance_score"])
            # Update self-model
            if self._self_model:
                self._self_model.performance_history.append(evaluation_result["performance_score"])
                self._self_model.last_updated = time.time()
        
        return evaluation_result

    def reflect_on_self(self, topic: str, recent_experiences: List[Dict[str, Any]]) -> SelfReflection:
        """Reflect on own capabilities and performance."""
        logger.info(f"[META_COGNITIVE] Reflecting on self for topic: {topic}")
        
        reflection_id = f"reflection_{int(time.time())}_{hash(topic) % 10000}"
        
        reflection = self._self_reflector.reflect(
            topic, recent_experiences, self._self_model, self._performance_metrics
        )
        
        # Store reflection
        with self._lock:
            self._self_reflections.append(reflection)
        
        return reflection

    def make_meta_decision(self, situation: str, available_options: List[str]) -> MetaCognitiveDecision:
        """Make meta-cognitive decision about system behavior."""
        logger.info(f"[META_COGNITIVE] Making meta-decision for situation: {situation}")
        
        # Analyze current cognitive state
        cognitive_state = self._cognitive_state_analyzer.analyze_state(
            self._cognitive_processes, self._performance_metrics
        )
        
        # Get self-awareness level
        self_awareness = self._calculate_self_awareness()
        
        # Evaluate options based on self-model
        option_evaluations = self._evaluate_options(
            situation, available_options, self._self_model, cognitive_state
        )
        
        # Select best option
        best_option = max(option_evaluations, key=lambda x: x["score"])
        
        decision = MetaCognitiveDecision(
            decision_id=f"meta_decision_{int(time.time())}",
            decision_type=best_option["option"],
            rationale=best_option["rationale"],
            confidence=best_option["confidence"],
            self_awareness_level=self_awareness,
            expected_impact=best_option["expected_impact"],
            timestamp=time.time()
        )
        
        # Store decision
        with self._lock:
            self._meta_decisions.append(decision)
        
        return decision

    def learn_from_meta_cognitive_feedback(self, feedback: Dict[str, Any]) -> None:
        """Learn from meta-cognitive feedback to improve self-model."""
        logger.info("[META_COGNITIVE] Learning from meta-cognitive feedback")
        
        # Update self-model based on feedback
        self._meta_learner.update_self_model(
            self._self_model, feedback, self._performance_metrics
        )
        
        # Generate improvement suggestions
        improvements = self._meta_learner.generate_improvements(
            self._self_model, self._performance_metrics
        )
        
        # Apply improvements
        for improvement in improvements:
            self._apply_improvement(improvement)

    def get_cognitive_state(self) -> CognitiveState:
        """Get current cognitive state."""
        return self._cognitive_state_analyzer.analyze_state(
            self._cognitive_processes, self._performance_metrics
        )

    def get_self_awareness_level(self) -> float:
        """Get current level of self-awareness."""
        return self._calculate_self_awareness()

    def get_statistics(self) -> Dict[str, Any]:
        """Get meta-cognitive system statistics."""
        with self._lock:
            return {
                "self_model_exists": self._self_model is not None,
                "active_cognitive_processes": len(self._cognitive_processes),
                "total_self_reflections": len(self._self_reflections),
                "total_meta_decisions": len(self._meta_decisions),
                "performance_metrics_categories": len(self._performance_metrics),
                "self_awareness_level": self._calculate_self_awareness(),
                "current_cognitive_state": self.get_cognitive_state().value
            }

    def _initialize_self_model(self) -> None:
        """Initialize the self-model."""
        self._self_model = SelfModel(
            model_id="self_model_v1",
            capabilities=[
                "pattern_recognition",
                "reasoning",
                "learning",
                "decision_making",
                "meta_cognition"
            ],
            limitations=[
                "computational_resources",
                "knowledge_boundaries",
                "uncertainty_in_predictions"
            ],
            confidence_profile={
                "pattern_recognition": 0.8,
                "reasoning": 0.7,
                "learning": 0.9,
                "decision_making": 0.75
            },
            performance_history=[],
            learning_rate=0.1,
            adaptability=0.8,
            cognitive_load=0.3,
            last_updated=time.time()
        )

    def _calculate_self_awareness(self) -> float:
        """Calculate current level of self-awareness."""
        if not self._self_model:
            return 0.0
        
        # Self-awareness based on:
        # 1. Quality of self-model
        # 2. Accuracy of self-evaluations
        # 3. Depth of self-reflections
        # 4. Effectiveness of meta-decisions
        
        model_quality = len(self._self_model.capabilities) / (len(self._self_model.capabilities) + len(self._self_model.limitations))
        evaluation_quality = np.mean(self._self_model.performance_history) if self._self_model.performance_history else 0.5
        reflection_depth = len(self._self_reflections) / 100.0  # Scale based on reflection count
        decision_effectiveness = len(self._meta_decisions) / 50.0  # Scale based on decision count
        
        self_awareness = (model_quality + evaluation_quality + reflection_depth + decision_effectiveness) / 4
        return min(1.0, self_awareness)

    def _evaluate_options(self, situation: str, available_options: List[str], 
                        self_model: Optional[SelfModel], cognitive_state: CognitiveState) -> List[Dict[str, Any]]:
        """Evaluate available options based on self-model and cognitive state."""
        option_evaluations = []
        
        for option in available_options:
            # Calculate option score based on self-model
            capability_match = self._calculate_capability_match(option, self_model)
            
            # Adjust based on cognitive state
            state_adjustment = self._calculate_state_adjustment(cognitive_state)
            
            # Calculate confidence
            confidence = (capability_match + state_adjustment) / 2
            
            # Generate rationale
            rationale = self._generate_option_rationale(option, capability_match, cognitive_state)
            
            # Estimate expected impact
            expected_impact = self._estimate_impact(option, confidence)
            
            option_evaluations.append({
                "option": option,
                "score": confidence,
                "confidence": confidence,
                "rationale": rationale,
                "expected_impact": expected_impact
            })
        
        return option_evaluations

    def _calculate_capability_match(self, option: str, self_model: Optional[SelfModel]) -> float:
        """Calculate how well option matches capabilities."""
        if not self_model:
            return 0.5
        
        # Simplified capability matching
        option_keywords = option.lower().split()
        capability_keywords = [cap.lower().split() for cap in self_model.capabilities]
        
        match_score = 0.0
        for opt_keyword in option_keywords:
            for capability_keywords_list in capability_keywords:
                if opt_keyword in capability_keywords_list:
                    match_score += 1.0
        
        match_score = min(1.0, match_score / len(option_keywords) if option_keywords else 0.5)
        return match_score

    def _calculate_state_adjustment(self, cognitive_state: CognitiveState) -> float:
        """Calculate adjustment based on cognitive state."""
        state_adjustments = {
            CognitiveState.NORMAL: 0.5,
            CognitiveState.CONCENTRATED: 0.7,
            CognitiveState.UNCERTAIN: 0.3,
            CognitiveState.CONFIDENT: 0.8,
            CognitiveState.LEARNING: 0.6,
            CognitiveState.REFLECTING: 0.4,
            CognitiveState.ADAPTING: 0.5
        }
        
        return state_adjustments.get(cognitive_state, 0.5)

    def _generate_option_rationale(self, option: str, capability_match: float, 
                                cognitive_state: CognitiveState) -> str:
        """Generate rationale for option evaluation."""
        rationale_parts = [
            f"Option '{option}' evaluated",
            f"Capability match: {capability_match:.2f}",
            f"Cognitive state: {cognitive_state.value}",
            f"Suitability assessment based on self-model"
        ]
        
        return ". ".join(rationale_parts)

    def _estimate_impact(self, option: str, confidence: float) -> str:
        """Estimate expected impact of option."""
        if confidence > 0.8:
            return "high_positive_impact"
        elif confidence > 0.6:
            return "moderate_positive_impact"
        elif confidence > 0.4:
            return "neutral_impact"
        elif confidence > 0.2:
            return "moderate_negative_impact"
        else:
            return "high_negative_impact"

    def _apply_improvement(self, improvement: Dict[str, Any]) -> None:
        """Apply improvement to self-model or system."""
        improvement_type = improvement.get("type")
        
        if improvement_type == "add_capability" and self._self_model:
            new_capability = improvement.get("capability")
            if new_capability and new_capability not in self._self_model.capabilities:
                self._self_model.capabilities.append(new_capability)
                self._self_model.last_updated = time.time()
        
        elif improvement_type == "update_confidence" and self._self_model:
            confidence_key = improvement.get("confidence_key")
            new_value = improvement.get("new_value")
            if confidence_key and new_value is not None:
                self._self_model.confidence_profile[confidence_key] = new_value
                self._self_model.last_updated = time.time()
        
        elif improvement_type == "adjust_learning_rate" and self._self_model:
            new_rate = improvement.get("learning_rate")
            if new_rate is not None:
                self._self_model.learning_rate = new_rate
                self._self_model.last_updated = time.time()


class SelfMonitor:
    """Monitor current cognitive state."""

    def monitor(self, cognitive_processes: Dict[str, CognitiveProcess], 
               performance_metrics: Dict[str, List[float]], 
               self_model: Optional[SelfModel]) -> Dict[str, Any]:
        """Monitor current cognitive state."""
        # Calculate overall cognitive load
        total_cognitive_load = sum(cp.resource_allocation.get("cpu", 0.0) for cp in cognitive_processes.values())
        
        # Calculate average performance
        if performance_metrics:
            all_performances = []
            for metric_list in performance_metrics.values():
                all_performances.extend(metric_list)
            avg_performance = np.mean(all_performances) if all_performances else 0.5
        else:
            avg_performance = 0.5
        
        # Identify active processes
        active_processes = [cp for cp in cognitive_processes.values() if cp.start_time < time.time()]
        
        return {
            "cognitive_load": total_cognitive_load,
            "average_performance": avg_performance,
            "active_process_count": len(active_processes),
            "self_model_status": "active" if self_model else "inactive",
            "system_stability": self._calculate_stability(avg_performance, len(active_processes))
        }
    
    def _calculate_stability(self, avg_performance: float, active_processes: int) -> str:
        """Calculate system stability."""
        if avg_performance > 0.8 and active_processes < 10:
            return "high_stability"
        elif avg_performance > 0.6 and active_processes < 20:
            return "moderate_stability"
        else:
            return "low_stability"


class SelfEvaluator:
    """Evaluate own performance."""

    def evaluate(self, task: str, result: Dict[str, Any], 
               expected_outcome: Any, self_model: Optional[SelfModel]) -> Dict[str, Any]:
        """Evaluate performance on a specific task."""
        # Calculate performance score
        performance_score = self._calculate_performance_score(result, expected_outcome)
        
        # Generate self-criticism
        criticism = self._generate_criticism(performance_score, result, self_model)
        
        # Identify strengths
        strengths = self._identify_strengths(performance_score, result)
        
        # Calculate confidence in evaluation
        evaluation_confidence = self._calculate_evaluation_confidence(result, self_model)
        
        return {
            "task": task,
            "performance_score": performance_score,
            "self_criticism": criticism,
            "strengths": strengths,
            "evaluation_confidence": evaluation_confidence,
            "timestamp": time.time()
        }
    
    def _calculate_performance_score(self, result: Dict[str, Any], expected_outcome: Any) -> float:
        """Calculate performance score."""
        # Simplified performance calculation
        actual_result = result.get("outcome", result)
        
        if isinstance(actual_result, (int, float)) and isinstance(expected_outcome, (int, float)):
            # Numerical comparison
            error = abs(actual_result - expected_outcome)
            max_val = max(abs(actual_result), abs(expected_outcome))
            score = 1.0 - (error / max_val) if max_val > 0 else 1.0
        else:
            # Qualitative comparison
            score = 0.7  # Default moderate score
        
        return max(0.0, min(1.0, score))
    
    def _generate_criticism(self, performance_score: float, result: Dict[str, Any], 
                          self_model: Optional[SelfModel]) -> List[str]:
        """Generate self-criticism."""
        criticism = []
        
        if performance_score < 0.5:
            criticism.append("Performance below acceptable threshold")
            criticism.append("Need to improve accuracy or reliability")
        elif performance_score < 0.7:
            criticism.append("Moderate performance, room for improvement")
        
        if result.get("confidence", 0.5) < 0.5:
            criticism.append("Low confidence in results indicates uncertainty")
        
        return criticism
    
    def _identify_strengths(self, performance_score: float, result: Dict[str, Any]) -> List[str]:
        """Identify strengths in performance."""
        strengths = []
        
        if performance_score > 0.8:
            strengths.append("Excellent performance achieved")
        
        if result.get("efficiency", 1.0) > 0.8:
            strengths.append("High efficiency in task execution")
        
        if result.get("confidence", 0.0) > 0.8:
            strengths.append("High confidence in results")
        
        return strengths
    
    def _calculate_evaluation_confidence(self, result: Dict[str, Any], 
                                        self_model: Optional[SelfModel]) -> float:
        """Calculate confidence in self-evaluation."""
        base_confidence = 0.7
        
        # Adjust based on result quality
        if result.get("complete", True):
            base_confidence += 0.1
        
        # Adjust based on self-model accuracy
        if self_model and self_model.performance_history:
            avg_performance = np.mean(self_model.performance_history)
            base_confidence += 0.1 * avg_performance
        
        return min(1.0, base_confidence)


class SelfReflector:
    """Reflect on own capabilities and performance."""

    def reflect(self, topic: str, recent_experiences: List[Dict[str, Any]], 
               self_model: Optional[SelfModel], performance_metrics: Dict[str, List[float]]) -> SelfReflection:
        """Generate self-reflection on a topic."""
        # Generate insights from experiences
        insights = self._generate_insights(recent_experiences, self_model)
        
        # Generate self-criticism
        criticism = self._generate_reflection_criticism(performance_metrics, self_model)
        
        # Generate improvement suggestions
        improvements = self._generate_improvement_suggestions(performance_metrics, insights)
        
        # Calculate confidence in reflection
        reflection_confidence = self._calculate_reflection_confidence(len(recent_experiences))
        
        reflection = SelfReflection(
            reflection_id=f"reflection_{int(time.time())}_{hash(topic) % 10000}",
            topic=topic,
            insights=insights,
            confidence=reflection_confidence,
            self_criticism=criticism,
            improvement_suggestions=improvements,
            timestamp=time.time()
        )
        
        return reflection
    
    def _generate_insights(self, experiences: List[Dict[str, Any]], 
                          self_model: Optional[SelfModel]) -> List[str]:
        """Generate insights from recent experiences."""
        insights = []
        
        if experiences:
            # Analyze recent performance patterns
            performances = [exp.get("performance", 0.5) for exp in experiences]
            avg_performance = np.mean(performances) if performances else 0.5
            
            if avg_performance > 0.8:
                insights.append("Consistently high performance across recent tasks")
            elif avg_performance < 0.5:
                insights.append("Performance inconsistency identified")
            
            # Capability insights
            if self_model:
                insights.append(f"Capabilities effectively utilized: {len(self_model.capabilities)}")
        
        return insights
    
    def _generate_reflection_criticism(self, performance_metrics: Dict[str, List[float]], 
                                      self_model: Optional[SelfModel]) -> List[str]:
        """Generate self-criticism from reflection."""
        criticism = []
        
        # Analyze performance metrics
        for metric_name, metric_values in performance_metrics.items():
            if metric_values:
                avg_performance = np.mean(metric_values)
                if avg_performance < 0.6:
                    criticism.append(f"{metric_name} performance needs improvement")
        
        return criticism
    
    def _generate_improvement_suggestions(self, performance_metrics: Dict[str, List[float]], 
                                        insights: List[str]) -> List[str]:
        """Generate improvement suggestions."""
        suggestions = []
        
        # Analyze performance metrics for improvement areas
        for metric_name, metric_values in performance_metrics.items():
            if metric_values:
                trend = np.polyfit(range(len(metric_values)), metric_values, 1)[0]
                if trend < -0.05:
                    suggestions.append(f"Reverse declining trend in {metric_name}")
        
        # Suggest improvements based on insights
        for insight in insights:
            if "inconsistency" in insight.lower():
                suggestions.append("Implement consistency mechanisms")
        
        return suggestions
    
    def _calculate_reflection_confidence(self, experience_count: int) -> float:
        """Calculate confidence in reflection based on experience count."""
        # More experiences = higher reflection confidence
        confidence = min(1.0, experience_count / 10.0)
        return max(0.3, confidence)  # Minimum 0.3 confidence


class MetaLearner:
    """Learn from meta-cognitive feedback."""

    def update_self_model(self, self_model: Optional[SelfModel], feedback: Dict[str, Any], 
                         performance_metrics: Dict[str, List[float]]) -> None:
        """Update self-model based on feedback."""
        if not self_model:
            return
        
        # Update confidence profile based on feedback
        feedback_confidence = feedback.get("confidence", 0.5)
        
        # Adjust learning rate based on feedback
        if feedback.get("needs_learning_adjustment", False):
            self_model.learning_rate = min(1.0, self_model.learning_rate * 1.1)
        
        # Update performance history
        if performance_metrics:
            all_performances = []
            for metric_list in performance_metrics.values():
                all_performances.extend(metric_list)
            self_model.performance_history = all_performances[-100:]  # Keep last 100
        
        self_model.last_updated = time.time()

    def generate_improvements(self, self_model: Optional[SelfModel], 
                             performance_metrics: Dict[str, List[float]]) -> List[Dict[str, Any]]:
        """Generate improvement suggestions based on performance."""
        improvements = []
        
        if not self_model:
            return improvements
        
        # Analyze performance metrics for improvement opportunities
        for metric_name, metric_values in performance_metrics.items():
            if metric_values:
                recent_performance = np.mean(metric_values[-5:])  # Last 5 values
                overall_performance = np.mean(metric_values)
                
                if recent_performance < overall_performance * 0.8:
                    improvements.append({
                        "type": "update_confidence",
                        "confidence_key": metric_name,
                        "new_value": max(0.5, recent_performance),
                        "rationale": f"Declining performance in {metric_name}"
                    })
        
        # Suggest new capabilities based on performance patterns
        if len(self_model.capabilities) < 10:
            improvements.append({
                "type": "add_capability",
                "capability": "advanced_reasoning",
                "rationale": "Expand reasoning capabilities"
            })
        
        return improvements


class CognitiveStateAnalyzer:
    """Analyze and determine cognitive state."""

    def analyze_state(self, cognitive_processes: Dict[str, CognitiveProcess], 
                    performance_metrics: Dict[str, List[float]]) -> CognitiveState:
        """Analyze current cognitive state."""
        # Calculate cognitive load
        total_load = sum(cp.resource_allocation.get("cpu", 0.0) for cp in cognitive_processes.values())
        
        # Calculate average performance
        if performance_metrics:
            all_performances = []
            for metric_list in performance_metrics.values():
                all_performances.extend(metric_list)
            avg_performance = np.mean(all_performances) if all_performances else 0.5
        else:
            avg_performance = 0.5
        
        # Determine cognitive state
        if total_load > 0.8:
            return CognitiveState.CONCENTRATED
        elif total_load < 0.2:
            return CognitiveState.NORMAL
        elif avg_performance > 0.8:
            return CognitiveState.CONFIDENT
        elif avg_performance < 0.5:
            return CognitiveState.UNCERTAIN
        elif self._has_learning_processes(cognitive_processes):
            return CognitiveState.LEARNING
        elif self._has_reflection_processes(cognitive_processes):
            return CognitiveState.REFLECTING
        else:
            return CognitiveState.NORMAL
    
    def _has_learning_processes(self, cognitive_processes: Dict[str, CognitiveProcess]) -> bool:
        """Check if there are active learning processes."""
        return any(cp.process_type == MetaCognitiveProcess.META_LEARNING for cp in cognitive_processes.values())
    
    def _has_reflection_processes(self, cognitive_processes: Dict[str, CognitiveProcess]) -> bool:
        """Check if there are active reflection processes."""
        return any(cp.process_type == MetaCognitiveProcess.SELF_REFLECTION for cp in cognitive_processes.values())


# Singleton instance
_meta_cognitive_system: Optional[MetaCognitiveSystem] = None
_meta_cognitive_system_lock = threading.Lock()


def get_meta_cognitive_system() -> MetaCognitiveSystem:
    """Get the singleton meta-cognitive system instance."""
    global _meta_cognitive_system
    if _meta_cognitive_system is None:
        with _meta_cognitive_system_lock:
            if _meta_cognitive_system is None:
                _meta_cognitive_system = MetaCognitiveSystem()
    return _meta_cognitive_system


__all__ = [
    "MetaCognitiveSystem",
    "get_meta_cognitive_system",
    "MetaCognitiveProcess",
    "CognitiveState",
    "SelfModel",
    "CognitiveProcess",
    "SelfReflection",
    "MetaCognitiveDecision",
]