/**
 * dashboard2026/src/types/generated/cognitive.ts
 * TypeScript type definitions for Cognitive Environment API
 * 
 * Generated from cognitive_control_center Python models
 */

/**
 * Types of entities in the cognitive environment
 */
export enum CognitiveEntityType {
  OPERATOR = 'operator',
  INDIRA = 'indira', // Trading agent
  DYON = 'dyon',     // System maintenance agent
  SYSTEM = 'system', // System-level processes
}

/**
 * Types of workspaces in the cognitive environment
 */
export enum WorkspaceType {
  AGENT_OPERATIONS = 'agent_operations',
  OPERATOR_WORKSPACE = 'operator_workspace',
  INDIRA_WORKSPACE = 'indira_workspace',
  DYON_WORKSPACE = 'dyon_workspace',
  TRADING_DOMAIN = 'trading_domain',
  MEMECOIN_DOMAIN = 'memecoin_domain',
  SYSTEM_MAINTENANCE = 'system_maintenance',
}

/**
 * Event within the cognitive environment
 */
export interface CognitiveEvent {
  entity_type: CognitiveEntityType;
  entity_id: string;
  event_type: string;
  timestamp: string;
  data: Record<string, unknown>;
  workspace?: WorkspaceType;
}

/**
 * Real-time agent activity for observability
 */
export interface AgentActivity {
  agent_type: CognitiveEntityType;
  agent_id: string;
  current_goal: string;
  current_task: string;
  cognitive_process: string;
  tools_in_use: string[];
  memory_accesses: string[];
  timestamp: string;
  workspace?: string;
}

/**
 * Workspace configuration
 */
export interface Workspace {
  workspace_type: WorkspaceType;
  name: string;
  description: string;
  active_entities: string[];
  shared_tools: string[];
  activity_log: WorkspaceActivity[];
  created_at: string;
  last_activity: string;
}

/**
 * Activity log entry for workspace
 */
export interface WorkspaceActivity {
  entity_id: string;
  action: string;
  timestamp: string;
  reason: string;
}

/**
 * Workspace transition record
 */
export interface WorkspaceTransition {
  entity_id: string;
  from_workspace: WorkspaceType | null;
  to_workspace: WorkspaceType;
  timestamp: string;
  reason: string;
}

/**
 * Cognitive environment state
 */
export interface CognitiveEnvironmentState {
  active_entities: Record<string, CognitiveEntityType>;
  active_workspaces: Record<WorkspaceType, Workspace>;
  agent_count: number;
  workspace_count: number;
  recent_events: number;
}

/**
 * Activity feed event (for agent operations center)
 */
export interface ActivityFeedEvent {
  agent_type: CognitiveEntityType;
  agent_id: string;
  activity_type: ActivityType;
  timestamp: string;
  description: string;
  data: Record<string, unknown>;
  severity: 'info' | 'warning' | 'error' | 'critical';
}

/**
 * Activity types
 */
export enum ActivityType {
  COGNITIVE_PROCESS = 'cognitive_process',
  TOOL_USAGE = 'tool_usage',
  MEMORY_ACCESS = 'memory_access',
  TASK_UPDATE = 'task_update',
  GOAL_CHANGE = 'goal_change',
  LEARNING_ACTIVITY = 'learning_activity',
  COMMUNICATION = 'communication',
  ERROR = 'error',
}

/**
 * Agent lifecycle event
 */
export interface AgentLifecycleEvent {
  agent_id: string;
  agent_type: CognitiveEntityType;
  from_state: string;
  to_state: string;
  timestamp: string;
  reason: string;
  data: Record<string, unknown>;
}

/**
 * Agent lifecycle states
 */
export enum AgentState {
  REGISTERED = 'registered',
  INITIALIZING = 'initializing',
  ACTIVE = 'active',
  PAUSED = 'paused',
  DEACTIVATING = 'deactivating',
  INACTIVE = 'inactive',
  ERROR = 'error',
}

/**
 * Agent registration
 */
export interface AgentRegistration {
  agent_id: string;
  agent_type: CognitiveEntityType;
  state: AgentState;
  registered_at: string;
  activated_at: string | null;
  deactivated_at: string | null;
  current_workspace: WorkspaceType | null;
  metadata: Record<string, unknown>;
}