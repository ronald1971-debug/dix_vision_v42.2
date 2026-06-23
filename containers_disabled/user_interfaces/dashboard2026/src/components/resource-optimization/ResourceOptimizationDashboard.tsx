/**
 * Resource Optimization Dashboard
 * DIX VISION v42.2 - Phase 2: Resource Optimization
 * 
 * Real-time dashboard for monitoring and controlling all resource
 * optimization systems including memory, CPU, network, and plugins.
 */

import React, { useState, useEffect } from 'react';
import { 
  memoryManager,
  cpuOptimizer,
  networkOptimizer,
  pluginConsolidator
} from '@/core/resource-optimization';
import { moduleRegistry } from '@/core/modular-architecture/ModuleRegistry';
import { resourceMonitor } from '@/core/modular-architecture/ResourceMonitor';
import { 
  Activity, 
  Cpu, 
  Database, 
  Network, 
  Zap, 
  AlertTriangle,
  CheckCircle,
  TrendingUp,
  TrendingDown,
  Settings,
  RefreshCw,
  Trash2,
  Download
} from 'lucide-react';

interface DashboardMetrics {
  memory: {
    currentMemory: number;
    memoryPressure: string;
    detectedLeaks: number;
    cleanupStrategies: number;
  };
  cpu: {
    totalWorkers: number;
    busyWorkers: number;
    queueLength: number;
    tasksCompleted: number;
    averageExecutionTime: number;
    totalErrors: number;
  };
  network: {
    cacheSize: number;
    cacheEntries: number;
    bandwidthQuality: string;
    offlineMode: boolean;
  };
  plugins: {
    originalPlugins: number;
    consolidatedPlugins: number;
    reductionPercent: number;
    preservedCapabilities: number;
  };
  system: {
    bundleSize: number;
    memoryUsage: number;
    loadTime: number;
    activeModules: number;
    totalModules: number;
  };
}

