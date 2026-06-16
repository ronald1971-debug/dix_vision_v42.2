/**
 * Backtesting and Simulation Framework - Phase 13 Index
 * DIX VISION v42.2 - Phase 13: Backtesting and Simulation Framework (Weeks 41-44)
 */

export { backtestEngine } from '../BacktestEngine';
export type {
  BacktestEngine,
  BacktestConfig,
  BacktestResults,
  BacktestPerformance,
  Trade,
  EquityPoint
} from '../BacktestEngine';

export { walkForwardAnalysisEngine } from '../WalkForwardAnalysis';
export type {
  WalkForwardAnalysis,
  WalkForwardSegment,
  DateRange,
  WalkForwardResults,
  PerformanceComparison,
  ParameterStability,
  WalkForwardConfig
} from '../WalkForwardAnalysis';

export { monteCarloSimulationEngine } from '../MonteCarloSimulation';
export type {
  MonteCarloSimulation,
  SimulationConfig,
  SimulationResults,
  ProbabilityDistribution,
  ConfidenceInterval,
  SimulationRiskMetrics
} from '../MonteCarloSimulation';

export { scenarioAnalysisEngine } from '../ScenarioAnalysis';
export type {
  ScenarioAnalysis,
  Scenario,
  ScenarioParameters,
  ScenarioComparison,
  SensitivityAnalysis,
  SensitivityFactor,
  FactorInteraction,
  StressTestResults,
  StressScenario,
  ScenarioConfig
} from '../ScenarioAnalysis';