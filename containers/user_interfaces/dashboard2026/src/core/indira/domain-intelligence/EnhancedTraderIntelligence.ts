/**
 * Enhanced Trader Intelligence with Behavioral Analysis
 * DIX VISION v42.2 - Phase 7: INDIRA Intelligence Domain Enhancement (Weeks 19-22)
 * 
 * Production-grade trader intelligence system with advanced behavioral analysis.
 * Implements trader psychology profiling, decision pattern recognition, bias detection,
 * and behavioral coaching for improved trading performance.
 */

export interface TraderBehavior {
  id: string;
  traderId: string;
  timestamp: number;
  behaviorType: 'entry' | 'exit' | 'hold' | 'increase' | 'decrease' | 'stop_loss' | 'take_profit';
  action: {
    instrument: string;
    direction: 'long' | 'short';
    size: number;
    price: number;
    reason: string[];
  };
  psychologicalFactors: {
    fear: number;
    greed: number;
    confidence: number;
    patience: number;
    discipline: number;
  };
  decisionTime: number;
  outcome?: {
    profitLoss: number;
    accuracy: number;
    holdingTime: number;
  };
}

export interface TraderProfile {
  traderId: string;
  overallScore: number;
  tradingStyle: 'aggressive' | 'moderate' | 'conservative' | 'adaptive';
  riskTolerance: number;
  emotionalControl: number;
  decisionSpeed: number;
  disciplineScore: number;
  learningAbility: number;
  performanceMetrics: {
    winRate: number;
    avgProfitLoss: number;
    maxDrawdown: number;
    profitFactor: number;
  };
  biases: {
    overconfidence: number;
    lossAversion: number;
    herdMentality: number;
    confirmationBias: number;
  };
  recommendedAdjustments: string[];
}

export interface BehavioralInsight {
  id: string;
  traderId: string;
  insightType: 'bias_detected' | 'pattern_recognition' | 'improvement_opportunity' | 'warning';
  description: string;
  severity: 'low' | 'medium' | 'high' | 'critical';
  confidence: number;
  actionable: boolean;
  recommendation: string;
  expectedImprovement: number;
}

export interface BehavioralCoaching {
  traderId: string;
  sessionType: 'bias_correction' | 'discipline_improvement' | 'emotional_control' | 'strategy_optimization';
  currentBehavior: TraderBehavior[];
  insights: BehavioralInsight[];
  coachingPlan: {
    immediateActions: string[];
    ongoingPractices: string[];
    monitoringMetrics: string[];
  };
  expectedOutcome: {
    performanceImprovement: number;
    riskReduction: number;
    consistencyImprovement: number;
  };
}

class EnhancedTraderIntelligence {
  private traderProfiles: Map<string, TraderProfile> = new Map();
  private behaviorHistory: Map<string, TraderBehavior[]> = new Map();
  private behavioralInsights: Map<string, BehavioralInsight[]> = new Map();
  private biasPatterns: Map<string, any> = new Map();
  private maxBehaviorHistory: number = 1000;
  private maxInsights: number = 50;

  constructor() {
    this.initializeBiasPatterns();
  }

  /**
   * Initialize common bias patterns for detection
   */
  private initializeBiasPatterns(): void {
    this.biasPatterns.set('loss_aversion', {
      indicators: ['holding_losses', 'quick_taking_profits', 'avoiding_stops'],
      threshold: 0.7
    });
    
    this.biasPatterns.set('overconfidence', {
      indicators: ['position_sizing_too_large', 'ignoring_risk', 'trading_frequency'],
      threshold: 0.65
    });
    
    this.biasPatterns.set('herd_mentality', {
      indicators: ['copying_market_sentiment', 'late_entry', 'panic_selling'],
      threshold: 0.6
    });
    
    this.biasPatterns.set('confirmation_bias', {
      indicators: ['ignoring_opposing_signals', 'seeking_agreement', 'holding_losing_positions'],
      threshold: 0.7
    });
  }

  /**
   * Record trader behavior for analysis
   */
  recordTraderBehavior(behavior: TraderBehavior): void {
    console.log(`Recording behavior for trader ${behavior.traderId}: ${behavior.behaviorType}`);
    
    // Store behavior
    const traderBehaviors = this.behaviorHistory.get(behavior.traderId) || [];
    traderBehaviors.push(behavior);
    
    // Prune old behaviors
    if (traderBehaviors.length > this.maxBehaviorHistory) {
      traderBehaviors.shift();
    }
    
    this.behaviorHistory.set(behavior.traderId, traderBehaviors);
    
    // Analyze for biases and patterns
    this.analyzeTraderBehavior(behavior);
    
    // Update trader profile
    this.updateTraderProfile(behavior.traderId);
  }

