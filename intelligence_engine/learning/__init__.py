"""Learning module - Mature with Reinforcement Loops and Cognitive Learning Governance."""

# Existing components
from .slow_loop import SlowLoopLearner, ParameterBounds, FeedbackSample

# New mature learning components
from .reinforcement_engine import (
    ReinforcementEngine,
    get_reinforcement_engine,
    FeedbackSample,
    ParameterBounds,
    ReinforcementUpdate,
    LearningRateStrategy,
    ReinforcementStatus,
)
from .cognitive_governance import (
    CognitiveLearningGovernance,
    get_cognitive_learning_governance,
    LearningConstraint,
    GovernanceDecision,
    GovernanceAction,
    LearningPhase,
)

__all__ = [
    # Existing
    "SlowLoopLearner",
    # Reinforcement Engine (supersedes slow_loop)
    "ReinforcementEngine",
    "get_reinforcement_engine",
    "FeedbackSample",
    "ParameterBounds",
    "ReinforcementUpdate",
    "LearningRateStrategy",
    "ReinforcementStatus",
    # Cognitive Governance
    "CognitiveLearningGovernance",
    "get_cognitive_learning_governance",
    "LearningConstraint",
    "GovernanceDecision",
    "GovernanceAction",
    "LearningPhase",
]