"""
state.source_conflict_graph
DIX VISION v42.2 — Source Conflict Graph

Priority 2 Implementation: Knowledge Layer Completion

Tracks and resolves conflicts between different knowledge sources.
Provides a graph-based approach to identifying, analyzing, and resolving
conflicting information from multiple sources.
"""

from __future__ import annotations

import logging
import threading
from collections import defaultdict
from datetime import datetime
from typing import Any, Dict, List, Optional, Set, Tuple
from dataclasses import dataclass, field
from enum import Enum

logger = logging.getLogger(__name__)


class ConflictSeverity(Enum):
    """Severity levels for source conflicts."""
    CRITICAL = "CRITICAL"
    HIGH = "HIGH"
    MEDIUM = "MEDIUM"
    LOW = "LOW"


class ConflictType(Enum):
    """Types of conflicts between sources."""
    FACTUAL = "FACTUAL"  # Direct contradiction of facts
    TEMPORAL = "TEMPORAL"  # Contradiction in timing/timestamps
    CAUSAL = "CAUSAL"  # Contradiction in causal relationships
    SEMANTIC = "SEMANTIC"  # Interpretation disagreements
    CONTEXTUAL = "CONTEXTUAL"  # Context-dependent contradictions


@dataclass
class ConflictNode:
    """A node in the conflict graph representing a source statement."""
    source_id: str
    statement_id: str
    content: str
    timestamp: str
    confidence: float
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class ConflictEdge:
    """An edge in the conflict graph representing a conflict between nodes."""
    source_node: ConflictNode
    target_node: ConflictNode
    conflict_type: ConflictType
    severity: ConflictSeverity
    description: str
    detected_at: str = ""
    resolved: bool = False
    resolution: Optional[str] = None


@dataclass
class ConflictResolution:
    """Resolution strategy for a conflict."""
    resolution_type: str  # "source_trust", "time_freshness", "confidence", "manual"
    chosen_node: ConflictNode
    rejected_nodes: List[ConflictNode]
    rationale: str
    resolved_at: str = ""


