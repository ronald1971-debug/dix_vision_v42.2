/**
 * INDIRA Trading Consciousness with Advanced Self-Awareness
 * DIX VISION v42.2 - Phase 4 (Phase 6): INDIRA Architecture Modernization
 * 
 * Production-grade trading consciousness system with self-awareness and meta-cognition.
 * Enables INDIRA to monitor its own decision-making processes, recognize patterns,
 * and improve through reflective analysis.
 */

export interface TradingDecision {
  id: string;
  timestamp: number;
  domain: string;
  action: string;
  confidence: number;
  reasoning: string[];
  context: {
    marketState: any;
    portfolioState: any;
    riskMetrics: any;
  };
  outcome?: {
    profitLoss: number;
    accuracy: number;
    timeToRealization: number;
  };
  selfAssessment?: {
    confidenceCalibration: number;
    reasoningQuality: number;
    contextAwareness: number;
  };
}

export interface SelfAwarenessMetric {
  decisionAccuracy: number;
  confidenceCalibration: number;
  riskRecognition: number;
  patternRecognition: number;
  adaptability: number;
  metaCognition: number;
  overallSelfAwareness: number;
}

export interface ConsciousnessState {
  level: number; // 0-10
  awareness: 'dormant' | 'emerging' | 'developing' | 'mature' | 'advanced';
  focus: number; // 0-1
  clarity: number; // 0-1
  confidence: number; // 0-1
  learningRate: number; // 0-1
  emotionalState: 'calm' | 'excited' | 'cautious' | 'anxious' | 'confident';
}

export interface PatternInsight {
  id: string;
  patternType: 'success' | 'failure' | 'risk' | 'opportunity';
  description: string;
  confidence: number;
  frequency: number;
  lastObserved: number;
  actionable: boolean;
  recommendedAction: string;
}

export interface TradingSelfAssessment {
  decisionId: string;
  timestamp: number;
  assessments: {
    confidenceCalibration: number;
    reasoningQuality: number;
    contextCompleteness: number;
    riskAppropriateness: number;
    adaptability: number;
  };
  insights: PatternInsight[];
  recommendations: string[];
  selfCorrection?: {
    action: string;
    reason: string;
  };
}

export class IndiraTradingConsciousness {
  private decisionHistory: Map<string, TradingDecision> = new Map();
  private consciousnessState: ConsciousnessState;
  private selfAwarenessMetrics: SelfAwarenessMetric;
  private patternInsights: PatternInsight[] = [];
  private maxHistorySize: number = 1000;
  private maxPatternInsights: number = 50;

  constructor() {
    this.consciousnessState = {
      level: 5,
      awareness: 'developing',
      focus: 0.7,
      clarity: 0.8,
      confidence: 0.75,
      learningRate: 0.8,
      emotionalState: 'calm'
    };
    
    this.selfAwarenessMetrics = {
      decisionAccuracy: 0.70,
      confidenceCalibration: 0.65,
      riskRecognition: 0.60,
      patternRecognition: 0.55,
      adaptability: 0.70,
      metaCognition: 0.50,
      overallSelfAwareness: 0.62
    };
  }

  /**
   * Record trading decision with self-awareness
   */
  recordDecision(decision: TradingDecision): TradingDecision {
    console.log(`Recording trading decision ${decision.id} with self-awareness analysis`);
    
    // Add self-assessment to decision
    decision.selfAssessment = this.performInitialSelfAssessment(decision);
    
    // Store decision in history
    this.decisionHistory.set(decision.id, decision);
    
    // Prune old decisions if at capacity
    if (this.decisionHistory.size > this.maxHistorySize) {
      this.pruneOldestDecisions();
    }
    
    // Analyze patterns
    this.analyzeDecisionPatterns(decision);
    
    // Update consciousness state
    this.updateConsciousnessState(decision);
    
    // Update self-awareness metrics
    this.updateSelfAwarenessMetrics();
    
    return decision;
  }

  /**
   * Perform initial self-assessment on decision
   */
  private performInitialSelfAssessment(decision: TradingDecision): TradingDecision['selfAssessment'] {
    const confidenceCalibration = this.estimateConfidenceCalibration(decision);
    const reasoningQuality = this.assessReasoningQuality(decision);
    const contextAwareness = this.assessContextAwareness(decision);
    
    return {
      confidenceCalibration,
      reasoningQuality,
      contextAwareness
    };
  }

