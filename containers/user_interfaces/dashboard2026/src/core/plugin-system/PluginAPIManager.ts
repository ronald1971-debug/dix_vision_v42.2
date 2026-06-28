/**
 * Enhanced Plugin API with Backward Compatibility
 * DIX VISION v42.2 - Phase 3: Plugin Preservation
 * 
 * Production-grade plugin API enhancements that maintain 100% backward compatibility
 * while providing enhanced capabilities and future-proofing.
 */

import { 
  PluginHealthStatus, 
  PluginMetrics, 
  PluginConfiguration,
  PluginCompatibilityInfo
} from './EnhancedPluginSystem';

export interface OriginalPluginAPI {
  id: string;
  name: string;
  version: string;
  execute(data: any): Promise<any>;
  getState(): any;
  setState(state: any): void;
  destroy(): void;
}

export interface EnhancedPluginAPI extends OriginalPluginAPI {
  // Enhanced fields
  dependencies: string[];
  health_status: PluginHealthStatus;
  performance_metrics: PluginMetrics;
  configuration: PluginConfiguration;
  api_version: string;
  compatibility_matrix: PluginCompatibilityInfo;
  
  // Enhanced methods
  executeWithMetrics(data: any): Promise<any>;
  getHealth(): PluginHealthStatus;
  getMetrics(): PluginMetrics;
  updateConfiguration(config: Partial<PluginConfiguration>): void;
  validateCompatibility(version: string): boolean;
  migrateState(toVersion: string): Promise<void>;
  rollbackState(): Promise<void>;
}

export interface PluginAPICompatibilityLayer {
  originalAPI: OriginalPluginAPI;
  enhancedAPI: EnhancedPluginAPI;
  versionMapping: Map<string, string>;
  stateAdapter: StateAdapter;
}

export interface StateAdapter {
  adaptState(oldState: any, newVersion: string): any;
  reverseAdaptState(newState: any, oldVersion: string): any;
}

class PluginAPIManager {
  private apiRegistry: Map<string, EnhancedPluginAPI> = new Map;
  private compatibilityLayers: Map<string, PluginAPICompatibilityLayer> = new Map;
  private stateSnapshots: Map<string, Map<string, any>> = new Map;

  /**
   * Create enhanced API wrapper for original plugin
   */
  wrapPluginAPI(pluginId: string, originalAPI: OriginalPluginAPI): EnhancedPluginAPI {
    const compatibilityLayer = this.createCompatibilityLayer(pluginId, originalAPI);
    const enhancedAPI = this.createEnhancedAPI(pluginId, originalAPI, compatibilityLayer);
    
    this.apiRegistry.set(pluginId, enhancedAPI);
    this.compatibilityLayers.set(pluginId, compatibilityLayer);
    
    // Take state snapshot
    this.takeStateSnapshot(pluginId, originalAPI);
    
    console.log(`Wrapped plugin API for ${pluginId}`);
    return enhancedAPI;
  }

  /**
   * Create compatibility layer between original and enhanced API
   */
  private createCompatibilityLayer(pluginId: string, originalAPI: OriginalPluginAPI): PluginAPICompatibilityLayer {
    const versionMapping = new Map<string, string>();
    const stateAdapter = this.createStateAdapter(pluginId, originalAPI);

    return {
      originalAPI,
      enhancedAPI: {} as EnhancedPluginAPI, // Will be filled in createEnhancedAPI
      versionMapping,
      stateAdapter
    };
  }

  /**
   * Create state adapter for plugin
   */
  private createStateAdapter(pluginId: string, _originalAPI: OriginalPluginAPI): StateAdapter {
    return {
      adaptState: (oldState: any, newVersion: string) => {
        console.log(`Adapting state for ${pluginId} to version ${newVersion}`);
        
        // Preserve all original state structure
        const adaptedState = {
          ...oldState,
          version: newVersion,
          migratedAt: Date.now(),
          preserved: true
        };
        
        return adaptedState;
      },
      reverseAdaptState: (newState: any, oldVersion: string) => {
        console.log(`Reversing state adaptation for ${pluginId} to version ${oldVersion}`);
        
        // Remove migration-specific fields
        const { version, migratedAt, preserved, ...originalState } = newState;
        return originalState;
      }
    };
  }

