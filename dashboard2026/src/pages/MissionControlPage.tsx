/**
 * Mission Control Page
 * 
 * Single pane of glass for complete DIXVISION v42.2 system overview
 * Provides visibility into System, Market, Portfolio, Risk, Agent, Opportunities, and Threats
 */

import { useState, useEffect } from 'react';
import { Panel } from '@/components/agent/Panel';
import { Clock } from 'lucide-react';

interface MissionControlProps {
  className?: string;
}

interface SystemStatus {
  engineHealth: {
    intelligence: { status: string; uptime: number; errors: number };
    learning: { status: string; uptime: number; errors: number };
    execution: { status: string; uptime: number; errors: number };
    governance: { status: string; uptime: number; errors: number };
  };
  services: { name: string; status: string; uptime: number }[];
}

interface MarketStatus {
  marketsOpen: boolean;
  volatilityIndex: number;
  liquidityIndex: number;
  activeAlerts: number;
}

interface PortfolioStatus {
  totalValue: number;
  dailyPnL: number;
  riskExposure: number;
  marginUsage: number;
}

interface RiskStatus {
  riskLevel: 'CRITICAL' | 'HIGH' | 'MEDIUM' | 'LOW';
  riskLimitUsage: number;
  drawdownStatus: string;
  hazardAlerts: number;
}

interface AgentStatus {
  indira: { status: string; currentTask: string; taskQueue: number };
  dyon: { status: string; currentTask: string; taskQueue: number };
  learningProgress: number;
}

interface Opportunities {
  trading: number;
  research: number;
  strategies: number;
  upgrades: number;
}

interface Threats {
  riskWarnings: number;
  systemAlerts: number;
  governanceIssues: number;
  securityEvents: number;
}

export function MissionControlPage({ className }: MissionControlProps) {
  const [systemStatus, setSystemStatus] = useState<SystemStatus | null>(null);
  const [marketStatus, setMarketStatus] = useState<MarketStatus | null>(null);
  const [portfolioStatus, setPortfolioStatus] = useState<PortfolioStatus | null>(null);
  const [riskStatus, setRiskStatus] = useState<RiskStatus | null>(null);
  const [agentStatus, setAgentStatus] = useState<AgentStatus | null>(null);
  const [opportunities, setOpportunities] = useState<Opportunities | null>(null);
  const [threats, setThreats] = useState<Threats | null>(null);

  // Simulate data fetching (replace with actual API calls)
  useEffect(() => {
    const interval = setInterval(() => {
      setSystemStatus({
        engineHealth: {
          intelligence: { status: 'HEALTHY', uptime: 7200, errors: 0 },
          learning: { status: 'HEALTHY', uptime: 7200, errors: 0 },
          execution: { status: 'HEALTHY', uptime: 7200, errors: 0 },
          governance: { status: 'HEALTHY', uptime: 7200, errors: 0 },
        },
        services: [
          { name: 'WebSocket', status: 'ACTIVE', uptime: 7200 },
          { name: 'Redis', status: 'ACTIVE', uptime: 7200 },
          { name: 'PostgreSQL', status: 'ACTIVE', uptime: 7200 },
        ],
      });

      setMarketStatus({
        marketsOpen: true,
        volatilityIndex: 15.3,
        liquidityIndex: 82.1,
        activeAlerts: 2,
      });

      setPortfolioStatus({
        totalValue: 1250000,
        dailyPnL: 15700,
        riskExposure: 0.15,
        marginUsage: 0.25,
      });

      setRiskStatus({
        riskLevel: 'LOW',
        riskLimitUsage: 45,
        drawdownStatus: 'WITHIN_LIMITS',
        hazardAlerts: 0,
      });

      setAgentStatus({
        indira: { status: 'ONLINE', currentTask: 'market_research', taskQueue: 3 },
        dyon: { status: 'ONLINE', currentTask: 'code_analysis', taskQueue: 2 },
        learningProgress: 72,
      });

      setOpportunities({
        trading: 5,
        research: 8,
        strategies: 3,
        upgrades: 1,
      });

      setThreats({
        riskWarnings: 0,
        systemAlerts: 1,
        governanceIssues: 0,
        securityEvents: 0,
      });
    }, 1000);

    return () => clearInterval(interval);
  }, []);

  const getStatusColor = (status: string) => {
    if (status === 'HEALTHY' || status === 'ACTIVE' || status === 'ONLINE') {
      return 'text-green-500';
    }
    if (status === 'DEGRADED' || status === 'WARNING') {
      return 'text-yellow-500';
    }
    return 'text-red-500';
  };

  const getRiskLevelColor = (level: string) => {
    switch (level) {
      case 'CRITICAL': return 'text-red-500';
      case 'HIGH': return 'text-orange-500';
      case 'MEDIUM': return 'text-yellow-500';
      case 'LOW': return 'text-green-500';
      default: return 'text-slate-500';
    }
  };

  return (
    <div className={`mission-control-page flex flex-col h-full ${className}`}>
      {/* Header */}
      <div className="flex items-center justify-between px-6 py-4 border-b border-border bg-surface">
        <div>
          <h1 className="text-2xl font-semibold tracking-tight">Mission Control</h1>
          <p className="text-sm text-slate-400 mt-1">Single pane of glass - complete system overview</p>
        </div>
        <div className="flex items-center gap-2">
          <div className="text-xs text-slate-500">
            <Clock className="w-4 h-4 inline mr-1" />
            Last updated: {new Date().toLocaleTimeString()}
          </div>
        </div>
      </div>

      {/* Main Content - 7-Panel Grid */}
      <div className="flex-1 p-6 overflow-auto">
        <div className="grid grid-cols-3 gap-4">
          {/* Row 1 */}
          <SystemStatusPanel status={systemStatus} getStatusColor={getStatusColor} />
          <MarketStatusPanel status={marketStatus} />
          <PortfolioStatusPanel status={portfolioStatus} />

          {/* Row 2 */}
          <RiskStatusPanel status={riskStatus} getRiskLevelColor={getRiskLevelColor} />
          <AgentStatusPanel status={agentStatus} />
          <OpportunitiesPanel opportunities={opportunities} />
          <ThreatsPanel threats={threats} />
        </div>
      </div>
    </div>
  );
}

