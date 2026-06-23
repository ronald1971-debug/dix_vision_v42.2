/**
 * StateProjection Bridge
 * 
 * Bridge between React frontend and Python backend StateProjection system.
 * Provides real-time state updates and synchronization between the frontend
 * and the kernel's StateProjection via WebSocket/SSE connections.
 */

import { apiUrl, wsUrl } from '@/api/base';

// ============================================================================
// StateProjection Types
// ============================================================================

export interface StateProjection {
  current_mode: TradingMode;
  mode_transitions: ModeTransition[];
  system_health: SystemHealth;
  engine_status: EngineStatus;
  domain_states: DomainStates;
  world_model: WorldModelState;
  governance_state: GovernanceState;
  last_updated: string;
}

export type TradingMode = 'manual' | 'semi_auto' | 'full_auto';

export interface ModeTransition {
  timestamp: string;
  from_mode: TradingMode;
  to_mode: TradingMode;
  reason: string;
  authorized_by: string;
}

export interface SystemHealth {
  overall_status: 'healthy' | 'degraded' | 'unhealthy';
  engines_status: Record<string, EngineStatus>;
  uptime: number;
  last_health_check: string;
}

export interface EngineStatus {
  status: 'running' | 'stopped' | 'error';
  last_event?: string;
  error_count: number;
  performance_metrics: PerformanceMetrics;
}

export interface PerformanceMetrics {
  latency_ms: number;
  throughput: number;
  error_rate: number;
}

export interface DomainStates {
  indira: DomainState;
  governance: DomainState;
  execution: DomainState;
  operator: DomainState;
  dyon: DomainState;
  world_model: DomainState;
  simulation: DomainState;
  learning: DomainState;
}

export interface DomainState {
  active: boolean;
  last_activity: string;
  event_count: number;
  error_count: number;
}

export interface WorldModelState {
  coherence_score: number;
  regime: string;
  confidence: number;
  last_coherence_check: string;
}

export interface GovernanceState {
  active_constraints: GovernanceConstraint[];
  pending_approvals: number;
  risk_level: 'low' | 'medium' | 'high';
  last_compliance_check: string;
}

export interface GovernanceConstraint {
  id: string;
  name: string;
  type: string;
  status: 'active' | 'suspended';
  limit: number;
  current_value: number;
}

// ============================================================================
// StateProjection Client
// ============================================================================

class StateProjectionClient {
  private static instance: StateProjectionClient;
  private ws: WebSocket | null = null;
  private reconnectInterval: number = 3000;
  private reconnectAttempts: number = 0;
  private maxReconnectAttempts: number = 20;
  private listeners: Set<StateUpdateListener> = new Set();
  private currentState: StateProjection | null = null;
  private url: string;
  private isConnecting: boolean = false;

  private constructor(url?: string) {
    // Use Docker-aware WebSocket URL if no custom URL provided
    this.url = url || wsUrl('/ws/state-projection');
    this.connect();
  }

  static getInstance(url?: string): StateProjectionClient {
    if (!StateProjectionClient.instance) {
      StateProjectionClient.instance = new StateProjectionClient(url);
    }
    return StateProjectionClient.instance;
  }

  connect(): void {
    if (this.isConnecting || (this.ws && this.ws.readyState === WebSocket.OPEN)) {
      return;
    }

    this.isConnecting = true;

    try {
      this.ws = new WebSocket(this.url);

      this.ws.onopen = () => {
        console.log('[StateProjection] Connected to backend StateProjection');
        this.isConnecting = false;
        this.reconnectAttempts = 0;
        
        // Request initial state
        if (this.ws && this.ws.readyState === WebSocket.OPEN) {
          this.ws.send(JSON.stringify({ type: 'subscribe', channel: 'state_projection' }));
        }
      };

      this.ws.onmessage = (event) => {
        try {
          const message = JSON.parse(event.data);
          this.handleMessage(message);
        } catch (error) {
          console.error('[StateProjection] Error parsing message:', error);
        }
      };

      this.ws.onerror = (error) => {
        console.error('[StateProjection] WebSocket error:', error);
        this.isConnecting = false;
      };

      this.ws.onclose = () => {
        console.log('[StateProjection] Disconnected from backend');
        this.isConnecting = false;
        this.ws = null;
        this.scheduleReconnect();
      };
    } catch (error) {
      console.error('[StateProjection] Failed to create WebSocket:', error);
      this.isConnecting = false;
      this.scheduleReconnect();
    }
  }

  disconnect(): void {
    if (this.ws) {
      this.ws.close();
      this.ws = null;
    }
    this.isConnecting = false;
  }

  private handleMessage(message: any): void {
    switch (message.type) {
      case 'state_update':
        this.currentState = message.data as StateProjection;
        this.notifyListeners(message.data);
        break;
      case 'mode_change':
        if (this.currentState) {
          this.currentState.current_mode = message.data.mode;
          this.currentState.mode_transitions.unshift(message.data.transition);
          this.notifyListeners(this.currentState);
        }
        break;
      case 'engine_status':
        if (this.currentState) {
          const engine = message.data.engine;
          this.currentState.system_health.engines_status[engine.name] = engine.status;
          this.notifyListeners(this.currentState);
        }
        break;
      case 'health_update':
        if (this.currentState) {
          this.currentState.system_health = message.data;
          this.notifyListeners(this.currentState);
        }
        break;
      default:
        console.log('[StateProjection] Unknown message type:', message.type);
    }
  }

