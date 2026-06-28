/**
 * Resource Monitor
 * DIX VISION v42.2 - Phase 1: Architecture Optimization
 * 
 * Production-grade resource monitoring system for tracking memory usage,
 * bundle sizes, load times, and system performance in real-time.
 */

import React from 'react';
import { moduleRegistry } from './ModuleRegistry';
import { getLoadMetrics, checkLazyLoadHealth } from './LazyLoadSystem';
import { ResourceMetrics } from './ModuleTypes';

interface MemoryInfo {
  usedJSHeapSize: number;
  totalJSHeapSize: number;
  jsHeapSizeLimit: number;
}

interface PerformanceEntry {
  name: string;
  duration: number;
  startTime: number;
  timestamp: number;
}

interface ResourceSnapshot {
  timestamp: number;
  memory: MemoryInfo;
  bundleSize: number;
  activeModules: number;
  loadMetrics: Record<string, { avgLoadTime: number; avgMemory: number }>;
  systemHealth: ReturnType<typeof checkLazyLoadHealth>;
}

class ResourceMonitor {
  private snapshots: ResourceSnapshot[] = [];
  private maxSnapshots = 100; // Keep last 100 snapshots
  private monitoringInterval: number | null = null;
  private isMonitoring = false;
  private performanceEntries: PerformanceEntry[] = [];

  /**
   * Get current memory information
   */
  private getMemoryInfo(): MemoryInfo {
    if (performance.memory) {
      return {
        usedJSHeapSize: performance.memory.usedJSHeapSize,
        totalJSHeapSize: performance.memory.totalJSHeapSize,
        jsHeapSizeLimit: performance.memory.jsHeapSizeLimit
      };
    }

    // Fallback for browsers that don't support performance.memory
    return {
      usedJSHeapSize: 0,
      totalJSHeapSize: 0,
      jsHeapSizeLimit: 0
    };
  }

  /**
   * Convert bytes to MB
   */
  private bytesToMB(bytes: number): number {
    return bytes / (1024 * 1024);
  }

  /**
   * Get current resource snapshot
   */
  private getCurrentSnapshot(): ResourceSnapshot {
    const memory = this.getMemoryInfo();
    const systemMetrics = moduleRegistry.getSystemMetrics();
    const loadMetrics = getLoadMetrics();
    const systemHealth = checkLazyLoadHealth();

    return {
      timestamp: Date.now(),
      memory,
      bundleSize: systemMetrics.loadedBundleSize,
      activeModules: systemMetrics.loadedModules,
      loadMetrics,
      systemHealth
    };
  }

  /**
   * Start resource monitoring
   */
  startMonitoring(intervalMs: number = 5000): void {
    if (this.isMonitoring) {
      console.warn('Resource monitoring already started');
      return;
    }

    console.log(`Starting resource monitoring with ${intervalMs}ms interval`);
    this.isMonitoring = true;

    // Take initial snapshot
    this.takeSnapshot();

    // Set up monitoring interval
    this.monitoringInterval = window.setInterval(() => {
      this.takeSnapshot();
    }, intervalMs);
  }

  /**
   * Stop resource monitoring
   */
  stopMonitoring(): void {
    if (!this.isMonitoring) {
      console.warn('Resource monitoring not started');
      return;
    }

    console.log('Stopping resource monitoring');
    this.isMonitoring = false;

    if (this.monitoringInterval) {
      clearInterval(this.monitoringInterval);
      this.monitoringInterval = null;
    }
  }

  /**
   * Take a resource snapshot
   */
  takeSnapshot(): ResourceSnapshot {
    const snapshot = this.getCurrentSnapshot();
    
    // Add to snapshots array
    this.snapshots.push(snapshot);
    
    // Maintain max snapshots limit
    if (this.snapshots.length > this.maxSnapshots) {
      this.snapshots.shift();
    }

    return snapshot;
  }

  /**
   * Get recent snapshots
   */
  getRecentSnapshots(count: number = 10): ResourceSnapshot[] {
    return this.snapshots.slice(-count);
  }

  /**
   * Get current resource metrics
   */
  getCurrentMetrics(): ResourceMetrics {
    const snapshot = this.getCurrentSnapshot();
    const systemMetrics = moduleRegistry.getSystemMetrics();

    return {
      bundleSize: snapshot.bundleSize,
      memoryUsage: this.bytesToMB(snapshot.memory.usedJSHeapSize),
      loadTime: snapshot.systemHealth.avgLoadTime,
      activeModules: snapshot.activeModules,
      totalModules: systemMetrics.totalModules
    };
  }

  /**
   * Get resource usage trend
   */
  getResourceTrend(windowMs: number = 60000): {
    memoryTrend: 'increasing' | 'decreasing' | 'stable';
    bundleSizeTrend: 'increasing' | 'decreasing' | 'stable';
    memoryChange: number;
    bundleSizeChange: number;
  } {
    const cutoffTime = Date.now() - windowMs;
    const recentSnapshots = this.snapshots.filter(s => s.timestamp >= cutoffTime);

    if (recentSnapshots.length < 2) {
      return {
        memoryTrend: 'stable',
        bundleSizeTrend: 'stable',
        memoryChange: 0,
        bundleSizeChange: 0
      };
    }

    const oldest = recentSnapshots[0];
    const newest = recentSnapshots[recentSnapshots.length - 1];

    const memoryChange = this.bytesToMB(newest.memory.usedJSHeapSize) - this.bytesToMB(oldest.memory.usedJSHeapSize);
    const bundleSizeChange = newest.bundleSize - oldest.bundleSize;

    const memoryTrend = Math.abs(memoryChange) < 5 ? 'stable' : (memoryChange > 0 ? 'increasing' : 'decreasing');
    const bundleSizeTrend = Math.abs(bundleSizeChange) < 50 ? 'stable' : (bundleSizeChange > 0 ? 'increasing' : 'decreasing');

    return {
      memoryTrend,
      bundleSizeTrend,
      memoryChange,
      bundleSizeChange
    };
  }

