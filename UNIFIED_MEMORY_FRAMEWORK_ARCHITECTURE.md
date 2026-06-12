# DIX VISION v42.2 - UNIFIED MEMORY FRAMEWORK ARCHITECTURE

**Version:** 1.0  
**Status:** Design Complete  
**Last Updated:** 2026-06-12

---

## **EXECUTIVE SUMMARY**

This document defines the architecture for the Unified Memory Framework - a foundational component that consolidates 7+ fragmented memory systems into a single, vector-first memory system supporting semantic, episodic, procedural, and working memory types with tier management, consolidation, and forgetting mechanisms.

---

## **ARCHITECTURE OVERVIEW**

### **High-Level Architecture**

```
┌─────────────────────────────────────────────────────────────┐
│              Unified Memory Orchestrator                      │
│  ┌──────────────┬──────────────┬──────────────┬────────────┐ │
│  │ Memory Query │ Memory Store │ Memory Update│ Memory     │ │
│  │ Interface   │ Interface    │ Interface    │ Consol.    │ │
│  └──────┬───────┴──────┬───────┴──────┬───────┴────┬─────┘ │
└─────────┼──────────────┼──────────────┼────────────┼─────────┘
          │              │              │            │
          ▼              ▼              ▼            ▼
┌─────────────────────────────────────────────────────────────┐
│              Memory Type Layer                               │
│  ┌──────────┬──────────┬──────────┬──────────┬──────────┐ │
│  │ Semantic │Episodic  │Procedural│ Working   │Meta      │ │
│  │ Memory   │ Memory   │ Memory   │ Memory   │ Memory   │ │
│  └────┬─────┴────┬─────┴────┬─────┴────┬─────┴────┬─────┘ │
└───────┼───────────┼───────────┼───────────┼───────────┼─────────┘
        │           │           │           │           │
        ▼           ▼           ▼           ▼           ▼
┌─────────────────────────────────────────────────────────────┐
│              Vector Database Layer                            │
│  ┌──────────┬──────────┬──────────┬──────────┬──────────┐ │
│  │ Hot Tier │Warm Tier │Cold Tier │Archive   │Index     │ │
│  │ (Redis)  │ (Qdrant) │ (Disk)   │ (S3)     │ (Qdrant) │ │
│  └──────────┴──────────┴──────────┴──────────┴──────────┘ │
└─────────────────────────────────────────────────────────────┘
```

---

## **MEMORY TYPES**

### **1. Semantic Memory**

**Purpose:** General knowledge, facts, concepts, relationships

**Characteristics:**
- **Storage Duration:** Long-term (indefinite)
- **Access Pattern:** Read-heavy, occasional updates
- **Content Type:** Facts, concepts, relationships, rules
- **Vector Embeddings:** Required for semantic search
- **Retrieval:** Semantic similarity search

**Data Structure:**
```python
class SemanticMemory:
    memory_id: str
    content: str
    vector_embedding: List[float]  # 768-dimensional embedding
    category: str  # TRADING | ENGINEERING | GENERAL
    confidence: float  # 0-1
    source: str  # who created this memory
    created_at: datetime
    last_accessed: datetime
    access_count: int
    metadata: Dict[str, Any]
```

**Use Cases:**
- Trading rules and strategies
- System architecture knowledge
- Domain concepts and definitions
- Best practices and guidelines
- Causal relationships

---

### **2. Episodic Memory**

**Purpose:** Experiences, events, sequences with temporal context

**Characteristics:**
- **Storage Duration:** Long-term (with consolidation)
- **Access Pattern:** Temporal queries, sequence reconstruction
- **Content Type:** Events, experiences, sequences
- **Temporal Index:** Required for time-based queries
- **Vector Embeddings:** Required for content search

**Data Structure:**
```python
class EpisodicMemory:
    memory_id: str
    content: str
    vector_embedding: List[float]
    event_type: str  # TRADE | ENGINEERING | SYSTEM | CUSTOM
    start_time: datetime
    end_time: datetime
    sequence_id: str  # for linked events
    temporal_position: int  # position in sequence
    confidence: float
    source: str
    created_at: datetime
    last_accessed: datetime
    access_count: int
    metadata: Dict[str, Any]
```

**Use Cases:**
- Trading decisions and outcomes
- System failures and fixes
- Investigation results
- Learning experiences
- Debugging sessions

---

### **3. Procedural Memory**

**Purpose:** Skills, procedures, methods, algorithms

