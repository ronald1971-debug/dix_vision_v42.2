"""
Bayesian Updating - Learning Engine Component
Real Bayesian learning for DIX VISION Tier-0 Production Implementation
Per Rule 4 of the DIX VISION Tier-0 Production Implementation Contract
"""

import logging
from typing import Dict, List, Set, Any, Optional, Tuple
from datetime import datetime
from dataclasses import dataclass, field
from enum import Enum
from collections import defaultdict
import math
import statistics

logger = logging.getLogger(__name__)

class BeliefType(Enum):
    """Types of beliefs in the learning system"""
    MARKET_REGIME = "market_regime"
    ASSET_CORRELATION = "asset_correlation"
    STRATEGY_PERFORMANCE = "strategy_performance"
    EXECUTION_QUALITY = "execution_quality"
    RISK_ASSESSMENT = "risk_assessment"
    PREDICTIVE_MODEL = "predictive_model"
    OPERATOR_PREFERENCE = "operator_preference"

class LearningEventType(Enum):
    """Types of learning events"""
    TRADE_EXECUTION = "trade_execution"
    PREDICTION_REALIZATION = "prediction_realization"
    REGIME_SWITCH = "regime_switch"
    RISK_EVENT = "risk_event"
    PERFORMANCE_UPDATE = "performance_update"
    FEEDBACK_SIGNAL = "feedback_signal"

@dataclass
class Belief:
    """A belief in the learning system"""
    belief_id: str
    belief_type: BeliefType
    topic: str
    prior_probability: float  # P(H)
    posterior_probability: float  # P(H|E)
    confidence: float  # Confidence in the belief
    evidence_count: int  # Number of evidence pieces
    last_updated: datetime
    evidence_history: List[Tuple[float, datetime]] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)

@dataclass
class LearningEvent:
    """An event that provides evidence for learning"""
    event_id: str
    event_type: LearningEventType
    timestamp: datetime
    outcome: float  # 1.0 for success, 0.0 for failure, or probability
    context: Dict[str, Any] = field(default_factory=dict)
    affected_beliefs: Set[str] = field(default_factory=set)

@dataclass
class BayesianUpdate:
    """Result of a Bayesian update"""
    update_id: str
    belief_id: str
    event_id: str
    prior_probability: float
    likelihood: float  # P(E|H)
    posterior_probability: float
    bayes_factor: float
    update_time: datetime
    confidence_delta: float