// ============================================================================
// System Status Panel
// ============================================================================

interface SystemStatusPanelProps {
  status: SystemStatus | null;
  getStatusColor: (status: string) => string;
}

function SystemStatusPanel({ status, getStatusColor }: SystemStatusPanelProps) {
  if (!status) {
    return (
      <Panel title="System Status" className="col-span-1">
        <div className="flex items-center justify-center h-full text-slate-500">
          Loading...
        </div>
      </Panel>
    );
  }

  return (
    <Panel title="System Status" className="col-span-1">
      <div className="space-y-4">
        {/* Engine Health */}
        <div>
          <h4 className="text-xs font-medium text-slate-500 mb-2">Engine Health</h4>
          <div className="space-y-2">
            <div className="flex items-center justify-between">
              <span className="text-xs text-slate-400">Intelligence</span>
              <span className={`text-xs font-medium ${getStatusColor(status.engineHealth.intelligence.status)}`}>
                {status.engineHealth.intelligence.status}
              </span>
            </div>
            <div className="flex items-center justify-between">
              <span className="text-xs text-slate-400">Learning</span>
              <span className={`text-xs font-medium ${getStatusColor(status.engineHealth.learning.status)}`}>
                {status.engineHealth.learning.status}
              </span>
            </div>
            <div className="flex items-center justify-between">
              <span className="text-xs text-slate-400">Execution</span>
              <span className={`text-xs font-medium ${getStatusColor(status.engineHealth.execution.status)}`}>
                {status.engineHealth.execution.status}
              </span>
            </div>
            <div className="flex items-center justify-between">
              <span className="text-xs text-slate-400">Governance</span>
              <span className={`text-xs font-medium ${getStatusColor(status.engineHealth.governance.status)}`}>
                {status.engineHealth.governance.status}
              </span>
            </div>
          </div>
        </div>

        {/* Services */}
        <div>
          <h4 className="text-xs font-medium text-slate-500 mb-2">Services</h4>
          <div className="space-y-1">
            {status.services.map((service, idx) => (
              <div key={idx} className="flex items-center justify-between">
                <span className="text-xs text-slate-400">{service.name}</span>
                <span className={`text-xs font-medium ${getStatusColor(service.status)}`}>
                  {service.status}
                </span>
              </div>
            ))}
          </div>
        </div>
      </div>
    </Panel>
  );
}

// ============================================================================
// Market Status Panel
// ============================================================================

interface MarketStatusPanelProps {
  status: MarketStatus | null;
}

