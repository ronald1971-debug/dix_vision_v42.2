/**
 * Advanced Memory Manager
 * DIX VISION v42.2 - Phase 2: Resource Optimization
 * 
 * Production-grade memory management system with automatic cleanup,
 * garbage collection optimization, memory leak detection, and memory pressure handling.
 */

import { moduleRegistry } from '../modular-architecture/ModuleRegistry';
import { resourceMonitor } from '../modular-architecture/ResourceMonitor';

interface MemoryPressureLevel {
  level: 'normal' | 'moderate' | 'high' | 'critical';
  threshold: number; // percentage
  action: 'none' | 'cleanup' | 'aggressive-cleanup' | 'emergency-unload';
}

interface MemoryCleanupStrategy {
  moduleId: string;
  priority: number;
  lastAccessed: number;
  memoryFootprint: number;
  cleanupAction: 'unload' | 'cache-clear' | 'state-reset';
}

interface MemoryLeak {
  source: string;
  leakedMemory: number;
  detectedAt: number;
  trend: 'increasing' | 'stable' | 'decreasing';
}

class MemoryManager {
  private memorySnapshots: Map<string, number[]> = new Map();
  private cleanupInterval: number | null = null;
  private memoryLeaks: MemoryLeak[] = [];
  private maxMemoryLeaks = 50;
  private cleanupStrategies: Map<string, MemoryCleanupStrategy> = new Map();
  private memoryPressureLevels: MemoryPressureLevel[] = [
    { level: 'normal', threshold: 50, action: 'none' },
    { level: 'moderate', threshold: 70, action: 'cleanup' },
    { level: 'high', threshold: 85, action: 'aggressive-cleanup' },
    { level: 'critical', threshold: 95, action: 'emergency-unload' }
  ];
  private isMonitoring = false;
  private gcTriggered = false;

  constructor() {
    this.initializeCleanupStrategies();
  }

  /**
   * Initialize cleanup strategies for different module types
   */
  private initializeCleanupStrategies(): void {
    const allModules = Array.from(moduleRegistry.modules.values());
    
    allModules.forEach(module => {
      const strategy: MemoryCleanupStrategy = {
        moduleId: module.id,
        priority: this.calculateModulePriority(module),
        lastAccessed: Date.now(),
        memoryFootprint: module.memoryEstimate,
        cleanupAction: this.determineCleanupAction(module)
      };
      
      this.cleanupStrategies.set(module.id, strategy);
    });
  }

  /**
   * Calculate module priority based on category and usage
   */
  private calculateModulePriority(module: any): number {
    const categoryPriority: Record<string, number> = {
      core: 100, // Never unload
      trading: 75,
      operations: 70,
      intelligence: 50, // Lower priority, can be unloaded
      plugin: 30 // Lowest priority
    };
    
    return categoryPriority[module.category] || 50;
  }

  /**
   * Determine cleanup action for a module
   */
  private determineCleanupAction(module: any): 'unload' | 'cache-clear' | 'state-reset' {
    if (module.category === 'core') {
      return 'state-reset'; // Core modules can reset state but not unload
    }
    
    if (module.loadStrategy === 'on_demand') {
      return 'unload'; // On-demand modules can be fully unloaded
    }
    
    if (module.category === 'intelligence') {
      return 'cache-clear'; // Intelligence modules clear caches first
    }
    
    return 'unload';
  }

  /**
   * Start memory monitoring and automatic cleanup
   */
  startMonitoring(intervalMs: number = 10000): void {
    if (this.isMonitoring) {
      console.warn('Memory manager already monitoring');
      return;
    }

    console.log(`Starting memory manager with ${intervalMs}ms interval`);
    this.isMonitoring = true;

    // Take initial snapshot
    this.takeMemorySnapshot();

    // Set up monitoring interval
    this.cleanupInterval = window.setInterval(() => {
      this.monitorAndCleanup();
    }, intervalMs);
  }