  /**
   * Get performance summary
   */
  getPerformanceSummary(): {
    averageMemoryUsage: number;
    peakMemoryUsage: number;
    averageLoadTime: number;
    slowLoadingModules: string[];
    systemHealth: 'healthy' | 'degraded' | 'unhealthy';
    recommendations: string[];
  } {
    if (this.snapshots.length === 0) {
      return {
        averageMemoryUsage: 0,
        peakMemoryUsage: 0,
        averageLoadTime: 0,
        slowLoadingModules: [],
        systemHealth: 'unhealthy',
        recommendations: ['No monitoring data available']
      };
    }

    const memoryUsages = this.snapshots.map(s => this.bytesToMB(s.memory.usedJSHeapSize));
    const averageMemoryUsage = memoryUsages.reduce((sum, mem) => sum + mem, 0) / memoryUsages.length;
    const peakMemoryUsage = Math.max(...memoryUsages);

    const loadTimes = Object.values(this.snapshots[this.snapshots.length - 1].loadMetrics)
      .map(m => m.avgLoadTime);
    const averageLoadTime = loadTimes.length > 0 ? 
      loadTimes.reduce((sum, time) => sum + time, 0) / loadTimes.length : 0;

    const latestHealth = this.snapshots[this.snapshots.length - 1].systemHealth;
    const slowLoadingModules = latestHealth.slowModules;

    // Determine system health
    let systemHealth: 'healthy' | 'degraded' | 'unhealthy';
    if (!latestHealth.healthy && slowLoadingModules.length > 5) {
      systemHealth = 'unhealthy';
    } else if (!latestHealth.healthy || slowLoadingModules.length > 2) {
      systemHealth = 'degraded';
    } else {
      systemHealth = 'healthy';
    }

    // Generate recommendations
    const recommendations: string[] = [];
    
    if (averageMemoryUsage > 500) {
      recommendations.push('Memory usage is high. Consider unloading unused modules.');
    }
    
    if (averageLoadTime > 1000) {
      recommendations.push('Average load time is high. Consider optimizing bundle sizes or implementing caching.');
    }
    
    if (slowLoadingModules.length > 0) {
      recommendations.push(`Slow loading modules detected: ${slowLoadingModules.join(', ')}. Consider code splitting or lazy loading optimization.`);
    }
    
    if (systemHealth === 'unhealthy') {
      recommendations.push('System health is critical. Immediate optimization required.');
    }

    return {
      averageMemoryUsage,
      peakMemoryUsage,
      averageLoadTime,
      slowLoadingModules,
      systemHealth,
      recommendations
    };
  }

  /**
   * Record a performance entry
   */
  recordPerformance(name: string, duration: number, startTime: number = performance.now()): void {
    this.performanceEntries.push({
      name,
      duration,
      startTime,
      timestamp: Date.now()
    });

    // Keep only last 1000 entries
    if (this.performanceEntries.length > 1000) {
      this.performanceEntries.shift();
    }
  }

  /**
   * Get performance entries by name
   */
  getPerformanceEntries(name: string, limit: number = 10): PerformanceEntry[] {
    return this.performanceEntries
      .filter(entry => entry.name === name)
      .slice(-limit);
  }

  /**
   * Get average performance for a specific operation
   */
  getAveragePerformance(name: string): number {
    const entries = this.getPerformanceEntries(name);
    if (entries.length === 0) return 0;

    return entries.reduce((sum, entry) => sum + entry.duration, 0) / entries.length;
  }

  /**
   * Export monitoring data for analysis
   */
  exportMonitoringData(): {
    snapshots: ResourceSnapshot[];
    performanceEntries: PerformanceEntry[];
    summary: ReturnType<typeof this.getPerformanceSummary>;
    trend: ReturnType<typeof this.getResourceTrend>;
  } {
    return {
      snapshots: [...this.snapshots],
      performanceEntries: [...this.performanceEntries],
      summary: this.getPerformanceSummary(),
      trend: this.getResourceTrend()
    };
  }

  /**
   * Clear monitoring data
   */
  clearMonitoringData(): void {
    this.snapshots = [];
    this.performanceEntries = [];
    console.log('Monitoring data cleared');
  }

  /**
   * Check if monitoring is active
   */
  isMonitoringActive(): boolean {
    return this.isMonitoring;
  }
}

// Singleton instance
export const resourceMonitor = new ResourceMonitor();

/**
 * Hook for using resource monitor in React components
 */
export function useResourceMonitor(intervalMs: number = 5000) {
  React.useEffect(() => {
    resourceMonitor.startMonitoring(intervalMs);
    return () => resourceMonitor.stopMonitoring();
  }, [intervalMs]);

  return {
    getCurrentMetrics: () => resourceMonitor.getCurrentMetrics(),
    getPerformanceSummary: () => resourceMonitor.getPerformanceSummary(),
    getResourceTrend: () => resourceMonitor.getResourceTrend(),
    getRecentSnapshots: (count?: number) => resourceMonitor.getRecentSnapshots(count),
    exportMonitoringData: () => resourceMonitor.exportMonitoringData(),
    isMonitoring: () => resourceMonitor.isMonitoringActive()
  };
}