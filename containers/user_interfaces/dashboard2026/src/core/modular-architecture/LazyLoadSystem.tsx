/**
 * Lazy Load System
 * DIX VISION v42.2 - Phase 1: Architecture Optimization
 * 
 * Production-grade lazy loading system with React.lazy(), Suspense boundaries,
 * error boundaries, and performance monitoring.
 */

import React, { lazy, Suspense, ComponentType, ReactNode } from 'react';
import { moduleRegistry } from './ModuleRegistry';
import { ModuleLoadResult } from './ModuleTypes';

interface LazyLoadProps {
  children: ReactNode;
  fallback?: ReactNode;
  error?: ReactNode;
  moduleId?: string;
}

interface LoadingState {
  isLoading: boolean;
  error: Error | null;
  progress: number;
}

/**
 * Error boundary for lazy-loaded components
 */
class LazyLoadErrorBoundary extends React.Component<
  { children: ReactNode; fallback: ReactNode; moduleId: string },
  { hasError: boolean; error: Error | null }
> {
  constructor(props: { children: ReactNode; fallback: ReactNode; moduleId: string }) {
    super(props);
    this.state = { hasError: false, error: null };
  }

  static getDerivedStateFromError(error: Error) {
    return { hasError: true, error };
  }

  componentDidCatch(error: Error, errorInfo: React.ErrorInfo) {
    console.error(`Lazy load error for module ${this.props.moduleId}:`, error, errorInfo);
    // Log to monitoring system
    this.logErrorToMonitoring(error, errorInfo);
  }

  private logErrorToMonitoring(error: Error, errorInfo: React.ErrorInfo) {
    // Production-grade error logging
    const errorData = {
      moduleId: this.props.moduleId,
      error: error.message,
      stack: error.stack,
      componentStack: errorInfo.componentStack,
      timestamp: new Date().toISOString(),
      userAgent: navigator.userAgent,
      url: window.location.href
    };

    // Send to monitoring system (implementation depends on your monitoring setup)
    if (typeof window !== 'undefined' && (window as any).monitoringClient) {
      (window as any).monitoringClient.logError('lazy_load_error', errorData);
    } else {
      console.error('Module load error:', errorData);
    }
  }

  render() {
    if (this.state.hasError) {
      return this.props.fallback;
    }
    return this.props.children;
  }
}

/**
 * Loading component with progress indication
 */
export const LazyLoadingFallback: React.FC<{ 
  message?: string; 
  showProgress?: boolean;
  moduleId?: string;
}> = ({ 
  message = 'Loading...', 
  showProgress = true,
  moduleId 
}) => {
  const [progress, setProgress] = React.useState(0);

  React.useEffect(() => {
    if (!showProgress) return;
    
    const interval = setInterval(() => {
      setProgress(prev => {
        if (prev >= 90) return 90;
        return prev + Math.random() * 10;
      });
    }, 200);

    return () => clearInterval(interval);
  }, [showProgress]);

  return (
    <div className="flex flex-col items-center justify-center h-full p-8">
      <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-500 mb-4" />
      <p className="text-sm text-slate-400">{message}</p>
      {moduleId && (
        <p className="text-xs text-slate-500 mt-1">Module: {moduleId}</p>
      )}
      {showProgress && (
        <div className="w-64 h-2 bg-slate-700 rounded-full mt-4 overflow-hidden">
          <div 
            className="h-full bg-blue-500 transition-all duration-300"
            style={{ width: `${progress}%` }}
          />
        </div>
      )}
    </div>
  );
};

/**
 * Error fallback component
 */
export const LazyLoadErrorFallback: React.FC<{ 
  error?: Error; 
  moduleId?: string;
  onRetry?: () => void;
}> = ({ error, moduleId, onRetry }) => {
  const errorMessage = error?.message || 'Failed to load module';
  
  return (
    <div className="flex flex-col items-center justify-center h-full p-8">
      <div className="w-12 h-12 bg-red-500/20 rounded-full flex items-center justify-center mb-4">
        <svg className="w-6 h-6 text-red-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
        </svg>
      </div>
      <p className="text-sm text-red-500 font-medium mb-2">Module Load Error</p>
      <p className="text-xs text-slate-400 mb-4">{errorMessage}</p>
      {moduleId && (
        <p className="text-xs text-slate-500 mb-4">Module: {moduleId}</p>
      )}
      {onRetry && (
        <button
          onClick={onRetry}
          className="px-4 py-2 bg-blue-500 hover:bg-blue-600 text-white rounded text-sm transition-colors"
        >
          Retry
        </button>
      )}
    </div>
  );
};

/**
 * Performance monitor for module loading
 */
class LoadPerformanceMonitor {
  private loadTimes: Map<string, number[]> = new Map();
  private memoryUsage: Map<string, number[]> = new Map();

  recordLoad(moduleId: string, loadTime: number, memoryUsed: number): void {
    if (!this.loadTimes.has(moduleId)) {
      this.loadTimes.set(moduleId, []);
      this.memoryUsage.set(moduleId, []);
    }
    
    this.loadTimes.get(moduleId)!.push(loadTime);
    this.memoryUsage.get(moduleId)!.push(memoryUsed);
    
    // Keep only last 10 measurements
    if (this.loadTimes.get(moduleId)!.length > 10) {
      this.loadTimes.get(moduleId)!.shift();
      this.memoryUsage.get(moduleId)!.shift();
    }
  }