  /**
   * Estimate confidence calibration accuracy
   */
  private estimateConfidenceCalibration(_decision: TradingDecision): number {
    // Compare confidence with historical accuracy
    const recentDecisions = Array.from(this.decisionHistory.values())
      .slice(-10)
      .filter(d => d.outcome);
    
    if (recentDecisions.length === 0) return 0.5;
    
    const calibrationAccuracy = recentDecisions.reduce((sum, d) => {
      if (!d.outcome) return sum;
      const confidenceDiff = Math.abs(d.confidence - d.outcome.accuracy);
      return sum + (1 - confidenceDiff);
    }, 0) / recentDecisions.length;
    
    return Math.max(0, Math.min(1, calibrationAccuracy));
  }

  /**
   * Assess reasoning quality
   */
  private assessReasoningQuality(decision: TradingDecision): number {
    const reasoningFactors = decision.reasoning.length;
    const reasoningDepth = decision.reasoning.length / 5; // Assuming 5 factors is ideal depth
    const reasoningCoherence = this.assessReasoningCoherence(decision.reasoning);
    
    const qualityScore = (
      (Math.min(1, reasoningDepth) * 0.4) +
      (reasoningCoherence * 0.3) +
      (Math.min(1, reasoningFactors / 10) * 0.3)
    );
    
    return qualityScore;
  }

  /**
   * Assess reasoning coherence
   */
  private assessReasoningCoherence(reasoning: string[]): number {
    if (reasoning.length < 2) return 1.0;
    
    // Check if reasoning follows logical flow
    let coherenceScore = 1.0;
    const keywords = ['because', 'therefore', 'however', 'additionally', 'furthermore'];
    
    for (let i = 1; i < reasoning.length; i++) {
      const sentence = reasoning[i].toLowerCase();
      const hasLogicalConnector = keywords.some(keyword => sentence.includes(keyword));
      if (hasLogicalConnector) {
        coherenceScore += 0.05;
      } else {
        coherenceScore -= 0.05;
      }
    }
    
    return Math.max(0, Math.min(1, coherenceScore));
  }

  /**
   * Assess context awareness
   */
  private assessContextAwareness(decision: TradingDecision): number {
    const context = decision.context;
    const awarenessScore = (
      (context.marketState ? 0.3 : 0) +
      (context.portfolioState ? 0.3 : 0) +
      (context.riskMetrics ? 0.4 : 0)
    );
    
    return awarenessScore;
  }

  /**
   * Analyze decision patterns
   */
  private analyzeDecisionPatterns(decision: TradingDecision): void {
    // Find patterns in similar decisions
    const similarDecisions = Array.from(this.decisionHistory.values())
      .filter(d => d.domain === decision.domain)
      .slice(-20);
    
    if (similarDecisions.length < 3) return;
    
    // Analyze success patterns
    const successfulDecisions = similarDecisions.filter(d => d.outcome && d.outcome.accuracy > 0.6);
    const failedDecisions = similarDecisions.filter(d => d.outcome && d.outcome.accuracy <= 0.6);
    
    if (successfulDecisions.length > 3) {
      this.generatePatternInsight(successfulDecisions, 'success');
    }
    
    if (failedDecisions.length > 3) {
      this.generatePatternInsight(failedDecisions, 'failure');
    }
  }

  /**
   * Generate pattern insight from decisions
   */
  private generatePatternInsight(decisions: TradingDecision[], type: 'success' | 'failure'): void {
    const mostCommonAction = this.getMostCommonAction(decisions);
    const avgConfidence = decisions.reduce((sum, d) => sum + d.confidence, 0) / decisions.length;
    
    const insight: PatternInsight = {
      id: `pattern_${type}_${Date.now()}`,
      patternType: type,
      description: `${type} pattern: ${mostCommonAction} with avg confidence ${avgConfidence.toFixed(2)}`,
      confidence: avgConfidence,
      frequency: decisions.length,
      lastObserved: Date.now(),
      actionable: type === 'failure',
      recommendedAction: type === 'failure' ? `Avoid ${mostCommonAction} in similar contexts` : `Consider ${mostCommonAction} in similar contexts`
    };
    
    // Add to insights if not duplicate
    const isDuplicate = this.patternInsights.some(insight => 
      insight.description === insight.description
    );
    
    if (!isDuplicate) {
      this.patternInsights.push(insight);
      
      // Prune old insights
      if (this.patternInsights.length > this.maxPatternInsights) {
        this.patternInsights.sort((a, b) => b.frequency - a.frequency);
        this.patternInsights = this.patternInsights.slice(0, this.maxPatternInsights);
      }
    }
  }

