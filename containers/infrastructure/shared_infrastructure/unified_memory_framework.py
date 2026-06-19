"""
shared_infrastructure.unified_memory_framework
DIX VISION v42.2 — Unified Memory Framework

Integrates all memory types with vector + knowledge graph hybrid approach.
Supports cognitive ledger, execution memory, market memory, working memory, and long-term memory.
"""

from __future__ import annotations

import logging
from datetime import datetime
from typing import Any, Dict, List, Optional
from dataclasses import dataclass, field
from abc import ABC, abstractmethod
import threading

from shared_infrastructure.knowledge_graph_adapter import (
    KnowledgeGraphAdapterInterface,
    KnowledgeNode,
    KnowledgeEdge,
    NodeType,
)
from shared_infrastructure.vector_database_adapter import (
    VectorDatabaseAdapterInterface,
    VectorRecord,
    VectorMemoryType,
    SemanticMemoryRetriever,
)

logger = logging.getLogger(__name__)


class MemoryType:
    """Types of memory in the unified framework."""
    COGNITIVE_LEDGER = "cognitive_ledger"
    EXECUTION_MEMORY = "execution_memory"
    MARKET_MEMORY = "market_memory"
    WORKING_MEMORY = "working_memory"
    LONG_TERM_MEMORY = "long_term_memory"
    EPISODIC_MEMORY = "episodic_memory"
    SEMANTIC_MEMORY = "semantic_memory"
    PROCEDURAL_MEMORY = "procedural_memory"
    SHORT_TERM_MEMORY = "short_term_memory"
    CUSTOM = "custom"


@dataclass
class MemoryItem:
    """A memory item in the unified framework."""
    memory_id: str
    memory_type: MemoryType
    content: Dict[str, Any]
    importance: float = 0.5  # 0.0 to 1.0
    retrieval_count: int = 0
    last_accessed: datetime = field(default_factory=datetime.utcnow)
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: datetime = field(default_factory=datetime.utcnow)
    expires_at: Optional[datetime] = None
    tags: List[str] = field(default_factory=list)
    embeddings: Optional[List[float]] = None
    knowledge_graph_node_id: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class MemoryRetrievalResult:
    """Result from memory retrieval."""
    memory_id: str
    memory_type: MemoryType
    content: Dict[str, Any]
    relevance_score: float
    temporal_score: float
    combined_score: float
    source: str  # vector | knowledge_graph | hybrid
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class MemoryConsolidationRequest:
    """Request for memory consolidation."""
    consolidation_id: str
    source_memory_ids: List[str]
    target_memory_type: MemoryType
    consolidation_strategy: str = "merge"  # merge | aggregate | summarize
    metadata: Dict[str, Any] = field(default_factory=dict)


class UnifiedMemoryFrameworkInterface(ABC):
    """Interface for unified memory operations."""
    
    @abstractmethod
    def store(
        self,
        memory_type: MemoryType,
        content: Dict[str, Any],
        importance: float = 0.5,
        tags: List[str] = None,
        expires_after: Optional[float] = None
    ) -> str:
        """Store a memory item."""
        pass
    
    @abstractmethod
    def retrieve(
        self,
        query: str,
        memory_types: Optional[List[MemoryType]] = None,
        limit: int = 10,
        importance_threshold: float = 0.0
    ) -> List[MemoryRetrievalResult]:
        """Retrieve memory items."""
        pass
    
    @abstractmethod
    def get_memory(self, memory_id: str) -> Optional[MemoryItem]:
        """Get a memory item by ID."""
        pass
    
    @abstractmethod
    def update_memory(
        self,
        memory_id: str,
        content: Optional[Dict[str, Any]] = None,
        importance: Optional[float] = None,
        tags: Optional[List[str]] = None
    ) -> bool:
        """Update a memory item."""
        pass
    
    @abstractmethod
    def delete_memory(self, memory_id: str) -> bool:
        """Delete a memory item."""
        pass
    
    @abstractmethod
    def consolidate_memories(self, request: MemoryConsolidationRequest) -> bool:
        """Consolidate memory items."""
        pass
    
    @abstractmethod
    def cleanup_expired_memories(self) -> int:
        """Clean up expired memory items."""
        pass
    
    @abstractmethod
    def get_statistics(self) -> Dict[str, Any]:
        """Get memory framework statistics."""
        pass


