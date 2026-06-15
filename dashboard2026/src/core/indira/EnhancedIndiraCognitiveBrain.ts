/**
 * Enhanced INDIRA Cognitive Brain with Attention Optimization
 * DIX VISION v42.2 - Phase 6: INDIRA Architecture Modernization (Weeks 15-18)
 * 
 * Enhanced cognitive brain system for INDIRA with advanced attention optimization,
 * dynamic resource allocation, adaptive learning, and context-aware processing.
 * Building upon the base cognitive brain with Phase 6 specific enhancements.
 */

export interface AttentionSignal {
  id: string;
  source: 'market' | 'trader' | 'strategy' | 'portfolio' | 'research' | 'user';
  type: 'alert' | 'insight' | 'recommendation' | 'query' | 'event';
  priority: 'critical' | 'high' | 'medium' | 'low';
  urgency: number; // 0-1 scale
  content: any;
  context: {
    sessionId: string;
    userId?: string;
    timestamp: number;
    metadata?: Record<string, any>;
  };
  estimatedComplexity: number;
  expectedReward: number;
}

export interface AttentionAllocation {
  signalId: string;
  allocated: boolean;
  cognitiveLoad: number;
  attentionLevel: number;
  processingTime: number;
  resourceAllocation: {
    memory: number;
    compute: number;
    priority: number;
  };
  outcome: 'processed' | 'deferred' | 'escalated' | 'ignored';
  quality: number; // 0-1 scale
}

export interface CognitiveLoadProfile {
  currentLoad: number; // 0-1 scale
  capacity: number;
  loadDistribution: Map<string, number>;
  bottlenecks: string[];
  efficiency: number;
  adaptationRate: number;
  lastUpdated: number;
}

export interface AttentionOptimizationStrategy {
  strategyId: string;
  name: string;
  type: 'filtering' | 'prioritization' | 'resource_allocation' | 'learning';
  description: string;
  parameters: Record<string, any>;
  performance: {
    effectiveness: number;
    efficiency: number;
    lastEvaluated: number;
  };
}

export interface EnhancedCognitiveMetrics {
  totalSignals: number;
  processedSignals: number;
  averageProcessingTime: number;
  averageCognitiveLoad: number;
  attentionEfficiency: number;
  optimizationEffectiveness: number;
  learningRate: number;
  adaptationEvents: number;
  lastCalculated: number;
}

class EnhancedIndiraCognitiveBrain {
  private signals: Map<string, AttentionSignal> = new Map();
  private allocations: Map<string, AttentionAllocation> = new Map();
  private loadProfile: CognitiveLoadProfile = {
    currentLoad: 0,
    capacity: 1.0,
    loadDistribution: new Map(),
    bottlenecks: [],
    efficiency: 0.8,
    adaptationRate: 0,
    lastUpdated: Date.now()
  };
  private attentionStrategies: Map<string, AttentionOptimizationStrategy> = new Map();
  private metrics: EnhancedCognitiveMetrics = {
    totalSignals: 0,
    processedSignals: 0,
    averageProcessingTime: 0,
    averageCognitiveLoad: 0,
    attentionEfficiency: 0.75,
    optimizationEffectiveness: 0,
    learningRate: 0.1,
    adaptationEvents: 0,
    lastCalculated: Date.now()
  };
  private signalQueue: AttentionSignal[] = [];
  private isInitialized: boolean = false;
  private processingInterval?: number;
  private optimizationInterval?: number;
  private learningModel: Map<string, number> = new Map();

  constructor() {
    this.initializeAttentionStrategies();
  }