  /**
   * Stop memory monitoring
   */
  stopMonitoring(): void {
    if (!this.isMonitoring) {
      return;
    }

    console.log('Stopping memory manager');
    this.isMonitoring = false;

    if (this.cleanupInterval) {
      clearInterval(this.cleanupInterval);
      this.cleanupInterval = null;
    }
  }

  /**
   * Take a memory snapshot for leak detection
   */
  private takeMemorySnapshot(): void {
    const memoryInfo = this.getMemoryInfo();
    const timestamp = Date.now();
    
    // Store memory info by module
    const loadedModules = moduleRegistry.getLoadedModules();
    loadedModules.forEach(moduleId => {
      if (!this.memorySnapshots.has(moduleId)) {
        this.memorySnapshots.set(moduleId, []);
      }
      
      const snapshots = this.memorySnapshots.get(moduleId)!;
      snapshots.push(memoryInfo.usedJSHeapSize);
      
      // Keep only last 20 snapshots
      if (snapshots.length > 20) {
        snapshots.shift();
      }
    });
  }

  /**
   * Monitor memory and perform cleanup as needed
   */
  private monitorAndCleanup(): void {
    const memoryInfo = this.getMemoryInfo();
    const pressureLevel = this.calculateMemoryPressure(memoryInfo);
    
    console.log(`Memory pressure: ${pressureLevel.level} (${pressureLevel.threshold}% threshold)`);
    
    // Take snapshot for leak detection
    this.takeMemorySnapshot();
    
    // Detect memory leaks
    this.detectMemoryLeaks();
    
    // Perform cleanup based on pressure level
    switch (pressureLevel.action) {
      case 'cleanup':
        this.performNormalCleanup();
        break;
      case 'aggressive-cleanup':
        this.performAggressiveCleanup();
        break;
      case 'emergency-unload':
        this.performEmergencyUnload();
        break;
      case 'none':
      default:
        // Normal operation, no cleanup needed
        break;
    }
    
    // Trigger garbage collection if needed
    if (pressureLevel.level === 'high' || pressureLevel.level === 'critical') {
      this.triggerGarbageCollection();
    }
  }

  /**
   * Calculate memory pressure level
   */
  private calculateMemoryPressure(memoryInfo: MemoryInfo): MemoryPressureLevel {
    const memoryUsagePercent = (memoryInfo.usedJSHeapSize / memoryInfo.jsHeapSizeLimit) * 100;
    
    for (const level of this.memoryPressureLevels) {
      if (memoryUsagePercent <= level.threshold) {
        return level;
      }
    }
    
    return this.memoryPressureLevels[this.memoryPressureLevels.length - 1];
  }

  /**
   * Detect memory leaks in loaded modules
   */
  private detectMemoryLeaks(): void {
    this.memorySnapshots.forEach((snapshots, moduleId) => {
      if (snapshots.length < 5) return; // Need at least 5 snapshots
      
      const recentSnapshots = snapshots.slice(-5);
      const firstSnapshot = recentSnapshots[0];
      const lastSnapshot = recentSnapshots[recentSnapshots.length - 1];
      
      // Calculate trend
      const increase = lastSnapshot - firstSnapshot;
      const trend: 'increasing' | 'stable' | 'decreasing' = 
        increase > 100000 ? 'increasing' : // More than 100KB increase
        increase < -100000 ? 'decreasing' : 
        'stable';
      
      // If trend is increasing significantly, flag as potential leak
      if (trend === 'increasing') {
        const existingLeak = this.memoryLeaks.find(leak => leak.source === moduleId);
        
        if (existingLeak) {
          // Update existing leak
          existingLeak.leakedMemory = increase;
          existingLeak.detectedAt = Date.now();
          existingLeak.trend = trend;
        } else {
          // Add new leak
          this.memoryLeaks.push({
            source: moduleId,
            leakedMemory: increase,
            detectedAt: Date.now(),
            trend
          });
        }
      }
    });
    
    // Keep only recent memory leaks
    this.memoryLeaks = this.memoryLeaks.slice(-this.maxMemoryLeaks);
    
    // Log detected leaks
    if (this.memoryLeaks.length > 0) {
      console.warn('Potential memory leaks detected:', this.memoryLeaks);
    }
  }

