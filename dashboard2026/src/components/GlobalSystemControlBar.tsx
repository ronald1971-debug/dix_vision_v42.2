/**
 * Global System Control Bar
 * 
 * Unified control surface displaying all 8 system states for DIXVISION v42.2
 * Provides complete system visibility and control at all times
 */

import { useState, useEffect } from 'react';
import { Shield, Activity, Cpu, Database, Zap, AlertTriangle, Power } from 'lucide-react';
import { ModeRibbon } from '@/components/ModeRibbon';
import { AutonomyRibbon } from '@/components/AutonomyRibbon';
import { KillSwitchPill } from '@/components/KillSwitchPill';
import { TradingStatusPill } from '@/components/TradingStatusPill';

interface SystemStatus {
  systemMode: 'MANUAL' | 'SEMI_AUTO' | 'FULL_AUTO';
  capitalMode: 'CONSERVATIVE' | 'STANDARD' | 'AGGRESSIVE' | 'CUSTOM';
  riskState: 'CRITICAL' | 'HIGH' | 'MEDIUM' | 'LOW';
  governanceState: 'ACTIVE' | 'PASSIVE' | 'MAINTENANCE';
  indiraStatus: 'ONLINE' | 'OFFLINE' | 'ERROR';
  dyonStatus: 'ONLINE' | 'OFFLINE' | 'ERROR';
  executionStatus: 'ACTIVE' | 'INACTIVE' | 'ERROR';
  killSwitchArmed: boolean;
}

interface GlobalSystemControlBarProps {
  className?: string;
}

export function GlobalSystemControlBar({ className }: GlobalSystemControlBarProps) {
  const [status, setStatus] = useState<SystemStatus>({
    systemMode: 'MANUAL',
    capitalMode: 'STANDARD',
    riskState: 'LOW',
    governanceState: 'ACTIVE',
    indiraStatus: 'ONLINE',
    dyonStatus: 'ONLINE',
    executionStatus: 'ACTIVE',
    killSwitchArmed: false,
  });

  // Simulate real-time updates (replace with actual WebSocket)
  useEffect(() => {
    const interval = setInterval(() => {
      // In production, this would come from WebSocket /ws/system/status
      setStatus(prev => ({
        ...prev,
        riskState: Math.random() > 0.9 ? 'HIGH' : 'LOW',
      }));
    }, 5000);

    return () => clearInterval(interval);
  }, []);

  const getRiskColor = (risk: string) => {
    switch (risk) {
      case 'CRITICAL': return 'text-red-500 bg-red-500/10 border-red-500/50';
      case 'HIGH': return 'text-orange-500 bg-orange-500/10 border-orange-500/50';
      case 'MEDIUM': return 'text-yellow-500 bg-yellow-500/10 border-yellow-500/50';
      case 'LOW': return 'text-green-500 bg-green-500/10 border-green-500/50';
      default: return 'text-slate-500 bg-slate-500/10 border-slate-500/50';
    }
  };

  const getStatusColor = (agentStatus: string) => {
    switch (agentStatus) {
      case 'ONLINE': return 'text-green-500 bg-green-500/10 border-green-500/50';
      case 'OFFLINE': return 'text-slate-500 bg-slate-500/10 border-slate-500/50';
      case 'ERROR': return 'text-red-500 bg-red-500/10 border-red-500/50';
      default: return 'text-slate-500 bg-slate-500/10 border-slate-500/50';
    }
  };

  const getGovernanceColor = (governance: string) => {
    switch (governance) {
      case 'ACTIVE': return 'text-blue-500 bg-blue-500/10 border-blue-500/50';
      case 'PASSIVE': return 'text-yellow-500 bg-yellow-500/10 border-yellow-500/50';
      case 'MAINTENANCE': return 'text-purple-500 bg-purple-500/10 border-purple-500/50';
      default: return 'text-slate-500 bg-slate-500/10 border-slate-500/50';
    }
  };

  return (
    <div className={`flex items-center gap-4 px-4 py-2 border-b border-border bg-surface ${className}`}>
      {/* System Mode */}
      <div className="flex items-center gap-2">
        <Shield className="w-4 h-4 text-blue-500" />
        <ModeRibbon />
      </div>

      {/* Capital Mode */}
      <div className="flex items-center gap-2">
        <Zap className="w-4 h-4 text-purple-500" />
        <AutonomyRibbon />
      </div>

      {/* Risk State */}
      <div className={`flex items-center gap-2 px-3 py-1 rounded border ${getRiskColor(status.riskState)}`}>
        <AlertTriangle className="w-4 h-4" />
        <span className="text-xs font-medium">RISK: {status.riskState}</span>
      </div>

      {/* Governance State */}
      <div className={`flex items-center gap-2 px-3 py-1 rounded border ${getGovernanceColor(status.governanceState)}`}>
        <Database className="w-4 h-4" />
        <span className="text-xs font-medium">GOV: {status.governanceState}</span>
      </div>

      {/* INDIRA Status */}
      <div className={`flex items-center gap-2 px-3 py-1 rounded border ${getStatusColor(status.indiraStatus)}`}>
        <Activity className="w-4 h-4" />
        <span className="text-xs font-medium">INDIRA: {status.indiraStatus}</span>
      </div>

      {/* DYON Status */}
      <div className={`flex items-center gap-2 px-3 py-1 rounded border ${getStatusColor(status.dyonStatus)}`}>
        <Cpu className="w-4 h-4" />
        <span className="text-xs font-medium">DYON: {status.dyonStatus}</span>
      </div>

      {/* Execution Status */}
      <div className={`flex items-center gap-2 px-3 py-1 rounded border ${getStatusColor(status.executionStatus)}`}>
        <Power className="w-4 h-4" />
        <span className="text-xs font-medium">EXEC: {status.executionStatus}</span>
      </div>

      {/* Trading Status */}
      <TradingStatusPill />

      {/* Kill Switch */}
      <KillSwitchPill />
    </div>
  );
}
