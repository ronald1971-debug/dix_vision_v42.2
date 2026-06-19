"""
INDIRA Memory Index - Knowledge Layer Component
Indexes and retrieves knowledge with provenance tracking
Per Rule 6 of the DIX VISION Tier-0 Production Implementation Contract
"""

import logging
from typing import Dict, List, Set, Tuple, Any, Optional, Callable
from datetime import datetime
from dataclasses import dataclass, field
from enum import Enum
from collections import defaultdict
import hashlib
import json

logger = logging.getLogger(__name__)

class MemoryType(Enum):
    """Types of memory/knowledge storage"""
    BELIEF = "belief"
    PREDICTION = "prediction"
    TRADE_DECISION = "trade_decision"
    MARKET_STATE = "market_state"
    EVIDENCE = "evidence"
    HYPOTHESIS = "hypothesis"
    OUTCOME = "outcome"

class AccessPattern(Enum):
    """Memory access patterns for optimization"""
    TEMPORAL = "temporal"
    FREQUENT = "frequent"
    RARE = "rare"
    SEQUENTIAL = "sequential"

@dataclass
class MemoryIndex:
    """Index entry for a piece of knowledge"""
    memory_id: str
    memory_type: MemoryType
    content_hash: str
    timestamp: datetime
    access_count: int = 0
    last_accessed: datetime = field(default_factory=datetime.utcnow)
    tags: Set[str] = field(default_factory=set)
    source: str = ""
    confidence: float = 0.0
    linked_memories: Set[str] = field(default_factory=set)
    metadata: Dict[str, Any] = field(default_factory=dict)

@dataclass
class RetrievalResult:
    """Result from memory retrieval operation"""
    memory_index: MemoryIndex
    content: Any
    confidence: float
    provenance: Dict[str, Any]
    access_latency_ms: float
    relevance_score: float