class UnifiedMemoryFramework(UnifiedMemoryFrameworkInterface):
    """
    Concrete implementation of unified memory framework.
    Integrates vector database and knowledge graph for hybrid retrieval.
    """
    
    def __init__(
        self,
        vector_adapter: Optional[VectorDatabaseAdapterInterface] = None,
        knowledge_graph_adapter: Optional[KnowledgeGraphAdapterInterface] = None
    ):
        self._lock = threading.Lock()
        
        # Connect to shared infrastructure
        self._vector_adapter = vector_adapter
        self._knowledge_graph_adapter = knowledge_graph_adapter
        self._semantic_retriever: Optional[SemanticMemoryRetriever] = None
        
        if self._vector_adapter:
            self._semantic_retriever = SemanticMemoryRetriever(self._vector_adapter)
        
        # In-memory storage for unified access
        self._memories: Dict[str, MemoryItem] = {}
        
        # Memory type-specific storage
        self._memory_by_type: Dict[MemoryType, List[str]] = {}
        
        # Working memory (fast access, limited size)
        self._working_memory: List[str] = []
        self._working_memory_limit = 100
        
        # Statistics
        self._store_count = 0
        self._retrieve_count = 0
        self._consolidation_count = 0
        
        logger.info("[UNIFIED_MEMORY] Framework initialized")
    
    def store(
        self,
        memory_type: MemoryType,
        content: Dict[str, Any],
        importance: float = 0.5,
        tags: List[str] = None,
        expires_after: Optional[float] = None
    ) -> str:
        """Store a memory item."""
        try:
            memory_id = f"memory_{memory_type}_{int(datetime.utcnow().timestamp())}"
            
            # Calculate expiration time
            expires_at = None
            if expires_after:
                expires_at = datetime.fromtimestamp(datetime.utcnow().timestamp() + expires_after)
            
            # Create memory item
            memory = MemoryItem(
                memory_id=memory_id,
                memory_type=memory_type,
                content=content,
                importance=importance,
                tags=tags or [],
                expires_at=expires_at
            )
            
            # Store in unified memory
            with self._lock:
                self._memories[memory_id] = memory
                
                # Add to memory type index
                if memory_type not in self._memory_by_type:
                    self._memory_by_type[memory_type] = []
                self._memory_by_type[memory_type].append(memory_id)
                
                # Add to working memory if short-term or working memory
                if memory_type in [MemoryType.WORKING_MEMORY, MemoryType.SHORT_TERM_MEMORY]:
                    self._working_memory.append(memory_id)
                    if len(self._working_memory) > self._working_memory_limit:
                        # Remove oldest
                        oldest = self._working_memory.pop(0)
                        if oldest in self._memories:
                            del self._memories[oldest]
                
                self._store_count += 1
            
            # Store in vector database for semantic search
            if self._semantic_retriever:
                try:
                    # Convert content to text for embedding
                    text_content = str(content)
                    
                    # Map memory type to vector memory type
                    vector_memory_type = self._map_memory_to_vector_type(memory_type)
                    
                    self._semantic_retriever.store(
                        text=text_content,
                        memory_type=vector_memory_type,
                        metadata={"memory_id": memory_id, "memory_type": memory_type}
                    )
                    
                    # Store the vector record ID in memory metadata
                    memory.metadata["vector_record_id"] = memory_id  # Simplified
                    
                except Exception as e:
                    logger.warning(f"[UNIFIED_MEMORY] Vector storage failed: {e}")
            
            # Store in knowledge graph for relationships
            if self._knowledge_graph_adapter:
                try:
                    node = KnowledgeNode(
                        node_id=memory_id,
                        node_type=NodeType.MEMORY,
                        label=f"{memory_type}",
                        properties={
                            "memory_type": memory_type,
                            "importance": importance,
                            "tags": tags or []
                        }
                    )
                    
                    self._knowledge_graph_adapter.add_node(node)
                    memory.knowledge_graph_node_id = memory_id  # Simplified
                    
                except Exception as e:
                    logger.warning(f"[UNIFIED_MEMORY] Knowledge graph storage failed: {e}")
            
            logger.debug(f"[UNIFIED_MEMORY] Stored memory: {memory_id} ({memory_type})")
            return memory_id
            
        except Exception as e:
            logger.error(f"[UNIFIED_MEMORY] Storage failed: {e}")
            return ""
    
    def _map_memory_to_vector_type(self, memory_type: MemoryType) -> VectorMemoryType:
        """Map memory type to vector memory type."""
        mapping = {
            MemoryType.SEMANTIC_MEMORY: VectorMemoryType.SEMANTIC,
            MemoryType.EPISODIC_MEMORY: VectorMemoryType.EPISODIC,
            MemoryType.PROCEDURAL_MEMORY: VectorMemoryType.PROCEDURAL,
            MemoryType.WORKING_MEMORY: VectorMemoryType.WORKING,
            MemoryType.LONG_TERM_MEMORY: VectorMemoryType.LONG_TERM,
        }
        return mapping.get(memory_type, VectorMemoryType.CUSTOM)
    
    def retrieve(
        self,
        query: str,
        memory_types: Optional[List[MemoryType]] = None,
        limit: int = 10,
        importance_threshold: float = 0.0
    ) -> List[MemoryRetrievalResult]:
        """Retrieve memory items using hybrid approach."""
        try:
            results = []
            
            # Try semantic search via vector database
            if self._semantic_retriever:
                try:
                    # Map memory types to vector memory types
                    vector_memory_types = None
                    if memory_types:
                        vector_memory_types = [
                            self._map_memory_to_vector_type(mt)
                            for mt in memory_types
                        ]
                    
                    vector_results = self._semantic_retriever.retrieve(
                        query_text=query,
                        memory_types=vector_memory_types,
                        limit=limit,
                        score_threshold=0.3
                    )
                    
                    # Convert vector results to memory retrieval results
                    for vr in vector_results:
                        memory_id = vr.payload.get("memory_id")
                        if memory_id in self._memories:
                            memory = self._memories[memory_id]
                            
                            # Apply importance threshold
                            if memory.importance >= importance_threshold:
                                # Calculate scores
                                relevance_score = vr.similarity
                                temporal_score = self._calculate_temporal_score(memory)
                                combined_score = (relevance_score * 0.7) + (temporal_score * 0.3)
                                
                                results.append(MemoryRetrievalResult(
                                    memory_id=memory_id,
                                    memory_type=memory.memory_type,
                                    content=memory.content,
                                    relevance_score=relevance_score,
                                    temporal_score=temporal_score,
                                    combined_score=combined_score,
                                    source="vector",
                                    metadata=memory.metadata
                                ))
                                
                                # Update retrieval count
                                with self._lock:
                                    memory.retrieval_count += 1
                                    memory.last_accessed = datetime.utcnow()
                    
                except Exception as e:
                    logger.warning(f"[UNIFIED_MEMORY] Semantic retrieval failed: {e}")
            
            # Try knowledge graph search
            if self._knowledge_graph_adapter and len(results) < limit:
                try:
                    from shared_infrastructure.knowledge_graph_adapter import KnowledgeQuery
                    
                    kg_query = KnowledgeQuery(
                        query_id=f"memory_query_{int(datetime.utcnow().timestamp())}",
                        query_type="node_query",
                        parameters={"label": query},
                        limit=limit - len(results)
                    )
                    
                    kg_results = self._knowledge_graph_adapter.query(kg_query)
                    
                    for node in kg_results.nodes:
                        memory_id = node.node_id
                        if memory_id in self._memories:
                            memory = self._memories[memory_id]
                            
                            # Apply importance threshold
                            if memory.importance >= importance_threshold:
                                # Calculate scores
                                relevance_score = 0.6  # Knowledge graph relevance
                                temporal_score = self._calculate_temporal_score(memory)
                                combined_score = (relevance_score * 0.5) + (temporal_score * 0.5)
                                
                                results.append(MemoryRetrievalResult(
                                    memory_id=memory_id,
                                    memory_type=memory.memory_type,
                                    content=memory.content,
                                    relevance_score=relevance_score,
                                    temporal_score=temporal_score,
                                    combined_score=combined_score,
                                    source="knowledge_graph",
                                    metadata=memory.metadata
                                ))
                                
                                # Update retrieval count
                                with self._lock:
                                    memory.retrieval_count += 1
                                    memory.last_accessed = datetime.utcnow()
                    
                except Exception as e:
                    logger.warning(f"[UNIFIED_MEMORY] Knowledge graph retrieval failed: {e}")
            
            # Sort by combined score
            results.sort(key=lambda x: x.combined_score, reverse=True)
            
            # Limit results
            results = results[:limit]
            
            # Update statistics
            with self._lock:
                self._retrieve_count += 1
            
            logger.info(f"[UNIFIED_MEMORY] Retrieved {len(results)} memories for: {query[:50]}...")
            
            return results
            
        except Exception as e:
            logger.error(f"[UNIFIED_MEMORY] Retrieval failed: {e}")
            return []
    
    def _calculate_temporal_score(self, memory: MemoryItem) -> float:
        """Calculate temporal score based on recency and access frequency."""
        try:
            # Time decay factor (more recent = higher score)
            time_diff = (datetime.utcnow() - memory.created_at).total_seconds()
            time_decay = 1.0 / (1.0 + time_diff / 86400.0)  # Daily decay
            
            # Access frequency factor (more accessed = higher score)
            access_boost = min(memory.retrieval_count / 100.0, 0.3)
            
            # Importance factor
            importance_factor = memory.importance * 0.5
            
            # Combined temporal score
            temporal_score = (time_decay * 0.5) + access_boost + importance_factor
            return min(1.0, temporal_score)
            
        except Exception as e:
            logger.warning(f"[UNIFIED_MEMORY] Temporal score calculation failed: {e}")
            return 0.5
    
    def get_memory(self, memory_id: str) -> Optional[MemoryItem]:
        """Get a memory item by ID."""
        with self._lock:
            return self._memories.get(memory_id)
    
    def update_memory(
        self,
        memory_id: str,
        content: Optional[Dict[str, Any]] = None,
        importance: Optional[float] = None,
        tags: Optional[List[str]] = None
    ) -> bool:
        """Update a memory item."""
        with self._lock:
            memory = self._memories.get(memory_id)
            if not memory:
                return False
            
            if content is not None:
                memory.content.update(content)
            
            if importance is not None:
                memory.importance = importance
            
            if tags is not None:
                memory.tags = tags
            
            memory.updated_at = datetime.utcnow()
            
            logger.debug(f"[UNIFIED_MEMORY] Updated memory: {memory_id}")
            return True
    
    def delete_memory(self, memory_id: str) -> bool:
        """Delete a memory item."""
        with self._lock:
            if memory_id not in self._memories:
                return False
            
            memory = self._memories[memory_id]
            
            # Remove from memory type index
            if memory.memory_type in self._memory_by_type:
                self._memory_by_type[memory.memory_type] = [
                    mid for mid in self._memory_by_type[memory.memory_type]
                    if mid != memory_id
                ]
            
            # Remove from working memory
            if memory_id in self._working_memory:
                self._working_memory.remove(memory_id)
            
            # Delete from unified memory
            del self._memories[memory_id]
            
            # Delete from vector database
            if self._vector_adapter:
                try:
                    self._vector_adapter.delete_record(memory_id)
                except Exception as e:
                    logger.warning(f"[UNIFIED_MEMORY] Vector deletion failed: {e}")
            
            # Delete from knowledge graph
            if self._knowledge_graph_adapter:
                try:
                    self._knowledge_graph_adapter.delete_node(memory_id)
                except Exception as e:
                    logger.warning(f"[UNIFIED_MEMORY] Knowledge graph deletion failed: {e}")
            
            logger.debug(f"[UNIFIED_MEMORY] Deleted memory: {memory_id}")
            return True
    
    def consolidate_memories(self, request: MemoryConsolidationRequest) -> bool:
        """Consolidate memory items."""
        try:
            # Get source memories
            source_memories = []
            for memory_id in request.source_memory_ids:
                memory = self.get_memory(memory_id)
                if memory:
                    source_memories.append(memory)
            
            if not source_memories:
                logger.warning("[UNIFIED_MEMORY] No source memories found for consolidation")
                return False
            
            # Consolidate based on strategy
            if request.consolidation_strategy == "merge":
                consolidated_content = {}
                for memory in source_memories:
                    consolidated_content.update(memory.content)
            elif request.consolidation_strategy == "aggregate":
                # Simple aggregation
                consolidated_content = {
                    "source_count": len(source_memories),
                    "average_importance": sum(m.importance for m in source_memories) / len(source_memories),
                    "source_ids": [m.memory_id for m in source_memories]
                }
            elif request.consolidation_strategy == "summarize":
                consolidated_content = {
                    "summary": f"Consolidated from {len(source_memories)} memories",
                    "source_ids": [m.memory_id for m in source_memories]
                }
            else:
                consolidated_content = {}
            
            # Calculate consolidated importance
            avg_importance = sum(m.importance for m in source_memories) / len(source_memories)
            
            # Store consolidated memory
            consolidated_id = self.store(
                memory_type=request.target_memory_type,
                content=consolidated_content,
                importance=avg_importance,
                tags=["consolidated"]
            )
            
            # Delete source memories
            for memory_id in request.source_memory_ids:
                self.delete_memory(memory_id)
            
            # Update statistics
            with self._lock:
                self._consolidation_count += 1
            
            logger.info(f"[UNIFIED_MEMORY] Consolidated memories: {consolidated_id}")
            return True
            
        except Exception as e:
            logger.error(f"[UNIFIED_MEMORY] Consolidation failed: {e}")
            return False
    
    def cleanup_expired_memories(self) -> int:
        """Clean up expired memory items."""
        with self._lock:
            expired_ids = []
            current_time = datetime.utcnow()
            
            for memory_id, memory in self._memories.items():
                if memory.expires_at and current_time > memory.expires_at:
                    expired_ids.append(memory_id)
            
            # Delete expired memories
            for memory_id in expired_ids:
                self.delete_memory(memory_id)
            
            logger.info(f"[UNIFIED_MEMORY] Cleaned up {len(expired_ids)} expired memories")
            return len(expired_ids)
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get memory framework statistics."""
        with self._lock:
            # Count memories by type
            memory_type_counts = {}
            for memory in self._memories.values():
                memory_type = memory.memory_type
                memory_type_counts[memory_type] = memory_type_counts.get(memory_type, 0) + 1
            
            return {
                "total_memories": len(self._memories),
                "memory_type_counts": memory_type_counts,
                "working_memory_size": len(self._working_memory),
                "working_memory_limit": self._working_memory_limit,
                "store_count": self._store_count,
                "retrieve_count": self._retrieve_count,
                "consolidation_count": self._consolidation_count,
                "connected_infrastructure": {
                    "vector_database": self._vector_adapter is not None,
                    "knowledge_graph": self._knowledge_graph_adapter is not None
                }
            }


# Global instance
_unified_memory_framework: Optional[UnifiedMemoryFramework] = None
_unified_memory_lock = threading.Lock()


def get_unified_memory_framework() -> UnifiedMemoryFramework:
    """Get global unified memory framework instance."""
    global _unified_memory_framework
    if _unified_memory_framework is None:
        with _unified_memory_lock:
            if _unified_memory_framework is None:
                _unified_memory_framework = UnifiedMemoryFramework()
    return _unified_memory_framework


__all__ = [
    "MemoryType",
    "MemoryItem",
    "MemoryRetrievalResult",
    "MemoryConsolidationRequest",
    "UnifiedMemoryFrameworkInterface",
    "UnifiedMemoryFramework",
    "get_unified_memory_framework",
]