/**
 * dashboard2026/src/api/cognitive.ts
 * Cognitive Environment API Client
 * 
 * Connects Dashboard2026 React frontend with cognitive_control_center backend services
 * Provides TypeScript interfaces and API methods for the cognitive operating environment
 */

// Temporarily define types inline to avoid import path issues
// TODO: Fix import path resolution and use types/generated/cognitive.ts

/**
 * Types of entities in the cognitive environment
 */
enum CognitiveEntityType {
  OPERATOR = 'operator',
  INDIRA = 'indira', // Trading agent
  DYON = 'dyon',     // System maintenance agent
  SYSTEM = 'system', // System-level processes
}

/**
 * Types of workspaces in the cognitive environment
 */
enum WorkspaceType {
  AGENT_OPERATIONS = 'agent_operations',
  OPERATOR_WORKSPACE = 'operator_workspace',
  INDIRA_WORKSPACE = 'indira_workspace',
  DYON_WORKSPACE = 'dyon_workspace',
  TRADING_DOMAIN = 'trading_domain',
  MEMECOIN_DOMAIN = 'memecoin_domain',
  SYSTEM_MAINTENANCE = 'system_maintenance',
}

/**
 * Real-time agent activity for observability
 */
interface AgentActivity {
  agent_type: CognitiveEntityType;
  agent_id: string;
  current_goal: string;
  current_task: string;
  cognitive_process: string;
  tools_in_use: string[];
  memory_accesses: string[];
  timestamp: string;
  workspace?: WorkspaceType;
}

/**
 * Cognitive Environment API Client
 */
export class CognitiveEnvironmentAPI {
  private baseURL: string;
  private token: string | null = null;

  constructor(baseURL: string = '/api/cognitive') {
    this.baseURL = baseURL;
    this.loadToken();
  }

  private loadToken(): void {
    this.token = localStorage.getItem('dix_token') || null;
  }

  private async fetchAPI<T>(
    endpoint: string,
    options: RequestInit = {}
  ): Promise<T> {
    const url = `${this.baseURL}${endpoint}`;
    const headers = new Headers();
    headers.set('Content-Type', 'application/json');
    
    if (this.token) {
      headers.set('Authorization', `Bearer ${this.token}`);
    }
    
    // Copy any additional headers from options
    if (options.headers) {
      const optionsHeaders = options.headers as Headers;
      optionsHeaders.forEach((value, key) => {
        headers.set(key, value);
      });
    }

    const response = await fetch(url, {
      ...options,
      headers,
    });

    if (!response.ok) {
      throw new Error(`Cognitive API error: ${response.status} ${response.statusText}`);
    }

    return response.json() as Promise<T>;
  }

  /**
   * Register an entity in the cognitive environment
   */
  async registerEntity(
    entityId: string,
    entityType: CognitiveEntityType
  ): Promise<{ success: boolean }> {
    return this.fetchAPI('/register', {
      method: 'POST',
      body: JSON.stringify({ entity_id: entityId, entity_type: entityType }),
    });
  }

  /**
   * Activate a workspace in the cognitive environment
   */
  async activateWorkspace(
    workspaceType: WorkspaceType,
    config?: Record<string, unknown>
  ): Promise<{ success: boolean }> {
    return this.fetchAPI('/workspace/activate', {
      method: 'POST',
      body: JSON.stringify({ workspace_type: workspaceType, config }),
    });
  }

  /**
   * Transition an entity to a different workspace
   */
  async transitionEntity(
    entityId: string,
    toWorkspace: WorkspaceType,
    reason: string = ''
  ): Promise<{ success: boolean; from_workspace?: string }> {
    return this.fetchAPI('/workspace/transition', {
      method: 'POST',
      body: JSON.stringify({
        entity_id: entityId,
        to_workspace: toWorkspace,
        reason,
      }),
    });
  }

  /**
   * Get the current workspace for an entity
   */
  async getEntityWorkspace(entityId: string): Promise<{ workspace_type: string }> {
    return this.fetchAPI(`/workspace/${entityId}`);
  }

