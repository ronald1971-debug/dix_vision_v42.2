/**
 * Agent WebSocket Manager
 * 
 * Manages WebSocket connections for real-time agent activity feeds
 */

import { useState, useEffect } from 'react';
import type {
  ConnectionState,
  MessageHandler,
  WebSocketMessage,
} from '@/types/agent';

/**
 * WebSocket Manager for Agent Operations Center
 * 
 * Handles connection lifecycle, message routing, and reconnection logic
 */
class AgentWebSocketManager {
  private ws: WebSocket | null = null;
  private reconnectTimer: NodeJS.Timeout | null = null;
  private connectionTimer: NodeJS.Timeout | null = null;
  private heartbeatTimer: NodeJS.Timeout | null = null;
  private messageHandlers: Map<string, MessageHandler[]> = new Map();
  private connectionState: ConnectionState = 'disconnected';
  private url: string;
  private reconnectDelay: number = 5000;
  private maxReconnectAttempts: number = 10;
  private reconnectAttempts: number = 0;
  private connectionTimeout: number = 10000; // 10 seconds connection timeout
  private heartbeatInterval: number = 30000; // 30 seconds heartbeat
  private lastHeartbeat: number = Date.now();

  constructor(url: string = 'ws://localhost:8080/ws') {
    this.url = url;
  }

  /**
   * Connect to WebSocket server
   */
  connect(): void {
    if (this.ws?.readyState === WebSocket.OPEN) {
      console.log('WebSocket already connected');
      return;
    }

    console.log(`Connecting to WebSocket at ${this.url}...`);
    this.connectionState = 'connecting';
    this.emit('connection:connecting', {});

    try {
      this.ws = new WebSocket(this.url);

      this.ws.onopen = this.handleOpen.bind(this);
      this.ws.onmessage = this.handleMessage.bind(this);
      this.ws.onclose = this.handleClose.bind(this);
      this.ws.onerror = this.handleError.bind(this);

      // Set connection timeout
      this.connectionTimer = setTimeout(() => {
        if (this.connectionState === 'connecting') {
          console.error('WebSocket connection timeout');
          this.ws?.close();
        }
      }, this.connectionTimeout);
    } catch (error) {
      console.error('Failed to create WebSocket connection:', error);
      this.connectionState = 'error';
      this.scheduleReconnect();
    }
  }

  /**
   * Disconnect from WebSocket server
   */
  disconnect(): void {
    this.clearReconnectTimer();
    this.clearConnectionTimer();
    this.clearHeartbeatTimer();
    if (this.ws) {
      this.ws.close();
      this.ws = null;
    }
    this.connectionState = 'disconnected';
    this.reconnectAttempts = 0;
    this.emit('connection:disconnected', {});
  }

  /**
   * Subscribe to specific event type
   */
  subscribe(eventType: string, handler: MessageHandler): () => void {
    if (!this.messageHandlers.has(eventType)) {
      this.messageHandlers.set(eventType, []);
    }
    this.messageHandlers.get(eventType)!.push(handler);

    // Return unsubscribe function
    return () => {
      const handlers = this.messageHandlers.get(eventType);
      if (handlers) {
        const index = handlers.indexOf(handler);
        if (index > -1) {
          handlers.splice(index, 1);
        }
      }
    };
  }

  /**
   * Send message to WebSocket server
   */
  send(message: WebSocketMessage): void {
    if (this.ws?.readyState === WebSocket.OPEN) {
      this.ws.send(JSON.stringify(message));
    } else {
      console.warn('WebSocket not connected, message not sent:', message);
    }
  }

  /**
   * Get current connection state
   */
  getConnectionState(): ConnectionState {
    return this.connectionState;
  }

  /**
   * Check if connected
   */
  isConnected(): boolean {
    return this.connectionState === 'connected';
  }

  // ==========================================================================
  // Private Methods
  // ==========================================================================

  private handleOpen(): void {
    console.log('WebSocket connected');
    this.connectionState = 'connected';
    this.reconnectAttempts = 0;
    this.clearReconnectTimer();
    this.clearConnectionTimer();
    this.lastHeartbeat = Date.now();
    this.startHeartbeat();
    this.emit('connection:connected', {});
  }

  private handleMessage(event: MessageEvent): void {
    this.lastHeartbeat = Date.now();
    try {
      const message: WebSocketMessage = JSON.parse(event.data);
      this.routeMessage(message);
    } catch (error) {
      console.error('Failed to parse WebSocket message:', error);
    }
  }

  private handleClose(event: CloseEvent): void {
    console.log('WebSocket closed:', event.code, event.reason);
    this.connectionState = 'disconnected';
    this.ws = null;
    this.scheduleReconnect();
    this.emit('connection:disconnected', { code: event.code, reason: event.reason });
  }