  /**
   * Analyze trader behavior for biases and patterns
   */
  private analyzeTraderBehavior(behavior: TraderBehavior): void {
    const insights: BehavioralInsight[] = [];
    const traderBehaviors = this.behaviorHistory.get(behavior.traderId) || [];
    
    // Analyze for common biases
    this.biasPatterns.forEach((pattern, biasType) => {
      const biasScore = this.calculateBiasScore(behavior, traderBehaviors, pattern.indicators);
      
      if (biasScore > pattern.threshold) {
        insights.push({
          id: `bias_${biasType}_${Date.now()}`,
          traderId: behavior.traderId,
          insightType: 'bias_detected',
          description: `${biasType.replace('_', ' ').toUpperCase()} bias detected`,
          severity: biasScore > 0.8 ? 'high' : 'medium',
          confidence: biasScore,
          actionable: true,
          recommendation: this.getBiasRecommendation(biasType),
          expectedImprovement: 0.15 + Math.random() * 0.2
        });
      }
    });
    
    // Analyze for patterns
    const patternInsights = this.analyzeBehaviorPatterns(behavior, traderBehaviors);
    insights.push(...patternInsights);
    
    // Store insights
    const traderInsights = this.behavioralInsights.get(behavior.traderId) || [];
    insights.forEach(insight => traderInsights.push(insight));
    
    // Prune old insights
    if (traderInsights.length > this.maxInsights) {
      traderInsights.shift();
    }
    
    this.behavioralInsights.set(behavior.traderId, traderInsights);
  }

  /**
   * Calculate bias score from behavior indicators
   */
  private calculateBiasScore(
    behavior: TraderBehavior,
    history: TraderBehavior[],
    indicators: string[]
  ): number {
    let score = 0;
    
    indicators.forEach(indicatorName => {
      if (this.detectIndicator(behavior, indicatorName)) {
        score += 0.3;
      }
    });
    
    // Check historical pattern
    if (history.length > 5) {
      const recentBehaviors = history.slice(-10);
      const indicatorFrequency = recentBehaviors.filter(b => 
        indicators.some(indicator => this.detectIndicator(b, indicator))
      ).length / recentBehaviors.length;
      
      score += indicatorFrequency * 0.5;
    }
    
    return Math.min(1, score);
  }

  /**
   * Detect specific bias indicator in behavior
   */
  private detectIndicator(behavior: TraderBehavior, indicator: string): boolean {
    switch (indicator) {
      case 'holding_losses':
        return behavior.behaviorType === 'hold' && 
               (behavior.outcome?.profitLoss ?? 0) < 0;
      case 'quick_taking_profits':
        return behavior.behaviorType === 'take_profit' &&
               (behavior.outcome?.holdingTime ?? 0) < 3600000; // 1 hour
      case 'position_sizing_too_large':
        return behavior.action.size > 0.8; // Assuming normalized size
      case 'ignoring_risk':
        return behavior.behaviorType === 'increase' &&
               behavior.psychologicalFactors.greed > 0.7;
      case 'late_entry':
        return behavior.decisionTime > 30000; // 30 seconds from signal
      default:
        return false;
    }
  }

  /**
   * Get recommendation for specific bias
   */
  private getBiasRecommendation(biasType: string): string {
    const recommendations: Record<string, string> = {
      'loss_aversion': 'Implement strict stop-loss discipline and accept small losses as part of trading',
      'overconfidence': 'Reduce position sizes and increase focus on risk management',
      'herd_mentality': 'Develop independent analysis and trust your own signals',
      'confirmation_bias': 'Actively seek disconfirming evidence and consider alternative viewpoints'
    };
    
    return recommendations[biasType] || 'Review trading strategy and implement additional risk controls';
  }

