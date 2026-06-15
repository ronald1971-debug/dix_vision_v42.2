/**
 * Module Registry
 * DIX VISION v42.2 - Phase 1: Architecture Optimization
 * 
 * Central registry for all system modules with load strategies,
 * dependency management, and resource optimization.
 */

import { ModuleConfig, ModuleCategory, LoadStrategy, UserProfile } from './ModuleTypes';

class ModuleRegistry {
  private modules: Map<string, ModuleConfig> = new Map();
  private loadedModules: Set<string> = new Set();
  private loadingModules: Map<string, Promise<any>> = new Map();
  private userProfile: UserProfile = 'standard';

  constructor() {
    this.initializeCoreModules();
    this.initializeTradingModules();
    this.initializeIntelligenceModules();
    this.initializeOperationsModules();
  }

  /**
   * Core System Modules - Always loaded (eager)
   * These are essential for the basic functionality of the application
   */
  private initializeCoreModules(): void {
    const coreModules: ModuleConfig[] = [
      {
        id: 'authentication',
        category: 'core',
        loadStrategy: 'eager',
        dependencies: [],
        bundleSize: 50, // KB
        memoryEstimate: 10, // MB
        requiredForProfile: ['minimal', 'standard', 'professional'],
        version: '1.0.0'
      },
      {
        id: 'user-management',
        category: 'core',
        loadStrategy: 'eager',
        dependencies: ['authentication'],
        bundleSize: 40,
        memoryEstimate: 8,
        requiredForProfile: ['minimal', 'standard', 'professional'],
        version: '1.0.0'
      },
      {
        id: 'basic-navigation',
        category: 'core',
        loadStrategy: 'eager',
        dependencies: [],
        bundleSize: 30,
        memoryEstimate: 5,
        requiredForProfile: ['minimal', 'standard', 'professional'],
        version: '1.0.0'
      },
      {
        id: 'core-router',
        category: 'core',
        loadStrategy: 'eager',
        dependencies: ['basic-navigation'],
        bundleSize: 45,
        memoryEstimate: 8,
        requiredForProfile: ['minimal', 'standard', 'professional'],
        version: '1.0.0'
      },
      {
        id: 'state-management',
        category: 'core',
        loadStrategy: 'eager',
        dependencies: [],
        bundleSize: 60,
        memoryEstimate: 12,
        requiredForProfile: ['minimal', 'standard', 'professional'],
        version: '1.0.0'
      },
      {
        id: 'api-client',
        category: 'core',
        loadStrategy: 'eager',
        dependencies: ['state-management'],
        bundleSize: 55,
        memoryEstimate: 10,
        requiredForProfile: ['minimal', 'standard', 'professional'],
        version: '1.0.0'
      },
      {
        id: 'error-handling',
        category: 'core',
        loadStrategy: 'eager',
        dependencies: [],
        bundleSize: 25,
        memoryEstimate: 5,
        requiredForProfile: ['minimal', 'standard', 'professional'],
        version: '1.0.0'
      },
      {
        id: 'logging-system',
        category: 'core',
        loadStrategy: 'eager',
        dependencies: [],
        bundleSize: 20,
        memoryEstimate: 4,
        requiredForProfile: ['minimal', 'standard', 'professional'],
        version: '1.0.0'
      }
    ];

    coreModules.forEach(module => {
      this.modules.set(module.id, module);
    });
  }

