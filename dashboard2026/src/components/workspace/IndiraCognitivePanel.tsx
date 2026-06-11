/**
 * INDIRA Cognitive Panel
 * 
 * Visualizes INDIRA's cognitive processes including portfolio reasoning,
 * risk reasoning, trade reasoning, and confidence analysis
 * Provides transparency into INDIRA's decision-making process
 */

import { useState } from 'react';
import { Panel, PanelSection } from '../agent/Panel';
import type {
  ReasoningProcess,
  ConfidenceAnalysis,
  ConfidenceFactor,
} from '@/types/workspace';
import {
  Brain,
  ChevronDown,
  ChevronRight,
  TrendingUp,
  Shield,
  DollarSign,
  Activity,
  Gauge,
  Sparkles,
} from 'lucide-react';

interface IndiraCognitivePanelProps {
  className?: string;
}

export function IndiraCognitivePanel({ className }: IndiraCognitivePanelProps) {
  const [expandedProcesses, setExpandedProcesses] = useState<Set<string>>(new Set(['portfolio-reasoning']));
  const [activeReasoningTab, setActiveReasoningTab] = useState<'portfolio' | 'risk' | 'trade'>('portfolio');

  // Mock reasoning processes
  const mockPortfolioReasoning: ReasoningProcess = {
    id: 'portfolio-reasoning-1',
    type: 'portfolio',
    status: 'active',
    steps: [
      {
        id: 'step-1',
        description: 'Analyze current portfolio allocation across assets',
        data: { BTC: 0.60, ETH: 0.25, USDT: 0.15 },
        logic: 'Portfolio allocation analysis based on market conditions',
        timestamp: Date.now() - 300000,
      },
      {
        id: 'step-2',
        description: 'Calculate portfolio risk metrics including VaR and beta',
        data: { VaR: 0.05, beta: 1.2, sharpe: 2.1 },
        logic: 'Risk-adjusted return calculation for optimization',
        timestamp: Date.now() - 240000,
      },
      {
        id: 'step-3',
        description: 'Evaluate rebalancing opportunities based on market signals',
        data: { rebalanceBTC: true, rebalanceETH: false, rebalanceUSDT: false },
        logic: 'Market signal analysis for optimal allocation',
        timestamp: Date.now() - 180000,
      },
      {
        id: 'step-4',
        description: 'Determine optimal rebalancing strategy and timing',
        data: { timing: 'immediate', strategy: 'gradual' },
        logic: 'Execution optimization considering market impact',
        timestamp: Date.now() - 120000,
      },
    ],
    conclusion: 'Portfolio should be rebalanced to reduce BTC exposure from 60% to 50% and increase USDT allocation for better risk management while maintaining expected returns',
    confidence: 0.78,
    timestamp: Date.now(),
  };

  const mockRiskReasoning: ReasoningProcess = {
    id: 'risk-reasoning-1',
    type: 'risk',
    status: 'active',
    steps: [
      {
        id: 'step-1',
        description: 'Assess current market volatility regime',
        data: { regime: 'high', vix: 28, btcVol: 0.65 },
        logic: 'Volatility regime classification for risk adjustment',
        timestamp: Date.now() - 180000,
      },
      {
        id: 'step-2',
        description: 'Evaluate portfolio concentration risk',
        data: { btcConcentration: 0.60, limit: 0.50, status: 'violation' },
        logic: 'Concentration risk assessment against limits',
        timestamp: Date.now() - 150000,
      },
      {
        id: 'step-3',
        description: 'Analyze correlation matrix for diversification benefits',
        data: { btcEthCorrelation: 0.85, btcUsdtCorrelation: 0.0 },
        logic: 'Correlation analysis for diversification optimization',
        timestamp: Date.now() - 120000,
      },
      {
        id: 'step-4',
        description: 'Calculate position-specific risk contributions',
        data: { btcRisk: 0.45, ethRisk: 0.30, usdtRisk: 0.25 },
        logic: 'Risk attribution analysis for position sizing',
        timestamp: Date.now() - 90000,
      },
    ],
    conclusion: 'High market volatility and BTC concentration violation require immediate portfolio rebalancing to reduce exposure',
    confidence: 0.82,
    timestamp: Date.now(),
  };

  const mockTradeReasoning: ReasoningProcess = {
    id: 'trade-reasoning-1',
    type: 'trade',
    status: 'completed',
    steps: [
      {
        id: 'step-1',
        description: 'Identify trade opportunity based on momentum signal',
        data: { asset: 'BTC', signal: 'LONG', strength: 0.75 },
        logic: 'Momentum signal detection for trade entry',
        timestamp: Date.now() - 600000,
      },
      {
        id: 'step-2',
        description: 'Calculate optimal position size based on risk parameters',
        data: { size: 2.5, riskPerTrade: 0.02, stopLoss: 41500 },
        logic: 'Risk-based position sizing calculation',
        timestamp: Date.now() - 540000,
      },
      {
        id: 'step-3',
        description: 'Determine entry price and execution timing',
        data: { entryPrice: 42350, timing: 'immediate' },
        logic: 'Market impact analysis for optimal execution',
        timestamp: Date.now() - 480000,
      },
      {
        id: 'step-4',
        description: 'Set target price and risk management parameters',
        data: { targetPrice: 44000, takeProfit: 0.038, stopLoss: 41500 },
        logic: 'Risk-reward ratio optimization',
        timestamp: Date.now() - 420000,
      },
      {
        id: 'step-5',
        description: 'Execute trade and monitor for adjustments',
        data: { executed: true, executionPrice: 42345, slippage: -0.01 },
        logic: 'Trade execution and initial monitoring',
        timestamp: Date.now() - 360000,
      },
    ],
    conclusion: 'Trade executed successfully at $42,345 with 2.5 BTC, expecting 3.8% return with 1.9% risk',
    confidence: 0.85,
    timestamp: Date.now() - 360000,
  };

  const mockConfidenceAnalysis: ConfidenceAnalysis = {
    overall: 0.78,
    portfolio: 0.78,
    risk: 0.82,
    trades: 0.85,
    factors: [
      {
        factor: 'Market Data Quality',
        impact: 0.15,
        confidence: 0.92,
        trend: 'stable',
      },
      {
        factor: 'Model Accuracy',
        impact: 0.30,
        confidence: 0.85,
        trend: 'improving',
      },
      {
        factor: 'Volatility Regime',
        impact: 0.20,
        confidence: 0.75,
        trend: 'deteriorating',
      },
      {
        factor: 'Liquidity Conditions',
        impact: 0.10,
        confidence: 0.88,
        trend: 'stable',
      },
      {
        factor: 'Correlation Stability',
        impact: 0.15,
        confidence: 0.70,
        trend: 'deteriorating',
      },
      {
        factor: 'Regulatory Environment',
        impact: 0.10,
        confidence: 0.80,
        trend: 'stable',
      },
    ],
    lastUpdated: Date.now(),
  };

  const activeProcess =
    activeReasoningTab === 'portfolio'
      ? mockPortfolioReasoning
      : activeReasoningTab === 'risk'
      ? mockRiskReasoning
      : mockTradeReasoning;

  const toggleProcessExpansion = (processId: string) => {
    setExpandedProcesses(prev => {
      const newSet = new Set(prev);
      if (newSet.has(processId)) {
        newSet.delete(processId);
      } else {
        newSet.add(processId);
      }
      return newSet;
    });
  };

  return (
    <Panel
      title="INDIRA Cognitive Process"
      className={className}
    >
      <div className="space-y-4">
        {/* Overall Confidence Score */}
        <SectionWithStatus status={mockConfidenceAnalysis.overall}>
          <div className="grid grid-cols-3 gap-4">
            <ConfidenceMetric
              label="Portfolio"
              value={mockConfidenceAnalysis.portfolio}
              icon={TrendingUp}
            />
            <ConfidenceMetric
              label="Risk"
              value={mockConfidenceAnalysis.risk}
              icon={Shield}
            />
            <ConfidenceMetric
              label="Trades"
              value={mockConfidenceAnalysis.trades}
              icon={DollarSign}
            />
          </div>
        </SectionWithStatus>

        {/* Reasoning Process Tabs */}
        <PanelSection title="Active Reasoning">
          <div className="flex gap-2 mb-4">
            <ReasoningTab
              active={activeReasoningTab === 'portfolio'}
              label="Portfolio"
              icon={Activity}
              onClick={() => setActiveReasoningTab('portfolio')}
              status={mockPortfolioReasoning.status}
            />
            <ReasoningTab
              active={activeReasoningTab === 'risk'}
              label="Risk"
              icon={Shield}
              onClick={() => setActiveReasoningTab('risk')}
              status={mockRiskReasoning.status}
            />
            <ReasoningTab
              active={activeReasoningTab === 'trade'}
              label="Trade"
              icon={DollarSign}
              onClick={() => setActiveReasoningTab('trade')}
              status={mockTradeReasoning.status}
            />
          </div>

          {/* Active Reasoning Process */}
          <ReasoningProcessView
            process={activeProcess}
            isExpanded={expandedProcesses.has(activeProcess.id)}
            onToggle={() => toggleProcessExpansion(activeProcess.id)}
          />
        </PanelSection>

        {/* Confidence Factors */}
        <PanelSection title="Confidence Factors">
          <div className="space-y-2">
            {mockConfidenceAnalysis.factors.map(factor => (
              <ConfidenceFactorItem key={factor.factor} factor={factor} />
            ))}
          </div>
        </PanelSection>
      </div>
    </Panel>
  );
}

