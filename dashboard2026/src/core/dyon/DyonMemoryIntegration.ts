/**
 * DYON Memory Integration with Smart Caching
 * DIX VISION v42.2 - Phase 9: DYON Architecture Modernization (Weeks 25-28)
 * 
 * Production-grade memory integration system for DYON engineering intelligence with
 * smart caching, multi-tier storage, eviction policies, and performance optimization.
 */

export interface EngineeringMemory {
  id: string;
  domain: string;
  type: 'architectural' | 'procedural' | 'episodic' | 'semantic';
  content: any;
  metadata: {
    importance: number; // 0-1 scale
    accessCount: number;
    lastAccess: number;
    creationTime: number;
    size: number; // in bytes
    tags: string[];
    associations: string[];
  };
  cacheLevel: 'hot' | 'warm' | 'cold';
}

export interface CacheEntry {
  memoryId: string;
  cachedAt: number;
  expiresAt: number;
  size: number;
  hitCount: number;
  missCount: number;
  level: 'L1' | 'L2' | 'L3';
}

export interface CacheMetrics {
  totalMemories: number;
  totalCacheSize: number;
  cacheHitRate: number;
  averageAccessTime: number;
  evictionCount: number;
  cacheLevels: {
    L1: { size: number; entries: number; hitRate: number };
    L2: { size: number; entries: number; hitRate: number };
    L3: { size: number; entries: number; hitRate: number };
  };
  memoryDistribution: Map<string, number>;
  lastCalculated: number;
}

export interface CacheConfig {
  maxSize: number; // in bytes
  maxEntries: number;
  ttl: number; // time to live in milliseconds
  evictionPolicy: 'LRU' | 'LFU' | 'FIFO' | 'adaptive';
  compressionEnabled: boolean;
  tieredCaching: boolean;
  preloadThreshold: number;
}

class DyonMemoryIntegration {
  private memories: Map<string, EngineeringMemory> = new Map();
  private cache: Map<string, CacheEntry> = new Map();
  private metrics: CacheMetrics = {
    totalMemories: 0,
    totalCacheSize: 0,
    cacheHitRate: 0,
    averageAccessTime: 0,
    evictionCount: 0,
    cacheLevels: {
      L1: { size: 0, entries: 0, hitRate: 0 },
      L2: { size: 0, entries: 0, hitRate: 0 },
      L3: { size: 0, entries: 0, hitRate: 0 }
    },
    memoryDistribution: new Map(),
    lastCalculated: Date.now()
  };
  private config: CacheConfig;
  private l1Cache: Map<string, CacheEntry> = new Map();
  private l2Cache: Map<string, CacheEntry> = new Map();
  private l3Cache: Map<string, CacheEntry> = new Map();
  private isInitialized: boolean = false;
  private cleanupInterval?: number;

  constructor(config: Partial<CacheConfig> = {}) {
    this.config = {
      maxSize: config.maxSize || 100 * 1024 * 1024, // 100MB default
      maxEntries: config.maxEntries || 10000,
      ttl: config.ttl || 3600000, // 1 hour default
      evictionPolicy: config.evictionPolicy || 'adaptive',
      compressionEnabled: config.compressionEnabled || true,
      tieredCaching: config.tieredCaching || true,
      preloadThreshold: config.preloadThreshold || 0.8
    };
  }

  /**
   * Initialize the memory integration system
   */
  initialize(): void {
    if (this.isInitialized) {
      console.warn('DYON Memory Integration already initialized');
      return;
    }

    console.log('Initializing DYON Memory Integration with Smart Caching...');
    
    // Start cleanup cycle
    this.startCleanupCycle();
    
    this.isInitialized = true;
    console.log('DYON Memory Integration initialized successfully');
  }

  /**
   * Store a memory with smart caching
   */
  async storeMemory(memory: EngineeringMemory): Promise<void> {
    // Calculate memory size
    memory.metadata.size = this.calculateMemorySize(memory);
    
    // Determine cache level based on importance and access patterns
    memory.cacheLevel = this.determineCacheLevel(memory);
    
    // Store in main memory
    this.memories.set(memory.id, memory);
    this.metrics.totalMemories = this.memories.size;
    
    // Update memory distribution
    const domainCount = this.metrics.memoryDistribution.get(memory.domain) || 0;
    this.metrics.memoryDistribution.set(memory.domain, domainCount + 1);
    
    // Cache based on tier
    if (this.config.tieredCaching) {
      await this.cacheMemory(memory);
    }
    
    console.log(`Memory stored: ${memory.id} in domain ${memory.domain} with size ${memory.metadata.size} bytes`);
  }

