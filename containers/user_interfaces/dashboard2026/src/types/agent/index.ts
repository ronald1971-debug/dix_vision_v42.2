/**
 * Agent Operations Center Type Definitions
 * 
 * Types for INDIRA, DYON, and shared agent activities
 */

// ============================================================================
// INDIRA Activity Types
// ============================================================================

export type IndiraActivityType =
  | 'goal-setting'
  | 'task-execution'
  | 'portfolio-reasoning'
  | 'risk-reasoning'
  | 'trade-reasoning'
  | 'confidence-analysis'
  | 'market-research'
  | 'trader-modeling'
  | 'strategy-creation'
  | 'strategy-evolution'
  | 'learning-activity'
  | 'browser-session';

export interface IndiraActivity {
  id: string;
  type: IndiraActivityType;
  timestamp: number;
  status: 'active' | 'completed' | 'paused' | 'error';
  data: unknown;
  context?: {
    objective?: string;
    strategy?: string;
    market?: string;
    trader?: string;
  };
}

export interface IndiraContext {
  currentObjectives: Objective[];
  activeResearch: Research[];
  activeTraderModels: TraderModel[];
  activeStrategies: Strategy[];
  portfolioReasoning: ReasoningProcess;
  riskReasoning: ReasoningProcess;
}

export interface Objective {
  id: string;
  title: string;
  description: string;
  priority: 'critical' | 'high' | 'medium' | 'low';
  status: 'active' | 'completed' | 'paused';
  progress: number;
  deadline?: number;
  relatedStrategies: string[];
}

export interface Research {
  id: string;
  topic: string;
  status: 'active' | 'completed' | 'paused';
  progress: number;
  findings: Finding[];
  relatedMarkets: string[];
  relatedTraders: string[];
}

export interface TraderModel {
  id: string;
  traderId: string;
  modelType: 'behavioral' | 'performance' | 'pattern';
  accuracy: number;
  confidence: number;
  lastUpdated: number;
  predictions: Prediction[];
}

export interface Strategy {
  id: string;
  name: string;
  type: string;
  status: 'active' | 'testing' | 'deprecated';
  performance: number;
}

export interface ReasoningProcess {
  id: string;
  type: 'portfolio' | 'risk' | 'trade';
  status: 'active' | 'completed';
  steps: ReasoningStep[];
  conclusion: string;
  confidence: number;
  timestamp: number;
}

export interface ReasoningStep {
  id: string;
  description: string;
  data: unknown;
  logic: string;
  timestamp: number;
}

export interface Finding {
  id: string;
  description: string;
  confidence: number;
  timestamp: number;
}

export interface Prediction {
  id: string;
  target: string;
  prediction: string;
  confidence: number;
  timeframe: string;
}

// ============================================================================
// DYON Activity Types
// ============================================================================

export type DyonActivityType =
  | 'goal-setting'
  | 'task-execution'
  | 'repository-analysis'
  | 'mutation-candidate'
  | 'refactor-activity'
  | 'build-task'
  | 'testing-activity'
  | 'code-review'
  | 'architecture-work'
  | 'infrastructure-task'
  | 'debugging-activity'
  | 'deployment-task'
  | 'workspace-activity';

export interface DyonActivity {
  id: string;
  type: DyonActivityType;
  timestamp: number;
  status: 'active' | 'completed' | 'paused' | 'error';
  data: unknown;
  context?: {
    repository?: string;
    file?: string;
    module?: string;
    project?: string;
  };
}

export interface DyonContext {
  repositoryAnalysis: RepoAnalysis;
  activeRefactors: Refactor[];
  activePatchCandidates: Patch[];
  activeAutomation: Automation[];
  activeBuildTasks: Build[];
}

export interface RepoAnalysis {
  repository: string;
  health: RepositoryHealth;
  dependencies: DependencyGraph;
  deadCode: DeadCodeReport;
  coverage: CoverageReport;
  technicalDebt: TechnicalDebtReport;
  lastAnalyzed: number;
}

export interface RepositoryHealth {
  overall: number;
  codeQuality: number;
  testCoverage: number;
  documentation: number;
  security: number;
  performance: number;
}

export interface DependencyGraph {
  nodes: DependencyNode[];
  edges: DependencyEdge[];
}

export interface DependencyNode {
  id: string;
  name: string;
  type: 'module' | 'package' | 'external';
}

export interface DependencyEdge {
  from: string;
  to: string;
  type: 'imports' | 'depends-on';
}

export interface DeadCodeReport {
  files: DeadCodeFile[];
  totalUnusedFunctions: number;
  totalUnusedImports: number;
}

export interface DeadCodeFile {
  path: string;
  unusedFunctions: string[];
  unusedImports: string[];
}

export interface CoverageReport {
  overall: number;
  byModule: Record<string, number>;
}

export interface TechnicalDebtReport {
  overall: number;
  issues: TechnicalDebtIssue[];
}

export interface TechnicalDebtIssue {
  id: string;
  description: string;
  severity: 'low' | 'medium' | 'high' | 'critical';
  file: string;
  line: number;
}

export interface Refactor {
  id: string;
  description: string;
  type: 'performance' | 'readability' | 'maintenance' | 'security';
  priority: 'critical' | 'high' | 'medium' | 'low';
  status: 'pending' | 'active' | 'completed';
  estimatedImpact: number;
  relatedFiles: string[];
}

export interface Patch {
  id: string;
  description: string;
  status: 'candidate' | 'validated' | 'applied';
  confidence: number;
  relatedFiles: string[];
}

export interface Automation {
  id: string;
  name: string;
  type: 'build' | 'test' | 'deploy' | 'monitoring';
  status: 'active' | 'paused' | 'error';
  lastRun: number;
}