class BayesianUpdating:
    """
    Bayesian Updating system for real learning
    Per Rule 4 of the DIX VISION contract, learning must perform Bayesian updating
    """
    
    def __init__(self):
        self._beliefs: Dict[str, Belief] = {}
        self._events: List[LearningEvent] = []
        self._updates: List[BayesianUpdate] = []
        self._belief_index: Dict[BeliefType, Set[str]] = defaultdict(set)
        self._performance_metrics = {
            "total_updates": 0,
            "average_confidence_improvement": 0.0,
            "belief_convergence_rate": 0.0,
            "prediction_accuracy": 0.0
        }
        self._priors: Dict[str, float] = {}  # Store initial priors for tracking
        
    def create_belief(
        self,
        belief_type: BeliefType,
        topic: str,
        prior_probability: float = 0.5,
        initial_confidence: float = 0.5,
        metadata: Optional[Dict[str, Any]] = None
    ) -> Belief:
        """Create a new belief with prior probability"""
        if not (0.0 <= prior_probability <= 1.0):
            raise ValueError("Prior probability must be between 0 and 1")
        
        if not (0.0 <= initial_confidence <= 1.0):
            raise ValueError("Initial confidence must be between 0 and 1")
        
        belief_id = f"{belief_type.value}_{topic.replace(' ', '_')}_{datetime.utcnow().timestamp()}:{datetime.utcnow().nanosecond()}"
        
        belief = Belief(
            belief_id=belief_id,
            belief_type=belief_type,
            topic=topic,
            prior_probability=prior_probability,
            posterior_probability=prior_probability,
            confidence=initial_confidence,
            evidence_count=0,
            last_updated=datetime.utcnow(),
            metadata=metadata or {}
        )
        
        self._beliefs[belief_id] = belief
        self._belief_index[belief_type].add(belief_id)
        self._priors[belief_id] = prior_probability
        
        logger.info(f"Created belief: {belief_id} with prior {prior_probability:.3f}")
        return belief
    
    def record_event(
        self,
        event_type: LearningEventType,
        outcome: float,
        context: Optional[Dict[str, Any]] = None,
        affected_beliefs: Optional[Set[str]] = None
    ) -> LearningEvent:
        """Record a learning event with its outcome"""
        event_id = f"event_{event_type.value}_{datetime.utcnow().timestamp()}:{datetime.utcnow().nanosecond()}"
        
        event = LearningEvent(
            event_id=event_id,
            event_type=event_type,
            timestamp=datetime.utcnow(),
            outcome=outcome,
            context=context or {},
            affected_beliefs=affected_beliefs or set()
        )
        
        self._events.append(event)
        
        # Update affected beliefs with Bayesian updating
        if affected_beliefs:
            for belief_id in affected_beliefs:
                if belief_id in self._beliefs:
                    self._update_belief(event, belief_id)
        
        logger.info(f"Recorded event: {event_id} with outcome {outcome:.3f}")
        return event
    
    def _update_belief(self, event: LearningEvent, belief_id: str) -> Optional[BayesianUpdate]:
        """Perform Bayesian update on a belief"""
        if belief_id not in self._beliefs:
            return None
        
        belief = self._beliefs[belief_id]
        
        # Calculate likelihood P(E|H) based on belief probability and event outcome
        likelihood = self._calculate_likelihood(belief, event)
        
        # Calculate P(E) = P(E|H) * P(H) + P(E|~H) * P(~H)
        prior = belief.posterior_probability
        complement_prior = 1.0 - prior
        
        # Calculate P(E|~H) - probability of evidence if belief is false
        likelihood_complement = self._calculate_likelihood_complement(belief, event)
        
        evidence_probability = likelihood * prior + likelihood_complement * complement_prior
        
        # Avoid division by zero
        if evidence_probability == 0:
            evidence_probability = 1e-10
        
        # Apply Bayes' theorem: P(H|E) = P(E|H) * P(H) / P(E)
        posterior = (likelihood * prior) / evidence_probability
        
        # Calculate Bayes factor
        if likelihood_complement > 0:
            bayes_factor = likelihood / likelihood_complement
        else:
            bayes_factor = 100.0  # Strong evidence
        
        # Clamp posterior to valid probability range
        posterior = max(0.001, min(0.999, posterior))
        
        # Update confidence based on new evidence
        confidence_delta = self._update_confidence(belief, posterior, prior)
        
        # Create update record
        update = BayesianUpdate(
            update_id=f"update_{belief_id}_{event.event_id}",
            belief_id=belief_id,
            event_id=event.event_id,
            prior_probability=prior,
            likelihood=likelihood,
            posterior_probability=posterior,
            bayes_factor=bayes_factor,
            update_time=datetime.utcnow(),
            confidence_delta=confidence_delta
        )
        
        # Update belief
        belief.posterior_probability = posterior
        belief.last_updated = datetime.utcnow()
        belief.evidence_count += 1
        belief.evidence_history.append((event.outcome, event.timestamp))
        
        self._updates.append(update)
        self._performance_metrics["total_updates"] += 1
        
        logger.info(f"Updated belief {belief_id}: {prior:.3f} -> {posterior:.3f} (Bayes factor: {bayes_factor:.3f})")
        return update
    
    def _calculate_likelihood(self, belief: Belief, event: LearningEvent) -> float:
        """Calculate likelihood P(E|H) - probability of evidence given hypothesis"""
        # Likelihood depends on belief type and event outcome
        
        if belief.belief_type == BeliefType.STRATEGY_PERFORMANCE:
            # If belief is about strategy performance, likelihood relates to event outcome
            if belief.posterior_probability > 0.7:
                # Strong belief in success
                return 0.7 + (event.outcome * 0.3)  # Higher likelihood for good outcomes
            elif belief.posterior_probability < 0.3:
                # Strong belief in failure
                return 0.7 + ((1.0 - event.outcome) * 0.3)  # Higher likelihood for bad outcomes
            else:
                # Uncertain belief
                return 0.5  # Neutral likelihood
        
        elif belief.belief_type == BeliefType.PREDICTIVE_MODEL:
            # If belief is about prediction accuracy
            prediction_confidence = belief.metadata.get("prediction_confidence", 0.5)
            return prediction_confidence if event.outcome > 0.5 else (1.0 - prediction_confidence)
        
        elif belief.belief_type == BeliefType.MARKET_REGIME:
            # If belief is about market regime, likelihood depends on context
            regime_match = belief.metadata.get("regime_match", 0.5)
            return regime_match
        
        else:
            # Default likelihood based on outcome
            return event.outcome if belief.posterior_probability > 0.5 else (1.0 - event.outcome)
    
    def _calculate_likelihood_complement(self, belief: Belief, event: LearningEvent) -> float:
        """Calculate P(E|~H) - probability of evidence given hypothesis is false"""
        # Complement likelihood is generally the inverse of likelihood
        likelihood = self._calculate_likelihood(belief, event)
        return 1.0 - likelihood
    
    def _update_confidence(self, belief: Belief, posterior: float, prior: float) -> float:
        """Update confidence based on new evidence and convergence"""
        # Confidence increases with evidence and converges toward 1
        evidence_count = belief.evidence_count + 1
        
        # Calculate convergence (how much posterior has moved from prior)
        convergence = abs(posterior - self._priors[belief.belief_id])
        
        # Confidence formula: increases with evidence, decreases with large swings
        target_confidence = min(0.95, 0.5 + (evidence_count * 0.05) - (convergence * 0.1))
        
        confidence_delta = target_confidence - belief.confidence
        belief.confidence = max(0.1, min(0.99, target_confidence))
        
        return confidence_delta
    
    def perform_attribution(self, event_id: str) -> Dict[str, float]:
        """
        Perform attribution to understand which beliefs contributed to event outcome
        Rule 4 requires: Perform attribution
        """
        event = next((e for e in self._events if e.event_id == event_id), None)
        if not event:
            return {}
        
        attribution_scores = {}
        
        # Calculate attribution based on related beliefs and their recent updates
        related_updates = [u for u in self._updates if u.event_id == event_id]
        
        for update in related_updates:
            # Attribution score based on Bayes factor and belief confidence
            belief = self._beliefs.get(update.belief_id)
            if belief:
                # Higher Bayes factor and confidence = higher attribution
                attribution_score = update.bayes_factor * belief.confidence
                attribution_scores[update.belief_id] = attribution_score
        
        # Normalize attribution scores
        total_score = sum(attribution_scores.values())
        if total_score > 0:
            attribution_scores = {k: v / total_score for k, v in attribution_scores.items()}
        
        return attribution_scores
    
    def calculate_performance_deltas(self, belief_id: str, time_window_hours: float = 24.0) -> Dict[str, float]:
        """
        Calculate performance deltas over time window
        Rule 4 requires: Calculate performance deltas
        """
        if belief_id not in self._beliefs:
            return {}
        
        belief = self._beliefs[belief_id]
        cutoff = datetime.utcnow() - timedelta(hours=time_window_hours)
        
        # Get recent updates within time window
        recent_updates = [
            u for u in self._updates
            if u.belief_id == belief_id and u.update_time > cutoff
        ]
        
        if not recent_updates:
            return {
                "performance_delta": 0.0,
                "confidence_delta": 0.0,
                "update_count": 0,
                "average_bayes_factor": 0.0
            }
        
        # Calculate performance metrics
        performance_delta = recent_updates[-1].posterior_probability - recent_updates[0].prior_probability
        confidence_delta = sum(u.confidence_delta for u in recent_updates)
        average_bayes_factor = statistics.mean([u.bayes_factor for u in recent_updates])
        
        return {
            "performance_delta": performance_delta,
            "confidence_delta": confidence_delta,
            "update_count": len(recent_updates),
            "average_bayes_factor": average_bayes_factor
        }
    
    def update_strategy_scores(self, strategy_id: str, performance_data: Dict[str, Any]) -> None:
        """
        Update strategy scores based on performance data
        Rule 4 requires: Update strategy scores
        """
        # Create or update belief about strategy performance
        belief_key = f"strategy_{strategy_id}"
        if belief_key not in self._beliefs:
            self.create_belief(
                BeliefType.STRATEGY_PERFORMANCE,
                f"Strategy {strategy_id} Performance",
                prior_probability=0.5,
                initial_confidence=0.5,
                metadata={"strategy_id": strategy_id}
            )
        
        belief_id = list(self._beliefs.keys())[list(self._beliefs.values()).index(belief for belief in self._beliefs.values() if belief.topic == f"Strategy {strategy_id} Performance")][0]
        
        # Record learning event with performance data
        performance_score = performance_data.get("performance_score", 0.5)
        self.record_event(
            LearningEventType.PERFORMANCE_UPDATE,
            outcome=performance_score,
            context=performance_data,
            affected_beliefs={belief_id}
        )
    
    def update_execution_scores(self, execution_id: str, execution_data: Dict[str, Any]) -> None:
        """
        Update execution scores based on execution data
        Rule 4 requires: Update execution scores
        """
        # Create or update belief about execution quality
        belief_key = f"execution_{execution_id}"
        if belief_key not in self._beliefs:
            self.create_belief(
                BeliefType.EXECUTION_QUALITY,
                f"Execution {execution_id} Quality",
                prior_probability=0.7,
                initial_confidence=0.5,
                metadata={"execution_id": execution_id}
            )
        
        # Find the execution quality belief
        execution_beliefs = self._belief_index[BeliefType.EXECUTION_QUALITY]
        matching_beliefs = [bid for bid in execution_beliefs if f"Execution {execution_id}" in self._beliefs[bid].topic]
        
        if not matching_beliefs:
            return
        
        belief_id = matching_beliefs[0]
        
        # Record learning event with execution data
        execution_quality = execution_data.get("quality_score", 0.5)
        self.record_event(
            LearningEventType.TRADE_EXECUTION,
            outcome=execution_quality,
            context=execution_data,
            affected_beliefs={belief_id}
        )
    
    def update_operator_models(self, operator_id: str, behavior_data: Dict[str, Any]) -> None:
        """
        Update operator models based on behavior data
        Rule 4 requires: Update operator models
        """
        # Create or update belief about operator preferences
        belief_key = f"operator_{operator_id}"
        if belief_key not in self._beliefs:
            self.create_belief(
                BeliefType.OPERATOR_PREFERENCE,
                f"Operator {operator_id} Preferences",
                prior_probability=0.5,
                initial_confidence=0.3,
                metadata={"operator_id": operator_id}
            )
        
        # Find operator preference belief
        operator_beliefs = self._belief_index[BeliefType.OPERATOR_PREFERENCE]
        matching_beliefs = [bid for bid in operator_beliefs if f"Operator {operator_id}" in self._beliefs[bid].topic]
        
        if not matching_beliefs:
            return
        
        belief_id = matching_beliefs[0]
        
        # Record learning event with operator behavior
        preference_score = behavior_data.get("preference_score", 0.5)
        self.record_event(
            LearningEventType.FEEDBACK_SIGNAL,
            outcome=preference_score,
            context=behavior_data,
            affected_beliefs={belief_id}
        )
    
    def get_belief(self, belief_id: str) -> Optional[Belief]:
        """Get a specific belief"""
        return self._beliefs.get(belief_id)
    
    def get_beliefs_by_type(self, belief_type: BeliefType) -> List[Belief]:
        """Get all beliefs of a specific type"""
        belief_ids = self._belief_index[belief_type]
        return [self._beliefs[bid] for bid in belief_ids if bid in self._beliefs]
    
    def get_learning_summary(self) -> Dict[str, Any]:
        """Get summary of Bayesian learning system"""
        total_beliefs = len(self._beliefs)
        high_confidence_beliefs = sum(1 for b in self._beliefs.values() if b.confidence > 0.8)
        convergent_beliefs = sum(
            1 for b in self._beliefs.values()
            if abs(b.posterior_probability - b.prior_probability) < 0.05
        )
        
        # Calculate average confidence improvement
        confidence_improvements = []
        for belief in self._beliefs.values():
            if belief.evidence_count > 0:
                improvement = belief.confidence - 0.5  # Starting from 0.5
                confidence_improvements.append(improvement)
        
        avg_confidence_improvement = statistics.mean(confidence_improvements) if confidence_improvements else 0.0
        self._performance_metrics["average_confidence_improvement"] = avg_confidence_improvement
        self._performance_metrics["belief_convergence_rate"] = convergent_beliefs / total_beliefs if total_beliefs > 0 else 0.0
        
        return {
            "total_beliefs": total_beliefs,
            "high_confidence_beliefs": high_confidence_beliefs,
            "convergent_beliefs": convergent_beliefs,
            "total_events": len(self._events),
            "total_updates": len(self._updates),
            "belief_types_distribution": {
                belief_type.value: len(self._belief_index[belief_type])
                for belief_type in BeliefType
            },
            "performance_metrics": self._performance_metrics.copy(),
            "timestamp": datetime.utcnow().isoformat()
        }
    
    def cleanup_old_events(self, older_than_days: int = 30) -> int:
        """Clean up old learning events and updates"""
        cutoff = datetime.utcnow() - timedelta(days=older_than_days)
        
        old_events_count = len(self._events)
        self._events = [e for e in self._events if e.timestamp > cutoff]
        
        old_updates_count = len(self._updates)
        self._updates = [u for u in self._updates if u.update_time > cutoff]
        
        removed_events = old_events_count - len(self._events)
        removed_updates = old_updates_count - len(self._updates)
        
        logger.info(f"Cleaned up {removed_events} old events and {removed_updates} old updates")
        return removed_events + removed_updates