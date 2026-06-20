/**
 * Domain Middleware System
 * 
 * Provides middleware for domain service communication, enabling
 * request/response interception, modification, and cross-cutting concerns.
 */

// ============================================================================
// Domain Middleware Types
// ============================================================================

export interface DomainMiddlewareContext {
  targetDomain: string;
  service: string;
  method: string;
  params: any;
  timestamp: number;
  requestId: string;
}

export interface DomainMiddlewareHandler {
  (context: DomainMiddlewareContext, next: () => Promise<any>): Promise<any>;
}

export interface DomainMiddleware {
  name: string;
  priority: number;
  handler: DomainMiddlewareHandler;
}

export interface MiddlewareRegistry {
  global: DomainMiddleware[];
  [domain: string]: DomainMiddleware[];
}

// ============================================================================
// Domain Middleware Manager
// ============================================================================

class DomainMiddlewareManager {
  private static instance: DomainMiddlewareManager;
  private registry: MiddlewareRegistry = {
    global: [],
  };
  private middlewareCounter = 0;

  private constructor() {}

  static getInstance(): DomainMiddlewareManager {
    if (!DomainMiddlewareManager.instance) {
      DomainMiddlewareManager.instance = new DomainMiddlewareManager();
    }
    return DomainMiddlewareManager.instance;
  }

  /**
   * Register global middleware (applies to all domains)
   */
  registerGlobalMiddleware(middleware: Omit<DomainMiddleware, 'name'>): string {
    const name = `global-middleware-${this.middlewareCounter++}`;
    const fullMiddleware: DomainMiddleware = {
      name,
      priority: middleware.priority,
      handler: middleware.handler,
    };

    this.registry.global.push(fullMiddleware);
    this.registry.global.sort((a, b) => a.priority - b.priority);

    return name;
  }

  /**
   * Register domain-specific middleware
   */
  registerDomainMiddleware(
    domain: string,
    middleware: Omit<DomainMiddleware, 'name'>
  ): string {
    const name = `${domain}-middleware-${this.middlewareCounter++}`;
    const fullMiddleware: DomainMiddleware = {
      name,
      priority: middleware.priority,
      handler: middleware.handler,
    };

    if (!this.registry[domain]) {
      this.registry[domain] = [];
    }

    this.registry[domain].push(fullMiddleware);
    this.registry[domain].sort((a, b) => a.priority - b.priority);

    return name;
  }

  /**
   * Unregister middleware
   */
  unregisterMiddleware(name: string): boolean {
    // Check global middleware
    const globalIndex = this.registry.global.findIndex(m => m.name === name);
    if (globalIndex >= 0) {
      this.registry.global.splice(globalIndex, 1);
      return true;
    }

    // Check domain middleware
    for (const domain in this.registry) {
      if (domain === 'global') continue;
      const domainIndex = this.registry[domain].findIndex(m => m.name === name);
      if (domainIndex >= 0) {
        this.registry[domain].splice(domainIndex, 1);
        return true;
      }
    }

    return false;
  }

  /**
   * Get middleware for a specific domain
   */
  getMiddlewareForDomain(domain: string): DomainMiddleware[] {
    const global = this.registry.global;
    const domainSpecific = this.registry[domain] || [];

    // Combine and sort by priority
    const combined = [...global, ...domainSpecific];
    return combined.sort((a, b) => a.priority - b.priority);
  }

  /**
   * Execute middleware chain
   */
  async executeMiddlewareChain(
    _domain: string,
    middleware: DomainMiddleware[],
    context: DomainMiddlewareContext,
    handler: () => Promise<any>
  ): Promise<any> {
    let currentIndex = 0;

    const next = async (): Promise<any> => {
      if (currentIndex >= middleware.length) {
        return handler();
      }
      const currentMiddleware = middleware[currentIndex];
      currentIndex++;
      return currentMiddleware.handler(context, next);
    };

    return next();
  }

  /**
   * Clear all middleware
   */
  clearMiddleware(): void {
    this.registry = { global: [] };
    this.middlewareCounter = 0;
  }

  /**
   * Get middleware statistics
   */
  getMiddlewareStats(): {
    totalMiddleware: number;
    globalCount: number;
    domainCount: number;
    domains: Record<string, number>;
  } {
    let domainCount = 0;
    const domains: Record<string, number> = {};

    for (const [domain, middleware] of Object.entries(this.registry)) {
      if (domain !== 'global') {
        domainCount++;
        domains[domain] = middleware.length;
      }
    }

    return {
      totalMiddleware: this.registry.global.length + Object.values(this.registry)
        .filter((_, idx) => idx > 0).reduce((sum, arr) => sum + arr.length, 0),
      globalCount: this.registry.global.length,
      domainCount,
      domains,
    };
  }
}