export interface Build {
  id: string;
  type: 'incremental' | 'full' | 'release';
  status: 'pending' | 'running' | 'completed' | 'failed';
  startTime: number;
  endTime?: number;
  logs: string[];
}

// ============================================================================
// Shared Task System
// ============================================================================

export interface Task {
  id: string;
  title: string;
  description: string;
  type: 'research' | 'engineering' | 'trading' | 'analysis' | 'general';
  priority: 'critical' | 'high' | 'medium' | 'low';
  status: 'pending' | 'active' | 'completed' | 'blocked' | 'cancelled';
  assignedTo: 'indira' | 'dyon' | 'operator' | 'shared';
  createdBy: string;
  createdAt: number;
  deadline?: number;
  dependencies: string[];
  subtasks: SubTask[];
  progress: number;
  context?: {
    project?: string;
    objective?: string;
    relatedTasks?: string[];
  };
}

export interface SubTask {
  id: string;
  title: string;
  status: 'pending' | 'completed';
  completedAt?: number;
}

export interface Assignment {
  id: string;
  taskId: string;
  assignedTo: 'indira' | 'dyon' | 'operator';
  assignedBy: string;
  assignedAt: number;
  status: 'accepted' | 'declined' | 'pending';
  notes?: string;
}

export interface Project {
  id: string;
  name: string;
  description: string;
  status: 'active' | 'completed' | 'paused';
  tasks: string[];
  milestones: Milestone[];
  createdAt: number;
  deadline?: number;
  progress: number;
}

export interface Milestone {
  id: string;
  name: string;
  deadline: number;
  status: 'pending' | 'completed';
  dependencies: string[];
}

// ============================================================================
// Global Event System
// ============================================================================

export type EventSource =
  | 'system'
  | 'market'
  | 'trade'
  | 'learning'
  | 'governance'
  | 'dyon'
  | 'indira'
  | 'desktop'
  | 'browser';

export interface SystemEvent {
  id: string;
  source: EventSource;
  type: string;
  timestamp: number;
  severity: 'info' | 'warning' | 'error' | 'critical';
  data: unknown;
  context?: {
    agent?: 'indira' | 'dyon';
    task?: string;
    project?: string;
    relatedEvents?: string[];
  };
}

export interface EventFilter {
  source?: EventSource[];
  type?: string[];
  severity?: SystemEvent['severity'][];
  agent?: 'indira' | 'dyon';
  timeRange?: {
    start: number;
    end: number;
  };
  searchQuery?: string;
}

// ============================================================================
// WebSocket Types
// ============================================================================

export type ConnectionState = 'disconnected' | 'connecting' | 'connected' | 'error';

export interface WebSocketMessage {
  type: string;
  data: unknown;
  timestamp: number;
}

export type MessageHandler = (message: WebSocketMessage) => void;

// ============================================================================
// Workspace Types
// ============================================================================

export type WorkspaceType =
  | 'mission-control'
  | 'agent-ops'
  | 'indira-workspace'
  | 'dyon-workspace'
  | 'operator-workspace'
  | 'tool-workspace'
  | 'domain-workspace'
  | 'system-workspace';

export interface Workspace {
  id: string;
  name: string;
  type: WorkspaceType;
  owner: 'operator' | 'indira' | 'dyon' | 'shared';
  state: WorkspaceState;
  panels: WorkspacePanel[];
  sharedTools: SharedTool[];
  activeSessions: Session[];
  lastAccessed: number;
  preferences: WorkspacePreferences;
}

export interface WorkspaceState {
  activePanel: string;
  panelStates: Record<string, PanelState>;
  globalFilters: EventFilter[];
  viewMode: 'grid' | 'list' | 'timeline';
  layout: LayoutConfig;
}

export interface PanelState {
  collapsed: boolean;
  position: number;
  size: number;
}

export interface LayoutConfig {
  columns: number;
  rows: number;
  gap: number;
}

export interface WorkspacePanel {
  id: string;
  name: string;
  type: PanelType;
  component: string;
  position: PanelPosition;
  size: PanelSize;
  state: PanelState;
}

export type PanelType =
  | 'context'
  | 'activity'
  | 'cognitive'
  | 'interaction'
  | 'tool'
  | 'feed'
  | 'timeline';

export interface PanelPosition {
  row: number;
  column: number;
}

export interface PanelSize {
  rows: number;
  columns: number;
}

export interface SharedTool {
  id: string;
  name: string;
  type: 'desktop' | 'browser' | 'knowledge';
  accessibleBy: ('operator' | 'indira' | 'dyon')[];
  session: ToolSession;
}

export interface Session {
  id: string;
  toolId: string;
  owner: 'operator' | 'indira' | 'dyon';
  participants: ('operator' | 'indira' | 'dyon')[];
  state: Record<string, unknown>;
  activity: ToolActivity[];
  startTime: number;
  lastActivity: number;
}

export interface ToolActivity {
  id: string;
  agent: 'operator' | 'indira' | 'dyon';
  action: string;
  data: unknown;
  timestamp: number;
}

export interface ToolSession {
  id: string;
  toolId: string;
  owner: 'operator' | 'indira' | 'dyon';
  participants: ('operator' | 'indira' | 'dyon')[];
  state: Record<string, unknown>;
  activity: ToolActivity[];
  startTime: number;
  lastActivity: number;
}

export interface WorkspacePreferences {
  theme: 'light' | 'dark' | 'auto';
  fontSize: 'small' | 'medium' | 'large';
  density: 'comfortable' | 'compact' | 'spacious';
}
