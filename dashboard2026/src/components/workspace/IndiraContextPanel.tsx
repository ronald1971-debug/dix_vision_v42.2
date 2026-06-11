/**
 * INDIRA Context Panel
 * 
 * Displays INDIRA's current objectives, research, models, strategies, and opportunities
 * Provides visibility into INDIRA's current focus and priorities
 */

import { useState } from 'react';
import { Panel, PanelSection } from '../agent/Panel';
import type {
  Objective,
  Research,
  TraderModel,
  Strategy,
  Opportunity,
  PortfolioState,
  RiskState,
  Constraint,
  ExposureLimit,
} from '@/types/workspace';
import {
  Target,
  BookOpen,
  TrendingUp,
  Brain,
  Zap,
  Lightbulb,
  PieChart,
  Shield,
  AlertTriangle,
  MoreHorizontal,
} from 'lucide-react';

interface IndiraContextPanelProps {
  className?: string;
}

export function IndiraContextPanel({ className }: IndiraContextPanelProps) {
  const [showAllObjectives, setShowAllObjectives] = useState(false);
  const [showAllResearch, setShowAllResearch] = useState(false);
  const [showAllModels, setShowAllModels] = useState(false);
  const [showAllStrategies, setShowAllStrategies] = useState(false);
  const [showAllOpportunities, setShowAllOpportunities] = useState(false);

  // Mock data for demonstration (in real scenario, this would come from backend)
  const mockObjectives: Objective[] = [
    {
      id: 'obj-1',
      title: 'Analyze Bitcoin market trends for Q3',
      description: 'Identify key trends and patterns in Bitcoin market for Q3 2024',
      priority: 'high',
      status: 'active',
      progress: 65,
      createdAt: Date.now() - 86400000,
      updatedAt: Date.now() - 3600000,
      relatedStrategies: ['strategy-1', 'strategy-2'],
    },
    {
      id: 'obj-2',
      title: 'Develop momentum-based trading strategy',
      description: 'Create strategy that capitalizes on market momentum patterns',
      priority: 'critical',
      status: 'active',
      progress: 40,
      deadline: Date.now() + 604800000,
      createdAt: Date.now() - 172800000,
      updatedAt: Date.now() - 7200000,
      relatedStrategies: ['strategy-3'],
    },
    {
      id: 'obj-3',
      title: 'Model top 100 Solana traders',
      description: 'Build comprehensive behavioral models for top Solana traders',
      priority: 'medium',
      status: 'paused',
      progress: 25,
      relatedStrategies: ['strategy-4'],
      createdAt: Date.now() - 259200000,
      updatedAt: Date.now() - 86400000,
    },
  ];

  const mockResearch: Research[] = [
    {
      id: 'research-1',
      topic: 'Bitcoin Lightning Network adoption trends',
      status: 'active',
      progress: 78,
      findings: [
        {
          id: 'find-1',
          description: 'Lightning Network capacity increased 40% in Q2',
          confidence: 0.85,
          evidence: ['chaindata', 'onchain'],
          timestamp: Date.now() - 3600000,
        },
      ],
      relatedMarkets: ['BTC', 'L-BTC'],
      relatedTraders: ['0x1234...', 'wallet_789'],
      startDate: Date.now() - 604800000,
      confidence: 0.72,
    },
    {
      id: 'research-2',
      topic: 'Ethereum DeFi liquidity fragmentation',
      status: 'active',
      progress: 45,
      findings: [
        {
          id: 'find-2',
          description: 'Liquidity spread increased by 200bps across major DEXs',
          confidence: 0.67,
          evidence: ['onchain', 'api'],
          timestamp: Date.now() - 7200000,
        },
      ],
      relatedMarkets: ['ETH', 'USDT'],
      relatedTraders: ['0xabcd...'],
      startDate: Date.now() - 1209600000,
      confidence: 0.65,
    },
    {
      id: 'research-3',
      topic: 'Solana memecoin seasonality patterns',
      status: 'completed',
      progress: 100,
      findings: [
        {
          id: 'find-3',
          description: 'Identified strong weekend volatility patterns',
          confidence: 0.91,
          evidence: ['historical', 'statistical'],
          timestamp: Date.now() - 604800000,
        },
      ],
      relatedMarkets: ['SOL', 'USDC'],
      relatedTraders: ['0x5678...'],
      startDate: Date.now() - 2592000000,
      endDate: Date.now() - 86400000,
      confidence: 0.91,
    },
  ];

  const mockTraderModels: TraderModel[] = [
    {
      id: 'model-1',
      traderId: '0x1234...',
      modelType: 'behavioral',
      accuracy: 0.78,
      confidence: 0.85,
      lastUpdated: Date.now() - 3600000,
      predictions: [
        {
          id: 'pred-1',
          target: 'BTC',
          prediction: 'LONG',
          confidence: 0.78,
          timeframe: '24h',
          actual: 'LONG',
          accuracy: 0.85,
          timestamp: Date.now() - 7200000,
        },
      ],
      performanceMetrics: {
        winRate: 0.78,
        averageReturn: 0.045,
        volatility: 0.12,
        maxDrawdown: 0.08,
        profitFactor: 2.1,
      },
    },
    {
      id: 'model-2',
      traderId: '0xabcd...',
      modelType: 'performance',
      accuracy: 0.82,
      confidence: 0.79,
      lastUpdated: Date.now() - 1800000,
      predictions: [],
      performanceMetrics: {
        winRate: 0.82,
        averageReturn: 0.052,
        volatility: 0.15,
        maxDrawdown: 0.06,
        profitFactor: 2.8,
      },
    },
    {
      id: 'model-3',
      traderId: 'wallet_789',
      modelType: 'pattern',
      accuracy: 0.71,
      confidence: 0.73,
      lastUpdated: Date.now() - 7200000,
      predictions: [],
      performanceMetrics: {
        winRate: 0.71,
        averageReturn: 0.038,
        volatility: 0.18,
        maxDrawdown: 0.12,
        profitFactor: 1.8,
      },
    },
  ];

  const mockStrategies: Strategy[] = [
    {
      id: 'strategy-1',
      name: 'BTC Momentum Reversal',
      type: 'trend-following',
      status: 'active',
      performance: 0.12,
      parameters: { lookbackPeriod: 24, threshold: 0.7 },
      riskLevel: 'medium',
      createdAt: Date.now() - 86400000,
      lastModified: Date.now() - 3600000,
    },
    {
      id: 'strategy-2',
      name: 'ETH Mean Reversion',
      type: 'mean-reversion',
      status: 'testing',
      performance: -0.03,
      parameters: { lookbackPeriod: 48, threshold: 2.0 },
      riskLevel: 'low',
      createdAt: Date.now() - 604800000,
      lastModified: Date.now() - 86400000,
    },
    {
      id: 'strategy-3',
      name: 'SOL Momentum',
      type: 'trend-following',
      status: 'active',
      performance: 0.25,
      parameters: { lookbackPeriod: 12, threshold: 0.8 },
      riskLevel: 'high',
      createdAt: Date.now() - 259200000,
      lastModified: Date.now() - 14400000,
    },
  ];

  const mockOpportunities: Opportunity[] = [
    {
      id: 'opp-1',
      type: 'trade',
      asset: 'BTC',
      description: 'BTC momentum signal detected at $42,500',
      confidence: 0.75,
      expectedReturn: 0.12,
      riskLevel: 'high',
      timeframe: '24h',
      createdAt: Date.now() - 1800000,
      expiresAt: Date.now() + 82800000,
    },
    {
      id: 'opp-2',
      type: 'research',
      asset: 'SOL',
      description: 'Solana liquidity fragmentation analysis opportunity',
      confidence: 0.68,
      expectedReturn: 0.0,
      riskLevel: 'medium',
      timeframe: '7d',
      createdAt: Date.now() - 3600000,
      expiresAt: Date.now() + 604800000,
    },
    {
      id: 'opp-3',
      type: 'arbitrage',
      asset: 'ETH/USDT',
      description: 'Cross-exchange arbitrage opportunity detected',
      confidence: 0.82,
      expectedReturn: 0.02,
      riskLevel: 'low',
      timeframe: '1h',
      createdAt: Date.now() - 900000,
      expiresAt: Date.now() + 3600000,
    },
  ];

  const mockPortfolioState: PortfolioState = {
    totalValue: 1500000,
    positions: [
      {
        id: 'pos-1',
        asset: 'BTC',
        quantity: 5,
        entryPrice: 42000,
        currentPrice: 42500,
        unrealizedPnL: 2500,
        realizedPnL: 15000,
        openDate: Date.now() - 86400000,
      },
    ],
    allocation: {
      byAsset: { 'BTC': 0.60, 'ETH': 0.25, 'USDT': 0.15 },
      byStrategy: { 'strategy-1': 0.40, 'strategy-2': 0.20, 'strategy-3': 0.30, 'manual': 0.10 },
      byRisk: { 'high': 0.30, 'medium': 0.50, 'low': 0.20 },
    },
    performance: {
      daily: 0.02,
      weekly: 0.08,
      monthly: 0.15,
      ytd: 0.35,
      sharpeRatio: 2.1,
      maxDrawdown: 0.08,
    },
    lastUpdated: Date.now(),
  };

  const mockRiskState: RiskState = {
    overallRisk: 'medium',
    riskFactors: [
      {
        id: 'rf-1',
        factor: 'Market Volatility',
        level: 'high',
        impact: 0.7,
        trend: 'stable',
      },
      {
        id: 'rf-2',
        factor: 'Concentration Risk',
        level: 'medium',
        impact: 0.3,
        trend: 'improving',
      },
    ],
    constraints: [
      {
        id: 'constraint-1',
        type: 'position_limit',
        limit: 100000,
        current: 75000,
        status: 'compliant',
      },
      {
        id: 'constraint-2',
        type: 'risk_limit',
        limit: 50000,
        current: 45000,
        status: 'warning',
      },
    ],
    exposureLimits: [
      {
        asset: 'BTC',
        limit: 0.50,
        current: 0.60,
        status: 'violation',
      },
      {
        asset: 'ETH',
        limit: 0.30,
        current: 0.25,
        status: 'compliant',
      },
    ],
    lastUpdated: Date.now(),
  };

  return (
    <Panel
      title="INDIRA Context"
      className={className}
    >
      <div className="space-y-4">
        {/* Current Status Overview */}
        <SectionWithStatus 
          title="Status Overview"
          status={mockRiskState.overallRisk}
          lastUpdated={mockRiskState.lastUpdated}
        >
          <div className="grid grid-cols-2 gap-4">
            <StatusCard
              label="Portfolio Value"
              value={formatCurrency(mockPortfolioState.totalValue)}
              change={mockPortfolioState.performance.daily}
              icon={PieChart}
            />
            <StatusCard
              label="Risk Level"
              value={mockRiskState.overallRisk}
              icon={Shield}
              isRisk
            />
          </div>
        </SectionWithStatus>

        {/* Current Objectives */}
        <SectionWithHeader
          title="Current Objectives"
          onExpand={() => setShowAllObjectives(!showAllObjectives)}
        >
          <div className="space-y-2">
            {mockObjectives.slice(0, showAllObjectives ? undefined : 3).map(objective => (
              <ObjectiveItem key={objective.id} objective={objective} />
            ))}
          </div>
        </SectionWithHeader>

        {/* Active Research */}
        <SectionWithHeader
          title="Active Research"
          onExpand={() => setShowAllResearch(!showAllResearch)}
        >
          <div className="space-y-2">
            {mockResearch.slice(0, showAllResearch ? undefined : 3).map(research => (
              <ResearchItem key={research.id} research={research} />
            ))}
          </div>
        </SectionWithHeader>

        {/* Trader Models */}
        <SectionWithHeader
          title="Trader Models"
          onExpand={() => setShowAllModels(!showAllModels)}
          count={mockTraderModels.length}
        >
          <div className="space-y-2">
            {mockTraderModels.slice(0, showAllModels ? undefined : 3).map(model => (
              <TraderModelItem key={model.id} model={model} />
            ))}
          </div>
        </SectionWithHeader>

        {/* Active Strategies */}
        <SectionWithHeader
          title="Active Strategies"
          onExpand={() => setShowAllStrategies(!showAllStrategies)}
          count={mockStrategies.length}
        >
          <div className="space-y-2">
            {mockStrategies.slice(0, showAllStrategies ? undefined : 3).map(strategy => (
              <StrategyItem key={strategy.id} strategy={strategy} />
            ))}
          </div>
        </SectionWithHeader>

        {/* Opportunities */}
        <SectionWithHeader
          title="Opportunities"
          onExpand={() => setShowAllOpportunities(!showAllOpportunities)}
          count={mockOpportunities.length}
        >
          <div className="space-y-2">
            {mockOpportunities.slice(0, showAllOpportunities ? undefined : 3).map(opportunity => (
              <OpportunityItem key={opportunity.id} opportunity={opportunity} />
            ))}
          </div>
        </SectionWithHeader>

        {/* Constraints & Alerts */}
        <SectionWithHeader title="Constraints & Alerts">
          <div className="space-y-2">
            {mockRiskState.constraints.map(constraint => (
              <ConstraintItem key={constraint.id} constraint={constraint} />
            ))}
            {mockRiskState.exposureLimits
              .filter(limit => limit.status !== 'compliant')
              .map(limit => (
                <ExposureLimitItem key={`${limit.asset}-limit`} limit={limit} />
              ))}
          </div>
        </SectionWithHeader>
      </div>
    </Panel>
  );
}