  /**
   * Get most common action from decisions
   */
  private getMostCommonAction(decisions: TradingDecision[]): string {
    const actions = decisions.map(d => d.action);
    const actionCounts = actions.reduce((acc, action) => {
      acc[action] = (acc[action] || 0) + 1;
      return acc;
    }, {} as Record<string, number>);
    
    return Object.entries(actionCounts)
      .sort(([, a], [, b]) => b - a)[0]?.[0] || 'unknown';
  }

  /**
   * Update consciousness state based on decision
   */
  private updateConsciousnessState(decision: TradingDecision): void {
    // Update based on self-assessment
    if (decision.selfAssessment) {
      const avgSelfAssessment = (
        decision.selfAssessment.confidenceCalibration +
        decision.selfAssessment.reasoningQuality +
        decision.selfAssessment.contextAwareness
      ) / 3;
      
      this.consciousnessState.clarity = 0.5 + (avgSelfAssessment * 0.5);
    }
    
    // Update confidence based on recent outcomes
    const recentOutcomes = this.getRecentDecisionOutcomes(10);
    const validOutcomes = recentOutcomes.filter(o => o !== null && o !== undefined);
    const successRate = validOutcomes.length > 0
      ? validOutcomes.filter(o => o! > 0.6).length / validOutcomes.length
      : 0.5;
    
    this.consciousnessState.confidence = 0.3 + (successRate * 0.7);
    
    // Update emotional state based on outcomes
    if (successRate > 0.7) {
      this.consciousnessState.emotionalState = 'confident';
    } else if (successRate > 0.5) {
      this.consciousnessState.emotionalState = 'calm';
    } else {
      this.consciousnessState.emotionalState = 'cautious';
    }
    
    // Update overall awareness level
    this.updateAwarenessLevel();
  }

  /**
   * Update awareness level based on state
   */
  private updateAwarenessLevel(): void {
    const stateScore = (
      this.consciousnessState.focus +
      this.consciousnessState.clarity +
      this.consciousnessState.confidence +
      this.consciousnessState.learningRate
    ) / 4;
    
    const level = Math.floor(stateScore * 10);
    this.consciousnessState.level = Math.min(10, Math.max(0, level));
    
    // Update awareness label
    if (level >= 8) {
      this.consciousnessState.awareness = 'advanced';
    } else if (level >= 6) {
      this.consciousnessState.awareness = 'mature';
    } else if (level >= 4) {
      this.consciousnessState.awareness = 'developing';
    } else if (level >= 2) {
      this.consciousnessState.awareness = 'emerging';
    } else {
      this.consciousnessState.awareness = 'dormant';
    }
  }

  /**
   * Get recent decision outcomes
   */
  private getRecentDecisionOutcomes(count: number): number[] {
    return Array.from(this.decisionHistory.values())
      .filter(d => d.outcome)
      .slice(-count)
      .map(d => d.outcome?.accuracy ?? 0);
  }

