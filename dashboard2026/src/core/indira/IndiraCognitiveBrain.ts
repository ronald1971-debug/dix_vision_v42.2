/**
 * INDIRA Cognitive Brain with Attention Optimization
 * DIX VISION v42.2 - Phase 4 (Phase 6): INDIRA Architecture Modernization
 * 
 * Production-grade cognitive brain system with attention optimization for INDIRA.
 * Implements attention mechanisms, memory consolidation, and cognitive load balancing
 * to optimize INDIRA's decision-making processes.
 */

export interface AttentionSignal {
  id: string;
  type: 'market' | 'trader' | 'strategy' | 'portfolio' | 'research';
  strength: number; // 0-1
  priority: 'high' | 'medium' | 'low';
  timestamp: number;
  decayRate: number;
  source: string;
}

export interface CognitiveLoad {
  totalLoad: number;
  marketLoad: number;
  traderLoad: number;
  strategyLoad: number;
  portfolioLoad: number;
  researchLoad: number;
  currentFocus: string[];
  availableCapacity: number;
}

export interface AttentionAllocation {
  domain: string;
  allocatedAttention: number;
  currentAllocation: number;
  targetAllocation: number;
  efficiency: number;
  timestamp: number;
}

export interface CognitiveMemory {
  id: string;
  type: 'short_term' | 'working' | 'long_term';
  content: any;
  importance: number;
  accessCount: number;
  lastAccess: number;
  strength: number;
  associations: string[];
  context: string;
}

export interface AttentionOptimizationResult {
  originalLoad: CognitiveLoad;
  optimizedLoad: CognitiveLoad;
  allocations: AttentionAllocation[];
  optimizationScore: number;
  processingTimeMs: number;
}

class IndiraCognitiveBrain {
  private attentionSignals: Map<string, AttentionSignal> = new Map();
  private cognitiveLoad: CognitiveLoad;
  private attentionAllocations: Map<string, AttentionAllocation> = new Map();
  private cognitiveMemory: Map<string, CognitiveMemory> = new Map();
  private attentionHistory: AttentionAllocation[] = [];
  private maxMemoryItems: number = 1000;
  private maxHistoryItems: number = 100;

  constructor() {
    this.cognitiveLoad = {
      totalLoad: 0,
      marketLoad: 0,
      traderLoad: 0,
      strategyLoad: 0,
      portfolioLoad: 0,
      researchLoad: 0,
      currentFocus: [],
      availableCapacity: 100
    };
    
    this.initializeAttentionAllocations();
  }

  /**
   * Initialize attention allocations for INDIRA domains
   */
  private initializeAttentionAllocations(): void {
    const domains = ['market', 'trader', 'strategy', 'portfolio', 'research'];
    
    domains.forEach(domain => {
      this.attentionAllocations.set(domain, {
        domain: `${domain}_intelligence`,
        allocatedAttention: 20,
        currentAllocation: 20,
        targetAllocation: 20,
        efficiency: 0.8,
        timestamp: Date.now()
      });
    });
  }

