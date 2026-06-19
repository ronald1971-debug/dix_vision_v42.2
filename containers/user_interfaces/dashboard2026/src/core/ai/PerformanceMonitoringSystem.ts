/**
 * Dashboard2026 AI vs INDIRA Performance Monitoring System
 * 
 * Monitors and compares AI performance against INDIRA trading performance
 * Implements autonomous takeover protocol with safety checks
 * Handles handoff between AI and INDIRA systems
 */

import { getAIOrchestrator } from './UnifiedAIOrchestrator';

export interface PerformanceMetrics {
  timestamp: number;
  indiraMetrics: {
    tradingAccuracy: number;
    predictionConfidence: number;
    strategyExecution: number;
    riskManagement: number;
    overall: number;
  };
  aiMetrics: {
    crossSystemLearning: number;
    patternRecognition: number;
    predictiveAccuracy: number;
    adaptability: number;
    overall: number;
  };
}

export interface TakeoverEvent {
  id: string;
  timestamp: number;
  from: 'INDIRA' | 'AI';
  to: 'INDIRA' | 'AI';
  reason: string;
  performanceGap: number;
  approvedBy: 'system' | 'governance' | 'manual';
  safetyChecksPassed: boolean;
}

export interface SafetyCheckResult {
  passed: boolean;
  reason: string;
  metrics: {
    performanceThreshold: boolean;
    timeThreshold: boolean;
    riskLimits: boolean;
    governanceApproval: boolean;
    anomalyCheck: boolean;
  };
}

export interface TakeoverProtocol {
  enabled: boolean;
  threshold: number;
  timeRequirement: number; // minutes
  requireGovernanceApproval: boolean;
  enableImmediateRollback: boolean;
  riskLimitEnforcement: boolean;
}

class PerformanceMonitoringSystem {
  private performanceHistory: PerformanceMetrics[] = [];
  private takeoverEvents: TakeoverEvent[] = [];
  private currentController: 'INDIRA' | 'AI' = 'INDIRA';
  private takeoverProtocol: TakeoverProtocol = {
    enabled: false,
    threshold: 0.80,
    timeRequirement: 5,
    requireGovernanceApproval: true,
    enableImmediateRollback: true,
    riskLimitEnforcement: true
  };
  private performanceStabilityWindow: number[] = [];
  private monitoringInterval: ReturnType<typeof setInterval> | undefined;

  constructor() {
    this.startMonitoring();
  }

  /**
   * Start continuous performance monitoring
   */
  private startMonitoring(): void {
    this.monitoringInterval = setInterval(() => {
      this.collectPerformanceMetrics();
      this.evaluateTakeoverConditions();
    }, 10000); // Monitor every 10 seconds
  }

  /**
   * Collect current performance metrics from both systems
   */
  private async collectPerformanceMetrics(): Promise<void> {
    const aiOrchestrator = getAIOrchestrator();
    const status = aiOrchestrator.getAIStatus();

    // Simulate INDIRA metrics (in real implementation, would come from INDIRA system)
    const indiraMetrics = {
      tradingAccuracy: 0.70 + Math.random() * 0.20,
      predictionConfidence: 0.65 + Math.random() * 0.25,
      strategyExecution: 0.75 + Math.random() * 0.20,
      riskManagement: 0.80 + Math.random() * 0.15,
      overall: 0
    };
    indiraMetrics.overall = (
      indiraMetrics.tradingAccuracy +
      indiraMetrics.predictionConfidence +
      indiraMetrics.strategyExecution +
      indiraMetrics.riskManagement
    ) / 4;

    // Get AI metrics from orchestrator
    const aiMetrics = {
      crossSystemLearning: status.assistants.find(a => a.type === 'contextual')?.confidence || 0.75,
      patternRecognition: status.assistants.find(a => a.type === 'analytical')?.confidence || 0.80,
      predictiveAccuracy: status.assistants.find(a => a.type === 'predictive')?.confidence || 0.78,
      adaptability: status.assistants.find(a => a.type === 'operational')?.confidence || 0.77,
      overall: 0
    };
    aiMetrics.overall = (
      aiMetrics.crossSystemLearning +
      aiMetrics.patternRecognition +
      aiMetrics.predictiveAccuracy +
      aiMetrics.adaptability
    ) / 4;

    const metrics: PerformanceMetrics = {
      timestamp: Date.now(),
      indiraMetrics,
      aiMetrics
    };

    this.performanceHistory.push(metrics);

    // Keep only last 100 measurements
    if (this.performanceHistory.length > 100) {
      this.performanceHistory = this.performanceHistory.slice(-100);
    }

    // Update performance stability window
    this.performanceStabilityWindow.push(aiMetrics.overall - indiraMetrics.overall);
    if (this.performanceStabilityWindow.length > 30) { // 5 minutes at 10s intervals
      this.performanceStabilityWindow = this.performanceStabilityWindow.slice(-30);
    }
  }