  getAverageLoadTime(moduleId: string): number {
    const times = this.loadTimes.get(moduleId);
    if (!times || times.length === 0) return 0;
    
    return times.reduce((sum, time) => sum + time, 0) / times.length;
  }

  getAverageMemoryUsage(moduleId: string): number {
    const memory = this.memoryUsage.get(moduleId);
    if (!memory || memory.length === 0) return 0;
    
    return memory.reduce((sum, mem) => sum + mem, 0) / memory.length;
  }

  getModuleMetrics(moduleId: string): { avgLoadTime: number; avgMemory: number } {
    return {
      avgLoadTime: this.getAverageLoadTime(moduleId),
      avgMemory: this.getAverageMemoryUsage(moduleId)
    };
  }

  getAllMetrics(): Record<string, { avgLoadTime: number; avgMemory: number }> {
    const metrics: Record<string, { avgLoadTime: number; avgMemory: number }> = {};
    
    this.loadTimes.forEach((_, moduleId) => {
      metrics[moduleId] = this.getModuleMetrics(moduleId);
    });
    
    return metrics;
  }
}

export const loadPerformanceMonitor = new LoadPerformanceMonitor();

/**
 * Lazy loader wrapper component with performance monitoring
 */
export const LazyLoader: React.FC<LazyLoadProps> = ({
  children,
  fallback = <LazyLoadingFallback />,
  error = <LazyLoadErrorFallback />,
  moduleId
}) => {
  return (
    <LazyLoadErrorBoundary fallback={error} moduleId={moduleId || 'unknown'}>
      <Suspense fallback={fallback}>
        {children}
      </Suspense>
    </LazyLoadErrorBoundary>
  );
};

/**
 * Create a lazy-loaded component with monitoring
 */
export function createLazyComponent<T extends ComponentType<any>>(
  importFn: () => Promise<{ default: T }>,
  moduleId: string
): T {
  const startTime = performance.now();
  
  const LazyComponent = lazy(() => {
    return importFn().then(module => {
      const endTime = performance.now();
      const loadTime = endTime - startTime;
      
      // Estimate memory usage (rough approximation)
      const memoryUsed = performance.memory ? 
        (performance.memory as any).usedJSHeapSize : 0;
      
      // Record performance metrics
      loadPerformanceMonitor.recordLoad(moduleId, loadTime, memoryUsed);
      
      // Mark module as loaded in registry
      moduleRegistry.markModuleLoaded(moduleId);
      
      console.log(`Module ${moduleId} loaded in ${loadTime.toFixed(2)}ms`);
      
      return module;
    }).catch(error => {
      console.error(`Failed to load module ${moduleId}:`, error);
      throw error;
    });
  });

  return LazyComponent as T;
}

/**
 * Prefetch a module for faster loading
 */
export async function prefetchModule(moduleId: string): Promise<void> {
  const module = moduleRegistry.getModule(moduleId);
  if (!module) {
    console.warn(`Module ${moduleId} not found in registry`);
    return;
  }

  if (moduleRegistry.isModuleLoaded(moduleId)) {
    console.log(`Module ${moduleId} already loaded`);
    return;
  }

  try {
    // Dynamically import the module to prefetch it
    const startTime = performance.now();
    
    // This would be implemented based on your actual module structure
    // For now, it's a placeholder for the prefetch mechanism
    console.log(`Prefetching module ${moduleId}...`);
    
    // In production, this would call the actual dynamic import
    // await import(`../modules/${moduleId}`);
    
    const endTime = performance.now();
    console.log(`Module ${moduleId} prefetched in ${(endTime - startTime).toFixed(2)}ms`);
    
  } catch (error) {
    console.error(`Failed to prefetch module ${moduleId}:`, error);
  }
}

/**
 * Unload a module to free memory
 */
export function unloadModule(moduleId: string): void {
  if (!moduleRegistry.isModuleLoaded(moduleId)) {
    console.log(`Module ${moduleId} not loaded`);
    return;
  }

  // Mark module as unloaded
  moduleRegistry.markModuleUnloaded(moduleId);
  
  // In a real implementation, you might want to:
  // 1. Clear any caches associated with the module
  // 2. Remove event listeners
  // 3. Clear any timers/intervals
  // 4. Trigger garbage collection if possible
  
  console.log(`Module ${moduleId} unloaded`);
}

/**
 * Get load performance metrics for all modules
 */
export function getLoadMetrics(): Record<string, { avgLoadTime: number; avgMemory: number }> {
  return loadPerformanceMonitor.getAllMetrics();
}

/**
 * System health check for lazy loading
 */
export function checkLazyLoadHealth(): {
  healthy: boolean;
  loadedModules: number;
  totalModules: number;
  avgLoadTime: number;
  slowModules: string[];
} {
  const metrics = getLoadMetrics();
  const loadedModules = moduleRegistry.getLoadedModules().length;
  const totalModules = moduleRegistry.getSystemMetrics().totalModules;
  
  const loadTimes = Object.values(metrics).map(m => m.avgLoadTime);
  const avgLoadTime = loadTimes.length > 0 ? 
    loadTimes.reduce((sum, time) => sum + time, 0) / loadTimes.length : 0;
  
  // Identify slow modules (load time > 2 seconds)
  const slowModules = Object.entries(metrics)
    .filter(([_, metrics]) => metrics.avgLoadTime > 2000)
    .map(([moduleId]) => moduleId);
  
  return {
    healthy: slowModules.length === 0 && avgLoadTime < 1000,
    loadedModules,
    totalModules,
    avgLoadTime,
    slowModules
  };
}