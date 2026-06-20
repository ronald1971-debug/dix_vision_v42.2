/**
 * State Management Performance Optimization
 * 
 * Provides performance optimization utilities for Zustand stores,
 * including memoization strategies, optimized selectors, and
 * store performance monitoring.
 */

import { StateCreator } from 'zustand';

// ============================================================================
// Performance Types
// ============================================================================

export interface SelectorPerformanceStats {
  selectorName: string;
  callCount: number;
  totalTime: number;
  averageTime: number;
  lastCallTime: number;
}

export interface StorePerformanceConfig {
  enableSelectorTracking: boolean;
  enableStateDiffing: boolean;
  maxTrackedSelectors: number;
}

// ============================================================================
// Selector Performance Tracking
// ============================================================================

class SelectorPerformanceTracker {
  private static instance: SelectorPerformanceTracker;
  private stats: Map<string, SelectorPerformanceStats> = new Map();
  private config: StorePerformanceConfig = {
    enableSelectorTracking: true,
    enableStateDiffing: false,
    maxTrackedSelectors: 50,
  };

  private constructor() {}

  static getInstance(): SelectorPerformanceTracker {
    if (!SelectorPerformanceTracker.instance) {
      SelectorPerformanceTracker.instance = new SelectorPerformanceTracker();
    }
    return SelectorPerformanceTracker.instance;
  }

  setConfig(config: Partial<StorePerformanceConfig>): void {
    this.config = { ...this.config, ...config };
  }

  trackSelector(selectorName: string, executionTime: number): void {
    if (!this.config.enableSelectorTracking) return;

    const stats = this.stats.get(selectorName) || {
      selectorName,
      callCount: 0,
      totalTime: 0,
      averageTime: 0,
      lastCallTime: 0,
    };

    stats.callCount++;
    stats.totalTime += executionTime;
    stats.averageTime = stats.totalTime / stats.callCount;
    stats.lastCallTime = executionTime;

    this.stats.set(selectorName, stats);

    // Prune old selectors if we exceed limit
    if (this.stats.size > this.config.maxTrackedSelectors) {
      this.pruneOldSelectors();
    }
  }

  private pruneOldSelectors(): void {
    const entries = Array.from(this.stats.entries());
    entries.sort((a, b) => b[1].lastCallTime - a[1].lastCallTime);
    
    const toKeep = entries.slice(0, this.config.maxTrackedSelectors);
    this.stats = new Map(toKeep);
  }

  getStats(selectorName: string): SelectorPerformanceStats | undefined {
    return this.stats.get(selectorName);
  }

  getAllStats(): SelectorPerformanceStats[] {
    return Array.from(this.stats.values());
  }

  resetStats(): void {
    this.stats.clear();
  }
}

// ============================================================================
// Performance-Optimized Selector
// ============================================================================

/**
 * Create a performance-tracked selector
 */
export function createOptimizedSelector<T>(
  selectorName: string,
  selector: (state: any) => T
): (state: any) => T {
  const tracker = SelectorPerformanceTracker.getInstance();

  return (state: any) => {
    const startTime = performance.now();
    const result = selector(state);
    const executionTime = performance.now() - startTime;

    tracker.trackSelector(selectorName, executionTime);

    return result;
  };
}

/**
 * Create a memoized selector with custom equality check
 */
export function createMemoizedSelector<T>(
  selector: (state: any) => T,
  equalityCheck: (a: T, b: T) => boolean = (a, b) => a === b
): (state: any) => T {
  let lastState: any = null;
  let lastResult: T;

  return (state: any) => {
    if (lastState === null) {
      lastState = state;
      lastResult = selector(state);
      return lastResult;
    }

    const newResult = selector(state);
    if (equalityCheck(lastResult, newResult)) {
      return lastResult;
    }

    lastState = state;
    lastResult = newResult;
    return newResult;
  };
}

/**
 * Create a shallow-memoized selector for object/array results
 */
