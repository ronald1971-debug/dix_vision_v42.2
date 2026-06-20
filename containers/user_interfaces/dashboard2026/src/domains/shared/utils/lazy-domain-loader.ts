/**
 * Lazy Domain Loading Utility
 * 
 * Provides utilities for lazy loading domains based on usage patterns
 * and dependencies, optimizing bundle size and initial load time.
 */

import { getLoadOrder, DOMAIN_DEPENDENCIES } from './dependency-graph';

// ============================================================================
// Domain Loading Types
// ============================================================================

interface DomainLoadConfig {
  /**
   * The domain to load
   */
  domain: string;
  
  /**
   * Priority of the domain (higher = load sooner)
   */
  priority: 'critical' | 'high' | 'normal' | 'low';
  
  /**
   * Whether the domain should be preloaded when dependencies load
   */
  preloadDependents?: boolean;
  
  /**
   * Custom load function for the domain
   */
  loader?: () => Promise<any>;
}

interface DomainLoadResult {
  domain: string;
  success: boolean;
  error?: string;
  loadTime: number;
  timestamp: number;
}

type DomainLoadStatus = 'unloaded' | 'loading' | 'loaded' | 'failed';

interface DomainLoadEntry {
  status: DomainLoadStatus;
  config: DomainLoadConfig;
  loadPromise?: Promise<DomainLoadResult>;
  result?: DomainLoadResult;
  dependents: string[];
}

// ============================================================================
// Domain Load Manager Class
// ============================================================================

class DomainLoadManager {
  private static instance: DomainLoadManager;
  private domains: Map<string, DomainLoadEntry> = new Map();
  private loadOrder: string[] = [];
  private loadedDomains: Set<string> = new Set();
  private loadQueue: DomainLoadConfig[] = [];

  private constructor() {
    this.initializeLoadOrder();
  }

  static getInstance(): DomainLoadManager {
    if (!DomainLoadManager.instance) {
      DomainLoadManager.instance = new DomainLoadManager();
    }
    return DomainLoadManager.instance;
  }

  /**
   * Initialize the load order based on dependency graph
   */
  private initializeLoadOrder() {
    this.loadOrder = getLoadOrder();
  }

  /**
   * Register a domain for lazy loading
   */
  registerDomain(config: DomainLoadConfig): void {
    const { domain } = config;
    
    this.domains.set(domain, {
      status: 'unloaded',
      config,
      dependents: this.getDomainDependents(domain),
    });

    // Queue domain based on priority
    this.loadQueue.push(config);
    this.loadQueue.sort((a, b) => {
      const priorityOrder = { critical: 0, high: 1, normal: 2, low: 3 };
      return priorityOrder[a.priority] - priorityOrder[b.priority];
    });
  }

  /**
   * Get all domains that depend on a specific domain
   */
  private getDomainDependents(domain: string): string[] {
    const dependents: string[] = [];
    for (const [depName, deps] of Object.entries(DOMAIN_DEPENDENCIES)) {
      if (deps.includes(domain)) {
        dependents.push(depName);
      }
    }
    return dependents;
  }

  /**
   * Load a specific domain
   */
  async loadDomain(domain: string): Promise<DomainLoadResult> {
    const manager = this.domains.get(domain);
    
    if (!manager) {
      return {
        domain,
        success: false,
        error: 'Domain not registered',
        loadTime: 0,
        timestamp: Date.now(),
      };
    }

    if (manager.status === 'loaded') {
      return manager.result!;
    }

    if (manager.status === 'loading') {
      return manager.loadPromise!;
    }

    const startTime = Date.now();
    manager.status = 'loading';

    try {
      // Load dependencies first
      const dependencies = DOMAIN_DEPENDENCIES[domain] || [];
      for (const dep of dependencies) {
        if (!this.loadedDomains.has(dep)) {
          await this.loadDomain(dep);
        }
      }

      // Load the domain itself
      if (manager.config.loader) {
        await manager.config.loader();
      } else {
        // Default loader - in production this would dynamically import
        // For now, we just mark as loaded
        await new Promise(resolve => setTimeout(resolve, 100));
      }

      const loadTime = Date.now() - startTime;
      const result: DomainLoadResult = {
        domain,
        success: true,
        loadTime,
        timestamp: Date.now(),
      };

      manager.status = 'loaded';
      manager.result = result;
      this.loadedDomains.add(domain);

      // Preload dependents if configured
      if (manager.config.preloadDependents) {
        for (const dependent of manager.dependents) {
          const depManager = this.domains.get(dependent);
          if (depManager && depManager.status === 'unloaded') {
            this.loadDomain(dependent).catch(() => {
              // Silent fail for preloading
            });
          }
        }
      }

      return result;

    } catch (error) {
      const loadTime = Date.now() - startTime;
      const result: DomainLoadResult = {
        domain,
        success: false,
        error: error instanceof Error ? error.message : 'Unknown error',
        loadTime,
        timestamp: Date.now(),
      };

      manager.status = 'failed';
      manager.result = result;

      return result;
    }
  }