class MemoryIndexSystem:
    """
    Memory indexing and retrieval system for INDIRA cognitive engine
    Ensures belief lineage and evidence provenance per Rule 6
    """
    
    def __init__(self):
        self._index: Dict[str, MemoryIndex] = {}
        self._content_index: Dict[str, Set[str]] = defaultdict(set)  # hash -> memory_ids
        self._tag_index: Dict[str, Set[str]] = defaultdict(set)  # tag -> memory_ids
        self._source_index: Dict[str, Set[str]] = defaultdict(set)  # source -> memory_ids
        self._type_index: Dict[MemoryType, Set[str]] = defaultdict(set)  # type -> memory_ids
        self._temporal_index: List[Tuple[datetime, str]] = []  # (timestamp, memory_id) sorted
        self._access_stats = {
            "retrievals": 0,
            "hits": 0,
            "misses": 0,
            "total_latency_ms": 0
        }
        
    def index_memory(
        self,
        content: Any,
        memory_type: MemoryType,
        tags: Optional[List[str]] = None,
        source: str = "unknown",
        confidence: float = 0.5,
        metadata: Optional[Dict[str, Any]] = None
    ) -> str:
        """Index a piece of knowledge in the memory system"""
        # Generate unique memory ID based on content hash and timestamp
        content_str = json.dumps(content, sort_keys=True, default=str)
        content_hash = hashlib.sha256(content_str.encode()).hexdigest()
        timestamp = datetime.utcnow()
        memory_id = f"{memory_type.value}_{content_hash[:16]}_{timestamp.timestamp()}:{timestamp.nanosecond()}"
        
        # Create memory index entry
        index = MemoryIndex(
            memory_id=memory_id,
            memory_type=memory_type,
            content_hash=content_hash,
            timestamp=timestamp,
            tags=set(tags or []),
            source=source,
            confidence=confidence,
            metadata=metadata or {}
        )
        
        # Add to all indices
        self._index[memory_id] = index
        self._content_index[content_hash].add(memory_id)
        self._temporal_index.append((timestamp, memory_id))
        
        for tag in index.tags:
            self._tag_index[tag].add(memory_id)
        
        self._source_index[source].add(memory_id)
        self._type_index[memory_type].add(memory_id)
        
        logger.info(f"Indexed memory {memory_id} of type {memory_type.value} with {len(index.tags)} tags")
        return memory_id
    
    def retrieve_by_id(self, memory_id: str) -> Optional[RetrievalResult]:
        """Retrieve memory by ID with provenance tracking"""
        if memory_id not in self._index:
            self._access_stats["misses"] += 1
            return None
        
        index = self._index[memory_id]
        start = datetime.utcnow()
        
        # Update access stats
        index.access_count += 1
        index.last_accessed = datetime.utcnow()
        
        # Reconstruct content from stored data (in real system, would fetch from storage)
        # For now, return metadata about the memory
        result = RetrievalResult(
            memory_index=index,
            content=f"Content for {memory_id}",  # Would return actual content in real system
            confidence=index.confidence,
            provenance={
                "source": index.source,
                "timestamp": index.timestamp.isoformat(),
                "hash": index.content_hash,
                "access_count": index.access_count
            },
            access_latency_ms=(datetime.utcnow() - start).total_seconds() * 1000,
            relevance_score=1.0
        )
        
        self._access_stats["retrievals"] += 1
        self._access_stats["hits"] += 1
        self._access_stats["total_latency_ms"] += result.access_latency_ms
        
        return result
    
    def retrieve_by_content_hash(self, content_hash: str) -> List[RetrievalResult]:
        """Retrieve all memories with specific content hash"""
        memory_ids = self._content_index.get(content_hash, set())
        results = []
        
        for memory_id in memory_ids:
            result = self.retrieve_by_id(memory_id)
            if result:
                results.append(result)
        
        return results
    
    def retrieve_by_tags(self, tags: List[str], match_all: bool = False) -> List[RetrievalResult]:
        """Retrieve memories by tags"""
        if match_all:
            # Find memories that have ALL specified tags
            candidate_ids = set.intersection(*[self._tag_index.get(tag, set()) for tag in tags])
        else:
            # Find memories that have ANY of the specified tags
            candidate_ids = set.union(*[self._tag_index.get(tag, set()) for tag in tags])
        
        results = []
        for memory_id in candidate_ids:
            result = self.retrieve_by_id(memory_id)
            if result:
                results.append(result)
        
        return results
    
    def retrieve_by_source(self, source: str) -> List[RetrievalResult]:
        """Retrieve all memories from a specific source"""
        memory_ids = self._source_index.get(source, set())
        results = []
        
        for memory_id in memory_ids:
            result = retrieve_by_id(memory_id)
            if result:
                results.append(result)
        
        return results
    
    def retrieve_by_type(self, memory_type: MemoryType) -> List[RetrievalResult]:
        """Retrieve all memories of a specific type"""
        memory_ids = self._type_index.get(memory_type, set())
        results = []
        
        for memory_id in memory_ids:
            result = self.retrieve_by_id(memory_id)
            if result:
                results.append(result)
        
        return results
    
    def retrieve_temporal_range(self, start: datetime, end: datetime) -> List[RetrievalResult]:
        """Retrieve memories from a specific time range"""
        # Binary search on temporal index for efficiency
        results = []
        
        for timestamp, memory_id in self._temporal_index:
            if start <= timestamp <= end:
                result = self.retrieve_by_id(memory_id)
                if result:
                    results.append(result)
            elif timestamp > end:
                break  # temporal index is sorted, so we can break
        
        return results
    
    def retrieve_related(self, memory_id: str, depth: int = 1) -> Dict[str, RetrievalResult]:
        """Retrieve memories related to a specific memory"""
        if memory_id not in self._index:
            return {}
        
        index = self._index[memory_id]
        related = {}
        
        # Start with direct links
        current_ids = {memory_id}
        
        for level in range(depth + 1):
            next_ids = set()
            
            for current_id in current_ids:
                if current_id not in self._index:
                    continue
                    
                current_index = self._index[current_id]
                
                # Add linked memories
                for linked_id in current_index.linked_memories:
                    if linked_id not in related:
                        result = self.retrieve_by_id(linked_id)
                        if result:
                            related[linked_id] = result
                            next_ids.add(linked_id)
            
            current_ids = next_ids
            if not current_ids:
                break
        
        return related
    
    def link_memories(self, memory_id_1: str, memory_id_2: str, bidirectional: bool = True) -> None:
        """Create a link between two memories to establish provenance chain"""
        if memory_id_1 not in self._index or memory_id_2 not in self._index:
            logger.warning(f"Cannot link non-existent memories: {memory_id_1} and {memory_id_2}")
            return
        
        self._index[memory_id_1].linked_memories.add(memory_id_2)
        if bidirectional:
            self._index[memory_id_2].linked_memories.add(memory_id_1)
        
        logger.info(f"Linked memories: {memory_id_1} {'<->' if bidirectional else '->'} {memory_id_2}")
    
    def get_memory_lineage(self, memory_id: str, max_depth: int = 10) -> List[Dict[str, Any]]:
        """
        Get the lineage chain for a memory for provenance tracking
        Rule 6 Acceptance: Every belief traceable to evidence
        """
        lineage = []
        current_id = memory_id
        visited = set()
        
        while current_id and current_id not in visited and len(lineage) < max_depth:
            if current_id not in self._index:
                break
                
            index = self._index[current_id]
            
            lineage_entry = {
                "memory_id": current_id,
                "type": index.memory_type.value,
                "source": index.source,
                "timestamp": index.timestamp.isoformat(),
                "confidence": index.confidence,
                "linked_from": list(index.linked_memories)
            }
            lineage.append(lineage_entry)
            
            visited.add(current_id)
            
            # Follow highest confidence link backwards
            if index.linked_memories:
                current_id = max(index.linked_memories, 
                              key=lambda x: self._index[x].confidence if x in self._index else 0)
            else:
                break
        
        return lineage
    
    def get_access_pattern(self, memory_id: str) -> AccessPattern:
        """Determine access pattern for a memory for optimization"""
        if memory_id not in self._index:
            return AccessPattern.RARE
        
        index = self._index[memory_id]
        
        if index.access_count > 100:
            return AccessPattern.FREQUENT
        elif index.access_count > 10:
            return AccessPattern.TEMPORAL
        else:
            return AccessPattern.RARE
    
    def optimize_access_patterns(self) -> Dict[str, Any]:
        """Optimize memory access patterns for performance"""
        pattern_distribution = defaultdict(int)
        
        for memory_id, index in self._index.items():
            pattern = self.get_access_pattern(memory_id)
            pattern_distribution[pattern.value] += 1
        
        return {
            "total_memories": len(self._index),
            "pattern_distribution": dict(pattern_distribution),
            "average_access_count": sum(idx.access_count for idx in self._index.values()) / len(self._index) if self._index else 0,
            "cache_hit_rate": self._access_stats["hits"] / self._access_stats["retrievals"] if self._access_stats["retrievals"] > 0 else 0,
            "average_latency_ms": self._access_stats["total_latency_ms"] / self._access_stats["hits"] if self._access_stats["hits"] > 0 else 0
        }
    
    def cleanup_old_memories(self, older_than_days: int = 30) -> int:
        """Remove memories older than specified days"""
        cutoff = datetime.utcnow().timestamp() - (older_than_days * 86400)
        memories_to_remove = []
        
        for memory_id, index in self._index.items():
            if index.timestamp.timestamp() < cutoff:
                memories_to_remove.append(memory_id)
        
        for memory_id in memories_to_remove:
            self._remove_memory(memory_id)
        
        logger.info(f"Cleaned up {len(memories_to_remove)} old memories")
        return len(memories_to_remove)
    
    def _remove_memory(self, memory_id: str) -> None:
        """Internal method to remove memory from all indices"""
        if memory_id not in self._index:
            return
        
        index = self._index[memory_id]
        
        # Remove from content index
        content_hash = index.content_hash
        if content_hash in self._content_index:
            self._content_index[content_hash].remove(memory_id)
            if not self._content_index[content_hash]:
                del self._content_index[content_hash]
        
        # Remove from tag index
        for tag in index.tags:
            if tag in self._tag_index:
                self._tag_index[tag].remove(memory_id)
                if not self._tag_index[tag]:
                    del self._tag_index[tag]
        
        # Remove from source index
        if index.source in self._source_index:
            self._source_index[index.source].remove(memory_id)
            if not self._source_index[index.source]:
                del self._source_index[index.source]
        
        # Remove from type index
        if index.memory_type in self._type_index:
            self._type_index[index.memory_type].remove(memory_id)
            if not self._type_index[index.memory_type]:
                del self._type_index[index.memory_type]
        
        # Remove from temporal index
        self._temporal_index = [(ts, mid) for ts, mid in self._temporal_index if mid != memory_id]
        
        # Remove linked memory references
        for linked_id in index.linked_memories:
            if linked_id in self._index:
                self._index[linked_id].linked_memories.discard(memory_id)
        
        # Remove from main index
        del self._index[memory_id]
    
    def get_index_summary(self) -> Dict[str, Any]:
        """Get summary of the memory index system state"""
        type_distribution = {mem_type.value: len(mem_ids) for mem_type, mem_ids in self._type_index.items()}
        source_distribution = {source: len(mem_ids) for source, mem_ids in self._source_index.items()}
        
        return {
            "total_memories": len(self._index),
            "type_distribution": type_distribution,
            "source_distribution": source_distribution,
            "total_tags": len(self._tag_index),
            "access_stats": self._access_stats,
            "temporal_index_size": len(self._temporal_index),
            "timestamp": datetime.utcnow().isoformat()
        }