  /**
   * Create enhanced API with compatibility layer
   */
  private createEnhancedAPI(
    pluginId: string,
    originalAPI: OriginalPluginAPI,
    compatibilityLayer: PluginAPICompatibilityLayer
  ): EnhancedPluginAPI {
    const enhancedAPI: EnhancedPluginAPI = {
      // Original API fields
      id: pluginId,
      name: originalAPI.name,
      version: originalAPI.version,
      execute: originalAPI.execute.bind(originalAPI),
      getState: originalAPI.getState.bind(originalAPI),
      setState: originalAPI.setState.bind(originalAPI),
      destroy: originalAPI.destroy.bind(originalAPI),
      
      // Enhanced fields
      dependencies: [],
      health_status: {
        healthy: true,
        lastCheck: Date.now(),
        executionTimeMs: 0,
        errorRate: 0,
        memoryUsageMB: 0,
        uptime: 0
      },
      performance_metrics: {
        execution_time_ms: 0,
        memory_usage_mb: 0,
        error_rate: 0,
        last_execution: Date.now(),
        success_count: 0
      },
      configuration: {
        enabled_features: [],
        performance_settings: {
          max_execution_time_ms: 30000,
          max_memory_mb: 100,
          cache_enabled: true
        },
        api_settings: {
          timeout_ms: 30000,
          retry_attempts: 3
        }
      },
      api_version: '1.0.0',
      compatibility_matrix: {
        compatible_versions: ['1.0.0'],
        breaking_changes: [],
        migrationRequired: false,
        migrationPath: []
      },
      
      // Enhanced methods
      executeWithMetrics: async (data: any) => {
        const startTime = performance.now();
        
        try {
          const result = await originalAPI.execute(data);
          const endTime = performance.now();
          
          const executionTime = endTime - startTime;
          const dataSize = JSON.stringify(data).length / (1024 * 1024); // Estimate memory usage
          
          // Update metrics
          enhancedAPI.performance_metrics.lastExecution = endTime;
          enhancedAPI.performance_metrics.executionTimeMs = executionTime;
          enhancedAPI.performance_metrics.memoryUsageMB = dataSize;
          enhancedAPI.performance_metrics.successCount++;
          
          // Update health status
          enhancedAPI.health_status.lastCheck = endTime;
          enhancedAPI.health_status.executionTimeMs = executionTime;
          enhancedAPI.health_status.memoryUsageMB = dataSize;
          
          return result;
        } catch (error) {
          const endTime = performance.now();
          
          // Update error metrics
          enhancedAPI.performance_metrics.lastExecution = endTime;
          enhancedAPI.performance_metrics.errorRate = 
            enhancedAPI.performance_metrics.errorRate + 0.01;
          
          // Update health status
          enhancedAPI.health_status.lastCheck = endTime;
          enhancedAPI.health_status.healthy = enhancedAPI.performance_metrics.errorRate < 0.05;
          
          throw error;
        }
      },
      
      getHealth: () => {
        return enhancedAPI.health_status;
      },
      
      getMetrics: () => {
        return enhancedAPI.performance_metrics;
      },
      
      updateConfiguration: (config: Partial<PluginConfiguration>) => {
        enhancedAPI.configuration = {
          ...enhancedAPI.configuration,
          ...config
        };
      },
      
      validateCompatibility: (version: string) => {
        return enhancedAPI.compatibility_matrix.compatible_versions.includes(version);
      },
      
      migrateState: async (toVersion: string) => {
        const currentState = originalAPI.getState();
        const adaptedState = compatibilityLayer.stateAdapter.adaptState(currentState, toVersion);
        
        originalAPI.setState(adaptedState);
        enhancedAPI.version = toVersion;
        
        console.log(`Migrated plugin ${pluginId} to version ${toVersion}`);
      },
      
      rollbackState: async () => {
        const currentState = originalAPI.getState();
        const revertedState = compatibilityLayer.stateAdapter.reverseAdaptState(
          currentState,
          enhancedAPI.version
        );
        
        originalAPI.setState(revertedState);
        enhancedAPI.version = originalAPI.version;
        
        console.log(`Rolled back plugin ${pluginId} to version ${enhancedAPI.version}`);
      }
    };
    
    // Store reference to compatibility layer for unwrap
    compatibilityLayer.enhancedAPI = enhancedAPI;
    
    return enhancedAPI;
  }

  /**
   * Unwrap enhanced API back to original API
   */
  unwrapPluginAPI(pluginId: string): OriginalPluginAPI | null {
    const compatibilityLayer = this.compatibilityLayers.get(pluginId);
    if (!compatibilityLayer) {
      console.warn(`No compatibility layer found for plugin ${pluginId}`);
      return null;
    }
    
    console.log(`Unwrapped plugin API for ${pluginId}`);
    return compatibilityLayer.originalAPI;
  }

  /**
   * Take state snapshot for rollback
   */
  private takeStateSnapshot(pluginId: string, originalAPI: OriginalPluginAPI): void {
    const currentState = originalAPI.getState();
    
    if (!this.stateSnapshots.has(pluginId)) {
      this.stateSnapshots.set(pluginId, new Map());
    }
    
    const pluginSnapshots = this.stateSnapshots.get(pluginId)!;
    const timestamp = Date.now().toString();
    
    pluginSnapshots.set(timestamp, JSON.parse(JSON.stringify(currentState)));
    
    console.log(`State snapshot taken for ${pluginId} at ${timestamp}`);
  }

  /**
   * Restore state from snapshot
   */
  restoreStateSnapshot(pluginId: string, timestamp: string): boolean {
    const pluginSnapshots = this.stateSnapshots.get(pluginId);
    if (!pluginSnapshots) {
      console.warn(`No state snapshots found for plugin ${pluginId}`);
      return false;
    }

    const snapshot = pluginSnapshots.get(timestamp);
    if (!snapshot) {
      console.warn(`No snapshot found for ${pluginId} at ${timestamp}`);
      return false;
    }

    const enhancedAPI = this.apiRegistry.get(pluginId);
    if (enhancedAPI) {
      enhancedAPI.setState(snapshot);
      console.log(`State restored for ${pluginId} from ${timestamp}`);
      return true;
    }

    return false;
  }

  /**
   * Get all plugin APIs
   */
  getAllPluginAPIs(): EnhancedPluginAPI[] {
    return Array.from(this.apiRegistry.values());
  }

  /**
   * Get plugin API by ID
   */
  getPluginAPI(pluginId: string): EnhancedPluginAPI | undefined {
    return this.apiRegistry.get(pluginId);
  }

  /**
   * Validate all plugin APIs for compatibility
   */
  validateAllCompatibility(version: string): {
    valid: number;
    invalid: string[];
  } {
    const apis = Array.from(this.apiRegistry.values());
    const invalid: string[] = [];
    let valid = 0;

    apis.forEach(api => {
      if (api.validateCompatibility(version)) {
        valid++;
      } else {
        invalid.push(api.id);
      }
    });

    return { valid, invalid };
  }
}

// Singleton instance
export const pluginAPIManager = new PluginAPIManager();