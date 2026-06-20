/**
 * Performance-Optimized Domain Loading
 * 
 * Provides optimized domain loading strategies including prefetching,
 * parallel loading, and intelligent caching for improved application startup performance.
 */

import { PerformanceTimer } from './performance-monitor';

// ============================================================================
// Domain Loading Configuration
// ============================================================================

export interface DomainLoadConfig {
  domain: string;
  priority: 'critical' | 'high' | 'medium' | 'low';
  prefetch?: boolean;
  preload?: boolean;
  timeout?: number;
}

export interface DomainLoadResult {
  domain: string;
  success: boolean;
  loadTime: number;
  timestamp: number;
  error?: string;
}

// ============================================================================
// Optimized Domain Loader
// ============================================================================

class OptimizedDomainLoader {
  private static instance: OptimizedDomainLoader;
  private loadedDomains: Set<string> = new Set();
  private loadingDomains: Map<string, Promise<any>> = new Map();
  private domainConfigs: Map<string, DomainLoadConfig> = new Map();
  private loadHistory: DomainLoadResult[] = [];
  private prefetchQueue: Set<string> = new Set();
  private maxHistorySize: number = 100;

  private constructor() {
    this.setupPrefetching();
  }

  static getInstance(): OptimizedDomainLoader {
    if (!OptimizedDomainLoader.instance) {
      OptimizedDomainLoader.instance = new OptimizedDomainLoader();
    }
    return OptimizedDomainLoader.instance;
  }

  /**
   * Configure domain loading behavior
   */
  configureDomain(config: DomainLoadConfig): void {
    this.domainConfigs.set(config.domain, config);

    // Preload if configured
    if (config.preload && !this.loadedDomains.has(config.domain)) {
      this.preloadDomain(config.domain);
    }

    // Prefetch if configured
    if (config.prefetch && !this.prefetchQueue.has(config.domain)) {
      this.prefetchQueue.add(config.domain);
    }
  }

  /**
   * Load a domain with performance tracking
   */
  async loadDomain(domain: string): Promise<DomainLoadResult> {
    const timer = new PerformanceTimer('domain-loader', `load-${domain}`);

    // Check if already loading
    if (this.loadingDomains.has(domain)) {
      await this.loadingDomains.get(domain);
      return this.createSuccessResult(domain, timer.stop());
    }

    // Check if already loaded
    if (this.loadedDomains.has(domain)) {
      return this.createSuccessResult(domain, timer.stop());
    }

    const config = this.domainConfigs.get(domain) || {
      domain,
      priority: 'medium',
      timeout: 10000,
    };

    // Create loading promise
    const loadPromise = this.loadDomainInternal(domain, config);
    this.loadingDomains.set(domain, loadPromise);

    try {
      await loadPromise;
      this.loadedDomains.add(domain);
      const result = this.createSuccessResult(domain, timer.stop());
      this.recordLoadResult(result);
      return result;
    } catch (error) {
      const result = this.createErrorResult(domain, timer.stop(), error);
      this.recordLoadResult(result);
      throw error;
    } finally {
      this.loadingDomains.delete(domain);
    }
  }

  /**
   * Internal domain loading implementation
   */
  private async loadDomainInternal(domain: string, _config: DomainLoadConfig): Promise<void> {
    // Dynamic import based on domain
    const domainModule = await import(`../${domain}/index.ts`);
    
    // Initialize domain if needed
    if (domainModule.initialize) {
      await domainModule.initialize();
    }
  }

  /**
   * Preload a domain asynchronously
   */
  async preloadDomain(domain: string): Promise<void> {
    try {
      await this.loadDomain(domain);
    } catch (error) {
      console.warn(`[Domain Loader] Failed to preload domain ${domain}:`, error);
    }
  }

  /**
   * Setup automatic prefetching
   */
  private setupPrefetching(): void {
    // Prefetch after initial load
    if (typeof window !== 'undefined') {
      setTimeout(() => {
        this.processPrefetchQueue();
      }, 2000);
    }
  }

