/**
 * Domain Gateway
 * 
 * Provides a gateway pattern for inter-domain service communication,
 * enabling type-safe and controlled access to domain services.
 */

import { executeMiddlewareChain, type DomainMiddlewareContext } from './domain-middleware';

export interface DomainServiceRequest {
  targetDomain: string;
  service: string;
  method: string;
  params?: any;
  timeout?: number;
  requestId?: string;
}

export interface DomainServiceResponse {
  success: boolean;
  data?: any;
  error?: string;
  domain: string;
  service: string;
  method: string;
  timestamp: number;
  executionTime?: number;
}

export interface DomainServiceRegistry {
  [domain: string]: {
    [service: string]: {
      [method: string]: (params: any) => Promise<any>;
    };
  };
}

/**
 * Domain Gateway Class
 */
export class DomainGateway {
  private static serviceRegistry: DomainServiceRegistry = {};
  private static defaultTimeout = 5000; // 5 seconds

  /**
   * Register a domain service
   */
  static registerService(
    domain: string,
    service: string,
    method: string,
    handler: (params: any) => Promise<any>
  ): void {
    if (!this.serviceRegistry[domain]) {
      this.serviceRegistry[domain] = {};
    }
    
    if (!this.serviceRegistry[domain][service]) {
      this.serviceRegistry[domain][service] = {};
    }
    
    this.serviceRegistry[domain][service][method] = handler;
  }

  /**
   * Register multiple methods for a service
   */
  static registerServiceMethods(
    domain: string,
    service: string,
    methods: Record<string, (params: any) => Promise<any>>
  ): void {
    for (const [method, handler] of Object.entries(methods)) {
      this.registerService(domain, service, method, handler);
    }
  }

  /**
   * Request service from another domain
   */
  static async request(request: DomainServiceRequest): Promise<DomainServiceResponse> {
    const { targetDomain, service, method, params, timeout = this.defaultTimeout, requestId = `req-${Date.now()}-${Math.random().toString(36).substr(2, 9)}` } = request;
    const startTime = Date.now();
    
    try {
      // Check if service exists
      if (!this.serviceRegistry[targetDomain]) {
        throw new Error(`Domain '${targetDomain}' has no registered services`);
      }
      
      if (!this.serviceRegistry[targetDomain][service]) {
        throw new Error(`Service '${service}' not found in domain '${targetDomain}'`);
      }
      
      if (!this.serviceRegistry[targetDomain][service][method]) {
        throw new Error(`Method '${method}' not found in service '${service}' of domain '${targetDomain}'`);
      }
      
      // Create middleware context
      const context: DomainMiddlewareContext = {
        targetDomain,
        service,
        method,
        params,
        timestamp: Date.now(),
        requestId,
      };
      
      // Execute middleware chain
      const result = await executeMiddlewareChain(targetDomain, context, async () => {
        // Execute service method with timeout
        const handler = this.serviceRegistry[targetDomain][service][method];
        const response = await Promise.race([
          handler(params),
          this.createTimeoutPromise(timeout),
        ]);
        
        return response;
      });
      
      const executionTime = Date.now() - startTime;
      
      return {
        success: true,
        data: result,
        domain: targetDomain,
        service,
        method,
        timestamp: Date.now(),
        executionTime,
      };
    } catch (error) {
      const executionTime = Date.now() - startTime;
      
      return {
        success: false,
        error: error instanceof Error ? error.message : 'Unknown error',
        domain: targetDomain,
        service,
        method,
        timestamp: Date.now(),
        executionTime,
      };
    }
  }

  /**
   * Broadcast a request to multiple domains
   */
  static async broadcast(
    domains: string[],
    service: string,
    method: string,
    params?: any
  ): Promise<DomainServiceResponse[]> {
    const requests = domains.map(domain =>
      this.request({ targetDomain: domain, service, method, params })
    );
    
    return Promise.all(requests);
  }

  /**
   * Get available services for a domain
   */
  static getDomainServices(domain: string): string[] {
    return Object.keys(this.serviceRegistry[domain] || {});
  }

  /**
   * Get available methods for a service
   */
  static getServiceMethods(domain: string, service: string): string[] {
    return Object.keys(this.serviceRegistry[domain]?.[service] || {});
  }

  /**
   * Check if a service method exists
   */
  static hasServiceMethod(domain: string, service: string, method: string): boolean {
    return !!this.serviceRegistry[domain]?.[service]?.[method];
  }

  /**
   * Unregister a service method
   */
  static unregisterService(domain: string, service: string, method: string): boolean {
    if (this.serviceRegistry[domain]?.[service]?.[method]) {
      delete this.serviceRegistry[domain][service][method];
      
      // Clean up empty objects
      if (Object.keys(this.serviceRegistry[domain][service]).length === 0) {
        delete this.serviceRegistry[domain][service];
      }
      
      if (Object.keys(this.serviceRegistry[domain]).length === 0) {
        delete this.serviceRegistry[domain];
      }
      
      return true;
    }
    
    return false;
  }

  /**
   * Unregister an entire service
   */
  static unregisterAllServiceMethods(domain: string, service: string): boolean {
    if (this.serviceRegistry[domain]?.[service]) {
      delete this.serviceRegistry[domain][service];
      
      if (Object.keys(this.serviceRegistry[domain]).length === 0) {
        delete this.serviceRegistry[domain];
      }
      
      return true;
    }
    
    return false;
  }

  /**
   * Unregister all services for a domain
   */
  static unregisterDomain(domain: string): boolean {
    if (this.serviceRegistry[domain]) {
      delete this.serviceRegistry[domain];
      return true;
    }
    
    return false;
  }

  /**
   * Get registry statistics
   */
  static getRegistryStats(): {
    totalDomains: number;
    totalServices: number;
    totalMethods: number;
    domains: Record<string, { services: number; methods: number }>;
  } {
    const stats = {
      totalDomains: 0,
      totalServices: 0,
      totalMethods: 0,
      domains: {} as Record<string, { services: number; methods: number }>,
    };
    
    for (const [domain, services] of Object.entries(this.serviceRegistry)) {
      const serviceCount = Object.keys(services).length;
      const methodCount = Object.values(services).reduce(
        (count, serviceMethods) => count + Object.keys(serviceMethods).length,
        0
      );
      
      stats.totalDomains++;
      stats.totalServices += serviceCount;
      stats.totalMethods += methodCount;
      
      stats.domains[domain] = {
        services: serviceCount,
        methods: methodCount,
      };
    }
    
    return stats;
  }

  /**
   * Clear entire registry (useful for testing)
   */
  static clearRegistry(): void {
    this.serviceRegistry = {};
  }

  /**
   * Create a timeout promise
   */
  private static createTimeoutPromise(timeout: number): Promise<never> {
    return new Promise((_, reject) => {
      setTimeout(() => reject(new Error('Request timeout')), timeout);
    });
  }
}