  /**
   * Retrieve a memory with cache lookup
   */
  async retrieveMemory(memoryId: string): Promise<EngineeringMemory | null> {
    const startTime = Date.now();
    
    // Check cache first
    const cached = this.lookupCache(memoryId);
    if (cached) {
      const memory = this.memories.get(memoryId);
      if (memory) {
        // Update access metadata
        memory.metadata.accessCount++;
        memory.metadata.lastAccess = Date.now();
        
        // Update cache hit rate
        this.updateCacheMetrics(true, Date.now() - startTime);
        
        console.log(`Cache hit: ${memoryId}`);
        return memory;
      }
    }
    
    // Cache miss - check main memory
    const memory = this.memories.get(memoryId);
    if (memory) {
      memory.metadata.accessCount++;
      memory.metadata.lastAccess = Date.now();
      
      // Promote to cache if appropriate
      if (memory.metadata.importance > 0.7) {
        await this.cacheMemory(memory);
      }
      
      // Update cache hit rate
      this.updateCacheMetrics(false, Date.now() - startTime);
      
      console.log(`Cache miss (found in memory): ${memoryId}`);
      return memory;
    }
    
    // Update cache hit rate
    this.updateCacheMetrics(false, Date.now() - startTime);
    
    console.log(`Memory not found: ${memoryId}`);
    return null;
  }

  /**
   * Cache a memory in appropriate tier
   */
  private async cacheMemory(memory: EngineeringMemory): Promise<void> {
    const cacheEntry: CacheEntry = {
      memoryId: memory.id,
      cachedAt: Date.now(),
      expiresAt: Date.now() + this.config.ttl,
      size: memory.metadata.size,
      hitCount: 0,
      missCount: 0,
      level: this.determineCacheTier(memory)
    };
    
    // Check cache capacity
    await this.checkCacheCapacity(cacheEntry.level);
    
    // Add to appropriate cache tier
    switch (cacheEntry.level) {
      case 'L1':
        this.l1Cache.set(memory.id, cacheEntry);
        this.metrics.cacheLevels.L1.size += cacheEntry.size;
        this.metrics.cacheLevels.L1.entries++;
        break;
      case 'L2':
        this.l2Cache.set(memory.id, cacheEntry);
        this.metrics.cacheLevels.L2.size += cacheEntry.size;
        this.metrics.cacheLevels.L2.entries++;
        break;
      case 'L3':
        this.l3Cache.set(memory.id, cacheEntry);
        this.metrics.cacheLevels.L3.size += cacheEntry.size;
        this.metrics.cacheLevels.L3.entries++;
        break;
    }
    
    this.metrics.totalCacheSize += cacheEntry.size;
    
    console.log(`Cached memory ${memory.id} in ${cacheEntry.level}`);
  }

  /**
   * Look up a memory in cache
   */
  private lookupCache(memoryId: string): CacheEntry | null {
    // Check L1 first (fastest)
    let entry = this.l1Cache.get(memoryId);
    if (entry && !this.isExpired(entry)) {
      entry.hitCount++;
      return entry;
    }
    
    // Check L2
    entry = this.l2Cache.get(memoryId);
    if (entry && !this.isExpired(entry)) {
      entry.hitCount++;
      // Promote to L1 on hit
      this.promoteToL1(memoryId, entry);
      return entry;
    }
    
    // Check L3
    entry = this.l3Cache.get(memoryId);
    if (entry && !this.isExpired(entry)) {
      entry.hitCount++;
      // Promote to L2 on hit
      this.promoteToL2(memoryId, entry);
      return entry;
    }
    
    return null;
  }

  /**
   * Determine cache level for a memory
   */
  private determineCacheLevel(memory: EngineeringMemory): 'hot' | 'warm' | 'cold' {
    if (memory.metadata.importance > 0.8 && memory.metadata.accessCount > 10) {
      return 'hot';
    } else if (memory.metadata.importance > 0.5 && memory.metadata.accessCount > 3) {
      return 'warm';
    }
    return 'cold';
  }

  /**
   * Determine cache tier for a memory
   */
  private determineCacheTier(memory: EngineeringMemory): 'L1' | 'L2' | 'L3' {
    if (memory.cacheLevel === 'hot') return 'L1';
    if (memory.cacheLevel === 'warm') return 'L2';
    return 'L3';
  }

  /**
   * Check if cache entry is expired
   */
  private isExpired(entry: CacheEntry): boolean {
    return Date.now() > entry.expiresAt;
  }