  /**
   * Trading Feature Modules - On navigation or on demand
   * These are loaded when the user navigates to trading sections
   */
  private initializeTradingModules(): void {
    const tradingModules: ModuleConfig[] = [
      {
        id: 'unified-markets',
        category: 'trading',
        loadStrategy: 'on_navigation',
        dependencies: ['api-client', 'state-management'],
        bundleSize: 200,
        memoryEstimate: 40,
        requiredForProfile: ['standard', 'professional'],
        optionalForProfile: ['minimal'],
        version: '1.0.0'
      },
      {
        id: 'order-flow',
        category: 'trading',
        loadStrategy: 'on_navigation',
        dependencies: ['unified-markets', 'api-client'],
        bundleSize: 180,
        memoryEstimate: 35,
        requiredForProfile: ['standard', 'professional'],
        optionalForProfile: ['minimal'],
        version: '1.0.0'
      },
      {
        id: 'charting',
        category: 'trading',
        loadStrategy: 'on_navigation',
        dependencies: ['unified-markets'],
        bundleSize: 250,
        memoryEstimate: 50,
        requiredForProfile: ['standard', 'professional'],
        optionalForProfile: ['minimal'],
        version: '1.0.0'
      },
      {
        id: 'portfolio',
        category: 'trading',
        loadStrategy: 'on_navigation',
        dependencies: ['api-client', 'state-management'],
        bundleSize: 150,
        memoryEstimate: 30,
        requiredForProfile: ['standard', 'professional'],
        optionalForProfile: ['minimal'],
        version: '1.0.0'
      },
      {
        id: 'execution',
        category: 'trading',
        loadStrategy: 'on_navigation',
        dependencies: ['unified-markets', 'api-client', 'portfolio'],
        bundleSize: 170,
        memoryEstimate: 35,
        requiredForProfile: ['professional'],
        optionalForProfile: ['minimal', 'standard'],
        version: '1.0.0'
      },
      {
        id: 'positions',
        category: 'trading',
        loadStrategy: 'on_navigation',
        dependencies: ['portfolio', 'execution'],
        bundleSize: 120,
        memoryEstimate: 25,
        requiredForProfile: ['standard', 'professional'],
        optionalForProfile: ['minimal'],
        version: '1.0.0'
      },
      {
        id: 'trading',
        category: 'trading',
        loadStrategy: 'on_navigation',
        dependencies: ['execution', 'order-flow', 'charting'],
        bundleSize: 220,
        memoryEstimate: 45,
        requiredForProfile: ['professional'],
        optionalForProfile: ['minimal', 'standard'],
        version: '1.0.0'
      }
    ];

    tradingModules.forEach(module => {
      this.modules.set(module.id, module);
    });
  }

  /**
   * Intelligence Feature Modules - On demand loading
   * These include INDIRA and DYON cognitive engines
   */
  private initializeIntelligenceModules(): void {
    const intelligenceModules: ModuleConfig[] = [
      {
        id: 'indira-cognitive-center',
        category: 'intelligence',
        loadStrategy: 'on_demand',
        dependencies: ['api-client', 'state-management'],
        bundleSize: 300,
        memoryEstimate: 60,
        requiredForProfile: ['professional'],
        optionalForProfile: ['minimal', 'standard'],
        version: '1.0.0'
      },
      {
        id: 'indira-learning',
        category: 'intelligence',
        loadStrategy: 'on_demand',
        dependencies: ['indira-cognitive-center'],
        bundleSize: 200,
        memoryEstimate: 40,
        requiredForProfile: ['professional'],
        optionalForProfile: ['minimal', 'standard'],
        version: '1.0.0'
      },
      {
        id: 'indira-workspace',
        category: 'intelligence',
        loadStrategy: 'on_demand',
        dependencies: ['indira-cognitive-center', 'indira-learning'],
        bundleSize: 180,
        memoryEstimate: 35,
        requiredForProfile: ['professional'],
        optionalForProfile: ['minimal', 'standard'],
        version: '1.0.0'
      },
      {
        id: 'dyon-workspace',
        category: 'intelligence',
        loadStrategy: 'on_demand',
        dependencies: ['api-client', 'state-management'],
        bundleSize: 250,
        memoryEstimate: 50,
        requiredForProfile: ['professional'],
        optionalForProfile: ['minimal', 'standard'],
        version: '1.0.0'
      },
      {
        id: 'dyon-learning',
        category: 'intelligence',
        loadStrategy: 'on_demand',
        dependencies: ['dyon-workspace'],
        bundleSize: 150,
        memoryEstimate: 30,
        requiredForProfile: ['professional'],
        optionalForProfile: ['minimal', 'standard'],
        version: '1.0.0'
      },
      {
        id: 'cognitive-chat',
        category: 'intelligence',
        loadStrategy: 'on_demand',
        dependencies: ['api-client', 'state-management'],
        bundleSize: 120,
        memoryEstimate: 25,
        requiredForProfile: ['standard', 'professional'],
        optionalForProfile: ['minimal'],
        version: '1.0.0'
      },
      {
        id: 'ai-features',
        category: 'intelligence',
        loadStrategy: 'on_demand',
        dependencies: ['api-client'],
        bundleSize: 180,
        memoryEstimate: 35,
        requiredForProfile: ['professional'],
        optionalForProfile: ['minimal', 'standard'],
        version: '1.0.0'
      },
      {
        id: 'memory',
        category: 'intelligence',
        loadStrategy: 'on_demand',
        dependencies: ['api-client', 'state-management'],
        bundleSize: 100,
        memoryEstimate: 20,
        requiredForProfile: ['standard', 'professional'],
        optionalForProfile: ['minimal'],
        version: '1.0.0'
      }
    ];

    intelligenceModules.forEach(module => {
      this.modules.set(module.id, module);
    });
  }