// ============================================================================
// Helper Components
// ============================================================================

interface SectionWithStatusProps {
  title: string;
  status: string;
  lastUpdated: number;
  children?: React.ReactNode;
}

function SectionWithStatus({ title, status, lastUpdated, children }: SectionWithStatusProps) {
  return (
    <PanelSection title={title}>
      <div className="mb-4 flex items-center gap-2">
        <div className={`px-2 py-1 rounded text-xs font-medium ${getStatusColor(status)}`}>
          {status.toUpperCase()}
        </div>
        <span className="text-xs text-muted-foreground">
          Updated {getTimeAgo(lastUpdated)}
        </span>
      </div>
      {children}
    </PanelSection>
  );
}

interface SectionWithHeaderProps {
  title: string;
  count?: number;
  onExpand?: () => void;
  children: React.ReactNode;
}

function SectionWithHeader({ title, count, onExpand, children }: SectionWithHeaderProps) {
  return (
    <PanelSection title={`${title} ${count !== undefined ? `(${count})` : ''}`}>
      {onExpand && (
        <button
          onClick={onExpand}
          className="text-xs text-muted-foreground hover:text-foreground transition-colors"
        >
          <MoreHorizontal className="w-3 h-3 inline" />
        </button>
      )}
      {children}
    </PanelSection>
  );
}

