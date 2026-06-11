"""AGENT-COORD-01 — Advanced multi-agent coordination and consensus.

Enhances INDIRA's agent coordination with dynamic agent selection,
weighted voting mechanisms, conflict resolution, and performance tracking.

Pure computation. No clocks, no I/O. INV-15 deterministic.
B1: No imports from execution_engine/governance_engine/learning_engine/evolution_engine.
"""

from __future__ import annotations

import math
from dataclasses import dataclass
from typing import Any
from collections import deque
from enum import Enum


class CoordinationProtocol(Enum):
    """Types of agent coordination protocols."""
    CONSENSUS = "consensus"  # Full agreement required
    MAJORITY = "majority"  # Simple majority vote
    WEIGHTED_MAJORITY = "weighted_majority"  # Majority with expert weighting
    DELEGATED = "delegated"  # Leadership-based decision
    LIQUID_DEMOCRACY = "liquid_democracy"  # Transferrable voting rights
    SUPERMAJORITY = "supermajority"  # 2/3 majority required


class AgentRole(Enum):
    """Specialized roles agents can take in coordination."""
    FACILITATOR = "facilitator"  # Manages coordination process
    EXPERT = "expert"  # Domain expert with higher weight
    DEVILS_ADVOCATE = "devils_advocate"  # Challenges consensus
    SYNTHESIZER = "synthesizer"  # Combines different viewpoints
    VALIDATOR = "validator"  # Validates decisions for quality
    OBSERVER = "observer"  # Non-voting participant


@dataclass(frozen=True, slots=True)
class AgentProfile:
    """Performance profile for an agent."""
    agent_id: str
    accuracy: float  # Historical accuracy (0.0 to 1.0)
    consistency: float  # Consistency of performance (0.0 to 1.0)
    expertise_areas: tuple[str, ...]  # Areas where agent excels
    confidence_score: float  # Calibration of confidence estimates
    reputation_score: float  # Overall reputation among peers
    participation_rate: float  # How often agent participates constructively
    last_updated_ns: int


@dataclass(frozen=True, slots=True)
class AgentVote:
    """Vote from an agent on a decision."""
    agent_id: str
    decision: str  # The decision being voted on
    confidence: float  # Agent's confidence in this decision
    rationale: str  # Reasoning for the vote
    weight: float  # Voting weight (based on role/performance)
    timestamp_ns: int


@dataclass(frozen=True, slots=True)
class CoordinationResult:
    """Result of multi-agent coordination."""
    coordination_id: str
    protocol: CoordinationProtocol
    final_decision: str
    consensus_level: float  # 0.0 to 1.0, how much agents agree
    participating_agents: tuple[str, ...]
    dissenting_agents: tuple[str, ...]
    voting_breakdown: dict[str, int]  # decision -> vote count
    required_votes_for_decision: int
    confidence_in_result: float
    reasoning_summary: str
    conflict_resolution_used: str | None
    timestamp_ns: int


@dataclass(frozen=True, slots=True)
class AgentConflict:
    """Detected conflict between agents."""
    conflict_id: str
    conflict_type: str  # "disagreement", "contradiction", "priority_conflict"
    agents_involved: tuple[str, ...]
    disagreement_intensity: float  # 0.0 to 1.0
    subject: str  # What the conflict is about
    potential_resolutions: tuple[str, ...]
    timestamp_ns: int