export function createShallowMemoizedSelector<T>(
  selectorName: string,
  selector: (state: any) => T
): (state: any) => T {
  const optimizedSelector = createOptimizedSelector(selectorName, selector);
  let lastResult: T | null = null;

  return (state: any) => {
    const newResult = optimizedSelector(state);
    
    if (lastResult === null) {
      lastResult = newResult;
      return newResult;
    }

    // Shallow comparison
    if (typeof newResult === 'object' && typeof lastResult === 'object') {
      const keysA = Object.keys(newResult as any);
      const keysB = Object.keys(lastResult as any);
      
      if (keysA.length !== keysB.length) {
        lastResult = newResult;
        return newResult;
      }

      for (const key of keysA) {
        if ((newResult as any)[key] !== (lastResult as any)[key]) {
          lastResult = newResult;
          return newResult;
        }
      }

      return lastResult;
    }

    if (newResult !== lastResult) {
      lastResult = newResult;
    }

    return lastResult;
  };
}

// ============================================================================
// Performance Middleware for Zustand
// ============================================================================

export interface PerformanceStoreState {
  performance: {
    selectorStats: () => SelectorPerformanceStats[];
    resetPerformanceStats: () => void;
  };
}

export function withPerformance<T>(
  config: Partial<StorePerformanceConfig>
) {
  return (configCreator: StateCreator<T>): StateCreator<T> => {
    const tracker = SelectorPerformanceTracker.getInstance();
    tracker.setConfig(config);

    return (set, get, api) => {
      const createdStore = configCreator(set, get, api);

      return {
        ...createdStore,
        performance: {
          selectorStats: () => tracker.getAllStats(),
          resetPerformanceStats: () => tracker.resetStats(),
        },
      };
    };
  };
}

// ============================================================================
// State Diffing for Debugging
// ============================================================================

/**
 * Generate a diff between two state objects
 */
export function generateStateDiff<T>(
  oldState: T,
  newState: T
): Array<{
  path: string;
  oldValue: any;
  newValue: any;
}> {
  const diffs: Array<{ path: string; oldValue: any; newValue: any }> = [];

  function compare(a: any, b: any, path: string = '') {
    if (a === b) return;

    if (typeof a !== typeof b) {
      diffs.push({ path, oldValue: a, newValue: b });
      return;
    }

    if (typeof a !== 'object' || a === null || b === null) {
      if (a !== b) {
        diffs.push({ path, oldValue: a, newValue: b });
      }
      return;
    }

    const keysA = Object.keys(a);
    const keysB = Object.keys(b);

    for (const key of keysA) {
      if (!keysB.includes(key)) {
        diffs.push({ path: `${path}.${key}`, oldValue: a[key], newValue: undefined });
      } else {
        compare(a[key], b[key], `${path}.${key}`);
      }
    }

    for (const key of keysB) {
      if (!keysA.includes(key)) {
        diffs.push({ path: `${path}.${key}`, oldValue: undefined, newValue: b[key] });
      }
    }
  }

  compare(oldState, newState);
  return diffs;
}

/**
 * Log state changes for debugging
 */
export function logStateChanges<T>(
  storeName: string,
  oldState: T,
  newState: T
): void {
  const diffs = generateStateDiff(oldState, newState);
  
  if (diffs.length > 0) {
    console.log(`[State Change] ${storeName}`, {
      changes: diffs,
      timestamp: Date.now(),
    });
  }
}

// ============================================================================
// Public API
// ============================================================================

/**
 * Get selector performance stats
 */
export function getSelectorStats(): SelectorPerformanceStats[] {
  return SelectorPerformanceTracker.getInstance().getAllStats();
}

/**
 * Reset selector performance stats
 */
export function resetSelectorStats(): void {
  return SelectorPerformanceTracker.getInstance().resetStats();
}

/**
 * Configure performance tracking
 */
export function configurePerformanceTracking(config: Partial<StorePerformanceConfig>): void {
  return SelectorPerformanceTracker.getInstance().setConfig(config);
}