interface StatusCardProps {
  label: string;
  value: string | number;
  change?: number;
  icon: React.ComponentType<{ className?: string }>;
  isRisk?: boolean;
}

function StatusCard({ label, value, change, icon: Icon, isRisk }: StatusCardProps) {
  const isNegative = change !== undefined && change < 0;
  const isPositive = change !== undefined && change > 0;
  
  return (
    <div className="p-3 bg-muted/30 rounded border border-border">
      <div className="flex items-center justify-between mb-1">
        <span className="text-xs text-muted-foreground">{label}</span>
        <Icon className={`w-4 h-4 ${isRisk ? 'text-orange-500' : 'text-blue-500'}`} />
      </div>
      <p className="text-lg font-semibold">{typeof value === 'number' ? formatCurrency(value) : value}</p>
      {change !== undefined && (
        <p className={`text-xs mt-1 ${isNegative ? 'text-red-500' : isPositive ? 'text-green-500' : 'text-muted-foreground'}`}>
          {isNegative ? '↓' : isPositive ? '↑' : ''} {Math.abs(change * 100).toFixed(2)}%
        </p>
      )}
    </div>
  );
}

function ObjectiveItem({ objective }: { objective: Objective }) {
  return (
    <div className="p-3 bg-muted/30 rounded border border-border hover:bg-muted/50 transition-colors">
      <div className="flex items-start justify-between mb-2">
        <div className="flex items-center gap-2">
          <Target className="w-4 h-4 text-blue-500" />
          <span className="text-sm font-medium">{objective.title}</span>
        </div>
        <span className={`text-xs px-2 py-0.5 rounded ${getPriorityColor(objective.priority)}`}>
          {objective.priority}
        </span>
      </div>
      <p className="text-xs text-muted-foreground line-clamp-2">{objective.description}</p>
      <div className="flex items-center gap-4 mt-2">
        <div className="flex-1">
          <div className="flex items-center justify-between mb-1">
            <span className="text-xs text-muted-foreground">Progress</span>
            <span className="text-xs font-medium">{objective.progress}%</span>
          </div>
          <div className="w-full bg-muted rounded-full h-1.5">
            <div
              className="bg-primary h-1.5 rounded-full transition-all"
              style={{ width: `${objective.progress}%` }}
            />
          </div>
        </div>
        <span className={`text-xs px-2 py-0.5 rounded ${getStatusColor(objective.status)}`}>
          {objective.status}
        </span>
      </div>
    </div>
  );
}