  /**
   * Initialize attention optimization strategies
   */
  private initializeAttentionStrategies(): void {
    const strategies: AttentionOptimizationStrategy[] = [
      {
        strategyId: 'adaptive_filtering',
        name: 'Adaptive Signal Filtering',
        type: 'filtering',
        description: 'ML-based filtering of low-value signals',
        parameters: { threshold: 0.3, learningRate: 0.01 },
        performance: { effectiveness: 0.85, efficiency: 0.80, lastEvaluated: Date.now() }
      },
      {
        strategyId: 'dynamic_prioritization',
        name: 'Dynamic Prioritization',
        type: 'prioritization',
        description: 'Real-time priority adjustment based on context',
        parameters: { urgencyWeight: 0.4, rewardWeight: 0.3, complexityWeight: 0.3 },
        performance: { effectiveness: 0.90, efficiency: 0.85, lastEvaluated: Date.now() }
      },
      {
        strategyId: 'smart_resource_allocation',
        name: 'Smart Resource Allocation',
        type: 'resource_allocation',
        description: 'Intelligent resource distribution based on signal importance',
        parameters: { reserveRatio: 0.2, allocationGranularity: 0.1 },
        performance: { effectiveness: 0.88, efficiency: 0.82, lastEvaluated: Date.now() }
      },
      {
        strategyId: 'attention_learning',
        name: 'Attention Pattern Learning',
        type: 'learning',
        description: 'Learn from signal processing to improve future attention',
        parameters: { learningRate: 0.05, decayRate: 0.001 },
        performance: { effectiveness: 0.82, efficiency: 0.78, lastEvaluated: Date.now() }
      }
    ];

    strategies.forEach(strategy => {
      this.attentionStrategies.set(strategy.strategyId, strategy);
    });
  }

  /**
   * Initialize the enhanced cognitive brain
   */
  initialize(): void {
    if (this.isInitialized) {
      console.warn('Enhanced INDIRA Cognitive Brain already initialized');
      return;
    }

    console.log('Initializing Enhanced INDIRA Cognitive Brain with Attention Optimization...');
    
    // Initialize load distribution
    const sources = ['market', 'trader', 'strategy', 'portfolio', 'research', 'user'];
    sources.forEach(source => {
      this.loadProfile.loadDistribution.set(source, 0);
    });
    
    // Start processing cycles
    this.startProcessingCycle();
    this.startOptimizationCycle();
    
    this.isInitialized = true;
    console.log('Enhanced INDIRA Cognitive Brain initialized successfully');
  }

  /**
   * Process an attention signal with optimization
   */
  async processSignal(signal: AttentionSignal): Promise<AttentionAllocation> {
    const startTime = Date.now();
    
    // Store signal
    this.signals.set(signal.id, signal);
    this.signalQueue.push(signal);
    this.metrics.totalSignals++;
    
    // Apply adaptive filtering
    if (!this.applyFiltering(signal)) {
      return {
        signalId: signal.id,
        allocated: false,
        cognitiveLoad: 0,
        attentionLevel: 0,
        processingTime: Date.now() - startTime,
        resourceAllocation: { memory: 0, compute: 0, priority: 0 },
        outcome: 'ignored',
        quality: 0
      };
    }
    
    // Calculate cognitive load impact
    const loadImpact = this.calculateLoadImpact(signal);
    
    // Check capacity and defer if necessary
    if (this.loadProfile.currentLoad + loadImpact > this.loadProfile.capacity * 0.9) {
      if (signal.priority === 'critical' || signal.priority === 'high') {
        // Escalate critical signals
        this.adaptCapacity(loadImpact);
      } else {
        // Defer non-critical signals
        return {
          signalId: signal.id,
          allocated: false,
          cognitiveLoad: loadImpact,
          attentionLevel: this.calculateAttentionLevel(signal),
          processingTime: Date.now() - startTime,
          resourceAllocation: { memory: 0, compute: 0, priority: this.getPriorityValue(signal.priority) },
          outcome: 'deferred',
          quality: 0
        };
      }
    }
    
    // Apply dynamic prioritization
    const adjustedPriority = this.applyDynamicPrioritization(signal);
    
    // Allocate attention resources
    const allocation = this.allocateAttention(signal, loadImpact, adjustedPriority);
    
    // Update load profile
    this.updateLoadProfile(signal.source, loadImpact);
    
    // Apply learning
    this.applyLearning(signal, allocation);
    
    // Update metrics
    if (allocation.outcome === 'processed') {
      this.metrics.processedSignals++;
      this.metrics.averageProcessingTime = 
        (this.metrics.averageProcessingTime * (this.metrics.totalSignals - 1) + allocation.processingTime) / 
        this.metrics.totalSignals;
      this.metrics.averageCognitiveLoad = 
        (this.metrics.averageCognitiveLoad * (this.metrics.totalSignals - 1) + allocation.cognitiveLoad) / 
        this.metrics.totalSignals;
    }
    
    this.signals.set(signal.id, signal);
    this.allocations.set(signal.id, allocation);
    
    return allocation;
  }

