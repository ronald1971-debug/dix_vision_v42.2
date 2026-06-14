/**
 * INDIRA Cognitive Center API Integration
 * 
 * Provides live API integration for all INDIRA Cognitive Center functionality:
 * - Market Intelligence
 * - Trader Intelligence  
 * - Strategy Intelligence
 * - Portfolio Intelligence
 * - Research Intelligence
 */

import { apiUrl } from '@/api/base';

// ============================================================================
// TYPE DEFINITIONS
// ============================================================================

// Market Intelligence Types
export interface MarketRegime {
  regime: string;
  confidence: number;
  duration: string;
  strength: 'strong' | 'moderate' | 'weak';
}

export interface MarketNarrative {
  narrative: string;
  sentiment: number;
  velocity: 'high' | 'moderate' | 'low';
  sources: number;
}

export interface LiquidityData {
  market: string;
  depth: 'high' | 'moderate' | 'low';
  spread: number;
  volume24h: string;
}

export interface VolatilityData {
  asset: string;
  current: number;
  regime: 'low' | 'moderate' | 'high' | 'very_high';
  trend: 'increasing' | 'decreasing' | 'stable';
}

export interface OrderFlowData {
  sentiment: 'bullish' | 'bearish' | 'neutral';
  aggressiveBuy: number;
  aggressiveSell: number;
  largeTrades: number;
  whaleActivity: 'high' | 'moderate' | 'low';
}

export interface CrossAssetCorrelation {
  pair: string;
  correlation: number;
  trend: 'strengthening' | 'weakening' | 'stable';
}

// Trader Intelligence Types
export interface TraderProfile {
  address: string;
  label: string;
  pnl: string;
  winRate: number;
  trades: number;
  age: string;
  avgPositionSize: string;
  preferredMarkets: string[];
  riskProfile: 'Aggressive' | 'Moderate' | 'Conservative';
}

export interface TraderCluster {
  name: string;
  size: number;
  avgPnl: string;
  characteristics: string[];
}

export interface TraderRelationship {
  type: 'copy_trading' | 'front_running' | 'coordinated';
  strength: number;
  traders: number;
}

export interface TraderSimilarity {
  targetTrader: string;
  similarTraders: {
    address: string;
    similarity: number;
    sharedPatterns: string[];
  }[];
}

export interface TraderPerformanceOverview {
  totalTraders: number;
  profitable: number;
  averageWinRate: number;
  averageReturn: string;
  topPerformer: {
    address: string;
    return: string;
    period: string;
  };
}

// Strategy Intelligence Types
export interface StrategyCreation {
  activeProposals: number;
  inDevelopment: number;
  readyForReview: number;
  avgCreationTime: string;
  successRate: number;
}

export interface StrategyEvolution {
  strategy: string;
  generation: number;
  improvement: string;
  status: 'evolving' | 'stable' | 'testing';
}

export interface StrategyOptimization {
  currentlyOptimizing: number;
  avgOptimizationTime: string;
  improvementRange: string;
  bestPerforming: string;
}

export interface StrategyBacktest {
  totalBacktests: number;
  avgBacktestTime: string;
  successRate: number;
  lastResults: {
    strategy: string;
    period: string;
    return: string;
    sharpe: number;
    maxDrawdown: string;
  };
}

export interface StrategyDeployment {
  liveStrategies: number;
  canaryStrategies: number;
  proposedStrategies: number;
  avgDeploymentTime: string;
  lastDeployment: {
    strategy: string;
    status: string;
    deployedAt: string;
    performance: string;
  };
}

// Portfolio Intelligence Types
export interface PortfolioAnalysis {
  totalValue: number;
  dailyPnL: number;
  dailyPnLPercent: number;
  weeklyPnL: number;
  monthlyPnL: number;
  ytdPnL: number;
}

export interface PortfolioAllocation {
  asset: string;
  percentage: number;
  value: number;
  target: number;
}

export interface PortfolioRisk {
  overallRisk: 'Low' | 'Medium' | 'High';
  riskScore: number;
  maxDrawdown: string;
  currentDrawdown: string;
  var95: string;
  beta: number;
  sharpe: number;
}

export interface PortfolioPerformance {
  totalReturn: number;
  annualizedReturn: number;
  volatility: number;
  winRate: number;
  avgWin: number;
  avgLoss: number;
  profitFactor: number;
}