function ResearchItem({ research }: { research: Research }) {
  return (
    <div className="p-3 bg-muted/30 rounded border border-border hover:bg-muted/50 transition-colors">
      <div className="flex items-start justify-between mb-2">
        <div className="flex items-center gap-2">
          <BookOpen className="w-4 h-4 text-purple-500" />
          <span className="text-sm font-medium">{research.topic}</span>
        </div>
        <span className={`text-xs px-2 py-0.5 rounded ${getStatusColor(research.status)}`}>
          {research.status}
        </span>
      </div>
      <div className="flex items-center gap-2 mb-2">
        <span className="text-xs text-muted-foreground">Progress</span>
        <span className="text-xs font-medium">{research.progress}%</span>
        <span className="text-xs text-muted-foreground">•</span>
        <span className="text-xs text-muted-foreground">Confidence: {Math.round(research.confidence * 100)}%</span>
      </div>
      {research.findings.length > 0 && research.findings[0] && (
        <div className="text-xs text-muted-foreground mb-1">
          Latest: {research.findings[0].description}
        </div>
      )}
      <div className="flex items-center gap-2">
        {research.relatedMarkets.map(market => (
          <span key={market} className="text-xs px-2 py-0.5 bg-muted rounded border border-border">
            {market}
          </span>
        ))}
      </div>
    </div>
  );
}

