"""Stateful intelligence agents (INV-54, B19, AGT-XX family).

Concrete agents live in this package and implement
:class:`core.contracts.agent.AgentIntrospection` via the abstract
base in :mod:`intelligence_engine.agents._base`.
"""

from intelligence_engine.agents._base import AgentBase
from intelligence_engine.agents.adversarial import AdversarialAgent
from intelligence_engine.agents.adversary_agent import (
    AdversaryAgent as AdversaryManipulationAgent,
)
from intelligence_engine.agents.adversary_agent import (
    ManipulationPattern,
)
from intelligence_engine.agents.lp import LiquidityProviderAgent
from intelligence_engine.agents.macro import MacroAgent
from intelligence_engine.agents.scalper import ScalperAgent
from intelligence_engine.agents.swing import SwingAgent
from intelligence_engine.agents.advanced_coordination import (
    CoordinationProtocol,
    AgentRole,
    AgentProfile,
    AgentVote,
    CoordinationResult,
    AgentConflict,
    AgentPerformanceTracker,
    AdvancedCoordinationEngine,
)

__all__ = [
    "AdversarialAgent",
    "AdversaryManipulationAgent",
    "AgentBase",
    "LiquidityProviderAgent",
    "MacroAgent",
    "ManipulationPattern",
    "ScalperAgent",
    "SwingAgent",
    "CoordinationProtocol",
    "AgentRole",
    "AgentProfile",
    "AgentVote",
    "CoordinationResult",
    "AgentConflict",
    "AgentPerformanceTracker",
    "AdvancedCoordinationEngine",
]
