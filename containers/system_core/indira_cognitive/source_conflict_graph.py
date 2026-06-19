"""
INDIRA Source Conflict Graph - Knowledge Layer Component
Tracks and resolves conflicts between different knowledge sources
Per Rule 6 of the DIX VISION Tier-0 Production Implementation Contract
"""

import logging
from typing import Dict, List, Set, Tuple, Any, Optional
from datetime import datetime
from dataclasses import dataclass, field
from enum import Enum
from collections import defaultdict

logger = logging.getLogger(__name__)

class ConflictSeverity(Enum):
    """Severity levels for knowledge conflicts"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"

class ConflictType(Enum):
    """Types of conflicts between knowledge sources"""
    VALUE_CONFLICT = "value_conflict"
    TEMPORAL_CONFLICT = "temporal_conflict"
    LOGICAL_CONFLICT = "logical_conflict"
    SOURCE_CONFLICT = "source_conflict"
    CONFIDENCE_CONFLICT = "confidence_conflict"

@dataclass
class ConflictNode:
    """A node in the conflict graph representing a knowledge piece"""
    knowledge_id: str
    source: str
    value: Any
    confidence: float
    timestamp: datetime
    conflicts: Set[str] = field(default_factory=set)
    
@dataclass
class ConflictEdge:
    """An edge in the conflict graph representing a conflict relationship"""
    from_node: str
    to_node: str
    conflict_type: ConflictType
    severity: ConflictSeverity
    metadata: Dict[str, Any] = field(default_factory=dict)

@dataclass
class ConflictResolution:
    """Resolution strategy for a conflict"""
    conflict_id: str
    resolution_strategy: str
    resolution_value: Any
    confidence: float
    reasoning: str

class SourceConflictGraph:
    """
    Graph structure to track and resolve conflicts between knowledge sources
    Ensures belief lineage and evidence provenance per Rule 6
    """
    
    def __init__(self):
        self._nodes: Dict[str, ConflictNode] = {}  # knowledge_id -> ConflictNode
        self._edges: Dict[str, List[ConflictEdge]] = defaultdict(list)  # node_id -> edges
        self._resolution_history: List[ConflictResolution] = []
        self._confidence_threshold = 0.75  # minimum confidence for resolution
        
    def add_knowledge(self, knowledge_id: str, source: str, value: Any, 
                     confidence: float, timestamp: datetime) -> None:
        """Add a knowledge piece to the conflict graph"""
        node = ConflictNode(
            knowledge_id=knowledge_id,
            source=source,
            value=value,
            confidence=confidence,
            timestamp=timestamp
        )
        self._nodes[knowledge_id] = node
        self._detect_and_link_conflicts(knowledge_id)
        logger.info(f"Added knowledge node: {knowledge_id} from {source}")
    
    def _detect_and_link_conflicts(self, knowledge_id: str) -> None:
        """Detect conflicts with existing knowledge and create edges"""
        new_node = self._nodes[knowledge_id]
        
        for existing_id, existing_node in self._nodes.items():
            if existing_id == knowledge_id:
                continue
                
            conflict = self._detect_conflict(new_node, existing_node)
            if conflict:
                self._add_conflict_edge(knowledge_id, existing_id, conflict)
                existing_node.conflicts.add(knowledge_id)
                new_node.conflicts.add(existing_id)
    
    def _detect_conflict(self, node_a: ConflictNode, node_b: ConflictNode) -> Optional[ConflictEdge]:
        """Detect if two knowledge pieces conflict and return conflict edge"""
        # Value conflict check
        if self._is_value_conflict(node_a.value, node_b.value):
            severity = self._calculate_conflict_severity(node_a, node_b)
            return ConflictEdge(
                from_node=node_a.knowledge_id,
                to_node=node_b.knowledge_id,
                conflict_type=ConflictType.VALUE_CONFLICT,
                severity=severity,
                metadata={
                    "value_a": str(node_a.value),
                    "value_b": str(node_b.value)
                }
            )
        
        # Temporal conflict check (same knowledge at same time)
        if self._is_temporal_conflict(node_a, node_b):
            return ConflictEdge(
                from_node=node_a.knowledge_id,
                to_node=node_b.knowledge_id,
                conflict_type=ConflictType.TEMPORAL_CONFLICT,
                severity=ConflictSeverity.HIGH,
                metadata={
                    "timestamp_a": str(node_a.timestamp),
                    "timestamp_b": str(node_b.timestamp)
                }
            )
        
        # Confidence conflict check (highly confident conflicting info)
        if node_a.confidence > 0.8 and node_b.confidence > 0.8:
            if self._is_value_conflict(node_a.value, node_b.value):
                return ConflictEdge(
                    from_node=node_a.knowledge_id,
                    to_node=node_b.knowledge_id,
                    conflict_type=ConflictType.CONFIDENCE_CONFLICT,
                    severity=ConflictSeverity.CRITICAL,
                    metadata={
                        "confidence_a": node_a.confidence,
                        "confidence_b": node_b.confidence
                    }
                )
        
        return None
    
    def _is_value_conflict(self, value_a: Any, value_b: Any) -> bool:
        """Check if two values conflict (simplified check)"""
        try:
            if value_a == value_b:
                return False
            # For numeric values, check if they're significantly different
            if isinstance(value_a, (int, float)) and isinstance(value_b, (int, float)):
                return abs(value_a - value_b) / max(abs(value_a), abs(value_b)) > 0.10
            # For strings, check if they're different
            if isinstance(value_a, str) and isinstance(value_b, str):
                return value_a != value_b
            return True
        except (TypeError, ValueError):
            return True
    
    def _is_temporal_conflict(self, node_a: ConflictNode, node_b: ConflictNode) -> bool:
        """Check if two knowledge pieces have temporal conflict"""
        time_diff = abs((node_a.timestamp - node_b.timestamp).total_seconds())
        return time_diff < 1.0  # same second
    
    def _calculate_conflict_severity(self, node_a: ConflictNode, node_b: ConflictNode) -> ConflictSeverity:
        """Calculate conflict severity based on confidence and time"""
        avg_confidence = (node_a.confidence + node_b.confidence) / 2
        
        if avg_confidence > 0.9:
            return ConflictSeverity.CRITICAL
        elif avg_confidence > 0.75:
            return ConflictSeverity.HIGH
        elif avg_confidence > 0.60:
            return ConflictSeverity.MEDIUM
        else:
            return ConflictSeverity.LOW
    
    def _add_conflict_edge(self, from_id: str, to_id: str, edge: ConflictEdge) -> None:
        """Add a conflict edge to the graph"""
        self._edges[from_id].append(edge)
        logger.info(f"Added conflict edge: {from_id} -> {to_id} ({edge.conflict_type.value})")
    
    def resolve_conflicts(self, knowledge_id: str) -> List[ConflictResolution]:
        """Resolve conflicts for a given knowledge piece using conflict resolution strategies"""
        if knowledge_id not in self._nodes:
            return []
        
        node = self._nodes[knowledge_id]
        conflicts = []
        
        if not node.conflicts:
            return []
        
        for conflict_id in node.conflicts:
            if conflict_id not in self._nodes:
                continue
                
            other_node = self._nodes[conflict_id]
            edge = self._find_edge(knowledge_id, conflict_id)
            
            if not edge:
                continue
            
            resolution = self._apply_resolution_strategy(node, other_node, edge)
            if resolution:
                conflicts.append(resolution)
                self._resolution_history.append(resolution)
        
        return conflicts
    
    def _find_edge(self, from_id: str, to_id: str) -> Optional[ConflictEdge]:
        """Find the edge between two nodes"""
        for edge in self._edges[from_id]:
            if edge.to_node == to_id:
                return edge
        return None
    
    def _apply_resolution_strategy(self, node_a: ConflictNode, node_b: ConflictNode, 
                             edge: ConflictEdge) -> Optional[ConflictResolution]:
        """Apply resolution strategy based on conflict type and confidence"""
        
        # Rule 6 Acceptance: Every belief traceable to evidence
        # Higher confidence source wins
        if node_a.confidence > node_b.confidence and node_a.confidence > self._confidence_threshold:
            resolution_value = node_a.value
            confidence = node_a.confidence
            reasoning = f"Resolved by higher confidence: {node_a.source} ({node_a.confidence:.2f}) vs {node_b.source} ({node_b.confidence:.2f})"
        elif node_b.confidence > node_a.confidence and node_b.confidence > self._confidence_threshold:
            resolution_value = node_b.value
            confidence = node_b.confidence
            reasoning = f"Resolved by higher confidence: {node_b.source} ({node_b.confidence:.2f}) vs {node_a.source} ({node_a.confidence:.2f})"
        else:
            # If confidence is similar, prefer more recent knowledge
            if node_a.timestamp > node_b.timestamp:
                resolution_value = node_a.value
                confidence = node_a.confidence
                reasoning = f"Resolved by recency: {node_a.timestamp} vs {node_b.timestamp}"
            else:
                resolution_value = node_b.value
                confidence = node_b.confidence
                reasoning = f"Resolved by recency: {node_b.timestamp} vs {node_a.timestamp}"
        
        return ConflictResolution(
            conflict_id=f"{node_a.knowledge_id}_vs_{node_b.knowledge_id}",
            resolution_strategy="confidence_priority",
            resolution_value=resolution_value,
            confidence=confidence,
            reasoning=reasoning
        )
    
    def get_conflict_graph_summary(self) -> Dict[str, Any]:
        """Get summary of the current conflict graph state"""
        return {
            "total_nodes": len(self._nodes),
            "total_edges": sum(len(edges) for edges in self._edges.values()),
            "conflicted_nodes": len([node for node in self._nodes.values() if node.conflicts]),
            "high_confidence_nodes": len([node for node in self._nodes.values() if node.confidence > 0.8]),
            "resolutions_attempted": len(self._resolution_history),
            "timestamp": datetime.utcnow().isoformat()
        }
    
    def get_conflicts_by_severity(self, severity: ConflictSeverity) -> List[ConflictEdge]:
        """Get all conflicts of a specific severity level"""
        conflicts = []
        for edge_list in self._edges.values():
            for edge in edge_list:
                if edge.severity == severity:
                    conflicts.append(edge)
        return conflicts
    
    def get_node_conflicts(self, knowledge_id: str) -> List[ConflictEdge]:
        """Get all conflicts for a specific knowledge node"""
        if knowledge_id not in self._edges:
            return []
        return self._edges[knowledge_id]
    
    def prune_old_knowledge(self, older_than_hours: int = 24) -> int:
        """Remove knowledge nodes older than specified hours"""
        cutoff = datetime.utcnow().timestamp() - (older_than_hours * 3600)
        nodes_to_remove = []
        
        for knowledge_id, node in self._nodes.items():
            if node.timestamp.timestamp() < cutoff:
                nodes_to_remove.append(knowledge_id)
                # Remove edges connected to this node
                if knowledge_id in self._edges:
                    del self._edges[knowledge_id]
                # Remove edges pointing to this node
                for edge_list in self._edges.values():
                    self._edges[edge_list] = [e for e in edge_list if e.to_node != knowledge_id]
        
        for node_id in nodes_to_remove:
            del self._nodes[node_id]
        
        logger.info(f"Pruned {len(nodes_to_remove)} old knowledge nodes")
        return len(nodes_to_remove)