  /**
   * Process prefetch queue by priority
   */
  private async processPrefetchQueue(): Promise<void> {
    const domains = Array.from(this.prefetchQueue);
    
    // Sort by priority
    const sortedDomains = domains.sort((a, b) => {
      const configA = this.domainConfigs.get(a);
      const configB = this.domainConfigs.get(b);
      const priorityOrder = { critical: 0, high: 1, medium: 2, low: 3 };
      
      return (priorityOrder[configA?.priority || 'medium'] || 2) - 
             (priorityOrder[configB?.priority || 'medium'] || 2);
    });

    // Prefetch in parallel batches
    const batchSize = 3;
    for (let i = 0; i < sortedDomains.length; i += batchSize) {
      const batch = sortedDomains.slice(i, i + batchSize);
      await Promise.all(batch.map(domain => this.preloadDomain(domain)));
    }

    this.prefetchQueue.clear();
  }

  /**
   * Load multiple domains in parallel
   */
  async loadDomainsParallel(domains: string[]): Promise<DomainLoadResult[]> {
    const timer = new PerformanceTimer('domain-loader', 'parallel-load');
    
    const results = await Promise.all(
      domains.map(domain => this.loadDomain(domain))
    );

    timer.stop();
    return results;
  }

  /**
   * Load domains sequentially (for dependencies)
   */
  async loadDomainsSequential(domains: string[]): Promise<DomainLoadResult[]> {
    const timer = new PerformanceTimer('domain-loader', 'sequential-load');
    const results: DomainLoadResult[] = [];

    for (const domain of domains) {
      const result = await this.loadDomain(domain);
      results.push(result);
    }

    timer.stop();
    return results;
  }

  /**
   * Check if domain is loaded
   */
  isDomainLoaded(domain: string): boolean {
    return this.loadedDomains.has(domain);
  }

  /**
   * Get loading status
   */
  getLoadingStatus(domain: string): 'not-loaded' | 'loading' | 'loaded' {
    if (this.loadedDomains.has(domain)) return 'loaded';
    if (this.loadingDomains.has(domain)) return 'loading';
    return 'not-loaded';
  }

  /**
   * Get load history
   */
  getLoadHistory(domain?: string): DomainLoadResult[] {
    if (domain) {
      return this.loadHistory.filter(r => r.domain === domain);
    }
    return [...this.loadHistory];
  }

  /**
   * Clear loaded domains (useful for testing)
   */
  clearLoadedDomains(): void {
    this.loadedDomains.clear();
    this.loadingDomains.clear();
  }

  /**
   * Create success result
   */
  private createSuccessResult(domain: string, loadTime: number): DomainLoadResult {
    return {
      domain,
      success: true,
      loadTime,
      timestamp: Date.now(),
    };
  }

  /**
   * Create error result
   */
  private createErrorResult(domain: string, loadTime: number, error: any): DomainLoadResult {
    return {
      domain,
      success: false,
      loadTime,
      timestamp: Date.now(),
      error: error instanceof Error ? error.message : String(error),
    };
  }

  /**
   * Record load result
   */
  private recordLoadResult(result: DomainLoadResult): void {
    this.loadHistory.push(result);
    
    // Limit history size
    if (this.loadHistory.length > this.maxHistorySize) {
      this.loadHistory.shift();
    }
  }
}

// ============================================================================
// Public API
// ============================================================================

/**
 * Configure domain loading
 */
export function configureDomainLoading(config: DomainLoadConfig): void {
  return OptimizedDomainLoader.getInstance().configureDomain(config);
}

/**
 * Load a domain
 */
export function loadDomainOptimized(domain: string): Promise<DomainLoadResult> {
  return OptimizedDomainLoader.getInstance().loadDomain(domain);
}

/**
 * Load domains in parallel
 */
export function loadDomainsParallel(domains: string[]): Promise<DomainLoadResult[]> {
  return OptimizedDomainLoader.getInstance().loadDomainsParallel(domains);
}

/**
 * Check if domain is loaded
 */
export function isDomainLoadedOptimized(domain: string): boolean {
  return OptimizedDomainLoader.getInstance().isDomainLoaded(domain);
}

/**
 * Get domain loading status
 */
export function getDomainLoadingStatusOptimized(domain: string): 'not-loaded' | 'loading' | 'loaded' {
  return OptimizedDomainLoader.getInstance().getLoadingStatus(domain);
}

/**
 * Get domain load history
 */
export function getDomainLoadHistoryOptimized(domain?: string): DomainLoadResult[] {
  return OptimizedDomainLoader.getInstance().getLoadHistory(domain);
}