  /**
   * Perform normal cleanup (moderate pressure)
   */
  private performNormalCleanup(): void {
    console.log('Performing normal memory cleanup');
    
    // Clear caches in intelligence modules
    this.clearModuleCaches(['indira-cognitive-center', 'dyon-workspace', 'cognitive-chat']);
    
    // Reset state in non-core modules that haven't been accessed recently
    this.cleanupInactiveModules(60000); // 1 minute threshold
  }

  /**
   * Perform aggressive cleanup (high pressure)
   */
  private performAggressiveCleanup(): void {
    console.log('Performing aggressive memory cleanup');
    
    // Clear all caches
    this.clearAllModuleCaches();
    
    // Unload low-priority modules
    this.unloadLowPriorityModules();
    
    // Reset state in all non-core modules
    this.resetModuleStates();
    
    // Force garbage collection
    this.triggerGarbageCollection();
  }

  /**
   * Perform emergency unload (critical pressure)
   */
  private performEmergencyUnload(): void {
    console.warn('EMERGENCY: Performing emergency module unload');
    
    // Unload all non-core modules
    const allModules = Array.from(moduleRegistry.modules.values());
    const nonCoreModules = allModules.filter(m => m.category !== 'core');
    
    nonCoreModules.forEach(module => {
      if (moduleRegistry.isModuleLoaded(module.id)) {
        console.log(`Emergency unloading module: ${module.id}`);
        moduleRegistry.markModuleUnloaded(module.id);
      }
    });
    
    // Clear all caches
    this.clearAllModuleCaches();
    
    // Force garbage collection
    this.triggerGarbageCollection();
    
    // Alert monitoring system
    this.alertMonitoringSystem('emergency-unload', nonCoreModules.length);
  }

  /**
   * Clear caches in specific modules
   */
  private clearModuleCaches(moduleIds: string[]): void {
    moduleIds.forEach(moduleId => {
      const strategy = this.cleanupStrategies.get(moduleId);
      if (strategy && strategy.cleanupAction === 'cache-clear') {
        console.log(`Clearing cache for module: ${moduleId}`);
        // In a real implementation, this would call module-specific cache clearing
        this.triggerModuleCacheClear(moduleId);
      }
    });
  }

  /**
   * Clear all module caches
   */
  private clearAllModuleCaches(): void {
    const allModules = Array.from(moduleRegistry.modules.values());
    allModules.forEach(module => {
      this.triggerModuleCacheClear(module.id);
    });
  }

  /**
   * Trigger cache clear for a specific module
   */
  private triggerModuleCacheClear(moduleId: string): void {
    // This would trigger the actual cache clearing in the module
    // For now, it's a placeholder for the implementation
    console.log(`Triggering cache clear for ${moduleId}`);
    
    // Emit event for module to handle
    if (typeof window !== 'undefined') {
      const event = new CustomEvent('module-cache-clear', { detail: { moduleId } });
      window.dispatchEvent(event);
    }
  }

  /**
   * Clean up inactive modules
   */
  private cleanupInactiveModules(thresholdMs: number): void {
    const now = Date.now();
    const strategies = Array.from(this.cleanupStrategies.values());
    
    strategies.forEach(strategy => {
      const timeSinceAccess = now - strategy.lastAccessed;
      
      if (timeSinceAccess > thresholdMs && strategy.priority < 80) {
        console.log(`Cleaning up inactive module: ${strategy.moduleId}`);
        
        if (strategy.cleanupAction === 'state-reset') {
          this.triggerModuleStateReset(strategy.moduleId);
        } else if (strategy.cleanupAction === 'cache-clear') {
          this.triggerModuleCacheClear(strategy.moduleId);
        }
      }
    });
  }