  /**
   * Load multiple domains in the optimal order
   */
  async loadDomains(domains: string[]): Promise<DomainLoadResult[]> {
    const results: DomainLoadResult[] = [];
    
    // Sort domains based on load order and priority
    const sortedDomains = domains.sort((a, b) => {
      const indexA = this.loadOrder.indexOf(a);
      const indexB = this.loadOrder.indexOf(b);
      return indexA - indexB;
    });

    for (const domain of sortedDomains) {
      const result = await this.loadDomain(domain);
      results.push(result);
    }

    return results;
  }

  /**
   * Load all registered domains
   */
  async loadAllDomains(): Promise<DomainLoadResult[]> {
    const domains = Array.from(this.domains.keys());
    return this.loadDomains(domains);
  }

  /**
   * Load domains by priority
   */
  async loadByPriority(priority: DomainLoadConfig['priority']): Promise<DomainLoadResult[]> {
    const domainsToLoad = Array.from(this.domains.entries())
      .filter(([_, manager]) => manager.config.priority === priority)
      .map(([domain]) => domain);

    return this.loadDomains(domainsToLoad);
  }

  /**
   * Get load status of all domains
   */
  getLoadStatus(): Record<string, DomainLoadStatus> {
    const status: Record<string, DomainLoadStatus> = {};
    
    for (const [domain, manager] of this.domains) {
      status[domain] = manager.status;
    }

    return status;
  }

  /**
   * Get load statistics
   */
  getLoadStatistics(): {
    totalDomains: number;
    loadedDomains: number;
    loadingDomains: number;
    failedDomains: number;
    unloadedDomains: number;
    averageLoadTime: number;
  } {
    let totalLoadTime = 0;
    let loadedCount = 0;
    
    for (const manager of this.domains.values()) {
      if (manager.result) {
        totalLoadTime += manager.result.loadTime;
        loadedCount++;
      }
    }

    return {
      totalDomains: this.domains.size,
      loadedDomains: this.loadedDomains.size,
      loadingDomains: Array.from(this.domains.values()).filter(m => m.status === 'loading').length,
      failedDomains: Array.from(this.domains.values()).filter(m => m.status === 'failed').length,
      unloadedDomains: Array.from(this.domains.values()).filter(m => m.status === 'unloaded').length,
      averageLoadTime: loadedCount > 0 ? totalLoadTime / loadedCount : 0,
    };
  }

  /**
   * Check if a domain is loaded
   */
  isDomainLoaded(domain: string): boolean {
    return this.loadedDomains.has(domain);
  }

  /**
   * Get loaded domains
   */
  getLoadedDomains(): string[] {
    return Array.from(this.loadedDomains);
  }

  /**
   * Unload a domain (useful for cleanup)
   */
  async unloadDomain(domain: string): Promise<void> {
    const manager = this.domains.get(domain);
    if (manager && manager.status === 'loaded') {
      // In production, this would clean up the module
      manager.status = 'unloaded';
      manager.result = undefined;
      this.loadedDomains.delete(domain);
    }
  }
}

// ============================================================================
// Public API
// ============================================================================

/**
 * Register a domain for lazy loading
 */
export function registerDomain(config: DomainLoadConfig): void {
  DomainLoadManager.getInstance().registerDomain(config);
}

/**
 * Load a specific domain
 */
export async function loadDomain(domain: string): Promise<DomainLoadResult> {
  return DomainLoadManager.getInstance().loadDomain(domain);
}

/**
 * Load multiple domains
 */
export async function loadDomains(domains: string[]): Promise<DomainLoadResult[]> {
  return DomainLoadManager.getInstance().loadDomains(domains);
}

/**
 * Load all registered domains
 */
export async function loadAllDomains(): Promise<DomainLoadResult[]> {
  return DomainLoadManager.getInstance().loadAllDomains();
}

/**
 * Load domains by priority
 */
export async function loadByPriority(priority: DomainLoadConfig['priority']): Promise<DomainLoadResult[]> {
  return DomainLoadManager.getInstance().loadByPriority(priority);
}

/**
 * Get load status of all domains
 */
export function getLoadStatus(): Record<string, DomainLoadStatus> {
  return DomainLoadManager.getInstance().getLoadStatus();
}

/**
 * Get load statistics
 */
export function getLoadStatistics() {
  return DomainLoadManager.getInstance().getLoadStatistics();
}

/**
 * Check if a domain is loaded
 */
export function isDomainLoaded(domain: string): boolean {
  return DomainLoadManager.getInstance().isDomainLoaded(domain);
}

/**
 * Get loaded domains
 */
export function getLoadedDomains(): string[] {
  return DomainLoadManager.getInstance().getLoadedDomains();
}

/**
 * Unload a domain
 */
export async function unloadDomain(domain: string): Promise<void> {
  return DomainLoadManager.getInstance().unloadDomain(domain);
}