// ============================================================================
// Helper Components
// ============================================================================

interface SectionWithStatusProps {
  status: number;
  children: React.ReactNode;
}

function SectionWithStatus({ status, children }: SectionWithStatusProps) {
  return (
    <PanelSection title="Overall Confidence">
      <div className="flex items-center gap-3 mb-3">
        <Gauge className={`w-5 h-5 ${getConfidenceIconColor(status)}`} />
        <span className="text-2xl font-bold">{(status * 100).toFixed(0)}%</span>
        <span className={`text-xs px-2 py-0.5 rounded ${getConfidenceColor(status)}`}>
          {getConfidenceLabel(status)}
        </span>
      </div>
      {children}
    </PanelSection>
  );
}

interface ConfidenceMetricProps {
  label: string;
  value: number;
  icon: React.ComponentType<{ className?: string }>;
}

function ConfidenceMetric({ label, value, icon: Icon }: ConfidenceMetricProps) {
  return (
    <div className="p-3 bg-muted/30 rounded border border-border">
      <div className="flex items-center gap-2 mb-1">
        <Icon className={`w-4 h-4 ${getConfidenceIconColor(value)}`} />
        <span className="text-xs text-muted-foreground">{label}</span>
      </div>
      <span className="text-lg font-semibold">{(value * 100).toFixed(0)}%</span>
      <div className="mt-2">
        <div className="w-full bg-muted rounded-full h-1.5">
          <div
            className={`h-1.5 rounded-full transition-all ${getConfidenceBarColor(value)}`}
            style={{ width: `${value * 100}%` }}
          />
        </div>
      </div>
    </div>
  );
}

