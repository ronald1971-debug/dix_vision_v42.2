/**
 * WebSocket Client for Real-Time Updates
 * 
 * Manages WebSocket connections to the API server for real-time data streaming.
 * Handles reconnection, error recovery, and data dispatching to components.
 */

type WebSocketMessage = {
  type: string;
  timestamp: number;
  data: any;
};

type WebSocketEventHandler = (message: WebSocketMessage) => void;

class WebSocketClient {
  private ws: WebSocket | null = null;
  private reconnectInterval: number = 5000;
  private reconnectAttempts: number = 0;
  private maxReconnectAttempts: number = 10;
  private handlers: Map<string, Set<WebSocketEventHandler>> = new Map();
  private url: string;
  private isConnecting: boolean = false;
  private reconnectTimer: number | null = null;

  constructor(url: string) {
    this.url = url;
  }

  connect(): void {
    if (this.isConnecting || (this.ws && this.ws.readyState === WebSocket.OPEN)) {
      return;
    }

    this.isConnecting = true;

    try {
      this.ws = new WebSocket(this.url);

      this.ws.onopen = () => {
        console.log(`[WS] Connected to ${this.url}`);
        this.isConnecting = false;
        this.reconnectAttempts = 0;
        this.clearReconnectTimer();
      };

      this.ws.onmessage = (event) => {
        try {
          const message: WebSocketMessage = JSON.parse(event.data);
          this.dispatch(message);
        } catch (error) {
          console.error('[WS] Error parsing message:', error);
        }
      };

      this.ws.onerror = (error) => {
        console.error(`[WS] Error on ${this.url}:`, error);
        this.isConnecting = false;
      };

      this.ws.onclose = () => {
        console.log(`[WS] Disconnected from ${this.url}`);
        this.isConnecting = false;
        this.ws = null;
        this.scheduleReconnect();
      };
    } catch (error) {
      console.error('[WS] Failed to create WebSocket:', error);
      this.isConnecting = false;
      this.scheduleReconnect();
    }
  }

  disconnect(): void {
    this.clearReconnectTimer();
    if (this.ws) {
      this.ws.close();
      this.ws = null;
    }
    this.isConnecting = false;
  }

  on(eventType: string, handler: WebSocketEventHandler): () => void {
    if (!this.handlers.has(eventType)) {
      this.handlers.set(eventType, new Set());
    }
    this.handlers.get(eventType)!.add(handler);

    // Return unsubscribe function
    return () => {
      const handlers = this.handlers.get(eventType);
      if (handlers) {
        handlers.delete(handler);
      }
    };
  }

  private dispatch(message: WebSocketMessage): void {
    const handlers = this.handlers.get(message.type);
    if (handlers) {
      handlers.forEach(handler => {
        try {
          handler(message);
        } catch (error) {
          console.error(`[WS] Error in handler for ${message.type}:`, error);
        }
      });
    }
  }

  private scheduleReconnect(): void {
    if (this.reconnectAttempts >= this.maxReconnectAttempts) {
      console.error('[WS] Max reconnection attempts reached');
      return;
    }

    this.reconnectAttempts++;
    const delay = this.reconnectInterval * Math.pow(1.5, this.reconnectAttempts - 1);

    console.log(`[WS] Scheduling reconnect in ${delay}ms (attempt ${this.reconnectAttempts})`);

    this.reconnectTimer = window.setTimeout(() => {
      this.connect();
    }, delay);
  }

  private clearReconnectTimer(): void {
    if (this.reconnectTimer !== null) {
      window.clearTimeout(this.reconnectTimer);
      this.reconnectTimer = null;
    }
  }

  isConnected(): boolean {
    return this.ws !== null && this.ws.readyState === WebSocket.OPEN;
  }
}

// Singleton instances for different WebSocket endpoints
let systemStatusClient: WebSocketClient | null = null;
let missionControlClient: WebSocketClient | null = null;
let portfolioClient: WebSocketClient | null = null;
let hazardsClient: WebSocketClient | null = null;

export function getSystemStatusClient(url: string = 'ws://127.0.0.1:8003/ws/system/status'): WebSocketClient {
  if (!systemStatusClient) {
    systemStatusClient = new WebSocketClient(url);
    systemStatusClient.connect();
  }
  return systemStatusClient;
}

export function getMissionControlClient(url: string = 'ws://127.0.0.1:8003/ws/mission-control'): WebSocketClient {
  if (!missionControlClient) {
    missionControlClient = new WebSocketClient(url);
    missionControlClient.connect();
  }
  return missionControlClient;
}

export function getPortfolioClient(url: string = 'ws://127.0.0.1:8003/ws/portfolio'): WebSocketClient {
  if (!portfolioClient) {
    portfolioClient = new WebSocketClient(url);
    portfolioClient.connect();
  }
  return portfolioClient;
}

export function getHazardsClient(url: string = 'ws://127.0.0.1:8003/ws/hazards'): WebSocketClient {
  if (!hazardsClient) {
    hazardsClient = new WebSocketClient(url);
    hazardsClient.connect();
  }
  return hazardsClient;
}

export function disconnectAll(): void {
  systemStatusClient?.disconnect();
  missionControlClient?.disconnect();
  portfolioClient?.disconnect();
  hazardsClient?.disconnect();
  
  systemStatusClient = null;
  missionControlClient = null;
  portfolioClient = null;
  hazardsClient = null;
}

export type { WebSocketMessage, WebSocketEventHandler };
