"""
Runtime Topology
Real implementation for runtime topology management
"""

import time
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Dict, List, Optional


class TopologyKind(Enum):
    """Topology kind enumeration"""

    LINEAR = "linear"
    TREE = "tree"
    GRAPH = "graph"
    MESH = "mesh"
    STAR = "star"


class EdgeRelation(str):
    """Edge relation enumeration - flexible to accept any value"""

    PARENT = "parent"
    CHILD = "child"
    PEER = "peer"
    DEPENDS_ON = "depends_on"
    PROVIDES_TO = "provides_to"
    PRODUCES = "produces"
    GATES = "gates"
    OWNS = "owns"
    PROJECTS = "projects"
    CONTROLS = "controls"

    def __new__(cls, value):
        return str.__new__(cls, value)

    def __init__(self, value):
        self.value = value


class LifecycleState(str):
    """Lifecycle state enumeration - flexible to accept any value"""

    INITIALIZING = "initializing"
    READY = "ready"
    ACTIVE = "active"
    RUNNING = "running"
    PAUSED = "paused"
    STOPPING = "stopping"
    STOPPED = "stopped"
    ERROR = "error"
    FAILED = "failed"
    STARTED = "started"
    DORMANT = "dormant"
    HEALTHY = "healthy"
    DEGRADED = "degraded"

    def __new__(cls, value):
        return str.__new__(cls, value)

    def __init__(self, value):
        self.value = value


class NodeKind(str):
    """Node kind enumeration - flexible to accept any value"""

    ENGINE = "engine"
    SERVICE = "service"
    COMPONENT = "component"
    ADAPTER = "adapter"
    PLUGIN = "plugin"
    LOOP = "loop"
    SYSTEM = "system"
    HELPER = "helper"
    MONITOR = "monitor"
    GATEWAY = "gateway"
    REGISTRY = "registry"
    GATE = "gate"
    POLICY = "policy"
    SENSOR = "sensor"

    def __new__(cls, value):
        return str.__new__(cls, value)

    def __init__(self, value):
        self.value = value


class NodeTier(str):
    """Node tier enumeration - flexible to accept any value"""

    T0 = "t0"
    T1 = "t1"
    T2 = "t2"
    T3 = "t3"
    T4 = "t4"
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"
    OPTIONAL = "optional"

    def __new__(cls, value):
        return str.__new__(cls, value)

    def __init__(self, value):
        self.value = value


@dataclass
class RuntimeEdge:
    """Runtime edge information"""

    edge_id: str
    source_id: str
    target_id: str
    relation: EdgeRelation
    properties: Dict[str, Any] = field(default_factory=dict)
    timestamp: float = field(default_factory=time.time)
    metadata: Dict[str, Any] = field(default_factory=dict)

    def __init__(self, edge_id: str = None, **kwargs):
        """Initialize RuntimeEdge - accepts any kwargs for compatibility"""
        self.edge_id = edge_id or kwargs.get("edge_id", "")
        self.source_id = kwargs.get("source_id", "")
        self.target_id = kwargs.get("target_id", "")
        self.relation = kwargs.get("relation", EdgeRelation.PEER)
        self.properties = kwargs.get("properties", {})
        self.timestamp = kwargs.get("timestamp", time.time())
        self.metadata = kwargs.get("metadata", {})
        # Store any additional parameters in metadata
        for key, value in kwargs.items():
            if key not in [
                "edge_id",
                "source_id",
                "target_id",
                "relation",
                "properties",
                "timestamp",
                "metadata",
            ]:
                self.metadata[key] = value

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            "edge_id": self.edge_id,
            "source_id": self.source_id,
            "target_id": self.target_id,
            "relation": str(self.relation),
            "properties": self.properties,
            "timestamp": self.timestamp,
            "metadata": self.metadata,
        }