interface ReasoningTabProps {
  active: boolean;
  label: string;
  icon: React.ComponentType<{ className?: string }>;
  onClick: () => void;
  status: string;
}

function ReasoningTab({ active, label, icon: Icon, onClick, status }: ReasoningTabProps) {
  return (
    <button
      onClick={onClick}
      className={`flex items-center gap-2 px-3 py-2 rounded-lg border transition-colors ${
        active
          ? 'bg-primary text-primary-foreground border-primary'
          : 'bg-muted border-border hover:bg-muted/80'
      }`}
    >
      <Icon className="w-4 h-4" />
      <span className="text-sm font-medium">{label}</span>
      <span className={`w-2 h-2 rounded-full ${getStatusDotColor(status)}`} />
    </button>
  );
}

interface ReasoningProcessViewProps {
  process: ReasoningProcess;
  isExpanded: boolean;
  onToggle: () => void;
}

function ReasoningProcessView({ process, isExpanded, onToggle }: ReasoningProcessViewProps) {
  return (
    <div className="p-3 bg-muted/30 rounded border border-border">
      <div className="flex items-start justify-between mb-2">
        <div className="flex items-center gap-2">
          <Brain className={`w-4 h-4 ${process.status === 'active' ? 'text-blue-500' : 'text-green-500'}`} />
          <span className="text-sm font-medium">
            {process.type.charAt(0).toUpperCase() + process.type.slice(1)} Reasoning
          </span>
          <span className={`text-xs px-2 py-0.5 rounded ${getStatusColor(process.status)}`}>
            {process.status}
          </span>
        </div>
        <button
          onClick={onToggle}
          className="text-muted-foreground hover:text-foreground transition-colors"
        >
          {isExpanded ? <ChevronDown className="w-4 h-4" /> : <ChevronRight className="w-4 h-4" />}
        </button>
      </div>

      {isExpanded && (
        <div className="mt-3 space-y-3">
          {/* Reasoning Steps */}
          <div className="space-y-2">
            {process.steps.map((step, index) => (
              <div key={step.id} className="relative pl-6">
                {/* Timeline line */}
                {index < process.steps.length - 1 && (
                  <div className="absolute left-2 top-4 w-0.5 h-full bg-border" />
                )}
                {/* Step indicator */}
                <div className="absolute left-0 top-0 w-4 h-4 rounded-full bg-primary" />
                
                <div className="text-sm mb-1">
                  <span className="font-medium">Step {index + 1}:</span> {step.description}
                </div>
                <div className="text-xs text-muted-foreground mb-1">
                  Logic: {step.logic}
                </div>
                <div className="p-2 bg-background rounded border border-border text-xs">
                  <span className="font-medium">Data:</span> {JSON.stringify(step.data)}
                </div>
                <div className="text-xs text-muted-foreground mt-1">
                  {getTimeAgo(step.timestamp)}
                </div>
              </div>
            ))}
          </div>

          {/* Conclusion */}
          <div className="mt-4 p-3 bg-primary/10 rounded border border-primary/20">
            <div className="flex items-center gap-2 mb-1">
              <Sparkles className="w-4 h-4 text-primary" />
              <span className="text-sm font-medium">Conclusion</span>
            </div>
            <p className="text-sm">{process.conclusion}</p>
            <div className="flex items-center gap-2 mt-2">
              <span className="text-xs text-muted-foreground">Confidence:</span>
              <span className={`text-xs font-medium ${getConfidenceTextColor(process.confidence)}`}>
                {(process.confidence * 100).toFixed(0)}%
              </span>
              <div className="flex-1">
                <div className="w-full bg-muted rounded-full h-1.5">
                  <div
                    className={`h-1.5 rounded-full ${getConfidenceBarColor(process.confidence)}`}
                    style={{ width: `${process.confidence * 100}%` }}
                  />
                </div>
              </div>
            </div>
          </div>
        </div>
      )}

      {!isExpanded && (
        <div className="mt-2 text-xs text-muted-foreground">
          {process.steps.length} steps • {getTimeAgo(process.timestamp)}
        </div>
      )}
    </div>
  );
}