export interface PortfolioAttribution {
  source: string;
  contribution: number;
  pnl: number;
}

// Research Intelligence Types
export interface ResearchQueue {
  highPriority: number;
  mediumPriority: number;
  lowPriority: number;
  inProgress: number;
  completed: number;
  avgCompletionTime: string;
}

export interface KnowledgeGraph {
  nodes: number;
  edges: number;
  clusters: number;
  lastUpdate: string;
  growthRate: string;
}

export interface ModelLearning {
  activeModels: number;
  trainingJobs: number;
  modelAccuracy: number;
  trainingProgress: number;
  lastTraining: string;
  nextScheduled: string;
}

export interface ResearchPublication {
  published: number;
  inReview: number;
  drafts: number;
  totalCitations: number;
  avgImpactScore: number;
  lastPublication: string;
}

export interface ResearchCollaboration {
  activeCollaborators: number;
  sharedProjects: number;
  contributions: number;
  pendingRequests: number;
  activeDiscussions: number;
  lastCollaboration: string;
}

// ============================================================================
// API CLIENT
// ============================================================================

class IndiraIntelligenceAPI {
  private baseURL: string;

  constructor(baseURL: string = '/api/indira') {
    this.baseURL = baseURL;
  }

  private async fetchAPI<T>(
    endpoint: string,
    options: RequestInit = {}
  ): Promise<T> {
    const url = apiUrl(`${this.baseURL}${endpoint}`);
    const headers = new Headers();
    headers.set('Content-Type', 'application/json');

    const response = await fetch(url, {
      ...options,
      headers,
    });

    if (!response.ok) {
      throw new Error(`INDIRA API error: ${response.status} ${response.statusText}`);
    }

    return response.json() as Promise<T>;
  }

  // ============================================================================
  // MARKET INTELLIGENCE ENDPOINTS
  // ============================================================================

  async getMarketRegimes(): Promise<MarketRegime[]> {
    return this.fetchAPI<MarketRegime[]>('/market/regimes');
  }

  async getMarketNarratives(): Promise<MarketNarrative[]> {
    return this.fetchAPI<MarketNarrative[]>('/market/narratives');
  }

  async getLiquidityData(): Promise<LiquidityData[]> {
    return this.fetchAPI<LiquidityData[]>('/market/liquidity');
  }

  async getVolatilityData(): Promise<VolatilityData[]> {
    return this.fetchAPI<VolatilityData[]>('/market/volatility');
  }

  async getOrderFlowData(): Promise<OrderFlowData> {
    return this.fetchAPI<OrderFlowData>('/market/orderflow');
  }

  async getCrossAssetData(): Promise<CrossAssetCorrelation[]> {
    return this.fetchAPI<CrossAssetCorrelation[]>('/market/crossasset');
  }

  // ============================================================================
  // TRADER INTELLIGENCE ENDPOINTS
  // ============================================================================

  async getTopTraders(limit: number = 10): Promise<TraderProfile[]> {
    return this.fetchAPI<TraderProfile[]>(`/traders/top?limit=${limit}`);
  }

  async getTraderProfile(address: string): Promise<TraderProfile> {
    return this.fetchAPI<TraderProfile>(`/traders/profile/${address}`);
  }

  async getTraderClusters(): Promise<TraderCluster[]> {
    return this.fetchAPI<TraderCluster[]>('/traders/clusters');
  }

  async getTraderRelationships(): Promise<TraderRelationship[]> {
    return this.fetchAPI<TraderRelationship[]>('/traders/relationships');
  }

  async getTraderSimilarity(address: string): Promise<TraderSimilarity> {
    return this.fetchAPI<TraderSimilarity>(`/traders/similarity/${address}`);
  }

  async getTraderPerformanceOverview(): Promise<TraderPerformanceOverview> {
    return this.fetchAPI<TraderPerformanceOverview>('/traders/performance/overview');
  }

  async searchTraders(query: string): Promise<TraderProfile[]> {
    return this.fetchAPI<TraderProfile[]>(`/traders/search?q=${encodeURIComponent(query)}`);
  }

  // ============================================================================
  // STRATEGY INTELLIGENCE ENDPOINTS
  // ============================================================================

  async getStrategyCreation(): Promise<StrategyCreation> {
    return this.fetchAPI<StrategyCreation>('/strategy/creation');
  }

