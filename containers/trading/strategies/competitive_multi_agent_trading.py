"""
DIX VISION Competitive Multi-Agent Trading System

Enhances the existing multi-agent system for competitive trading dynamics,
enabling agents to compete and collaborate in trading environments.
"""

from __future__ import annotations

import logging
import threading
from collections import defaultdict, deque
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Dict, List, Optional
import numpy as np

# Import existing multi-agent system
import sys
sys.path.insert(0, "c:/dix_vision_v42.2/containers/system_core/cognitive_os/multi_agent")
from multi_agent_system import MultiAgentSystem, AgentRole, AgentCapability

logger = logging.getLogger(__name__)


@dataclass
class TradingAgent:
    """Trading agent with competitive capabilities."""
    agent_id: str
    agent_name: str
    agent_role: AgentRole
    trading_strategy: str
    competitive_profile: Dict[str, float]
    performance_metrics: Dict[str, float]
    collaboration_score: float
    competition_score: float
    resources: Dict[str, float]
    timestamp: float


@dataclass
class CompetitiveInteraction:
    """Interaction between competitive trading agents."""
    interaction_id: str
    agent1_id: str
    agent2_id: str
    interaction_type: str  # "compete", "collaborate", "observe", "learn"
    interaction_outcome: str
    mutual_benefit: float
    resource_transfer: Dict[str, float]
    knowledge_transfer: Dict[str, Any]
    timestamp: float


@dataclass
class AgentCompetitionResult:
    """Result of agent competition."""
    competition_id: str
    participating_agents: List[str]
    winner: str
    winning_strategy: str
    performance_scores: Dict[str, float]
    learning_insights: Dict[str, Any]
    timestamp: float


@dataclass
class MarketSimulation:
    """Market simulation for agent competition."""
    simulation_id: str
    market_conditions: Dict[str, Any]
    participating_agents: List[str]
    agent_positions: Dict[str, Dict[str, float]]
    market_dynamics: List[Dict[str, Any]]
    final_state: Dict[str, Any]
    timestamp: datetime = field(default_factory=datetime.now)