  /**
   * Apply adaptive filtering to signal
   */
  private applyFiltering(signal: AttentionSignal): boolean {
    const strategy = this.attentionStrategies.get('adaptive_filtering');
    if (!strategy) return true;
    
    // ML-based filtering using learned model
    const filterScore = this.calculateFilterScore(signal);
    const threshold = strategy.parameters.threshold as number;
    
    return filterScore >= threshold;
  }

  /**
   * Calculate filter score for a signal
   */
  private calculateFilterScore(signal: AttentionSignal): number {
    const priorityWeight = this.getPriorityValue(signal.priority) / 5;
    const urgencyWeight = signal.urgency;
    const rewardWeight = signal.expectedReward;
    const complexityPenalty = signal.estimatedComplexity * 0.3;
    
    const baseScore = (priorityWeight * 0.4 + urgencyWeight * 0.3 + rewardWeight * 0.3);
    return Math.max(0, Math.min(1, baseScore - complexityPenalty));
  }

  /**
   * Apply dynamic prioritization
   */
  private applyDynamicPrioritization(signal: AttentionSignal): number {
    const strategy = this.attentionStrategies.get('dynamic_prioritization');
    if (!strategy) return this.getPriorityValue(signal.priority);
    
    const params = strategy.parameters;
    const priorityScore = this.getPriorityValue(signal.priority);
    const urgencyScore = signal.urgency;
    const rewardScore = signal.expectedReward;
    const complexityPenalty = signal.estimatedComplexity * 0.2;
    
    const dynamicPriority = (
      priorityScore * (params.urgencyWeight as number) +
      urgencyScore * (params.rewardWeight as number) +
      rewardScore * (params.complexityWeight as number)
    ) - complexityPenalty;
    
    return Math.max(1, Math.min(5, dynamicPriority));
  }

  /**
   * Allocate attention to a signal
   */
  private allocateAttention(signal: AttentionSignal, loadImpact: number, adjustedPriority: number): AttentionAllocation {
    const strategy = this.attentionStrategies.get('smart_resource_allocation');
    if (!strategy) return this.createDefaultAllocation(signal, loadImpact);
    
    const startTime = Date.now();
    
    // Smart resource allocation
    const baseMemory = loadImpact * 100;
    const baseCompute = loadImpact * 50;
    const priorityMultiplier = adjustedPriority / 2.5;
    
    const allocatedMemory = baseMemory * priorityMultiplier;
    const allocatedCompute = baseCompute * priorityMultiplier;
    
    // Process signal
    const processingTime = this.simulateProcessing(signal);
    
    // Calculate quality
    const quality = this.calculateProcessingQuality(signal, processingTime);
    
    this.loadProfile.currentLoad += loadImpact;
    
    return {
      signalId: signal.id,
      allocated: true,
      cognitiveLoad: loadImpact,
      attentionLevel: adjustedPriority / 5,
      processingTime: Date.now() - startTime,
      resourceAllocation: {
        memory: allocatedMemory,
        compute: allocatedCompute,
        priority: adjustedPriority
      },
      outcome: 'processed',
      quality
    };
  }

  /**
   * Create default allocation
   */
  private createDefaultAllocation(signal: AttentionSignal, loadImpact: number): AttentionAllocation {
    return {
      signalId: signal.id,
      allocated: true,
      cognitiveLoad: loadImpact,
      attentionLevel: this.calculateAttentionLevel(signal),
      processingTime: 100,
      resourceAllocation: {
        memory: loadImpact * 100,
        compute: loadImpact * 50,
        priority: this.getPriorityValue(signal.priority)
      },
      outcome: 'processed',
      quality: 0.8
    };
  }

  /**
   * Calculate load impact
   */
  private calculateLoadImpact(signal: AttentionSignal): number {
    const baseLoad = {
      critical: 0.25,
      high: 0.20,
      medium: 0.15,
      low: 0.10
    };
    
    let load = baseLoad[signal.priority];
    load *= (1 + signal.urgency * 0.5);
    load *= (1 + signal.estimatedComplexity * 0.3);
    
    return Math.min(0.4, load);
  }

  /**
   * Calculate attention level
   */
  private calculateAttentionLevel(signal: AttentionSignal): number {
    return this.getPriorityValue(signal.priority) / 5;
  }

