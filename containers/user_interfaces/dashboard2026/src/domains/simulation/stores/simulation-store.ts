/**
 * SIMULATION Domain Store
 * 
 * Manages SIMULATION-specific state including backtesting, simulation testing,
 * strategy validation, and performance analysis.
 */

import { create } from 'zustand';
import { devtools, persist } from 'zustand/middleware';

// ============================================================================
// SIMULATION Domain State Types
// ============================================================================

interface SimulationState {
  // Backtesting
  backtestResults: {
    strategyId: string;
    period: {
      start: number;
      end: number;
    };
    performance: {
      totalReturn: number;
      sharpeRatio: number;
      maxDrawdown: number;
      winRate: number;
    };
    trades: number;
    timestamp: number;
  }[];
  
  // Simulation Configuration
  simulationConfig: {
    timeRange: string;
    granularity: string;
    slippage: number;
    commission: number;
    initialCapital: number;
  } | null;
  
  // Strategy Validation
  strategyValidation: {
    [strategyId: string]: {
      status: 'pending' | 'running' | 'completed' | 'failed';
      progress: number;
      results: any;
      errors: string[];
      startTime: number;
    };
  };
  
  // Performance Analysis
  performanceMetrics: {
    equityCurve: number[];
    rollingReturns: number[];
    riskMetrics: {
      volatility: number;
      var: number;
      cvar: number;
    };
    benchmarkComparison: any;
  } | null;
  
  // Testing Queue
  testingQueue: {
    id: string;
    type: 'backtest' | 'forward_test' | 'monte_carlo';
    parameters: any;
    status: 'queued' | 'running' | 'completed' | 'failed';
    priority: number;
    timestamp: number;
  }[];
  
  // UI State
  isLoading: boolean;
  error: string | null;
  selectedBacktest: string | null;
}

interface SimulationActions {
  // Backtest Actions
  addBacktestResult: (result: Omit<SimulationState['backtestResults'][0], 'timestamp'>) => void;
  clearBacktestResults: () => void;
  removeBacktestResult: (strategyId: string) => void;
  
  // Configuration Actions
  setSimulationConfig: (config: SimulationState['simulationConfig']) => void;
  updateSimulationConfig: (config: Partial<SimulationState['simulationConfig']>) => void;
  
  // Validation Actions
  startStrategyValidation: (strategyId: string) => void;
  updateStrategyProgress: (strategyId: string, progress: number) => void;
  completeStrategyValidation: (strategyId: string, results: any) => void;
  failStrategyValidation: (strategyId: string, errors: string[]) => void;
  
  // Performance Actions
  setPerformanceMetrics: (metrics: SimulationState['performanceMetrics']) => void;
  
  // Testing Queue Actions
  addToTestingQueue: (test: Omit<SimulationState['testingQueue'][0], 'timestamp'>) => void;
  updateTestStatus: (id: string, status: SimulationState['testingQueue'][0]['status']) => void;
  removeTest: (id: string) => void;
  
  // UI Actions
  setLoading: (loading: boolean) => void;
  setError: (error: string | null) => void;
  setSelectedBacktest: (id: string | null) => void;
  reset: () => void;
}

type SimulationStore = SimulationState & SimulationActions;

// ============================================================================
// SIMULATION Store Implementation
// ============================================================================

