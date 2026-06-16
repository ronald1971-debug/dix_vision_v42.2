"""Multi-Agent Intelligence Collaboration System.

This module provides multi-agent intelligence capabilities, enabling multiple specialized
AI agents to collaborate, share knowledge, and make collective decisions.
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
import hashlib

logger = logging.getLogger(__name__)


class AgentType(str, Enum):
    """Types of specialized agents."""
    MARKET_ANALYST = "MARKET_ANALYST"
    RISK_MANAGER = "RISK_MANAGER"
    PORTFOLIO_OPTIMIZER = "PORTFOLIO_OPTIMIZER"
    SIGNAL_PROCESSOR = "SIGNAL_PROCESSOR"
    PREDICTION_ENGINE = "PREDICTION_ENGINE"
    EXECUTION_COACH = "EXECUTION_COACH"
    KNOWLEDGE_ARCHITECT = "KNOWLEDGE_ARCHITECT"
    STRATEGY_CONSULTANT = "STRATEGY_CONSULTANT"


class CollaborationMode(str, Enum):
    """Collaboration modes for agents."""
    PARALLEL = "PARALLEL"
    SEQUENTIAL = "SEQUENTIAL"
    CONSENSUS = "CONSENSUS"
    HIERARCHICAL = "HIERARCHICAL"
    COMPETITIVE = "COMPETITIVE"


class MessageType(str, Enum):
    """Types of messages between agents."""
    REQUEST = "REQUEST"
    RESPONSE = "RESPONSE"
    BROADCAST = "BROADCAST"
    NOTIFICATION = "NOTIFICATION"
    QUERY = "QUERY"
    RESULT = "RESULT"


@dataclass
class Agent:
    """Specialized AI agent."""
    agent_id: str
    agent_type: AgentType
    capabilities: List[str]
    confidence: float
    reliability: float
    specialization_score: float
    status: str  # "idle", "busy", "offline"
    current_task: Optional[str] = None
    performance_history: List[float] = field(default_factory=list)
    knowledge_base: Dict[str, Any] = field(default_factory=dict)


@dataclass
class AgentMessage:
    """Message between agents."""
    message_id: str
    sender_id: str
    receiver_id: str
    message_type: MessageType
    content: Dict[str, Any]
    timestamp: float
    priority: int


@dataclass
class CollaborativeDecision:
    """Decision made through agent collaboration."""
    decision_id: str
    primary_agent_id: str
    contributing_agents: List[str]
    decision_content: Dict[str, Any]
    consensus_level: float
    individual_contributions: Dict[str, Dict[str, Any]]
    collaboration_mode: CollaborationMode
    timestamp: float


@dataclass
class AgentPerformance:
    """Performance metrics for an agent."""
    agent_id: str
    agent_type: AgentType
    total_tasks: int
    successful_tasks: int
    average_confidence: float
    reliability_score: float
    specializations: Dict[str, float]
    recent_performance: float


class MultiAgentSystem:
    """Multi-agent intelligence collaboration system."""

    def __init__(self):
        self._lock = threading.Lock()
        self._agents: Dict[str, Agent] = {}
        self._message_bus: deque = deque(maxlen=10000)
        self._agent_coordinator = AgentCoordinator()
        self._consensus_builder = ConsensusBuilder()
        self._task_distributor = TaskDistributor()
        self._knowledge_sharer = KnowledgeSharer()
        self._collaboration_history: deque = deque(maxlen=1000)
        self._initialized = False

    def start(self) -> bool:
        """Start multi-agent system."""
        logger.info("[MULTI_AGENT] Starting multi-agent system...")
        
        # Initialize default agents
        self._initialize_default_agents()
        
        self._initialized = True
        logger.info(f"[MULTI_AGENT] Multi-agent system started with {len(self._agents)} agents")
        return True

    def stop(self) -> bool:
        """Stop multi-agent system."""
        logger.info("[MULTI_AGENT] Stopping multi-agent system...")
        
        # Set all agents to offline
        with self._lock:
            for agent in self._agents.values():
                agent.status = "offline"
        
        self._initialized = False
        logger.info("[MULTI_AGENT] Multi-agent system stopped")
        return True

    def register_agent(self, agent: Agent) -> bool:
        """Register a new agent."""
        with self._lock:
            if agent.agent_id in self._agents:
                logger.warning(f"[MULTI_AGENT] Agent {agent.agent_id} already registered")
                return False
            
            self._agents[agent.agent_id] = agent
            logger.info(f"[MULTI_AGENT] Registered agent {agent.agent_id} of type {agent.agent_type}")
            return True

    def send_message(self, sender_id: str, receiver_id: str, message_type: MessageType, 
                    content: Dict[str, Any], priority: int = 0) -> str:
        """Send message from one agent to another."""
        message_id = f"msg_{int(time.time())}_{hash(str(content)) % 10000}"
        
        message = AgentMessage(
            message_id=message_id,
            sender_id=sender_id,
            receiver_id=receiver_id,
            message_type=message_type,
            content=content,
            timestamp=time.time(),
            priority=priority
        )
        
        with self._lock:
            self._message_bus.append(message)
        
        logger.debug(f"[MULTI_AGENT] Message {message_id} from {sender_id} to {receiver_id}")
        return message_id

    def collaborate_decision(self, task: Dict[str, Any], 
                           collaboration_mode: CollaborationMode = CollaborationMode.CONSENSUS) -> CollaborativeDecision:
        """Make a decision through agent collaboration."""
        logger.info(f"[MULTI_AGENT] Collaborating on decision using {collaboration_mode} mode")
        
        decision_id = f"collab_decision_{int(time.time())}"
        
        # Select relevant agents for the task
        relevant_agents = self._task_distributor.select_agents(task, list(self._agents.values()))
        
        if not relevant_agents:
            # Fallback to any available agent
            relevant_agents = list(self._agents.values())[:3]
        
        # Coordinate collaboration
        if collaboration_mode == CollaborationMode.PARALLEL:
            decision = self._agent_coordinator.parallel_collaboration(relevant_agents, task)
        elif collaboration_mode == CollaborationMode.SEQUENTIAL:
            decision = self._agent_coordinator.sequential_collaboration(relevant_agents, task)
        elif collaboration_mode == CollaborationMode.CONSENSUS:
            decision = self._consensus_builder.build_consensus(relevant_agents, task)
        elif collaboration_mode == CollaborationMode.HIERARCHICAL:
            decision = self._agent_coordinator.hierarchical_collaboration(relevant_agents, task)
        elif collaboration_mode == CollaborationMode.COMPETITIVE:
            decision = self._agent_coordinator.competitive_collaboration(relevant_agents, task)
        else:
            decision = self._consensus_builder.build_consensus(relevant_agents, task)
        
        # Store collaboration history
        with self._lock:
            self._collaboration_history.append(decision)
        
        return decision

    def share_knowledge(self, source_agent_id: str, knowledge: Dict[str, Any], 
                       target_agent_ids: Optional[List[str]] = None) -> None:
        """Share knowledge between agents."""
        logger.info(f"[MULTI_AGENT] Agent {source_agent_id} sharing knowledge")
        
        with self._lock:
            if target_agent_ids:
                # Share with specific agents
                for target_id in target_agent_ids:
                    if target_id in self._agents:
                        self._agents[target_id].knowledge_base.update(knowledge)
                        self.send_message(source_agent_id, target_id, MessageType.NOTIFICATION, knowledge)
            else:
                # Broadcast to all agents
                for agent_id in self._agents:
                    if agent_id != source_agent_id:
                        self._agents[agent_id].knowledge_base.update(knowledge)
                        self.send_message(source_agent_id, agent_id, MessageType.BROADCAST, knowledge)

    def get_agent_performance(self, agent_id: str) -> Optional[AgentPerformance]:
        """Get performance metrics for an agent."""
        with self._lock:
            if agent_id not in self._agents:
                return None
            
            agent = self._agents[agent_id]
            
            performance = AgentPerformance(
                agent_id=agent.agent_id,
                agent_type=agent.agent_type,
                total_tasks=len(agent.performance_history),
                successful_tasks=sum(1 for score in agent.performance_history if score > 0.7),
                average_confidence=np.mean(agent.performance_history) if agent.performance_history else agent.confidence,
                reliability_score=agent.reliability,
                specializations={cap: agent.specialization_score for cap in agent.capabilities},
                recent_performance=np.mean(agent.performance_history[-5:]) if len(agent.performance_history) >= 5 else agent.confidence
            )
            
            return performance

    def get_system_statistics(self) -> Dict[str, Any]:
        """Get multi-agent system statistics."""
        with self._lock:
            active_agents = sum(1 for agent in self._agents.values() if agent.status == "idle" or agent.status == "busy")
            
            return {
                "total_agents": len(self._agents),
                "active_agents": active_agents,
                "agent_types": {agent_type.value: sum(1 for agent in self._agents.values() if agent.agent_type == agent_type) 
                              for agent_type in AgentType},
                "total_messages": len(self._message_bus),
                "collaboration_history_size": len(self._collaboration_history),
                "average_agent_confidence": np.mean([agent.confidence for agent in self._agents.values()]) if self._agents else 0.0
            }

    def _initialize_default_agents(self) -> None:
        """Initialize default specialized agents."""
        default_agents = [
            Agent(
                agent_id="market_analyst_1",
                agent_type=AgentType.MARKET_ANALYST,
                capabilities=["market_analysis", "trend_detection", "market_prediction"],
                confidence=0.8,
                reliability=0.9,
                specialization_score=0.85,
                status="idle"
            ),
            Agent(
                agent_id="risk_manager_1",
                agent_type=AgentType.RISK_MANAGER,
                capabilities=["risk_assessment", "risk_mitigation", "risk_monitoring"],
                confidence=0.85,
                reliability=0.95,
                specialization_score=0.9,
                status="idle"
            ),
            Agent(
                agent_id="signal_processor_1",
                agent_type=AgentType.SIGNAL_PROCESSOR,
                capabilities=["signal_detection", "noise_filtering", "pattern_recognition"],
                confidence=0.75,
                reliability=0.85,
                specialization_score=0.8,
                status="idle"
            ),
            Agent(
                agent_id="portfolio_optimizer_1",
                agent_type=AgentType.PORTFOLIO_OPTIMIZER,
                capabilities=["portfolio_optimization", "asset_allocation", "rebalancing"],
                confidence=0.8,
                reliability=0.9,
                specialization_score=0.85,
                status="idle"
            ),
            Agent(
                agent_id="prediction_engine_1",
                agent_type=AgentType.PREDICTION_ENGINE,
                capabilities=["market_prediction", "price_forecasting", "trend_prediction"],
                confidence=0.7,
                reliability=0.8,
                specialization_score=0.75,
                status="idle"
            )
        ]
        
        for agent in default_agents:
            self.register_agent(agent)


class AgentCoordinator:
    """Coordinate agent collaboration."""

    def parallel_collaboration(self, agents: List[Agent], task: Dict[str, Any]) -> CollaborativeDecision:
        """Parallel collaboration - all agents work independently."""
        contributions = {}
        
        for agent in agents:
            contribution = self._get_agent_contribution(agent, task)
            contributions[agent.agent_id] = contribution
        
        # Combine contributions
        combined_decision = self._combine_contributions(contributions)
        
        return CollaborativeDecision(
            decision_id=f"parallel_{int(time.time())}",
            primary_agent_id=agents[0].agent_id if agents else "unknown",
            contributing_agents=[agent.agent_id for agent in agents],
            decision_content=combined_decision,
            consensus_level=self._calculate_consensus(contributions),
            individual_contributions=contributions,
            collaboration_mode=CollaborationMode.PARALLEL,
            timestamp=time.time()
        )

    def sequential_collaboration(self, agents: List[Agent], task: Dict[str, Any]) -> CollaborativeDecision:
        """Sequential collaboration - agents work in sequence."""
        contributions = {}
        current_task = task
        
        for agent in agents:
            contribution = self._get_agent_contribution(agent, current_task)
            contributions[agent.agent_id] = contribution
            
            # Update task based on previous agent's output
            if contribution.get("output"):
                current_task = contribution["output"]
        
        combined_decision = contributions[agents[-1].agent_id] if agents else {}
        
        return CollaborativeDecision(
            decision_id=f"sequential_{int(time.time())}",
            primary_agent_id=agents[-1].agent_id if agents else "unknown",
            contributing_agents=[agent.agent_id for agent in agents],
            decision_content=combined_decision,
            consensus_level=self._calculate_consensus(contributions),
            individual_contributions=contributions,
            collaboration_mode=CollaborationMode.SEQUENTIAL,
            timestamp=time.time()
        )

    def hierarchical_collaboration(self, agents: List[Agent], task: Dict[str, Any]) -> CollaborativeDecision:
        """Hierarchical collaboration - agents work in hierarchy."""
        # Sort agents by specialization score
        sorted_agents = sorted(agents, key=lambda x: x.specialization_score, reverse=True)
        
        if not sorted_agents:
            return self._create_empty_decision()
        
        # Primary agent (highest specialization)
        primary_agent = sorted_agents[0]
        primary_contribution = self._get_agent_contribution(primary_agent, task)
        
        # Supporting agents
        supporting_agents = sorted_agents[1:]
        supporting_contributions = {}
        for agent in supporting_agents:
            contribution = self._get_agent_contribution(agent, task)
            supporting_contributions[agent.agent_id] = contribution
        
        # Primary agent makes final decision with supporting input
        final_decision = self._combine_with_primary(primary_contribution, supporting_contributions)
        
        contributions = {primary_agent.agent_id: primary_contribution}
        contributions.update(supporting_contributions)
        
        return CollaborativeDecision(
            decision_id=f"hierarchical_{int(time.time())}",
            primary_agent_id=primary_agent.agent_id,
            contributing_agents=[agent.agent_id for agent in agents],
            decision_content=final_decision,
            consensus_level=0.9,  # High consensus in hierarchical mode
            individual_contributions=contributions,
            collaboration_mode=CollaborationMode.HIERARCHICAL,
            timestamp=time.time()
        )

    def competitive_collaboration(self, agents: List[Agent], task: Dict[str, Any]) -> CollaborativeDecision:
        """Competitive collaboration - agents compete for best solution."""
        contributions = {}
        
        for agent in agents:
            contribution = self._get_agent_contribution(agent, task)
            contributions[agent.agent_id] = contribution
        
        # Select best contribution
        best_agent_id = max(contributions.keys(), key=lambda x: contributions[x].get("confidence", 0.0))
        best_contribution = contributions[best_agent_id]
        
        return CollaborativeDecision(
            decision_id=f"competitive_{int(time.time())}",
            primary_agent_id=best_agent_id,
            contributing_agents=[agent.agent_id for agent in agents],
            decision_content=best_contribution,
            consensus_level=best_contribution.get("confidence", 0.5),
            individual_contributions=contributions,
            collaboration_mode=CollaborationMode.COMPETITIVE,
            timestamp=time.time()
        )

    def _get_agent_contribution(self, agent: Agent, task: Dict[str, Any]) -> Dict[str, Any]:
        """Get contribution from an agent for a task."""
        # Simplified contribution generation
        # In real implementation, would call agent's actual reasoning process
        
        contribution = {
            "agent_id": agent.agent_id,
            "agent_type": agent.agent_type.value,
            "confidence": agent.confidence,
            "output": {
                "recommendation": "proceed",
                "risk_level": "moderate",
                "expected_outcome": "positive"
            },
            "reasoning": f"Agent {agent.agent_id} analyzed task based on capabilities: {agent.capabilities}"
        }
        
        return contribution

    def _combine_contributions(self, contributions: Dict[str, Dict]) -> Dict[str, Any]:
        """Combine contributions from multiple agents."""
        if not contributions:
            return {}
        
        # Simple combination: average confidence, combine outputs
        avg_confidence = np.mean([c.get("confidence", 0.5) for c in contributions.values()])
        
        combined_output = {
            "recommendation": "proceed" if avg_confidence > 0.5 else "wait",
            "confidence": avg_confidence,
            "contributing_agents": len(contributions)
        }
        
        return combined_output

    def _combine_with_primary(self, primary: Dict, supporting: Dict[str, Dict]) -> Dict[str, Any]:
        """Combine primary contribution with supporting contributions."""
        combined = primary.copy()
        combined["supporting_inputs"] = supporting
        combined["confidence"] = primary.get("confidence", 0.5)  # Primary confidence dominates
        return combined

    def _calculate_consensus(self, contributions: Dict[str, Dict]) -> float:
        """Calculate consensus level among contributions."""
        if not contributions:
            return 0.0
        
        confidences = [c.get("confidence", 0.5) for c in contributions.values()]
        
        # Consensus based on confidence variance
        if len(confidences) < 2:
            return confidences[0] if confidences else 0.0
        
        variance = np.var(confidences)
        consensus = 1.0 - min(1.0, variance * 2.0)  # Higher variance = lower consensus
        
        return consensus

    def _create_empty_decision(self) -> CollaborativeDecision:
        """Create empty decision when no agents available."""
        return CollaborativeDecision(
            decision_id=f"empty_{int(time.time())}",
            primary_agent_id="none",
            contributing_agents=[],
            decision_content={},
            consensus_level=0.0,
            individual_contributions={},
            collaboration_mode=CollaborationMode.CONSENSUS,
            timestamp=time.time()
        )


class ConsensusBuilder:
    """Build consensus among multiple agents."""

    def build_consensus(self, agents: List[Agent], task: Dict[str, Any]) -> CollaborativeDecision:
        """Build consensus through agent collaboration."""
        if not agents:
            return self._create_empty_decision()

        coordinator = AgentCoordinator()
        contributions = {}
        
        # Get individual contributions
        for agent in agents:
            contribution = coordinator._get_agent_contribution(agent, task)
            contributions[agent.agent_id] = contribution
        
        # Weight agents by reliability and specialization
        weights = self._calculate_agent_weights(agents)
        
        # Build weighted consensus
        consensus = self._build_weighted_consensus(contributions, weights)
        
        consensus_level = self._calculate_consensus_agreement(contributions)
        
        return CollaborativeDecision(
            decision_id=f"consensus_{int(time.time())}",
            primary_agent_id=max(contributions.keys(), key=lambda x: weights.get(x, 0.5)),
            contributing_agents=[agent.agent_id for agent in agents],
            decision_content=consensus,
            consensus_level=consensus_level,
            individual_contributions=contributions,
            collaboration_mode=CollaborationMode.CONSENSUS,
            timestamp=time.time()
        )

    def _calculate_agent_weights(self, agents: List[Agent]) -> Dict[str, float]:
        """Calculate weights for agents based on reliability and specialization."""
        weights = {}
        total_weight = 0.0
        
        for agent in agents:
            # Weight based on reliability and specialization
            weight = agent.reliability * agent.specialization_score
            weights[agent.agent_id] = weight
            total_weight += weight
        
        # Normalize weights
        if total_weight > 0:
            weights = {k: v / total_weight for k, v in weights.items()}
        
        return weights

    def _build_weighted_consensus(self, contributions: Dict[str, Dict], weights: Dict[str, float]) -> Dict[str, Any]:
        """Build weighted consensus from contributions."""
        if not contributions:
            return {}
        
        # Weighted average of confidences
        weighted_confidence = 0.0
        for agent_id, contribution in contributions.items():
            weight = weights.get(agent_id, 1.0 / len(contributions))
            weighted_confidence += weight * contribution.get("confidence", 0.5)
        
        consensus = {
            "recommendation": "proceed" if weighted_confidence > 0.6 else "wait",
            "confidence": weighted_confidence,
            "consensus_method": "weighted_voting"
        }
        
        return consensus

    def _calculate_consensus_agreement(self, contributions: Dict[str, Dict]) -> float:
        """Calculate level of agreement among contributions."""
        if len(contributions) < 2:
            return contributions[list(contributions.keys())[0]].get("confidence", 0.5) if contributions else 0.0
        
        # Calculate agreement based on confidence proximity
        confidences = [c.get("confidence", 0.5) for c in contributions.values()]
        
        # Use inverse of standard deviation as agreement measure
        if len(confidences) < 2:
            return confidences[0]
        
        std_dev = np.std(confidences)
        agreement = 1.0 - min(1.0, std_dev)
        
        return agreement

    def _create_empty_decision(self) -> CollaborativeDecision:
        """Create empty decision."""
        return CollaborativeDecision(
            decision_id=f"empty_{int(time.time())}",
            primary_agent_id="none",
            contributing_agents=[],
            decision_content={},
            consensus_level=0.0,
            individual_contributions={},
            collaboration_mode=CollaborationMode.CONSENSUS,
            timestamp=time.time()
        )


class TaskDistributor:
    """Distribute tasks to appropriate agents."""

    def select_agents(self, task: Dict[str, Any], available_agents: List[Agent]) -> List[Agent]:
        """Select appropriate agents for a task."""
        # Extract task requirements
        task_type = task.get("task_type", "general")
        required_capabilities = task.get("required_capabilities", [])
        
        # Score agents based on relevance
        scored_agents = []
        for agent in available_agents:
            score = self._score_agent_relevance(agent, task_type, required_capabilities)
            scored_agents.append((agent, score))
        
        # Sort by score and select top agents
        scored_agents.sort(key=lambda x: x[1], reverse=True)
        selected_agents = [agent for agent, score in scored_agents[:5]]  # Top 5 agents
        
        return selected_agents

    def _score_agent_relevance(self, agent: Agent, task_type: str, required_capabilities: List[str]) -> float:
        """Score agent relevance for a task."""
        score = 0.0
        
        # Capability match score
        capability_matches = len(set(agent.capabilities) & set(required_capabilities))
        if required_capabilities:
            score += capability_matches / len(required_capabilities) * 0.5
        else:
            score += 0.3  # Base score if no specific requirements
        
        # Specialization score
        score += agent.specialization_score * 0.3
        
        # Reliability score
        score += agent.reliability * 0.2
        
        return score


class KnowledgeSharer:
    """Share knowledge between agents."""

    def share_agent_knowledge(self, source_agent: Agent, target_agents: List[Agent], 
                            message_bus: deque, send_message_fn: Callable) -> None:
        """Share knowledge from source agent to target agents."""
        knowledge_to_share = source_agent.knowledge_base
        
        for target_agent in target_agents:
            # Determine relevance of knowledge
            relevance = self._calculate_knowledge_relevance(knowledge_to_share, target_agent)
            
            if relevance > 0.5:  # Only share relevant knowledge
                # Share knowledge
                target_agent.knowledge_base.update(knowledge_to_share)
                
                # Send notification message
                send_message_fn(
                    source_agent.agent_id,
                    target_agent.agent_id,
                    MessageType.NOTIFICATION,
                    {"type": "knowledge_share", "knowledge": knowledge_to_share}
                )

    def _calculate_knowledge_relevance(self, knowledge: Dict, target_agent: Agent) -> float:
        """Calculate relevance of knowledge to target agent."""
        # Simple relevance calculation based on capability overlap
        knowledge_keys = set(knowledge.keys())
        agent_capabilities = set(target_agent.capabilities)
        
        # Look for overlap between knowledge keys and agent capabilities
        overlap = len(knowledge_keys & agent_capabilities)
        total_keys = len(knowledge_keys) if knowledge_keys else 1
        
        relevance = overlap / total_keys if total_keys > 0 else 0.0
        
        return min(1.0, relevance + 0.2)  # Base relevance of 0.2


# Singleton instance
_multi_agent_system: Optional[MultiAgentSystem] = None
_multi_agent_system_lock = threading.Lock()


def get_multi_agent_system() -> MultiAgentSystem:
    """Get the singleton multi-agent system instance."""
    global _multi_agent_system
    if _multi_agent_system is None:
        with _multi_agent_system_lock:
            if _multi_agent_system is None:
                _multi_agent_system = MultiAgentSystem()
    return _multi_agent_system


__all__ = [
    "MultiAgentSystem",
    "get_multi_agent_system",
    "AgentType",
    "CollaborationMode",
    "MessageType",
    "Agent",
    "AgentMessage",
    "CollaborativeDecision",
    "AgentPerformance",
]