**Characteristics:**
- **Storage Duration:** Long-term
- **Access Pattern:** Execution-focused
- **Content Type:** Code, procedures, algorithms
- **Executable:** Often executable code
- **Version Control:** Required for procedure evolution

**Data Structure:**
```python
class ProceduralMemory:
    memory_id: str
    procedure_name: str
    procedure_type: str  # ALGORITHM | CODE | PROCESS | CUSTOM
    content: str  # code or procedure description
    parameters: Dict[str, Any]
    version: str
    confidence: float
    source: str
    created_at: datetime
    last_executed: datetime
    execution_count: int
    success_rate: float
    metadata: Dict[str, Any]
```

**Use Cases:**
- Trading algorithms
- Analysis procedures
- Debugging procedures
- Optimization techniques
- Code patterns

---

### **4. Working Memory**

**Purpose:** Current task state, temporary data, active focus

**Characteristics:**
- **Storage Duration:** Short-term (minutes to hours)
- **Access Pattern:** High-frequency reads/writes
- **Content Type:** Active task data, intermediate results
- **Performance:** Critical (<1ms access)
- **Capacity:** Limited (100-1000 items)

**Data Structure:**
```python
class WorkingMemory:
    memory_id: str
    content: str
    task_id: str  # associated task
    priority: float  # 0-1, for eviction
    created_at: datetime
    last_accessed: datetime
    access_count: int
    ttl_seconds: float  # time-to-live
    metadata: Dict[str, Any]
```

**Use Cases:**
- Current market state
- Active investigation context
- Decision intermediate states
- Attention allocation state
- Temporary computation results

---

### **5. Meta Memory**

**Purpose:** Memory system self-awareness, memory management

**Characteristics:**
- **Storage Duration:** Persistent
- **Access Pattern:** Management-focused
- **Content Type:** Memory statistics, access patterns
- **Self-Referential:** Meta-information about memory system

**Data Structure:**
```python
class MetaMemory:
    memory_id: str
    metric_type: str  # ACCESS_PATTERN | CONSOLIDATION | FORGETTING
    metric_data: Dict[str, Any]
    time_window: str  # HOURLY | DAILY | WEEKLY
    timestamp: datetime
    metadata: Dict[str, Any]
```

**Use Cases:**
- Access pattern tracking
- Consolidation triggers
- Forgetting decisions
- Memory optimization
- Performance monitoring

---

## **MEMORY TIER ARCHITECTURE**

### **Hot Tier (Redis)**
- **Purpose:** Extremely fast access for working memory
- **Latency:** <1ms
- **Capacity:** 10GB
- **Content:** Working memory, frequently accessed semantic/episodic
- **Eviction:** LRU with priority
- **Persistence:** Optional (for recovery)

### **Warm Tier (Qdrant)**
- **Purpose:** Vector search for semantic/episodic/procedural memory
- **Latency:** <10ms
- **Capacity:** 100GB
- **Content:** All memory types with vector embeddings
- **Search:** Semantic similarity, hybrid search
- **Persistence:** Persistent

### **Cold Tier (Disk)**
- **Purpose:** Long-term storage for rarely accessed memory
- **Latency:** <100ms
- **Capacity:** 1TB
- **Content:** Archival memory, historical data
- **Compression:** Enabled
- **Persistence:** Persistent

### **Archive Tier (S3/Cloud)**
- **Purpose:** Long-term backup and compliance
- **Latency:** <1s
- **Capacity:** Unlimited
- **Content:** Complete memory snapshots
- **Compression:** Enabled
- **Persistence:** Permanent

---

## **MEMORY CONSOLIDATION MECHANISM**

### **Consolidation Process**

**Trigger Conditions:**
1. **Time-based:** Daily at low-activity periods
2. **Capacity-based:** When warm tier reaches 80% capacity
3. **Performance-based:** When query latency degrades
4. **Event-based:** After significant learning events

**Consolidation Strategies:**

1. **Working Memory Consolidation:**
   - Migrate important working memory to episodic memory
   - Preserve temporal context and task relationships
   - Add vector embeddings for future retrieval

2. **Episodic Memory Consolidation:**
   - Merge related episodes into narrative summaries
   - Extract semantic knowledge from episodes
   - Update procedural memory based on episode patterns

3. **Semantic Memory Consolidation:**
   - Merge similar semantic memories
   - Update confidence scores based on usage
   - Remove conflicting or outdated memories

