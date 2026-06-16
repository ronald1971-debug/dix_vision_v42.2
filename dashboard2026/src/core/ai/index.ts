/**
 * Dashboard2026 AI Core Module
 * DIX VISION v42.2 - Phase: AI Intelligence Enhancement
 * 
 * Central AI orchestration and intelligence module that extends
 * INDIRA and DYON capabilities across the entire dashboard.
 */

export { UnifiedAIOrchestrator, getAIOrchestrator, initializeAIOrchestrator } from './UnifiedAIOrchestrator';
export { getPerformanceMonitor } from './PerformanceMonitoringSystem';

export type {
  AIContext,
  AIAssistant,
  AIRecommendation,
  AIPrediction,
  AIOrchestrationConfig
} from './UnifiedAIOrchestrator';

export type {
  PerformanceMetrics,
  TakeoverEvent,
  SafetyCheckResult,
  TakeoverProtocol
} from './PerformanceMonitoringSystem';