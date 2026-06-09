"""
DYON Memory - Engineering and automation memory for DYON
"""

import logging
from typing import Dict, List, Any, Optional
from .memory import AgentMemory


class DYONMemory(AgentMemory):
    """
    Memory system for DYON agent.
    
    Stores repository graphs, architecture graphs, dependency graphs,
    skill graphs, and automation graphs for engineering intelligence.
    """
    
    def __init__(self, config: Dict[str, Any] = None):
        """
        Initialize DYON memory.
        
        Args:
            config: Memory configuration
        """
        super().__init__(config)
        
        # Graphs
        self.repository_graph: Dict[str, Dict[str, Any]] = {}
        self.architecture_graph: Dict[str, Dict[str, Any]] = {}
        self.dependency_graph: Dict[str, List[str]] = {}
        self.skill_graph: Dict[str, Dict[str, Any]] = {}
        self.automation_graph: Dict[str, Dict[str, Any]] = {}
        
    async def initialize(self) -> None:
        """Initialize memory system."""
        self.is_initialized = True
        self.logger.info("DYON Memory initialized")
        
    async def store(self, key: str, value: Any) -> None:
        """
        Store a value in memory.
        
        Args:
            key: Storage key
            value: Value to store
        """
        if key.startswith("repository:"):
            self.repository_graph[key.replace("repository:", "")] = value
        elif key.startswith("architecture:"):
            self.architecture_graph[key.replace("architecture:", "")] = value
        elif key.startswith("dependency:"):
            self.dependency_graph[key.replace("dependency:", "")] = value
        elif key.startswith("skill:"):
            self.skill_graph[key.replace("skill:", "")] = value
        elif key.startswith("automation:"):
            self.automation_graph[key.replace("automation:", "")] = value
            
    async def retrieve(self, key: str) -> Optional[Any]:
        """
        Retrieve a value from memory.
        
        Args:
            key: Storage key
            
        Returns:
            Stored value or None
        """
        if key.startswith("repository:"):
            return self.repository_graph.get(key.replace("repository:", ""))
        elif key.startswith("architecture:"):
            return self.architecture_graph.get(key.replace("architecture:", ""))
        elif key.startswith("dependency:"):
            return self.dependency_graph.get(key.replace("dependency:", ""))
        elif key.startswith("skill:"):
            return self.skill_graph.get(key.replace("skill:", ""))
        elif key.startswith("automation:"):
            return self.automation_graph.get(key.replace("automation:", ""))
        return None
        
    async def search(self, query: str) -> List[Dict[str, Any]]:
        """
        Search memory for matching entries.
        
        Args:
            query: Search query
            
        Returns:
            List of matching entries
        """
        results = []
        
        for graph in [
            self.repository_graph,
            self.architecture_graph,
            self.skill_graph,
            self.automation_graph,
        ]:
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
        if key.startswith("repository:"):
            self.repository_graph.pop(key.replace("repository:", ""), None)
        elif key.startswith("architecture:"):
            self.architecture_graph.pop(key.replace("architecture:", ""), None)
        elif key.startswith("dependency:"):
            self.dependency_graph.pop(key.replace("dependency:", ""), None)
        elif key.startswith("skill:"):
            self.skill_graph.pop(key.replace("skill:", ""), None)
        elif key.startswith("automation:"):
            self.automation_graph.pop(key.replace("automation:", ""), None)
            
    async def add_dependency(self, source: str, target: str) -> None:
        """
        Add a dependency relationship.
        
        Args:
            source: Source component
            target: Target component
        """
        if source not in self.dependency_graph:
            self.dependency_graph[source] = []
        if target not in self.dependency_graph[source]:
            self.dependency_graph[source].append(target)
            
    async def get_dependencies(self, component: str) -> List[str]:
        """
        Get dependencies for a component.
        
        Args:
            component: Component name
            
        Returns:
            List of dependencies
        """
        return self.dependency_graph.get(component, [])
        
    def get_status(self) -> Dict[str, Any]:
        """
        Get memory status.
        
        Returns:
            Status dictionary
        """
        return {
            "repository_nodes": len(self.repository_graph),
            "architecture_nodes": len(self.architecture_graph),
            "dependency_edges": sum(len(v) for v in self.dependency_graph.values()),
            "skill_nodes": len(self.skill_graph),
            "automation_nodes": len(self.automation_graph),
        }
