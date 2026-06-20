/**
 * Domain-Level Caching System
 * 
 * Provides intelligent caching strategies for domain-level operations,
 * including TTL-based caching, cache invalidation, and cache statistics.
 */

// ============================================================================
// Caching Types
// ============================================================================

export interface CacheEntry<T> {
  key: string;
  value: T;
  timestamp: number;
  ttl: number;
  hitCount: number;
}

export interface CacheConfig {
  maxSize: number;
  defaultTTL: number; // milliseconds
  enableStats: boolean;
}

export interface CacheStatistics {
  hits: number;
  misses: number;
  hitRate: number;
  totalRequests: number;
  size: number;
  maxSize: number;
}

export interface CacheKey {
  domain: string;
  operation: string;
  parameters?: any;
}

// ============================================================================
// Domain Cache Manager
// ============================================================================

class DomainCacheManager {
  private static instance: DomainCacheManager;
  private cache: Map<string, CacheEntry<any>> = new Map();
  private config: CacheConfig;
  private stats: {
    hits: number;
    misses: number;
  } = { hits: 0, misses: 0 };

  private constructor(config: Partial<CacheConfig> = {}) {
    this.config = {
      maxSize: 1000,
      defaultTTL: 60000, // 1 minute
      enableStats: true,
      ...config,
    };

    // Start periodic cleanup
    this.startCleanupInterval();
  }

  static getInstance(config?: Partial<CacheConfig>): DomainCacheManager {
    if (!DomainCacheManager.instance) {
      DomainCacheManager.instance = new DomainCacheManager(config);
    }
    return DomainCacheManager.instance;
  }

  /**
   * Generate cache key from domain, operation, and parameters
   */
  private generateKey(cacheKey: CacheKey): string {
    const params = cacheKey.parameters ? JSON.stringify(cacheKey.parameters) : '';
    return `${cacheKey.domain}:${cacheKey.operation}:${params}`;
  }

  /**
   * Check if cache entry is expired
   */
  private isExpired(entry: CacheEntry<any>): boolean {
    return Date.now() - entry.timestamp > entry.ttl;
  }

  /**
   * Get value from cache
   */
  get<T>(cacheKey: CacheKey): T | null {
    const key = this.generateKey(cacheKey);
    const entry = this.cache.get(key);

    if (!entry) {
      if (this.config.enableStats) {
        this.stats.misses++;
      }
      return null;
    }

    if (this.isExpired(entry)) {
      this.cache.delete(key);
      if (this.config.enableStats) {
        this.stats.misses++;
      }
      return null;
    }

    if (this.config.enableStats) {
      entry.hitCount++;
      this.stats.hits++;
    }

    return entry.value as T;
  }

  /**
   * Set value in cache
   */
  set<T>(cacheKey: CacheKey, value: T, ttl?: number): void {
    const key = this.generateKey(cacheKey);

    // Check if cache is full
    if (this.cache.size >= this.config.maxSize) {
      this.evictLRU();
    }

    const entry: CacheEntry<T> = {
      key,
      value,
      timestamp: Date.now(),
      ttl: ttl || this.config.defaultTTL,
      hitCount: 0,
    };

    this.cache.set(key, entry);
  }

  /**
   * Delete specific cache entry
   */
  delete(cacheKey: CacheKey): boolean {
    const key = this.generateKey(cacheKey);
    return this.cache.delete(key);
  }

  /**
   * Clear all cache entries for a domain
   */
  clearDomain(domain: string): void {
    const keysToDelete: string[] = [];
    
    this.cache.forEach((_entry, key) => {
      if (key.startsWith(`${domain}:`)) {
        keysToDelete.push(key);
      }
    });

    keysToDelete.forEach(key => this.cache.delete(key));
  }

  /**
   * Clear all cache entries
   */
  clear(): void {
    this.cache.clear();
    this.stats = { hits: 0, misses: 0 };
  }

  /**
   * Evict least recently used entry
   */
  private evictLRU(): void {
    let lruKey: string | null = null;
    let lruCount = Infinity;

    this.cache.forEach((_entry, key) => {
      if (_entry.hitCount < lruCount) {
        lruCount = _entry.hitCount;
        lruKey = key;
      }
    });

    if (lruKey) {
      this.cache.delete(lruKey);
    }
  }

  /**
   * Periodic cleanup of expired entries
   */
  private startCleanupInterval(): void {
    setInterval(() => {
      this.cleanupExpired();
    }, 60000); // Clean up every minute
  }

  /**
   * Clean up expired entries
   */
  private cleanupExpired(): void {
    const keysToDelete: string[] = [];
    
    this.cache.forEach((entry, key) => {
      if (this.isExpired(entry)) {
        keysToDelete.push(key);
      }
    });

    keysToDelete.forEach(key => this.cache.delete(key));
  }

  /**
   * Get cache statistics
   */
  getStatistics(): CacheStatistics {
    const totalRequests = this.stats.hits + this.stats.misses;
    const hitRate = totalRequests > 0 ? this.stats.hits / totalRequests : 0;

    return {
      hits: this.stats.hits,
      misses: this.stats.misses,
      hitRate,
      totalRequests,
      size: this.cache.size,
      maxSize: this.config.maxSize,
    };
  }

