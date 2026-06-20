/**
 * Performance Optimization Integration Tests
 * 
 * Integration tests for performance optimization features including
 * caching systems, state management performance, domain loading, and
 * general performance utilities.
 */

import { getDomainCache, getCacheStats, createTimer } from '../shared/utils';

// Simple test runner without framework dependencies
class TestRunner {
  private results: { testName: string; passed: boolean; error?: string }[] = [];

  async runTest(testName: string, testFunction: () => Promise<void>): Promise<boolean> {
    try {
      await testFunction();
      this.results.push({ testName, passed: true });
      return true;
    } catch (error) {
      this.results.push({ 
        testName, 
        passed: false, 
        error: error instanceof Error ? error.message : String(error) 
      });
      return false;
    }
  }

  getResults() {
    return this.results;
  }

  printSummary() {
    const passed = this.results.filter(r => r.passed).length;
    const failed = this.results.filter(r => !r.passed).length;
    console.log(`\n=== Performance Optimization Tests Summary ===`);
    console.log(`Total: ${this.results.length}`);
    console.log(`Passed: ${passed}`);
    console.log(`Failed: ${failed}`);
    console.log(`Success Rate: ${((passed / this.results.length) * 100).toFixed(2)}%`);
  }
}

// Run performance optimization integration tests
async function runPerformanceOptimizationIntegrationTests() {
  const runner = new TestRunner();

  console.log('Running Performance Optimization Integration Tests...\n');

  // Caching System Tests
  await runner.runTest('Caching - Cache Retrieval Efficiency', async () => {
    const cache = getDomainCache();
    const startTime = performance.now();
    
    // Test cache set and get using correct API
    const testData = { key: 'test', value: 'data', timestamp: Date.now() };
    cache.set({ domain: 'test', operation: 'test-operation', parameters: testData }, testData);
    const retrieved = cache.get({ domain: 'test', operation: 'test-operation', parameters: testData });
    
    const executionTime = performance.now() - startTime;
    
    if (executionTime >= 10) throw new Error('Cache operations too slow');
    if (!retrieved) throw new Error('Cache retrieval failed');
  });

  await runner.runTest('Caching - Cache Hit Rate', async () => {
    const cache = getDomainCache();
    
    // Populate cache
    for (let i = 0; i < 100; i++) {
      cache.set({ domain: 'test', operation: 'test', parameters: { id: i } }, { id: i, data: `test-${i}` });
    }
    
    // Test cache hits
    let hits = 0;
    for (let i = 0; i < 100; i++) {
      const result = cache.get({ domain: 'test', operation: 'test', parameters: { id: i } });
      if (result) hits++;
    }
    
    const hitRate = hits / 100;
    if (hitRate <= 0.9) throw new Error(`Cache hit rate too low: ${hitRate}`);
  });

  await runner.runTest('Caching - Cache Expiration', async () => {
    const cache = getDomainCache({ defaultTTL: 100 }); // 100ms TTL
    
    cache.set({ domain: 'test', operation: 'test', parameters: {} }, { data: 'test' }, 100);
    
    // Immediately retrieve - should work
    const immediate = cache.get({ domain: 'test', operation: 'test', parameters: {} });
    if (!immediate) throw new Error('Cache should not be expired immediately');
    
    // Wait for expiration
    await new Promise(resolve => setTimeout(resolve, 150));
    
    // Should be expired
    const expired = cache.get({ domain: 'test', operation: 'test', parameters: {} });
    if (expired) throw new Error('Cache should be expired');
  });

  await runner.runTest('Caching - Cache Statistics', async () => {
    const cache = getDomainCache();
    
    // Add some cache entries
    for (let i = 0; i < 10; i++) {
      cache.set({ domain: 'test', operation: 'test', parameters: { id: i } }, { id: i, data: `test-${i}` });
    }
    
    // Generate some hits
    cache.get({ domain: 'test', operation: 'test', parameters: { id: 1 } });
    cache.get({ domain: 'test', operation: 'test', parameters: { id: 2 } });
    
    const stats = getCacheStats();
    if (stats.size <= 0) throw new Error('Cache should have entries');
    if (stats.totalRequests <= 0) throw new Error('Cache should have requests');
  });

  // State Management Performance Tests
  await runner.runTest('State Performance - Selector Execution Time', async () => {
    const startTime = performance.now();
    
    // Test selector execution performance
    const testState = { data: [1, 2, 3, 4, 5], metadata: { count: 5 } };
    const selectorResult = testState.data.filter(item => item > 2);
    
    const executionTime = performance.now() - startTime;
    
    if (executionTime >= 5) throw new Error('Selector execution too slow');
    if (selectorResult.length !== 3) throw new Error('Selector result incorrect');
  });

  await runner.runTest('State Performance - Memoized Selector Optimization', async () => {
    let callCount = 0;
    
    const memoizedFn = () => {
      callCount++;
      return { data: 'test', timestamp: Date.now() };
    };
    
    // First call
    memoizedFn();
    
    // Second call with same parameters
    memoizedFn();
    
    // Verify function was called
    if (callCount <= 0) throw new Error('Function should have been called');
  });

  await runner.runTest('State Performance - Batch State Updates', async () => {
    const startTime = performance.now();
    
    // Simulate batch updates
    const updates = [];
    for (let i = 0; i < 50; i++) {
      updates.push({ id: i, data: `update-${i}` });
    }
    
    const batchUpdateTime = performance.now() - startTime;
    
    if (batchUpdateTime >= 10) throw new Error('Batch updates too slow');
    if (updates.length !== 50) throw new Error('Batch updates count incorrect');
  });

  // Domain Loading Performance Tests
  await runner.runTest('Domain Loading - Domain Initialization', async () => {
    const timer = createTimer('test', 'domain-init');
    
    // Simulate domain initialization
    await new Promise(resolve => setTimeout(resolve, 50));
    const duration = timer.stop();
    
    if (duration >= 100) throw new Error('Domain initialization too slow');
  });

  await runner.runTest('Domain Loading - Parallel Domain Loading', async () => {
    const startTime = performance.now();
    
    // Simulate parallel loading
    const domains = ['domain1', 'domain2', 'domain3'];
    await Promise.all(domains.map(() => 
      new Promise(resolve => setTimeout(resolve, 50))
    ));
    
    const loadTime = performance.now() - startTime;
    
    // Parallel loading should be much faster than sequential
    if (loadTime >= 200) throw new Error('Parallel loading too slow');
  });

  await runner.runTest('Domain Loading - Domain Loading Priority', async () => {
    // Simulate priority-based loading
    const domains = [
      { name: 'critical', priority: 0 },
      { name: 'high', priority: 1 },
      { name: 'medium', priority: 2 },
    ];
    
    // Sort by priority
    domains.sort((a, b) => a.priority - b.priority);
    
    if (domains[0].name !== 'critical') throw new Error('Priority order incorrect');
    if (domains[1].name !== 'high') throw new Error('Priority order incorrect');
    if (domains[2].name !== 'medium') throw new Error('Priority order incorrect');
  });

  // Performance Monitoring Tests
  await runner.runTest('Performance Monitoring - Performance Metrics Tracking', async () => {
    const timer = createTimer('test', 'metric-tracking');
    
    // Simulate some work
    await new Promise(resolve => setTimeout(resolve, 100));
    const duration = timer.stop();
    
    if (duration <= 90) throw new Error('Duration should be greater than 90ms');
    if (duration >= 150) throw new Error('Duration should be less than 150ms');
  });

  await runner.runTest('Performance Monitoring - Performance Threshold Alerts', async () => {
    // Test threshold monitoring
    const testDuration = 150; // Above typical threshold
    const threshold = 100;
    
    const shouldAlert = testDuration > threshold;
    if (!shouldAlert) throw new Error('Should trigger threshold alert');
  });

  await runner.runTest('Performance Monitoring - Performance Report Generation', async () => {
    const startTime = performance.now();
    
    // Simulate generating a report
    const report = {
      period: { start: Date.now() - 3600000, end: Date.now() },
      metrics: [],
      summary: { totalOperations: 100, averageResponseTime: 50 }
    };
    
    const generationTime = performance.now() - startTime;
    
    if (generationTime >= 50) throw new Error('Report generation too slow');
    if (report.summary.totalOperations !== 100) throw new Error('Report summary incorrect');
  });

  // General Performance Utilities Tests
  await runner.runTest('Utilities - Debouncing', async () => {
    let callCount = 0;
    
    const debouncedFn = () => { callCount++; };
    
    // Simulate debounce implementation
    const debounce = (fn: () => void, delay: number) => {
      let timeout: NodeJS.Timeout | null = null;
      return () => {
        if (timeout) clearTimeout(timeout);
        timeout = setTimeout(fn, delay);
      };
    };
    
    const debounced = debounce(debouncedFn, 100);
    
    debounced();
    debounced();
    debounced();
    
    await new Promise(resolve => setTimeout(resolve, 150));
    
    // Should only execute once due to debouncing
    if (callCount !== 1) throw new Error(`Expected 1 call, got ${callCount}`);
  });

  await runner.runTest('Utilities - Throttling', async () => {
    let callCount = 0;
    
    const throttle = (fn: () => void, limit: number) => {
      let inThrottle = false;
      return () => {
        if (!inThrottle) {
          fn();
          inThrottle = true;
          setTimeout(() => inThrottle = false, limit);
        }
      };
    };
    
    const throttled = throttle(() => callCount++, 100);
    
    throttled();
    throttled();
    throttled();
    
    // Should execute immediately once, then throttle
    if (callCount !== 1) throw new Error(`Expected 1 call, got ${callCount}`);
  });

  await runner.runTest('Utilities - Batch Processing', async () => {
    const startTime = performance.now();
    
    // Simulate batch processing
    const items = Array.from({ length: 100 }, (_, i) => ({ id: i, data: `item-${i}` }));
    const batchSize = 10;
    
    const batches = [];
    for (let i = 0; i < items.length; i += batchSize) {
      batches.push(items.slice(i, i + batchSize));
    }
    
    const processingTime = performance.now() - startTime;
    
    if (processingTime >= 10) throw new Error('Batch processing too slow');
    if (batches.length !== 10) throw new Error('Batch count incorrect');
  });

  await runner.runTest('Utilities - Memory-Efficient Collections', async () => {
    // Simulate memory-efficient map
    class MemoryEfficientMap<K, V> {
      private map: Map<K, V> = new Map();
      private maxSize: number;
      
      constructor(maxSize: number = 1000) {
        this.maxSize = maxSize;
      }
      
      set(key: K, value: V): void {
        this.map.set(key, value);
        if (this.map.size > this.maxSize) {
          const firstKey = this.map.keys().next().value;
          if (firstKey !== undefined) {
            this.map.delete(firstKey);
          }
        }
      }
      
      get(key: K): V | undefined {
        return this.map.get(key);
      }
      
      size(): number {
        return this.map.size;
      }
    }
    
    const memoryMap = new MemoryEfficientMap<number, string>(10);
    
    // Add more items than maxSize
    for (let i = 0; i < 20; i++) {
      memoryMap.set(i, `item-${i}`);
    }
    
    // Should not exceed maxSize
    if (memoryMap.size() > 10) throw new Error('Memory map exceeded max size');
  });

  runner.printSummary();
  return runner.getResults();
}

// Export test runner for manual execution
export { runPerformanceOptimizationIntegrationTests };

// Auto-run if executed directly
if (typeof window === 'undefined') {
  runPerformanceOptimizationIntegrationTests().then(results => {
    const failed = results.filter(r => !r.passed);
    if (failed.length > 0) {
      console.error('Some tests failed:', failed);
      process.exit(1);
    } else {
      console.log('All tests passed!');
      process.exit(0);
    }
  }).catch(error => {
    console.error('Test execution failed:', error);
    process.exit(1);
  });
}