function MarketStatusPanel({ status }: MarketStatusPanelProps) {
  if (!status) {
    return (
      <Panel title="Market Status">
        <div className="flex items-center justify-center h-full text-slate-500">
          Loading...
        </div>
      </Panel>
    );
  }

  return (
    <Panel title="Market Status">
      <div className="space-y-4">
        <div className="flex items-center justify-between">
          <span className="text-xs text-slate-400">Markets Open</span>
          <span className={status.marketsOpen ? 'text-green-500' : 'text-red-500'}>
            {status.marketsOpen ? 'OPEN' : 'CLOSED'}
          </span>
        </div>
        <div className="flex items-center justify-between">
          <span className="text-xs text-slate-400">Volatility Index</span>
          <span className="text-xs font-medium">{status.volatilityIndex.toFixed(1)}</span>
        </div>
        <div className="flex items-center justify-between">
          <span className="text-xs text-slate-400">Liquidity Index</span>
          <span className="text-xs font-medium">{status.liquidityIndex.toFixed(1)}</span>
        </div>
        <div className="flex items-center justify-between">
          <span className="text-xs text-slate-400">Active Alerts</span>
          <span className={`text-xs font-medium ${status.activeAlerts > 0 ? 'text-orange-500' : 'text-slate-400'}`}>
            {status.activeAlerts}
          </span>
        </div>
      </div>
    </Panel>
  );
}

// ============================================================================
// Portfolio Status Panel
// ============================================================================

interface PortfolioStatusPanelProps {
  status: PortfolioStatus | null;
}

function PortfolioStatusPanel({ status }: PortfolioStatusPanelProps) {
  if (!status) {
    return (
      <Panel title="Portfolio Status">
        <div className="flex items-center justify-center h-full text-slate-500">
          Loading...
        </div>
      </Panel>
    );
  }

  const pnlColor = status.dailyPnL >= 0 ? 'text-green-500' : 'text-red-500';

  return (
    <Panel title="Portfolio Status">
      <div className="space-y-4">
        <div>
          <span className="text-xs text-slate-400">Total Value</span>
          <span className="text-lg font-semibold">${status.totalValue.toLocaleString()}</span>
        </div>
        <div>
          <span className="text-xs text-slate-400">Daily PnL</span>
          <span className={`text-lg font-semibold ${pnlColor}`}>
            {status.dailyPnL >= 0 ? '+' : ''}{status.dailyPnL.toLocaleString()}
          </span>
        </div>
        <div className="flex items-center justify-between">
          <span className="text-xs text-slate-400">Risk Exposure</span>
          <span className="text-xs font-medium">{(status.riskExposure * 100).toFixed(1)}%</span>
        </div>
        <div className="flex items-center justify-between">
          <span className="text-xs text-slate-400">Margin Usage</span>
          <span className="text-xs font-medium">{(status.marginUsage * 100).toFixed(1)}%</span>
        </div>
      </div>
    </Panel>
  );
}

// ============================================================================
// Risk Status Panel
// ============================================================================

interface RiskStatusPanelProps {
  status: RiskStatus | null;
  getRiskLevelColor: (level: string) => string;
}

function RiskStatusPanel({ status, getRiskLevelColor }: RiskStatusPanelProps) {
  if (!status) {
    return (
      <Panel title="Risk Status">
        <div className="flex items-center justify-center h-full text-slate-500">
          Loading...
        </div>
      </Panel>
    );
  }

  return (
    <Panel title="Risk Status">
      <div className="space-y-4">
        <div className="flex items-center justify-between">
          <span className="text-xs text-slate-400">Risk Level</span>
          <span className={`text-sm font-bold ${getRiskLevelColor(status.riskLevel)}`}>
            {status.riskLevel}
          </span>
        </div>
        <div className="flex items-center justify-between">
          <span className="text-xs text-slate-400">Risk Limit Usage</span>
          <span className="text-xs font-medium">{status.riskLimitUsage}%</span>
        </div>
        <div className="flex items-center justify-between">
          <span className="text-xs text-slate-400">Drawdown Status</span>
          <span className={status.drawdownStatus === 'WITHIN_LIMITS' ? 'text-green-500' : 'text-orange-500'}>
            {status.drawdownStatus}
          </span>
        </div>
        <div className="flex items-center justify-between">
          <span className="text-xs text-slate-400">Hazard Alerts</span>
          <span className={`text-xs font-medium ${status.hazardAlerts > 0 ? 'text-orange-500' : 'text-slate-400'}`}>
            {status.hazardAlerts}
          </span>
        </div>
      </div>
    </Panel>
  );
}

// ============================================================================
// Agent Status Panel
// ============================================================================

interface AgentStatusPanelProps {
  status: AgentStatus | null;
}