  private handleError(error: Event): void {
    console.error('WebSocket error:', error);
    this.connectionState = 'error';
    this.emit('connection:error', { error });
  }

  private routeMessage(message: WebSocketMessage): void {
    // Route to specific event type handlers
    const handlers = this.messageHandlers.get(message.type) || [];
    handlers.forEach(handler => {
      try {
        handler(message);
      } catch (error) {
        console.error(`Error in message handler for ${message.type}:`, error);
      }
    });

    // Also route to wildcard handlers
    const wildcardHandlers = this.messageHandlers.get('*') || [];
    wildcardHandlers.forEach(handler => {
      try {
        handler(message);
      } catch (error) {
        console.error('Error in wildcard message handler:', error);
      }
    });
  }

  private scheduleReconnect(): void {
    if (this.reconnectAttempts >= this.maxReconnectAttempts) {
      console.error('Max reconnection attempts reached, giving up');
      return;
    }

    if (this.reconnectTimer) return;

    const delay = this.reconnectDelay * Math.pow(2, this.reconnectAttempts);
    console.log(`Scheduling reconnect in ${delay}ms (attempt ${this.reconnectAttempts + 1})`);

    this.reconnectTimer = setTimeout(() => {
      this.reconnectAttempts++;
      this.connect();
    }, delay);
  }

  private clearReconnectTimer(): void {
    if (this.reconnectTimer) {
      clearTimeout(this.reconnectTimer);
      this.reconnectTimer = null;
    }
  }

  private clearConnectionTimer(): void {
    if (this.connectionTimer) {
      clearTimeout(this.connectionTimer);
      this.connectionTimer = null;
    }
  }

  private clearHeartbeatTimer(): void {
    if (this.heartbeatTimer) {
      clearInterval(this.heartbeatTimer);
      this.heartbeatTimer = null;
    }
  }

  private startHeartbeat(): void {
    this.clearHeartbeatTimer();
    this.heartbeatTimer = setInterval(() => {
      const now = Date.now();
      if (now - this.lastHeartbeat > this.heartbeatInterval * 2) {
        console.warn('WebSocket heartbeat timeout - closing connection');
        this.ws?.close();
      }
    }, this.heartbeatInterval);
  }

  private emit(eventType: string, data: unknown): void {
    const message: WebSocketMessage = {
      type: eventType,
      data,
      timestamp: Date.now(),
    };

    // Internal event routing
    const handlers = this.messageHandlers.get(eventType) || [];
    handlers.forEach(handler => handler(message));
  }

  /**
   * Set custom reconnect delay
   */
  setReconnectDelay(delay: number): void {
    this.reconnectDelay = delay;
  }

  /**
   * Set max reconnection attempts
   */
  setMaxReconnectAttempts(attempts: number): void {
    this.maxReconnectAttempts = attempts;
  }
}

// ==========================================================================
// Singleton Instance
// ==========================================================================

let wsManagerInstance: AgentWebSocketManager | null = null;

/**
 * Get singleton WebSocket manager instance
 */
export function getWebSocketManager(url?: string): AgentWebSocketManager {
  if (!wsManagerInstance) {
    wsManagerInstance = new AgentWebSocketManager(url);
  }
  return wsManagerInstance;
}

/**
 * Reset WebSocket manager instance (mainly for testing)
 */
export function resetWebSocketManager(): void {
  if (wsManagerInstance) {
    wsManagerInstance.disconnect();
    wsManagerInstance = null;
  }
}

// ==========================================================================
// React Hook
// ==========================================================================

/**
 * React hook for WebSocket connection
 */
export function useWebSocket(url?: string) {
  const [connectionState, setConnectionState] = useState<ConnectionState>('disconnected');
  const [isConnected, setIsConnected] = useState(false);

  useEffect(() => {
    const manager = getWebSocketManager(url);

    // Subscribe to connection state changes
    const unsubscribeConnected = manager.subscribe('connection:connected', () => {
      setConnectionState('connected');
      setIsConnected(true);
    });

    const unsubscribeDisconnected = manager.subscribe('connection:disconnected', () => {
      setConnectionState('disconnected');
      setIsConnected(false);
    });

    const unsubscribeConnecting = manager.subscribe('connection:connecting', () => {
      setConnectionState('connecting');
      setIsConnected(false);
    });

    const unsubscribeError = manager.subscribe('connection:error', () => {
      setConnectionState('error');
      setIsConnected(false);
    });

    // Connect on mount
    manager.connect();

    // Disconnect on unmount
    return () => {
      unsubscribeConnected();
      unsubscribeDisconnected();
      unsubscribeConnecting();
      unsubscribeError();
      // Don't disconnect here as manager is singleton
    };
  }, [url]);

  const manager = getWebSocketManager(url);

  return {
    manager,
    connectionState,
    isConnected,
    connect: () => manager.connect(),
    disconnect: () => manager.disconnect(),
  };
}