function TraderModelItem({ model }: { model: TraderModel }) {
  return (
    <div className="p-3 bg-muted/30 rounded border border-border hover:bg-muted/50 transition-colors">
      <div className="flex items-start justify-between mb-2">
        <div className="flex items-center gap-2">
          <Brain className="w-4 h-4 text-green-500" />
          <span className="text-sm font-medium">Model: {model.modelType}</span>
        </div>
        <span className="text-xs px-2 py-0.5 rounded bg-blue-500/10 text-blue-500">
          {Math.round(model.accuracy * 100)}% accuracy
        </span>
      </div>
      <div className="flex items-center gap-4 mb-2">
        <div className="flex-1">
          <div className="flex items-center justify-between mb-1">
            <span className="text-xs text-muted-foreground">Win Rate</span>
            <span className="text-xs font-medium">{(model.performanceMetrics.winRate * 100).toFixed(0)}%</span>
          </div>
          <div className="flex items-center justify-between mb-1">
            <span className="text-xs text-muted-foreground">Profit Factor</span>
            <span className="text-xs font-medium">{model.performanceMetrics.profitFactor.toFixed(1)}</span>
          </div>
        </div>
        <div className="text-xs text-muted-foreground">
          Trader: {model.traderId}
        </div>
      </div>
      <p className="text-xs text-muted-foreground">
        Updated {getTimeAgo(model.lastUpdated)}
      </p>
    </div>
  );
}

