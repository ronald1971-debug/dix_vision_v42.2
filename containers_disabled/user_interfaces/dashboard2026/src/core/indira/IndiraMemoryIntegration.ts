/**
 * INDIRA Memory Integration with Vector Optimization
 * DIX VISION v42.2 - Phase 4 (Phase 6): INDIRA Architecture Modernization
 * 
 * Production-grade memory integration system with vector-based storage and retrieval optimization.
 * Implements efficient vector embeddings for similarity search, memory consolidation,
 * and optimized retrieval patterns for INDIRA's cognitive processes.
 */

export interface MemoryVector {
  id: string;
  vector: number[];
  content: any;
  metadata: {
    type: string;
    timestamp: number;
    importance: number;
    accessCount: number;
    lastAccess: number;
    associations: string[];
    emotionalValence: number;
    contextTags: string[];
  };
  size: number;
}

export interface VectorSearchResult {
  memoryId: string;
  similarity: number;
  content: any;
  metadata: MemoryVector['metadata'];
  relevanceScore: number;
}

export interface MemoryConsolidationResult {
  originalMemories: number;
  consolidatedMemories: number;
  memorySaved: number;
  consolidationRatio: number;
  processingTimeMs: number;
}

export interface MemoryRetrievalQuery {
  queryVector?: number[];
  queryText?: string;
  filters?: {
    type?: string;
    minImportance?: number;
    timeRange?: { start: number; end: number };
    contextTags?: string[];
    emotionalValence?: { min: number; max: number };
  };
  limit: number;
  threshold: number;
}

class IndiraMemoryIntegration {
  private memoryVectors: Map<string, MemoryVector> = new Map();
  private vectorIndex: Map<string, string[]> = new Map(); // Type -> Memory IDs
  private temporalIndex: Map<number, string[]> = new Map(); // Timestamp -> Memory IDs
  private importanceIndex: Map<string, string[]> = new Map(); // Importance level -> Memory IDs
  private maxMemorySize: number = 10000;
  private vectorDimensions: number = 128;
  private consolidationThreshold: number = 0.85;

  constructor() {
    this.initializeIndices();
  }

  /**
   * Initialize memory indices
   */
  private initializeIndices(): void {
    this.vectorIndex.set('market', []);
    this.vectorIndex.set('trader', []);
    this.vectorIndex.set('strategy', []);
    this.vectorIndex.set('portfolio', []);
    this.vectorIndex.set('research', []);
    
    this.importanceIndex.set('high', []);
    this.importanceIndex.set('medium', []);
    this.importanceIndex.set('low', []);
  }

  /**
   * Generate vector embedding for content
   */
  private generateVector(content: any): number[] {
    // Simplified vector generation - in production would use actual embedding model
    const vector: number[] = [];
    
    // Convert content to hash-like vector
    const contentString = JSON.stringify(content);
    let hash = 0;
    for (let i = 0; i < contentString.length; i++) {
      hash = ((hash << 5) - hash) + contentString.charCodeAt(i);
      hash = hash & hash;
    }
    
    // Generate normalized vector
    for (let i = 0; i < this.vectorDimensions; i++) {
      const value = Math.sin(hash * (i + 1) * 0.1) * Math.cos(hash * (i + 2) * 0.05);
      vector.push(value);
    }
    
    // Normalize vector
    const magnitude = Math.sqrt(vector.reduce((sum, val) => sum + val * val, 0));
    return vector.map(val => val / magnitude);
  }