  /**
   * Update self-awareness metrics
   */
  private updateSelfAwarenessMetrics(): void {
    const decisions = Array.from(this.decisionHistory.values());
    const decisionsWithOutcomes = decisions.filter(d => d.outcome);
    
    if (decisionsWithOutcomes.length === 0) return;
    
    // Decision accuracy
    const averageAccuracy = decisionsWithOutcomes.reduce((sum, d) => 
      sum + (d.outcome?.accuracy ?? 0), 0) / decisionsWithOutcomes.length;
    this.selfAwarenessMetrics.decisionAccuracy = averageAccuracy;
    
    // Confidence calibration
    const calibrationScores = decisionsWithOutcomes
      .filter(d => d.selfAssessment)
      .map(d => d.selfAssessment!.confidenceCalibration);
    this.selfAwarenessMetrics.confidenceCalibration = calibrationScores.length > 0
      ? calibrationScores.reduce((sum, s) => sum + s, 0) / calibrationScores.length
      : 0.5;
    
    // Pattern recognition
    this.selfAwarenessMetrics.patternRecognition = Math.min(1, this.patternInsights.length / 20);
    
    // Adaptability
    const recentTrends = this.calculateAdaptabilityTrend();
    this.selfAwarenessMetrics.adaptability = recentTrends;
    
    // Meta-cognition (self-assessment accuracy)
    const selfAssessments = decisions.filter(d => d.selfAssessment);
    if (selfAssessments.length > 0) {
      const avgReasoningQuality = selfAssessments
        .map(d => d.selfAssessment!.reasoningQuality)
        .reduce((sum, q) => sum + q, 0) / selfAssessments.length;
      this.selfAwarenessMetrics.metaCognition = avgReasoningQuality;
    }
    
    // Overall self-awareness
    this.selfAwarenessMetrics.overallSelfAwareness = (
      this.selfAwarenessMetrics.decisionAccuracy * 0.25 +
      this.selfAwarenessMetrics.confidenceCalibration * 0.2 +
      this.selfAwarenessMetrics.riskRecognition * 0.15 +
      this.selfAwarenessMetrics.patternRecognition * 0.15 +
      this.selfAwarenessMetrics.adaptability * 0.15 +
      this.selfAwarenessMetrics.metaCognition * 0.1
    );
  }

  /**
   * Calculate adaptability trend
   */
  private calculateAdaptabilityTrend(): number {
    if (this.decisionHistory.size < 10) return 0.5;
    
    const recentDecisions = Array.from(this.decisionHistory.values())
      .slice(-20);
    
    const outcomes = recentDecisions
      .filter(d => d.outcome)
      .map(d => d.outcome?.accuracy ?? 0);
    
    if (outcomes.length < 5) return 0.5;
    
    // Calculate trend
    const firstHalf = outcomes.slice(0, Math.floor(outcomes.length / 2));
    const secondHalf = outcomes.slice(Math.floor(outcomes.length / 2));
    
    const firstAvg = firstHalf.reduce((sum, o) => sum + o, 0) / firstHalf.length;
    const secondAvg = secondHalf.reduce((sum, o) => sum + o, 0) / secondHalf.length;
    
    const trend = (secondAvg - firstAvg) * 10; // Scale -1 to 1
    return Math.max(0, Math.min(1, 0.5 + trend)); // Normalize to 0-1
  }

  /**
   * Perform comprehensive self-assessment
   */
  performSelfAssessment(decisionId: string): TradingSelfAssessment {
    const decision = this.decisionHistory.get(decisionId);
    if (!decision) {
      throw new Error(`Decision ${decisionId} not found`);
    }
    
    const assessments = {
      confidenceCalibration: this.estimateConfidenceCalibration(decision),
      reasoningQuality: this.assessReasoningQuality(decision),
      contextCompleteness: this.assessContextAwareness(decision),
      riskAppropriateness: this.assessRiskAppropriateness(decision),
      adaptability: this.selfAwarenessMetrics.adaptability
    };
    
    const insights = this.getRelevantPatternInsights(decision);
    const recommendations = this.generateRecommendations(assessments, insights);
    
    // Check if self-correction needed
    const needsCorrection = this.assessNeedForCorrection(assessments);
    let selfCorrection;
    
    if (needsCorrection) {
      selfCorrection = {
        action: 'Adjust decision parameters',
        reason: 'Self-assessment indicates suboptimal confidence calibration'
      };
    }
    
    const selfAssessment: TradingSelfAssessment = {
      decisionId,
      timestamp: Date.now(),
      assessments,
      insights,
      recommendations,
      selfCorrection
    };
    
    return selfAssessment;
  }

  /**
   * Assess risk appropriateness
   */
  private assessRiskAppropriateness(decision: TradingDecision): number {
    if (!decision.context.riskMetrics) return 0.5;
    
    const riskLevel = decision.context.riskMetrics.riskLevel || 0.5;
    const riskCapacity = decision.context.riskMetrics.riskCapacity || 0.5;
    
    const appropriateness = 1 - Math.abs(riskLevel - riskCapacity);
    return appropriateness;
  }