class CompetitiveMultiAgentTrading:
    """
    Competitive multi-agent trading system.
    
    Enables agents to:
    - Compete for trading opportunities
    - Collaborate on complex strategies
    - Learn from each other's performance
    - Adapt to competitive dynamics
    """
    
    def __init__(self):
        # Initialize multi-agent system
        self._multi_agent_system = MultiAgentSystem()
        
        # Trading agents
        self._trading_agents: Dict[str, TradingAgent] = {}
        
        # Competitive interactions
        self._competitive_interactions: List[CompetitiveInteraction] = []
        
        # Competition results
        self._competition_results: List[AgentCompetitionResult] = []
        
        # Market simulations
        self._market_simulations: List[MarketSimulation] = []
        
        # Competitive dynamics parameters
        self._competition_intensity = 0.7
        self._collaboration_incentive = 0.3
        self._learning_rate = 0.1
        
        self._lock = threading.Lock()
        
        # Initialize default trading agents
        self._initialize_default_agents()
        
        logger.info("Competitive Multi-Agent Trading System initialized")
    
    def _initialize_default_agents(self):
        """Initialize default trading agents."""
        default_agents = [
            {
                "agent_id": "momentum_agent",
                "agent_name": "Momentum Specialist",
                "agent_role": AgentRole.TRADER,
                "trading_strategy": "momentum",
                "competitive_profile": {
                    "aggressiveness": 0.8,
                    "risk_tolerance": 0.6,
                    "adaptability": 0.7,
                    "learning_speed": 0.5
                }
            },
            {
                "agent_id": "mean_reversion_agent",
                "agent_name": "Mean Reversion Specialist",
                "agent_role": AgentRole.TRADER,
                "trading_strategy": "mean_reversion",
                "competitive_profile": {
                    "aggressiveness": 0.4,
                    "risk_tolerance": 0.5,
                    "adaptability": 0.6,
                    "learning_speed": 0.7
                }
            },
            {
                "agent_id": "arbitrage_agent",
                "agent_name": "Arbitrage Specialist",
                "agent_role": AgentRole.ANALYZER,
                "trading_strategy": "arbitrage",
                "competitive_profile": {
                    "aggressiveness": 0.6,
                    "risk_tolerance": 0.3,
                    "adaptability": 0.8,
                    "learning_speed": 0.6
                }
            },
            {
                "agent_id": "sentiment_agent",
                "agent_name": "Sentiment Analyst",
                "agent_role": AgentRole.ANALYZER,
                "trading_strategy": "sentiment",
                "competitive_profile": {
                    "aggressiveness": 0.5,
                    "risk_tolerance": 0.4,
                    "adaptability": 0.9,
                    "learning_speed": 0.8
                }
            }
        ]
        
        for agent_config in default_agents:
            agent = TradingAgent(
                agent_id=agent_config["agent_id"],
                agent_name=agent_config["agent_name"],
                agent_role=agent_config["agent_role"],
                trading_strategy=agent_config["trading_strategy"],
                competitive_profile=agent_config["competitive_profile"],
                performance_metrics={
                    "total_trades": 0,
                    "win_rate": 0.0,
                    "profit_factor": 1.0,
                    "sharpe_ratio": 0.0
                },
                collaboration_score=0.5,
                competition_score=0.5,
                resources={
                    "capital": 100000.0,
                    "compute": 0.5,
                    "data": 0.6
                },
                timestamp=datetime.now().timestamp()
            )
            
            self._trading_agents[agent.agent_id] = agent
        
        logger.info(f"Initialized {len(self._trading_agents)} default trading agents")
    
    def create_competitive_interaction(self, agent1_id: str, agent2_id: str,
                                    interaction_type: str) -> CompetitiveInteraction:
        """Create a competitive interaction between agents."""
        agent1 = self._trading_agents.get(agent1_id)
        agent2 = self._trading_agents.get(agent2_id)
        
        if not agent1 or not agent2:
            return None
        
        # Calculate interaction outcome based on competitive profiles
        if interaction_type == "compete":
            interaction_outcome = self._simulate_competition(agent1, agent2)
            mutual_benefit = 0.0  # Competition has zero mutual benefit
        elif interaction_type == "collaborate":
            interaction_outcome = self._simulate_collaboration(agent1, agent2)
            mutual_benefit = 0.7  # Collaboration has high mutual benefit
        elif interaction_type == "observe":
            interaction_outcome = "observation_complete"
            mutual_benefit = 0.3  # Observation has some benefit
        elif interaction_type == "learn":
            interaction_outcome = self._simulate_learning(agent1, agent2)
            mutual_benefit = 0.5  # Learning has moderate mutual benefit
        else:
            interaction_outcome = "unknown"
            mutual_benefit = 0.0
        
        # Calculate resource transfer
        resource_transfer = self._calculate_resource_transfer(agent1, agent2, interaction_type)
        
        # Calculate knowledge transfer
        knowledge_transfer = self._calculate_knowledge_transfer(agent1, agent2, interaction_type)
        
        interaction = CompetitiveInteraction(
            interaction_id=f"interaction_{int(datetime.now().timestamp())}",
            agent1_id=agent1_id,
            agent2_id=agent2_id,
            interaction_type=interaction_type,
            interaction_outcome=interaction_outcome,
            mutual_benefit=mutual_benefit,
            resource_transfer=resource_transfer,
            knowledge_transfer=knowledge_transfer,
            timestamp=datetime.now().timestamp()
        )
        
        # Update agent scores based on interaction
        self._update_agent_interaction_scores(agent1, agent2, interaction)
        
        with self._lock:
            self._competitive_interactions.append(interaction)
        
        return interaction
    
    def _simulate_competition(self, agent1: TradingAgent, agent2: TradingAgent) -> str:
        """Simulate competition between two agents."""
        # Compare competitive profiles
        agent1_score = (
            agent1.competitive_profile["aggressiveness"] * 0.4 +
            agent1.competitive_profile["risk_tolerance"] * 0.3 +
            agent1.competitive_profile["adaptability"] * 0.3
        )
        
        agent2_score = (
            agent2.competitive_profile["aggressiveness"] * 0.4 +
            agent2.competitive_profile["risk_tolerance"] * 0.3 +
            agent2.competitive_profile["adaptability"] * 0.3
        )
        
        # Add some randomness
        agent1_score += np.random.uniform(-0.1, 0.1)
        agent2_score += np.random.uniform(-0.1, 0.1)
        
        if agent1_score > agent2_score:
            return f"{agent1.agent_id}_wins"
        elif agent2_score > agent1_score:
            return f"{agent2.agent_id}_wins"
        else:
            return "draw"
    
    def _simulate_collaboration(self, agent1: TradingAgent, agent2: TradingAgent) -> str:
        """Simulate collaboration between two agents."""
        # Collaboration success based on compatibility
        strategy_compatibility = self._calculate_strategy_compatibility(
            agent1.trading_strategy, agent2.trading_strategy
        )
        
        collaboration_success = strategy_compatibility * 0.7 + np.random.uniform(0.0, 0.3)
        
        if collaboration_success > 0.7:
            return "collaboration_successful"
        elif collaboration_success > 0.4:
            return "collaboration_partial"
        else:
            return "collaboration_failed"
    
    def _simulate_learning(self, agent1: TradingAgent, agent2: TradingAgent) -> str:
        """Simulate learning from another agent."""
        # Learning success based on learning speed and knowledge gap
        learning_potential = (
            agent1.competitive_profile["learning_speed"] * 0.6 +
            (1.0 - abs(agent1.performance_metrics["win_rate"] - agent2.performance_metrics["win_rate"])) * 0.4
        )
        
        if learning_potential > 0.7:
            return "learning_successful"
        elif learning_potential > 0.4:
            return "learning_partial"
        else:
            return "learning_failed"
    
    def _calculate_strategy_compatibility(self, strategy1: str, strategy2: str) -> float:
        """Calculate compatibility between two trading strategies."""
        # Strategy compatibility matrix
        compatibility_matrix = {
            ("momentum", "momentum"): 0.3,  # Same strategies have low compatibility (competition)
            ("momentum", "mean_reversion"): 0.8,  # Complementary strategies
            ("momentum", "arbitrage"): 0.6,  # Moderate compatibility
            ("momentum", "sentiment"): 0.7,  # Good compatibility
            ("mean_reversion", "mean_reversion"): 0.3,
            ("mean_reversion", "arbitrage"): 0.7,
            ("mean_reversion", "sentiment"): 0.6,
            ("arbitrage", "arbitrage"): 0.3,
            ("arbitrage", "sentiment"): 0.5,
            ("sentiment", "sentiment"): 0.3
        }
        
        return compatibility_matrix.get((strategy1, strategy2), 0.5)
    
    def _calculate_resource_transfer(self, agent1: TradingAgent, agent2: TradingAgent,
                                   interaction_type: str) -> Dict[str, float]:
        """Calculate resource transfer between agents."""
        resource_transfer = {}
        
        if interaction_type == "collaborate":
            # In collaboration, agents share resources
            resource_transfer["capital"] = min(agent1.resources["capital"], agent2.resources["capital"]) * 0.1
            resource_transfer["compute"] = 0.1
            resource_transfer["data"] = 0.1
        elif interaction_type == "learn":
            # Learning requires some resource transfer
            resource_transfer["compute"] = 0.05
            resource_transfer["data"] = 0.05
        else:
            # Competition and observation don't transfer resources
            resource_transfer["capital"] = 0.0
            resource_transfer["compute"] = 0.0
            resource_transfer["data"] = 0.0
        
        return resource_transfer
    
    def _calculate_knowledge_transfer(self, agent1: TradingAgent, agent2: TradingAgent,
                                   interaction_type: str) -> Dict[str, Any]:
        """Calculate knowledge transfer between agents."""
        knowledge_transfer = {}
        
        if interaction_type == "collaborate":
            # Collaboration enables significant knowledge sharing
            knowledge_transfer["strategy_insights"] = True
            knowledge_transfer["market_analysis"] = True
            knowledge_transfer["risk_assessment"] = True
        elif interaction_type == "learn":
            # Learning enables单向 knowledge transfer
            knowledge_transfer["strategy_insights"] = True
            knowledge_transfer["market_analysis"] = False
            knowledge_transfer["risk_assessment"] = False
        elif interaction_type == "observe":
            # Observation enables limited knowledge transfer
            knowledge_transfer["strategy_insights"] = False
            knowledge_transfer["market_analysis"] = True
            knowledge_transfer["risk_assessment"] = False
        else:
            # Competition doesn't enable knowledge transfer
            knowledge_transfer["strategy_insights"] = False
            knowledge_transfer["market_analysis"] = False
            knowledge_transfer["risk_assessment"] = False
        
        return knowledge_transfer
    
    def _update_agent_interaction_scores(self, agent1: TradingAgent, agent2: TradingAgent,
                                       interaction: CompetitiveInteraction):
        """Update agent collaboration and competition scores."""
        if interaction.interaction_type == "collaborate":
            agent1.collaboration_score = min(1.0, agent1.collaboration_score + 0.1)
            agent2.collaboration_score = min(1.0, agent2.collaboration_score + 0.1)
        elif interaction.interaction_type == "compete":
            agent1.competition_score = min(1.0, agent1.competition_score + 0.1)
            agent2.competition_score = min(1.0, agent2.competition_score + 0.1)
        elif interaction.interaction_type == "learn":
            # Learning doesn't strongly affect scores
            pass
    
    def run_competition(self, participating_agents: List[str],
                      market_conditions: Dict[str, Any]) -> AgentCompetitionResult:
        """Run a competition between trading agents."""
        # Validate agents
        valid_agents = [agent_id for agent_id in participating_agents if agent_id in self._trading_agents]
        
        if len(valid_agents) < 2:
            return None
        
        # Simulate competition
        performance_scores = {}
        
        for agent_id in valid_agents:
            agent = self._trading_agents[agent_id]
            
            # Calculate performance based on strategy and market conditions
            performance = self._calculate_agent_performance(agent, market_conditions)
            performance_scores[agent_id] = performance
            
            # Update agent metrics
            agent.performance_metrics["total_trades"] += 1
            agent.performance_metrics["win_rate"] = performance
        
        # Determine winner
        winner = max(performance_scores, key=performance_scores.get)
        winning_agent = self._trading_agents[winner]
        
        # Generate learning insights
        learning_insights = {
            "best_performing_strategy": winning_agent.trading_strategy,
            "market_conditions_favor": market_conditions.get("regime", "UNKNOWN"),
            "average_performance": np.mean(list(performance_scores.values())),
            "performance_variance": np.var(list(performance_scores.values()))
        }
        
        competition_result = AgentCompetitionResult(
            competition_id=f"competition_{int(datetime.now().timestamp())}",
            participating_agents=valid_agents,
            winner=winner,
            winning_strategy=winning_agent.trading_strategy,
            performance_scores=performance_scores,
            learning_insights=learning_insights,
            timestamp=datetime.now().timestamp()
        )
        
        with self._lock:
            self._competition_results.append(competition_result)
        
        logger.info(f"Competition completed: winner={winner}, strategy={winning_agent.trading_strategy}")
        
        return competition_result
    
    def _calculate_agent_performance(self, agent: TradingAgent,
                                  market_conditions: Dict[str, Any]) -> float:
        """Calculate agent performance in given market conditions."""
        strategy = agent.trading_strategy
        regime = market_conditions.get("regime", "UNKNOWN")
        volatility = market_conditions.get("volatility", 0.2)
        
        # Strategy-market fit
        strategy_fit = {
            "momentum": {"BULLISH": 0.9, "BEARISH": 0.3, "SIDEWAYS": 0.4, "HIGH_VOLATILITY": 0.5},
            "mean_reversion": {"BULLISH": 0.3, "BEARISH": 0.4, "SIDEWAYS": 0.9, "HIGH_VOLATILITY": 0.7},
            "arbitrage": {"BULLISH": 0.5, "BEARISH": 0.5, "SIDEWAYS": 0.6, "HIGH_VOLATILITY": 0.8},
            "sentiment": {"BULLISH": 0.7, "BEARISH": 0.6, "SIDEWAYS": 0.5, "HIGH_VOLATILITY": 0.4}
        }
        
        base_performance = strategy_fit.get(strategy, {}).get(regime, 0.5)
        
        # Adjust for agent capabilities
        capability_adjustment = (
            agent.competitive_profile["adaptability"] * 0.3 +
            agent.competitive_profile["learning_speed"] * 0.2 +
            agent.competitive_profile["risk_tolerance"] * 0.2
        )
        
        # Adjust for volatility
        volatility_adjustment = 0.0
        if volatility > 0.5 and strategy in ["momentum", "sentiment"]:
            volatility_adjustment = -0.2  # High volatility hurts momentum/sentiment
        elif volatility > 0.5 and strategy in ["arbitrage", "mean_reversion"]:
            volatility_adjustment = 0.2  # High volatility helps arbitrage/mean reversion
        
        # Calculate final performance
        performance = base_performance + capability_adjustment + volatility_adjustment
        performance = max(0.0, min(1.0, performance + np.random.uniform(-0.1, 0.1)))
        
        return performance
    
    def simulate_market_competition(self, market_conditions: Dict[str, Any],
                                   num_steps: int = 10) -> MarketSimulation:
        """Simulate competitive trading in market conditions."""
        participating_agents = list(self._trading_agents.keys())
        
        # Initialize agent positions
        agent_positions = {
            agent_id: {
                "capital": self._trading_agents[agent_id].resources["capital"],
                "position": 0.0,
                "pnl": 0.0
            }
            for agent_id in participating_agents
        }
        
        # Simulate market dynamics
        market_dynamics = []
        
        for step in range(num_steps):
            # Update market conditions
            step_conditions = market_conditions.copy()
            step_conditions["step"] = step
            step_conditions["volatility"] = market_conditions.get("volatility", 0.2) * (1 + np.random.uniform(-0.2, 0.2))
            
            # Run competition for this step
            step_result = self.run_competition(participating_agents, step_conditions)
            
            if step_result:
                # Update agent positions based on competition result
                winner = step_result.winner
                loser_performance = min([score for agent, score in step_result.performance_scores.items() if agent != winner])
                
                # Winner gains, loser loses
                agent_positions[winner]["pnl"] += 1000.0 * step_result.performance_scores[winner]
                for agent_id in participating_agents:
                    if agent_id != winner:
                        agent_positions[agent_id]["pnl"] -= 500.0 * loser_performance
            
            market_dynamics.append({
                "step": step,
                "conditions": step_conditions,
                "positions": {k: v.copy() for k, v in agent_positions.items()}
            })
        
        # Calculate final state
        final_state = {
            "winner": max(agent_positions, key=lambda k: agent_positions[k]["pnl"]),
            "total_pnl": sum(pos["pnl"] for pos in agent_positions.values()),
            "best_performing_agent": max(participating_agents, key=lambda k: agent_positions[k]["pnl"])
        }
        
        simulation = MarketSimulation(
            simulation_id=f"simulation_{int(datetime.now().timestamp())}",
            market_conditions=market_conditions,
            participating_agents=participating_agents,
            agent_positions=agent_positions,
            market_dynamics=market_dynamics,
            final_state=final_state
        )
        
        with self._lock:
            self._market_simulations.append(simulation)
        
        return simulation
    
    def get_competitive_insights(self) -> Dict[str, Any]:
        """Get insights from competitive interactions."""
        with self._lock:
            recent_interactions = self._competitive_interactions[-20:] if self._competitive_interactions else []
            recent_competitions = self._competition_results[-10:] if self._competition_results else []
            
            interaction_type_distribution = {}
            for interaction in recent_interactions:
                interaction_type = interaction.interaction_type
                interaction_type_distribution[interaction_type] = interaction_type_distribution.get(interaction_type, 0) + 1
            
            winner_distribution = {}
            for competition in recent_competitions:
                winner = competition.winner
                winner_distribution[winner] = winner_distribution.get(winner, 0) + 1
            
            return {
                "total_agents": len(self._trading_agents),
                "total_interactions": len(self._competitive_interactions),
                "total_competitions": len(self._competition_results),
                "total_simulations": len(self._market_simulations),
                "interaction_type_distribution": interaction_type_distribution,
                "winner_distribution": winner_distribution,
                "average_collaboration_score": np.mean([a.collaboration_score for a in self._trading_agents.values()]),
                "average_competition_score": np.mean([a.competition_score for a in self._trading_agents.values()]),
                "competition_intensity": self._competition_intensity,
                "collaboration_incentive": self._collaboration_incentive
            }


# Global instance
_competitive_multi_agent_trading: Optional[CompetitiveMultiAgentTrading] = None


def get_competitive_multi_agent_trading() -> CompetitiveMultiAgentTrading:
    """Get global competitive multi-agent trading instance."""
    global _competitive_multi_agent_trading
    if _competitive_multi_agent_trading is None:
        _competitive_multi_agent_trading = CompetitiveMultiAgentTrading()
    return _competitive_multi_agent_trading