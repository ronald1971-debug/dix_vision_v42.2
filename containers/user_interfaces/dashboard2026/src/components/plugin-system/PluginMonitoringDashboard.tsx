/**
 * Plugin Monitoring Dashboard
 * DIX VISION v42.2 - Phase 3: Plugin Preservation
 * 
 * Real-time dashboard for monitoring plugin system including
 * marketplace, development framework, and active plugins.
 */

import React, { useState, useEffect } from 'react';
import { 
  pluginMarketplace,
  pluginDevelopmentFramework,
  pluginMonitoringSystem
} from '@/core/plugin-system';
import {
  Package,
  TrendingUp,
  Activity,
  CheckCircle,
  Star,
  Download,
  Code,
  Settings,
  RefreshCw,
  Cpu,
  HardDrive
} from 'lucide-react';

export function PluginMonitoringDashboard() {
  const [marketplaceStats, setMarketplaceStats] = useState<any>(null);
  const [devProjects, setDevProjects] = useState<any[]>([]);
  const [pluginMetrics, setPluginMetrics] = useState<any[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [autoRefresh, setAutoRefresh] = useState(true);

  useEffect(() => {
    loadDashboardData();
    setIsLoading(false);

    // Start monitoring
    pluginMonitoringSystem.startMonitoring(10000);

    if (autoRefresh) {
      const interval = setInterval(loadDashboardData, 15000);
      return () => clearInterval(interval);
    }

    return () => {
      pluginMonitoringSystem.stopMonitoring();
    };
  }, [autoRefresh]);

  const loadDashboardData = () => {
    const stats = pluginMarketplace.getMarketplaceStatistics();
    const projects = pluginDevelopmentFramework.getAllProjects();
    const metrics = pluginMonitoringSystem.getAllMetrics();

    setMarketplaceStats(stats);
    setDevProjects(projects);
    setPluginMetrics(metrics);
  };

  if (isLoading) {
    return (
      <div className="flex items-center justify-center h-full">
        <RefreshCw className="w-8 h-8 animate-spin text-blue-500" />
        <span className="ml-2 text-sm text-slate-400">Loading plugin metrics...</span>
      </div>
    );
  }

  return (
    <div className="plugin-monitoring-dashboard space-y-4">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-3">
          <Package className="w-6 h-6 text-blue-500" />
          <h2 className="text-lg font-semibold">Plugin Monitoring Dashboard</h2>
        </div>
        <div className="flex items-center gap-2">
          <button
            onClick={() => setAutoRefresh(!autoRefresh)}
            className={`px-3 py-1.5 rounded text-sm ${
              autoRefresh 
                ? 'bg-green-500/20 text-green-500 border border-green-500/20' 
                : 'bg-slate-700 text-slate-400'
            }`}
          >
            {autoRefresh ? 'Auto-Refresh On' : 'Auto-Refresh Off'}
          </button>
          <button
            onClick={loadDashboardData}
            className="p-1.5 bg-slate-700 hover:bg-slate-600 rounded text-slate-300 transition-colors"
          >
            <RefreshCw className="w-4 h-4" />
          </button>
        </div>
      </div>

      {/* Marketplace Statistics */}
      <div className="bg-surface-raised rounded-lg p-4 border border-border">
        <h3 className="text-sm font-medium text-slate-400 mb-3">Marketplace Overview</h3>
        {marketplaceStats && (
          <div className="grid grid-cols-4 gap-4">
            <StatCard
              icon={<Package className="w-5 h-5" />}
              label="Total Plugins"
              value={marketplaceStats.totalPlugins}
              _trend="neutral"
            />
            <StatCard
              icon={<CheckCircle className="w-5 h-5" />}
              label="Verified Plugins"
              value={marketplaceStats.verifiedPlugins}
              _trend="good"
            />
            <StatCard
              icon={<Download className="w-5 h-5" />}
              label="Total Downloads"
              value={marketplaceStats.totalDownloads}
              _trend="good"
            />
            <StatCard
              icon={<Star className="w-5 h-5" />}
              label="Average Rating"
              value={marketplaceStats.averageRating}
              _trend="neutral"
            />
          </div>
        )}
      </div>

      {/* Development Projects */}
      <div className="bg-surface-raised rounded-lg p-4 border border-border">
        <h3 className="text-sm font-medium text-slate-400 mb-3">Development Projects</h3>
        {devProjects.length === 0 ? (
          <div className="text-sm text-slate-500">No active development projects</div>
        ) : (
          <div className="space-y-2">
            {devProjects.map((project) => (
              <div key={project.id} className="flex items-center justify-between p-3 bg-surface rounded border border-border">
                <div className="flex items-center gap-3">
                  <Code className="w-5 h-5 text-slate-400" />
                  <div>
                    <div className="text-sm font-medium">{project.name}</div>
                    <div className="text-xs text-slate-500">{project.category} • v{project.version}</div>
                  </div>
                </div>
                <div className="flex items-center gap-2">
                  <span className={`text-xs px-2 py-1 rounded ${
                    project.status === 'ready' ? 'bg-green-500/20 text-green-500' :
                    project.status === 'testing' ? 'bg-yellow-500/20 text-yellow-500' :
                    'bg-blue-500/20 text-blue-500'
                  }`}>
                    {project.status}
                  </span>
                  <Settings className="w-4 h-4 text-slate-400 cursor-pointer hover:text-slate-300" />
                </div>
              </div>
            ))}
          </div>
        )}
      </div>

      {/* Active Plugin Metrics */}
      <div className="bg-surface-raised rounded-lg p-4 border border-border">
        <h3 className="text-sm font-medium text-slate-400 mb-3">Active Plugin Performance</h3>
        {pluginMetrics.length === 0 ? (
          <div className="text-sm text-slate-500">No active plugin metrics</div>
        ) : (
          <div className="space-y-3">
            {pluginMetrics.map((metrics) => (
              <PluginMetricCard key={metrics.pluginId} metrics={metrics} />
            ))}
          </div>
        )}
      </div>

      {/* System Status */}
      <div className="bg-surface-raised rounded-lg p-4 border border-border">
        <h3 className="text-sm font-medium text-slate-400 mb-3">System Status</h3>
        <div className="flex items-center gap-2">
          <CheckCircle className="w-5 h-5 text-green-500" />
          <span className="text-sm text-green-500">Plugin System Operational</span>
        </div>
      </div>
    </div>
  );
}

function StatCard({ 
  icon, 
  label, 
  value, 
  trend 
}: { 
  icon: React.ReactNode; 
  label: string; 
  value: number;
  _trend: 'good' | 'neutral' | 'error';
}) {
  return (
    <div className="flex flex-col">
      <div className="flex items-center gap-2 mb-1">
        <div className="text-slate-400">{icon}</div>
        <span className="text-xs text-slate-500">{label}</span>
      </div>
      <div className="text-lg font-semibold">{value}</div>
    </div>
  );
}

function PluginMetricCard({ metrics }: { metrics: any }) {
  const healthStatus = metrics.errorRate < 0.05 ? 'healthy' : 'unhealthy';
  const healthColor = healthStatus === 'healthy' ? 'text-green-500' : 'text-red-500';

  return (
    <div className="p-3 bg-surface rounded border border-border">
      <div className="flex items-center justify-between mb-3">
        <div className="text-sm font-medium">{metrics.pluginId}</div>
        <div className={`text-xs ${healthColor}`}>
          {healthStatus.toUpperCase()}
        </div>
      </div>
      <div className="grid grid-cols-4 gap-4">
        <div>
          <div className="flex items-center gap-1 text-xs text-slate-500">
            <Activity className="w-3 h-3" />
            Execution Time
          </div>
          <div className="text-sm font-medium">{metrics.averageExecutionTimeMs.toFixed(0)}ms</div>
        </div>
        <div>
          <div className="flex items-center gap-1 text-xs text-slate-500">
            <HardDrive className="w-3 h-3" />
            Memory
          </div>
          <div className="text-sm font-medium">{metrics.averageMemoryUsageMB.toFixed(1)}MB</div>
        </div>
        <div>
          <div className="flex items-center gap-1 text-xs text-slate-500">
            <TrendingUp className="w-3 h-3" />
            Success Rate
          </div>
          <div className="text-sm font-medium">{(metrics.successRate * 100).toFixed(1)}%</div>
        </div>
        <div>
          <div className="flex items-center gap-1 text-xs text-slate-500">
            <Cpu className="w-3 h-3" />
            Executions
          </div>
          <div className="text-sm font-medium">{metrics.totalExecutions}</div>
        </div>
      </div>
    </div>
  );
}