// ============================================================================
// Common Middleware
// ============================================================================

/**
 * Logging middleware for debugging
 */
export const loggingMiddleware: Omit<DomainMiddleware, 'name'> = {
  priority: 100,
  handler: async (context, next) => {
    console.log(`[Domain Middleware] ${context.targetDomain}:${context.service}:${context.method}`, {
      params: context.params,
      timestamp: new Date(context.timestamp).toISOString(),
    });

    const startTime = Date.now();
    try {
      const result = await next();
      const duration = Date.now() - startTime;
      console.log(`[Domain Middleware] ${context.targetDomain}:${context.service}:${context.method} completed`, {
        duration,
      });
      return result;
    } catch (error) {
      const duration = Date.now() - startTime;
      console.error(`[Domain Middleware] ${context.targetDomain}:${context.service}:${context.method} failed`, {
        duration,
        error,
      });
      throw error;
    }
  },
};

/**
 * Authentication middleware
 */
export const authMiddleware: Omit<DomainMiddleware, 'name'> = {
  priority: 200,
  handler: async (_context, next) => {
    // Check if the request requires authentication
    if (_context.service === 'governance' && _context.method === 'approve') {
      // Add authentication check logic here
      console.log(`[Auth Middleware] Checking permissions for ${_context.method}`);
      // For now, just pass through
    }
    return next();
  },
};

/**
 * Caching middleware
 */
export const cachingMiddleware: Omit<DomainMiddleware, 'name'> = {
  priority: 50,
  handler: async (_context, next) => {
    const cacheKey = `${_context.targetDomain}:${_context.service}:${_context.method}:${JSON.stringify(_context.params)}`;
    
    // Check cache (in a real implementation, this would use a proper cache)
    // For now, just pass through
    const result = await next();
    
    // Cache the result
    console.log(`[Cache Middleware] Cached result for ${cacheKey}`);
    
    return result;
  },
};

/**
 * Rate limiting middleware
 */
export const rateLimitMiddleware: Omit<DomainMiddleware, 'name'> = {
  priority: 150,
  handler: async (_context, next) => {
    // In a real implementation, this would track request counts per domain
    // For now, just pass through
    return next();
  },
};

/**
 * Validation middleware
 */
export const validationMiddleware: Omit<DomainMiddleware, 'name'> = {
  priority: 180,
  handler: async (context, next) => {
    // Validate request parameters
    if (!context.params) {
      throw new Error('Parameters are required');
    }

    // Add custom validation logic based on domain/service/method
    return next();
  },
};

// ============================================================================
// Public API
// ============================================================================

/**
 * Register global middleware
 */
export function registerGlobalMiddleware(middleware: Omit<DomainMiddleware, 'name'>): string {
  return DomainMiddlewareManager.getInstance().registerGlobalMiddleware(middleware);
}

/**
 * Register domain-specific middleware
 */
export function registerDomainMiddleware(
  domain: string,
  middleware: Omit<DomainMiddleware, 'name'>
): string {
  return DomainMiddlewareManager.getInstance().registerDomainMiddleware(domain, middleware);
}

/**
 * Unregister middleware
 */
export function unregisterMiddleware(name: string): boolean {
  return DomainMiddlewareManager.getInstance().unregisterMiddleware(name);
}

/**
 * Get middleware for a domain
 */
export function getMiddlewareForDomain(domain: string): DomainMiddleware[] {
  return DomainMiddlewareManager.getInstance().getMiddlewareForDomain(domain);
}

/**
 * Execute middleware chain for a domain
 */
export async function executeMiddlewareChain(
  domain: string,
  context: DomainMiddlewareContext,
  handler: () => Promise<any>
): Promise<any> {
  const middleware = getMiddlewareForDomain(domain);
  return DomainMiddlewareManager.getInstance().executeMiddlewareChain(domain, middleware, context, handler);
}

/**
 * Clear all middleware
 */
export function clearAllMiddleware(): void {
  DomainMiddlewareManager.getInstance().clearMiddleware();
}

/**
 * Get middleware statistics
 */
export function getMiddlewareStats() {
  return DomainMiddlewareManager.getInstance().getMiddlewareStats();
}