  /**
   * Get all workspaces
   */
  async getAllWorkspaces(): Promise<
    Record<string, { name: string; description: string; shared_tools: string[] }>
  > {
    return this.fetchAPI('/workspaces');
  }

  /**
   * Get agents currently in a workspace
   */
  async getWorkspaceEntities(workspaceType: WorkspaceType): Promise<{ entity_ids: string[] }> {
    return this.fetchAPI(`/workspace/${workspaceType}/entities`);
  }

  /**
   * Get current agent activities for observability
   */
  async getAgentActivities(): Promise<Record<string, AgentActivity>> {
    return this.fetchAPI('/activities');
  }

  /**
   * Get recent activity across all agents
   */
  async getRecentActivity(minutes: number = 5): Promise<{ activities: AgentActivity[] }> {
    return this.fetchAPI(`/activities/recent?minutes=${minutes}`);
  }

  /**
   * Get cognitive environment state
   */
  async getEnvironmentState(): Promise<{
    active_entities: Record<string, string>;
    active_workspaces: Record<string, Record<string, unknown>>;
    agent_count: number;
    workspace_count: number;
    recent_events: number;
  }> {
    return this.fetchAPI('/state');
  }

  /**
   * Subscribe to cognitive environment events (WebSocket)
   */
  subscribeToEvents(callback: (event: unknown) => void): WebSocket {
    const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
    const host = window.location.host;
    const ws = new WebSocket(`${protocol}//${host}/api/cognitive/ws`);

    ws.onopen = () => {
      console.log('[Cognitive API] WebSocket connected');
    };

    ws.onmessage = (event) => {
      try {
        const data = JSON.parse(event.data);
        callback(data);
      } catch (error) {
        console.error('[Cognitive API] WebSocket parse error:', error);
      }
    };

    ws.onerror = (error) => {
      console.error('[Cognitive API] WebSocket error:', error);
    };

    ws.onclose = () => {
      console.log('[Cognitive API] WebSocket disconnected');
    };

    return ws;
  }
}

/**
 * Get cognitive snapshot (for CognitiveHealthStrip)
 */
export async function fetchCognitiveSnapshot(signal?: AbortSignal): Promise<{
  indira: {
    tick_count: number;
    cycle_position: number;
  };
  evo: {
    dyon: {
      tick_count: number;
      scan_count: number;
      structural_loop_wired: boolean;
    };
  };
  memory: {
    episodic_size: number;
    semantic_size: number;
    consolidate_seq: number;
  };
  research: {
    running: boolean;
    queue_depth: number;
    total_runs: number;
  };
}> {
  const BASE = (import.meta.env.VITE_API_BASE ?? "").replace(/\/$/, "");
  const token = localStorage.getItem('dix_token') || null;
  
  const headers = new Headers();
  headers.set('Content-Type', 'application/json');
  if (token) {
    headers.set('Authorization', `Bearer ${token}`);
  }

  const response = await fetch(`${BASE}/api/cognitive/snapshot`, {
    signal,
    headers
  });

  if (!response.ok) {
    // Return mock data if API fails (for development)
    console.warn('Cognitive snapshot API unavailable, using mock data');
    return {
      indira: { tick_count: 10, cycle_position: 5 },
      evo: {
        dyon: {
          tick_count: 8,
          scan_count: 15,
          structural_loop_wired: true
        }
      },
      memory: {
        episodic_size: 100,
        semantic_size: 200,
        consolidate_seq: 50
      },
      research: {
        running: false,
        queue_depth: 0,
        total_runs: 0
      }
    };
  }

  return response.json();
}

// Singleton instance
let cognitiveAPIInstance: CognitiveEnvironmentAPI | null = null;

export function getCognitiveEnvironmentAPI(): CognitiveEnvironmentAPI {
  if (!cognitiveAPIInstance) {
    cognitiveAPIInstance = new CognitiveEnvironmentAPI();
  }
  return cognitiveAPIInstance;
}