  /**
   * Operations Feature Modules - On navigation loading
   * These include mission control, system health, governance
   */
  private initializeOperationsModules(): void {
    const operationsModules: ModuleConfig[] = [
      {
        id: 'mission-control',
        category: 'operations',
        loadStrategy: 'on_navigation',
        dependencies: ['api-client', 'state-management'],
        bundleSize: 280,
        memoryEstimate: 55,
        requiredForProfile: ['minimal', 'standard', 'professional'],
        version: '1.0.0'
      },
      {
        id: 'system-health',
        category: 'operations',
        loadStrategy: 'on_navigation',
        dependencies: ['api-client'],
        bundleSize: 150,
        memoryEstimate: 30,
        requiredForProfile: ['minimal', 'standard', 'professional'],
        version: '1.0.0'
      },
      {
        id: 'governance',
        category: 'operations',
        loadStrategy: 'on_navigation',
        dependencies: ['api-client', 'authentication'],
        bundleSize: 200,
        memoryEstimate: 40,
        requiredForProfile: ['standard', 'professional'],
        optionalForProfile: ['minimal'],
        version: '1.0.0'
      },
      {
        id: 'security',
        category: 'operations',
        loadStrategy: 'on_navigation',
        dependencies: ['authentication', 'governance'],
        bundleSize: 130,
        memoryEstimate: 25,
        requiredForProfile: ['minimal', 'standard', 'professional'],
        version: '1.0.0'
      },
      {
        id: 'risk',
        category: 'operations',
        loadStrategy: 'on_navigation',
        dependencies: ['portfolio', 'execution'],
        bundleSize: 160,
        memoryEstimate: 32,
        requiredForProfile: ['professional'],
        optionalForProfile: ['minimal', 'standard'],
        version: '1.0.0'
      },
      {
        id: 'alerts',
        category: 'operations',
        loadStrategy: 'on_navigation',
        dependencies: ['api-client', 'state-management'],
        bundleSize: 90,
        memoryEstimate: 18,
        requiredForProfile: ['minimal', 'standard', 'professional'],
        version: '1.0.0'
      },
      {
        id: 'audit',
        category: 'operations',
        loadStrategy: 'on_navigation',
        dependencies: ['governance', 'logging-system'],
        bundleSize: 110,
        memoryEstimate: 22,
        requiredForProfile: ['standard', 'professional'],
        optionalForProfile: ['minimal'],
        version: '1.0.0'
      }
    ];

    operationsModules.forEach(module => {
      this.modules.set(module.id, module);
    });
  }

  /**
   * Get module configuration by ID
   */
  getModule(moduleId: string): ModuleConfig | undefined {
    return this.modules.get(moduleId);
  }

  /**
   * Get all modules for a specific category
   */
  getModulesByCategory(category: ModuleCategory): ModuleConfig[] {
    return Array.from(this.modules.values()).filter(
      module => module.category === category
    );
  }

