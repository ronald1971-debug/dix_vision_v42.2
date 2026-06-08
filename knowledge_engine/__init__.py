"""knowledge_engine — Cognitive memory architecture for INDIRA.

Stage 11 — Knowledge Engine Creation

Provides persistent, accumulated knowledge storage across:
- trader_memory: Trader profile knowledge and behavior patterns
- strategy_memory: Evolved strategy knowledge and performance history
- market_memory: Market structure and regime observations
- execution_memory: Execution quality and venue knowledge
- cognitive_memory: Cross-domain knowledge synthesis
"""

from knowledge_engine.cognitive_ledger.ledger import (
    CognitiveEvent,
    CognitiveEventType,
    CognitiveLedger,
)
from knowledge_engine.execution_memory.store import ExecutionKnowledgeStore
from knowledge_engine.market_memory.store import MarketKnowledgeStore
from knowledge_engine.regime_memory.store import RegimeKnowledgeStore
from knowledge_engine.strategy_memory.genome import Gene, StrategyGenome
from knowledge_engine.strategy_memory.store import StrategyKnowledgeStore
from knowledge_engine.trader_memory.accretion import KnowledgeAccretor
from knowledge_engine.trader_memory.store import TraderKnowledgeStore, TraderMemory

__all__ = [
    "CognitiveEvent",
    "CognitiveEventType",
    "CognitiveLedger",
    "ExecutionKnowledgeStore",
    "Gene",
    "KnowledgeAccretor",
    "MarketKnowledgeStore",
    "RegimeKnowledgeStore",
    "StrategyGenome",
    "StrategyKnowledgeStore",
    "TraderKnowledgeStore",
    "TraderMemory",
]