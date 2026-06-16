/**
 * INDIRA Cognitive Center Page
 * 
 * Core intelligence workspace for INDIRA with 5 specialized intelligence tabs:
 * - Market Intelligence: Market regimes, narratives, liquidity, volatility, order flow, cross-asset analysis
 * - Trader Intelligence: Trader discovery, profiles, clustering, relationships, similarity, performance
 * - Strategy Intelligence: Strategy creation, evolution, optimization, backtesting, deployment
 * - Portfolio Intelligence: Portfolio analysis, allocation, risk, performance, attribution
 * - Research Intelligence: Research queue, knowledge graph, learning, publication, collaboration
 * 
 * This is the primary interface for INDIRA's market intelligence, trader profiling,
 * and strategy research capabilities.
 */

import { useState, useEffect } from 'react';
import {
  useMarketRegimes,
  useMarketNarratives,
  useLiquidityData,
  useVolatilityData,
  useOrderFlowData,
  useCrossAssetData,
  useTopTraders,
  useTraderProfile,
  useTraderClusters,
  useTraderRelationships,
  useTraderSimilarity,
  useTraderPerformanceOverview,
  useStrategyCreation,
  useStrategyEvolution,
  useStrategyOptimization,
  useStrategyBacktesting,
  useStrategyDeployment,
  usePortfolioAnalysis,
  usePortfolioAllocation,
  usePortfolioRisk,
  usePortfolioPerformance,
  usePortfolioAttribution,
  useResearchQueue,
  useKnowledgeGraph,
  useModelLearning,
  useResearchPublication,
  useResearchCollaboration,
} from '@/hooks/useIndiraIntelligence';
import { getAIOrchestrator, getPerformanceMonitor } from '@/core/ai';
import { AIAssistantPanel } from '@/components/ai/AIAssistantPanel';
import { 
  Brain, 
  TrendingUp, 
  Users, 
  Briefcase, 
  Search,
  BarChart3,
  Activity,
  Target,
  PieChart,
  FlaskConical,
  BookOpen,
  Network,
  Sparkles,
  Clock,
  AlertTriangle,
  CheckCircle
} from 'lucide-react';

// ============================================================================
// TAB CONFIGURATION
// ============================================================================

type IntelligenceTab = 'market' | 'trader' | 'strategy' | 'portfolio' | 'research' | 'ai-assistant';

interface TabConfig {
  id: IntelligenceTab;
  label: string;
  icon: any;
  description: string;
}

const INTELLIGENCE_TABS: TabConfig[] = [
  {
    id: 'market',
    label: 'Market Intelligence',
    icon: TrendingUp,
    description: 'Market regimes, narratives, liquidity, volatility, order flow, cross-asset analysis'
  },
  {
    id: 'trader',
    label: 'Trader Intelligence',
    icon: Users,
    description: 'Trader discovery, profiles, clustering, relationships, similarity, performance'
  },
  {
    id: 'strategy',
    label: 'Strategy Intelligence',
    icon: Target,
    description: 'Strategy creation, evolution, optimization, backtesting, deployment'
  },
  {
    id: 'portfolio',
    label: 'Portfolio Intelligence',
    icon: Briefcase,
    description: 'Portfolio analysis, allocation, risk, performance, attribution'
  },
  {
    id: 'research',
    label: 'Research Intelligence',
    icon: BookOpen,
    description: 'Research queue, knowledge graph, learning, publication, collaboration'
  },
  {
    id: 'ai-assistant',
    label: 'AI Assistant',
    icon: Sparkles,
    description: 'Unified AI assistance with recommendations, predictions, and cross-system intelligence'
  },
];

// ============================================================================
// MAIN COMPONENT
// ============================================================================

export function IndiraCognitiveCenterPage() {
  const [activeTab, setActiveTab] = useState<IntelligenceTab>('market');
  const isMockMode = true; // Will be replaced with real connection state

  return (
    <div className="indira-cognitive-center-page flex flex-col h-full">
      {/* Header */}
      <div className="indira-cognitive-center-header flex items-center justify-between border-b border-border bg-surface px-6 py-4">
        <div className="flex items-center gap-4">
          <Brain className="w-8 h-8 text-blue-500" />
          <div>
            <h1 className="text-2xl font-semibold tracking-tight">INDIRA Cognitive Center</h1>
            <p className="text-sm text-slate-400 mt-1">
              Advanced intelligence workspace for market analysis, trader profiling, and strategy research
            </p>
          </div>
        </div>

        <div className="flex items-center gap-4">
          {/* Mock Mode Indicator */}
          {isMockMode && (
            <div className="flex items-center gap-2 px-3 py-1.5 bg-purple-500/10 border border-purple-500/20 rounded">
              <FlaskConical className="w-4 h-4 text-purple-500" />
              <span className="text-xs font-medium text-purple-500">DEMO MODE</span>
            </div>
          )}

          {/* Status Indicator */}
          <div className="flex items-center gap-2 px-3 py-1.5 bg-green-500/10 border border-green-500/20 rounded">
            <CheckCircle className="w-4 h-4 text-green-500" />
            <span className="text-xs font-medium text-green-500">INDIRA ONLINE</span>
          </div>
        </div>
      </div>

      {/* Tab Navigation */}
      <div className="indira-cognitive-center-tabs flex items-center gap-1 px-6 py-3 bg-surface border-b border-border">
        {INTELLIGENCE_TABS.map((tab) => {
          const Icon = tab.icon;
          const isActive = activeTab === tab.id;
          
          return (
            <button
              key={tab.id}
              onClick={() => setActiveTab(tab.id)}
              className={`flex items-center gap-2 px-4 py-2 rounded-lg transition-colors ${
                isActive 
                  ? 'bg-accent/10 text-accent border border-accent/20' 
                  : 'text-slate-400 hover:text-slate-300 hover:bg-surface-raised'
              }`}
            >
              <Icon className="w-4 h-4" />
              <span className="text-sm font-medium">{tab.label}</span>
            </button>
          );
        })}
      </div>

      {/* Tab Content */}
      <div className="indira-cognitive-center-content flex-1 overflow-auto p-6">
        {activeTab === 'market' && <MarketIntelligenceTab />}
        {activeTab === 'trader' && <TraderIntelligenceTab />}
        {activeTab === 'strategy' && <StrategyIntelligenceTab />}
        {activeTab === 'portfolio' && <PortfolioIntelligenceTab />}
        {activeTab === 'research' && <ResearchIntelligenceTab />}
        {activeTab === 'ai-assistant' && <AIAssistantIntegrationsTab />}
      </div>
    </div>
  );
}

// ============================================================================
// MARKET INTELLIGENCE TAB
// ============================================================================

function MarketIntelligenceTab() {
  // Fetch all market intelligence data
  const { data: regimes, isLoading: regimesLoading, error: regimesError } = useMarketRegimes();
  const { data: narratives, isLoading: narrativesLoading, error: narrativesError } = useMarketNarratives();
  const { data: liquidity, isLoading: liquidityLoading, error: liquidityError } = useLiquidityData();
  const { data: volatility, isLoading: volatilityLoading, error: volatilityError } = useVolatilityData();
  const { data: orderFlow, isLoading: orderFlowLoading, error: orderFlowError } = useOrderFlowData();
  const { data: crossAsset, isLoading: crossAssetLoading, error: crossAssetError } = useCrossAssetData();

  const hasData = regimes || narratives || liquidity || volatility || orderFlow || crossAsset;
  const isLoading = regimesLoading || narrativesLoading || liquidityLoading || volatilityLoading || orderFlowLoading || crossAssetLoading;
  const hasError = regimesError || narrativesError || liquidityError || volatilityError || orderFlowError || crossAssetError;

  return (
    <div className="market-intelligence-tab space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-lg font-semibold">Market Intelligence</h2>
          <p className="text-sm text-slate-400 mt-1">
            Real-time market analysis across regimes, narratives, liquidity, and order flow
          </p>
        </div>
        <div className="flex items-center gap-2 text-xs text-slate-500">
          <Clock className="w-4 h-4" />
          Last updated: {new Date().toLocaleTimeString()}
          {isLoading && <span className="text-blue-500">• Updating...</span>}
        </div>
      </div>

      {/* Error State */}
      {hasError && (
        <div className="p-4 bg-red-500/10 border border-red-500/20 rounded">
          <p className="text-sm text-red-500">Failed to load market intelligence data. Check API connection.</p>
        </div>
      )}

      {/* Loading State */}
      {isLoading && !hasData && (
        <div className="p-4 bg-surface-raised border border-border rounded">
          <p className="text-sm text-slate-400">Loading market intelligence data...</p>
        </div>
      )}

      {/* 6-Panel Grid Layout */}
      <div className="grid grid-cols-3 gap-4">
        <MarketRegimesPanel data={regimes} isLoading={regimesLoading} />
        <NarrativesPanel data={narratives} isLoading={narrativesLoading} />
        <LiquidityPanel data={liquidity} isLoading={liquidityLoading} />
        <VolatilityPanel data={volatility} isLoading={volatilityLoading} />
        <OrderFlowPanel data={orderFlow} isLoading={orderFlowLoading} />
        <CrossAssetPanel data={crossAsset} isLoading={crossAssetLoading} />
      </div>
    </div>
  );
}

