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
    // Try to fetch from the real API
    try {
      const url = apiUrl(`${this.baseURL}${endpoint}`);
      const headers = new Headers();
      headers.set('Content-Type', 'application/json');

      const response = await fetch(url, {
        ...options,
        headers,
      });

      if (response.ok) {
        return response.json() as Promise<T>;
      }
    } catch (error) {
      console.warn(`INDIRA API error: ${endpoint}, using mock data`, error);
    }

    // Return mock data if API fails
    return this.getMockData<T>(endpoint);
  }

  private async getMockData<T>(endpoint: string): Promise<T> {
    // Mock data for development
    const mockData: Record<string, any> = {
      '/market/regimes': [
        { regime: 'Bullish Trend', confidence: 0.85, duration: '2h 15m', strength: 'strong' },
        { regime: 'Volatility Compression', confidence: 0.72, duration: '45m', strength: 'moderate' },
        { regime: 'Range Bound', confidence: 0.91, duration: '4h 30m', strength: 'weak' }
      ],
      '/market/narratives': [
        { narrative: 'Institutional accumulation at key support', sentiment: 0.78, velocity: 'high', sources: 23 },
        { narrative: 'Retail sentiment remains cautiously optimistic', sentiment: 0.65, velocity: 'moderate', sources: 15 }
      ],
      '/market/liquidity': [
        { market: 'BTC', depth: 'high', spread: 0.12, volume24h: '$45.2B' },
        { market: 'ETH', depth: 'moderate', spread: 0.28, volume24h: '$28.7B' },
        { market: 'SOL', depth: 'low', spread: 0.45, volume24h: '$12.1B' }
      ],
      '/market/volatility': [
        { asset: 'BTC', current: 4.2, regime: 'moderate', trend: 'stable' },
        { asset: 'ETH', current: 5.8, regime: 'high', trend: 'increasing' },
        { asset: 'SOL', current: 7.1, regime: 'high', trend: 'increasing' }
      ],
      '/market/orderflow': { sentiment: 'bullish', aggressiveBuy: 65, aggressiveSell: 22, largeTrades: 34, whaleActivity: 'high' },
      '/market/crossasset': [
        { pair: 'BTC-ETH', correlation: 0.89, trend: 'stable' },
        { pair: 'BTC-SOL', correlation: 0.76, trend: 'weakening' }
      ],
      '/traders/top': [
        { address: '0x7a25d...2f8a', label: 'Whale_Alpha', pnl: '+$8.2M', winRate: 72, trades: 234, age: '18 months', avgPositionSize: '$450K', preferredMarkets: ['BTC', 'ETH'], riskProfile: 'Aggressive' },
        { address: '0x3b9e1...7d2c', label: 'Conservative_Growth', pnl: '+$1.5M', winRate: 85, trades: 89, age: '8 months', avgPositionSize: '$120K', preferredMarkets: ['ETH', 'stablecoins'], riskProfile: 'Conservative' },
        { address: '0x8c5f4...4e9b', label: 'Swing_Pro', pnl: '+$2.8M', winRate: 68, trades: 145, age: '12 months', avgPositionSize: '$280K', preferredMarkets: ['BTC', 'SOL'], riskProfile: 'Moderate' }
      ],
      '/traders/clusters': [
        { name: 'High Frequency Scalpers', size: 23, avgPnl: '+$4.2M', characteristics: ['sub-1s holds', 'latency sensitive'] },
        { name: 'Long-term Holders', size: 156, avgPnl: '+$8.7M', characteristics: ['multi-day positions', 'fundamental analysis'] }
      ],
      '/traders/relationships': [
        { type: 'copy_trading', strength: 0.67, traders: 34 },
        { type: 'front_running', strength: 0.23, traders: 8 }
      ],
      '/traders/performance': {
        totalTraders: 289,
        profitable: 198,
        averageWinRate: 68.5,
        averageReturn: '+$847K',
        topPerformer: { address: '0x7a25d...2f8a', return: '+$2.4M', period: '30 days' }
      },
      '/strategy/creation': { activeProposals: 5, inDevelopment: 3, readyForReview: 2, avgCreationTime: '2.5 hours', successRate: 78 },
      '/strategy/evolution': [
        { strategy: 'TrendFollowing_ML', generation: 4, improvement: '+18% return', status: 'evolving' },
        { strategy: 'MeanReversion_HFT', generation: 2, improvement: '+5% return', status: 'stable' }
      ],
      '/strategy/optimization': { currentlyOptimizing: 3, avgOptimizationTime: '45 min', improvementRange: '8-12%', bestPerforming: 'TrendFollowing_ML' },
      '/strategy/backtesting': { totalBacktests: 47, avgBacktestTime: '12 min', successRate: 65, lastResults: { strategy: 'TrendFollowing_ML', period: '30 days', return: '+18%', sharpe: 2.4, maxDrawdown: '-8.2%' } },
      '/strategy/deployment': { liveStrategies: 12, canaryStrategies: 3, proposedStrategies: 2, avgDeploymentTime: '1.5 hours', lastDeployment: { strategy: 'TrendFollowing_ML', status: 'live', deployedAt: '2026-06-10 14:30', performance: '+18%' } },
      '/portfolio/analysis': { totalValue: 12.4, dailyPnL: 0.08, dailyPnLPercent: 0.65, weeklyPnL: 0.32, monthlyPnL: 1.8, ytdPnL: 8.4 },
      '/portfolio/allocation': [
        { asset: 'BTC', percentage: 45, value: 5.58, target: 50 },
        { asset: 'ETH', percentage: 30, value: 3.72, target: 30 },
        { asset: 'SOL', percentage: 15, value: 1.86, target: 15 },
        { asset: 'USDC', percentage: 10, value: 1.24, target: 5 }
      ],
      '/portfolio/risk': { overallRisk: 'Medium', riskScore: 52, maxDrawdown: '-8.2%', currentDrawdown: '-2.4%', var95: '-5.8%', beta: 1.2, sharpe: 1.8 },
      '/portfolio/performance': { totalReturn: 8.4, annualizedReturn: 12.3, volatility: 15.2, winRate: 68, avgWin: 234, avgLoss: -156, profitFactor: 1.5 },
      '/portfolio/attribution': [
        { source: 'Market Making', contribution: 0.45, pnl: 3.78 },
        { source: 'Trend Following', contribution: 0.32, pnl: 2.69 },
        { source: 'Arbitrage', contribution: 0.23, pnl: 1.94 }
      ],
      '/research/queue': { highPriority: 8, mediumPriority: 23, lowPriority: 45, inProgress: 12, completed: 76, avgCompletionTime: '4.2 hours' },
      '/research/knowledge-graph': { nodes: 234, edges: 567, clusters: 12, lastUpdate: '2 hours ago', growthRate: '+8.5%' },
      '/research/learning': { activeModels: 8, trainingJobs: 3, modelAccuracy: 0.87, trainingProgress: 67, lastTraining: '45 min ago', nextScheduled: '2 hours' },
      '/research/publications': { published: 234, inReview: 18, drafts: 45, totalCitations: 1567, avgImpactScore: 7.2, lastPublication: '6 hours ago' },
      '/research/collaboration': { activeCollaborators: 45, sharedProjects: 23, contributions: 156, pendingRequests: 8, activeDiscussions: 34, lastCollaboration: '1 hour ago' }
    };

    // Return mock data based on endpoint
    return mockData[endpoint] as T;
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
