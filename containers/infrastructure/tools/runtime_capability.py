"""
Runtime Capability
Real implementation for runtime capability management
"""

import time
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Set


class CapabilityKind(str):
    """Capability kind enumeration - flexible to accept any value"""

    DEPENDENCY = "dependency"
    RESOURCE = "resource"
    FEATURE = "feature"
    SERVICE = "service"

    def __new__(cls, value):
        return str.__new__(cls, value)

    def __init__(self, value):
        self.value = value


@dataclass
class DependencyNode:
    """Dependency node information"""

    node_id: str
    node_type: str
    dependencies: List[str] = field(default_factory=list)
    timestamp: float = field(default_factory=time.time)
    metadata: Dict[str, Any] = field(default_factory=dict)

    def __init__(self, **kwargs):
        """Initialize DependencyNode - accepts any kwargs for compatibility"""
        self.node_id = kwargs.get("node_id", "")
        self.node_type = kwargs.get("node_type", "")
        self.dependencies = kwargs.get("dependencies", [])
        self.timestamp = kwargs.get("timestamp", time.time())
        self.metadata = kwargs.get("metadata", {})
        # Store any additional parameters in metadata
        for key, value in kwargs.items():
            if key not in ["node_id", "node_type", "dependencies", "timestamp", "metadata"]:
                self.metadata[key] = value

    def has_dependency(self, dependency_id: str) -> bool:
        """Check if node has a specific dependency"""
        return dependency_id in self.dependencies

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            "node_id": self.node_id,
            "node_type": self.node_type,
            "dependencies": self.dependencies,
            "timestamp": self.timestamp,
            "metadata": self.metadata,
        }


class DependencyGraphResolver:
    """Resolver for dependency graphs"""

    def __init__(self):
        self._nodes: Dict[str, DependencyNode] = {}
        self._graph: Dict[str, Set[str]] = {}

    def add_node(self, node: DependencyNode) -> bool:
        """Add a node to the dependency graph"""
        self._nodes[node.node_id] = node
        self._graph[node.node_id] = set(node.dependencies)
        return True

    def get_node(self, node_id: str) -> Optional[DependencyNode]:
        """Get a specific node"""
        return self._nodes.get(node_id)

    def resolve_dependencies(self, node_id: str) -> List[str]:
        """Resolve dependencies for a node"""
        if node_id not in self._graph:
            return []
        resolved = []
        visited = set()

        def dfs(nid):
            if nid in visited:
                return
            visited.add(nid)
            for dep in self._graph.get(nid, []):
                dfs(dep)
            resolved.append(nid)

        dfs(node_id)
        return resolved

    def get_all_nodes(self) -> List[DependencyNode]:
        """Get all nodes"""
        return list(self._nodes.values())


@dataclass
class RuntimeCapabilityMap:
    """Runtime capability map information"""

    map_id: str
    capabilities: Dict[str, Any] = field(default_factory=dict)
    timestamp: float = field(default_factory=time.time)
    metadata: Dict[str, Any] = field(default_factory=dict)

    def __init__(self, **kwargs):
        """Initialize RuntimeCapabilityMap - accepts any kwargs for compatibility"""
        self.map_id = kwargs.get("map_id", "")
        self.capabilities = kwargs.get("capabilities", {})
        self.timestamp = kwargs.get("timestamp", time.time())
        self.metadata = kwargs.get("metadata", {})
        # Store any additional parameters in metadata
        for key, value in kwargs.items():
            if key not in ["map_id", "capabilities", "timestamp", "metadata"]:
                self.metadata[key] = value

    def has_capability(self, capability: str) -> bool:
        """Check if has a specific capability"""
        return capability in self.capabilities

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            "map_id": self.map_id,
            "capabilities": self.capabilities,
            "timestamp": self.timestamp,
            "metadata": self.metadata,
        }


# Global dependency resolver
_dependency_resolver: Optional[DependencyGraphResolver] = None


def get_dependency_resolver() -> DependencyGraphResolver:
    """Get the global dependency resolver"""
    global _dependency_resolver
    if _dependency_resolver is None:
        _dependency_resolver = DependencyGraphResolver()
    return _dependency_resolver


__all__ = [
    "CapabilityKind",
    "DependencyNode",
    "DependencyGraphResolver",
    "RuntimeCapabilityMap",
    "get_dependency_resolver",
]