function StrategyItem({ strategy }: { strategy: Strategy }) {
  return (
    <div className="p-3 bg-muted/30 rounded border border-border hover:bg-muted/50 transition-colors">
      <div className="flex items-start justify-between mb-2">
        <div className="flex items-center gap-2">
          <TrendingUp className="w-4 h-4 text-orange-500" />
          <span className="text-sm font-medium">{strategy.name}</span>
        </div>
        <span className={`text-xs px-2 py-0.5 rounded ${getStrategyColor(strategy.status)}`}>
          {strategy.status}
        </span>
      </div>
      <div className="flex items-center gap-4 mb-2">
        <div className="flex-1">
          <div className="flex items-center justify-between mb-1">
            <span className="text-xs text-muted-foreground">Performance</span>
            <span className={`text-xs font-medium ${strategy.performance >= 0 ? 'text-green-500' : 'text-red-500'}`}>
              {strategy.performance >= 0 ? '+' : ''}{(strategy.performance * 100).toFixed(0)}%
            </span>
          </div>
        </div>
        <div>
          <span className={`text-xs px-2 py-0.5 rounded ${getRiskColor(strategy.riskLevel)}`}>
            {strategy.riskLevel}
          </span>
        </div>
      </div>
      <p className="text-xs text-muted-foreground">
        Type: {strategy.type} • Modified {getTimeAgo(strategy.lastModified)}
      </p>
    </div>
  );
}

function OpportunityItem({ opportunity }: { opportunity: Opportunity }) {
  return (
    <div className="p-3 bg-muted/30 rounded border border-border hover:bg-muted/50 transition-colors">
      <div className="flex items-start justify-between mb-2">
        <div className="flex items-center gap-2">
          <Lightbulb className="w-4 h-4 text-yellow-500" />
          <span className="text-sm font-medium">{opportunity.type}</span>
        </div>
        <span className={`text-xs px-2 py-0.5 rounded ${getConfidenceColor(opportunity.confidence)}`}>
          {(opportunity.confidence * 100).toFixed(0)}%
        </span>
      </div>
      <p className="text-xs font-medium mb-1">{opportunity.description}</p>
      <div className="flex items-center gap-3 text-xs text-muted-foreground">
        <span>{opportunity.asset}</span>
        <span>•</span>
        <span>{opportunity.timeframe}</span>
        <span>•</span>
        <span className={opportunity.expectedReturn > 0 ? 'text-green-500' : 'text-red-500'}>
          {(opportunity.expectedReturn * 100).toFixed(1)}% expected
        </span>
      </div>
      <p className="text-xs text-muted-foreground mt-1">
        {opportunity.expiresAt ? `Expires ${getTimeAgo(opportunity.expiresAt)}` : `Created ${getTimeAgo(opportunity.createdAt)}`}
      </p>
    </div>
  );
}

function ConstraintItem({ constraint }: { constraint: Constraint }) {
  return (
    <div className={`p-2 rounded border ${
      constraint.status === 'compliant' 
        ? 'border-green-500/30 bg-green-500/10' 
        : constraint.status === 'warning'
        ? 'border-yellow-500/30 bg-yellow-500/10'
        : 'border-red-500/30 bg-red-500/10'
    }`}>
      <div className="flex items-center gap-2">
        <AlertTriangle className="w-4 h-4" />
        <span className="text-xs font-medium">
          {constraint.type} at {formatCurrency(constraint.limit)}
        </span>
      </div>
      <div className="flex items-center gap-2 mt-1">
        <div className="flex-1">
          <span className="text-xs text-muted-foreground">Current:</span>
        </div>
        <span className={`text-xs font-medium ${
          constraint.status === 'compliant' ? 'text-green-500' : 'text-red-500'
        }`}>
          {formatCurrency(constraint.current)}
        </span>
      </div>
    </div>
  );
}