  private scheduleReconnect(): void {
    if (this.reconnectAttempts >= this.maxReconnectAttempts) {
      console.error('[StateProjection] Max reconnection attempts reached');
      return;
    }

    this.reconnectAttempts++;
    const delay = this.reconnectInterval * Math.pow(1.2, this.reconnectAttempts - 1);

    console.log(`[StateProjection] Scheduling reconnect in ${delay}ms (attempt ${this.reconnectAttempts})`);

    setTimeout(() => {
      this.connect();
    }, delay);
  }

  subscribe(listener: StateUpdateListener): () => void {
    this.listeners.add(listener);
    
    // Return unsubscribe function
    return () => {
      this.listeners.delete(listener);
    };
  }

  private notifyListeners(state: StateProjection): void {
    this.listeners.forEach(listener => {
      try {
        listener(state);
      } catch (error) {
        console.error('[StateProjection] Error in listener:', error);
      }
    });
  }

  getCurrentState(): StateProjection | null {
    return this.currentState;
  }

  async fetchInitialState(): Promise<StateProjection | null> {
    try {
      const response = await fetch(apiUrl('/api/state-projection'));
      if (response.ok) {
        const state = await response.json();
        this.currentState = state;
        return state;
      }
    } catch (error) {
      console.error('[StateProjection] Failed to fetch initial state:', error);
    }
    
    // Return fallback state if fetch fails
    return this.getFallbackState();
  }

  private getFallbackState(): StateProjection {
    return {
      current_mode: 'manual',
      mode_transitions: [],
      system_health: {
        overall_status: 'healthy',
        engines_status: {},
        uptime: 0,
        last_health_check: new Date().toISOString(),
      },
      engine_status: {
        status: 'running',
        performance_metrics: {
          latency_ms: 0,
          throughput: 0,
          error_rate: 0,
        },
        error_count: 0,
      },
      domain_states: {
        indira: { active: true, last_activity: new Date().toISOString(), event_count: 0, error_count: 0 },
        governance: { active: true, last_activity: new Date().toISOString(), event_count: 0, error_count: 0 },
        execution: { active: true, last_activity: new Date().toISOString(), event_count: 0, error_count: 0 },
        operator: { active: true, last_activity: new Date().toISOString(), event_count: 0, error_count: 0 },
        dyon: { active: true, last_activity: new Date().toISOString(), event_count: 0, error_count: 0 },
        world_model: { active: true, last_activity: new Date().toISOString(), event_count: 0, error_count: 0 },
        simulation: { active: true, last_activity: new Date().toISOString(), event_count: 0, error_count: 0 },
        learning: { active: true, last_activity: new Date().toISOString(), event_count: 0, error_count: 0 },
      },
      world_model: {
        coherence_score: 0.95,
        regime: 'normal',
        confidence: 0.9,
        last_coherence_check: new Date().toISOString(),
      },
      governance_state: {
        active_constraints: [],
        pending_approvals: 0,
        risk_level: 'low',
        last_compliance_check: new Date().toISOString(),
      },
      last_updated: new Date().toISOString(),
    };
  }

  async setMode(mode: TradingMode, reason: string, authorizedBy: string): Promise<boolean> {
    try {
      const response = await fetch(apiUrl('/api/mode'), {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          mode,
          reason,
          authorizedBy,
        }),
      });

      return response.ok;
    } catch (error) {
      console.error('[StateProjection] Failed to set mode:', error);
      return false;
    }
  }

  isConnected(): boolean {
    return this.ws !== null && this.ws.readyState === WebSocket.OPEN;
  }
}

// ============================================================================
// Type Definitions
// ============================================================================

type StateUpdateListener = (state: StateProjection) => void;

// ============================================================================
// Public API Functions
// ============================================================================

/**
 * Get StateProjection client instance
 */
export function getStateProjectionClient(url?: string): StateProjectionClient {
  return StateProjectionClient.getInstance(url);
}

/**
 * Get current state projection
 */
export function getCurrentState(): StateProjection | null {
  return StateProjectionClient.getInstance().getCurrentState();
}

/**
 * Fetch initial state from backend
 */
export async function fetchInitialState(): Promise<StateProjection | null> {
  return StateProjectionClient.getInstance().fetchInitialState();
}

/**
 * Set trading mode
 */
export async function setTradingMode(mode: TradingMode, reason: string, authorizedBy: string): Promise<boolean> {
  return StateProjectionClient.getInstance().setMode(mode, reason, authorizedBy);
}

/**
 * Check if StateProjection is connected
 */
export function isStateProjectionConnected(): boolean {
  return StateProjectionClient.getInstance().isConnected();
}