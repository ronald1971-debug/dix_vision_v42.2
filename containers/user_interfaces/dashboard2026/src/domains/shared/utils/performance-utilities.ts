/**
 * Performance Optimization Utilities
 * 
 * General performance optimization utilities including debouncing,
 * throttling, memory optimization, and batch processing.
 */

// ============================================================================
// Debouncing and Throttling
// ============================================================================

/**
 * Create a debounced function
 */
export function debounce<T extends (...args: any[]) => any>(
  func: T,
  wait: number
): (...args: Parameters<T>) => void {
  let timeout: NodeJS.Timeout | null = null;

  return function executedFunction(...args: Parameters<T>) {
    const later = () => {
      timeout = null;
      func(...args);
    };

    if (timeout) {
      clearTimeout(timeout);
    }
    timeout = setTimeout(later, wait);
  };
}

/**
 * Create a throttled function
 */
export function throttle<T extends (...args: any[]) => any>(
  func: T,
  limit: number
): (...args: Parameters<T>) => void {
  let inThrottle: boolean = false;

  return function executedFunction(...args: Parameters<T>) {
    if (!inThrottle) {
      func(...args);
      inThrottle = true;
      setTimeout(() => (inThrottle = false), limit);
    }
  };
}

/**
 * Create a requestAnimationFrame-based throttle
 */
export function throttleRAF<T extends (...args: any[]) => any>(
  func: T
): (...args: Parameters<T>) => void {
  let rafId: number | null = null;
  let lastArgs: Parameters<T> | null = null;

  return function executedFunction(...args: Parameters<T>) {
    lastArgs = args;

    if (rafId === null) {
      rafId = requestAnimationFrame(() => {
        if (lastArgs) {
          func(...lastArgs);
          rafId = null;
          lastArgs = null;
        }
      });
    }
  };
}

// ============================================================================
// Memory Optimization
// ============================================================================

/**
 * Create a memory-efficient map with size limits
 */
export class MemoryEfficientMap<K, V> {
  private map: Map<K, V> = new Map();
  private maxSize: number;
  private accessOrder: K[] = [];

  constructor(maxSize: number = 1000) {
    this.maxSize = maxSize;
  }

  get(key: K): V | undefined {
    const value = this.map.get(key);
    if (value !== undefined) {
      this.updateAccessOrder(key);
    }
    return value;
  }

  set(key: K, value: V): void {
    this.map.set(key, value);
    this.updateAccessOrder(key);
    this.enforceSizeLimit();
  }

  delete(key: K): boolean {
    this.accessOrder = this.accessOrder.filter(k => k !== key);
    return this.map.delete(key);
  }

  has(key: K): boolean {
    return this.map.has(key);
  }

  clear(): void {
    this.map.clear();
    this.accessOrder = [];
  }

  size(): number {
    return this.map.size;
  }

  private updateAccessOrder(key: K): void {
    this.accessOrder = this.accessOrder.filter(k => k !== key);
    this.accessOrder.push(key);
  }

  private enforceSizeLimit(): void {
    while (this.map.size > this.maxSize) {
      const oldestKey = this.accessOrder.shift();
      if (oldestKey !== undefined) {
        this.map.delete(oldestKey);
      }
    }
  }
}

/**
 * Create a memory-efficient set with size limits
 */
export class MemoryEfficientSet<T> {
  private set: Set<T> = new Set();
  private maxSize: number;
  private accessOrder: T[] = [];

  constructor(maxSize: number = 1000) {
    this.maxSize = maxSize;
  }

  add(value: T): void {
    this.set.add(value);
    this.updateAccessOrder(value);
    this.enforceSizeLimit();
  }

  has(value: T): boolean {
    return this.set.has(value);
  }

  delete(value: T): boolean {
    this.accessOrder = this.accessOrder.filter(v => v !== value);
    return this.set.delete(value);
  }

  clear(): void {
    this.set.clear();
    this.accessOrder = [];
  }

  size(): number {
    return this.set.size;
  }

  private updateAccessOrder(value: T): void {
    this.accessOrder = this.accessOrder.filter(v => v !== value);
    this.accessOrder.push(value);
  }

  private enforceSizeLimit(): void {
    while (this.set.size > this.maxSize) {
      const oldestValue = this.accessOrder.shift();
      if (oldestValue !== undefined) {
        this.set.delete(oldestValue);
      }
    }
  }
}

/**
 * Weak map for memory-sensitive caching
 */
export function createWeakCache<K extends object, V>(): WeakMap<K, V> {
  return new WeakMap<K, V>();
}

// ============================================================================
// Batch Processing
// ============================================================================

/**
 * Create a batch processor
 */
export function createBatchProcessor<T>(
  processor: (items: T[]) => Promise<void>,
  options: {
    batchSize?: number;
    delay?: number;
    maxWait?: number;
  } = {}
) {
  const { batchSize = 10, delay = 100, maxWait = 1000 } = options;
  let batch: T[] = [];
  let timer: NodeJS.Timeout | null = null;
  let maxWaitTimer: NodeJS.Timeout | null = null;

  const flush = async () => {
    if (batch.length === 0) return;

    const itemsToProcess = [...batch];
    batch = [];

    if (timer) {
      clearTimeout(timer);
      timer = null;
    }
    if (maxWaitTimer) {
      clearTimeout(maxWaitTimer);
      maxWaitTimer = null;
    }

    try {
      await processor(itemsToProcess);
    } catch (error) {
      console.error('[Batch Processor] Error processing batch:', error);
    }
  };

  const add = (item: T) => {
    batch.push(item);

    if (batch.length >= batchSize) {
      flush();
    } else if (!timer) {
      timer = setTimeout(flush, delay);
    }

    if (!maxWaitTimer) {
      maxWaitTimer = setTimeout(flush, maxWait);
    }
  };

  return {
    add,
    flush,
    size: () => batch.length,
  };
}

