/**
 * Workspace Type Definitions
 * 
 * Extended types for unified workspace architecture
 */

// ============================================================================
// Base Workspace Types
// ============================================================================

export type WorkspaceId = string;

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
  customData?: Record<string, unknown>;
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

// ============================================================================
// Event Filter Types
// ============================================================================

import type { SystemEvent } from '../agent';

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
// Workspace Switching System
// ============================================================================

export interface WorkspaceNavigation {
  currentWorkspace: Workspace;
  workspaceHistory: Workspace[];
  workspaceFavorites: Workspace[];
  quickSwitch: QuickSwitchConfig;
}

export interface QuickSwitchConfig {
  enabled: boolean;
  shortcut: string;
  recentWorkspaces: Workspace[];
}

export interface WorkspaceSwitcher {
  switchWorkspace(workspaceId: string): Promise<void>;
  switchToPreviousWorkspace(): Promise<void>;
  switchToNextWorkspace(): Promise<void>;
  addToFavorites(workspaceId: string): void;
  removeFromFavorites(workspaceId: string): void;
  getRecentWorkspaces(limit: number): Workspace[];
}

// ============================================================================
// Cross-Workspace Communication
// ============================================================================

export interface WorkspaceEventBus {
  publish(event: WorkspaceEvent): void;
  subscribe(eventType: string, handler: EventHandler): () => void;
  unsubscribe(eventType: string, handler: EventHandler): void;
}

export interface WorkspaceEvent {
  id: string;
  type: string;
  source: WorkspaceId;
  target?: WorkspaceId;
  data: unknown;
  timestamp: number;
}

export type WorkspaceEventType =
  | 'task:assigned'
  | 'task:completed'
  | 'agent:status-change'
  | 'workspace:activity'
  | 'tool:used'
  | 'system:alert'
  | 'collaboration:request';

export type EventHandler = (event: WorkspaceEvent) => void;

// ============================================================================
// INDIRA Workspace Specific Types
// ============================================================================

export interface IndiraWorkspaceConfig {
  id: string;
  name: string;
  type: 'indira-workspace';
  owner: 'operator' | 'indira' | 'dyon' | 'shared';
  state: WorkspaceState;
  panels: [
    IndiraContextPanel,
    IndiraCognitivePanel,
    IndiraActivityPanel,
    IndiraInteractionPanel
  ];
  sharedTools: [
    BrowserTool,
    KnowledgeTool,
    DesktopTool
  ];
  activeSessions: Session[];
  lastAccessed: number;
  preferences: WorkspacePreferences;
}

export interface IndiraContextPanel {
  currentObjectives: Objective[];
  activeResearch: Research[];
  activeTraderModels: TraderModel[];
  activeStrategies: Strategy[];
  activeOpportunities: Opportunity[];
  portfolioState: PortfolioState;
  riskState: RiskState;
}

export interface IndiraCognitivePanel {
  portfolioReasoning: ReasoningProcess;
  riskReasoning: ReasoningProcess;
  tradeReasoning: ReasoningProcess;
  confidenceAnalysis: ConfidenceAnalysis;
}

export interface IndiraActivityPanel {
  researchActivities: ResearchActivity[];
  learningActivities: LearningActivity[];
  strategyActivities: StrategyActivity[];
  traderModelingActivities: ModelingActivity[];
  browserSessions: BrowserSession[];
}

export interface IndiraInteractionPanel {
  voiceCommands: VoiceCommand[];
  chatMessages: ChatMessage[];
  taskAssignments: TaskAssignment[];
  quickActions: QuickAction[];
}

// ============================================================================
// INDIRA Context Types
// ============================================================================

export interface Objective {
  id: string;
  title: string;
  description: string;
  priority: 'critical' | 'high' | 'medium' | 'low';
  status: 'active' | 'completed' | 'paused';
  progress: number;
  deadline?: number;
  relatedStrategies: string[];
  createdAt: number;
  updatedAt: number;
}