**Consolidation Algorithm:**
```python
def consolidate_memory():
    # 1. Identify consolidation candidates
    candidates = identify_consolidation_candidates()
    
    # 2. For each candidate
    for candidate in candidates:
        # 3. Extract key information
        key_info = extract_key_information(candidate)
        
        # 4. Determine target memory type
        target_type = determine_target_type(candidate, key_info)
        
        # 5. Create consolidated memory
        consolidated = create_consolidated_memory(candidate, key_info)
        
        # 6. Store in target memory
        store_memory(consolidated, target_type)
        
        # 7. Mark original for deletion
        mark_for_deletion(candidate.memory_id)
    
    # 8. Execute deletions
    execute_deletions()
    
    # 9. Update meta memory
    update_meta_memory(consolidation_results)
```

---

## **FORGETTING MECHANISM**

### **Forgetting Strategies**

**1. Time-Based Forgetting:**
- Decay memory importance over time
- Automatic removal after TTL expires
- Configurable decay rates per memory type

**2. Access-Based Forgetting:**
- Prioritize frequently accessed memories
- Deprioritize rarely accessed memories
- Gradual importance decay based on access patterns

**3. Importance-Based Forgetting:**
- High-confidence memories retained longer
- Low-confidence memories forgotten faster
- Memory importance scores computed from multiple factors

**4. Conflict-Based Forgetting:**
- Remove conflicting memories
- Keep most recent/confident version
- Log conflicts for learning

**Forgetting Algorithm:**
```python
def evaluate_memory_importance(memory):
    # 1. Time decay (older = less important)
    time_factor = compute_time_decay(memory.created_at)
    
    # 2. Access frequency
    access_factor = compute_access_frequency(memory.access_count)
    
    # 3. Confidence score
    confidence_factor = memory.confidence
    
    # 4. Source reliability
    source_factor = get_source_reliability(memory.source)
    
    # 5. Combined importance score
    importance = (
        0.3 * time_factor +
        0.3 * access_factor +
        0.2 * confidence_factor +
        0.2 * source_factor
    )
    
    return importance

def forget_memories():
    # 1. Evaluate all memories
    memories = get_all_memories()
    importance_scores = {
        m.memory_id: evaluate_memory_importance(m)
        for m in memories
    }
    
    # 2. Sort by importance
    sorted_memories = sorted(
        memories,
        key=lambda m: importance_scores[m.memory_id]
    )
    
    # 3. Mark low-importance memories for deletion
    threshold = get_forgetting_threshold()
    candidates_for_deletion = [
        m for m in sorted_memories
        if importance_scores[m.memory_id] < threshold
    ]
    
    # 4. Execute forgetting
    for memory in candidates_for_deletion:
        if should_forget(memory):
            delete_memory(memory.memory_id)
            log_forgetting(memory)
```

---

## **VECTOR DATABASE INTEGRATION**

### **Qdrant Configuration**

**Collection Schema:**
```python
{
    "collection_name": "unified_memory",
    "vectors": {
        "size": 768,  # Sentence-Transformers embedding size
        "distance": "Cosine"
    },
    "payload_schema": {
        "memory_type": "keyword",
        "content": "text",
        "category": "keyword",
        "confidence": "float",
        "source": "keyword",
        "created_at": "timestamp",
        "last_accessed": "timestamp",
        "metadata": "json"
    }
}
```

**Indexing Strategy:**
- **Primary Index:** Vector similarity (HNSW index)
- **Secondary Indexes:** Memory type, category, source, timestamp
- **Hybrid Search:** Vector similarity + BM25 text search

**Embedding Model:**
- **Model:** Sentence-Transformers (all-MiniLM-L6-v2)
- **Embedding Size:** 384 or 768 dimensions
- **Batch Size:** 32 embeddings per batch
- **Latency:** <10ms per embedding

---

## **INTERFACE DEFINITION**

### **UnifiedMemoryInterface**