@dataclass
class RuntimeNode:
    """Runtime node information"""

    node_id: str
    node_kind: NodeKind
    node_tier: NodeTier
    lifecycle_state: LifecycleState
    properties: Dict[str, Any] = field(default_factory=dict)
    timestamp: float = field(default_factory=time.time)
    metadata: Dict[str, Any] = field(default_factory=dict)

    def __init__(self, node_id: str, **kwargs):
        """Initialize RuntimeNode - accepts any kwargs for compatibility"""
        self.node_id = node_id
        # Accept both naming conventions
        self.node_kind = kwargs.get("kind") or kwargs.get("node_kind", NodeKind.ENGINE)
        self.node_tier = kwargs.get("tier") or kwargs.get("node_tier", NodeTier.T1)
        self.lifecycle_state = (
            kwargs.get("lifecycle_state")
            or kwargs.get("state")
            or kwargs.get("state_attr", LifecycleState.READY)
        )
        self.properties = kwargs.get("properties", {})
        self.timestamp = kwargs.get("timestamp", time.time())
        self.metadata = kwargs.get("metadata", {})
        # Add capabilities if provided
        self.capabilities = kwargs.get("capabilities", set())
        # Store any additional parameters in metadata
        for key, value in kwargs.items():
            if key not in [
                "node_id",
                "kind",
                "node_kind",
                "tier",
                "node_tier",
                "lifecycle_state",
                "state",
                "state_attr",
                "properties",
                "timestamp",
                "metadata",
                "capabilities",
                "declared_version",
            ]:
                self.metadata[key] = value

    def is_active(self) -> bool:
        """Check if node is active"""
        return str(self.lifecycle_state) == "active"

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            "node_id": self.node_id,
            "node_kind": str(self.node_kind),
            "node_tier": str(self.node_tier),
            "lifecycle_state": str(self.lifecycle_state),
            "properties": self.properties,
            "timestamp": self.timestamp,
            "metadata": self.metadata,
        }


@dataclass
class TopologyNode:
    """Topology node information"""

    node_id: str
    node_type: str
    connections: List[str] = field(default_factory=list)
    properties: Dict[str, Any] = field(default_factory=dict)
    timestamp: float = field(default_factory=time.time)
    metadata: Dict[str, Any] = field(default_factory=dict)

    def is_connected_to(self, node_id: str) -> bool:
        """Check if connected to a specific node"""
        return node_id in self.connections

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            "node_id": self.node_id,
            "node_type": self.node_type,
            "connections": self.connections,
            "properties": self.properties,
            "timestamp": self.timestamp,
            "metadata": self.metadata,
        }


class RuntimeTopology:
    """Runtime topology manager"""

    def __init__(self, **kwargs):
        """Initialize - accepts any kwargs for compatibility"""
        self._nodes: Dict[str, TopologyNode] = {}
        tk = kwargs.get("topology_kind", "graph")
        self._topology_kind = TopologyKind.GRAPH

    def add_node(self, node: TopologyNode) -> bool:
        """Add a node to the topology"""
        self._nodes[node.node_id] = node
        return True

    def get_node(self, node_id: str) -> Optional[TopologyNode]:
        """Get a specific node"""
        return self._nodes.get(node_id)

    def remove_node(self, node_id: str) -> bool:
        """Remove a node from the topology"""
        if node_id in self._nodes:
            del self._nodes[node_id]
            return True
        return False

    def get_connected_nodes(self, node_id: str) -> List[TopologyNode]:
        """Get all nodes connected to a specific node"""
        node = self.get_node(node_id)
        if not node:
            return []
        return [self._nodes[nid] for nid in node.connections if nid in self._nodes]

    def get_all_nodes(self) -> List[TopologyNode]:
        """Get all nodes"""
        return list(self._nodes.values())

    @property
    def digest(self) -> str:
        """Get digest of topology"""
        import hashlib
        import json

        data = json.dumps(
            {nid: node.to_dict() for nid, node in self._nodes.items()}, sort_keys=True
        )
        return hashlib.sha256(data.encode()).hexdigest()


# Global topology manager
_topology_manager: Optional[RuntimeTopology] = None


def get_topology_manager() -> RuntimeTopology:
    """Get the global topology manager"""
    global _topology_manager
    if _topology_manager is None:
        _topology_manager = RuntimeTopology()
    return _topology_manager


__all__ = [
    "TopologyKind",
    "EdgeRelation",
    "LifecycleState",
    "NodeKind",
    "NodeTier",
    "RuntimeEdge",
    "RuntimeNode",
    "TopologyNode",
    "RuntimeTopology",
    "get_topology_manager",
]