function ConfidenceFactorItem({ factor }: { factor: ConfidenceFactor }) {
  return (
    <div className="p-2 bg-muted/30 rounded border border-border">
      <div className="flex items-start justify-between mb-1">
        <span className="text-xs font-medium">{factor.factor}</span>
        <div className="flex items-center gap-2">
          <span className={`text-xs ${getTrendColor(factor.trend)}`}>
            {factor.trend === 'improving' ? '↑' : factor.trend === 'deteriorating' ? '↓' : '→'}
          </span>
          <span className={`text-xs font-medium ${getConfidenceTextColor(factor.confidence)}`}>
            {(factor.confidence * 100).toFixed(0)}%
          </span>
        </div>
      </div>
      <div className="flex items-center gap-3">
        <div className="flex-1">
          <div className="flex items-center justify-between mb-1">
            <span className="text-xs text-muted-foreground">Impact</span>
            <span className="text-xs">{(factor.impact * 100).toFixed(0)}%</span>
          </div>
          <div className="w-full bg-muted rounded-full h-1">
            <div
              className="bg-primary h-1 rounded-full"
              style={{ width: `${factor.impact * 100}%` }}
            />
          </div>
        </div>
      </div>
    </div>
  );
}

// ============================================================================
// Helper Functions
// ============================================================================

function getConfidenceIconColor(confidence: number): string {
  if (confidence >= 0.8) return 'text-green-500';
  if (confidence >= 0.6) return 'text-yellow-500';
  return 'text-red-500';
}

function getConfidenceColor(confidence: number): string {
  if (confidence >= 0.8) return 'bg-green-500/10 text-green-500';
  if (confidence >= 0.6) return 'bg-yellow-500/10 text-yellow-500';
  return 'bg-red-500/10 text-red-500';
}

function getConfidenceBarColor(confidence: number): string {
  if (confidence >= 0.8) return 'bg-green-500';
  if (confidence >= 0.6) return 'bg-yellow-500';
  return 'bg-red-500';
}

function getConfidenceTextColor(confidence: number): string {
  if (confidence >= 0.8) return 'text-green-500';
  if (confidence >= 0.6) return 'text-yellow-500';
  return 'text-red-500';
}

function getConfidenceLabel(confidence: number): string {
  if (confidence >= 0.8) return 'High';
  if (confidence >= 0.6) return 'Medium';
  return 'Low';
}

function getStatusDotColor(status: string): string {
  switch (status) {
    case 'active':
      return 'bg-blue-500';
    case 'completed':
      return 'bg-green-500';
    case 'paused':
      return 'bg-yellow-500';
    case 'error':
      return 'bg-red-500';
    default:
      return 'bg-gray-500';
  }
}

function getStatusColor(status: string): string {
  switch (status) {
    case 'active':
      return 'bg-blue-500/10 text-blue-500';
    case 'completed':
      return 'bg-green-500/10 text-green-500';
    case 'paused':
      return 'bg-yellow-500/10 text-yellow-500';
    case 'error':
      return 'bg-red-500/10 text-red-500';
    default:
      return 'bg-gray-500/10 text-gray-500';
  }
}

function getTrendColor(trend: string): string {
  switch (trend) {
    case 'improving':
      return 'text-green-500';
    case 'deteriorating':
      return 'text-red-500';
    default:
      return 'text-gray-500';
  }
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