/**
 * Create a parallel batch processor
 */
export function createParallelBatchProcessor<T>(
  processor: (items: T[]) => Promise<void>,
  options: {
    concurrency?: number;
    batchSize?: number;
  } = {}
) {
  const { concurrency = 4, batchSize = 10 } = options;
  let queue: T[] = [];
  let activeBatches = 0;

  const processBatch = async (batchItems: T[]) => {
    activeBatches++;
    try {
      await processor(batchItems);
    } catch (error) {
      console.error('[Parallel Batch Processor] Error processing batch:', error);
    } finally {
      activeBatches--;
      processQueue();
    }
  };

  const processQueue = () => {
    while (queue.length > 0 && activeBatches < concurrency) {
      const batchItems = queue.splice(0, batchSize);
      processBatch(batchItems);
    }
  };

  const add = (item: T) => {
    queue.push(item);
    processQueue();
  };

  return {
    add,
    size: () => queue.length,
    activeBatches: () => activeBatches,
    flush: async () => {
      while (queue.length > 0 || activeBatches > 0) {
        if (queue.length > 0) {
          processQueue();
        }
        await new Promise(resolve => setTimeout(resolve, 10));
      }
    },
  };
}

// ============================================================================
// Object Pooling
// ============================================================================

/**
 * Create an object pool for reusable objects
 */
export function createObjectPool<T>(
  factory: () => T,
  reset: (obj: T) => void,
  initialSize: number = 10,
  maxSize: number = 100
) {
  const pool: T[] = [];
  const active = new Set<T>();

  // Initialize pool
  for (let i = 0; i < initialSize; i++) {
    pool.push(factory());
  }

  const acquire = (): T => {
    let obj: T;

    if (pool.length > 0) {
      obj = pool.pop()!;
    } else if (active.size < maxSize) {
      obj = factory();
    } else {
      throw new Error('Object pool exhausted');
    }

    active.add(obj);
    return obj;
  };

  const release = (obj: T): void => {
    if (active.has(obj)) {
      active.delete(obj);
      reset(obj);
      
      if (pool.length < maxSize) {
        pool.push(obj);
      }
    }
  };

  const size = () => ({
    available: pool.length,
    active: active.size,
    total: pool.length + active.size,
  });

  const clear = () => {
    pool.length = 0;
    active.clear();
  };

  return {
    acquire,
    release,
    size,
    clear,
  };
}

// ============================================================================
// Performance Measurement
// ============================================================================

/**
 * Measure function execution time
 */
export async function measurePerformance<T>(
  fn: () => Promise<T>,
  name?: string
): Promise<{ result: T; duration: number }> {
  const start = performance.now();
  const result = await fn();
  const duration = performance.now() - start;

  if (name) {
    console.log(`[Performance] ${name} took ${duration.toFixed(2)}ms`);
  }

  return { result, duration };
}

/**
 * Measure synchronous function execution time
 */
export function measureSyncPerformance<T>(
  fn: () => T,
  name?: string
): { result: T; duration: number } {
  const start = performance.now();
  const result = fn();
  const duration = performance.now() - start;

  if (name) {
    console.log(`[Performance] ${name} took ${duration.toFixed(2)}ms`);
  }

  return { result, duration };
}

/**
 * Create a performance-measured version of a function
 */
export function withPerformanceMeasurement<T extends (...args: any[]) => any>(
  fn: T,
  name?: string
): T {
  return ((...args: Parameters<T>) => {
    const start = performance.now();
    const result = fn(...args);
    const duration = performance.now() - start;

    if (name) {
      console.log(`[Performance] ${name} took ${duration.toFixed(2)}ms`);
    }

    return result;
  }) as T;
}

// ============================================================================
// Array Optimization
// ============================================================================

/**
 * Optimized array chunking
 */
export function chunkArray<T>(array: T[], size: number): T[][] {
  const chunks: T[][] = [];
  for (let i = 0; i < array.length; i += size) {
    chunks.push(array.slice(i, i + size));
  }
  return chunks;
}

/**
 * Optimized array flattening
 */
export function flattenArray<T>(array: any[]): T[] {
  const result: T[] = [];
  const stack: any[] = [...array];

  while (stack.length > 0) {
    const current = stack.pop()!;
    if (Array.isArray(current)) {
      for (let i = current.length - 1; i >= 0; i--) {
        stack.push(current[i]);
      }
    } else {
      result.push(current as T);
    }
  }

  return result;
}

/**
 * Optimized array unique
 */
export function uniqueArray<T>(array: T[]): T[] {
  return Array.from(new Set(array));
}

/**
 * Optimized array intersection
 */
export function intersectArrays<T>(...arrays: T[][]): T[] {
  if (arrays.length === 0) return [];
  if (arrays.length === 1) return arrays[0];

  const [first, ...rest] = arrays;

  return first.filter(item => rest.every(arr => new Set(arr).has(item)));
}