export const useSimulationStore = create<SimulationStore>()(
  devtools(
    persist(
      (set) => ({
        // Initial State
        backtestResults: [],
        simulationConfig: null,
        strategyValidation: {},
        performanceMetrics: null,
        testingQueue: [],
        isLoading: false,
        error: null,
        selectedBacktest: null,
        
        // Backtest Actions
        addBacktestResult: (result) => set((state) => ({
          backtestResults: [
            ...state.backtestResults,
            { ...result, timestamp: Date.now() },
          ],
        })),
        
        clearBacktestResults: () => set({ backtestResults: [] }),
        
        removeBacktestResult: (strategyId) => set((state) => ({
          backtestResults: state.backtestResults.filter(r => r.strategyId !== strategyId),
        })),
        
        // Configuration Actions
        setSimulationConfig: (config) => set({ simulationConfig: config }),
        updateSimulationConfig: (config) => set((state) => ({
          simulationConfig: state.simulationConfig ? {
            ...state.simulationConfig,
            ...config,
          } : null,
        })),
        
        // Validation Actions
        startStrategyValidation: (strategyId) => set((state) => ({
          strategyValidation: {
            ...state.strategyValidation,
            [strategyId]: {
              status: 'running',
              progress: 0,
              results: null,
              errors: [],
              startTime: Date.now(),
            },
          },
        })),
        
        updateStrategyProgress: (strategyId, progress) => set((state) => ({
          strategyValidation: {
            ...state.strategyValidation,
            [strategyId]: state.strategyValidation[strategyId] ? {
              ...state.strategyValidation[strategyId],
              progress,
            } : {
              status: 'pending',
              progress,
              results: null,
              errors: [],
              startTime: Date.now(),
            },
          },
        })),
        
        completeStrategyValidation: (strategyId, results) => set((state) => ({
          strategyValidation: {
            ...state.strategyValidation,
            [strategyId]: state.strategyValidation[strategyId] ? {
              ...state.strategyValidation[strategyId],
              status: 'completed',
              progress: 100,
              results,
            } : {
              status: 'completed',
              progress: 100,
              results,
              errors: [],
              startTime: Date.now(),
            },
          },
        })),
        
        failStrategyValidation: (strategyId, errors) => set((state) => ({
          strategyValidation: {
            ...state.strategyValidation,
            [strategyId]: state.strategyValidation[strategyId] ? {
              ...state.strategyValidation[strategyId],
              status: 'failed',
              errors,
            } : {
              status: 'failed',
              progress: 0,
              results: null,
              errors,
              startTime: Date.now(),
            },
          },
        })),
        
        // Performance Actions
        setPerformanceMetrics: (metrics) => set({ performanceMetrics: metrics }),
        
        // Testing Queue Actions
        addToTestingQueue: (test) => set((state) => ({
          testingQueue: [
            ...state.testingQueue,
            { ...test, timestamp: Date.now() },
          ],
        })),
        
        updateTestStatus: (id, status) => set((state) => ({
          testingQueue: state.testingQueue.map(t =>
            t.id === id ? { ...t, status, timestamp: Date.now() } : t
          ),
        })),
        
        removeTest: (id) => set((state) => ({
          testingQueue: state.testingQueue.filter(t => t.id !== id),
        })),
        
        // UI Actions
        setLoading: (loading) => set({ isLoading: loading }),
        setError: (error) => set({ error }),
        setSelectedBacktest: (id) => set({ selectedBacktest: id }),
        
        reset: () => set({
          backtestResults: [],
          simulationConfig: null,
          strategyValidation: {},
          performanceMetrics: null,
          testingQueue: [],
          isLoading: false,
          error: null,
          selectedBacktest: null,
        }),
      }),
      {
        name: 'simulation-store',
        partialize: (state) => ({
          // Persist critical simulation data
          simulationConfig: state.simulationConfig,
          strategyValidation: state.strategyValidation,
        }),
      }
    )
  )
);

// ============================================================================
// Selectors
// ============================================================================

export const useSimulationBacktests = () => {
  return useSimulationStore((state) => ({
    backtestResults: state.backtestResults,
    selectedBacktest: state.selectedBacktest,
    addBacktestResult: state.addBacktestResult,
    clearBacktestResults: state.clearBacktestResults,
    removeBacktestResult: state.removeBacktestResult,
    setSelectedBacktest: state.setSelectedBacktest,
  }));
};

export const useSimulationConfig = () => {
  return useSimulationStore((state) => ({
    simulationConfig: state.simulationConfig,
    setSimulationConfig: state.setSimulationConfig,
    updateSimulationConfig: state.updateSimulationConfig,
  }));
};

export const useSimulationValidation = () => {
  return useSimulationStore((state) => ({
    strategyValidation: state.strategyValidation,
    startStrategyValidation: state.startStrategyValidation,
    updateStrategyProgress: state.updateStrategyProgress,
    completeStrategyValidation: state.completeStrategyValidation,
    failStrategyValidation: state.failStrategyValidation,
  }));
};

export const useSimulationPerformance = () => {
  return useSimulationStore((state) => ({
    performanceMetrics: state.performanceMetrics,
    setPerformanceMetrics: state.setPerformanceMetrics,
  }));
};

export const useSimulationQueue = () => {
  return useSimulationStore((state) => ({
    testingQueue: state.testingQueue,
    addToTestingQueue: state.addToTestingQueue,
    updateTestStatus: state.updateTestStatus,
    removeTest: state.removeTest,
  }));
};