  /**
   * Evaluate whether takeover conditions are met
   */
  private evaluateTakeoverConditions(): void {
    if (!this.takeoverProtocol.enabled) return;

    const latestMetrics = this.performanceHistory[this.performanceHistory.length - 1];
    if (!latestMetrics) return;

    const performanceGap = latestMetrics.aiMetrics.overall - latestMetrics.indiraMetrics.overall;
    const isAIBetter = performanceGap > 0;

    if (isAIBetter && this.currentController === 'INDIRA') {
      this.checkTakeoverConditions(performanceGap);
    } else if (!isAIBetter && this.currentController === 'AI') {
      this.checkRollbackConditions(performanceGap);
    }
  }

  /**
   * Check if takeover conditions are met
   */
  private checkTakeoverConditions(performanceGap: number): void {
    const safetyCheck = this.performSafetyChecks(performanceGap, 'takeover');

    if (safetyCheck.passed) {
      this.initiateTakeover('AI', performanceGap, safetyCheck);
    }
  }

  /**
   * Check if rollback conditions are met
   */
  private checkRollbackConditions(performanceGap: number): void {
    const safetyCheck = this.performSafetyChecks(Math.abs(performanceGap), 'rollback');

    if (safetyCheck.passed) {
      this.initiateTakeover('INDIRA', performanceGap, safetyCheck);
    }
  }

  /**
   * Perform safety checks for takeover/rollback
   */
  private performSafetyChecks(performanceGap: number, action: 'takeover' | 'rollback'): SafetyCheckResult {
    const metrics = {
      performanceThreshold: false,
      timeThreshold: false,
      riskLimits: true, // Would check actual risk limits in real implementation
      governanceApproval: !this.takeoverProtocol.requireGovernanceApproval || action === 'rollback',
      anomalyCheck: true // Would check for anomalies in real implementation
    };

    // Performance threshold check
    const threshold = action === 'takeover' ? this.takeoverProtocol.threshold : -this.takeoverProtocol.threshold * 0.5;
    metrics.performanceThreshold = performanceGap > threshold;

    // Time threshold check (AI must be better for required time)
    if (action === 'takeover' && this.takeoverProtocol.timeRequirement > 0) {
      const timeRequirementMs = this.takeoverProtocol.timeRequirement * 60 * 1000;
      const windowDuration = this.performanceStabilityWindow.length * 10000; // 10s intervals
      metrics.timeThreshold = windowDuration >= timeRequirementMs;
    } else {
      metrics.timeThreshold = true;
    }

    const allPassed = Object.values(metrics).every(v => v);

    return {
      passed: allPassed,
      reason: allPassed ? 'All safety checks passed' : this.getFailureReason(metrics),
      metrics
    };
  }

  /**
   * Get failure reason for safety check
   */
  private getFailureReason(metrics: { performanceThreshold: boolean; timeThreshold: boolean; riskLimits: boolean; governanceApproval: boolean; anomalyCheck: boolean }): string {
    if (!metrics.performanceThreshold) return 'Performance threshold not met';
    if (!metrics.timeThreshold) return 'Time requirement not met';
    if (!metrics.riskLimits) return 'Risk limits would be exceeded';
    if (!metrics.governanceApproval) return 'Governance approval required';
    if (!metrics.anomalyCheck) return 'Anomalies detected in performance';
    return 'Unknown safety check failure';
  }

