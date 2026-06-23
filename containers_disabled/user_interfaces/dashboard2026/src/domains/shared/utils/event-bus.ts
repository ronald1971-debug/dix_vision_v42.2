/**
 * Domain Event Bus
 * 
 * Provides event-driven communication between domains,
 * enabling loose coupling and flexible inter-domain communication.
 */

export type DomainEventHandler = (data: any) => void;
export type DomainEventFilter = (data: any) => boolean;

export interface DomainEvent {
  domain: string;
  event: string;
  data: any;
  timestamp: number;
  id: string;
}

export interface DomainEventSubscription {
  domain: string;
  event: string;
  handler: DomainEventHandler;
  filter?: DomainEventFilter;
  id: string;
}

/**
 * Domain Event Bus Class
 */
export class DomainEventBus {
  private static subscriptions: Map<string, DomainEventSubscription[]> = new Map();
  private static eventHistory: DomainEvent[] = [];
  private static maxHistorySize = 100;
  private static subscriptionCounter = 0;

  /**
   * Publish an event to a specific domain
   */
  static publish(domain: string, event: string, data: any): string {
    const eventId = `${domain}-${event}-${Date.now()}-${Math.random().toString(36).substr(2, 9)}`;
    
    const domainEvent: DomainEvent = {
      domain,
      event,
      data,
      timestamp: Date.now(),
      id: eventId,
    };
    
    // Store in history
    this.eventHistory.push(domainEvent);
    if (this.eventHistory.length > this.maxHistorySize) {
      this.eventHistory.shift();
    }
    
    // Get subscriptions for this domain and event
    const subscriptions = this.subscriptions.get(`${domain}:${event}`) || [];
    
    // Execute handlers
    for (const subscription of subscriptions) {
      try {
        // Apply filter if provided
        if (subscription.filter && !subscription.filter(data)) {
          continue;
        }
        
        subscription.handler(domainEvent);
      } catch (error) {
        console.error(`Error in event handler for ${domain}:${event}:`, error);
      }
    }
    
    return eventId;
  }

  /**
   * Subscribe to events from a specific domain
   */
  static subscribe(
    domain: string,
    event: string,
    handler: DomainEventHandler,
    filter?: DomainEventFilter
  ): string {
    const subscriptionId = `sub-${this.subscriptionCounter++}`;
    
    const subscription: DomainEventSubscription = {
      domain,
      event,
      handler,
      filter,
      id: subscriptionId,
    };
    
    const key = `${domain}:${event}`;
    if (!this.subscriptions.has(key)) {
      this.subscriptions.set(key, []);
    }
    
    this.subscriptions.get(key)!.push(subscription);
    
    return subscriptionId;
  }

  /**
   * Unsubscribe from a specific event
   */
  static unsubscribe(subscriptionId: string): boolean {
    for (const subscriptions of this.subscriptions.values()) {
      const index = subscriptions.findIndex(sub => sub.id === subscriptionId);
      if (index !== -1) {
        subscriptions.splice(index, 1);
        return true;
      }
    }
    
    return false;
  }

  /**
   * Subscribe to all events from a domain
   */
  static subscribeToDomain(domain: string, handler: DomainEventHandler): string[] {
    const subscriptionIds: string[] = [];
    
    // Subscribe to wildcard events for this domain
    const wildcardSubscription = this.subscribe(domain, '*', handler);
    subscriptionIds.push(wildcardSubscription);
    
    return subscriptionIds;
  }

  /**
   * Broadcast an event to all domains
   */
  static broadcast(event: string, data: any): string[] {
    const eventIds: string[] = [];
    const domains = Object.keys(DEPENDENCIES || {});
    
    for (const domain of domains) {
      if (domain !== 'shared') { // Skip shared domain
        const eventId = this.publish(domain, event, data);
        eventIds.push(eventId);
      }
    }
    
    return eventIds;
  }

  /**
   * Get event history
   */
  static getEventHistory(filter?: {
    domain?: string;
    event?: string;
    since?: number;
  }): DomainEvent[] {
    let history = [...this.eventHistory];
    
    if (filter?.domain) {
      history = history.filter(e => e.domain === filter.domain);
    }
    
    if (filter?.event) {
      history = history.filter(e => e.event === filter.event);
    }
    
    if (filter?.since !== undefined) {
      history = history.filter(e => e.timestamp >= (filter.since ?? 0));
    }
    
    return history;
  }

  /**
   * Clear event history
   */
  static clearHistory(): void {
    this.eventHistory = [];
  }

  /**
   * Get subscription statistics
   */
  static getSubscriptionStats(): {
    totalSubscriptions: number;
    subscriptionsByDomain: Record<string, number>;
    subscriptionsByEvent: Record<string, number>;
  } {
    const stats = {
      totalSubscriptions: 0,
      subscriptionsByDomain: {} as Record<string, number>,
      subscriptionsByEvent: {} as Record<string, number>,
    };
    
    for (const [key, subscriptions] of this.subscriptions.entries()) {
      const [domain, event] = key.split(':');
      
      stats.totalSubscriptions += subscriptions.length;
      stats.subscriptionsByDomain[domain] = (stats.subscriptionsByDomain[domain] || 0) + subscriptions.length;
      stats.subscriptionsByEvent[event] = (stats.subscriptionsByEvent[event] || 0) + subscriptions.length;
    }
    
    return stats;
  }

  /**
   * Clear all subscriptions (useful for testing)
   */
  static clearAllSubscriptions(): void {
    this.subscriptions.clear();
    this.subscriptionCounter = 0;
  }
}

// Import domain dependencies for wildcard support
import { DOMAIN_DEPENDENCIES as DEPENDENCIES } from './dependency-graph';