function MarketRegimesPanel({ data, isLoading }: { data?: any[], isLoading?: boolean }) {
  if (isLoading) {
    return (
      <div className="panel rounded-lg border border-border bg-surface p-4">
        <div className="flex items-center gap-2 mb-4">
          <Activity className="w-4 h-4 text-blue-500" />
          <h3 className="text-sm font-semibold">Market Regimes</h3>
        </div>
        <div className="p-3 bg-surface-raised rounded border border-border">
          <p className="text-xs text-slate-400">Loading regimes...</p>
        </div>
      </div>
    );
  }

  if (!data || data.length === 0) {
    return (
      <div className="panel rounded-lg border border-border bg-surface p-4">
        <div className="flex items-center gap-2 mb-4">
          <Activity className="w-4 h-4 text-blue-500" />
          <h3 className="text-sm font-semibold">Market Regimes</h3>
        </div>
        <div className="p-3 bg-surface-raised rounded border border-border">
          <p className="text-xs text-slate-400">No regime data available</p>
        </div>
      </div>
    );
  }

  return (
    <div className="panel rounded-lg border border-border bg-surface p-4">
      <div className="flex items-center gap-2 mb-4">
        <Activity className="w-4 h-4 text-blue-500" />
        <h3 className="text-sm font-semibold">Market Regimes</h3>
      </div>
      <div className="space-y-3">
        {data.map((regime: any, idx: number) => (
          <div key={idx} className="p-3 bg-surface-raised rounded border border-border">
            <div className="flex items-center justify-between mb-2">
              <span className="text-xs font-medium">{regime.regime}</span>
              <span className={`text-xs px-2 py-0.5 rounded ${
                regime.strength === 'strong' ? 'bg-green-500/20 text-green-500' : 'bg-yellow-500/20 text-yellow-500'
              }`}>
                {regime.strength}
              </span>
            </div>
            <div className="flex items-center justify-between text-xs text-slate-400">
              <span>Confidence: {(regime.confidence * 100).toFixed(0)}%</span>
              <span>Duration: {regime.duration}</span>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}

function NarrativesPanel({ data, isLoading }: { data?: any[], isLoading?: boolean }) {
  if (isLoading) {
    return (
      <div className="panel rounded-lg border border-border bg-surface p-4">
        <div className="flex items-center gap-2 mb-4">
          <Sparkles className="w-4 h-4 text-purple-500" />
          <h3 className="text-sm font-semibold">Market Narratives</h3>
        </div>
        <div className="p-3 bg-surface-raised rounded border border-border">
          <p className="text-xs text-slate-400">Loading narratives...</p>
        </div>
      </div>
    );
  }

  if (!data || data.length === 0) {
    return (
      <div className="panel rounded-lg border border-border bg-surface p-4">
        <div className="flex items-center gap-2 mb-4">
          <Sparkles className="w-4 h-4 text-purple-500" />
          <h3 className="text-sm font-semibold">Market Narratives</h3>
        </div>
        <div className="p-3 bg-surface-raised rounded border border-border">
          <p className="text-xs text-slate-400">No narrative data available</p>
        </div>
      </div>
    );
  }

  return (
    <div className="panel rounded-lg border border-border bg-surface p-4">
      <div className="flex items-center gap-2 mb-4">
        <Sparkles className="w-4 h-4 text-purple-500" />
        <h3 className="text-sm font-semibold">Market Narratives</h3>
      </div>
      <div className="space-y-3">
        {data.map((narrative: any, idx: number) => (
          <div key={idx} className="p-3 bg-surface-raised rounded border border-border">
            <div className="flex items-center justify-between mb-2">
              <span className="text-xs font-medium">{narrative.narrative}</span>
              <span className={`text-xs ${narrative.sentiment > 0.7 ? 'text-green-500' : 'text-yellow-500'}`}>
                {(narrative.sentiment * 100).toFixed(0)}%
              </span>
            </div>
            <div className="flex items-center justify-between text-xs text-slate-400">
              <span>Velocity: {narrative.velocity}</span>
              <span>Sources: {narrative.sources}</span>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}

function LiquidityPanel({ data, isLoading }: { data?: any[], isLoading?: boolean }) {
  if (isLoading) {
    return (
      <div className="panel rounded-lg border border-border bg-surface p-4">
        <div className="flex items-center gap-2 mb-4">
          <BarChart3 className="w-4 h-4 text-green-500" />
          <h3 className="text-sm font-semibold">Liquidity Analysis</h3>
        </div>
        <div className="p-3 bg-surface-raised rounded border border-border">
          <p className="text-xs text-slate-400">Loading liquidity...</p>
        </div>
      </div>
    );
  }

  if (!data || data.length === 0) {
    return (
      <div className="panel rounded-lg border border-border bg-surface p-4">
        <div className="flex items-center gap-2 mb-4">
          <BarChart3 className="w-4 h-4 text-green-500" />
          <h3 className="text-sm font-semibold">Liquidity Analysis</h3>
        </div>
        <div className="p-3 bg-surface-raised rounded border border-border">
          <p className="text-xs text-slate-400">No liquidity data available</p>
        </div>
      </div>
    );
  }

  return (
    <div className="panel rounded-lg border border-border bg-surface p-4">
      <div className="flex items-center gap-2 mb-4">
        <BarChart3 className="w-4 h-4 text-green-500" />
        <h3 className="text-sm font-semibold">Liquidity Analysis</h3>
      </div>
      <div className="space-y-3">
        {data.map((liquidity: any, idx: number) => (
          <div key={idx} className="p-3 bg-surface-raised rounded border border-border">
            <div className="flex items-center justify-between mb-2">
              <span className="text-xs font-medium">{liquidity.market}</span>
              <span className={`text-xs px-2 py-0.5 rounded ${
                liquidity.depth === 'high' ? 'bg-green-500/20 text-green-500' : 'bg-yellow-500/20 text-yellow-500'
              }`}>
                {liquidity.depth}
              </span>
            </div>
            <div className="flex items-center justify-between text-xs text-slate-400">
              <span>Spread: {liquidity.spread}%</span>
              <span>24h Vol: ${liquidity.volume24h}</span>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}

function VolatilityPanel({ data, isLoading }: { data?: any[], isLoading?: boolean }) {
  if (isLoading) {
    return (
      <div className="panel rounded-lg border border-border bg-surface p-4">
        <div className="flex items-center gap-2 mb-4">
          <AlertTriangle className="w-4 h-4 text-orange-500" />
          <h3 className="text-sm font-semibold">Volatility Monitor</h3>
        </div>
        <div className="p-3 bg-surface-raised rounded border border-border">
          <p className="text-xs text-slate-400">Loading volatility...</p>
        </div>
      </div>
    );
  }

  if (!data || data.length === 0) {
    return (
      <div className="panel rounded-lg border border-border bg-surface p-4">
        <div className="flex items-center gap-2 mb-4">
          <AlertTriangle className="w-4 h-4 text-orange-500" />
          <h3 className="text-sm font-semibold">Volatility Monitor</h3>
        </div>
        <div className="p-3 bg-surface-raised rounded border border-border">
          <p className="text-xs text-slate-400">No volatility data available</p>
        </div>
      </div>
    );
  }

  return (
    <div className="panel rounded-lg border border-border bg-surface p-4">
      <div className="flex items-center gap-2 mb-4">
        <AlertTriangle className="w-4 h-4 text-orange-500" />
        <h3 className="text-sm font-semibold">Volatility Monitor</h3>
      </div>
      <div className="space-y-3">
        {data.map((vol: any, idx: number) => (
          <div key={idx} className="p-3 bg-surface-raised rounded border border-border">
            <div className="flex items-center justify-between mb-2">
              <span className="text-xs font-medium">{vol.asset}</span>
              <span className="text-xs">{(vol.current * 100).toFixed(0)}%</span>
            </div>
            <div className="flex items-center justify-between text-xs text-slate-400">
              <span className="capitalize">{vol.regime.replace('_', ' ')}</span>
              <span className={vol.trend === 'increasing' ? 'text-red-500' : 'text-slate-400'}>
                {vol.trend}
              </span>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}

function OrderFlowPanel({ data, isLoading }: { data?: any, isLoading?: boolean }) {
  if (isLoading) {
    return (
      <div className="panel rounded-lg border border-border bg-surface p-4">
        <div className="flex items-center gap-2 mb-4">
          <Activity className="w-4 h-4 text-blue-500" />
          <h3 className="text-sm font-semibold">Order Flow</h3>
        </div>
        <div className="p-3 bg-surface-raised rounded border border-border">
          <p className="text-xs text-slate-400">Loading order flow...</p>
        </div>
      </div>
    );
  }

  if (!data) {
    return (
      <div className="panel rounded-lg border border-border bg-surface p-4">
        <div className="flex items-center gap-2 mb-4">
          <Activity className="w-4 h-4 text-blue-500" />
          <h3 className="text-sm font-semibold">Order Flow</h3>
        </div>
        <div className="p-3 bg-surface-raised rounded border border-border">
          <p className="text-xs text-slate-400">No order flow data available</p>
        </div>
      </div>
    );
  }

  return (
    <div className="panel rounded-lg border border-border bg-surface p-4">
      <div className="flex items-center gap-2 mb-4">
        <Activity className="w-4 h-4 text-blue-500" />
        <h3 className="text-sm font-semibold">Order Flow</h3>
      </div>
      <div className="space-y-3">
        <div className="p-3 bg-surface-raised rounded border border-border">
          <div className="flex items-center justify-between mb-2">
            <span className="text-xs font-medium">Sentiment</span>
            <span className="text-xs text-green-500 capitalize">{data.sentiment}</span>
          </div>
          <div className="flex items-center gap-2 text-xs text-slate-400">
            <div className="flex-1 bg-slate-700 rounded-full h-2">
              <div 
                className="bg-green-500 h-2 rounded-full" 
                style={{ width: `${data.aggressiveBuy * 100}%` }}
              />
            </div>
            <span>Buy {data.aggressiveBuy * 100}%</span>
          </div>
        </div>
        <div className="p-3 bg-surface-raised rounded border border-border">
          <div className="flex items-center justify-between text-xs text-slate-400">
            <span>Large Trades: {data.largeTrades}</span>
            <span>Whale Activity: {data.whaleActivity}</span>
          </div>
        </div>
      </div>
    </div>
  );
}

function CrossAssetPanel({ data, isLoading }: { data?: any[], isLoading?: boolean }) {
  if (isLoading) {
    return (
      <div className="panel rounded-lg border border-border bg-surface p-4">
        <div className="flex items-center gap-2 mb-4">
          <Network className="w-4 h-4 text-purple-500" />
          <h3 className="text-sm font-semibold">Cross-Asset Analysis</h3>
        </div>
        <div className="p-3 bg-surface-raised rounded border border-border">
          <p className="text-xs text-slate-400">Loading cross-asset data...</p>
        </div>
      </div>
    );
  }

  if (!data || data.length === 0) {
    return (
      <div className="panel rounded-lg border border-border bg-surface p-4">
        <div className="flex items-center gap-2 mb-4">
          <Network className="w-4 h-4 text-purple-500" />
          <h3 className="text-sm font-semibold">Cross-Asset Analysis</h3>
        </div>
        <div className="p-3 bg-surface-raised rounded border border-border">
          <p className="text-xs text-slate-400">No cross-asset data available</p>
        </div>
      </div>
    );
  }

  return (
    <div className="panel rounded-lg border border-border bg-surface p-4">
      <div className="flex items-center gap-2 mb-4">
        <Network className="w-4 h-4 text-purple-500" />
        <h3 className="text-sm font-semibold">Cross-Asset Analysis</h3>
      </div>
      <div className="space-y-3">
        {data.map((corr: any, idx: number) => (
          <div key={idx} className="p-3 bg-surface-raised rounded border border-border">
            <div className="flex items-center justify-between mb-2">
              <span className="text-xs font-medium">{corr.pair}</span>
              <span className="text-xs">{corr.correlation.toFixed(2)}</span>
            </div>
            <div className="flex items-center justify-between text-xs text-slate-400">
              <span>Correlation</span>
              <span className={corr.trend === 'strengthening' ? 'text-green-500' : 'text-slate-400'}>
                {corr.trend}
              </span>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}

// ============================================================================
// TRADER INTELLIGENCE TAB
// ============================================================================

function TraderIntelligenceTab() {
  // Fetch all trader intelligence data
  const { data: topTraders, isLoading: topTradersLoading } = useTopTraders(10);
  const { data: clusters, isLoading: clustersLoading } = useTraderClusters();
  const { data: relationships, isLoading: relationshipsLoading } = useTraderRelationships();
  const { data: performanceOverview, isLoading: performanceLoading } = useTraderPerformanceOverview();
  
  // For similarity and profile, we'll use the first top trader as default
  const defaultTraderAddress = topTraders?.[0]?.address;
  const { data: traderProfile, isLoading: profileLoading } = useTraderProfile(defaultTraderAddress || '');
  const { data: traderSimilarity, isLoading: similarityLoading } = useTraderSimilarity(defaultTraderAddress || '');

  const isLoading = topTradersLoading || clustersLoading || relationshipsLoading || performanceLoading || profileLoading || similarityLoading;
  const hasData = topTraders || clusters || relationships || performanceOverview || traderProfile || traderSimilarity;

  return (
    <div className="trader-intelligence-tab space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-lg font-semibold">Trader Intelligence</h2>
          <p className="text-sm text-slate-400 mt-1">
            Trader discovery, profiling, clustering, and performance analysis
          </p>
        </div>
        <div className="flex items-center gap-2 text-xs text-slate-500">
          <Users className="w-4 h-4" />
          {performanceOverview?.totalTraders || 'Loading...'} traders profiled
        </div>
      </div>

      {/* Loading State */}
      {isLoading && !hasData && (
        <div className="p-4 bg-surface-raised border border-border rounded">
          <p className="text-sm text-slate-400">Loading trader intelligence data...</p>
        </div>
      )}

      {/* 6-Panel Grid Layout */}
      <div className="grid grid-cols-3 gap-4">
        <TraderDiscoveryPanel data={topTraders} isLoading={topTradersLoading} />
        <TraderProfilesPanel data={traderProfile} isLoading={profileLoading} />
        <TraderClusteringPanel data={clusters} isLoading={clustersLoading} />
        <TraderRelationshipsPanel data={relationships} isLoading={relationshipsLoading} />
        <TraderSimilarityPanel data={traderSimilarity} isLoading={similarityLoading} />
        <TraderPerformancePanel data={performanceOverview} isLoading={performanceLoading} />
      </div>
    </div>
  );
}

function TraderDiscoveryPanel({ data, isLoading }: { data?: any[], isLoading?: boolean }) {
  if (isLoading) {
    return (
      <div className="panel rounded-lg border border-border bg-surface p-4">
        <div className="flex items-center gap-2 mb-4">
          <Search className="w-4 h-4 text-blue-500" />
          <h3 className="text-sm font-semibold">Trader Discovery</h3>
        </div>
        <div className="p-3 bg-surface-raised rounded border border-border">
          <p className="text-xs text-slate-400">Loading traders...</p>
        </div>
      </div>
    );
  }

  if (!data || data.length === 0) {
    return (
      <div className="panel rounded-lg border border-border bg-surface p-4">
        <div className="flex items-center gap-2 mb-4">
          <Search className="w-4 h-4 text-blue-500" />
          <h3 className="text-sm font-semibold">Trader Discovery</h3>
        </div>
        <div className="p-3 bg-surface-raised rounded border border-border">
          <p className="text-xs text-slate-400">No trader data available</p>
        </div>
      </div>
    );
  }

  return (
    <div className="panel rounded-lg border border-border bg-surface p-4">
      <div className="flex items-center gap-2 mb-4">
        <Search className="w-4 h-4 text-blue-500" />
        <h3 className="text-sm font-semibold">Trader Discovery</h3>
      </div>
      <div className="space-y-3">
        {data.slice(0, 3).map((trader: any, idx: number) => (
          <div key={idx} className="p-3 bg-surface-raised rounded border border-border">
            <div className="flex items-center justify-between mb-2">
              <span className="text-xs font-medium font-mono">{trader.address}</span>
              <span className="text-xs text-green-500">{trader.pnl}</span>
            </div>
            <div className="flex items-center justify-between text-xs text-slate-400">
              <span>Win Rate: {(trader.winRate * 100).toFixed(0)}%</span>
              <span>Trades: {trader.trades}</span>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}

function TraderProfilesPanel({ data, isLoading }: { data?: any, isLoading?: boolean }) {
  if (isLoading) {
    return (
      <div className="panel rounded-lg border border-border bg-surface p-4">
        <div className="flex items-center gap-2 mb-4">
          <Users className="w-4 h-4 text-purple-500" />
          <h3 className="text-sm font-semibold">Trader Profile</h3>
        </div>
        <div className="p-3 bg-surface-raised rounded border border-border">
          <p className="text-xs text-slate-400">Loading profile...</p>
        </div>
      </div>
    );
  }

  if (!data) {
    return (
      <div className="panel rounded-lg border border-border bg-surface p-4">
        <div className="flex items-center gap-2 mb-4">
          <Users className="w-4 h-4 text-purple-500" />
          <h3 className="text-sm font-semibold">Trader Profile</h3>
        </div>
        <div className="p-3 bg-surface-raised rounded border border-border">
          <p className="text-xs text-slate-400">Select a trader to view profile</p>
        </div>
      </div>
    );
  }

  return (
    <div className="panel rounded-lg border border-border bg-surface p-4">
      <div className="flex items-center gap-2 mb-4">
        <Users className="w-4 h-4 text-purple-500" />
        <h3 className="text-sm font-semibold">Trader Profile</h3>
      </div>
      <div className="p-3 bg-surface-raised rounded border border-border space-y-3">
        <div className="flex items-center justify-between">
          <span className="text-xs text-slate-400">Address</span>
          <span className="text-xs font-medium font-mono">{data.address}</span>
        </div>
        <div className="flex items-center justify-between">
          <span className="text-xs text-slate-400">Label</span>
          <span className="text-xs font-medium">{data.label}</span>
        </div>
        <div className="flex items-center justify-between">
          <span className="text-xs text-slate-400">Age</span>
          <span className="text-xs">{data.age}</span>
        </div>
        <div className="flex items-center justify-between">
          <span className="text-xs text-slate-400">Avg Position</span>
          <span className="text-xs">{data.avgPositionSize}</span>
        </div>
        <div className="flex items-center justify-between">
          <span className="text-xs text-slate-400">Risk Profile</span>
          <span className="text-xs text-orange-500">{data.riskProfile}</span>
        </div>
      </div>
    </div>
  );
}

function TraderClusteringPanel({ data, isLoading }: { data?: any[], isLoading?: boolean }) {
  if (isLoading) {
    return (
      <div className="panel rounded-lg border border-border bg-surface p-4">
        <div className="flex items-center gap-2 mb-4">
          <Network className="w-4 h-4 text-green-500" />
          <h3 className="text-sm font-semibold">Trader Clustering</h3>
        </div>
        <div className="p-3 bg-surface-raised rounded border border-border">
          <p className="text-xs text-slate-400">Loading clusters...</p>
        </div>
      </div>
    );
  }

  if (!data || data.length === 0) {
    return (
      <div className="panel rounded-lg border border-border bg-surface p-4">
        <div className="flex items-center gap-2 mb-4">
          <Network className="w-4 h-4 text-green-500" />
          <h3 className="text-sm font-semibold">Trader Clustering</h3>
        </div>
        <div className="p-3 bg-surface-raised rounded border border-border">
          <p className="text-xs text-slate-400">No cluster data available</p>
        </div>
      </div>
    );
  }

  return (
    <div className="panel rounded-lg border border-border bg-surface p-4">
      <div className="flex items-center gap-2 mb-4">
        <Network className="w-4 h-4 text-green-500" />
        <h3 className="text-sm font-semibold">Trader Clustering</h3>
      </div>
      <div className="space-y-3">
        {data.slice(0, 3).map((cluster: any, idx: number) => (
          <div key={idx} className="p-3 bg-surface-raised rounded border border-border">
            <div className="flex items-center justify-between mb-2">
              <span className="text-xs font-medium">{cluster.name}</span>
              <span className="text-xs text-slate-400">{cluster.size} traders</span>
            </div>
            <div className="flex items-center justify-between mb-1">
              <span className="text-xs text-slate-400">Avg P&L</span>
              <span className="text-xs text-green-500">{cluster.avgPnl}</span>
            </div>
            <div className="flex flex-wrap gap-1 mt-2">
              {cluster.characteristics.slice(0, 2).map((char: string, charIdx: number) => (
                <span key={charIdx} className="text-xs px-2 py-0.5 bg-surface-overlay rounded">
                  {char}
                </span>
              ))}
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}

function TraderRelationshipsPanel({ data, isLoading }: { data?: any[], isLoading?: boolean }) {
  if (isLoading) {
    return (
      <div className="panel rounded-lg border border-border bg-surface p-4">
        <div className="flex items-center gap-2 mb-4">
          <Network className="w-4 h-4 text-blue-500" />
          <h3 className="text-sm font-semibold">Trader Relationships</h3>
        </div>
        <div className="p-3 bg-surface-raised rounded border border-border">
          <p className="text-xs text-slate-400">Loading relationships...</p>
        </div>
      </div>
    );
  }

  if (!data || data.length === 0) {
    return (
      <div className="panel rounded-lg border border-border bg-surface p-4">
        <div className="flex items-center gap-2 mb-4">
          <Network className="w-4 h-4 text-blue-500" />
          <h3 className="text-sm font-semibold">Trader Relationships</h3>
        </div>
        <div className="p-3 bg-surface-raised rounded border border-border">
          <p className="text-xs text-slate-400">No relationship data available</p>
        </div>
      </div>
    );
  }

  return (
    <div className="panel rounded-lg border border-border bg-surface p-4">
      <div className="flex items-center gap-2 mb-4">
        <Network className="w-4 h-4 text-blue-500" />
        <h3 className="text-sm font-semibold">Trader Relationships</h3>
      </div>
      <div className="space-y-3">
        {data.map((rel: any, idx: number) => (
          <div key={idx} className="p-3 bg-surface-raised rounded border border-border">
            <div className="flex items-center justify-between mb-2">
              <span className="text-xs font-medium capitalize">{rel.type.replace('_', ' ')}</span>
              <span className="text-xs">{(rel.strength * 100).toFixed(0)}%</span>
            </div>
            <div className="text-xs text-slate-400">
              {rel.traders} trader pairs detected
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}

function TraderSimilarityPanel({ data, isLoading }: { data?: any, isLoading?: boolean }) {
  if (isLoading) {
    return (
      <div className="panel rounded-lg border border-border bg-surface p-4">
        <div className="flex items-center gap-2 mb-4">
          <Target className="w-4 h-4 text-purple-500" />
          <h3 className="text-sm font-semibold">Similarity Analysis</h3>
        </div>
        <div className="p-3 bg-surface-raised rounded border border-border">
          <p className="text-xs text-slate-400">Loading similarity...</p>
        </div>
      </div>
    );
  }

  if (!data) {
    return (
      <div className="panel rounded-lg border border-border bg-surface p-4">
        <div className="flex items-center gap-2 mb-4">
          <Target className="w-4 h-4 text-purple-500" />
          <h3 className="text-sm font-semibold">Similarity Analysis</h3>
        </div>
        <div className="p-3 bg-surface-raised rounded border border-border">
          <p className="text-xs text-slate-400">Select a trader for similarity analysis</p>
        </div>
      </div>
    );
  }

  return (
    <div className="panel rounded-lg border border-border bg-surface p-4">
      <div className="flex items-center gap-2 mb-4">
        <Target className="w-4 h-4 text-purple-500" />
        <h3 className="text-sm font-semibold">Similarity Analysis</h3>
      </div>
      <div className="space-y-3">
        <div className="p-2 bg-surface-raised rounded border border-border">
          <span className="text-xs text-slate-400">Target:</span>
          <span className="text-xs font-medium font-mono ml-2">{data.targetTrader}</span>
        </div>
        {data.similarTraders.slice(0, 3).map((trader: any, idx: number) => (
          <div key={idx} className="p-3 bg-surface-raised rounded border border-border">
            <div className="flex items-center justify-between mb-2">
              <span className="text-xs font-medium font-mono">{trader.address}</span>
              <span className="text-xs text-green-500">{(trader.similarity * 100).toFixed(0)}%</span>
            </div>
            <div className="flex flex-wrap gap-1">
              {trader.sharedPatterns.slice(0, 2).map((pattern: string, patternIdx: number) => (
                <span key={patternIdx} className="text-xs px-2 py-0.5 bg-surface-overlay rounded">
                  {pattern}
                </span>
              ))}
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}

function TraderPerformancePanel({ data, isLoading }: { data?: any, isLoading?: boolean }) {
  if (isLoading) {
    return (
      <div className="panel rounded-lg border border-border bg-surface p-4">
        <div className="flex items-center gap-2 mb-4">
          <BarChart3 className="w-4 h-4 text-green-500" />
          <h3 className="text-sm font-semibold">Performance Overview</h3>
        </div>
        <div className="p-3 bg-surface-raised rounded border border-border">
          <p className="text-xs text-slate-400">Loading performance...</p>
        </div>
      </div>
    );
  }

  if (!data) {
    return (
      <div className="panel rounded-lg border border-border bg-surface p-4">
        <div className="flex items-center gap-2 mb-4">
          <BarChart3 className="w-4 h-4 text-green-500" />
          <h3 className="text-sm font-semibold">Performance Overview</h3>
        </div>
        <div className="p-3 bg-surface-raised rounded border border-border">
          <p className="text-xs text-slate-400">No performance data available</p>
        </div>
      </div>
    );
  }

  return (
    <div className="panel rounded-lg border border-border bg-surface p-4">
      <div className="flex items-center gap-2 mb-4">
        <BarChart3 className="w-4 h-4 text-green-500" />
        <h3 className="text-sm font-semibold">Performance Overview</h3>
      </div>
      <div className="space-y-3">
        <div className="grid grid-cols-2 gap-3">
          <div className="p-3 bg-surface-raised rounded border border-border text-center">
            <div className="text-lg font-semibold text-green-500">{data.profitable}</div>
            <div className="text-xs text-slate-400">Profitable</div>
          </div>
          <div className="p-3 bg-surface-raised rounded border border-border text-center">
            <div className="text-lg font-semibold">{data.totalTraders}</div>
            <div className="text-xs text-slate-400">Total</div>
          </div>
        </div>
        <div className="p-3 bg-surface-raised rounded border border-border">
          <div className="flex items-center justify-between mb-2">
            <span className="text-xs text-slate-400">Average Win Rate</span>
            <span className="text-xs font-medium">{(data.averageWinRate * 100).toFixed(0)}%</span>
          </div>
          <div className="flex items-center justify-between">
            <span className="text-xs text-slate-400">Average Return</span>
            <span className="text-xs text-green-500">{data.averageReturn}</span>
          </div>
        </div>
        <div className="p-3 bg-green-500/10 rounded border border-green-500/20">
          <div className="text-xs text-slate-400 mb-1">Top Performer ({data.topPerformer.period})</div>
          <div className="text-xs font-medium font-mono">{data.topPerformer.address}</div>
          <div className="text-xs text-green-500">{data.topPerformer.return}</div>
        </div>
      </div>
    </div>
  );
}

// ============================================================================
// STRATEGY INTELLIGENCE TAB
// ============================================================================

function StrategyIntelligenceTab() {
  // Fetch all strategy intelligence data
  const { data: creation, isLoading: creationLoading } = useStrategyCreation();
  const { data: evolution, isLoading: evolutionLoading } = useStrategyEvolution();
  const { data: optimization, isLoading: optimizationLoading } = useStrategyOptimization();
  const { data: backtesting, isLoading: backtestingLoading } = useStrategyBacktesting();
  const { data: deployment, isLoading: deploymentLoading } = useStrategyDeployment();

  const isLoading = creationLoading || evolutionLoading || optimizationLoading || backtestingLoading || deploymentLoading;
  const hasData = creation || evolution || optimization || backtesting || deployment;

  return (
    <div className="strategy-intelligence-tab space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-lg font-semibold">Strategy Intelligence</h2>
          <p className="text-sm text-slate-400 mt-1">
            Strategy creation, evolution, optimization, backtesting, and deployment
          </p>
        </div>
        <div className="flex items-center gap-2 text-xs text-slate-500">
          <Target className="w-4 h-4" />
          {deployment?.liveStrategies || 'Loading...'} active strategies
        </div>
      </div>

      {/* Loading State */}
      {isLoading && !hasData && (
        <div className="p-4 bg-surface-raised border border-border rounded">
          <p className="text-sm text-slate-400">Loading strategy intelligence data...</p>
        </div>
      )}

      {/* 5-Panel Grid Layout */}
      <div className="grid grid-cols-3 gap-4">
        <StrategyCreationPanel data={creation} isLoading={creationLoading} />
        <StrategyEvolutionPanel data={evolution} isLoading={evolutionLoading} />
        <StrategyOptimizationPanel data={optimization} isLoading={optimizationLoading} />
        <StrategyBacktestingPanel data={backtesting} isLoading={backtestingLoading} />
        <StrategyDeploymentPanel data={deployment} isLoading={deploymentLoading} />
      </div>
    </div>
  );
}

function StrategyCreationPanel({ data, isLoading }: { data?: any, isLoading?: boolean }) {
  if (isLoading) {
    return (
      <div className="panel rounded-lg border border-border bg-surface p-4">
        <div className="flex items-center gap-2 mb-4">
          <Sparkles className="w-4 h-4 text-purple-500" />
          <h3 className="text-sm font-semibold">Strategy Creation</h3>
        </div>
        <div className="p-3 bg-surface-raised rounded border border-border">
          <p className="text-xs text-slate-400">Loading creation data...</p>
        </div>
      </div>
    );
  }

  if (!data) {
    return (
      <div className="panel rounded-lg border border-border bg-surface p-4">
        <div className="flex items-center gap-2 mb-4">
          <Sparkles className="w-4 h-4 text-purple-500" />
          <h3 className="text-sm font-semibold">Strategy Creation</h3>
        </div>
        <div className="p-3 bg-surface-raised rounded border border-border">
          <p className="text-xs text-slate-400">No creation data available</p>
        </div>
      </div>
    );
  }

  return (
    <div className="panel rounded-lg border border-border bg-surface p-4">
      <div className="flex items-center gap-2 mb-4">
        <Sparkles className="w-4 h-4 text-purple-500" />
        <h3 className="text-sm font-semibold">Strategy Creation</h3>
      </div>
      <div className="space-y-3">
        <div className="grid grid-cols-2 gap-3">
          <div className="p-3 bg-surface-raised rounded border border-border text-center">
            <div className="text-lg font-semibold text-purple-500">{data.activeProposals}</div>
            <div className="text-xs text-slate-400">Proposals</div>
          </div>
          <div className="p-3 bg-surface-raised rounded border border-border text-center">
            <div className="text-lg font-semibold text-blue-500">{data.inDevelopment}</div>
            <div className="text-xs text-slate-400">In Development</div>
          </div>
        </div>
        <div className="p-3 bg-surface-raised rounded border border-border">
          <div className="flex items-center justify-between mb-1">
            <span className="text-xs text-slate-400">Ready for Review</span>
            <span className="text-xs font-medium text-green-500">{data.readyForReview}</span>
          </div>
          <div className="flex items-center justify-between mb-1">
            <span className="text-xs text-slate-400">Avg Creation Time</span>
            <span className="text-xs">{data.avgCreationTime}</span>
          </div>
          <div className="flex items-center justify-between">
            <span className="text-xs text-slate-400">Success Rate</span>
            <span className="text-xs text-green-500">{(data.successRate * 100).toFixed(0)}%</span>
          </div>
        </div>
      </div>
    </div>
  );
}

function StrategyEvolutionPanel({ data, isLoading }: { data?: any[], isLoading?: boolean }) {
  if (isLoading) {
    return (
      <div className="panel rounded-lg border border-border bg-surface p-4">
        <div className="flex items-center gap-2 mb-4">
          <TrendingUp className="w-4 h-4 text-green-500" />
          <h3 className="text-sm font-semibold">Strategy Evolution</h3>
        </div>
        <div className="p-3 bg-surface-raised rounded border border-border">
          <p className="text-xs text-slate-400">Loading evolution data...</p>
        </div>
      </div>
    );
  }

  if (!data || data.length === 0) {
    return (
      <div className="panel rounded-lg border border-border bg-surface p-4">
        <div className="flex items-center gap-2 mb-4">
          <TrendingUp className="w-4 h-4 text-green-500" />
          <h3 className="text-sm font-semibold">Strategy Evolution</h3>
        </div>
        <div className="p-3 bg-surface-raised rounded border border-border">
          <p className="text-xs text-slate-400">No evolution data available</p>
        </div>
      </div>
    );
  }

  return (
    <div className="panel rounded-lg border border-border bg-surface p-4">
      <div className="flex items-center gap-2 mb-4">
        <TrendingUp className="w-4 h-4 text-green-500" />
        <h3 className="text-sm font-semibold">Strategy Evolution</h3>
      </div>
      <div className="space-y-3">
        {data.slice(0, 3).map((strategy: any, idx: number) => (
          <div key={idx} className="p-3 bg-surface-raised rounded border border-border">
            <div className="flex items-center justify-between mb-2">
              <span className="text-xs font-medium">{strategy.strategy}</span>
              <span className="text-xs text-green-500">{strategy.improvement}</span>
            </div>
            <div className="flex items-center justify-between text-xs text-slate-400">
              <span>Gen {strategy.generation}</span>
              <span className={`capitalize ${strategy.status === 'evolving' ? 'text-purple-500' : 'text-slate-400'}`}>
                {strategy.status}
              </span>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}

function StrategyOptimizationPanel({ data, isLoading }: { data?: any, isLoading?: boolean }) {
  if (isLoading) {
    return (
      <div className="panel rounded-lg border border-border bg-surface p-4">
        <div className="flex items-center gap-2 mb-4">
          <Target className="w-4 h-4 text-blue-500" />
          <h3 className="text-sm font-semibold">Strategy Optimization</h3>
        </div>
        <div className="p-3 bg-surface-raised rounded border border-border">
          <p className="text-xs text-slate-400">Loading optimization data...</p>
        </div>
      </div>
    );
  }

  if (!data) {
    return (
      <div className="panel rounded-lg border border-border bg-surface p-4">
        <div className="flex items-center gap-2 mb-4">
          <Target className="w-4 h-4 text-blue-500" />
          <h3 className="text-sm font-semibold">Strategy Optimization</h3>
        </div>
        <div className="p-3 bg-surface-raised rounded border border-border">
          <p className="text-xs text-slate-400">No optimization data available</p>
        </div>
      </div>
    );
  }

  return (
    <div className="panel rounded-lg border border-border bg-surface p-4">
      <div className="flex items-center gap-2 mb-4">
        <Target className="w-4 h-4 text-blue-500" />
        <h3 className="text-sm font-semibold">Strategy Optimization</h3>
      </div>
      <div className="space-y-3">
        <div className="p-3 bg-surface-raised rounded border border-border">
          <div className="flex items-center justify-between mb-2">
            <span className="text-xs text-slate-400">Currently Optimizing</span>
            <span className="text-xs font-medium">{data.currentlyOptimizing}</span>
          </div>
          <div className="flex items-center justify-between mb-1">
            <span className="text-xs text-slate-400">Avg Time</span>
            <span className="text-xs">{data.avgOptimizationTime}</span>
          </div>
          <div className="flex items-center justify-between">
            <span className="text-xs text-slate-400">Improvement Range</span>
            <span className="text-xs text-green-500">{data.improvementRange}</span>
          </div>
        </div>
        <div className="p-3 bg-green-500/10 rounded border border-green-500/20">
          <div className="text-xs text-slate-400 mb-1">Best Performing</div>
          <div className="text-xs font-medium">{data.bestPerforming}</div>
        </div>
      </div>
    </div>
  );
}

function StrategyBacktestingPanel({ data, isLoading }: { data?: any, isLoading?: boolean }) {
  if (isLoading) {
    return (
      <div className="panel rounded-lg border border-border bg-surface p-4">
        <div className="flex items-center gap-2 mb-4">
          <BarChart3 className="w-4 h-4 text-orange-500" />
          <h3 className="text-sm font-semibold">Backtesting</h3>
        </div>
        <div className="p-3 bg-surface-raised rounded border border-border">
          <p className="text-xs text-slate-400">Loading backtesting data...</p>
        </div>
      </div>
    );
  }

  if (!data) {
    return (
      <div className="panel rounded-lg border border-border bg-surface p-4">
        <div className="flex items-center gap-2 mb-4">
          <BarChart3 className="w-4 h-4 text-orange-500" />
          <h3 className="text-sm font-semibold">Backtesting</h3>
        </div>
        <div className="p-3 bg-surface-raised rounded border border-border">
          <p className="text-xs text-slate-400">No backtesting data available</p>
        </div>
      </div>
    );
  }

  return (
    <div className="panel rounded-lg border border-border bg-surface p-4">
      <div className="flex items-center gap-2 mb-4">
        <BarChart3 className="w-4 h-4 text-orange-500" />
        <h3 className="text-sm font-semibold">Backtesting</h3>
      </div>
      <div className="space-y-3">
        <div className="grid grid-cols-2 gap-3">
          <div className="p-3 bg-surface-raised rounded border border-border text-center">
            <div className="text-lg font-semibold">{data.totalBacktests}</div>
            <div className="text-xs text-slate-400">Total</div>
          </div>
          <div className="p-3 bg-surface-raised rounded border border-border text-center">
            <div className="text-lg font-semibold text-green-500">{(data.successRate * 100).toFixed(0)}%</div>
            <div className="text-xs text-slate-400">Success</div>
          </div>
        </div>
        <div className="p-3 bg-surface-raised rounded border border-border">
          <div className="text-xs text-slate-400 mb-2">Last Results: {data.lastResults.strategy}</div>
          <div className="grid grid-cols-2 gap-2 text-xs">
            <div>
              <span className="text-slate-400">Period:</span>
              <span className="ml-1">{data.lastResults.period}</span>
            </div>
            <div>
              <span className="text-slate-400">Return:</span>
              <span className="ml-1 text-green-500">{data.lastResults.return}</span>
            </div>
            <div>
              <span className="text-slate-400">Sharpe:</span>
              <span className="ml-1">{data.lastResults.sharpe}</span>
            </div>
            <div>
              <span className="text-slate-400">Max DD:</span>
              <span className="ml-1 text-red-500">{data.lastResults.maxDrawdown}</span>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}

function StrategyDeploymentPanel({ data, isLoading }: { data?: any, isLoading?: boolean }) {
  if (isLoading) {
    return (
      <div className="panel rounded-lg border border-border bg-surface p-4">
        <div className="flex items-center gap-2 mb-4">
          <CheckCircle className="w-4 h-4 text-green-500" />
          <h3 className="text-sm font-semibold">Deployment</h3>
        </div>
        <div className="p-3 bg-surface-raised rounded border border-border">
          <p className="text-xs text-slate-400">Loading deployment data...</p>
        </div>
      </div>
    );
  }

  if (!data) {
    return (
      <div className="panel rounded-lg border border-border bg-surface p-4">
        <div className="flex items-center gap-2 mb-4">
          <CheckCircle className="w-4 h-4 text-green-500" />
          <h3 className="text-sm font-semibold">Deployment</h3>
        </div>
        <div className="p-3 bg-surface-raised rounded border border-border">
          <p className="text-xs text-slate-400">No deployment data available</p>
        </div>
      </div>
    );
  }

  return (
    <div className="panel rounded-lg border border-border bg-surface p-4">
      <div className="flex items-center gap-2 mb-4">
        <CheckCircle className="w-4 h-4 text-green-500" />
        <h3 className="text-sm font-semibold">Deployment</h3>
      </div>
      <div className="space-y-3">
        <div className="grid grid-cols-3 gap-3">
          <div className="p-3 bg-surface-raised rounded border border-border text-center">
            <div className="text-lg font-semibold text-green-500">{data.liveStrategies}</div>
            <div className="text-xs text-slate-400">Live</div>
          </div>
          <div className="p-3 bg-surface-raised rounded border border-border text-center">
            <div className="text-lg font-semibold text-yellow-500">{data.canaryStrategies}</div>
            <div className="text-xs text-slate-400">Canary</div>
          </div>
          <div className="p-3 bg-surface-raised rounded border border-border text-center">
            <div className="text-lg font-semibold text-blue-500">{data.proposedStrategies}</div>
            <div className="text-xs text-slate-400">Proposed</div>
          </div>
        </div>
        <div className="p-3 bg-green-500/10 rounded border border-green-500/20">
          <div className="text-xs text-slate-400 mb-1">Last Deployment</div>
          <div className="text-xs font-medium">{data.lastDeployment.strategy}</div>
          <div className="flex items-center justify-between mt-1 text-xs">
            <span className="text-green-500">{data.lastDeployment.status}</span>
            <span className="text-green-500">{data.lastDeployment.performance}</span>
          </div>
        </div>
      </div>
    </div>
  );
}

// ============================================================================
// PORTFOLIO INTELLIGENCE TAB
// ============================================================================

function PortfolioIntelligenceTab() {
  // Fetch all portfolio intelligence data
  const { data: analysis, isLoading: analysisLoading } = usePortfolioAnalysis();
  const { data: allocation, isLoading: allocationLoading } = usePortfolioAllocation();
  const { data: risk, isLoading: riskLoading } = usePortfolioRisk();
  const { data: performance, isLoading: performanceLoading } = usePortfolioPerformance();
  const { data: attribution, isLoading: attributionLoading } = usePortfolioAttribution();

  const isLoading = analysisLoading || allocationLoading || riskLoading || performanceLoading || attributionLoading;
  const hasData = analysis || allocation || risk || performance || attribution;

  return (
    <div className="portfolio-intelligence-tab space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-lg font-semibold">Portfolio Intelligence</h2>
          <p className="text-sm text-slate-400 mt-1">
            Portfolio analysis, allocation, risk, performance, and attribution
          </p>
        </div>
        <div className="flex items-center gap-2 text-xs text-slate-500">
          <PieChart className="w-4 h-4" />
          {analysis ? `$${(analysis.totalValue / 1000000).toFixed(2)}M` : 'Loading...'}
        </div>
      </div>

      {/* Loading State */}
      {isLoading && !hasData && (
        <div className="p-4 bg-surface-raised border border-border rounded">
          <p className="text-sm text-slate-400">Loading portfolio intelligence data...</p>
        </div>
      )}

      {/* 5-Panel Grid Layout */}
      <div className="grid grid-cols-3 gap-4">
        <PortfolioAnalysisPanel data={analysis} isLoading={analysisLoading} />
        <PortfolioAllocationPanel data={allocation} isLoading={allocationLoading} />
        <PortfolioRiskPanel data={risk} isLoading={riskLoading} />
        <PortfolioPerformancePanel data={performance} isLoading={performanceLoading} />
        <PortfolioAttributionPanel data={attribution} isLoading={attributionLoading} />
      </div>
    </div>
  );
}

function PortfolioAnalysisPanel({ data, isLoading }: { data?: any, isLoading?: boolean }) {
  if (isLoading) {
    return (
      <div className="panel rounded-lg border border-border bg-surface p-4">
        <div className="flex items-center gap-2 mb-4">
          <PieChart className="w-4 h-4 text-purple-500" />
          <h3 className="text-sm font-semibold">Portfolio Analysis</h3>
        </div>
        <div className="p-3 bg-surface-raised rounded border border-border">
          <p className="text-xs text-slate-400">Loading analysis...</p>
        </div>
      </div>
    );
  }

  if (!data) {
    return (
      <div className="panel rounded-lg border border-border bg-surface p-4">
        <div className="flex items-center gap-2 mb-4">
          <PieChart className="w-4 h-4 text-purple-500" />
          <h3 className="text-sm font-semibold">Portfolio Analysis</h3>
        </div>
        <div className="p-3 bg-surface-raised rounded border border-border">
          <p className="text-xs text-slate-400">No analysis data available</p>
        </div>
      </div>
    );
  }

  return (
    <div className="panel rounded-lg border border-border bg-surface p-4">
      <div className="flex items-center gap-2 mb-4">
        <PieChart className="w-4 h-4 text-purple-500" />
        <h3 className="text-sm font-semibold">Portfolio Analysis</h3>
      </div>
      <div className="space-y-3">
        <div className="p-3 bg-surface-raised rounded border border-border">
          <div className="text-xs text-slate-400 mb-1">Total Value</div>
          <div className="text-lg font-semibold">${(data.totalValue / 1000000).toFixed(2)}M</div>
        </div>
        <div className="p-3 bg-green-500/10 rounded border border-green-500/20">
          <div className="text-xs text-slate-400 mb-1">Daily P&L</div>
          <div className="text-lg font-semibold text-green-500">
            ${data.dailyPnL.toLocaleString()}
          </div>
          <div className="text-xs text-green-500">+{data.dailyPnLPercent.toFixed(2)}%</div>
        </div>
        <div className="grid grid-cols-2 gap-2">
          <div className="p-2 bg-surface-raised rounded border border-border text-center">
            <div className="text-xs text-slate-400">Weekly</div>
            <div className="text-xs font-medium text-green-500">+${data.weeklyPnL.toLocaleString()}</div>
          </div>
          <div className="p-2 bg-surface-raised rounded border border-border text-center">
            <div className="text-xs text-slate-400">Monthly</div>
            <div className="text-xs font-medium text-green-500">+${data.monthlyPnL.toLocaleString()}</div>
          </div>
        </div>
      </div>
    </div>
  );
}

function PortfolioAllocationPanel({ data, isLoading }: { data?: any[], isLoading?: boolean }) {
  if (isLoading) {
    return (
      <div className="panel rounded-lg border border-border bg-surface p-4">
        <div className="flex items-center gap-2 mb-4">
          <PieChart className="w-4 h-4 text-blue-500" />
          <h3 className="text-sm font-semibold">Allocation</h3>
        </div>
        <div className="p-3 bg-surface-raised rounded border border-border">
          <p className="text-xs text-slate-400">Loading allocation...</p>
        </div>
      </div>
    );
  }

  if (!data || data.length === 0) {
    return (
      <div className="panel rounded-lg border border-border bg-surface p-4">
        <div className="flex items-center gap-2 mb-4">
          <PieChart className="w-4 h-4 text-blue-500" />
          <h3 className="text-sm font-semibold">Allocation</h3>
        </div>
        <div className="p-3 bg-surface-raised rounded border border-border">
          <p className="text-xs text-slate-400">No allocation data available</p>
        </div>
      </div>
    );
  }

  return (
    <div className="panel rounded-lg border border-border bg-surface p-4">
      <div className="flex items-center gap-2 mb-4">
        <PieChart className="w-4 h-4 text-blue-500" />
        <h3 className="text-sm font-semibold">Allocation</h3>
      </div>
      <div className="space-y-3">
        {data.map((alloc: any, idx: number) => (
          <div key={idx} className="p-3 bg-surface-raised rounded border border-border">
            <div className="flex items-center justify-between mb-2">
              <span className="text-xs font-medium">{alloc.asset}</span>
              <span className="text-xs">${(alloc.value / 1000).toFixed(0)}K</span>
            </div>
            <div className="flex items-center gap-2 mb-1">
              <div className="flex-1 bg-slate-700 rounded-full h-2">
                <div 
                  className="bg-blue-500 h-2 rounded-full" 
                  style={{ width: `${alloc.percentage}%` }}
                />
              </div>
              <span className="text-xs">{alloc.percentage}%</span>
            </div>
            <div className="flex items-center justify-between text-xs text-slate-400">
              <span>Target: {alloc.target}%</span>
              <span className={alloc.percentage > alloc.target ? 'text-red-500' : 'text-green-500'}>
                {alloc.percentage > alloc.target ? 'Over' : 'On Target'}
              </span>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}

function PortfolioRiskPanel({ data, isLoading }: { data?: any, isLoading?: boolean }) {
  if (isLoading) {
    return (
      <div className="panel rounded-lg border border-border bg-surface p-4">
        <div className="flex items-center gap-2 mb-4">
          <AlertTriangle className="w-4 h-4 text-orange-500" />
          <h3 className="text-sm font-semibold">Risk Analysis</h3>
        </div>
        <div className="p-3 bg-surface-raised rounded border border-border">
          <p className="text-xs text-slate-400">Loading risk data...</p>
        </div>
      </div>
    );
  }

  if (!data) {
    return (
      <div className="panel rounded-lg border border-border bg-surface p-4">
        <div className="flex items-center gap-2 mb-4">
          <AlertTriangle className="w-4 h-4 text-orange-500" />
          <h3 className="text-sm font-semibold">Risk Analysis</h3>
        </div>
        <div className="p-3 bg-surface-raised rounded border border-border">
          <p className="text-xs text-slate-400">No risk data available</p>
        </div>
      </div>
    );
  }

  return (
    <div className="panel rounded-lg border border-border bg-surface p-4">
      <div className="flex items-center gap-2 mb-4">
        <AlertTriangle className="w-4 h-4 text-orange-500" />
        <h3 className="text-sm font-semibold">Risk Analysis</h3>
      </div>
      <div className="space-y-3">
        <div className="p-3 bg-surface-raised rounded border border-border">
          <div className="flex items-center justify-between mb-2">
            <span className="text-xs text-slate-400">Overall Risk</span>
            <span className="text-xs font-medium text-yellow-500">{data.overallRisk}</span>
          </div>
          <div className="flex items-center gap-2">
            <div className="flex-1 bg-slate-700 rounded-full h-2">
              <div 
                className="bg-yellow-500 h-2 rounded-full" 
                style={{ width: `${data.riskScore * 100}%` }}
              />
            </div>
            <span className="text-xs">{(data.riskScore * 100).toFixed(0)}%</span>
          </div>
        </div>
        <div className="grid grid-cols-2 gap-2">
          <div className="p-2 bg-surface-raised rounded border border-border">
            <div className="text-xs text-slate-400">Max DD</div>
            <div className="text-xs font-medium text-red-500">{data.maxDrawdown}</div>
          </div>
          <div className="p-2 bg-surface-raised rounded border border-border">
            <div className="text-xs text-slate-400">Current DD</div>
            <div className="text-xs font-medium text-red-500">{data.currentDrawdown}</div>
          </div>
          <div className="p-2 bg-surface-raised rounded border border-border">
            <div className="text-xs text-slate-400">VaR 95%</div>
            <div className="text-xs font-medium">{data.var95}</div>
          </div>
          <div className="p-2 bg-surface-raised rounded border border-border">
            <div className="text-xs text-slate-400">Beta</div>
            <div className="text-xs font-medium">{data.beta}</div>
          </div>
        </div>
        <div className="p-3 bg-green-500/10 rounded border border-green-500/20">
          <div className="flex items-center justify-between">
            <span className="text-xs text-slate-400">Sharpe Ratio</span>
            <span className="text-xs font-medium text-green-500">{data.sharpe}</span>
          </div>
        </div>
      </div>
    </div>
  );
}

function PortfolioPerformancePanel({ data, isLoading }: { data?: any, isLoading?: boolean }) {
  if (isLoading) {
    return (
      <div className="panel rounded-lg border border-border bg-surface p-4">
        <div className="flex items-center gap-2 mb-4">
          <TrendingUp className="w-4 h-4 text-green-500" />
          <h3 className="text-sm font-semibold">Performance</h3>
        </div>
        <div className="p-3 bg-surface-raised rounded border border-border">
          <p className="text-xs text-slate-400">Loading performance...</p>
        </div>
      </div>
    );
  }

  if (!data) {
    return (
      <div className="panel rounded-lg border border-border bg-surface p-4">
        <div className="flex items-center gap-2 mb-4">
          <TrendingUp className="w-4 h-4 text-green-500" />
          <h3 className="text-sm font-semibold">Performance</h3>
        </div>
        <div className="p-3 bg-surface-raised rounded border border-border">
          <p className="text-xs text-slate-400">No performance data available</p>
        </div>
      </div>
    );
  }

  return (
    <div className="panel rounded-lg border border-border bg-surface p-4">
      <div className="flex items-center gap-2 mb-4">
        <TrendingUp className="w-4 h-4 text-green-500" />
        <h3 className="text-sm font-semibold">Performance</h3>
      </div>
      <div className="space-y-3">
        <div className="grid grid-cols-2 gap-3">
          <div className="p-3 bg-surface-raised rounded border border-border text-center">
            <div className="text-lg font-semibold text-green-500">{data.totalReturn}%</div>
            <div className="text-xs text-slate-400">Total Return</div>
          </div>
          <div className="p-3 bg-surface-raised rounded border border-border text-center">
            <div className="text-lg font-semibold text-green-500">{data.annualizedReturn}%</div>
            <div className="text-xs text-slate-400">Annualized</div>
          </div>
        </div>
        <div className="grid grid-cols-2 gap-2">
          <div className="p-2 bg-surface-raised rounded border border-border">
            <div className="text-xs text-slate-400">Volatility</div>
            <div className="text-xs font-medium">{data.volatility}%</div>
          </div>
          <div className="p-2 bg-surface-raised rounded border border-border">
            <div className="text-xs text-slate-400">Win Rate</div>
            <div className="text-xs font-medium">{(data.winRate * 100).toFixed(0)}%</div>
          </div>
          <div className="p-2 bg-surface-raised rounded border border-border">
            <div className="text-xs text-slate-400">Avg Win</div>
            <div className="text-xs font-medium text-green-500">${data.avgWin.toLocaleString()}</div>
          </div>
          <div className="p-2 bg-surface-raised rounded border border-border">
            <div className="text-xs text-slate-400">Avg Loss</div>
            <div className="text-xs font-medium text-red-500">${data.avgLoss.toLocaleString()}</div>
          </div>
        </div>
        <div className="p-3 bg-surface-raised rounded border border-border">
          <div className="flex items-center justify-between">
            <span className="text-xs text-slate-400">Profit Factor</span>
            <span className="text-xs font-medium text-green-500">{data.profitFactor}</span>
          </div>
        </div>
      </div>
    </div>
  );
}

function PortfolioAttributionPanel({ data, isLoading }: { data?: any[], isLoading?: boolean }) {
  if (isLoading) {
    return (
      <div className="panel rounded-lg border border-border bg-surface p-4">
        <div className="flex items-center gap-2 mb-4">
          <BarChart3 className="w-4 h-4 text-purple-500" />
          <h3 className="text-sm font-semibold">Performance Attribution</h3>
        </div>
        <div className="p-3 bg-surface-raised rounded border border-border">
          <p className="text-xs text-slate-400">Loading attribution...</p>
        </div>
      </div>
    );
  }

  if (!data || data.length === 0) {
    return (
      <div className="panel rounded-lg border border-border bg-surface p-4">
        <div className="flex items-center gap-2 mb-4">
          <BarChart3 className="w-4 h-4 text-purple-500" />
          <h3 className="text-sm font-semibold">Performance Attribution</h3>
        </div>
        <div className="p-3 bg-surface-raised rounded border border-border">
          <p className="text-xs text-slate-400">No attribution data available</p>
        </div>
      </div>
    );
  }

  return (
    <div className="panel rounded-lg border border-border bg-surface p-4">
      <div className="flex items-center gap-2 mb-4">
        <BarChart3 className="w-4 h-4 text-purple-500" />
        <h3 className="text-sm font-semibold">Performance Attribution</h3>
      </div>
      <div className="space-y-3">
        {data.map((attr: any, idx: number) => (
          <div key={idx} className="p-3 bg-surface-raised rounded border border-border">
            <div className="flex items-center justify-between mb-2">
              <span className="text-xs font-medium">{attr.source}</span>
              <span className="text-xs text-green-500">${attr.pnl.toLocaleString()}</span>
            </div>
            <div className="flex items-center gap-2">
              <div className="flex-1 bg-slate-700 rounded-full h-2">
                <div 
                  className="bg-purple-500 h-2 rounded-full" 
                  style={{ width: `${attr.contribution}%` }}
                />
              </div>
              <span className="text-xs">{attr.contribution}%</span>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}

// ============================================================================
// RESEARCH INTELLIGENCE TAB
// ============================================================================

function ResearchIntelligenceTab() {
  // Fetch all research intelligence data
  const { data: queue, isLoading: queueLoading } = useResearchQueue();
  const { data: knowledgeGraph, isLoading: knowledgeGraphLoading } = useKnowledgeGraph();
  const { data: learning, isLoading: learningLoading } = useModelLearning();
  const { data: publication, isLoading: publicationLoading } = useResearchPublication();
  const { data: collaboration, isLoading: collaborationLoading } = useResearchCollaboration();

  const isLoading = queueLoading || knowledgeGraphLoading || learningLoading || publicationLoading || collaborationLoading;
  const hasData = queue || knowledgeGraph || learning || publication || collaboration;

  return (
    <div className="research-intelligence-tab space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-lg font-semibold">Research Intelligence</h2>
          <p className="text-sm text-slate-400 mt-1">
            Research queue, knowledge graph, learning, publication, and collaboration
          </p>
        </div>
        <div className="flex items-center gap-2 text-xs text-slate-500">
          <BookOpen className="w-4 h-4" />
          {queue ? (queue.inProgress + queue.completed) : 'Loading...'} active projects
        </div>
      </div>

      {/* Loading State */}
      {isLoading && !hasData && (
        <div className="p-4 bg-surface-raised border border-border rounded">
          <p className="text-sm text-slate-400">Loading research intelligence data...</p>
        </div>
      )}

      {/* 5-Panel Grid Layout */}
      <div className="grid grid-cols-3 gap-4">
        <ResearchQueuePanel data={queue} isLoading={queueLoading} />
        <KnowledgeGraphPanel data={knowledgeGraph} isLoading={knowledgeGraphLoading} />
        <LearningPanel data={learning} isLoading={learningLoading} />
        <PublicationPanel data={publication} isLoading={publicationLoading} />
      </div>
    </div>
  );
}

function ResearchQueuePanel({ data, isLoading }: { data?: any, isLoading?: boolean }) {
  if (isLoading) {
    return (
      <div className="panel rounded-lg border border-border bg-surface p-4">
        <div className="flex items-center gap-2 mb-4">
          <FlaskConical className="w-4 h-4 text-purple-500" />
          <h3 className="text-sm font-semibold">Research Queue</h3>
        </div>
        <div className="p-3 bg-surface-raised rounded border border-border">
          <p className="text-xs text-slate-400">Loading queue...</p>
        </div>
      </div>
    );
  }

  if (!data) {
    return (
      <div className="panel rounded-lg border border-border bg-surface p-4">
        <div className="flex items-center gap-2 mb-4">
          <FlaskConical className="w-4 h-4 text-purple-500" />
          <h3 className="text-sm font-semibold">Research Queue</h3>
        </div>
        <div className="p-3 bg-surface-raised rounded border border-border">
          <p className="text-xs text-slate-400">No queue data available</p>
        </div>
      </div>
    );
  }

  return (
    <div className="panel rounded-lg border border-border bg-surface p-4">
      <div className="flex items-center gap-2 mb-4">
        <FlaskConical className="w-4 h-4 text-purple-500" />
        <h3 className="text-sm font-semibold">Research Queue</h3>
      </div>
      <div className="space-y-3">
        <div className="grid grid-cols-3 gap-2">
          <div className="p-2 bg-red-500/10 rounded border border-red-500/20 text-center">
            <div className="text-lg font-semibold text-red-500">{data.highPriority}</div>
            <div className="text-xs text-slate-400">High</div>
          </div>
          <div className="p-2 bg-yellow-500/10 rounded border border-yellow-500/20 text-center">
            <div className="text-lg font-semibold text-yellow-500">{data.mediumPriority}</div>
            <div className="text-xs text-slate-400">Medium</div>
          </div>
          <div className="p-2 bg-green-500/10 rounded border border-green-500/20 text-center">
            <div className="text-lg font-semibold text-green-500">{data.lowPriority}</div>
            <div className="text-xs text-slate-400">Low</div>
          </div>
        </div>
        <div className="grid grid-cols-2 gap-2">
          <div className="p-2 bg-surface-raised rounded border border-border text-center">
            <div className="text-lg font-semibold text-blue-500">{data.inProgress}</div>
            <div className="text-xs text-slate-400">In Progress</div>
          </div>
          <div className="p-2 bg-surface-raised rounded border border-border text-center">
            <div className="text-lg font-semibold text-green-500">{data.completed}</div>
            <div className="text-xs text-slate-400">Completed</div>
          </div>
        </div>
        <div className="p-3 bg-surface-raised rounded border border-border">
          <div className="flex items-center justify-between text-xs">
            <span className="text-slate-400">Avg Completion Time</span>
            <span className="font-medium">{data.avgCompletionTime}</span>
          </div>
        </div>
      </div>
    </div>
  );
}

function KnowledgeGraphPanel({ data, isLoading }: { data?: any, isLoading?: boolean }) {
  if (isLoading) {
    return (
      <div className="panel rounded-lg border border-border bg-surface p-4">
        <div className="flex items-center gap-2 mb-4">
          <Network className="w-4 h-4 text-blue-500" />
          <h3 className="text-sm font-semibold">Knowledge Graph</h3>
        </div>
        <div className="p-3 bg-surface-raised rounded border border-border">
          <p className="text-xs text-slate-400">Loading graph...</p>
        </div>
      </div>
    );
  }

  if (!data) {
    return (
      <div className="panel rounded-lg border border-border bg-surface p-4">
        <div className="flex items-center gap-2 mb-4">
          <Network className="w-4 h-4 text-blue-500" />
          <h3 className="text-sm font-semibold">Knowledge Graph</h3>
        </div>
        <div className="p-3 bg-surface-raised rounded border border-border">
          <p className="text-xs text-slate-400">No graph data available</p>
        </div>
      </div>
    );
  }

  return (
    <div className="panel rounded-lg border border-border bg-surface p-4">
      <div className="flex items-center gap-2 mb-4">
        <Network className="w-4 h-4 text-blue-500" />
        <h3 className="text-sm font-semibold">Knowledge Graph</h3>
      </div>
      <div className="space-y-3">
        <div className="grid grid-cols-2 gap-3">
          <div className="p-3 bg-surface-raised rounded border border-border text-center">
            <div className="text-lg font-semibold">{data.nodes.toLocaleString()}</div>
            <div className="text-xs text-slate-400">Nodes</div>
          </div>
          <div className="p-3 bg-surface-raised rounded border border-border text-center">
            <div className="text-lg font-semibold">{data.edges.toLocaleString()}</div>
            <div className="text-xs text-slate-400">Edges</div>
          </div>
        </div>
        <div className="grid grid-cols-2 gap-2">
          <div className="p-2 bg-surface-raised rounded border border-border text-center">
            <div className="text-sm font-medium">{data.clusters}</div>
            <div className="text-xs text-slate-400">Clusters</div>
          </div>
          <div className="p-2 bg-surface-raised rounded border border-border text-center">
            <div className="text-sm font-medium text-green-500">{data.growthRate}</div>
            <div className="text-xs text-slate-400">Growth</div>
          </div>
        </div>
        <div className="p-3 bg-surface-raised rounded border border-border">
          <div className="flex items-center justify-between text-xs">
            <span className="text-slate-400">Last Update</span>
            <span className="font-medium">{data.lastUpdate}</span>
          </div>
        </div>
      </div>
    </div>
  );
}

function LearningPanel({ data, isLoading }: { data?: any, isLoading?: boolean }) {
  if (isLoading) {
    return (
      <div className="panel rounded-lg border border-border bg-surface p-4">
        <div className="flex items-center gap-2 mb-4">
          <Brain className="w-4 h-4 text-green-500" />
          <h3 className="text-sm font-semibold">Model Learning</h3>
        </div>
        <div className="p-3 bg-surface-raised rounded border border-border">
          <p className="text-xs text-slate-400">Loading learning...</p>
        </div>
      </div>
    );
  }

  if (!data) {
    return (
      <div className="panel rounded-lg border border-border bg-surface p-4">
        <div className="flex items-center gap-2 mb-4">
          <Brain className="w-4 h-4 text-green-500" />
          <h3 className="text-sm font-semibold">Model Learning</h3>
        </div>
        <div className="p-3 bg-surface-raised rounded border border-border">
          <p className="text-xs text-slate-400">No learning data available</p>
        </div>
      </div>
    );
  }

  return (
    <div className="panel rounded-lg border border-border bg-surface p-4">
      <div className="flex items-center gap-2 mb-4">
        <Brain className="w-4 h-4 text-green-500" />
        <h3 className="text-sm font-semibold">Model Learning</h3>
      </div>
      <div className="space-y-3">
        <div className="grid grid-cols-2 gap-3">
          <div className="p-3 bg-surface-raised rounded border border-border text-center">
            <div className="text-lg font-semibold text-green-500">{data.activeModels}</div>
            <div className="text-xs text-slate-400">Active Models</div>
          </div>
          <div className="p-3 bg-surface-raised rounded border border-border text-center">
            <div className="text-lg font-semibold text-blue-500">{data.trainingJobs}</div>
            <div className="text-xs text-slate-400">Training</div>
          </div>
        </div>
        <div className="p-3 bg-surface-raised rounded border border-border">
          <div className="flex items-center justify-between mb-2">
            <span className="text-xs text-slate-400">Model Accuracy</span>
            <span className="text-xs font-medium text-green-500">{(data.modelAccuracy * 100).toFixed(0)}%</span>
          </div>
          <div className="flex items-center gap-2">
            <div className="flex-1 bg-slate-700 rounded-full h-2">
              <div 
                className="bg-green-500 h-2 rounded-full" 
                style={{ width: `${data.trainingProgress}%` }}
              />
            </div>
            <span className="text-xs">{data.trainingProgress}%</span>
          </div>
        </div>
        <div className="grid grid-cols-2 gap-2">
          <div className="p-2 bg-surface-raised rounded border border-border">
            <div className="text-xs text-slate-400">Last Training</div>
            <div className="text-xs">{data.lastTraining}</div>
          </div>
          <div className="p-2 bg-surface-raised rounded border border-border">
            <div className="text-xs text-slate-400">Next Scheduled</div>
            <div className="text-xs">{data.nextScheduled}</div>
          </div>
        </div>
      </div>
    </div>
  );
}

function PublicationPanel({ data, isLoading }: { data?: any, isLoading?: boolean }) {
  if (isLoading) {
    return (
      <div className="panel rounded-lg border border-border bg-surface p-4">
        <div className="flex items-center gap-2 mb-4">
          <BookOpen className="w-4 h-4 text-purple-500" />
          <h3 className="text-sm font-semibold">Publications</h3>
        </div>
        <div className="p-3 bg-surface-raised rounded border border-border">
          <p className="text-xs text-slate-400">Loading publications...</p>
        </div>
      </div>
    );
  }

  if (!data) {
    return (
      <div className="panel rounded-lg border border-border bg-surface p-4">
        <div className="flex items-center gap-2 mb-4">
          <BookOpen className="w-4 h-4 text-purple-500" />
          <h3 className="text-sm font-semibold">Publications</h3>
        </div>
        <div className="p-3 bg-surface-raised rounded border border-border">
          <p className="text-xs text-slate-400">No publication data available</p>
        </div>
      </div>
    );
  }

  return (
    <div className="panel rounded-lg border border-border bg-surface p-4">
      <div className="flex items-center gap-2 mb-4">
        <BookOpen className="w-4 h-4 text-purple-500" />
        <h3 className="text-sm font-semibold">Publications</h3>
      </div>
      <div className="space-y-3">
        <div className="grid grid-cols-3 gap-2">
          <div className="p-2 bg-surface-raised rounded border border-border text-center">
            <div className="text-lg font-semibold text-green-500">{data.published}</div>
            <div className="text-xs text-slate-400">Published</div>
          </div>
          <div className="p-2 bg-surface-raised rounded border border-border text-center">
            <div className="text-lg font-semibold text-yellow-500">{data.inReview}</div>
            <div className="text-xs text-slate-400">In Review</div>
          </div>
          <div className="p-2 bg-surface-raised rounded border border-border text-center">
            <div className="text-lg font-semibold text-blue-500">{data.drafts}</div>
            <div className="text-xs text-slate-400">Drafts</div>
          </div>
        </div>
        <div className="grid grid-cols-2 gap-2">
          <div className="p-2 bg-surface-raised rounded border border-border">
            <div className="text-xs text-slate-400">Total Citations</div>
            <div className="text-xs font-medium">{data.totalCitations}</div>
          </div>
          <div className="p-2 bg-surface-raised rounded border border-border">
            <div className="text-xs text-slate-400">Avg Impact Score</div>
            <div className="text-xs font-medium text-green-500">{data.avgImpactScore}</div>
          </div>
        </div>
        <div className="p-3 bg-surface-raised rounded border border-border">
          <div className="flex items-center justify-between text-xs">
            <span className="text-slate-400">Last Publication</span>
            <span className="font-medium">{data.lastPublication}</span>
          </div>
        </div>
      </div>
    </div>
  );
}

// ============================================================================
// AI ASSISTANT INTEGRATIONS TAB
// ============================================================================

function AIAssistantIntegrationsTab() {
  return (
    <div className="ai-assistant-integrations-tab h-full">
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 h-full">
        {/* AI Assistant Panel */}
        <div className="lg:col-span-2">
          <div className="bg-gradient-to-br from-purple-900/20 to-blue-900/20 rounded-lg border border-purple-500/30 p-6">
            <div className="flex items-center gap-3 mb-4">
              <Sparkles className="w-6 h-6 text-purple-400" />
              <div>
                <h2 className="text-xl font-bold text-white">Unified AI Assistant</h2>
                <p className="text-sm text-slate-400">Cross-system AI intelligence from INDIRA, DYON, and Unified Orchestrator</p>
              </div>
            </div>

            {/* Embedded AI Assistant Panel */}
            <div className="bg-slate-900 rounded-lg p-4 border border-slate-700">
              <AIAssistantPanel currentPage="indira-cognitive-center" />
            </div>
          </div>
        </div>

        {/* AI System Status */}
        <div className="bg-surface rounded-lg border border-border p-4">
          <div className="flex items-center gap-2 mb-4">
            <Brain className="w-5 h-5 text-blue-500" />
            <h3 className="font-semibold">AI System Status</h3>
          </div>
          <AISystemStatus />
        </div>

        {/* Cross-System Integration */}
        <div className="bg-surface rounded-lg border border-border p-4">
          <div className="flex items-center gap-2 mb-4">
            <Network className="w-5 h-5 text-green-500" />
            <h3 className="font-semibold">Cross-System Integration</h3>
          </div>
          <CrossSystemIntegration />
        </div>
      </div>
    </div>
  );
}

function AISystemStatus() {
  const aiOrchestrator = getAIOrchestrator();
  const performanceMonitor = getPerformanceMonitor();
  const [status, setStatus] = useState(aiOrchestrator.getAIStatus());
  const [systemStatus, setSystemStatus] = useState(performanceMonitor.getSystemStatus());

  useEffect(() => {
    const interval = setInterval(() => {
      setStatus(aiOrchestrator.getAIStatus());
      setSystemStatus(performanceMonitor.getSystemStatus());
    }, 5000);
    return () => clearInterval(interval);
  }, []);

  return (
    <div className="space-y-3">
      <div className="p-3 bg-surface-raised rounded border border-border">
        <div className="flex items-center justify-between mb-2">
          <span className="text-xs font-medium">Active Assistants</span>
          <span className="text-xs text-green-500">{status.assistants.filter(a => a.status === 'active').length}/{status.assistants.length}</span>
        </div>
        <div className="space-y-1">
          {status.assistants.map(assistant => (
            <div key={assistant.id} className="flex items-center justify-between text-xs">
              <span className="text-slate-400">{assistant.name}</span>
              <span className={`px-2 py-0.5 rounded ${
                assistant.status === 'active' ? 'bg-green-500/20 text-green-400' :
                assistant.status === 'processing' ? 'bg-yellow-500/20 text-yellow-400' :
                'bg-slate-500/20 text-slate-400'
              }`}>
                {assistant.status}
              </span>
            </div>
          ))}
        </div>
      </div>

      <div className="p-3 bg-surface-raised rounded border border-border">
        <div className="flex items-center justify-between mb-2">
          <span className="text-xs font-medium">Active Recommendations</span>
          <span className="text-xs text-blue-500">{status.recommendations.length}</span>
        </div>
        <div className="flex items-center justify-between mb-1">
          <span className="text-xs text-slate-400">Predictions</span>
          <span className="text-xs text-purple-500">{status.predictions.length}</span>
        </div>
        <div className="flex items-center justify-between">
          <span className="text-xs text-slate-400">Cross-System Insights</span>
          <span className="text-xs text-green-500">{status.crossSystemInsights.size}</span>
        </div>
      </div>

      {/* AI vs INDIRA Performance */}
      <div className="p-3 bg-gradient-to-r from-purple-500/10 to-blue-500/10 rounded border border-purple-500/30">
        <div className="flex items-center justify-between mb-2">
          <span className="text-xs font-medium text-purple-400">AI vs INDIRA</span>
          <span className={`text-xs ${systemStatus.performanceGap > 0 ? 'text-green-400' : 'text-blue-400'}`}>
            {systemStatus.performanceGap > 0 ? '+' : ''}{(systemStatus.performanceGap * 100).toFixed(1)}%
          </span>
        </div>
        <div className="flex items-center justify-between mb-1">
          <span className="text-xs text-slate-400">Current Controller</span>
          <span className={`text-xs font-medium ${systemStatus.currentController === 'AI' ? 'text-purple-400' : 'text-blue-400'}`}>
            {systemStatus.currentController}
          </span>
        </div>
        <div className="flex items-center justify-between">
          <span className="text-xs text-slate-400">Takeover Enabled</span>
          <span className={`text-xs ${systemStatus.takeoverEnabled ? 'text-green-400' : 'text-slate-500'}`}>
            {systemStatus.takeoverEnabled ? 'Yes' : 'No'}
          </span>
        </div>
      </div>

      <div className="p-3 bg-surface-raised rounded border border-border">
        <div className="flex items-center justify-between mb-2">
          <span className="text-xs font-medium">Configuration</span>
        </div>
        <div className="space-y-1 text-xs">
          <div className="flex items-center justify-between">
            <span className="text-slate-400">Predictive AI</span>
            <span className={status.config.enablePredictiveAI ? 'text-green-500' : 'text-slate-500'}>
              {status.config.enablePredictiveAI ? 'Enabled' : 'Disabled'}
            </span>
          </div>
          <div className="flex items-center justify-between">
            <span className="text-slate-400">Contextual Assistance</span>
            <span className={status.config.enableContextualAssistance ? 'text-green-500' : 'text-slate-500'}>
              {status.config.enableContextualAssistance ? 'Enabled' : 'Disabled'}
            </span>
          </div>
          <div className="flex items-center justify-between">
            <span className="text-slate-400">Cross-System Learning</span>
            <span className={status.config.enableCrossSystemLearning ? 'text-green-500' : 'text-slate-500'}>
              {status.config.enableCrossSystemLearning ? 'Enabled' : 'Disabled'}
            </span>
          </div>
        </div>
      </div>
    </div>
  );
}

function CrossSystemIntegration() {
  const aiOrchestrator = getAIOrchestrator();
  const [insights, setInsights] = useState(aiOrchestrator.getCrossSystemInsights());

  useEffect(() => {
    const interval = setInterval(() => {
      setInsights(aiOrchestrator.getCrossSystemInsights());
    }, 10000);
    return () => clearInterval(interval);
  }, []);

  const insightArray = Array.from(insights.entries());

  return (
    <div className="space-y-3">
      {insightArray.length === 0 ? (
        <div className="p-4 bg-surface-raised rounded border border-border text-center">
          <p className="text-xs text-slate-400">No cross-system patterns detected yet</p>
          <p className="text-xs text-slate-500 mt-1">AI will learn from your interactions across the dashboard</p>
        </div>
      ) : (
        insightArray.map(([id, insight]) => (
          <div key={id} className="p-3 bg-surface-raised rounded border border-border">
            <div className="flex items-center justify-between mb-2">
              <span className="text-xs font-medium capitalize">{insight.action.replace(/_/g, ' ')}</span>
              <span className="text-xs text-blue-500">{insight.frequency}x</span>
            </div>
            <div className="flex items-center gap-2 text-xs">
              <span className="text-slate-400">Last seen:</span>
              <span className="text-slate-300">
                {new Date(insight.lastSeen).toLocaleTimeString()}
              </span>
            </div>
            {insight.automationOpportunity && (
              <div className="mt-2 p-2 bg-green-500/10 rounded border border-green-500/20">
                <span className="text-xs text-green-400">⚡ Automation Opportunity</span>
              </div>
            )}
          </div>
        ))
      )}

      <div className="p-3 bg-blue-500/10 rounded border border-blue-500/20">
        <div className="text-xs text-blue-400 mb-1">INDIRA Integration</div>
        <div className="text-xs text-slate-400">
          Market, Trader, Strategy, Portfolio, and Research intelligence active
        </div>
      </div>

      <div className="p-3 bg-purple-500/10 rounded border border-purple-500/20">
        <div className="text-xs text-purple-400 mb-1">DYON Integration</div>
        <div className="text-xs text-slate-400">
          Repository, Architecture, Runtime, Infrastructure, Research, and Advisory intelligence active
        </div>
      </div>
    </div>
  );
}