  /**
   * Promote memory to L1 cache
   */
  private promoteToL1(memoryId: string, entry: CacheEntry): void {
    // Remove from current tier
    this.l2Cache.delete(memoryId);
    this.metrics.cacheLevels.L2.size -= entry.size;
    this.metrics.cacheLevels.L2.entries--;
    
    // Update entry level
    entry.level = 'L1';
    
    // Add to L1
    this.l1Cache.set(memoryId, entry);
    this.metrics.cacheLevels.L1.size += entry.size;
    this.metrics.cacheLevels.L1.entries++;
    
    console.log(`Promoted ${memoryId} to L1 cache`);
  }

  /**
   * Promote memory to L2 cache
   */
  private promoteToL2(memoryId: string, entry: CacheEntry): void {
    // Remove from L3
    this.l3Cache.delete(memoryId);
    this.metrics.cacheLevels.L3.size -= entry.size;
    this.metrics.cacheLevels.L3.entries--;
    
    // Update entry level
    entry.level = 'L2';
    
    // Add to L2
    this.l2Cache.set(memoryId, entry);
    this.metrics.cacheLevels.L2.size += entry.size;
    this.metrics.cacheLevels.L2.entries++;
    
    console.log(`Promoted ${memoryId} to L2 cache`);
  }

  /**
   * Check cache capacity and evict if necessary
   */
  private async checkCacheCapacity(tier: 'L1' | 'L2' | 'L3'): Promise<void> {
    const tierConfig = {
      L1: { maxSize: this.config.maxSize * 0.1, maxEntries: this.config.maxEntries * 0.1 },
      L2: { maxSize: this.config.maxSize * 0.3, maxEntries: this.config.maxEntries * 0.3 },
      L3: { maxSize: this.config.maxSize * 0.6, maxEntries: this.config.maxEntries * 0.6 }
    };
    
    const config = tierConfig[tier];
    const metrics = this.metrics.cacheLevels[tier];
    
    // Check size capacity
    if (metrics.size > config.maxSize * this.config.preloadThreshold) {
      await this.evictFromCache(tier, 'size');
    }
    
    // Check entry capacity
    if (metrics.entries > config.maxEntries * this.config.preloadThreshold) {
      await this.evictFromCache(tier, 'entries');
    }
  }

  /**
   * Evict entries from cache based on policy
   */
  private async evictFromCache(tier: 'L1' | 'L2' | 'L3', reason: 'size' | 'entries'): Promise<void> {
    const cache = tier === 'L1' ? this.l1Cache : tier === 'L2' ? this.l2Cache : this.l3Cache;
    
    if (cache.size === 0) return;
    
    const entries = Array.from(cache.entries());
    let entriesToEvict: [string, CacheEntry][] = [];
    
    switch (this.config.evictionPolicy) {
      case 'LRU':
        // Sort by last accessed (least recently used first)
        entriesToEvict = entries.sort((a, b) => a[1].cachedAt - b[1].cachedAt).slice(0, Math.floor(cache.size * 0.1));
        break;
      case 'LFU':
        // Sort by hit count (least frequently used first)
        entriesToEvict = entries.sort((a, b) => a[1].hitCount - b[1].hitCount).slice(0, Math.floor(cache.size * 0.1));
        break;
      case 'FIFO':
        // Sort by cache time (oldest first)
        entriesToEvict = entries.sort((a, b) => a[1].cachedAt - b[1].cachedAt).slice(0, Math.floor(cache.size * 0.1));
        break;
      case 'adaptive':
        // Combine LRU and importance
        entriesToEvict = entries
          .sort((a, b) => {
            const scoreA = (a[1].cachedAt / Date.now()) * a[1].hitCount;
            const scoreB = (b[1].cachedAt / Date.now()) * b[1].hitCount;
            return scoreA - scoreB;
          })
          .slice(0, Math.floor(cache.size * 0.1));
        break;
    }
    
    // Evict selected entries
    entriesToEvict.forEach(([memoryId, entry]) => {
      cache.delete(memoryId);
      this.metrics.cacheLevels[tier].size -= entry.size;
      this.metrics.cacheLevels[tier].entries--;
      this.metrics.totalCacheSize -= entry.size;
      this.metrics.evictionCount++;
    });
    
    console.log(`Evicted ${entriesToEvict.length} entries from ${tier} cache due to ${reason}`);
  }

  /**
   * Calculate memory size
   */
  private calculateMemorySize(memory: EngineeringMemory): number {
    return JSON.stringify(memory).length * 2; // Approximate bytes (UTF-16)
  }

