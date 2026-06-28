/**
 * Domain Streaming Communication
 * 
 * Provides streaming communication capabilities for real-time data flow
 * between domains, supporting live updates and continuous data streams.
 */

// ============================================================================
// Streaming Communication Types
// ============================================================================

export interface StreamSubscription {
  id: string;
  domain: string;
  channel: string;
  callback: (data: any) => void;
  filter?: (data: any) => boolean;
  createdAt: number;
  lastActivity: number;
}

export interface StreamMessage {
  streamId: string;
  domain: string;
  channel: string;
  data: any;
  timestamp: number;
  sequence: number;
}

export interface StreamConfig {
  domain: string;
  channel: string;
  bufferSize?: number;
  batchInterval?: number;
  throttleMs?: number;
}

// ============================================================================
// Streaming Manager
// ============================================================================

class DomainStreamingManager {
  private static instance: DomainStreamingManager;
  private subscriptions: Map<string, StreamSubscription[]> = new Map();
  private streamCounters: Map<string, number> = new Map();
  private sequenceNumbers: Map<string, number> = new Map();
  private subscriptionCounter = 0;

  private constructor() {}

  static getInstance(): DomainStreamingManager {
    if (!DomainStreamingManager.instance) {
      DomainStreamingManager.instance = new DomainStreamingManager();
    }
    return DomainStreamingManager.instance;
  }

  /**
   * Create a stream ID
   */
  private createStreamId(domain: string, channel: string): string {
    return `${domain}:${channel}:${Date.now()}-${Math.random().toString(36).substr(2, 9)}`;
  }

  /**
   * Get sequence number for a stream
   */
  private getSequenceNumber(streamId: string): number {
    const current = this.sequenceNumbers.get(streamId) || 0;
    this.sequenceNumbers.set(streamId, current + 1);
    return current;
  }

  /**
   * Subscribe to a data stream
   */
  subscribe(
    domain: string,
    channel: string,
    callback: (data: any) => void,
    options?: { filter?: (data: any) => boolean }
  ): () => void {
    const subscriptionId = `sub-${this.subscriptionCounter++}`;

    const subscription: StreamSubscription = {
      id: subscriptionId,
      domain,
      channel,
      callback,
      filter: options?.filter,
      createdAt: Date.now(),
      lastActivity: Date.now(),
    };

    // Add subscription to registry
    const key = `${domain}:${channel}`;
    if (!this.subscriptions.has(key)) {
      this.subscriptions.set(key, []);
      this.streamCounters.set(key, 0);
    }

    this.subscriptions.get(key)!.push(subscription);
    this.streamCounters.set(key, (this.streamCounters.get(key) || 0) + 1);

    // Return unsubscribe function
    return () => {
      const subs = this.subscriptions.get(key);
      if (subs) {
        const index = subs.findIndex(s => s.id === subscriptionId);
        if (index >= 0) {
          subs.splice(index, 1);
          this.streamCounters.set(key, subs.length);
          
          // Clean up if no more subscriptions
          if (subs.length === 0) {
            this.subscriptions.delete(key);
            this.streamCounters.delete(key);
          }
        }
      }
    };
  }

  /**
   * Publish data to a stream
   */
  publish(domain: string, channel: string, data: any): void {
    const key = `${domain}:${channel}`;
    const _streamId = this.createStreamId(domain, channel);

    const message: StreamMessage = {
      streamId: _streamId,
      domain,
      channel,
      data,
      timestamp: Date.now(),
      sequence: this.getSequenceNumber(_streamId),
    };

    const subscriptions = this.subscriptions.get(key);
    if (!subscriptions) return;

    subscriptions.forEach(subscription => {
      // Update last activity
      subscription.lastActivity = Date.now();

      // Apply filter if provided
      if (subscription.filter && !subscription.filter(data)) {
        return;
      }

      // Deliver message
      try {
        subscription.callback(message);
      } catch (error) {
        console.error(`[Streaming Manager] Error in subscription callback:`, error);
      }
    });
  }