export function ResourceOptimizationDashboard() {
  const [metrics, setMetrics] = useState<DashboardMetrics | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [autoRefresh, setAutoRefresh] = useState(true);
  const [refreshInterval, setRefreshInterval] = useState<NodeJS.Timeout | null>(null);

  // Load initial metrics
  useEffect(() => {
    loadMetrics();
    setIsLoading(false);

    // Set up auto-refresh
    if (autoRefresh) {
      const interval = setInterval(loadMetrics, 5000); // Refresh every 5 seconds
      setRefreshInterval(interval);
    }

    return () => {
      if (refreshInterval) {
        clearInterval(refreshInterval);
      }
    };
  }, [autoRefresh]);

  const loadMetrics = () => {
    const memoryStats = memoryManager.getMemoryStats();
    const cpuStats = cpuOptimizer.getCPUStats();
    const networkStats = networkOptimizer.getCacheStats();
    const pluginStats = pluginConsolidator.getConsolidationStats();
    const systemMetrics = resourceMonitor.getCurrentMetrics();

    setMetrics({
      memory: {
        currentMemory: memoryStats.currentMemory,
        memoryPressure: memoryStats.memoryPressure.level,
        detectedLeaks: memoryStats.detectedLeaks,
        cleanupStrategies: memoryStats.cleanupStrategies
      },
      cpu: {
        totalWorkers: cpuStats.totalWorkers,
        busyWorkers: cpuStats.busyWorkers,
        queueLength: cpuStats.queueLength,
        tasksCompleted: cpuStats.tasksCompleted,
        averageExecutionTime: cpuStats.averageExecutionTime,
        totalErrors: cpuStats.totalErrors
      },
      network: {
        cacheSize: networkStats.size,
        cacheEntries: networkStats.entries,
        bandwidthQuality: networkStats.bandwidthQuality,
        offlineMode: networkStats.offlineMode
      },
      plugins: {
        originalPlugins: pluginStats.originalPlugins,
        consolidatedPlugins: pluginStats.consolidatedPlugins,
        reductionPercent: pluginStats.reductionPercent,
        preservedCapabilities: pluginStats.preservedCapabilities
      },
      system: {
        bundleSize: systemMetrics.bundleSize,
        memoryUsage: systemMetrics.memoryUsage,
        loadTime: systemMetrics.loadTime,
        activeModules: systemMetrics.activeModules,
        totalModules: systemMetrics.totalModules
      }
    });
  };

  const handleForceCleanup = (level: 'normal' | 'aggressive' | 'emergency') => {
    memoryManager.forceCleanup(level);
    loadMetrics();
  };

  const handleClearCache = () => {
    networkOptimizer.clearCache();
    loadMetrics();
  };

  const handleConsolidatePlugins = async () => {
    try {
      await pluginConsolidator.consolidate();
      loadMetrics();
    } catch (error) {
      console.error('Plugin consolidation failed:', error);
    }
  };

  const formatBytes = (bytes: number): string => {
    if (bytes === 0) return '0 B';
    const k = 1024;
    const sizes = ['B', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return Math.round(bytes / Math.pow(k, i) * 100) / 100 + ' ' + sizes[i];
  };

  const formatTime = (ms: number): string => {
    if (ms < 1000) return `${Math.round(ms)}ms`;
    if (ms < 60000) return `${Math.round(ms / 1000)}s`;
    return `${Math.round(ms / 60000)}m`;
  };

  if (isLoading || !metrics) {
    return (
      <div className="flex items-center justify-center h-full">
        <RefreshCw className="w-8 h-8 animate-spin text-blue-500" />
        <span className="ml-2 text-sm text-slate-400">Loading resource metrics...</span>
      </div>
    );
  }

  return (
    <div className="resource-optimization-dashboard space-y-4">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-3">
          <Activity className="w-6 h-6 text-blue-500" />
          <h2 className="text-lg font-semibold">Resource Optimization Dashboard</h2>
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
            onClick={loadMetrics}
            className="p-1.5 bg-slate-700 hover:bg-slate-600 rounded text-slate-300 transition-colors"
          >
            <RefreshCw className="w-4 h-4" />
          </button>
        </div>
      </div>

      {/* System Overview */}
      <div className="bg-surface-raised rounded-lg p-4 border border-border">
        <h3 className="text-sm font-medium text-slate-400 mb-3">System Overview</h3>
        <div className="grid grid-cols-4 gap-4">
          <MetricCard
            icon={<Database className="w-5 h-5" />}
            label="Bundle Size"
            value={formatBytes(metrics.system.bundleSize * 1024)}
            trend={metrics.system.bundleSize < 2000 ? 'good' : 'warning'}
          />
          <MetricCard
            icon={<Activity className="w-5 h-5" />}
            label="Memory Usage"
            value={`${metrics.system.memoryUsage.toFixed(1)} MB`}
            trend={metrics.system.memoryUsage < 300 ? 'good' : 'warning'}
          />
          <MetricCard
            icon={<Zap className="w-5 h-5" />}
            label="Load Time"
            value={formatTime(metrics.system.loadTime)}
            trend={metrics.system.loadTime < 1000 ? 'good' : 'warning'}
          />
          <MetricCard
            icon={<Database className="w-5 h-5" />}
            label="Active Modules"
            value={`${metrics.system.activeModules}/${metrics.system.totalModules}`}
            trend={metrics.system.activeModules < 10 ? 'good' : 'warning'}
          />
        </div>
      </div>

      {/* Memory Management */}
      <div className="bg-surface-raised rounded-lg p-4 border border-border">
        <div className="flex items-center justify-between mb-3">
          <h3 className="text-sm font-medium text-slate-400">Memory Management</h3>
          <div className="flex items-center gap-2">
            {metrics.memory.detectedLeaks > 0 && (
              <span className="flex items-center gap-1 text-xs text-red-500">
                <AlertTriangle className="w-3 h-3" />
                {metrics.memory.detectedLeaks} Leaks
              </span>
            )}
            <span className={`text-xs px-2 py-1 rounded ${
              metrics.memory.memoryPressure === 'normal' ? 'bg-green-500/20 text-green-500' :
              metrics.memory.memoryPressure === 'moderate' ? 'bg-yellow-500/20 text-yellow-500' :
              metrics.memory.memoryPressure === 'high' ? 'bg-orange-500/20 text-orange-500' :
              'bg-red-500/20 text-red-500'
            }`}>
              {metrics.memory.memoryPressure} Pressure
            </span>
          </div>
        </div>
        <div className="grid grid-cols-3 gap-4 mb-4">
          <div>
            <div className="text-xs text-slate-500">Memory Usage</div>
            <div className="text-lg font-semibold">{formatBytes(metrics.memory.currentMemory)}</div>
          </div>
          <div>
            <div className="text-xs text-slate-500">Cleanup Strategies</div>
            <div className="text-lg font-semibold">{metrics.memory.cleanupStrategies}</div>
          </div>
          <div>
            <div className="text-xs text-slate-500">Detected Leaks</div>
            <div className="text-lg font-semibold">{metrics.memory.detectedLeaks}</div>
          </div>
        </div>
        <div className="flex gap-2">
          <button
            onClick={() => handleForceCleanup('normal')}
            className="flex items-center gap-1 px-3 py-1.5 bg-blue-500 hover:bg-blue-600 rounded text-sm text-white transition-colors"
          >
            <RefreshCw className="w-4 h-4" />
            Normal Cleanup
          </button>
          <button
            onClick={() => handleForceCleanup('aggressive')}
            className="flex items-center gap-1 px-3 py-1.5 bg-yellow-500 hover:bg-yellow-600 rounded text-sm text-white transition-colors"
          >
            <RefreshCw className="w-4 h-4" />
            Aggressive Cleanup
          </button>
          <button
            onClick={() => handleForceCleanup('emergency')}
            className="flex items-center gap-1 px-3 py-1.5 bg-red-500 hover:bg-red-600 rounded text-sm text-white transition-colors"
          >
            <AlertTriangle className="w-4 h-4" />
            Emergency
          </button>
        </div>
      </div>

      {/* CPU Optimization */}
      <div className="bg-surface-raised rounded-lg p-4 border border-border">
        <div className="flex items-center justify-between mb-3">
          <h3 className="text-sm font-medium text-slate-400">CPU Optimization</h3>
          <span className={`text-xs px-2 py-1 rounded ${
            metrics.cpu.busyWorkers === 0 ? 'bg-green-500/20 text-green-500' :
            metrics.cpu.busyWorkers < metrics.cpu.totalWorkers / 2 ? 'bg-yellow-500/20 text-yellow-500' :
            'bg-red-500/20 text-red-500'
          }`}>
            {metrics.cpu.busyWorkers}/{metrics.cpu.totalWorkers} Workers Busy
          </span>
        </div>
        <div className="grid grid-cols-4 gap-4 mb-4">
          <div>
            <div className="text-xs text-slate-500">Tasks Completed</div>
            <div className="text-lg font-semibold">{metrics.cpu.tasksCompleted}</div>
          </div>
          <div>
            <div className="text-xs text-slate-500">Queue Length</div>
            <div className="text-lg font-semibold">{metrics.cpu.queueLength}</div>
          </div>
          <div>
            <div className="text-xs text-slate-500">Avg Execution</div>
            <div className="text-lg font-semibold">{formatTime(metrics.cpu.averageExecutionTime)}</div>
          </div>
          <div>
            <div className="text-xs text-slate-500">Errors</div>
            <div className="text-lg font-semibold text-red-500">{metrics.cpu.totalErrors}</div>
          </div>
        </div>
      </div>

      {/* Network Optimization */}
      <div className="bg-surface-raised rounded-lg p-4 border border-border">
        <div className="flex items-center justify-between mb-3">
          <h3 className="text-sm font-medium text-slate-400">Network Optimization</h3>
          <div className="flex items-center gap-2">
            {metrics.network.offlineMode && (
              <span className="flex items-center gap-1 text-xs text-red-500">
                <Network className="w-3 h-3" />
                Offline
              </span>
            )}
            <span className={`text-xs px-2 py-1 rounded ${
              metrics.network.bandwidthQuality === 'high' ? 'bg-green-500/20 text-green-500' :
              metrics.network.bandwidthQuality === 'medium' ? 'bg-yellow-500/20 text-yellow-500' :
              'bg-red-500/20 text-red-500'
            }`}>
              {metrics.network.bandwidthQuality} Quality
            </span>
          </div>
        </div>
        <div className="grid grid-cols-3 gap-4 mb-4">
          <div>
            <div className="text-xs text-slate-500">Cache Size</div>
            <div className="text-lg font-semibold">{formatBytes(metrics.network.cacheSize)}</div>
          </div>
          <div>
            <div className="text-xs text-slate-500">Cache Entries</div>
            <div className="text-lg font-semibold">{metrics.network.cacheEntries}</div>
          </div>
          <div>
            <div className="text-xs text-slate-500">Hit Rate</div>
            <div className="text-lg font-semibold">0%</div>
          </div>
        </div>
        <button
          onClick={handleClearCache}
          className="flex items-center gap-1 px-3 py-1.5 bg-slate-700 hover:bg-slate-600 rounded text-sm text-slate-300 transition-colors"
        >
          <Trash2 className="w-4 h-4" />
          Clear Cache
        </button>
      </div>

      {/* Plugin Consolidation */}
      <div className="bg-surface-raised rounded-lg p-4 border border-border">
        <div className="flex items-center justify-between mb-3">
          <h3 className="text-sm font-medium text-slate-400">Plugin Consolidation</h3>
          <span className="flex items-center gap-1 text-xs text-green-500">
            <CheckCircle className="w-3 h-3" />
            {metrics.plugins.reductionPercent}% Reduction
          </span>
        </div>
        <div className="grid grid-cols-3 gap-4 mb-4">
          <div>
            <div className="text-xs text-slate-500">Original Plugins</div>
            <div className="text-lg font-semibold">{metrics.plugins.originalPlugins}</div>
          </div>
          <div>
            <div className="text-xs text-slate-500">Consolidated</div>
            <div className="text-lg font-semibold">{metrics.plugins.consolidatedPlugins}</div>
          </div>
          <div>
            <div className="text-xs text-slate-500">Preserved Capabilities</div>
            <div className="text-lg font-semibold">{metrics.plugins.preservedCapabilities}</div>
          </div>
        </div>
        <button
          onClick={handleConsolidatePlugins}
          className="flex items-center gap-1 px-3 py-1.5 bg-blue-500 hover:bg-blue-600 rounded text-sm text-white transition-colors"
        >
          <Settings className="w-4 h-4" />
          Run Consolidation
        </button>
      </div>

      {/* Overall Health Status */}
      <div className="bg-surface-raised rounded-lg p-4 border border-border">
        <h3 className="text-sm font-medium text-slate-400 mb-3">System Health Status</h3>
        <div className="flex items-center gap-2">
          <CheckCircle className="w-5 h-5 text-green-500" />
          <span className="text-sm text-green-500">All Systems Operational</span>
        </div>
      </div>
    </div>
  );
}

function MetricCard({ 
  icon, 
  label, 
  value, 
  trend 
}: { 
  icon: React.ReactNode; 
  label: string; 
  value: string; 
  trend: 'good' | 'warning' | 'error';
}) {
  const trendColors = {
    good: 'text-green-500',
    warning: 'text-yellow-500',
    error: 'text-red-500'
  };

  const trendIcons = {
    good: <TrendingDown className="w-3 h-3" />,
    warning: <TrendingUp className="w-3 h-3" />,
    error: <AlertTriangle className="w-3 h-3" />
  };

  return (
    <div className="flex flex-col">
      <div className="flex items-center gap-2 mb-1">
        <div className="text-slate-400">{icon}</div>
        <span className="text-xs text-slate-500">{label}</span>
      </div>
      <div className="flex items-center gap-2">
        <span className="text-lg font-semibold">{value}</span>
        <span className={trendColors[trend]}>{trendIcons[trend]}</span>
      </div>
    </div>
  );
}