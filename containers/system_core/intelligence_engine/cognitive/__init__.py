"""Cognitive module - M-1 Knowledge Layer and production cognitive intelligence."""

from .approval_edge import ApprovalEdge
from .approval_projection import ApprovalProjection, get_approval_projection, projection_rows_from_payloads, DECISION_KINDS, PENDING_KIND
from .approval_queue import ApprovalQueue, get_approval_queue
from .chat import CognitiveChatFeatureFlag, FEATURE_FLAG_ENV_VAR

# Production-grade cognitive intelligence
from .production_intelligence import (
    ProductionPatternRecognition,
    ProductionRiskAssessment,
    ProductionDecisionEngine,
    get_production_decision_engine,
    DecisionType,
    ConfidenceLevel,
    MarketDataPoint,
    DecisionContext,
    CognitiveDecision,
)

__all__ = [
    # Existing cognitive components
    "ApprovalEdge",
    "ApprovalProjection",
    "get_approval_projection",
    "projection_rows_from_payloads",
    "DECISION_KINDS",
    "PENDING_KIND",
    "ApprovalQueue",
    "get_approval_queue",
    "CognitiveChatFeatureFlag",
    "FEATURE_FLAG_ENV_VAR",
    # Production intelligence
    "ProductionPatternRecognition",
    "ProductionRiskAssessment",
    "ProductionDecisionEngine",
    "get_production_decision_engine",
    "DecisionType",
    "ConfidenceLevel",
    "MarketDataPoint",
    "DecisionContext",
    "CognitiveDecision",
]
