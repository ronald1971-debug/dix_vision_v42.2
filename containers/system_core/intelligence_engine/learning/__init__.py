"""Learning module - Mature with Reinforcement Loops and Cognitive Learning Governance."""

# Existing components
from .cognitive_governance import (
    CognitiveLearningGovernance,
    GovernanceAction,
    GovernanceDecision,
    LearningConstraint,
    LearningPhase,
    get_cognitive_learning_governance,
)

# New mature learning components
from .reinforcement_engine import (
    FeedbackSample,
    LearningRateStrategy,
    ParameterBounds,
    ReinforcementEngine,
    ReinforcementStatus,
    ReinforcementUpdate,
    get_reinforcement_engine,
)
from .slow_loop import FeedbackSample, ParameterBounds, SlowLoopLearner

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