export interface Research {
  id: string;
  topic: string;
  status: 'active' | 'completed' | 'paused';
  progress: number;
  findings: Finding[];
  relatedMarkets: string[];
  relatedTraders: string[];
  startDate: number;
  endDate?: number;
  confidence: number;
}

export interface TraderModel {
  id: string;
  traderId: string;
  modelType: 'behavioral' | 'performance' | 'pattern';
  accuracy: number;
  confidence: number;
  lastUpdated: number;
  predictions: Prediction[];
  performanceMetrics: PerformanceMetrics;
}

export interface Strategy {
  id: string;
  name: string;
  type: string;
  status: 'active' | 'testing' | 'deprecated';
  performance: number;
  parameters: Record<string, unknown>;
  riskLevel: 'low' | 'medium' | 'high' | 'critical';
  backtestResults?: BacktestResults;
  createdAt: number;
  lastModified: number;
}

export interface Opportunity {
  id: string;
  type: 'trade' | 'research' | 'arbitrage';
  asset: string;
  description: string;
  confidence: number;
  expectedReturn: number;
  riskLevel: 'low' | 'medium' | 'high';
  timeframe: string;
  createdAt: number;
  expiresAt?: number;
}

export interface PortfolioState {
  totalValue: number;
  positions: Position[];
  allocation: Allocation;
  performance: Performance;
  lastUpdated: number;
}

export interface RiskState {
  overallRisk: 'low' | 'medium' | 'high' | 'critical';
  riskFactors: RiskFactor[];
  constraints: Constraint[];
  exposureLimits: ExposureLimit[];
  lastUpdated: number;
}

export interface Position {
  id: string;
  asset: string;
  quantity: number;
  entryPrice: number;
  currentPrice: number;
  unrealizedPnL: number;
  realizedPnL: number;
  openDate: number;
}

export interface Allocation {
  byAsset: Record<string, number>;
  byStrategy: Record<string, number>;
  byRisk: Record<string, number>;
}

export interface Performance {
  daily: number;
  weekly: number;
  monthly: number;
  ytd: number;
  sharpeRatio: number;
  maxDrawdown: number;
}

export interface PerformanceMetrics {
  winRate: number;
  averageReturn: number;
  volatility: number;
  maxDrawdown: number;
  profitFactor: number;
}

export interface Finding {
  id: string;
  description: string;
  confidence: number;
  evidence: string[];
  timestamp: number;
}

export interface Prediction {
  id: string;
  target: string;
  prediction: string;
  confidence: number;
  timeframe: string;
  actual?: string;
  accuracy?: number;
  timestamp: number;
}

export interface BacktestResults {
  totalReturn: number;
  sharpeRatio: number;
  maxDrawdown: number;
  winRate: number;
  totalTrades: number;
  averageHoldTime: number;
  startDate: number;
  endDate: number;
}

export interface RiskFactor {
  id: string;
  factor: string;
  level: 'low' | 'medium' | 'high' | 'critical';
  impact: number;
  trend: 'improving' | 'stable' | 'deteriorating';
}

export interface Constraint {
  id: string;
  type: 'position_limit' | 'risk_limit' | 'concentration_limit';
  limit: number;
  current: number;
  status: 'compliant' | 'warning' | 'violation';
}

export interface ExposureLimit {
  asset: string;
  limit: number;
  current: number;
  status: 'compliant' | 'warning' | 'violation';
}

// ============================================================================
// INDIRA Cognitive Process Types
// ============================================================================

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

export interface ConfidenceAnalysis {
  overall: number;
  portfolio: number;
  risk: number;
  trades: number;
  factors: ConfidenceFactor[];
  lastUpdated: number;
}

export interface ConfidenceFactor {
  factor: string;
  impact: number;
  confidence: number;
  trend: 'improving' | 'stable' | 'deteriorating';
}

// ============================================================================
// INDIRA Activity Types (Extended)
// ============================================================================

export interface ResearchActivity {
  id: string;
  topic: string;
  status: 'active' | 'completed' | 'paused';
  progress: number;
  sources: Source[];
  findings: Finding[];
  timestamp: number;
}