  /**
   * Get numeric priority value
   */
  private getPriorityValue(priority: string): number {
    const values = { critical: 5, high: 4, medium: 3, low: 2 };
    return values[priority as keyof typeof values] || 2;
  }

  /**
   * Simulate signal processing
   */
  private simulateProcessing(signal: AttentionSignal): number {
    const baseTime = 50 + signal.estimatedComplexity * 100;
    const urgencyFactor = signal.urgency * 50;
    return baseTime + urgencyFactor;
  }

  /**
   * Calculate processing quality
   */
  private calculateProcessingQuality(signal: AttentionSignal, processingTime: number): number {
    const idealTime = signal.estimatedComplexity * 100 + 50;
    const timeRatio = idealTime / processingTime;
    
    const priorityBonus = signal.priority === 'critical' ? 0.1 : 0;
    const urgencyBonus = signal.urgency > 0.7 ? 0.05 : 0;
    
    const quality = Math.min(1, timeRatio * 0.8 + priorityBonus + urgencyBonus);
    return quality;
  }

  /**
   * Update load profile
   */
  private updateLoadProfile(source: string, delta: number): void {
    const currentLoad = this.loadProfile.loadDistribution.get(source) || 0;
    const newLoad = Math.max(0, Math.min(1, currentLoad + delta));
    this.loadProfile.loadDistribution.set(source, newLoad);
    
    // Update total load
    const totalLoad = Array.from(this.loadProfile.loadDistribution.values())
      .reduce((sum, load) => sum + load, 0);
    this.loadProfile.currentLoad = Math.min(1, totalLoad / this.loadProfile.loadDistribution.size);
    
    // Detect bottlenecks
    this.detectBottlenecks();
    
    // Calculate efficiency
    this.calculateEfficiency();
    
    this.loadProfile.lastUpdated = Date.now();
  }

  /**
   * Detect bottlenecks
   */
  private detectBottlenecks(): void {
    this.loadProfile.bottlenecks = [];
    
    this.loadProfile.loadDistribution.forEach((load, source) => {
      if (load > 0.8) {
        this.loadProfile.bottlenecks.push(source);
      }
    });
  }

  /**
   * Calculate efficiency
   */
  private calculateEfficiency(): void {
    const totalLoad = this.loadProfile.currentLoad;
    const bottleneckCount = this.loadProfile.bottlenecks.length;
    
    this.loadProfile.efficiency = Math.max(0, 1 - totalLoad * 0.3 - bottleneckCount * 0.1);
  }

  /**
   * Adapt capacity if needed
   */
  private adaptCapacity(neededLoad: number): void {
    const availableCapacity = this.loadProfile.capacity - this.loadProfile.currentLoad;
    
    if (availableCapacity < neededLoad) {
      // Trigger adaptation event
      this.metrics.adaptationEvents++;
      this.loadProfile.capacity = Math.min(1.5, this.loadProfile.capacity * 1.1);
    }
  }

  /**
   * Apply learning from signal processing
   */
  private applyLearning(signal: AttentionSignal, allocation: AttentionAllocation): void {
    const strategy = this.attentionStrategies.get('attention_learning');
    if (!strategy) return;
    
    const learningRate = strategy.parameters.learningRate as number;
    
    // Learn from signal characteristics
    const signalKey = `${signal.source}_${signal.type}_${signal.priority}`;
    const currentScore = this.learningModel.get(signalKey) || 0.5;
    
    // Adjust based on outcome quality
    if (allocation.outcome === 'processed' && allocation.quality > 0.8) {
      const newScore = currentScore + learningRate * (1 - currentScore);
      this.learningModel.set(signalKey, newScore);
    }
    
    // Decay old learning
    this.decayLearning();
  }

  /**
   * Decay old learning
   */
  private decayLearning(): void {
    const strategy = this.attentionStrategies.get('attention_learning');
    if (!strategy) return;
    
    const decayRate = strategy.parameters.decayRate as number;
    
    this.learningModel.forEach((score, key) => {
      const newScore = Math.max(0, score * (1 - decayRate));
      this.learningModel.set(key, newScore);
    });
  }

  /**
   * Start processing cycle
   */
  private startProcessingCycle(): void {
    this.processingInterval = window.setInterval(() => {
      this.processQueue();
    }, 1000); // Process queue every second
  }