  /**
   * Reset statistics
   */
  resetStatistics(): void {
    this.stats = { hits: 0, misses: 0 };
  }

  /**
   * Get cache size
   */
  size(): number {
    return this.cache.size;
  }

  /**
   * Check if cache has key
   */
  has(cacheKey: CacheKey): boolean {
    const key = this.generateKey(cacheKey);
    const entry = this.cache.get(key);
    
    if (!entry) return false;
    if (this.isExpired(entry)) {
      this.cache.delete(key);
      return false;
    }
    
    return true;
  }
}

// ============================================================================
// Cache Strategies
// ============================================================================

export interface CacheStrategy {
  shouldCache(cacheKey: CacheKey, value: any): boolean;
  shouldInvalidate(cacheKey: CacheKey, value: any): boolean;
}

/**
 * Strategy: Cache only successful operations
 */
export const successOnlyStrategy: CacheStrategy = {
  shouldCache: (cacheKey, value) => {
    // Cache only if the operation was successful
    return value !== null && value !== undefined;
  },
  shouldInvalidate: (cacheKey, value) => {
    // Invalidate if operation failed
    return value === null || value === undefined;
  },
};

/**
 * Strategy: Cache based on data size
 */
export const sizeBasedStrategy = (maxSizeKB: number): CacheStrategy => {
  const maxSizeBytes = maxSizeKB * 1024;

  return {
    shouldCache: (cacheKey, value) => {
      const size = JSON.stringify(value).length;
      return size < maxSizeBytes;
    },
    shouldInvalidate: () => false,
  };
};

/**
 * Strategy: Cache based on operation type
 */
export const operationBasedStrategy = (cacheableOperations: string[]): CacheStrategy => {
  return {
    shouldCache: (cacheKey, value) => {
      return cacheableOperations.includes(cacheKey.operation);
    },
    shouldInvalidate: () => false,
  };
};

/**
 * Strategy: Cache based on domain
 */
export const domainBasedStrategy = (cacheableDomains: string[]): CacheStrategy => {
  return {
    shouldCache: (cacheKey, value) => {
      return cacheableDomains.includes(cacheKey.domain);
    },
    shouldInvalidate: () => false,
  };
};

// ============================================================================
// Cache Decorator
// ============================================================================

/**
 * Decorator to cache function results
 */
export function cacheResult(
  config?: Partial<CacheConfig> & { 
    strategy?: CacheStrategy;
    keyGenerator?: (...args: any[]) => CacheKey;
  }
) {
  return function (
    _target: any,
    propertyKey: string,
    descriptor: PropertyDescriptor
  ) {
    const originalMethod = descriptor.value;
    const cache = DomainCacheManager.getInstance(config);
    const strategy = config?.strategy;
    const keyGenerator = config?.keyGenerator;

    descriptor.value = async function (...args: any[]) {
      const cacheKey: CacheKey = keyGenerator
        ? keyGenerator(...args)
        : {
            domain: (this as any).domain || 'default',
            operation: propertyKey,
            parameters: args.length === 1 ? args[0] : args,
          };

      // Check cache
      const cachedValue = cache.get(cacheKey);
      if (cachedValue !== null) {
        return cachedValue;
      }

      // Execute original method
      const result = await originalMethod.apply(this, args);

      // Cache result based on strategy
      if (strategy) {
        if (strategy.shouldCache(cacheKey, result)) {
          cache.set(cacheKey, result);
        }
      } else {
        cache.set(cacheKey, result);
      }

      return result;
    };

    return descriptor;
  };
}

// ============================================================================
// Public API
// ============================================================================

/**
 * Get cache instance
 */
export function getDomainCache(config?: Partial<CacheConfig>): DomainCacheManager {
  return DomainCacheManager.getInstance(config);
}

/**
 * Cache a value
 */
export function cacheValue<T>(cacheKey: CacheKey, value: T, ttl?: number): void {
  return DomainCacheManager.getInstance().set(cacheKey, value, ttl);
}

/**
 * Get cached value
 */
export function getCachedValue<T>(cacheKey: CacheKey): T | null {
  return DomainCacheManager.getInstance().get<T>(cacheKey);
}

/**
 * Invalidate cache
 */
export function invalidateCache(cacheKey: CacheKey): boolean {
  return DomainCacheManager.getInstance().delete(cacheKey);
}

/**
 * Clear domain cache
 */
export function clearDomainCache(domain: string): void {
  return DomainCacheManager.getInstance().clearDomain(domain);
}

/**
 * Clear all cache
 */
export function clearAllCache(): void {
  return DomainCacheManager.getInstance().clear();
}

/**
 * Get cache statistics
 */
export function getCacheStats(): CacheStatistics {
  return DomainCacheManager.getInstance().getStatistics();
}

/**
 * Reset cache statistics
 */
export function resetCacheStats(): void {
  return DomainCacheManager.getInstance().resetStatistics();
}