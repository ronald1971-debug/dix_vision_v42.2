/**
 * Cross-Domain Communication Hook
 * 
 * Provides a unified interface for domains to communicate with each other
 * using the event bus and domain gateway infrastructure.
 */

import { useCallback, useEffect, useRef } from 'react';
import { DomainEventBus } from './event-bus';
import { DomainGateway, type DomainServiceRequest, type DomainServiceResponse } from './domain-gateway';
import { DOMAIN_DEPENDENCIES, getAllDependencies, getAllDependents } from './dependency-graph';

// ============================================================================
// Domain Communication Hook Types
// ============================================================================

interface UseDomainCommunicationOptions {
  /**
   * The domain using this hook
   */
  domain: string;
  
  /**
   * Whether to automatically subscribe to events from dependent domains
   */
  autoSubscribe?: boolean;
  
  /**
   * Whether to log communication for debugging
   */
  debug?: boolean;
}

interface DomainCommunicationResult {
  // Event Bus Methods
  publishEvent: (event: string, data: any) => void;
  subscribeToEvent: (event: string, handler: (data: any) => void) => () => void;
  subscribeToDomain: (sourceDomain: string, event: string, handler: (data: any) => void) => () => void;
  
  // Service Gateway Methods
  requestService: (targetDomain: string, service: string, method: string, params?: any) => Promise<DomainServiceResponse>;
  broadcastService: (targetDomains: string[], service: string, method: string, params?: any) => Promise<DomainServiceResponse[]>;
  
  // Dependency Methods
  getDependencies: () => string[];
  getDependents: () => string[];
  dependsOn: (target: string) => boolean;
  
  // Registration Methods
  registerService: (service: string, method: string, handler: (params: any) => Promise<any>) => void;
  unregisterService: (service: string, method: string) => void;
}

// ============================================================================
// Cross-Domain Communication Hook Implementation
// ============================================================================