  /**
   * Unload low-priority modules
   */
  private unloadLowPriorityModules(): void {
    const strategies = Array.from(this.cleanupStrategies.values())
      .filter(s => s.priority < 50); // Low priority
    
    strategies.forEach(strategy => {
      if (moduleRegistry.isModuleLoaded(strategy.moduleId)) {
        console.log(`Unloading low-priority module: ${strategy.moduleId}`);
        moduleRegistry.markModuleUnloaded(strategy.moduleId);
      }
    });
  }

  /**
   * Reset module states
   */
  private resetModuleStates(): void {
    const nonCoreModules = Array.from(moduleRegistry.modules.values())
      .filter(m => m.category !== 'core');
    
    nonCoreModules.forEach(module => {
      this.triggerModuleStateReset(module.id);
    });
  }

  /**
   * Trigger state reset for a specific module
   */
  private triggerModuleStateReset(moduleId: string): void {
    console.log(`Triggering state reset for ${moduleId}`);
    
    // Emit event for module to handle
    if (typeof window !== 'undefined') {
      const event = new CustomEvent('module-state-reset', { detail: { moduleId } });
      window.dispatchEvent(event);
    }
  }

  /**
   * Trigger garbage collection
   */
  private triggerGarbageCollection(): void {
    if (this.gcTriggered) return;
    
    console.log('Triggering garbage collection');
    this.gcTriggered = true;
    
    // Try to trigger GC if available
    if (typeof window !== 'undefined' && (window as any).gc) {
      try {
        (window as any).gc();
      } catch (error) {
        console.warn('Manual GC trigger failed:', error);
      }
    }
    
    // Reset flag after delay
    setTimeout(() => {
      this.gcTriggered = false;
    }, 5000);
  }

  /**
   * Get memory information
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
   * Update module access time
   */
  updateModuleAccess(moduleId: string): void {
    const strategy = this.cleanupStrategies.get(moduleId);
    if (strategy) {
      strategy.lastAccessed = Date.now();
    }
  }

  /**
   * Get memory leak report
   */
  getMemoryLeakReport(): MemoryLeak[] {
    return [...this.memoryLeaks];
  }

  /**
   * Get memory statistics
   */
  getMemoryStats(): {
    currentMemory: number;
    memoryPressure: MemoryPressureLevel;
    detectedLeaks: number;
    cleanupStrategies: number;
  } {
    const memoryInfo = this.getMemoryInfo();
    const memoryPressure = this.calculateMemoryPressure(memoryInfo);
    
    return {
      currentMemory: memoryInfo.usedJSHeapSize,
      memoryPressure,
      detectedLeaks: this.memoryLeaks.length,
      cleanupStrategies: this.cleanupStrategies.size
    };
  }

  /**
   * Alert monitoring system about critical events
   */
  private alertMonitoringSystem(event: string, data: any): void {
    const alertData = {
      event,
      data,
      timestamp: new Date().toISOString(),
      memoryStats: this.getMemoryStats()
    };

    // Send to monitoring system
    if (typeof window !== 'undefined' && (window as any).monitoringClient) {
      (window as any).monitoringClient.logAlert('memory-manager', alertData);
    } else {
      console.error('Memory Manager Alert:', alertData);
    }
  }

  /**
   * Check if monitoring is active
   */
  isMonitoringActive(): boolean {
    return this.isMonitoring;
  }

  /**
   * Force immediate cleanup
   */
  forceCleanup(level: 'normal' | 'aggressive' | 'emergency' = 'normal'): void {
    console.log(`Forcing ${level} cleanup`);
    
    switch (level) {
      case 'normal':
        this.performNormalCleanup();
        break;
      case 'aggressive':
        this.performAggressiveCleanup();
        break;
      case 'emergency':
        this.performEmergencyUnload();
        break;
    }
  }
}

// Singleton instance
export const memoryManager = new MemoryManager();

// Type definitions
interface MemoryInfo {
  usedJSHeapSize: number;
  totalJSHeapSize: number;
  jsHeapSizeLimit: number;
}