class AgentPerformanceTracker:
    """Tracks agent performance for coordination optimization.
    
    Monitors accuracy, consistency, and participation to enable
    dynamic agent selection and weighted voting.
    """
    
    def __init__(self, performance_window: int = 100) -> None:
        self._performance_window = performance_window
        
        self._agent_profiles: dict[str, AgentProfile] = {}
        self._decision_history: deque[dict[str, Any]] = deque(maxlen=performance_window)
        self._conflict_history: deque[AgentConflict] = deque(maxlen=50)
        
    def record_agent_decision(
        self,
        agent_id: str,
        decision: str,
        actual_outcome: str,
        confidence: float,
        timestamp_ns: int
    ) -> None:
        """Record an agent's decision and its outcome.
        
        Args:
            agent_id: Agent identifier
            decision: Decision made by agent
            actual_outcome: What actually happened
            confidence: Agent's confidence at decision time
            timestamp_ns: Timestamp of decision
        """
        correct = decision == actual_outcome
        
        self._decision_history.append({
            "agent_id": agent_id,
            "decision": decision,
            "actual_outcome": actual_outcome,
            "correct": correct,
            "confidence": confidence,
            "timestamp_ns": timestamp_ns
        })
        
        # Update agent profile
        if agent_id not in self._agent_profiles:
            self._agent_profiles[agent_id] = AgentProfile(
                agent_id=agent_id,
                accuracy=0.5,
                consistency=0.5,
                expertise_areas=(),
                confidence_score=0.5,
                reputation_score=0.5,
                participation_rate=0.5,
                last_updated_ns=timestamp_ns
            )
        
        self._update_agent_profile(agent_id, correct, confidence, timestamp_ns)
    
    def _update_agent_profile(
        self,
        agent_id: str,
        correct: bool,
        confidence: float,
        timestamp_ns: int
    ) -> None:
        """Update an agent's performance profile."""
        profile = self._agent_profiles[agent_id]
        
        # Get recent history for this agent
        agent_decisions = [
            d for d in self._decision_history
            if d["agent_id"] == agent_id
        ][-self._performance_window:]
        
        if not agent_decisions:
            return
        
        # Calculate accuracy
        accuracy = sum(d["correct"] for d in agent_decisions) / len(agent_decisions)
        
        # Calculate consistency (calibration of confidence)
        confidence_errors = []
        for d in agent_decisions:
            expected_confidence = 1.0 if d["correct"] else 0.0
            confidence_errors.append(abs(d["confidence"] - expected_confidence))
        
        consistency = 1.0 - (sum(confidence_errors) / len(confidence_errors) if confidence_errors else 0.0)
        
        # Calculate confidence score (how well confidence predicts correctness)
        correct_confidences = [d["confidence"] for d in agent_decisions if d["correct"]]
        incorrect_confidences = [d["confidence"] for d in agent_decisions if not d["correct"]]
        
        avg_correct_conf = sum(correct_confidences) / len(correct_confidences) if correct_confidences else 0.0
        avg_incorrect_conf = sum(incorrect_confidences) / len(incorrect_confidences) if incorrect_confidences else 0.0
        
        confidence_score = avg_correct_conf - avg_incorrect_conf if (avg_correct_conf + avg_incorrect_conf) > 0 else 0.5
        
        # Update profile
        updated_profile = AgentProfile(
            agent_id=agent_id,
            accuracy=accuracy,
            consistency=consistency,
            expertise_areas=profile.expertise_areas,
            confidence_score=max(0.0, min(1.0, confidence_score + 0.5)),  # Normalize to [0,1]
            reputation_score=profile.reputation_score,  # Would update based on peer feedback
            participation_rate=profile.participation_rate,
            last_updated_ns=timestamp_ns
        )
        
        self._agent_profiles[agent_id] = updated_profile
    
    def assign_agent_role(self, agent_id: str, role: AgentRole, expertise_areas: tuple[str, ...]) -> None:
        """Assign a specialized role to an agent."""
        if agent_id not in self._agent_profiles:
            self._agent_profiles[agent_id] = AgentProfile(
                agent_id=agent_id,
                accuracy=0.5,
                consistency=0.5,
                expertise_areas=expertise_areas,
                confidence_score=0.5,
                reputation_score=0.5,
                participation_rate=0.5,
                last_updated_ns=0
            )
        else:
            profile = self._agent_profiles[agent_id]
            self._agent_profiles[agent_id] = AgentProfile(
                agent_id=agent_id,
                accuracy=profile.accuracy,
                consistency=profile.consistency,
                expertise_areas=expertise_areas,
                confidence_score=profile.confidence_score,
                reputation_score=profile.reputation_score,
                participation_rate=profile.participation_rate,
                last_updated_ns=profile.last_updated_ns
            )
    
    def get_agent_profile(self, agent_id: str) -> AgentProfile | None:
        """Get performance profile for an agent."""
        return self._agent_profiles.get(agent_id)
    
    def select_expert_agents(
        self,
        domain: str,
        num_agents: int = 3
    ) -> tuple[str, ...]:
        """Select the top expert agents for a domain.
        
        Args:
            domain: Domain of expertise needed
            num_agents: Number of agents to select
            
        Returns:
            Tuple of selected agent IDs
        """
        candidates = []
        
        for agent_id, profile in self._agent_profiles.items():
            if domain in profile.expertise_areas:
                # Score based on accuracy, consistency, and reputation
                score = (
                    profile.accuracy * 0.4 +
                    profile.consistency * 0.3 +
                    profile.reputation_score * 0.3
                )
                candidates.append((agent_id, score))
        
        # Sort by score and select top agents
        candidates.sort(key=lambda x: x[1], reverse=True)
        return tuple(agent_id for agent_id, _ in candidates[:num_agents])