export function useDomainCommunication(options: UseDomainCommunicationOptions): DomainCommunicationResult {
  const { domain, autoSubscribe = true, debug = false } = options;
  const subscriptionsRef = useRef<Map<string, () => void>>(new Map());

  // Helper to log debug information
  const log = useCallback((message: string, data?: any) => {
    if (debug) {
      console.log(`[Domain:${domain}] ${message}`, data || '');
    }
  }, [domain, debug]);

  // Publish event to the domain
  const publishEvent = useCallback((event: string, data: any) => {
    log('Publishing event', { event, data });
    DomainEventBus.publish(domain, event, data);
  }, [domain, log]);

  // Subscribe to events from the same domain
  const subscribeToEvent = useCallback((event: string, handler: (data: any) => void) => {
    log('Subscribing to event', { event });
    
    const subscriptionId = DomainEventBus.subscribe(domain, event, handler);
    
    const subscriptionKey = `${domain}:${event}`;
    const cleanup = () => {
      DomainEventBus.unsubscribe(subscriptionId);
      subscriptionsRef.current.delete(subscriptionKey);
    };
    subscriptionsRef.current.set(subscriptionKey, cleanup);
    
    return cleanup;
  }, [domain, log]);

  // Subscribe to events from another domain
  const subscribeToDomain = useCallback((sourceDomain: string, event: string, handler: (data: any) => void) => {
    log('Subscribing to domain event', { sourceDomain, event });
    
    const subscriptionId = DomainEventBus.subscribe(sourceDomain, event, handler);
    
    const subscriptionKey = `${sourceDomain}:${event}`;
    const cleanup = () => {
      DomainEventBus.unsubscribe(subscriptionId);
      subscriptionsRef.current.delete(subscriptionKey);
    };
    subscriptionsRef.current.set(subscriptionKey, cleanup);
    
    return cleanup;
  }, [log]);

  // Request service from another domain
  const requestService = useCallback(async (
    targetDomain: string,
    service: string,
    method: string,
    params?: any
  ): Promise<DomainServiceResponse> => {
    log('Requesting service', { targetDomain, service, method, params });
    
    const request: DomainServiceRequest = {
      targetDomain,
      service,
      method,
      params,
    };
    
    return DomainGateway.request(request);
  }, [log]);

  // Broadcast service request to multiple domains
  const broadcastService = useCallback(async (
    targetDomains: string[],
    service: string,
    method: string,
    params?: any
  ): Promise<DomainServiceResponse[]> => {
    log('Broadcasting service', { targetDomains, service, method, params });
    
    return DomainGateway.broadcast(targetDomains, service, method, params);
  }, [log]);

  // Get all dependencies for this domain
  const getDependencies = useCallback(() => {
    return getAllDependencies(domain);
  }, [domain]);

  // Get all domains that depend on this domain
  const getDependents = useCallback(() => {
    return getAllDependents(domain);
  }, [domain]);

  // Check if this domain depends on a specific target
  const dependsOn = useCallback((target: string): boolean => {
    return DOMAIN_DEPENDENCIES[domain]?.includes(target) || false;
  }, [domain]);

  // Register a service method for this domain
  const registerService = useCallback((service: string, method: string, handler: (params: any) => Promise<any>) => {
    log('Registering service method', { service, method });
    DomainGateway.registerService(domain, service, method, handler);
  }, [domain, log]);

  // Unregister a service method
  const unregisterService = useCallback((service: string, method: string) => {
    log('Unregistering service method', { service, method });
    DomainGateway.unregisterService(domain, service, method);
  }, [domain, log]);

  // Auto-subscribe to events from dependent domains
  useEffect(() => {
    if (!autoSubscribe) return;

    const dependencies = getDependencies();
    log('Auto-subscribing to dependencies', { dependencies });

    // Subscribe to key events from dependent domains
    const commonEvents = ['state:updated', 'status:changed', 'error:occurred'];
    
    dependencies.forEach(depDomain => {
      commonEvents.forEach(event => {
        const subscriptionId = DomainEventBus.subscribe(depDomain, event, (data) => {
          log(`Received event from ${depDomain}`, { event, data });
        });
        
        const subscriptionKey = `${depDomain}:${event}`;
        const cleanup = () => {
          DomainEventBus.unsubscribe(subscriptionId);
          subscriptionsRef.current.delete(subscriptionKey);
        };
        subscriptionsRef.current.set(subscriptionKey, cleanup);
      });
    });

    // Cleanup on unmount
    return () => {
      subscriptionsRef.current.forEach(unsubscribe => {
        unsubscribe();
      });
      subscriptionsRef.current.clear();
    };
  }, [autoSubscribe, getDependencies, log]);

  return {
    // Event Bus Methods
    publishEvent,
    subscribeToEvent,
    subscribeToDomain,
    
    // Service Gateway Methods
    requestService,
    broadcastService,
    
    // Dependency Methods
    getDependencies,
    getDependents,
    dependsOn,
    
    // Registration Methods
    registerService,
    unregisterService,
  };
}

// ============================================================================
// Specialized Hooks for Common Communication Patterns
// ============================================================================

/**
 * Hook for requesting data from another domain
 */
export function useDomainServiceRequest<T = any>(
  targetDomain: string,
  service: string,
  method: string
) {
  const communication = useDomainCommunication({
    domain: 'requester', // Generic requester domain
    debug: false,
  });

  const request = useCallback(async (params?: any): Promise<T | null> => {
    const response = await communication.requestService(targetDomain, service, method, params);
    return response.success ? response.data as T : null;
  }, [communication, targetDomain, service, method]);

  return { request };
}

/**
 * Hook for subscribing to domain events
 */
export function useDomainEventSubscription<T = any>(
  sourceDomain: string,
  event: string,
  handler: (data: T) => void
) {
  const communication = useDomainCommunication({
    domain: 'subscriber', // Generic subscriber domain
    debug: false,
  });

  useEffect(() => {
    const unsubscribe = communication.subscribeToDomain(sourceDomain, event, handler);
    return unsubscribe;
  }, [communication, sourceDomain, event, handler]);
}