  /**
   * Update cache metrics
   */
  private updateCacheMetrics(hit: boolean, accessTime: number): void {
    const totalAccesses = this.metrics.cacheHitRate === 0 ? 1 : 
      this.metrics.cacheHitRate * 100 + 1;
    
    if (hit) {
      this.metrics.cacheHitRate = (this.metrics.cacheHitRate * totalAccesses + 1) / (totalAccesses + 1);
    } else {
      this.metrics.cacheHitRate = (this.metrics.cacheHitRate * totalAccesses) / (totalAccesses + 1);
    }
    
    this.metrics.averageAccessTime = 
      (this.metrics.averageAccessTime * totalAccesses + accessTime) / (totalAccesses + 1);
  }

  /**
   * Start cleanup cycle
   */
  private startCleanupCycle(): void {
    this.cleanupInterval = window.setInterval(() => {
      this.cleanupExpired();
      this.optimizeCache();
    }, 60000); // Clean up every minute
  }

  /**
   * Clean up expired cache entries
   */
  private cleanupExpired(): void {
    const cleanup = (cache: Map<string, CacheEntry>, tier: 'L1' | 'L2' | 'L3') => {
      const expired = Array.from(cache.entries()).filter(([_, entry]) => this.isExpired(entry));
      
      expired.forEach(([memoryId, entry]) => {
        cache.delete(memoryId);
        this.metrics.cacheLevels[tier].size -= entry.size;
        this.metrics.cacheLevels[tier].entries--;
        this.metrics.totalCacheSize -= entry.size;
      });
      
      if (expired.length > 0) {
        console.log(`Cleaned up ${expired.length} expired entries from ${tier} cache`);
      }
    };
    
    cleanup(this.l1Cache, 'L1');
    cleanup(this.l2Cache, 'L2');
    cleanup(this.l3Cache, 'L3');
  }

  /**
   * Optimize cache performance
   */
  private optimizeCache(): void {
    // Calculate hit rates per tier
    const calculateTierHitRate = (cache: Map<string, CacheEntry>) => {
      const entries = Array.from(cache.values());
      if (entries.length === 0) return 0;
      
      const totalHits = entries.reduce((sum, entry) => sum + entry.hitCount, 0);
      const totalAccesses = entries.reduce((sum, entry) => sum + entry.hitCount + entry.missCount, 0);
      
      return totalAccesses > 0 ? totalHits / totalAccesses : 0;
    };
    
    this.metrics.cacheLevels.L1.hitRate = calculateTierHitRate(this.l1Cache);
    this.metrics.cacheLevels.L2.hitRate = calculateTierHitRate(this.l2Cache);
    this.metrics.cacheLevels.L3.hitRate = calculateTierHitRate(this.l3Cache);
    
    this.metrics.lastCalculated = Date.now();
  }

  /**
   * Get cache metrics
   */
  getMetrics(): CacheMetrics {
    return { ...this.metrics };
  }

  /**
   * Get memories by domain
   */
  getMemoriesByDomain(domain: string): EngineeringMemory[] {
    return Array.from(this.memories.values()).filter(memory => memory.domain === domain);
  }

  /**
   * Get memories by type
   */
  getMemoriesByType(type: EngineeringMemory['type']): EngineeringMemory[] {
    return Array.from(this.memories.values()).filter(memory => memory.type === type);
  }

  /**
   * Get memories by tags
   */
  getMemoriesByTags(tags: string[]): EngineeringMemory[] {
    return Array.from(this.memories.values()).filter(memory =>
      tags.some(tag => memory.metadata.tags.includes(tag))
    );
  }

  /**
   * Stop cleanup cycle
   */
  stopCleanup(): void {
    if (this.cleanupInterval) {
      clearInterval(this.cleanupInterval);
      this.cleanupInterval = undefined;
    }
  }

  /**
   * Reset the memory integration system
   */
  reset(): void {
    this.memories.clear();
    this.cache.clear();
    this.l1Cache.clear();
    this.l2Cache.clear();
    this.l3Cache.clear();
    
    this.metrics = {
      totalMemories: 0,
      totalCacheSize: 0,
      cacheHitRate: 0,
      averageAccessTime: 0,
      evictionCount: 0,
      cacheLevels: {
        L1: { size: 0, entries: 0, hitRate: 0 },
        L2: { size: 0, entries: 0, hitRate: 0 },
        L3: { size: 0, entries: 0, hitRate: 0 }
      },
      memoryDistribution: new Map(),
      lastCalculated: Date.now()
    };
    
    console.log('DYON Memory Integration reset');
  }
}

// Singleton instance
export const dyonMemoryIntegration = new DyonMemoryIntegration();

export default DyonMemoryIntegration;