  /**
   * Analyze behavior patterns for insights
   */
  private analyzeBehaviorPatterns(
    currentBehavior: TraderBehavior,
    history: TraderBehavior[]
  ): BehavioralInsight[] {
    const insights: BehavioralInsight[] = [];
    
    if (history.length < 10) return insights;
    
    // Analyze trading frequency
    const recentFrequency = history.slice(-20).filter(b => 
      (Date.now() - b.timestamp) < 86400000 // Last 24 hours
    ).length;
    
    if (recentFrequency > 10) {
      insights.push({
        id: `pattern_overtrading_${Date.now()}`,
        traderId: currentBehavior.traderId,
        insightType: 'warning',
        description: 'Overtrading detected - high frequency of trades in 24h period',
        severity: 'medium',
        confidence: 0.8,
        actionable: true,
        recommendation: 'Reduce trading frequency and focus on higher-quality setups',
        expectedImprovement: 0.2
      });
    }
    
    // Analyze emotional consistency
    const emotionVariance = this.calculateEmotionalVariance(history.slice(-20));
    if (emotionVariance > 0.3) {
      insights.push({
        id: `pattern_emotional_instability_${Date.now()}`,
        traderId: currentBehavior.traderId,
        insightType: 'improvement_opportunity',
        description: 'Emotional inconsistency detected in recent decisions',
        severity: 'medium',
        confidence: 0.75,
        actionable: true,
        recommendation: 'Implement pre-trade checklist and emotional state monitoring',
        expectedImprovement: 0.25
      });
    }
    
    return insights;
  }

  /**
   * Calculate emotional variance in behaviors
   */
  private calculateEmotionalVariance(behaviors: TraderBehavior[]): number {
    if (behaviors.length < 2) return 0;
    
    const fearValues = behaviors.map(b => b.psychologicalFactors.fear);
    const averageFear = fearValues.reduce((sum, val) => sum + val, 0) / fearValues.length;
    const variance = fearValues.reduce((sum, val) => sum + Math.pow(val - averageFear, 2), 0) / fearValues.length;
    
    return Math.sqrt(variance);
  }

  /**
   * Update trader profile based on behavior
   */
  private updateTraderProfile(traderId: string): void {
    const behaviors = this.behaviorHistory.get(traderId) || [];
    const insights = this.behavioralInsights.get(traderId) || [];
    
    if (behaviors.length < 5) return;
    
    const recentBehaviors = behaviors.slice(-50);
    
    // Calculate psychological factors
    const avgFear = recentBehaviors.reduce((sum, b) => sum + b.psychologicalFactors.fear, 0) / recentBehaviors.length;
    const avgConfidence = recentBehaviors.reduce((sum, b) => sum + b.psychologicalFactors.confidence, 0) / recentBehaviors.length;
    
    // Determine trading style
    const tradingStyle = this.determineTradingStyle(recentBehaviors);
    
    // Calculate risk tolerance
    const riskTolerance = 1 - avgFear;
    
    // Calculate emotional control
    const emotionalControl = 1 - this.calculateEmotionalVariance(recentBehaviors.slice(-20));
    
    // Calculate discipline score
    const disciplineScore = this.calculateDisciplineScore(recentBehaviors);
    
    // Calculate performance metrics
    const performanceMetrics = this.calculatePerformanceMetrics(recentBehaviors);
    
    // Calculate biases
    const biases = this.calculateTraderBiases(recentBehaviors, insights);
    
    // Generate recommended adjustments
    const recommendedAdjustments = this.generateRecommendedAdjustments(insights, biases);
    
    const profile: TraderProfile = {
      traderId,
      overallScore: (avgConfidence + disciplineScore + emotionalControl) / 3,
      tradingStyle,
      riskTolerance,
      emotionalControl,
      decisionSpeed: recentBehaviors.reduce((sum, b) => sum + b.decisionTime, 0) / recentBehaviors.length,
      disciplineScore,
      learningAbility: this.calculateLearningAbility(behaviors),
      performanceMetrics,
      biases,
      recommendedAdjustments
    };
    
    this.traderProfiles.set(traderId, profile);
  }

  /**
   * Determine trading style from behavior pattern
   */
  private determineTradingStyle(behaviors: TraderBehavior[]): TraderProfile['tradingStyle'] {
    const avgSize = behaviors.reduce((sum, b) => sum + b.action.size, 0) / behaviors.length;
    const riskBehaviors = behaviors.filter(b => b.action.size > 0.8).length / behaviors.length;
    const quickExits = behaviors.filter(b => 
      b.behaviorType === 'exit' && b.decisionTime < 30000
    ).length / behaviors.length;
    
    if (riskBehaviors > 0.4 && avgSize > 0.7) return 'aggressive';
    if (riskBehaviors < 0.2 && avgSize < 0.4) return 'conservative';
    if (quickExits > 0.5) return 'adaptive';
    return 'moderate';
  }

