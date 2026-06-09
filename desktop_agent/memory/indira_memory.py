"""
INDIRA Memory - Market and research memory for INDIRA
"""

import logging
from typing import Dict, List, Any, Optional
from .memory import AgentMemory


class INDIRAMemory(AgentMemory):
    """
    Memory system for INDIRA agent.
    
    Stores knowledge graphs, trader graphs, narrative graphs,
    strategy graphs, market beliefs, hypotheses, and research history.
    """
    
    def __init__(self, config: Dict[str, Any] = None):
        """
        Initialize INDIRA memory.
        
        Args:
            config: Memory configuration
        """
        super().__init__(config)
        
        # Graphs
        self.knowledge_graph: Dict[str, Dict[str, Any]] = {}
        self.trader_graph: Dict[str, Dict[str, Any]] = {}
        self.narrative_graph: Dict[str, Dict[str, Any]] = {}
        self.strategy_graph: Dict[str, Dict[str, Any]] = {}
        
        # Other memory
        self.market_beliefs: Dict[str, Any] = {}
        self.hypotheses: List[Dict[str, Any]] = []
        self.research_history: List[Dict[str, Any]] = []
        
    async def initialize(self) -> None:
        """Initialize memory system."""
        self.is_initialized = True
        self.logger.info("INDIRA Memory initialized")
        
    async def store(self, key: str, value: Any) -> None:
        """
        Store a value in memory.
        
        Args:
            key: Storage key
            value: Value to store
        """
        # Determine which graph/memory to store in
        if key.startswith("knowledge:"):
            self.knowledge_graph[key.replace("knowledge:", "")] = value
        elif key.startswith("trader:"):
            self.trader_graph[key.replace("trader:", "")] = value
        elif key.startswith("narrative:"):
            self.narrative_graph[key.replace("narrative:", "")] = value
        elif key.startswith("strategy:"):
            self.strategy_graph[key.replace("strategy:", "")] = value
        else:
            self.market_beliefs[key] = value
            
    async def retrieve(self, key: str) -> Optional[Any]:
        """
        Retrieve a value from memory.
        
        Args:
            key: Storage key
            
        Returns:
            Stored value or None
        """
        if key.startswith("knowledge:"):
            return self.knowledge_graph.get(key.replace("knowledge:", ""))
        elif key.startswith("trader:"):
            return self.trader_graph.get(key.replace("trader:", ""))
        elif key.startswith("narrative:"):
            return self.narrative_graph.get(key.replace("narrative:", ""))
        elif key.startswith("strategy:"):
            return self.strategy_graph.get(key.replace("strategy:", ""))
        else:
            return self.market_beliefs.get(key)
            
    async def search(self, query: str) -> List[Dict[str, Any]]:
        """
        Search memory for matching entries.
        
        Args:
            query: Search query
            
        Returns:
            List of matching entries
        """
        results = []
        
        for graph in [self.knowledge_graph, self.trader_graph, self.narrative_graph]:
            for key, value in graph.items():
                if query.lower() in str(value).lower():
                    results.append({"key": key, "value": value})
                    
        return results
        
    async def forget(self, key: str) -> None:
        """
        Remove an entry from memory.
        
        Args:
            key: Storage key
        """
        if key.startswith("knowledge:"):
            self.knowledge_graph.pop(key.replace("knowledge:", ""), None)
        elif key.startswith("trader:"):
            self.trader_graph.pop(key.replace("trader:", ""), None)
        elif key.startswith("narrative:"):
            self.narrative_graph.pop(key.replace("narrative:", ""), None)
        elif key.startswith("strategy:"):
            self.strategy_graph.pop(key.replace("strategy:", ""), None)
        else:
            self.market_beliefs.pop(key, None)
            
    async def add_hypothesis(self, hypothesis: Dict[str, Any]) -> None:
        """
        Add a hypothesis to memory.
        
        Args:
            hypothesis: Hypothesis data
        """
        self.hypotheses.append(hypothesis)
        
    async def get_hypotheses(self) -> List[Dict[str, Any]]:
        """
        Get all hypotheses.
        
        Returns:
            List of hypotheses
        """
        return self.hypotheses
        
    async def add_research_entry(self, entry: Dict[str, Any]) -> None:
        """
        Add a research history entry.
        
        Args:
            entry: Research entry data
        """
        self.research_history.append(entry)
        
    async def get_research_history(self) -> List[Dict[str, Any]]:
        """
        Get research history.
        
        Returns:
            List of research entries
        """
        return self.research_history
        
    def get_status(self) -> Dict[str, Any]:
        """
        Get memory status.
        
        Returns:
            Status dictionary
        """
        return {
            "knowledge_nodes": len(self.knowledge_graph),
            "trader_nodes": len(self.trader_graph),
            "narrative_nodes": len(self.narrative_graph),
            "strategy_nodes": len(self.strategy_graph),
            "hypotheses": len(self.hypotheses),
            "research_entries": len(self.research_history),
        }