function ExposureLimitItem({ limit }: { limit: ExposureLimit }) {
  return (
    <div className={`p-2 rounded border ${
      limit.status === 'compliant' 
        ? 'border-green-500/30 bg-green-500/10' 
        : 'border-red-500/30 bg-red-500/10'
    }`}>
      <div className="flex items-center gap-2">
        <Zap className="w-4 h-4" />
        <span className="text-xs font-medium">{limit.asset}</span>
      </div>
      <div className="flex items-center gap-2 mt-1">
        <span className="text-xs text-muted-foreground">
          Limit: {(limit.limit * 100).toFixed(0)}%
        </span>
        <span className={`text-xs font-medium ${
          limit.status === 'compliant' ? 'text-green-500' : 'text-red-500'
        }`}>
          Current: {(limit.current * 100).toFixed(0)}%
        </span>
      </div>
    </div>
  );
}

// ============================================================================
// Helper Functions
// ============================================================================

function getStatusColor(status: string): string {
  switch (status.toLowerCase()) {
    case 'active':
      return 'bg-blue-500/10 text-blue-500';
    case 'completed':
      return 'bg-green-500/10 text-green-500';
    case 'paused':
      return 'bg-yellow-500/10 text-yellow-500';
    case 'error':
      return 'bg-red-500/10 text-red-500';
    case 'low':
      return 'bg-green-500/10 text-green-500';
    case 'medium':
      return 'bg-yellow-500/10 text-yellow-500';
    case 'high':
      return 'bg-orange-500/10 text-orange-500';
    case 'critical':
      return 'bg-red-500/10 text-red-500';
    default:
      return 'bg-gray-500/10 text-gray-500';
  }
}

function getPriorityColor(priority: string): string {
  switch (priority.toLowerCase()) {
    case 'critical':
      return 'bg-red-500 text-white';
    case 'high':
      return 'bg-orange-500 text-white';
    case 'medium':
      return 'bg-yellow-500 text-black';
    case 'low':
      return 'bg-blue-500 text-white';
    default:
      return 'bg-gray-500 text-white';
  }
}

function getStrategyColor(status: string): string {
  switch (status.toLowerCase()) {
    case 'active':
      return 'bg-green-500/10 text-green-500';
    case 'testing':
      return 'bg-yellow-500/10 text-yellow-500';
    case 'deprecated':
      return 'bg-gray-500/10 text-gray-500';
    default:
      return 'bg-blue-500/10 text-blue-500';
  }
}

function getRiskColor(level: string): string {
  switch (level.toLowerCase()) {
    case 'low':
      return 'bg-green-500/10 text-green-500';
    case 'medium':
      return 'bg-yellow-500/10 text-yellow-500';
    case 'high':
      return 'bg-orange-500/10 text-orange-500';
    case 'critical':
      return 'bg-red-500/10 text-red-500';
    default:
      return 'bg-gray-500/10 text-gray-500';
  }
}

function getConfidenceColor(confidence: number): string {
  if (confidence >= 0.8) return 'bg-green-500 text-white';
  if (confidence >= 0.6) return 'bg-yellow-500 text-black';
  return 'bg-orange-500 text-white';
}

function formatCurrency(value: number): string {
  return new Intl.NumberFormat('en-US', {
    style: 'currency',
    currency: 'USD',
    minimumFractionDigits: 0,
    maximumFractionDigits: 0,
  }).format(value);
}

function getTimeAgo(timestamp: number): string {
  const now = Date.now();
  const diff = now - timestamp;

  const seconds = Math.floor(diff / 1000);
  const minutes = Math.floor(seconds / 60);
  const hours = Math.floor(minutes / 60);
  const days = Math.floor(hours / 24);

  if (seconds < 60) {
    return 'just now';
  } else if (minutes < 60) {
    return `${minutes}m ago`;
  } else if (hours < 24) {
    return `${hours}h ago`;
  } else {
    return `${days}d ago`;
  }
}
