"""
shared_infrastructure.vector_database_adapter
DIX VISION v42.2 — Vector Database Adapter

Provides interface for vector database operations supporting semantic search.
Adapts to Qdrant or similar vector databases for vector-first memory retrieval.
"""

from __future__ import annotations

import logging
import math
from datetime import datetime
from typing import Any, Dict, List, Optional, Tuple
from dataclasses import dataclass, field
from abc import ABC, abstractmethod
import threading

logger = logging.getLogger(__name__)


class VectorMemoryType:
    """Types of vector memory."""
    SEMANTIC = "semantic"
    EPISODIC = "episodic"
    PROCEDURAL = "procedural"
    WORKING = "working"
    LONG_TERM = "long_term"
    CUSTOM = "custom"


@dataclass
class VectorRecord:
    """A vector record in the database."""
    record_id: str
    vector: List[float]
    payload: Dict[str, Any]
    memory_type: VectorMemoryType
    metadata: Dict[str, Any] = field(default_factory=dict)
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: datetime = field(default_factory=datetime.utcnow)


@dataclass
class VectorSearchResult:
    """Result from a vector search."""
    record_id: str
    vector: List[float]
    payload: Dict[str, Any]
    memory_type: VectorMemoryType
    similarity: float  # Cosine similarity (0 to 1)
    distance: float   # Euclidean distance
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class VectorSearchQuery:
    """A query for vector search."""
    query_id: str
    query_vector: List[float]
    memory_types: Optional[List[VectorMemoryType]] = None
    limit: int = 10
    score_threshold: float = 0.5
    filters: Dict[str, Any] = field(default_factory=dict)
    search_params: Dict[str, Any] = field(default_factory=dict)


class VectorDatabaseAdapterInterface(ABC):
    """Interface for vector database operations."""
    
    @abstractmethod
    def upsert(self, record: VectorRecord) -> str:
        """Insert or update a vector record."""
        pass
    
    @abstractmethod
    def search(self, query: VectorSearchQuery) -> List[VectorSearchResult]:
        """Search for similar vectors."""
        pass
    
    @abstractmethod
    def get_record(self, record_id: str) -> Optional[VectorRecord]:
        """Get a record by ID."""
        pass
    
    @abstractmethod
    def delete_record(self, record_id: str) -> bool:
        """Delete a record by ID."""
        pass
    
    @abstractmethod
    def delete_by_filter(self, filter_dict: Dict[str, Any]) -> int:
        """Delete records matching a filter."""
        pass
    
    @abstractmethod
    def create_collection(
        self,
        collection_name: str,
        vector_size: int,
        distance_metric: str = "cosine"
    ) -> bool:
        """Create a new collection."""
        pass
    
    @abstractmethod
    def delete_collection(self, collection_name: str) -> bool:
        """Delete a collection."""
        pass
    
    @abstractmethod
    def get_collection_info(self, collection_name: str) -> Optional[Dict[str, Any]]:
        """Get information about a collection."""
        pass
    
    @abstractmethod
    def get_statistics(self) -> Dict[str, Any]:
        """Get vector database statistics."""
        pass