  /**
   * Store memory with vector optimization
   */
  storeMemory(content: any, metadata: Partial<MemoryVector['metadata']>): MemoryVector {
    const memoryId = `mem_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
    const vector = this.generateVector(content);
    
    const completeMetadata: MemoryVector['metadata'] = {
      type: metadata.type || 'general',
      timestamp: metadata.timestamp || Date.now(),
      importance: metadata.importance || 0.5,
      accessCount: 0,
      lastAccess: Date.now(),
      associations: metadata.associations || [],
      emotionalValence: metadata.emotionalValence || 0,
      contextTags: metadata.contextTags || []
    };
    
    const memoryVector: MemoryVector = {
      id: memoryId,
      vector,
      content,
      metadata: completeMetadata,
      size: JSON.stringify(content).length
    };
    
    this.memoryVectors.set(memoryId, memoryVector);
    
    // Update indices
    this.updateIndices(memoryVector);
    
    // Prune if at capacity
    if (this.memoryVectors.size > this.maxMemorySize) {
      this.pruneLowImportanceMemories();
    }
    
    console.log(`Stored memory ${memoryId} with vector optimization`);
    return memoryVector;
  }

  /**
   * Update indices for memory
   */
  private updateIndices(memory: MemoryVector): void {
    // Type index
    const typeIds = this.vectorIndex.get(memory.metadata.type) || [];
    typeIds.push(memory.id);
    this.vectorIndex.set(memory.metadata.type, typeIds);
    
    // Temporal index
    const timestamp = Math.floor(memory.metadata.timestamp / 3600000) * 3600000; // Hour buckets
    const timeIds = this.temporalIndex.get(timestamp) || [];
    timeIds.push(memory.id);
    this.temporalIndex.set(timestamp, timeIds);
    
    // Importance index
    const importanceLevel = this.getImportanceLevel(memory.metadata.importance);
    const importanceIds = this.importanceIndex.get(importanceLevel) || [];
    importanceIds.push(memory.id);
    this.importanceIndex.set(importanceLevel, importanceIds);
  }

  /**
   * Get importance level from score
   */
  private getImportanceLevel(importance: number): string {
    if (importance >= 0.8) return 'high';
    if (importance >= 0.5) return 'medium';
    return 'low';
  }

  /**
   * Search memories by vector similarity
   */
  searchMemories(query: MemoryRetrievalQuery): VectorSearchResult[] {
    const startTime = Date.now();
    let candidateIds: string[] = [];
    
    // Apply type filter
    if (query.filters?.type) {
      candidateIds = this.vectorIndex.get(query.filters.type) || [];
    } else {
      candidateIds = Array.from(this.memoryVectors.keys());
    }
    
    // Apply importance filter
    if (query.filters?.minImportance !== undefined) {
      candidateIds = candidateIds.filter(id => {
        const memory = this.memoryVectors.get(id);
        return memory && memory.metadata.importance >= query.filters!.minImportance!;
      });
    }
    
    // Apply time range filter
    if (query.filters?.timeRange) {
      const { start, end } = query.filters.timeRange;
      candidateIds = candidateIds.filter(id => {
        const memory = this.memoryVectors.get(id);
        return memory && memory.metadata.timestamp >= start && memory.metadata.timestamp <= end;
      });
    }
    
    // Apply context tags filter
    if (query.filters?.contextTags && query.filters.contextTags.length > 0) {
      candidateIds = candidateIds.filter(id => {
        const memory = this.memoryVectors.get(id);
        if (!memory) return false;
        return query.filters!.contextTags!.some(tag => 
          memory.metadata.contextTags.includes(tag)
        );
      });
    }
    
    // Apply emotional valence filter
    if (query.filters?.emotionalValence) {
      const { min, max } = query.filters.emotionalValence;
      candidateIds = candidateIds.filter(id => {
        const memory = this.memoryVectors.get(id);
        return memory && 
          memory.metadata.emotionalValence >= min && 
          memory.metadata.emotionalValence <= max;
      });
    }
    
    // Calculate similarities
    const results: VectorSearchResult[] = [];
    const queryVector = query.queryVector || this.generateVector(query.queryText || {});
    
    candidateIds.forEach(id => {
      const memory = this.memoryVectors.get(id);
      if (!memory) return;
      
      const similarity = this.calculateCosineSimilarity(queryVector, memory.vector);
      
      if (similarity >= query.threshold) {
        // Update access metrics
        memory.metadata.accessCount++;
        memory.metadata.lastAccess = Date.now();
        
        results.push({
          memoryId: id,
          similarity,
          content: memory.content,
          metadata: memory.metadata,
          relevanceScore: similarity * memory.metadata.importance
        });
      }
    });
    
    // Sort by relevance and limit
    results.sort((a, b) => b.relevanceScore - a.relevanceScore);
    
    const searchTime = Date.now() - startTime;
    console.log(`Vector search completed in ${searchTime}ms, found ${results.length} results`);
    
    return results.slice(0, query.limit);
  }

  /**
   * Calculate cosine similarity between vectors
   */
  private calculateCosineSimilarity(vec1: number[], vec2: number[]): number {
    const dotProduct = vec1.reduce((sum, val, i) => sum + val * vec2[i], 0);
    const magnitude1 = Math.sqrt(vec1.reduce((sum, val) => sum + val * val, 0));
    const magnitude2 = Math.sqrt(vec2.reduce((sum, val) => sum + val * val, 0));
    
    if (magnitude1 === 0 || magnitude2 === 0) return 0;
    
    return dotProduct / (magnitude1 * magnitude2);
  }

  /**
   * Retrieve memory by ID
   */
  retrieveMemory(memoryId: string): MemoryVector | null {
    const memory = this.memoryVectors.get(memoryId);
    if (memory) {
      memory.metadata.accessCount++;
      memory.metadata.lastAccess = Date.now();
    }
    return memory || null;
  }

  /**
   * Get memory statistics
   */
  getMemoryStats(): {
    totalMemories: number;
    memoriesByType: Record<string, number>;
    memoriesByImportance: Record<string, number>;
    averageAccessCount: number;
    totalMemorySize: number;
    consolidationCandidates: number;
  } {
    const memories = Array.from(this.memoryVectors.values());
    
    const memoriesByType: Record<string, number> = {};
    const memoriesByImportance: Record<string, number> = {};
    
    memories.forEach(memory => {
      memoriesByType[memory.metadata.type] = (memoriesByType[memory.metadata.type] || 0) + 1;
      
      const importanceLevel = this.getImportanceLevel(memory.metadata.importance);
      memoriesByImportance[importanceLevel] = (memoriesByImportance[importanceLevel] || 0) + 1;
    });
    
    const averageAccessCount = memories.length > 0
      ? memories.reduce((sum, m) => sum + m.metadata.accessCount, 0) / memories.length
      : 0;
    
    const totalMemorySize = memories.reduce((sum, m) => sum + m.size, 0);
    
    // Count consolidation candidates
    const consolidationCandidates = memories.filter(m => 
      m.metadata.importance < this.consolidationThreshold &&
      m.metadata.accessCount < 3
    ).length;
    
    return {
      totalMemories: memories.length,
      memoriesByType,
      memoriesByImportance,
      averageAccessCount,
      totalMemorySize,
      consolidationCandidates
    };
  }

  /**
   * Perform memory consolidation
   */
  async performMemoryConsolidation(): Promise<MemoryConsolidationResult> {
    const startTime = Date.now();
    const originalMemories = this.memoryVectors.size;
    
    console.log('Starting memory consolidation...');
    
    // Find consolidation candidates
    const candidates = Array.from(this.memoryVectors.values()).filter(m =>
      m.metadata.importance < this.consolidationThreshold &&
      m.metadata.accessCount < 3 &&
      (Date.now() - m.metadata.lastAccess) > 86400000 // 24 hours old
    );
    
    console.log(`Found ${candidates.length} consolidation candidates`);
    
    // Group similar memories for consolidation
    const consolidatedGroups = this.groupSimilarMemories(candidates);
    
    // Create consolidated memories
    let consolidatedCount = 0;
    consolidatedGroups.forEach(group => {
      if (group.length > 1) {
        const consolidatedMemory = this.createConsolidatedMemory(group);
        group.forEach(memory => {
          this.memoryVectors.delete(memory.id);
          this.removeFromIndices(memory);
        });
        this.memoryVectors.set(consolidatedMemory.id, consolidatedMemory);
        this.updateIndices(consolidatedMemory);
        consolidatedCount++;
      }
    });
    
    const processingTimeMs = Date.now() - startTime;
    const memorySaved = candidates.length - consolidatedCount;
    const consolidationRatio = originalMemories > 0 ? consolidatedCount / originalMemories : 0;
    
    console.log(`Consolidation completed: ${candidates.length} → ${consolidatedCount} memories`);
    
    return {
      originalMemories,
      consolidatedMemories: consolidatedCount,
      memorySaved,
      consolidationRatio,
      processingTimeMs
    };
  }

  /**
   * Group similar memories for consolidation
   */
  private groupSimilarMemories(memories: MemoryVector[]): MemoryVector[][] {
    const groups: MemoryVector[][] = [];
    const usedIds = new Set<string>();
    
    memories.forEach(memory => {
      if (usedIds.has(memory.id)) return;
      
      const group = [memory];
      usedIds.add(memory.id);
      
      // Find similar memories
      memories.forEach(other => {
        if (usedIds.has(other.id)) return;
        
        const similarity = this.calculateCosineSimilarity(memory.vector, other.vector);
        if (similarity > 0.9) {
          group.push(other);
          usedIds.add(other.id);
        }
      });
      
      if (group.length > 1) {
        groups.push(group);
      }
    });
    
    return groups;
  }

  /**
   * Create consolidated memory from group
   */
  private createConsolidatedMemory(group: MemoryVector[]): MemoryVector {
    const mostImportant = group.reduce((max, m) => 
      m.metadata.importance > max.metadata.importance ? m : max
    );
    
    // Combine content with metadata about consolidation
    const consolidatedContent = {
      type: 'consolidated',
      originalCount: group.length,
      originalIds: group.map(m => m.id),
      timeRange: {
        start: Math.min(...group.map(m => m.metadata.timestamp)),
        end: Math.max(...group.map(m => m.metadata.timestamp))
      },
      representativeContent: mostImportant.content,
      metadata: {
        types: group.map(m => m.metadata.type),
        totalAccessCount: group.reduce((sum, m) => sum + m.metadata.accessCount, 0),
        averageImportance: group.reduce((sum, m) => sum + m.metadata.importance, 0) / group.length
      }
    };
    
    const consolidatedVector = this.generateVector(consolidatedContent);
    
    return {
      id: `cons_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`,
      vector: consolidatedVector,
      content: consolidatedContent,
      metadata: {
        type: 'consolidated',
        timestamp: Date.now(),
        importance: mostImportant.metadata.importance * 0.9, // Slightly reduced
        accessCount: 0,
        lastAccess: Date.now(),
        associations: group.flatMap(m => m.metadata.associations),
        emotionalValence: group.reduce((sum, m) => sum + m.metadata.emotionalValence, 0) / group.length,
        contextTags: [...new Set(group.flatMap(m => m.metadata.contextTags))]
      },
      size: JSON.stringify(consolidatedContent).length
    };
  }

  /**
   * Remove memory from indices
   */
  private removeFromIndices(memory: MemoryVector): void {
    // Type index
    const typeIds = this.vectorIndex.get(memory.metadata.type) || [];
    this.vectorIndex.set(memory.metadata.type, typeIds.filter(id => id !== memory.id));
    
    // Temporal index
    const timestamp = Math.floor(memory.metadata.timestamp / 3600000) * 3600000;
    const timeIds = this.temporalIndex.get(timestamp) || [];
    this.temporalIndex.set(timestamp, timeIds.filter(id => id !== memory.id));
    
    // Importance index
    const importanceLevel = this.getImportanceLevel(memory.metadata.importance);
    const importanceIds = this.importanceIndex.get(importanceLevel) || [];
    this.importanceIndex.set(importanceLevel, importanceIds.filter(id => id !== memory.id));
  }

  /**
   * Prune low importance memories
   */
  private pruneLowImportanceMemories(): number {
    const memories = Array.from(this.memoryVectors.values())
      .sort((a, b) => {
        // Sort by (importance - age) composite score
        const ageScore = (Date.now() - a.metadata.timestamp) / 86400000; // days
        const compositeA = a.metadata.importance - (ageScore * 0.01);
        const ageScoreB = (Date.now() - b.metadata.timestamp) / 86400000;
        const compositeB = b.metadata.importance - (ageScoreB * 0.01);
        return compositeA - compositeB;
      });
    
    const toRemove = memories.slice(0, 100); // Remove bottom 100
    toRemove.forEach(memory => {
      this.memoryVectors.delete(memory.id);
      this.removeFromIndices(memory);
    });
    
    console.log(`Pruned ${toRemove.length} low importance memories`);
    return toRemove.length;
  }

  /**
   * Clear old memories by type
   */
  clearMemoriesByType(type: string, maxAgeMs: number = 604800000): number {
    const cutoffTime = Date.now() - maxAgeMs;
    let clearedCount = 0;
    
    const typeMemories = this.vectorIndex.get(type) || [];
    typeMemories.forEach(id => {
      const memory = this.memoryVectors.get(id);
      if (memory && memory.metadata.timestamp < cutoffTime) {
        this.memoryVectors.delete(id);
        this.removeFromIndices(memory);
        clearedCount++;
      }
    });
    
    console.log(`Cleared ${clearedCount} ${type} memories older than ${maxAgeMs}ms`);
    return clearedCount;
  }

  /**
   * Get memory usage by type
   */
  getMemoryUsageByType(): Record<string, {
    count: number;
    totalSize: number;
    averageSize: number;
    averageImportance: number;
  }> {
    const usage: Record<string, any> = {};
    
    const memoriesByType = new Map<string, MemoryVector[]>();
    this.memoryVectors.forEach(memory => {
      const type = memory.metadata.type;
      if (!memoriesByType.has(type)) {
        memoriesByType.set(type, []);
      }
      memoriesByType.get(type)!.push(memory);
    });
    
    memoriesByType.forEach((memories, type) => {
      const totalSize = memories.reduce((sum, m) => sum + m.size, 0);
      const averageSize = memories.length > 0 ? totalSize / memories.length : 0;
      const averageImportance = memories.length > 0
        ? memories.reduce((sum, m) => sum + m.metadata.importance, 0) / memories.length
        : 0;
      
      usage[type] = {
        count: memories.length,
        totalSize,
        averageSize,
        averageImportance
      };
    });
    
    return usage;
  }

  /**
   * Reset memory integration
   */
  resetMemoryIntegration(): void {
    this.memoryVectors.clear();
    this.vectorIndex.clear();
    this.temporalIndex.clear();
    this.importanceIndex.clear();
    this.initializeIndices();
  }
}

// Singleton instance
export const indiraMemoryIntegration = new IndiraMemoryIntegration();