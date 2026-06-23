"""
DIXVISION INDIRA Transfer Learning Across Markets
Contract-Compliant Real Implementation
"""

from .transfer_learning import (
    DomainAdaptation,
    FewShotLearning,
    KnowledgeGraphTransfer,
    MarketDomain,
    TransferLearningSystem,
    TransferRelationship,
    TransferResult,
    ZeroShotTransfer,
    get_transfer_learning_system,
)

__all__ = [
    "MarketDomain",
    "TransferRelationship",
    "TransferResult",
    "DomainAdaptation",
    "FewShotLearning",
    "ZeroShotTransfer",
    "KnowledgeGraphTransfer",
    "TransferLearningSystem",
    "get_transfer_learning_system",
]