class InMemoryVectorDatabaseAdapter(VectorDatabaseAdapterInterface):
    """
    In-memory implementation of vector database for development and testing.
    Can be replaced with Qdrant or other vector database implementations.
    """
    
    def __init__(self, default_vector_size: int = 768):
        self._lock = threading.Lock()
        
        # In-memory storage
        self._records: Dict[str, VectorRecord] = {}
        self._default_vector_size = default_vector_size
        
        # Collections (simulated)
        self._collections: Dict[str, Dict[str, Any]] = {
            "default": {
                "name": "default",
                "vector_size": default_vector_size,
                "distance_metric": "cosine",
                "created_at": datetime.utcnow()
            }
        }
        
        # Statistics
        self._search_count = 0
        self._upsert_count = 0
        self._search_total_time_ms = 0.0
        
        logger.info(f"[VECTOR_DB] In-memory adapter initialized (vector_size: {default_vector_size})")
    
    def upsert(self, record: VectorRecord) -> str:
        """Insert or update a vector record."""
        with self._lock:
            # Validate vector size
            collection = self._collections.get("default")
            if collection and len(record.vector) != collection["vector_size"]:
                logger.warning(f"[VECTOR_DB] Vector size mismatch: expected {collection['vector_size']}, got {len(record.vector)}")
                # Normalize vector size for compatibility
                if len(record.vector) > collection["vector_size"]:
                    record.vector = record.vector[:collection["vector_size"]]
                else:
                    record.vector = record.vector + [0.0] * (collection["vector_size"] - len(record.vector))
            
            self._records[record.record_id] = record
            self._upsert_count += 1
            
            logger.debug(f"[VECTOR_DB] Upserted record: {record.record_id} ({record.memory_type})")
            return record.record_id
    
    def search(self, query: VectorSearchQuery) -> List[VectorSearchResult]:
        """Search for similar vectors using cosine similarity."""
        start_time = datetime.utcnow()
        
        try:
            results = []
            
            # Calculate similarity for all records
            for record in self._records.values():
                # Apply memory type filter
                if query.memory_types and record.memory_type not in query.memory_types:
                    continue
                
                # Apply payload filters
                if query.filters:
                    match = True
                    for key, value in query.filters.items():
                        if record.payload.get(key) != value:
                            match = False
                            break
                    if not match:
                        continue
                
                # Calculate cosine similarity
                similarity = self._cosine_similarity(query.query_vector, record.vector)
                distance = self._euclidean_distance(query.query_vector, record.vector)
                
                # Apply score threshold
                if similarity >= query.score_threshold:
                    results.append(VectorSearchResult(
                        record_id=record.record_id,
                        vector=record.vector,
                        payload=record.payload,
                        memory_type=record.memory_type,
                        similarity=similarity,
                        distance=distance,
                        metadata=record.metadata
                    ))
            
            # Sort by similarity (descending)
            results.sort(key=lambda x: x.similarity, reverse=True)
            
            # Limit results
            results = results[:query.limit]
            
            # Calculate execution time
            execution_time_ms = (datetime.utcnow() - start_time).total_seconds() * 1000
            
            # Update statistics
            with self._lock:
                self._search_count += 1
                self._search_total_time_ms += execution_time_ms
            
            logger.info(f"[VECTOR_DB] Search completed: {len(results)} results ({execution_time_ms:.2f}ms)")
            
            return results
            
        except Exception as e:
            logger.error(f"[VECTOR_DB] Search failed: {e}")
            return []
    
    def _cosine_similarity(self, vec1: List[float], vec2: List[float]) -> float:
        """Calculate cosine similarity between two vectors."""
        try:
            # Dot product
            dot_product = sum(a * b for a, b in zip(vec1, vec2))
            
            # Magnitudes
            magnitude1 = math.sqrt(sum(a * a for a in vec1))
            magnitude2 = math.sqrt(sum(b * b for b in vec2))
            
            if magnitude1 == 0 or magnitude2 == 0:
                return 0.0
            
            # Cosine similarity
            return dot_product / (magnitude1 * magnitude2)
            
        except Exception as e:
            logger.warning(f"[VECTOR_DB] Cosine similarity calculation failed: {e}")
            return 0.0
    
    def _euclidean_distance(self, vec1: List[float], vec2: List[float]) -> float:
        """Calculate Euclidean distance between two vectors."""
        try:
            return math.sqrt(sum((a - b) ** 2 for a, b in zip(vec1, vec2)))
        except Exception as e:
            logger.warning(f"[VECTOR_DB] Euclidean distance calculation failed: {e}")
            return float('inf')
    
    def get_record(self, record_id: str) -> Optional[VectorRecord]:
        """Get a record by ID."""
        with self._lock:
            return self._records.get(record_id)
    
    def delete_record(self, record_id: str) -> bool:
        """Delete a record by ID."""
        with self._lock:
            if record_id in self._records:
                del self._records[record_id]
                logger.debug(f"[VECTOR_DB] Deleted record: {record_id}")
                return True
            return False
    
    def delete_by_filter(self, filter_dict: Dict[str, Any]) -> int:
        """Delete records matching a filter."""
        with self._lock:
            records_to_delete = []
            
            for record_id, record in self._records.items():
                match = True
                for key, value in filter_dict.items():
                    if record.payload.get(key) != value:
                        match = False
                        break
                if match:
                    records_to_delete.append(record_id)
            
            # Delete matching records
            for record_id in records_to_delete:
                del self._records[record_id]
            
            logger.debug(f"[VECTOR_DB] Deleted {len(records_to_delete)} records matching filter")
            return len(records_to_delete)
    
    def create_collection(
        self,
        collection_name: str,
        vector_size: int,
        distance_metric: str = "cosine"
    ) -> bool:
        """Create a new collection."""
        with self._lock:
            if collection_name in self._collections:
                logger.warning(f"[VECTOR_DB] Collection {collection_name} already exists")
                return False
            
            self._collections[collection_name] = {
                "name": collection_name,
                "vector_size": vector_size,
                "distance_metric": distance_metric,
                "created_at": datetime.utcnow()
            }
            
            logger.info(f"[VECTOR_DB] Created collection: {collection_name} (vector_size: {vector_size})")
            return True
    
    def delete_collection(self, collection_name: str) -> bool:
        """Delete a collection."""
        with self._lock:
            if collection_name not in self._collections:
                logger.warning(f"[VECTOR_DB] Collection {collection_name} not found")
                return False
            
            # Delete all records in this collection (simplified - uses all records)
            # In a real implementation, records would be scoped to collections
            del self._collections[collection_name]
            
            logger.info(f"[VECTOR_DB] Deleted collection: {collection_name}")
            return True
    
    def get_collection_info(self, collection_name: str) -> Optional[Dict[str, Any]]:
        """Get information about a collection."""
        with self._lock:
            collection = self._collections.get(collection_name)
            if collection:
                # Count records in this collection (simplified)
                record_count = len(self._records)  # In real impl, would filter by collection
                return {
                    "name": collection["name"],
                    "vector_size": collection["vector_size"],
                    "distance_metric": collection["distance_metric"],
                    "record_count": record_count,
                    "created_at": collection["created_at"].isoformat()
                }
            return None
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get vector database statistics."""
        with self._lock:
            # Count records by memory type
            memory_type_counts = {}
            for record in self._records.values():
                memory_type = record.memory_type
                memory_type_counts[memory_type] = memory_type_counts.get(memory_type, 0) + 1
            
            # Calculate average search time
            avg_search_time = (
                self._search_total_time_ms / self._search_count
                if self._search_count > 0 else 0.0
            )
            
            return {
                "total_records": len(self._records),
                "total_collections": len(self._collections),
                "memory_type_counts": memory_type_counts,
                "search_count": self._search_count,
                "upsert_count": self._upsert_count,
                "average_search_time_ms": avg_search_time,
                "adapter_type": "in_memory"
            }


class SemanticMemoryRetriever:
    """Retriever for semantic memory using vector database."""
    
    def __init__(self, vector_adapter: VectorDatabaseAdapterInterface):
        self._vector_adapter = vector_adapter
        self._lock = threading.Lock()
        
        logger.info("[SEMANTIC_MEMORY] Retriever initialized")
    
    def retrieve(
        self,
        query_text: str,
        query_embedding: Optional[List[float]] = None,
        memory_types: Optional[List[VectorMemoryType]] = None,
        limit: int = 10,
        score_threshold: float = 0.5
    ) -> List[VectorSearchResult]:
        """Retrieve semantic memories."""
        try:
            # If no embedding provided, create placeholder
            # In real implementation, would use embedding model
            if query_embedding is None:
                query_embedding = self._create_placeholder_embedding(query_text)
            
            query = VectorSearchQuery(
                query_id=f"semantic_{int(datetime.utcnow().timestamp())}",
                query_vector=query_embedding,
                memory_types=memory_types,
                limit=limit,
                score_threshold=score_threshold
            )
            
            results = self._vector_adapter.search(query)
            
            logger.info(f"[SEMANTIC_MEMORY] Retrieved {len(results)} semantic memories for: {query_text[:50]}...")
            
            return results
            
        except Exception as e:
            logger.error(f"[SEMANTIC_MEMORY] Retrieval failed: {e}")
            return []
    
    def store(
        self,
        text: str,
        embedding: Optional[List[float]] = None,
        memory_type: VectorMemoryType = VectorMemoryType.SEMANTIC,
        metadata: Optional[Dict[str, Any]] = None
    ) -> str:
        """Store semantic memory."""
        try:
            # If no embedding provided, create placeholder
            if embedding is None:
                embedding = self._create_placeholder_embedding(text)
            
            record_id = f"semantic_{int(datetime.utcnow().timestamp())}"
            
            record = VectorRecord(
                record_id=record_id,
                vector=embedding,
                payload={
                    "text": text,
                    "created_at": datetime.utcnow().isoformat()
                },
                memory_type=memory_type,
                metadata=metadata or {}
            )
            
            self._vector_adapter.upsert(record)
            
            logger.info(f"[SEMANTIC_MEMORY] Stored semantic memory: {record_id}")
            
            return record_id
            
        except Exception as e:
            logger.error(f"[SEMANTIC_MEMORY] Storage failed: {e}")
            return ""
    
    def _create_placeholder_embedding(self, text: str) -> List[float]:
        """Create placeholder embedding for text."""
        # In real implementation, would use embedding model (e.g., sentence-transformers)
        # For now, create a hash-based embedding
        import hashlib
        
        # Create hash of text
        text_hash = hashlib.md5(text.encode()).hexdigest()
        
        # Convert hash to normalized vector
        vector = []
        for i in range(0, len(text_hash), 2):
            byte_pair = text_hash[i:i+2]
            value = int(byte_pair, 16) / 255.0
            vector.append(value)
        
        # Pad or truncate to default size
        default_size = self._vector_adapter._collections.get("default", {}).get("vector_size", 768)
        if len(vector) < default_size:
            vector = vector + [0.0] * (default_size - len(vector))
        else:
            vector = vector[:default_size]
        
        return vector


# Global instances
_vector_database_adapter: Optional[VectorDatabaseAdapterInterface] = None
_vector_db_lock = threading.Lock()


def get_vector_database_adapter() -> VectorDatabaseAdapterInterface:
    """Get global vector database adapter instance."""
    global _vector_database_adapter
    if _vector_database_adapter is None:
        with _vector_db_lock:
            if _vector_database_adapter is None:
                _vector_database_adapter = InMemoryVectorDatabaseAdapter()
    return _vector_database_adapter


def get_semantic_memory_retriever() -> SemanticMemoryRetriever:
    """Get semantic memory retriever with global adapter."""
    adapter = get_vector_database_adapter()
    return SemanticMemoryRetriever(adapter)


__all__ = [
    "VectorMemoryType",
    "VectorRecord",
    "VectorSearchResult",
    "VectorSearchQuery",
    "VectorDatabaseAdapterInterface",
    "InMemoryVectorDatabaseAdapter",
    "SemanticMemoryRetriever",
    "get_vector_database_adapter",
    "get_semantic_memory_retriever",
]