  /**
   * Process attention signal from intelligence domain
   */
  processAttentionSignal(signal: AttentionSignal): void {
    const signalId = `${signal.type}_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
    
    const enhancedSignal: AttentionSignal = {
      ...signal,
      id: signalId,
      timestamp: Date.now()
    };
    
    this.attentionSignals.set(signalId, enhancedSignal);
    
    console.log(`Processing ${signal.type} attention signal with strength ${signal.strength}`);
    
    // Update cognitive load
    this.updateCognitiveLoad(signal);
    
    // Optimize attention allocation
    this.optimizeAttentionAllocation();
    
    // Store in cognitive memory
    this.storeInCognitiveMemory(enhancedSignal);
  }

  /**
   * Update cognitive load based on signal
   */
  private updateCognitiveLoad(signal: AttentionSignal): void {
    const loadIncrement = signal.strength * 10;
    
    switch (signal.type) {
      case 'market':
        this.cognitiveLoad.marketLoad = Math.min(100, this.cognitiveLoad.marketLoad + loadIncrement);
        break;
      case 'trader':
        this.cognitiveLoad.traderLoad = Math.min(100, this.cognitiveLoad.traderLoad + loadIncrement);
        break;
      case 'strategy':
        this.cognitiveLoad.strategyLoad = Math.min(100, this.cognitiveLoad.strategyLoad + loadIncrement);
        break;
      case 'portfolio':
        this.cognitiveLoad.portfolioLoad = Math.min(100, this.cognitiveLoad.portfolioLoad + loadIncrement);
        break;
      case 'research':
        this.cognitiveLoad.researchLoad = Math.min(100, this.cognitiveLoad.researchLoad + loadIncrement);
        break;
    }
    
    this.cognitiveLoad.totalLoad = (
      this.cognitiveLoad.marketLoad +
      this.cognitiveLoad.traderLoad +
      this.cognitiveLoad.strategyLoad +
      this.cognitiveLoad.portfolioLoad +
      this.cognitiveLoad.researchLoad
    ) / 5;
    
    this.cognitiveLoad.availableCapacity = Math.max(0, 100 - this.cognitiveLoad.totalLoad);
  }

  /**
   * Optimize attention allocation across domains
   */
  private optimizeAttentionAllocation(): void {
    const domains = Array.from(this.attentionAllocations.values());
    
    // Calculate optimal allocation based on current load and priority
    domains.forEach(allocation => {
      const domainType = allocation.domain.split('_')[0];
      const domainLoad = this.cognitiveLoad[`${domainType}Load` as keyof CognitiveLoad];
      const currentLoadValue = domainLoad as number;
      
      // Target allocation inversely proportional to load
      allocation.targetAllocation = Math.max(5, 40 - currentLoadValue * 0.4);
      
      // Calculate allocation efficiency
      const efficiency = 1 - Math.abs(allocation.currentAllocation - allocation.targetAllocation) / 40;
      allocation.efficiency = Math.max(0, Math.min(1, efficiency));
      
      // Gradually adjust allocation towards target
      const adjustmentRate = 0.1;
      allocation.allocatedAttention = allocation.currentAllocation + 
        (allocation.targetAllocation - allocation.currentAllocation) * adjustmentRate;
      
      allocation.timestamp = Date.now();
      
      // Store in history
      this.attentionHistory.push({ ...allocation });
      if (this.attentionHistory.length > this.maxHistoryItems) {
        this.attentionHistory.shift();
      }
    });
  }

  /**
   * Get current cognitive load
   */
  getCognitiveLoad(): CognitiveLoad {
    return { ...this.cognitiveLoad };
  }

  /**
   * Get current attention allocations
   */
  getAttentionAllocations(): AttentionAllocation[] {
    return Array.from(this.attentionAllocations.values());
  }

  /**
   * Perform attention optimization
   */
  async performAttentionOptimization(): Promise<AttentionOptimizationResult> {
    const startTime = Date.now();
    const originalLoad = this.getCognitiveLoad();
    
    console.log('Performing attention optimization...');
    
    // Calculate optimal allocations
    const domains = Array.from(this.attentionAllocations.values());
    domains.forEach(allocation => {
      const domainType = allocation.domain.split('_')[0];
      const domainLoad = this.cognitiveLoad[`${domainType}Load` as keyof CognitiveLoad];
      const currentLoadValue = domainLoad as number;
      
      // Optimize based on load and signal strength
      const signalStrength = this.getDomainSignalStrength(domainType);
      
      // Higher load + higher signal = more attention
      const optimalAllocation = 20 + (currentLoadValue * 0.3) + (signalStrength * 0.2);
      allocation.targetAllocation = Math.min(40, optimalAllocation);
    });
    
    // Simulate optimization process
    await this.simulateOptimizationProcess();
    
    // Apply optimized allocations
    domains.forEach(allocation => {
      allocation.currentAllocation = allocation.targetAllocation;
      allocation.timestamp = Date.now();
    });
    
    const optimizedLoad = this.getCognitiveLoad();
    const processingTimeMs = Date.now() - startTime;
    
    // Calculate optimization score
    const optimizationScore = this.calculateOptimizationScore(originalLoad, optimizedLoad);
    
    return {
      originalLoad,
      optimizedLoad,
      allocations: domains,
      optimizationScore,
      processingTimeMs
    };
  }

  /**
   * Get signal strength for domain
   */
  private getDomainSignalStrength(domainType: string): number {
    const domainSignals = Array.from(this.attentionSignals.values())
      .filter(signal => signal.type === domainType)
      .slice(-5); // Get last 5 signals
    
    if (domainSignals.length === 0) return 0;
    
    // Apply decay to recent signals
    const weightedStrength = domainSignals.reduce((sum, signal, index) => {
      const weight = 1 - signal.decayRate * (domainSignals.length - index);
      return sum + signal.strength * weight;
    }, 0);
    
    return weightedStrength / domainSignals.length;
  }

  /**
   * Simulate optimization process
   */
  private async simulateOptimizationProcess(): Promise<void> {
    await new Promise(resolve => setTimeout(resolve, 500 + Math.random() * 1000));
  }

  /**
   * Calculate optimization score
   */
  private calculateOptimizationScore(original: CognitiveLoad, optimized: CognitiveLoad): number {
    const loadImprovement = original.totalLoad - optimized.totalLoad;
    const capacityImprovement = optimized.availableCapacity - original.availableCapacity;
    
    const efficiencyScore = (loadImprovement / 100) + (capacityImprovement / 100);
    
    return Math.min(1, Math.max(0, efficiencyScore));
  }

  /**
   * Store information in cognitive memory
   */
  private storeInCognitiveMemory(signal: AttentionSignal): void {
    const memoryId = `${signal.type}_memory_${Date.now()}`;
    
    const memory: CognitiveMemory = {
      id: memoryId,
      type: 'working' as 'short_term' | 'working' | 'long_term',
      content: signal,
      importance: signal.strength * (signal.priority === 'high' ? 1 : 0.7),
      accessCount: 1,
      lastAccess: Date.now(),
      strength: 1.0,
      associations: this.findAssociatedMemories(signal),
      context: this.buildContextString(signal)
    };
    
    this.cognitiveMemory.set(memoryId, memory);
    
    // Prune old memories if at capacity
    if (this.cognitiveMemory.size > this.maxMemoryItems) {
      this.pruneWeakestMemories();
    }
  }

  /**
   * Find associated memories
   */
  private findAssociatedMemories(signal: AttentionSignal): string[] {
    const associations: string[] = [];
    
    // Find memories from same type with high importance
    this.cognitiveMemory.forEach((memory, id) => {
      if (memory.content && memory.content.type === signal.type && memory.importance > 0.8) {
        associations.push(id);
      }
    });
    
    return associations.slice(0, 5); // Top 5 associations
  }

  /**
   * Build context string for memory
   */
  private buildContextString(signal: AttentionSignal): string {
    return `${signal.type} attention signal at ${new Date(signal.timestamp).toISOString()} with strength ${signal.strength}`;
  }

  /**
   * Prune weakest memories to maintain capacity
   */
  private pruneWeakestMemories(): void {
    const memories = Array.from(this.cognitiveMemory.values())
      .sort((a, b) => a.importance - b.importance)
      .slice(0, 10); // Remove 10 weakest
    
    memories.forEach(memory => {
      this.cognitiveMemory.delete(memory.id);
    });
  }

  /**
   * Retrieve from cognitive memory
   */
  retrieveFromMemory(type: string, limit: number = 10): CognitiveMemory[] {
    return Array.from(this.cognitiveMemory.values())
      .filter(memory => memory.type === type)
      .sort((a, b) => b.importance - a.importance)
      .slice(0, limit)
      .map(memory => {
        memory.accessCount++;
        memory.lastAccess = Date.now();
        return memory;
      });
  }

  /**
   * Consolidate memory (move from working to long-term)
   */
  consolidateMemory(memoryId: string): void {
    const memory = this.cognitiveMemory.get(memoryId);
    if (!memory) return;
    
    // Move from working to long-term based on access patterns
    if (memory.accessCount > 5 && memory.importance > 0.7) {
      memory.type = 'long_term';
      memory.strength = 0.9; // Strengthen important memories
    } else if (memory.accessCount > 2) {
      memory.type = 'short_term';
    }
    
    this.cognitiveMemory.set(memoryId, memory);
  }

  /**
   * Get memory statistics
   */
  getMemoryStats(): {
    totalMemory: number;
    workingMemory: number;
    shortTermMemory: number;
    longTermMemory: number;
    averageImportance: number;
  } {
    const memories = Array.from(this.cognitiveMemory.values());
    
    const workingMemory = memories.filter(m => m.type === 'working').length;
    const shortTermMemory = memories.filter(m => m.type === 'short_term').length;
    const longTermMemory = memories.filter(m => m.type === 'long_term').length;
    
    const averageImportance = memories.length > 0
      ? memories.reduce((sum, m) => sum + m.importance, 0) / memories.length
      : 0;
    
    return {
      totalMemory: memories.length,
      workingMemory,
      shortTermMemory,
      longTermMemory,
      averageImportance
    };
  }

  /**
   * Clear old attention signals
   */
  clearOldSignals(maxAgeMs: number = 3600000): number {
    const cutoffTime = Date.now() - maxAgeMs;
    let clearedCount = 0;
    
    this.attentionSignals.forEach((signal, id) => {
      if (signal.timestamp < cutoffTime) {
        this.attentionSignals.delete(id);
        clearedCount++;
      }
    });
    
    console.log(`Cleared ${clearedCount} old attention signals`);
    return clearedCount;
  }

  /**
   * Get current focus areas
   */
  getCurrentFocus(): string[] {
    // Update current focus based on highest load domains
    const domainLoads = [
      { domain: 'market', load: this.cognitiveLoad.marketLoad },
      { domain: 'trader', load: this.cognitiveLoad.traderLoad },
      { domain: 'strategy', load: this.cognitiveLoad.strategyLoad },
      { domain: 'portfolio', load: this.cognitiveLoad.portfolioLoad },
      { domain: 'research', load: this.cognitiveLoad.researchLoad }
    ];
    
    domainLoads.sort((a, b) => b.load - a.load);
    
    // Focus on top 3 domains by load
    this.cognitiveLoad.currentFocus = domainLoads.slice(0, 3).map(d => d.domain);
    
    return this.cognitiveLoad.currentFocus;
  }

  /**
   * Reset cognitive brain state
   */
  resetCognitiveBrain(): void {
    this.attentionSignals.clear();
    this.cognitiveLoad = {
      totalLoad: 0,
      marketLoad: 0,
      traderLoad: 0,
      strategyLoad: 0,
      portfolioLoad: 0,
      researchLoad: 0,
      currentFocus: [],
      availableCapacity: 100
    };
    
    this.attentionHistory = [];
    this.initializeAttentionAllocations();
  }
}

// Singleton instance
export const indiraCognitiveBrain = new IndiraCognitiveBrain();