  async getStrategyEvolution(): Promise<StrategyEvolution[]> {
    return this.fetchAPI<StrategyEvolution[]>('/strategy/evolution');
  }

  async getStrategyOptimization(): Promise<StrategyOptimization> {
    return this.fetchAPI<StrategyOptimization>('/strategy/optimization');
  }

  async getStrategyBacktesting(): Promise<StrategyBacktest> {
    return this.fetchAPI<StrategyBacktest>('/strategy/backtesting');
  }

  async getStrategyDeployment(): Promise<StrategyDeployment> {
    return this.fetchAPI<StrategyDeployment>('/strategy/deployment');
  }

  // ============================================================================
  // PORTFOLIO INTELLIGENCE ENDPOINTS
  // ============================================================================

  async getPortfolioAnalysis(): Promise<PortfolioAnalysis> {
    return this.fetchAPI<PortfolioAnalysis>('/portfolio/analysis');
  }

  async getPortfolioAllocation(): Promise<PortfolioAllocation[]> {
    return this.fetchAPI<PortfolioAllocation[]>('/portfolio/allocation');
  }

  async getPortfolioRisk(): Promise<PortfolioRisk> {
    return this.fetchAPI<PortfolioRisk>('/portfolio/risk');
  }

  async getPortfolioPerformance(): Promise<PortfolioPerformance> {
    return this.fetchAPI<PortfolioPerformance>('/portfolio/performance');
  }

  async getPortfolioAttribution(): Promise<PortfolioAttribution[]> {
    return this.fetchAPI<PortfolioAttribution[]>('/portfolio/attribution');
  }

  // ============================================================================
  // RESEARCH INTELLIGENCE ENDPOINTS
  // ============================================================================

  async getResearchQueue(): Promise<ResearchQueue> {
    return this.fetchAPI<ResearchQueue>('/research/queue');
  }

  async getKnowledgeGraph(): Promise<KnowledgeGraph> {
    return this.fetchAPI<KnowledgeGraph>('/research/knowledge-graph');
  }

  async getModelLearning(): Promise<ModelLearning> {
    return this.fetchAPI<ModelLearning>('/research/learning');
  }

  async getResearchPublication(): Promise<ResearchPublication> {
    return this.fetchAPI<ResearchPublication>('/research/publications');
  }

  async getResearchCollaboration(): Promise<ResearchCollaboration> {
    return this.fetchAPI<ResearchCollaboration>('/research/collaboration');
  }

  // ============================================================================
  // WEBSOCKET CONNECTIONS
  // ============================================================================

  connectToMarketUpdates(callback: (data: any) => void): WebSocket {
    const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
    const host = window.location.host;
    const ws = new WebSocket(`${protocol}//${host}${this.baseURL}/ws/market`);

    ws.onopen = () => {
      console.log('[INDIRA API] Market updates WebSocket connected');
    };

    ws.onmessage = (event) => {
      try {
        const data = JSON.parse(event.data);
        callback(data);
      } catch (error) {
        console.error('[INDIRA API] WebSocket parse error:', error);
      }
    };

    ws.onerror = (error) => {
      console.error('[INDIRA API] WebSocket error:', error);
    };

    ws.onclose = () => {
      console.log('[INDIRA API] WebSocket disconnected');
    };

    return ws;
  }

  connectToTraderUpdates(callback: (data: any) => void): WebSocket {
    const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
    const host = window.location.host;
    const ws = new WebSocket(`${protocol}//${host}${this.baseURL}/ws/traders`);

    ws.onopen = () => {
      console.log('[INDIRA API] Trader updates WebSocket connected');
    };

    ws.onmessage = (event) => {
      try {
        const data = JSON.parse(event.data);
        callback(data);
      } catch (error) {
        console.error('[INDIRA API] WebSocket parse error:', error);
      }
    };

    ws.onerror = (error) => {
      console.error('[INDIRA API] WebSocket error:', error);
    };

    ws.onclose = () => {
      console.log('[INDIRA API] WebSocket disconnected');
    };

    return ws;
  }
}

// Singleton instance
let indiraIntelligenceAPIInstance: IndiraIntelligenceAPI | null = null;

export function getIndiraIntelligenceAPI(): IndiraIntelligenceAPI {
  if (!indiraIntelligenceAPIInstance) {
    indiraIntelligenceAPIInstance = new IndiraIntelligenceAPI();
  }
  return indiraIntelligenceAPIInstance;
}