```python
class UnifiedMemoryInterface(ABC):
    @abstractmethod
    def store_memory(
        self,
        content: str,
        memory_type: str,
        category: str = "GENERAL",
        confidence: float = 0.5,
        metadata: Dict[str, Any] | None = None
    ) -> str:
        """Store memory in unified memory framework."""
        pass
    
    @abstractmethod
    def retrieve_memory(
        self,
        query: str,
        memory_type: str = "semantic",
        limit: int = 10,
        filters: Dict[str, Any] | None = None
    ) -> List[MemoryRetrievalResult]:
        """Retrieve memory using vector search."""
        pass
    
    @abstractmethod
    def retrieve_by_id(
        self,
        memory_id: str
    ) -> Optional[Memory]:
        """Retrieve memory by ID."""
        pass
    
    @abstractmethod
    def update_memory(
        self,
        memory_id: str,
        content: str | None = None,
        confidence: float | None = None,
        metadata: Dict[str, Any] | None = None
    ) -> bool:
        """Update existing memory."""
        pass
    
    @abstractmethod
    def delete_memory(
        self,
        memory_id: str
    ) -> bool:
        """Delete memory."""
        pass
    
    @abstractmethod
    def consolidate_memory(self) -> ConsolidationResult:
        """Execute memory consolidation."""
        pass
    
    @abstractmethod
    def forget_memory(self, threshold: float = 0.1) -> ForgettingResult:
        """Execute memory forgetting."""
        pass
    
    @abstractmethod
    def get_memory_stats(self) -> MemoryStats:
        """Get memory system statistics."""
        pass
    
    @abstractmethod
    def search_hybrid(
        self,
        query: str,
        memory_type: str = "semantic",
        vector_weight: float = 0.7,
        text_weight: float = 0.3,
        limit: int = 10
    ) -> List[MemoryRetrievalResult]:
        """Hybrid search (vector + text)."""
        pass
```

---

## **PERFORMANCE SPECIFICATIONS**

### **Latency Targets:**
- **Working Memory Access:** <1ms (99th percentile)
- **Semantic Memory Retrieval:** <10ms (99th percentile)
- **Episodic Memory Retrieval:** <10ms (99th percentile)
- **Procedural Memory Retrieval:** <10ms (99th percentile)
- **Consolidation Operation:** <60s (total)
- **Forgetting Operation:** <30s (total)

### **Throughput Targets:**
- **Memory Store Operations:** 1000 ops/sec
- **Memory Retrieve Operations:** 500 ops/sec
- **Vector Search Operations:** 200 ops/sec
- **Concurrent Queries:** 50 concurrent

### **Capacity Targets:**
- **Hot Tier (Redis):** 10GB, 1M keys
- **Warm Tier (Qdrant):** 100GB, 10M vectors
- **Cold Tier (Disk):** 1TB, 100M memories
- **Archive Tier (S3):** Unlimited

---

## **IMPLEMENTATION PRIORITY**

### **Phase 1: Core Memory Framework (Week 5-6)**
1. ✅ Interface definitions
2. ⏳ Memory orchestrator implementation
3. ⏳ Qdrant vector database integration
4. ⏳ Redis hot tier integration
5. ⏳ Basic memory storage and retrieval

### **Phase 2: Memory Types Implementation (Week 7-8)**
1. ⏳ Semantic memory implementation
2. ⏳ Episodic memory implementation
3. ⏳ Procedural memory implementation
4. ⏳ Working memory implementation
5. ⏳ Meta memory implementation

### **Phase 3: Advanced Features (Week 9-10)**
1. ⏳ Memory consolidation mechanism
2. ⏳ Forgetting mechanism
3. ⏳ Tier management
4. ⏳ Hybrid search
5. ⏳ Memory optimization

### **Phase 4: Integration (Week 11-12)**
1. ⏳ Integration with INDIRA
2. ⏳ Integration with DYON
3. ⏳ Integration with Coordination Layer
4. ⏳ Performance optimization
5. ⏳ Testing and validation

---

## **SUCCESS CRITERIA**

### **Functional:**
- ✅ All memory types operational
- ✅ Vector search functional
- ✅ Tier management operational
- ✅ Consolidation functional
- ✅ Forgetting functional

### **Performance:**
- ✅ Memory access latency within targets
- ✅ Throughput within targets
- ✅ Vector search accuracy >85%
- ✅ Consolidation time <60s
- ✅ Forgetting time <30s

### **Integration:**
- ✅ INDIRA integration working
- ✅ DYON integration working
- ✅ Coordination integration working
- ✅ No data loss during migration
- ✅ Feature parity validated

---

## **NEXT STEPS**

1. **Review and Approve Architecture** - Stakeholder approval
2. **Set Up Qdrant Vector Database** - Week 3-4
3. **Set Up Redis Hot Tier** - Week 3-4
4. **Implement Memory Orchestrator** - Week 5-6
5. **Implement Memory Types** - Week 7-8

---

**Document Status:** Complete  
**Version:** 1.0  
**Next Review:** After Week 5-6 implementation