  /**
   * Get modules that should be loaded for a user profile
   */
  getModulesForProfile(profile: UserProfile): ModuleConfig[] {
    return Array.from(this.modules.values()).filter(
      module => module.requiredForProfile.includes(profile)
    );
  }

  /**
   * Get optional modules for a user profile
   */
  getOptionalModulesForProfile(profile: UserProfile): ModuleConfig[] {
    return Array.from(this.modules.values()).filter(
      module => module.optionalForProfile?.includes(profile)
    );
  }

  /**
   * Check if a module should be loaded based on user profile
   */
  shouldLoadForProfile(moduleId: string, profile: UserProfile): boolean {
    const module = this.modules.get(moduleId);
    if (!module) return false;
    return module.requiredForProfile.includes(profile);
  }

  /**
   * Set the current user profile
   */
  setUserProfile(profile: UserProfile): void {
    this.userProfile = profile;
  }

  /**
   * Get the current user profile
   */
  getUserProfile(): UserProfile {
    return this.userProfile;
  }

  /**
   * Check if a module is currently loaded
   */
  isModuleLoaded(moduleId: string): boolean {
    return this.loadedModules.has(moduleId);
  }

  /**
   * Mark a module as loaded
   */
  markModuleLoaded(moduleId: string): void {
    this.loadedModules.add(moduleId);
  }

  /**
   * Mark a module as unloaded
   */
  markModuleUnloaded(moduleId: string): void {
    this.loadedModules.delete(moduleId);
  }

  /**
   * Get all loaded modules
   */
  getLoadedModules(): string[] {
    return Array.from(this.loadedModules);
  }

  /**
   * Calculate total bundle size for loaded modules
   */
  getLoadedBundleSize(): number {
    return Array.from(this.loadedModules).reduce((total, moduleId) => {
      const module = this.modules.get(moduleId);
      return total + (module?.bundleSize || 0);
    }, 0);
  }

  /**
   * Calculate total memory estimate for loaded modules
   */
  getLoadedMemoryEstimate(): number {
    return Array.from(this.loadedModules).reduce((total, moduleId) => {
      const module = this.modules.get(moduleId);
      return total + (module?.memoryEstimate || 0);
    }, 0);
  }

  /**
   * Get module dependencies recursively
   */
  getModuleDependencies(moduleId: string, visited: Set<string> = new Set()): string[] {
    if (visited.has(moduleId)) return [];
    
    const module = this.modules.get(moduleId);
    if (!module) return [];
    
    visited.add(moduleId);
    
    const dependencies: string[] = [...module.dependencies];
    
    module.dependencies.forEach(dep => {
      dependencies.push(...this.getModuleDependencies(dep, visited));
    });
    
    return [...new Set(dependencies)]; // Remove duplicates
  }

  /**
   * Get total system metrics
   */
  getSystemMetrics() {
    const totalModules = this.modules.size;
    const loadedModules = this.loadedModules.size;
    const totalBundleSize = this.getLoadedBundleSize();
    const totalMemoryEstimate = this.getLoadedMemoryEstimate();
    const unloadedModules = totalModules - loadedModules;
    
    // Calculate potential savings
    const totalSystemBundleSize = Array.from(this.modules.values()).reduce(
      (total, module) => total + module.bundleSize, 0
    );
    const totalSystemMemory = Array.from(this.modules.values()).reduce(
      (total, module) => total + module.memoryEstimate, 0
    );
    
    return {
      totalModules,
      loadedModules,
      unloadedModules,
      loadedBundleSize: totalBundleSize,
      loadedMemoryEstimate: totalMemoryEstimate,
      totalSystemBundleSize,
      totalSystemMemory,
      bundleSizeReduction: ((totalSystemBundleSize - totalBundleSize) / totalSystemBundleSize * 100).toFixed(1),
      memoryReduction: ((totalSystemMemory - totalMemoryEstimate) / totalSystemMemory * 100).toFixed(1),
      userProfile: this.userProfile
    };
  }
}

// Singleton instance
export const moduleRegistry = new ModuleRegistry();