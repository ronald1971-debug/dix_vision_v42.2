"""
Core Coherence Belief State
Real implementation for belief state management
"""

import time
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Dict, List, Optional


class Regime(Enum):
    """Belief state regime enumeration"""

    ACTIVE = "active"
    PASSIVE = "passive"
    HYBRID = "hybrid"
    ADAPTIVE = "adaptive"
    STATIC = "static"
    DYNAMIC = "dynamic"
    EXPLORATORY = "exploratory"
    EXPLOITATIVE = "exploitative"
    CAUTIOUS = "cautious"
    AGGRESSIVE = "aggressive"


class BeliefStatus(Enum):
    """Belief status enumeration"""

    CONFIDENT = "confident"
    UNCERTAIN = "uncertain"
    LEARNING = "learning"
    CONSOLIDATED = "consolidated"
    FRAGMENTED = "fragmented"
    CONFLICTING = "conflicting"
    PENDING = "pending"
    STALE = "stale"


@dataclass
class Belief:
    """Single belief in the belief state"""

    belief_id: str
    topic: str
    content: str
    confidence: float
    status: BeliefStatus = BeliefStatus.PENDING
    timestamp: float = field(default_factory=time.time)
    evidence: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)

    def is_confident(self) -> bool:
        """Check if belief is confident"""
        return self.status == BeliefStatus.CONFIDENT and self.confidence > 0.7

    def is_uncertain(self) -> bool:
        """Check if belief is uncertain"""
        return self.status in [BeliefStatus.UNCERTAIN, BeliefStatus.LEARNING]

    def add_evidence(self, evidence: str) -> None:
        """Add evidence to the belief"""
        self.evidence.append(evidence)
        self.timestamp = time.time()

    def update_confidence(self, delta: float) -> None:
        """Update confidence by delta, clamping to [0, 1]"""
        self.confidence = max(0.0, min(1.0, self.confidence + delta))
        self.timestamp = time.time()

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            "belief_id": self.belief_id,
            "topic": self.topic,
            "content": self.content,
            "confidence": self.confidence,
            "status": self.status.value,
            "timestamp": self.timestamp,
            "evidence": self.evidence,
            "metadata": self.metadata,
        }


@dataclass
class BeliefState:
    """Complete belief state"""

    state_id: str
    regime: Regime
    beliefs: Dict[str, Belief] = field(default_factory=dict)
    timestamp: float = field(default_factory=time.time)
    metadata: Dict[str, Any] = field(default_factory=dict)

    def add_belief(self, belief: Belief) -> bool:
        """Add a belief to the state"""
        self.beliefs[belief.belief_id] = belief
        self.timestamp = time.time()
        return True

    def remove_belief(self, belief_id: str) -> bool:
        """Remove a belief from the state"""
        if belief_id in self.beliefs:
            del self.beliefs[belief_id]
            self.timestamp = time.time()
            return True
        return False

    def get_belief(self, belief_id: str) -> Optional[Belief]:
        """Get a specific belief"""
        return self.beliefs.get(belief_id)

    def get_beliefs_by_topic(self, topic: str) -> List[Belief]:
        """Get all beliefs for a topic"""
        return [b for b in self.beliefs.values() if b.topic == topic]

    def get_confident_beliefs(self) -> List[Belief]:
        """Get all confident beliefs"""
        return [b for b in self.beliefs.values() if b.is_confident()]

    def get_uncertain_beliefs(self) -> List[Belief]:
        """Get all uncertain beliefs"""
        return [b for b in self.beliefs.values() if b.is_uncertain()]

    def update_regime(self, new_regime: Regime) -> None:
        """Update the regime"""
        self.regime = new_regime
        self.timestamp = time.time()

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            "state_id": self.state_id,
            "regime": self.regime.value,
            "beliefs": {k: v.to_dict() for k, v in self.beliefs.items()},
            "timestamp": self.timestamp,
            "metadata": self.metadata,
        }


class BeliefStateManager:
    """Manager for belief states"""

    def __init__(self):
        self._states: Dict[str, BeliefState] = {}
        self._active_state_id: Optional[str] = None

    def create_state(self, state_id: str, regime: Regime) -> BeliefState:
        """Create a new belief state"""
        state = BeliefState(state_id=state_id, regime=regime)
        self._states[state_id] = state
        if self._active_state_id is None:
            self._active_state_id = state_id
        return state

    def get_state(self, state_id: str) -> Optional[BeliefState]:
        """Get a specific belief state"""
        return self._states.get(state_id)

    def get_active_state(self) -> Optional[BeliefState]:
        """Get the active belief state"""
        if self._active_state_id:
            return self._states.get(self._active_state_id)
        return None

    def set_active_state(self, state_id: str) -> bool:
        """Set the active belief state"""
        if state_id in self._states:
            self._active_state_id = state_id
            return True
        return False

    def get_all_states(self) -> List[BeliefState]:
        """Get all belief states"""
        return list(self._states.values())


# Global belief state manager
_belief_state_manager: Optional[BeliefStateManager] = None


def get_belief_state_manager() -> BeliefStateManager:
    """Get the global belief state manager"""
    global _belief_state_manager
    if _belief_state_manager is None:
        _belief_state_manager = BeliefStateManager()
    return _belief_state_manager


def create_belief_state(state_id: str, regime: Regime) -> BeliefState:
    """Create a new belief state"""
    return get_belief_state_manager().create_state(state_id, regime)


def create_belief(belief_id: str, topic: str, content: str, confidence: float) -> Belief:
    """Create a new belief"""
    return Belief(belief_id=belief_id, topic=topic, content=content, confidence=confidence)


__all__ = [
    "Regime",
    "BeliefStatus",
    "Belief",
    "BeliefState",
    "BeliefStateManager",
    "get_belief_state_manager",
    "create_belief_state",
    "create_belief",
]