export interface LearningActivity {
  id: string;
  type: 'market' | 'trader' | 'strategy' | 'pattern';
  status: 'active' | 'completed';
  data: unknown;
  confidence: number;
  timestamp: number;
}

export interface StrategyActivity {
  id: string;
  strategyId: string;
  action: 'creation' | 'evolution' | 'testing' | 'deployment';
  status: 'active' | 'completed' | 'failed';
  performance?: number;
  timestamp: number;
}

export interface ModelingActivity {
  id: string;
  traderId: string;
  modelType: 'behavioral' | 'performance' | 'pattern';
  action: 'training' | 'validation' | 'update';
  status: 'active' | 'completed' | 'failed';
  accuracy?: number;
  timestamp: number;
}

export interface BrowserSession {
  id: string;
  url: string;
  tabs: BrowserTab[];
  navigationHistory: NavigationEntry[];
  researchActivity: ResearchActivity[];
  startTime: number;
  lastActivity: number;
}

export interface BrowserTab {
  id: string;
  url: string;
  title: string;
  favicon?: string;
  isActive: boolean;
}

export interface NavigationEntry {
  url: string;
  title: string;
  timestamp: number;
}

export interface Source {
  id: string;
  name: string;
  type: 'news' | 'social' | 'api' | 'documentation';
  reliability: number;
}

// ============================================================================
// INDIRA Interaction Types
// ============================================================================

export interface VoiceCommand {
  id: string;
  transcript: string;
  intent: CommandIntent;
  response: string;
  confidence: number;
  timestamp: number;
}

export interface CommandIntent {
  agent: 'indira' | 'dyon' | 'both' | 'system';
  action: string;
  context: unknown;
}

export interface ChatMessage {
  id: string;
  sender: 'operator' | 'indira';
  content: string;
  context: unknown;
  timestamp: number;
  taskAssignment?: TaskAssignment;
}

export interface TaskAssignment {
  id: string;
  taskId: string;
  assignedTo: 'indira' | 'dyon';
  assignedBy: string;
  assignedAt: number;
  status: 'pending' | 'accepted' | 'completed' | 'declined';
  notes?: string;
}

export interface QuickAction {
  id: string;
  label: string;
  action: () => void;
  icon: string;
  shortcut?: string;
}

// ============================================================================
// Tool Types (Extended)
// ============================================================================

export interface BrowserTool {
  id: string;
  name: string;
  sessions: BrowserSession[];
  activeSession?: string;
  capabilities: BrowserCapabilities;
}

export interface BrowserCapabilities {
  research: boolean;
  trading: boolean;
  analysis: boolean;
  social: boolean;
}

export interface KnowledgeTool {
  id: string;
  name: string;
  knowledgeGraph: KnowledgeGraph;
  searchEnabled: boolean;
  lastUpdated: number;
}

export interface KnowledgeGraph {
  nodes: KnowledgeNode[];
  edges: KnowledgeEdge[];
  clusters: KnowledgeCluster[];
}

export interface KnowledgeNode {
  id: string;
  label: string;
  type: 'concept' | 'entity' | 'relationship';
  properties: Record<string, unknown>;
}

export interface KnowledgeEdge {
  source: string;
  target: string;
  type: string;
  weight: number;
}

export interface KnowledgeCluster {
  id: string;
  label: string;
  nodes: string[];
  centrality: number;
}

export interface DesktopTool {
  id: string;
  name: string;
  applications: DesktopApplication[];
  activeProcesses: DesktopProcess[];
}

export interface DesktopApplication {
  id: string;
  name: string;
  path: string;
  status: 'running' | 'stopped' | 'crashed';
  resourceUsage: ResourceUsage;
}

export interface DesktopProcess {
  id: string;
  name: string;
  pid: number;
  cpuUsage: number;
  memoryUsage: number;
  status: 'running' | 'stopped';
}

export interface ResourceUsage {
  cpu: number;
  memory: number;
  disk: number;
  network: number;
}