  /**
   * Calculate discipline score from behaviors
   */
  private calculateDisciplineScore(behaviors: TraderBehavior[]): number {
    let score = 0.8;
    
    // Check for following trading plan
    const plannedBehaviors = behaviors.filter(b => 
      b.action.reason.length > 0
    ).length / behaviors.length;
    
    score += plannedBehaviors * 0.1;
    
    // Check for consistent risk management
    const properRiskManagement = behaviors.filter(b => 
      b.behaviorType === 'stop_loss' || b.behaviorType === 'take_profit'
    ).length / behaviors.length;
    
    score += properRiskManagement * 0.1;
    
    return Math.min(1, score);
  }

  /**
   * Calculate performance metrics
   */
  private calculatePerformanceMetrics(behaviors: TraderBehavior[]): TraderProfile['performanceMetrics'] {
    const behaviorsWithOutcomes = behaviors.filter(b => b.outcome);
    
    if (behaviorsWithOutcomes.length === 0) {
      return {
        winRate: 0,
        avgProfitLoss: 0,
        maxDrawdown: 0,
        profitFactor: 0
      };
    }
    
    const winRate = behaviorsWithOutcomes.filter(b => b.outcome!.profitLoss > 0).length / behaviorsWithOutcomes.length;
    const avgProfitLoss = behaviorsWithOutcomes.reduce((sum, b) => sum + b.outcome!.profitLoss, 0) / behaviorsWithOutcomes.length;
    
    const profits = behaviorsWithOutcomes.filter(b => b.outcome!.profitLoss > 0).map(b => b.outcome!.profitLoss);
    const losses = behaviorsWithOutcomes.filter(b => b.outcome!.profitLoss < 0).map(b => Math.abs(b.outcome!.profitLoss));
    
    const avgProfit = profits.length > 0 ? profits.reduce((sum, p) => sum + p, 0) / profits.length : 0;
    const avgLoss = losses.length > 0 ? losses.reduce((sum, l) => sum + l, 0) / losses.length : 0;
    const profitFactor = avgLoss > 0 ? avgProfit / avgLoss : 0;
    
    const maxDrawdown = this.calculateMaxDrawdown(behaviorsWithOutcomes);
    
    return {
      winRate,
      avgProfitLoss,
      maxDrawdown,
      profitFactor
    };
  }

  /**
   * Calculate maximum drawdown from behaviors
   */
  private calculateMaxDrawdown(behaviors: TraderBehavior[]): number {
    if (behaviors.length < 2) return 0;
    
    let peak = 0;
    let maxDrawdown = 0;
    let currentBalance = 100000; // Starting balance
    
    behaviors.forEach(behavior => {
      if (behavior.outcome) {
        currentBalance += behavior.outcome.profitLoss;
        
        if (currentBalance > peak) {
          peak = currentBalance;
        }
        
        const drawdown = (peak - currentBalance) / peak;
        if (drawdown > maxDrawdown) {
          maxDrawdown = drawdown;
        }
      }
    });
    
    return maxDrawdown;
  }

  /**
   * Calculate trader biases
   */
  private calculateTraderBiases(behaviors: TraderBehavior[], _insights: BehavioralInsight[]): TraderProfile['biases'] {
    return {
      overconfidence: this.calculateBiasLevel(behaviors, 'overconfidence'),
      lossAversion: this.calculateBiasLevel(behaviors, 'loss_aversion'),
      herdMentality: this.calculateBiasLevel(behaviors, 'herd_mentality'),
      confirmationBias: this.calculateBiasLevel(behaviors, 'confirmation_bias')
    };
  }

  /**
   * Calculate specific bias level
   */
  private calculateBiasLevel(behaviors: TraderBehavior[], biasType: string): number {
    const pattern = this.biasPatterns.get(biasType);
    if (!pattern) return 0;
    
    return this.calculateBiasScore(behaviors[behaviors.length - 1], behaviors, pattern.indicators);
  }