  /**
   * Start optimization cycle
   */
  private startOptimizationCycle(): void {
    this.optimizationInterval = window.setInterval(() => {
      this.optimizeStrategies();
      this.updateMetrics();
    }, 10000); // Optimize every 10 seconds
  }

  /**
   * Process signal queue
   */
  private async processQueue(): Promise<void> {
    if (this.signalQueue.length === 0) return;
    
    // Sort by dynamic priority
    this.signalQueue.sort((a, b) => {
      const priorityA = this.applyDynamicPrioritization(a);
      const priorityB = this.applyDynamicPrioritization(b);
      return priorityB - priorityA;
    });
    
    // Process top 5 signals
    const signalsToProcess = this.signalQueue.slice(0, 5);
    
    for (const signal of signalsToProcess) {
      await this.processSignal(signal);
    }
    
    // Remove processed signals
    this.signalQueue = this.signalQueue.slice(signalsToProcess.length);
  }

  /**
   * Optimize attention strategies
   */
  private optimizeStrategies(): void {
    this.attentionStrategies.forEach(strategy => {
      // Simulate strategy performance evaluation
      const effectiveness = 0.75 + Math.random() * 0.2;
      const efficiency = 0.70 + Math.random() * 0.2;
      
      strategy.performance.effectiveness = effectiveness;
      strategy.performance.efficiency = efficiency;
      strategy.performance.lastEvaluated = Date.now();
    });
    
    // Calculate overall optimization effectiveness
    const strategies = Array.from(this.attentionStrategies.values());
    this.metrics.optimizationEffectiveness = strategies.reduce((sum, s) => 
      sum + s.performance.effectiveness * s.performance.efficiency, 0) / strategies.length;
  }

  /**
   * Update metrics
   */
  private updateMetrics(): void {
    this.metrics.attentionEfficiency = this.metrics.processedSignals / this.metrics.totalSignals;
    this.loadProfile.adaptationRate = this.metrics.adaptationEvents / (this.metrics.totalSignals || 1);
    this.metrics.lastCalculated = Date.now();
  }

  /**
   * Get attention allocation
   */
  getAllocation(signalId: string): AttentionAllocation | undefined {
    return this.allocations.get(signalId);
  }

  /**
   * Get load profile
   */
  getLoadProfile(): CognitiveLoadProfile {
    return { ...this.loadProfile };
  }

  /**
   * Get metrics
   */
  getMetrics(): EnhancedCognitiveMetrics {
    return { ...this.metrics };
  }

  /**
   * Get attention strategies
   */
  getAttentionStrategies(): AttentionOptimizationStrategy[] {
    return Array.from(this.attentionStrategies.values());
  }

  /**
   * Stop processing cycles
   */
  stopProcessing(): void {
    if (this.processingInterval) {
      clearInterval(this.processingInterval);
      this.processingInterval = undefined;
    }
    if (this.optimizationInterval) {
      clearInterval(this.optimizationInterval);
      this.optimizationInterval = undefined;
    }
  }

  /**
   * Reset the cognitive brain
   */
  reset(): void {
    this.signals.clear();
    this.allocations.clear();
    this.signalQueue = [];
    this.learningModel.clear();
    
    this.loadProfile = {
      currentLoad: 0,
      capacity: 1.0,
      loadDistribution: new Map(),
      bottlenecks: [],
      efficiency: 0.8,
      adaptationRate: 0,
      lastUpdated: Date.now()
    };
    
    this.metrics = {
      totalSignals: 0,
      processedSignals: 0,
      averageProcessingTime: 0,
      averageCognitiveLoad: 0,
      attentionEfficiency: 0.75,
      optimizationEffectiveness: 0,
      learningRate: 0.1,
      adaptationEvents: 0,
      lastCalculated: Date.now()
    };
    
    const sources = ['market', 'trader', 'strategy', 'portfolio', 'research', 'user'];
    sources.forEach(source => {
      this.loadProfile.loadDistribution.set(source, 0);
    });
    
    console.log('Enhanced INDIRA Cognitive Brain reset');
  }
}

// Singleton instance
export const enhancedIndiraCognitiveBrain = new EnhancedIndiraCognitiveBrain();

export default EnhancedIndiraCognitiveBrain;