function AgentStatusPanel({ status }: AgentStatusPanelProps) {
  if (!status) {
    return (
      <Panel title="Agent Status">
        <div className="flex items-center justify-center h-full text-slate-500">
          Loading...
        </div>
      </Panel>
    );
  }

  const getStatusColor = (agentStatus: string) => {
    if (agentStatus === 'ONLINE') return 'text-green-500';
    if (agentStatus === 'OFFLINE') return 'text-slate-500';
    return 'text-red-500';
  };

  return (
    <Panel title="Agent Status">
      <div className="space-y-4">
        {/* INDIRA */}
        <div>
          <div className="flex items-center justify-between mb-1">
            <span className="text-xs text-slate-400">INDIRA</span>
            <span className={`text-xs font-medium ${getStatusColor(status.indira.status)}`}>
              {status.indira.status}
            </span>
          </div>
          <div className="text-xs text-slate-500 truncate">{status.indira.currentTask}</div>
          <div className="text-xs text-slate-400 mt-1">Queue: {status.indira.taskQueue} tasks</div>
        </div>

        {/* DYON */}
        <div>
          <div className="flex items-center justify-between mb-1">
            <span className="text-xs text-slate-400">DYON</span>
            <span className={`text-xs font-medium ${getStatusColor(status.dyon.status)}`}>
              {status.dyon.status}
            </span>
          </div>
          <div className="text-xs text-slate-500 truncate">{status.dyon.currentTask}</div>
          <div className="text-xs text-slate-400 mt-1">Queue: {status.dyon.taskQueue} tasks</div>
        </div>

        {/* Learning Progress */}
        <div>
          <div className="flex items-center justify-between mb-1">
            <span className="text-xs text-slate-400">Learning Progress</span>
            <span className="text-xs font-medium">{status.learningProgress}%</span>
          </div>
          <div className="w-full bg-slate-700 rounded-full h-2">
            <div 
              className="bg-blue-500 rounded-full h-2 transition-all"
              style={{ width: `${status.learningProgress}%` }}
            />
          </div>
        </div>
      </div>
    </Panel>
  );
}

// ============================================================================
// Opportunities Panel
// ============================================================================

interface OpportunitiesPanelProps {
  opportunities: Opportunities | null;
}

function OpportunitiesPanel({ opportunities }: OpportunitiesPanelProps) {
  if (!opportunities) {
    return (
      <Panel title="Opportunities">
        <div className="flex items-center justify-center h-full text-slate-500">
          Loading...
        </div>
      </Panel>
    );
  }

  return (
    <Panel title="Opportunities">
      <div className="space-y-3">
        <div className="flex items-center justify-between">
          <span className="text-xs text-slate-400">Trading</span>
          <span className="text-xs font-medium text-green-500">{opportunities.trading}</span>
        </div>
        <div className="flex items-center justify-between">
          <span className="text-xs text-slate-400">Research</span>
          <span className="text-xs font-medium text-blue-500">{opportunities.research}</span>
        </div>
        <div className="flex items-center justify-between">
          <span className="text-xs text-slate-400">Strategies</span>
          <span className="text-xs font-medium text-purple-500">{opportunities.strategies}</span>
        </div>
        <div className="flex items-center justify-between">
          <span className="text-xs text-slate-400">Upgrades</span>
          <span className="text-xs font-medium text-orange-500">{opportunities.upgrades}</span>
        </div>
      </div>
    </Panel>
  );
}

// ============================================================================
// Threats Panel
// ============================================================================

interface ThreatsPanelProps {
  threats: Threats | null;
}

function ThreatsPanel({ threats }: ThreatsPanelProps) {
  if (!threats) {
    return (
      <Panel title="Threats">
        <div className="flex items-center justify-center h-full text-slate-500">
          Loading...
        </div>
      </Panel>
    );
  }

  return (
    <Panel title="Threats">
      <div className="space-y-3">
        <div className="flex items-center justify-between">
          <span className="text-xs text-slate-400">Risk Warnings</span>
          <span className={`text-xs font-medium ${threats.riskWarnings > 0 ? 'text-orange-500' : 'text-slate-400'}`}>
            {threats.riskWarnings}
          </span>
        </div>
        <div className="flex items-center justify-between">
          <span className="text-xs text-slate-400">System Alerts</span>
          <span className={`text-xs font-medium ${threats.systemAlerts > 0 ? 'text-yellow-500' : 'text-slate-400'}`}>
            {threats.systemAlerts}
          </span>
        </div>
        <div className="flex items-center justify-between">
          <span className="text-xs text-slate-400">Governance Issues</span>
          <span className={`text-xs font-medium ${threats.governanceIssues > 0 ? 'text-purple-500' : 'text-slate-400'}`}>
            {threats.governanceIssues}
          </span>
        </div>
        <div className="flex items-center justify-between">
          <span className="text-xs text-slate-400">Security Events</span>
          <span className={`text-xs font-medium ${threats.securityEvents > 0 ? 'text-red-500' : 'text-slate-400'}`}>
            {threats.securityEvents}
          </span>
        </div>
      </div>
    </Panel>
  );
}