class SourceConflictGraph:
    """
    Graph-based system for tracking and resolving conflicts between knowledge sources.
    
    Responsibilities:
    - Detect conflicts between knowledge sources
    - Build conflict graph structure
    - Analyze conflict severity and type
    - Provide resolution strategies
    - Track resolution history
    - Maintain conflict statistics
    """
    
    def __init__(self):
        self._lock = threading.Lock()
        
        # Graph structure
        self._nodes: Dict[str, ConflictNode] = {}  # statement_id -> ConflictNode
        self._edges: Dict[str, List[ConflictEdge]] = defaultdict(list)  # source_id -> List[ConflictEdge]
        self._conflict_groups: Dict[str, Set[str]] = defaultdict(set)  # group_id -> set of statement_ids
        
        # Resolution history
        self._resolutions: List[ConflictResolution] = []
        
        # Source trust scores
        self._source_trust: Dict[str, float] = {}
        
        # Conflict statistics
        self._conflict_stats = {
            "total_conflicts": 0,
            "by_severity": defaultdict(int),
            "by_type": defaultdict(int),
            "resolved": 0,
            "unresolved": 0
        }
        
        logger.info("[SOURCE_CONFLICT_GRAPH] Source Conflict Graph initialized")
    
    def add_source_statement(
        self,
        source_id: str,
        statement_id: str,
        content: str,
        confidence: float,
        metadata: Optional[Dict[str, Any]] = None
    ) -> ConflictNode:
        """
        Add a source statement to the conflict graph and check for conflicts.
        
        Args:
            source_id: Identifier for the knowledge source
            statement_id: Unique identifier for the statement
            content: The statement content
            confidence: Confidence score for the statement (0.0 to 1.0)
            metadata: Additional metadata about the statement
            
        Returns:
            The created ConflictNode
        """
        with self._lock:
            node = ConflictNode(
                source_id=source_id,
                statement_id=statement_id,
                content=content,
                timestamp=datetime.utcnow().isoformat(),
                confidence=confidence,
                metadata=metadata or {}
            )
            
            # Add node to graph
            self._nodes[statement_id] = node
            
            # Check for conflicts with existing nodes
            conflicts = self._detect_conflicts(node)
            
            # Add conflict edges
            for conflict in conflicts:
                self._edges[statement_id].append(conflict)
                self._conflict_stats["total_conflicts"] += 1
                self._conflict_stats["by_severity"][conflict.severity.value] += 1
                self._conflict_stats["by_type"][conflict.conflict_type.value] += 1
                self._conflict_stats["unresolved"] += 1
            
            logger.info(f"[SOURCE_CONFLICT_GRAPH] Added statement {statement_id} from {source_id}, detected {len(conflicts)} conflicts")
            
            return node
    
    def _detect_conflicts(self, new_node: ConflictNode) -> List[ConflictEdge]:
        """Detect conflicts between new node and existing nodes."""
        conflicts = []
        
        for existing_id, existing_node in self._nodes.items():
            if existing_id == new_node.statement_id:
                continue
            
            # Check for factual contradictions
            if self._check_factual_conflict(new_node, existing_node):
                conflicts.append(ConflictEdge(
                    source_node=new_node,
                    target_node=existing_node,
                    conflict_type=ConflictType.FACTUAL,
                    severity=self._determine_severity(new_node, existing_node),
                    description=f"Factual contradiction between statements",
                    detected_at=str(datetime.utcnow())
                ))
            
            # Check for temporal conflicts
            if self._check_temporal_conflict(new_node, existing_node):
                conflicts.append(ConflictEdge(
                    source_node=new_node,
                    target_node=existing_node,
                    conflict_type=ConflictType.TEMPORAL,
                    severity=ConflictSeverity.MEDIUM,
                    description=f"Temporal contradiction between statements",
                    detected_at=str(datetime.utcnow())
                ))
            
            # Check for semantic conflicts
            if self._check_semantic_conflict(new_node, existing_node):
                conflicts.append(ConflictEdge(
                    source_node=new_node,
                    target_node=existing_node,
                    conflict_type=ConflictType.SEMANTIC,
                    severity=ConflictSeverity.LOW,
                    description=f"Semantic contradiction between statements",
                    detected_at=str(datetime.utcnow())
                ))
        
        return conflicts
    
    def _check_factual_conflict(self, node1: ConflictNode, node2: ConflictNode) -> bool:
        """Check for factual contradictions between statements."""
        # Simple keyword-based contradiction detection
        # In production, this would use more sophisticated NLP
        
        contradictory_pairs = [
            ("increase", "decrease"),
            ("rise", "fall"),
            ("up", "down"),
            ("positive", "negative"),
            ("bullish", "bearish"),
            ("expansion", "contraction")
        ]
        
        content1_lower = node1.content.lower()
        content2_lower = node2.content.lower()
        
        for word1, word2 in contradictory_pairs:
            if word1 in content1_lower and word2 in content2_lower:
                return True
            if word2 in content1_lower and word1 in content2_lower:
                return True
        
        return False
    
    def _check_temporal_conflict(self, node1: ConflictNode, node2: ConflictNode) -> bool:
        """Check for temporal contradictions between statements."""
        # Check if timestamps are significantly different for the same event
        try:
            time1 = datetime.fromisoformat(node1.timestamp)
            time2 = datetime.fromisoformat(node2.timestamp)
            
            # If timestamps differ by more than 1 hour, flag as potential conflict
            time_diff = abs((time1 - time2).total_seconds())
            if time_diff > 3600:  # 1 hour
                return True
        except ValueError:
            pass
        
        return False
    
    def _check_semantic_conflict(self, node1: ConflictNode, node2: ConflictNode) -> bool:
        """Check for semantic contradictions between statements."""
        # Check for semantic opposites in the same context
        # This is a simplified implementation
        
        content1_lower = node1.content.lower()
        content2_lower = node2.content.lower()
        
        # Check for contradictory statements about the same entity
        # Example: "AAPL is strong" vs "AAPL is weak"
        entities = self._extract_entities(content1_lower)
        if entities:
            for entity in entities:
                if entity in content2_lower:
                    # Both statements talk about the same entity
                    # Check for contradictory adjectives
                    if "strong" in content1_lower and "weak" in content2_lower:
                        return True
                    if "weak" in content1_lower and "strong" in content2_lower:
                        return True
        
        return False
    
    def _extract_entities(self, text: str) -> List[str]:
        """Extract potential entities from text (simplified)."""
        # In production, this would use NER
        # For now, just return empty list
        return []
    
    def _determine_severity(self, node1: ConflictNode, node2: ConflictNode) -> ConflictSeverity:
        """Determine severity of a conflict based on node characteristics."""
        # High confidence contradictions are more severe
        avg_confidence = (node1.confidence + node2.confidence) / 2
        
        if avg_confidence > 0.8:
            return ConflictSeverity.CRITICAL
        elif avg_confidence > 0.6:
            return ConflictSeverity.HIGH
        elif avg_confidence > 0.4:
            return ConflictSeverity.MEDIUM
        else:
            return ConflictSeverity.LOW
    
    def resolve_conflict(
        self,
        statement_id: str,
        resolution_strategy: str = "confidence"
    ) -> Optional[ConflictResolution]:
        """
        Resolve conflicts for a statement using the specified strategy.
        
        Args:
            statement_id: The statement to resolve conflicts for
            resolution_strategy: Strategy to use ("confidence", "source_trust", "time_freshness", "manual")
            
        Returns:
            ConflictResolution if conflicts were resolved, None otherwise
        """
        with self._lock:
            if statement_id not in self._edges:
                logger.warning(f"[SOURCE_CONFLICT_GRAPH] No conflicts found for statement {statement_id}")
                return None
            
            conflicts = self._edges[statement_id]
            if not conflicts:
                return None
            
            # Get all conflicting nodes
            all_nodes = set()
            all_nodes.add(self._nodes[statement_id])
            for conflict in conflicts:
                all_nodes.add(conflict.target_node)
            
            # Apply resolution strategy
            if resolution_strategy == "confidence":
                resolution = self._resolve_by_confidence(all_nodes)
            elif resolution_strategy == "source_trust":
                resolution = self._resolve_by_source_trust(all_nodes)
            elif resolution_strategy == "time_freshness":
                resolution = self._resolve_by_time_freshness(all_nodes)
            elif resolution_strategy == "manual":
                resolution = self._resolve_manually(all_nodes)
            else:
                logger.error(f"[SOURCE_CONFLICT_GRAPH] Unknown resolution strategy: {resolution_strategy}")
                return None
            
            if resolution:
                # Mark conflicts as resolved
                for conflict in conflicts:
                    conflict.resolved = True
                    conflict.resolution = resolution.rationale
                
                # Update statistics
                self._conflict_stats["resolved"] += len(conflicts)
                self._conflict_stats["unresolved"] -= len(conflicts)
                
                # Store resolution history
                self._resolutions.append(resolution)
                
                logger.info(f"[SOURCE_CONFLICT_GRAPH] Resolved {len(conflicts)} conflicts for {statement_id} using {resolution_strategy}")
            
            return resolution
    
    def _resolve_by_confidence(self, nodes: Set[ConflictNode]) -> ConflictResolution:
        """Resolve conflict by choosing the node with highest confidence."""
        chosen = max(nodes, key=lambda n: n.confidence)
        rejected = [n for n in nodes if n != chosen]
        
        return ConflictResolution(
            resolution_type="confidence",
            chosen_node=chosen,
            rejected_nodes=rejected,
            rationale=f"Chose statement with highest confidence ({chosen.confidence})",
            resolved_at=str(datetime.utcnow())
        )
    
    def _resolve_by_source_trust(self, nodes: Set[ConflictNode]) -> ConflictResolution:
        """Resolve conflict by choosing from the most trusted source."""
        # Get trust scores for sources
        source_scores = {}
        for node in nodes:
            source_scores[node.source_id] = self._source_trust.get(node.source_id, 0.5)
        
        # Choose node from highest-trusted source
        chosen = max(nodes, key=lambda n: source_scores.get(n.source_id, 0.5))
        rejected = [n for n in nodes if n != chosen]
        
        return ConflictResolution(
            resolution_type="source_trust",
            chosen_node=chosen,
            rejected_nodes=rejected,
            rationale=f"Chose statement from most trusted source ({chosen.source_id} with trust {source_scores[chosen.source_id]})",
            resolved_at=str(datetime.utcnow())
        )
    
    def _resolve_by_time_freshness(self, nodes: Set[ConflictNode]) -> ConflictResolution:
        """Resolve conflict by choosing the most recent statement."""
        def get_timestamp(node: ConflictNode) -> datetime:
            try:
                return datetime.fromisoformat(node.timestamp)
            except ValueError:
                return datetime.min
        
        chosen = max(nodes, key=get_timestamp)
        rejected = [n for n in nodes if n != chosen]
        
        return ConflictResolution(
            resolution_type="time_freshness",
            chosen_node=chosen,
            rejected_nodes=rejected,
            rationale=f"Chose most recent statement (timestamp: {chosen.timestamp})",
            resolved_at=str(datetime.utcnow())
        )
    
    def _resolve_manually(self, nodes: Set[ConflictNode]) -> ConflictResolution:
        """Manual resolution (placeholder for human intervention)."""
        # For manual resolution, we'd need a different interface
        # For now, just choose the first node as placeholder
        chosen = list(nodes)[0]
        rejected = [n for n in nodes if n != chosen]
        
        return ConflictResolution(
            resolution_type="manual",
            chosen_node=chosen,
            rejected_nodes=rejected,
            rationale="Manual resolution required (placeholder)",
            resolved_at=str(datetime.utcnow())
        )
    
    def update_source_trust(self, source_id: str, trust_score: float) -> None:
        """Update trust score for a source."""
        with self._lock:
            self._source_trust[source_id] = max(0.0, min(1.0, trust_score))
            logger.info(f"[SOURCE_CONFLICT_GRAPH] Updated source trust: {source_id} -> {trust_score}")
    
    def get_conflicts_for_statement(self, statement_id: str) -> List[ConflictEdge]:
        """Get all conflicts for a specific statement."""
        with self._lock:
            return self._edges.get(statement_id, [])
    
    def get_conflict_statistics(self) -> Dict[str, Any]:
        """Get statistics about conflicts in the graph."""
        with self._lock:
            return {
                "total_nodes": len(self._nodes),
                "total_conflicts": self._conflict_stats["total_conflicts"],
                "resolved": self._conflict_stats["resolved"],
                "unresolved": self._conflict_stats["unresolved"],
                "by_severity": dict(self._conflict_stats["by_severity"]),
                "by_type": dict(self._conflict_stats["by_type"]),
                "resolution_history_size": len(self._resolutions)
            }
    
    def get_resolution_history(self) -> List[ConflictResolution]:
        """Get history of conflict resolutions."""
        with self._lock:
            return self._resolutions.copy()


# Singleton instance
_source_conflict_graph: Optional[SourceConflictGraph] = None
_source_conflict_graph_lock = threading.Lock()

def get_source_conflict_graph() -> SourceConflictGraph:
    """Get the singleton source conflict graph instance."""
    global _source_conflict_graph
    if _source_conflict_graph is None:
        with _source_conflict_graph_lock:
            if _source_conflict_graph is None:
                _source_conflict_graph = SourceConflictGraph()
    return _source_conflict_graph


__all__ = [
    "ConflictSeverity",
    "ConflictType",
    "ConflictNode",
    "ConflictEdge",
    "ConflictResolution",
    "SourceConflictGraph",
    "get_source_conflict_graph",
]