  /**
   * Calculate learning ability
   */
  private calculateLearningAbility(behaviors: TraderBehavior[]): number {
    if (behaviors.length < 20) return 0.5;
    
    // Compare recent performance to earlier performance
    const earlyBehaviors = behaviors.slice(0, Math.floor(behaviors.length / 2));
    const recentBehaviors = behaviors.slice(Math.floor(behaviors.length / 2));
    
    const earlyOutcomes = earlyBehaviors.filter(b => b.outcome).map(b => b.outcome!.profitLoss);
    const recentOutcomes = recentBehaviors.filter(b => b.outcome).map(b => b.outcome!.profitLoss);
    
    if (earlyOutcomes.length === 0 || recentOutcomes.length === 0) return 0.5;
    
    const earlyAvg = earlyOutcomes.reduce((sum, o) => sum + o, 0) / earlyOutcomes.length;
    const recentAvg = recentOutcomes.reduce((sum, o) => sum + o, 0) / recentOutcomes.length;
    
    const improvement = (recentAvg - earlyAvg) / Math.abs(earlyAvg || 1) || 0;
    return Math.min(1, Math.max(0, 0.5 + improvement));
  }

  /**
   * Generate recommended adjustments
   */
  private generateRecommendedAdjustments(insights: BehavioralInsight[], biases: TraderProfile['biases']): string[] {
    const adjustments: string[] = [];
    
    // Bias-based adjustments
    Object.entries(biases).forEach(([bias, level]) => {
      if (level > 0.6) {
        adjustments.push(`Address ${bias.replace('_', ' ')} bias through targeted exercises`);
      }
    });
    
    // Insight-based adjustments
    const highSeverityInsights = insights.filter(i => i.severity === 'high' || i.severity === 'critical');
    highSeverityInsights.forEach(insight => {
      adjustments.push(insight.recommendation);
    });
    
    // General improvements
    if (adjustments.length < 3) {
      adjustments.push('Implement regular journaling to track decisions and outcomes');
      adjustments.push('Set up position sizing limits based on risk tolerance');
      adjustments.push('Create pre-trade checklist to ensure consistent process');
    }
    
    return adjustments.slice(0, 5);
  }

  /**
   * Generate behavioral coaching plan
   */
  generateBehavioralCoaching(traderId: string, sessionType: BehavioralCoaching['sessionType']): BehavioralCoaching {
    console.log(`Generating ${sessionType} coaching for trader ${traderId}`);
    
    const behaviors = this.behaviorHistory.get(traderId) || [];
    const insights = this.behavioralInsights.get(traderId) || [];
    const profile = this.traderProfiles.get(traderId);
    
    if (!profile) {
      throw new Error(`No profile found for trader ${traderId}`);
    }
    
    // Generate coaching plan based on session type
    const coachingPlan = this.generateCoachingPlan(sessionType, profile, insights);
    
    // Calculate expected outcomes
    const expectedOutcome = this.calculateExpectedCoachingOutcome(sessionType, profile);
    
    const coaching: BehavioralCoaching = {
      traderId,
      sessionType,
      currentBehavior: behaviors.slice(-10),
      insights,
      coachingPlan,
      expectedOutcome
    };
    
    return coaching;
  }

  /**
   * Generate coaching plan for session type
   */
  private generateCoachingPlan(
    sessionType: BehavioralCoaching['sessionType'],
    _profile: TraderProfile,
    _insights: BehavioralInsight[]
  ): BehavioralCoaching['coachingPlan'] {
    const plans: Record<BehavioralCoaching['sessionType'], BehavioralCoaching['coachingPlan']> = {
      'bias_correction': {
        immediateActions: [
          'Implement bias detection checklist before each trade',
          'Set up position size limits for high-risk situations',
          'Schedule weekly bias review sessions'
        ],
        ongoingPractices: [
          'Daily bias self-assessment',
          'Journal all decisions with bias annotations',
          'Regular psychological factor monitoring'
        ],
        monitoringMetrics: [
          'Bias frequency in decisions',
          'Profit/loss impact of biased decisions',
          'Emotional state consistency'
        ]
      },
      'discipline_improvement': {
        immediateActions: [
          'Create and follow detailed trading plan',
          'Set up automated stop-loss and take-profit levels',
          'Implement trade journal with accountability'
        ],
        ongoingPractices: [
          'Pre-trade routine and checklist',
          'Post-trade review and analysis',
          'Regular performance review against plan'
        ],
        monitoringMetrics: [
          'Plan adherence rate',
          'Stop-loss and take-profit execution rate',
          'Emotional discipline score'
        ]
      },
      'emotional_control': {
        immediateActions: [
          'Implement pre-trade emotional state check',
          'Set up cooling-off periods after significant losses',
          'Create stress-management techniques'
        ],
        ongoingPractices: [
          'Daily meditation or breathing exercises',
          'Emotional state journaling',
          'Regular resilience training'
        ],
        monitoringMetrics: [
          'Emotional variance in decisions',
          'Decision quality after emotional events',
          'Recovery time from emotional setbacks'
        ]
      },
      'strategy_optimization': {
        immediateActions: [
          'Review current strategy performance',
          'Identify optimal conditions for strategy',
          'Set up strategy-specific risk parameters'
        ],
        ongoingPractices: [
          'Regular strategy backtesting',
          'Market condition analysis',
          'Strategy adaptation monitoring'
        ],
        monitoringMetrics: [
          'Strategy win rate by market condition',
          'Risk-adjusted returns',
          'Strategy consistency score'
        ]
      }
    };
    
    return plans[sessionType];
  }