class AdvancedCoordinationEngine:
    """Advanced multi-agent coordination engine.
    
    Implements various coordination protocols, weighted voting,
    and conflict resolution for optimal agent collaboration.
    """
    
    def __init__(
        self,
        default_protocol: CoordinationProtocol = CoordinationProtocol.WEIGHTED_MAJORITY,
        performance_tracker: AgentPerformanceTracker | None = None
    ) -> None:
        self._default_protocol = default_protocol
        self._performance_tracker = performance_tracker or AgentPerformanceTracker()
        
        self._coordination_history: deque[CoordinationResult] = deque(maxlen=50)
        self._active_roles: dict[str, AgentRole] = {}  # agent_id -> role
        
    def coordinate_decision(
        self,
        topic: str,
        available_agents: tuple[str, ...],
        agent_votes: tuple[AgentVote, ...],
        protocol: CoordinationProtocol | None = None,
        timestamp_ns: int = 0
    ) -> CoordinationResult:
        """Coordinate a decision across multiple agents.
        
        Args:
            topic: Topic requiring coordination
            available_agents: Agents available for coordination
            agent_votes: Votes from participating agents
            protocol: Coordination protocol to use
            timestamp_ns: Current timestamp
            
        Returns:
            Coordination result with final decision
        """
        protocol = protocol or self._default_protocol
        
        # Apply protocol-specific coordination
        if protocol == CoordinationProtocol.CONSENSUS:
            result = self._consensus_coordination(agent_votes, timestamp_ns)
        elif protocol == CoordinationProtocol.MAJORITY:
            result = self._majority_coordination(agent_votes, timestamp_ns)
        elif protocol == CoordinationProtocol.WEIGHTED_MAJORITY:
            result = self._weighted_majority_coordination(agent_votes, timestamp_ns)
        elif protocol == CoordinationProtocol.SUPERMAJORITY:
            result = self._supermajority_coordination(agent_votes, timestamp_ns)
        else:
            result = self._weighted_majority_coordination(agent_votes, timestamp_ns)
        
        # Detect and resolve conflicts
        conflict = self._detect_conflict(result, timestamp_ns)
        if conflict:
            result = self._resolve_conflict(result, conflict, timestamp_ns)
        
        # Store coordination result
        self._coordination_history.append(result)
        
        return result
    
    def _consensus_coordination(
        self,
        votes: tuple[AgentVote, ...],
        timestamp_ns: int
    ) -> CoordinationResult:
        """Full consensus coordination (all agents must agree)."""
        if not votes:
            return CoordinationResult(
                coordination_id=f"coord_{timestamp_ns}",
                protocol=CoordinationProtocol.CONSENSUS,
                final_decision="NO_DECISION",
                consensus_level=0.0,
                participating_agents=(),
                dissenting_agents=(),
                voting_breakdown={},
                required_votes_for_decision=len(votes) if votes else 0,
                confidence_in_result=0.0,
                reasoning_summary="No votes provided",
                conflict_resolution_used=None,
                timestamp_ns=timestamp_ns
            )
        
        decisions = [vote.decision for vote in votes]
        unique_decisions = set(decisions)
        
        # Check for full consensus
        if len(unique_decisions) == 1:
            final_decision = decisions[0]
            consensus_level = 1.0
            participating_agents = tuple(vote.agent_id for vote in votes)
            dissenting_agents = ()
            
            voting_breakdown = {}
            for decision in unique_decisions:
                voting_breakdown[decision] = decisions.count(decision)
            
            # Combine rationales
            rationales = [vote.rationale for vote in votes]
            reasoning_summary = " | ".join(rationales[:3])  # First 3 rationales
            
            confidence = sum(vote.confidence for vote in votes) / len(votes)
        else:
            # No consensus
            final_decision = "NO_CONSENSUS"
            consensus_level = 0.0
            participating_agents = tuple(vote.agent_id for vote in votes)
            dissenting_agents = tuple(vote.agent_id for vote in votes)
            
            voting_breakdown = {}
            for decision in unique_decisions:
                voting_breakdown[decision] = decisions.count(decision)
            
            reasoning_summary = f"Agents disagree: {', '.join(unique_decisions)}"
            confidence = 0.0
        
        return CoordinationResult(
            coordination_id=f"coord_{timestamp_ns}",
            protocol=CoordinationProtocol.CONSENSUS,
            final_decision=final_decision,
            consensus_level=consensus_level,
            participating_agents=participating_agents,
            dissenting_agents=dissenting_agents,
            voting_breakdown=voting_breakdown,
            required_votes_for_decision=len(votes),
            confidence_in_result=confidence,
            reasoning_summary=reasoning_summary,
            conflict_resolution_used=None,
            timestamp_ns=timestamp_ns
        )
    
    def _majority_coordination(
        self,
        votes: tuple[AgentVote, ...],
        timestamp_ns: int
    ) -> CoordinationResult:
        """Simple majority coordination."""
        if not votes:
            return CoordinationResult(
                coordination_id=f"coord_{timestamp_ns}",
                protocol=CoordinationProtocol.MAJORITY,
                final_decision="NO_DECISION",
                consensus_level=0.0,
                participating_agents=(),
                dissenting_agents=(),
                voting_breakdown={},
                required_votes_for_decision=len(votes) // 2 + 1 if votes else 0,
                confidence_in_result=0.0,
                reasoning_summary="No votes provided",
                conflict_resolution_used=None,
                timestamp_ns=timestamp_ns
            )
        
        # Count votes per decision
        decision_counts = {}
        decision_confidences = {}
        
        for vote in votes:
            decision_counts[vote.decision] = decision_counts.get(vote.decision, 0) + 1
            if vote.decision not in decision_confidences:
                decision_confidences[vote.decision] = []
            decision_confidences[vote.decision].append(vote.confidence)
        
        # Find majority decision
        sorted_decisions = sorted(decision_counts.items(), key=lambda x: x[1], reverse=True)
        majority_decision, majority_count = sorted_decisions[0]
        
        total_votes = len(votes)
        required = total_votes // 2 + 1
        
        if majority_count >= required:
            final_decision = majority_decision
            consensus_level = majority_count / total_votes
            
            # Calculate average confidence for winning decision
            avg_confidence = sum(decision_confidences[majority_decision]) / len(decision_confidences[majority_decision])
            
            # Identify participating vs dissenting agents
            participating_agents = tuple(vote.agent_id for vote in votes if vote.decision == majority_decision)
            dissenting_agents = tuple(vote.agent_id for vote in votes if vote.decision != majority_decision)
            
            reasoning_summary = f"Majority decision: {majority_decision} with {majority_count}/{total_votes} votes"
        else:
            final_decision = "NO_MAJORITY"
            consensus_level = 0.0
            participating_agents = tuple(vote.agent_id for vote in votes)
            dissenting_agents = ()
            avg_confidence = 0.0
            reasoning_summary = f"No majority achieved (needed {required}, got {majority_count})"
        
        return CoordinationResult(
            coordination_id=f"coord_{timestamp_ns}",
            protocol=CoordinationProtocol.MAJORITY,
            final_decision=final_decision,
            consensus_level=consensus_level,
            participating_agents=participating_agents,
            dissenting_agents=dissenting_agents,
            voting_breakdown=dict(decision_counts),
            required_votes_for_decision=required,
            confidence_in_result=avg_confidence,
            reasoning_summary=reasoning_summary,
            conflict_resolution_used=None,
            timestamp_ns=timestamp_ns
        )
    
    def _weighted_majority_coordination(
        self,
        votes: tuple[AgentVote, ...],
        timestamp_ns: int
    ) -> CoordinationResult:
        """Weighted majority coordination with performance-based weights."""
        if not votes:
            return CoordinationResult(
                coordination_id=f"coord_{timestamp_ns}",
                protocol=CoordinationProtocol.WEIGHTED_MAJORITY,
                final_decision="NO_DECISION",
                consensus_level=0.0,
                participating_agents=(),
                dissenting_agents=(),
                voting_breakdown={},
                required_votes_for_decision=0,
                confidence_in_result=0.0,
                reasoning_summary="No votes provided",
                conflict_resolution_used=None,
                timestamp_ns=timestamp_ns
            )
        
        # Calculate weighted votes
        weighted_decision_scores = {}
        
        for vote in votes:
            # Get agent's performance profile
            profile = self._performance_tracker.get_agent_profile(vote.agent_id)
            
            if profile:
                # Weight based on accuracy, consistency, and confidence calibration
                performance_weight = (
                    profile.accuracy * 0.4 +
                    profile.consistency * 0.3 +
                    profile.confidence_score * 0.3
                )
            else:
                performance_weight = 1.0  # Default weight for unknown agents
            
            # Apply the agent's confidence to their vote
            vote_weight = performance_weight * vote.confidence
            
            if vote.decision not in weighted_decision_scores:
                weighted_decision_scores[vote.decision] = 0.0
            weighted_decision_scores[vote.decision] += vote_weight
        
        # Find decision with highest weighted score
        if not weighted_decision_scores:
            final_decision = "NO_DECISION"
            consensus_level = 0.0
            participating_agents = ()
        else:
            sorted_decisions = sorted(weighted_decision_scores.items(), key=lambda x: x[1], reverse=True)
            final_decision = sorted_decisions[0][0]
            
            # Calculate consensus level based on weight distribution
            total_weight = sum(weighted_decision_scores.values())
            consensus_level = sorted_decisions[0][1] / total_weight if total_weight > 0 else 0.0
            
            participating_agents = tuple(vote.agent_id for vote in votes if vote.decision == final_decision)
            dissenting_agents = tuple(vote.agent_id for vote in votes if vote.decision != final_decision)
        
        # Calculate confidence
        final_votes = [v for v in votes if v.decision == final_decision]
        avg_confidence = sum(v.confidence for v in final_votes) / len(final_votes) if final_votes else 0.0
        
        # Voting breakdown (unweighted)
        voting_breakdown = {}
        for vote in votes:
            voting_breakdown[vote.decision] = voting_breakdown.get(vote.decision, 0) + 1
        
        reasoning_summary = f"Weighted majority: {final_decision} with {consensus_level:.1%} weighted consensus"
        
        return CoordinationResult(
            coordination_id=f"coord_{timestamp_ns}",
            protocol=CoordinationProtocol.WEIGHTED_MAJORITY,
            final_decision=final_decision,
            consensus_level=consensus_level,
            participating_agents=participating_agents,
            dissenting_agents=dissenting_agents,
            voting_breakdown=voting_breakdown,
            required_votes_for_decision=len(votes) // 2 + 1,
            confidence_in_result=avg_confidence,
            reasoning_summary=reasoning_summary,
            conflict_resolution_used=None,
            timestamp_ns=timestamp_ns
        )
    
    def _supermajority_coordination(
        self,
        votes: tuple[AgentVote, ...],
        timestamp_ns: int
    ) -> CoordinationResult:
        """Supermajority coordination (2/3 majority required)."""
        if not votes:
            return CoordinationResult(
                coordination_id=f"coord_{timestamp_ns}",
                protocol=CoordinationProtocol.SUPERMAJORITY,
                final_decision="NO_DECISION",
                consensus_level=0.0,
                participating_agents=(),
                dissenting_agents=(),
                voting_breakdown={},
                required_votes_for_decision=len(votes) * 2 // 3 if votes else 0,
                confidence_in_result=0.0,
                reasoning_summary="No votes provided",
                conflict_resolution_used=None,
                timestamp_ns=timestamp_ns
            )
        
        # Use weighted voting but require supermajority
        weighted_result = self._weighted_majority_coordination(votes, timestamp_ns)
        
        total_votes = len(votes)
        supermajority_required = (2 * total_votes) // 3
        
        winning_vote_count = len(weighted_result.participating_agents)
        
        if winning_vote_count >= supermajority_required:
            return weighted_result
        else:
            return CoordinationResult(
                coordination_id=f"coord_{timestamp_ns}",
                protocol=CoordinationProtocol.SUPERMAJORITY,
                final_decision="NO_SUPERMAJORITY",
                consensus_level=weighted_result.consensus_level,
                participating_agents=(),
                dissenting_agents=weighted_result.participating_agents,
                voting_breakdown=weighted_result.voting_breakdown,
                required_votes_for_decision=supermajority_required,
                confidence_in_result=0.0,
                reasoning_summary=f"No supermajority (needed {supermajority_required}, got {winning_vote_count})",
                conflict_resolution_used="escalation",
                timestamp_ns=timestamp_ns
            )
    
    def _detect_conflict(
        self,
        result: CoordinationResult,
        timestamp_ns: int
    ) -> AgentConflict | None:
        """Detect conflicts in coordination result."""
        if result.consensus_level > 0.8:
            return None  # High consensus, no significant conflict
        
        if result.final_decision in ("NO_DECISION", "NO_CONSENSUS", "NO_MAJORITY", "NO_SUPERMAJORITY"):
            conflict_type = "disagreement"
            subject = f"Unable to reach {result.protocol.value} consensus"
            intensity = 1.0 - result.consensus_level
        else:
            conflict_type = "partial_disagreement"
            subject = f"Dissenting agents on {result.final_decision}"
            intensity = 1.0 - result.consensus_level
        
        if intensity < 0.3:
            return None  # Low intensity conflict not worth flagging
        
        return AgentConflict(
            conflict_id=f"conflict_{timestamp_ns}",
            conflict_type=conflict_type,
            agents_involved=result.dissenting_agents,
            disagreement_intensity=intensity,
            subject=subject,
            potential_resolutions=("escalate_to_human", "use_voting_protocol", "delay_decision"),
            timestamp_ns=timestamp_ns
        )
    
    def _resolve_conflict(
        self,
        result: CoordinationResult,
        conflict: AgentConflict,
        timestamp_ns: int
    ) -> CoordinationResult:
        """Resolve conflict using predefined strategies."""
        # For now, return the original result with conflict resolution noted
        # In production, could implement escalation or alternative protocols
        
        return CoordinationResult(
            coordination_id=result.coordination_id,
            protocol=result.protocol,
            final_decision=result.final_decision,
            consensus_level=result.consensus_level,
            participating_agents=result.participating_agents,
            dissenting_agents=result.dissenting_agents,
            voting_breakdown=result.voting_breakdown,
            required_votes_for_decision=result.required_votes_for_decision,
            confidence_in_result=result.confidence_in_result * 0.8,  # Reduce confidence due to conflict
            reasoning_summary=f"{result.reasoning_summary} (conflict: {conflict.subject})",
            conflict_resolution_used="confidence_reduction",
            timestamp_ns=timestamp_ns
        )
    
    def get_recent_coordinations(self, limit: int = 10) -> tuple[CoordinationResult, ...]:
        """Get recent coordination results."""
        return tuple(list(self._coordination_history)[-limit:])


__all__ = [
    "CoordinationProtocol",
    "AgentRole",
    "AgentProfile",
    "AgentVote",
    "CoordinationResult",
    "AgentConflict",
    "AgentPerformanceTracker",
    "AdvancedCoordinationEngine"
]