  /**
   * Create a buffered stream for high-frequency data
   */
  createBufferedStream(config: StreamConfig): {
    publish: (data: any) => void;
    getSubscribers: () => number;
  } {
    const { domain, channel, bufferSize = 100, batchInterval = 100 } = config;
    const key = `${domain}:${channel}`;
    let buffer: any[] = [];
    let batchTimer: NodeJS.Timeout | null = null;

    const flushBuffer = () => {
      if (buffer.length > 0) {
        const batchData = [...buffer];
        buffer = [];
        this.publish(domain, channel, batchData);
      }
      if (batchTimer) {
        clearTimeout(batchTimer);
        batchTimer = null;
      }
    };

    const publish = (data: any) => {
      buffer.push(data);
      
      if (buffer.length >= bufferSize) {
        flushBuffer();
      } else if (!batchTimer) {
        batchTimer = setTimeout(flushBuffer, batchInterval);
      }
    };

    const getSubscribers = () => {
      return this.streamCounters.get(key) || 0;
    };

    return { publish, getSubscribers };
  }

  /**
   * Create a throttled stream
   */
  createThrottledStream(config: StreamConfig): {
    publish: (data: any) => void;
    getSubscribers: () => number;
  } {
    const { domain, channel, throttleMs = 100 } = config;
    let lastPublish = 0;

    const publish = (data: any) => {
      const now = Date.now();
      const timeSinceLast = now - lastPublish;

      if (timeSinceLast >= throttleMs) {
        this.publish(domain, channel, data);
        lastPublish = now;
      }
    };

    const getSubscribers = () => {
      const key = `${domain}:${channel}`;
      return this.streamCounters.get(key) || 0;
    };

    return { publish, getSubscribers };
  }

  /**
   * Get streaming statistics
   */
  getStreamStats(): {
    [key: string]: number;
  } {
    const stats: Record<string, number> = {};
    this.streamCounters.forEach((count, key) => {
      stats[key] = count;
    });
    return stats;
  }

  /**
   * Get all subscriptions
   */
  getAllSubscriptions(): StreamSubscription[] {
    const allSubscriptions: StreamSubscription[] = [];
    this.subscriptions.forEach(subs => {
      allSubscriptions.push(...subs);
    });
    return allSubscriptions;
  }

  /**
   * Clear all subscriptions for a domain
   */
  clearDomainSubscriptions(domain: string): void {
    const keysToDelete: string[] = [];
    
    this.subscriptions.forEach((_, key) => {
      if (key.startsWith(`${domain}:`)) {
        keysToDelete.push(key);
      }
    });

    keysToDelete.forEach(key => {
      this.subscriptions.delete(key);
      this.streamCounters.delete(key);
    });
  }

  /**
   * Clear all subscriptions
   */
  clearAllSubscriptions(): void {
    this.subscriptions.clear();
    this.streamCounters.clear();
  }
}

// ============================================================================
// Public API
// ============================================================================

/**
 * Subscribe to a domain stream
 */
export function subscribeToStream(
  domain: string,
  channel: string,
  callback: (data: any) => void,
  options?: { filter?: (data: any) => boolean }
): () => void {
  return DomainStreamingManager.getInstance().subscribe(domain, channel, callback, options);
}

/**
 * Publish data to a domain stream
 */
export function publishToStream(domain: string, channel: string, data: any): void {
  DomainStreamingManager.getInstance().publish(domain, channel, data);
}

/**
 * Create a buffered stream for high-frequency data
 */
export function createBufferedStream(config: StreamConfig) {
  return DomainStreamingManager.getInstance().createBufferedStream(config);
}

/**
 * Create a throttled stream
 */
export function createThrottledStream(config: StreamConfig) {
  return DomainStreamingManager.getInstance().createThrottledStream(config);
}

/**
 * Get streaming statistics
 */
export function getStreamStats() {
  return DomainStreamingManager.getInstance().getStreamStats();
}

/**
 * Get all subscriptions
 */
export function getAllSubscriptions() {
  return DomainStreamingManager.getInstance().getAllSubscriptions();
}

/**
 * Clear domain subscriptions
 */
export function clearDomainSubscriptions(domain: string) {
  DomainStreamingManager.getInstance().clearDomainSubscriptions(domain);
}

/**
 * Clear all streaming subscriptions
 */
export function clearAllStreamSubscriptions() {
  DomainStreamingManager.getInstance().clearAllSubscriptions();
}