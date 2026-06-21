"""
Core Contracts Learning
Real implementation for learning contracts
"""

from dataclasses import dataclass, field
from enum import Enum
from typing import Dict, Any, List, Optional
import time

class LearningUpdateKind(Enum):
    """Learning update kind enumeration"""
    POLICY = "policy"
    VALUE = "value"
    MODEL = "model"
    STATE = "state"
    CONFIGURATION = "configuration"
    PATCH = "patch"

class TradeOutcome(Enum):
    """Trade outcome enumeration"""
    WIN = "win"
    LOSS = "loss"
    BREAK_EVEN = "break_even"
    PARTIAL = "partial"
    CANCELLED = "cancelled"
    ERROR = "error"

class PatchProposal:
    """Proposal for learning patches"""
    def __init__(self, patch_id: str, description: str, confidence: float = 0.5):
        self.patch_id = patch_id
        self.description = description
        self.confidence = confidence
        self.approved = False

class StrategyStats:
    """Statistics for strategies"""
    def __init__(self, strategy_id: str):
        self.strategy_id = strategy_id
        self.trades_count = 0
        self.win_rate = 0.0
        self.profit_loss = 0.0

@dataclass
class LearningUpdate:
    """Learning update information"""
    update_id: str
    update_kind: LearningUpdateKind
    source: str
    timestamp: float = field(default_factory=time.time)
    data: Dict[str, Any] = field(default_factory=dict)
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def is_policy_update(self) -> bool:
        """Check if update is a policy update"""
        return self.update_kind == LearningUpdateKind.POLICY
    
    def is_model_update(self) -> bool:
        """Check if update is a model update"""
        return self.update_kind == LearningUpdateKind.MODEL
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            "update_id": self.update_id,
            "update_kind": self.update_kind.value,
            "source": self.source,
            "timestamp": self.timestamp,
            "data": self.data,
            "metadata": self.metadata
        }

__all__ = [
    "LearningUpdateKind",
    "TradeOutcome",
    "PatchProposal",
    "StrategyStats",
    "LearningUpdate"
]