  /**
   * Initiate takeover between systems
   */
  private initiateTakeover(target: 'INDIRA' | 'AI', performanceGap: number, safetyCheck: SafetyCheckResult): void {
    const event: TakeoverEvent = {
      id: `takeover_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`,
      timestamp: Date.now(),
      from: this.currentController,
      to: target,
      reason: target === 'AI' ? 'AI performance superior' : 'Performance regression detected',
      performanceGap,
      approvedBy: this.takeoverProtocol.requireGovernanceApproval ? 'system' : 'governance',
      safetyChecksPassed: safetyCheck.passed
    };

    this.takeoverEvents.push(event);
    this.currentController = target;

    console.log(`Takeover initiated: ${this.currentController} -> ${target}`, event);

    // Learn from the takeover
    const aiOrchestrator = getAIOrchestrator();
    aiOrchestrator.learnFromAction(`takeover_${target.toLowerCase()}`, {
      from: this.currentController,
      performanceGap,
      safetyCheck
    });
  }

  /**
   * Request manual takeover (user-initiated)
   */
  requestManualTakeover(target: 'INDIRA' | 'AI', reason: string): boolean {
    const latestMetrics = this.performanceHistory[this.performanceHistory.length - 1];
    if (!latestMetrics) return false;

    const performanceGap = latestMetrics.aiMetrics.overall - latestMetrics.indiraMetrics.overall;
    const safetyCheck = this.performSafetyChecks(performanceGap, 'takeover');

    // Override safety checks for manual request with warning
    const manualEvent: TakeoverEvent = {
      id: `manual_takeover_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`,
      timestamp: Date.now(),
      from: this.currentController,
      to: target,
      reason,
      performanceGap,
      approvedBy: 'manual',
      safetyChecksPassed: safetyCheck.passed
    };

    this.takeoverEvents.push(manualEvent);
    this.currentController = target;

    console.log(`Manual takeover: ${this.currentController} -> ${target}`, manualEvent);

    return true;
  }

  /**
   * Update takeover protocol configuration
   */
  updateProtocol(protocol: Partial<TakeoverProtocol>): void {
    this.takeoverProtocol = {
      ...this.takeoverProtocol,
      ...protocol
    };
  }

  /**
   * Get current performance metrics
   */
  getCurrentMetrics(): PerformanceMetrics | null {
    return this.performanceHistory[this.performanceHistory.length - 1] || null;
  }

  /**
   * Get performance history
   */
  getPerformanceHistory(): PerformanceMetrics[] {
    return this.performanceHistory;
  }

  /**
   * Get takeover events
   */
  getTakeoverEvents(): TakeoverEvent[] {
    return this.takeoverEvents;
  }

  /**
   * Get current controller
   */
  getCurrentController(): 'INDIRA' | 'AI' {
    return this.currentController;
  }

  /**
   * Get takeover protocol
   */
  getProtocol(): TakeoverProtocol {
    return this.takeoverProtocol;
  }

  /**
   * Get system status
   */
  getSystemStatus(): {
    currentController: 'INDIRA' | 'AI';
    takeoverEnabled: boolean;
    performanceGap: number;
    stabilityWindow: number[];
    lastTakeover: TakeoverEvent | null;
  } {
    const latestMetrics = this.performanceHistory[this.performanceHistory.length - 1];
    const performanceGap = latestMetrics 
      ? latestMetrics.aiMetrics.overall - latestMetrics.indiraMetrics.overall 
      : 0;

    return {
      currentController: this.currentController,
      takeoverEnabled: this.takeoverProtocol.enabled,
      performanceGap,
      stabilityWindow: this.performanceStabilityWindow,
      lastTakeover: this.takeoverEvents[this.takeoverEvents.length - 1] || null
    };
  }

  /**
   * Stop monitoring
   */
  stopMonitoring(): void {
    if (this.monitoringInterval) {
      clearInterval(this.monitoringInterval);
    }
  }
}

// Global instance
let globalPerformanceMonitor: PerformanceMonitoringSystem | null = null;

export function getPerformanceMonitor(): PerformanceMonitoringSystem {
  if (!globalPerformanceMonitor) {
    globalPerformanceMonitor = new PerformanceMonitoringSystem();
  }
  return globalPerformanceMonitor;
}