/**
 * Monte Carlo Simulation
 * DIX VISION v42.2 - Phase 13: Backtesting and Simulation Framework (Weeks 41-44)
 */

export interface MonteCarloSimulation {
  simulationId: string;
  strategyId: string;
  config: SimulationConfig;
  results: SimulationResults;
  distributions: ProbabilityDistribution[];
  confidenceIntervals: ConfidenceInterval[];
  riskMetrics: SimulationRiskMetrics;
  timestamp: number;
}

export interface SimulationConfig {
  numSimulations: number;
  timeHorizon: number;
  initialCapital: number;
  assetReturns: number[];
  volatilities: number[];
  correlations?: number[][];
  randomSeed?: number;
}

export interface SimulationResults {
  finalValues: number[];
  meanFinalValue: number;
  medianFinalValue: number;
  stdFinalValue: number;
  percentile5: number;
  percentile25: number;
  percentile75: number;
  percentile95: number;
  probabilityOfSuccess: number;
  expectedReturn: number;
}

export interface ProbabilityDistribution {
  finalValue: number;
  probability: number;
  cumulativeProbability: number;
}

export interface ConfidenceInterval {
  level: number;
  lowerBound: number;
  upperBound: number;
  mean: number;
}

export interface SimulationRiskMetrics {
  valueAtRisk95: number;
  valueAtRisk99: number;
  conditionalVaR95: number;
  expectedShortfall: number;
  probabilityOfLoss: number;
  maxLoss: number;
  riskOfRuin: number;
}

class MonteCarloSimulationEngine {
  private simulations: Map<string, MonteCarloSimulation> = new Map();

  async runSimulation(strategyId: string, config: SimulationConfig): Promise<MonteCarloSimulation> {
    const finalValues: number[] = [];

    for (let i = 0; i < config.numSimulations; i++) {
      const simulationResult = this.runSingleSimulation(config);
      finalValues.push(simulationResult);
    }

    finalValues.sort((a, b) => a - b);

    const results: SimulationResults = {
      finalValues,
      meanFinalValue: finalValues.reduce((sum, v) => sum + v, 0) / finalValues.length,
      medianFinalValue: finalValues[Math.floor(finalValues.length / 2)],
      stdFinalValue: Math.sqrt(finalValues.reduce((sum, v) => sum + Math.pow(v - (finalValues.reduce((s, v) => s + v, 0) / finalValues.length), 2), 0) / finalValues.length),
      percentile5: finalValues[Math.floor(finalValues.length * 0.05)],
      percentile25: finalValues[Math.floor(finalValues.length * 0.25)],
      percentile75: finalValues[Math.floor(finalValues.length * 0.75)],
      percentile95: finalValues[Math.floor(finalValues.length * 0.95)],
      probabilityOfSuccess: finalValues.filter(v => v > config.initialCapital).length / finalValues.length,
      expectedReturn: (finalValues.reduce((sum, v) => sum + v, 0) / finalValues.length - config.initialCapital) / config.initialCapital
    };

    const distributions = this.calculateDistributions(finalValues);
    const confidenceIntervals = this.calculateConfidenceIntervals(finalValues, results);
    const riskMetrics = this.calculateRiskMetrics(finalValues, config);

    const simulation: MonteCarloSimulation = {
      simulationId: `monte_carlo_${Date.now()}`,
      strategyId,
      config,
      results,
      distributions,
      confidenceIntervals,
      riskMetrics,
      timestamp: Date.now()
    };

    this.simulations.set(simulation.simulationId, simulation);
    return simulation;
  }

  private runSingleSimulation(config: SimulationConfig): number {
    let capital = config.initialCapital;
    const returns = config.assetReturns;

    for (let i = 0; i < config.timeHorizon; i++) {
      const dailyReturn = returns[Math.floor(Math.random() * returns.length)];
      capital = capital * (1 + dailyReturn);
      
      if (capital < 0) break; // Account for ruin
    }

    return capital;
  }

  private calculateDistributions(finalValues: number[]): ProbabilityDistribution[] {
    const total = finalValues.length;
    const distributions: ProbabilityDistribution[] = [];

    finalValues.forEach((value, index) => {
      const probability = 1 / total;
      const cumulative = (index + 1) / total;

      distributions.push({
        finalValue: value,
        probability,
        cumulativeProbability: cumulative
      });
    });

    return distributions;
  }

  private calculateConfidenceIntervals(finalValues: number[], results: SimulationResults): ConfidenceInterval[] {
    const intervals: ConfidenceInterval[] = [
      { level: 95, lowerBound: results.percentile5, upperBound: results.percentile95, mean: results.meanFinalValue },
      { level: 90, lowerBound: finalValues[Math.floor(finalValues.length * 0.05)], upperBound: finalValues[Math.floor(finalValues.length * 0.95)], mean: results.meanFinalValue },
      { level: 80, lowerBound: finalValues[Math.floor(finalValues.length * 0.1)], upperBound: finalValues[Math.floor(finalValues.length * 0.9)], mean: results.meanFinalValue },
      { level: 50, lowerBound: finalValues[Math.floor(finalValues.length * 0.25)], upperBound: finalValues[Math.floor(finalValues.length * 0.75)], mean: results.meanFinalValue }
    ];

    return intervals;
  }

  private calculateRiskMetrics(finalValues: number[], config: SimulationConfig): SimulationRiskMetrics {
    const meanValue = finalValues.reduce((sum, v) => sum + v, 0) / finalValues.length;
    const losses = finalValues.filter(v => v < meanValue).sort((a, b) => a - b);

    const var95 = losses[Math.floor(losses.length * 0.05)] || meanValue;
    const var99 = losses[Math.floor(losses.length * 0.01)] || meanValue;

    const tailLosses = losses.filter(v => v < var95);
    const cvar95 = tailLosses.length > 0 ? tailLosses.reduce((sum, v) => sum + v, 0) / tailLosses.length : meanValue;

    return {
      valueAtRisk95: meanValue - var95,
      valueAtRisk99: meanValue - var99,
      conditionalVaR95: meanValue - cvar95,
      expectedShortfall: (meanValue - cvar95) / meanValue,
      probabilityOfLoss: finalValues.filter(v => v < config.initialCapital).length / finalValues.length,
      maxLoss: Math.min(...finalValues),
      riskOfRuin: finalValues.filter(v => v <= 0).length / finalValues.length
    };
  }

  getSimulation(simulationId: string): MonteCarloSimulation | undefined {
    return this.simulations.get(simulationId);
  }

  getAllSimulations(): MonteCarloSimulation[] {
    return Array.from(this.simulations.values());
  }
}

export const monteCarloSimulationEngine = new MonteCarloSimulationEngine();
export default MonteCarloSimulationEngine;