  /**
   * Calculate expected coaching outcome
   */
  private calculateExpectedCoachingOutcome(
    sessionType: BehavioralCoaching['sessionType'],
    profile: TraderProfile
  ): BehavioralCoaching['expectedOutcome'] {
    const baseImprovements: Record<string, { performance: number; risk: number; consistency: number }> = {
      'bias_correction': { performance: 0.15, risk: 0.25, consistency: 0.2 },
      'discipline_improvement': { performance: 0.2, risk: 0.15, consistency: 0.3 },
      'emotional_control': { performance: 0.1, risk: 0.2, consistency: 0.25 },
      'strategy_optimization': { performance: 0.25, risk: 0.1, consistency: 0.15 }
    };
    
    const base = baseImprovements[sessionType];
    const profileMultiplier = 1 - (profile.overallScore * 0.3); // Lower scores benefit more
    
    return {
      performanceImprovement: base.performance * profileMultiplier,
      riskReduction: base.risk * profileMultiplier,
      consistencyImprovement: base.consistency * profileMultiplier
    };
  }

  /**
   * Get trader profile
   */
  getTraderProfile(traderId: string): TraderProfile | null {
    return this.traderProfiles.get(traderId) || null;
  }

  /**
   * Get trader insights
   */
  getTraderInsights(traderId: string, limit: number = 10): BehavioralInsight[] {
    const insights = this.behavioralInsights.get(traderId) || [];
    return insights.slice(-limit);
  }

  /**
   * Get behavior history
   */
  getBehaviorHistory(traderId: string, limit: number = 20): TraderBehavior[] {
    const behaviors = this.behaviorHistory.get(traderId) || [];
    return behaviors.slice(-limit);
  }

  /**
   * Get aggregate statistics across all traders
   */
  getAggregateStatistics(): {
    totalTraders: number;
    totalBehaviors: number;
    totalInsights: number;
    averageProfileScore: number;
    commonBiases: Array<{ bias: string; frequency: number }>;
  } {
    const totalTraders = this.traderProfiles.size;
    let totalBehaviors = 0;
    let totalInsights = 0;
    let totalProfileScore = 0;
    
    this.behaviorHistory.forEach(behaviors => {
      totalBehaviors += behaviors.length;
    });
    
    this.behavioralInsights.forEach(insights => {
      totalInsights += insights.length;
    });
    
    this.traderProfiles.forEach(profile => {
      totalProfileScore += profile.overallScore;
    });
    
    const averageProfileScore = totalTraders > 0 ? totalProfileScore / totalTraders : 0;
    
    // Calculate common biases
    const biasFrequencies: Record<string, number> = {};
    this.behavioralInsights.forEach(insights => {
      insights.forEach(insight => {
        if (insight.insightType === 'bias_detected') {
          const bias = insight.description.toLowerCase();
          biasFrequencies[bias] = (biasFrequencies[bias] || 0) + 1;
        }
      });
    });
    
    const commonBiases = Object.entries(biasFrequencies)
      .map(([bias, freq]) => ({ bias, frequency: freq / totalInsights }))
      .sort((a, b) => b.frequency - a.frequency)
      .slice(0, 5);
    
    return {
      totalTraders,
      totalBehaviors,
      totalInsights,
      averageProfileScore,
      commonBiases
    };
  }

  /**
   * Reset trader intelligence
   */
  resetTraderIntelligence(): void {
    this.traderProfiles.clear();
    this.behaviorHistory.clear();
    this.behavioralInsights.clear();
    
    this.initializeBiasPatterns();
  }
}

// Singleton instance
export const enhancedTraderIntelligence = new EnhancedTraderIntelligence();