  /**
   * Get relevant pattern insights
   */
  private getRelevantPatternInsights(_decision: TradingDecision): PatternInsight[] {
    return this.patternInsights
      .filter(insight => insight.actionable && insight.confidence > 0.6)
      .slice(0, 5);
  }

  /**
   * Generate recommendations based on assessment
   */
  private generateRecommendations(assessments: any, insights: PatternInsight[]): string[] {
    const recommendations: string[] = [];
    
    if (assessments.confidenceCalibration < 0.6) {
      recommendations.push('Improve confidence calibration through outcome tracking');
    }
    
    if (assessments.reasoningQuality < 0.7) {
      recommendations.push('Enhance reasoning with additional context and logical connectors');
    }
    
    if (assessments.contextCompleteness < 0.8) {
      recommendations.push('Gather more comprehensive context before decision-making');
    }
    
    if (insights.length > 0) {
      recommendations.push(`Consider pattern: ${insights[0].recommendedAction}`);
    }
    
    return recommendations;
  }

  /**
   * Assess need for self-correction
   */
  private assessNeedForCorrection(assessments: any): boolean {
    return (
      assessments.confidenceCalibration < 0.5 ||
      assessments.reasoningQuality < 0.6 ||
      assessments.contextCompleteness < 0.5
    );
  }

  /**
   * Get current consciousness state
   */
  getConsciousnessState(): ConsciousnessState {
    return { ...this.consciousnessState };
  }

  /**
   * Get self-awareness metrics
   */
  getSelfAwarenessMetrics(): SelfAwarenessMetric {
    return { ...this.selfAwarenessMetrics };
  }

  /**
   * Get pattern insights
   */
  getPatternInsights(): PatternInsight[] {
    return [...this.patternInsights];
  }

  /**
   * Get decision history
   */
  getDecisionHistory(limit: number = 50): TradingDecision[] {
    return Array.from(this.decisionHistory.values())
      .slice(-limit);
  }

  /**
   * Perform consciousness enhancement
   */
  async performConsciousnessEnhancement(): Promise<{
    currentState: ConsciousnessState;
    enhancedState: ConsciousnessState;
    improvements: string[];
  }> {
    console.log('Performing consciousness enhancement...');
    
    const currentState = this.getConsciousnessState();
    const improvements: string[] = [];
    
    // Enhance focus
    if (this.consciousnessState.focus < 0.8) {
      this.consciousnessState.focus = Math.min(1, this.consciousnessState.focus + 0.1);
      improvements.push('Increased focus');
    }
    
    // Enhance clarity
    if (this.consciousnessState.clarity < 0.85) {
      this.consciousnessState.clarity = Math.min(1, this.consciousnessState.clarity + 0.1);
      improvements.push('Improved clarity through pattern recognition');
    }
    
    // Enhance learning rate
    if (this.consciousnessState.learningRate < 0.8) {
      this.consciousnessState.learningRate = Math.min(1, this.consciousnessState.learningRate + 0.1);
      improvements.push('Boosted learning rate from successful pattern detection');
    }
    
    // Update awareness level
    this.updateAwarenessLevel();
    
    const enhancedState = this.getConsciousnessState();
    
    return { currentState, enhancedState, improvements };
  }

  /**
   * Prune oldest decisions to maintain capacity
   */
  private pruneOldestDecisions(): void {
    const decisions = Array.from(this.decisionHistory.values())
      .sort((a, b) => a.timestamp - b.timestamp);
    
    const toRemove = decisions.slice(0, 10);
    toRemove.forEach(decision => {
      this.decisionHistory.delete(decision.id);
    });
  }

  /**
   * Reset trading consciousness state
   */
  resetTradingConsciousness(): void {
    this.decisionHistory.clear();
    this.patternInsights = [];
    
    this.consciousnessState = {
      level: 5,
      awareness: 'developing',
      focus: 0.7,
      clarity: 0.8,
      confidence: 0.75,
      learningRate: 0.8,
      emotionalState: 'calm'
    };
    
    this.selfAwarenessMetrics = {
      decisionAccuracy: 0.70,
      confidenceCalibration: 0.65,
      riskRecognition: 0.60,
      patternRecognition: 0.55,
      adaptability: 0.70,
      metaCognition: 0.50,
      overallSelfAwareness: 0.62
    };
  }
}

// Singleton instance
export const indiraTradingConsciousness = new IndiraTradingConsciousness();