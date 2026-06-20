/**
 * INDIRA Domain Store
 * 
 * Manages INDIRA-specific state including market intelligence,
 * trader profiles, cognitive metrics, and learning data.
 */

import { create } from 'zustand';
import { devtools, persist } from 'zustand/middleware';

// ============================================================================
// INDIRA Domain State Types
// ============================================================================

interface IndiraState {
  // Market Intelligence
  currentRegime: string | null;
  marketTrend: string;
  marketVolatility: number;
  marketMomentum: number;
  
  // Trader Intelligence
  traderProfile: {
    id: string;
    psychologicalFactors: {
      fear: number;
      greed: number;
      confidence: number;
      patience: number;
      discipline: number;
    };
    decisionTime: number;
    accuracy: number;
  } | null;
  
  // Portfolio Intelligence
  portfolioMetrics: {
    currentWeight: number;
    targetWeight: number;
    unrealizedPnL: number;
    riskContribution: number;
    returnContribution: number;
  } | null;
  
  // Cognitive Metrics
  cognitiveLoad: number;
  consciousnessLevel: {
    awareness: string;
    focus: number;
    confidence: number;
    learningRate: number;
  } | null;
  
  // Learning Metrics
  learningMetrics: {
    patternsLearned: number;
    accuracy: number;
    learningRate: number;
  } | null;
  
  // UI State
  isInitialized: boolean;
  isLoading: boolean;
  error: string | null;
}

interface IndiraActions {
  // Market Intelligence Actions
  setCurrentRegime: (regime: string) => void;
  setMarketData: (data: Partial<{trend: string; volatility: number; momentum: number}>) => void;
  
  // Trader Intelligence Actions
  setTraderProfile: (profile: IndiraState['traderProfile']) => void;
  updatePsychologicalFactors: (factors: Partial<{fear: number; greed: number; confidence: number; patience: number; discipline: number}>) => void;
  
  // Portfolio Intelligence Actions
  setPortfolioMetrics: (metrics: IndiraState['portfolioMetrics']) => void;
  updatePortfolioMetrics: (metrics: Partial<IndiraState['portfolioMetrics']>) => void;
  
  // Cognitive Metrics Actions
  setCognitiveLoad: (load: number) => void;
  setConsciousnessLevel: (level: IndiraState['consciousnessLevel']) => void;
  
  // Learning Metrics Actions
  setLearningMetrics: (metrics: IndiraState['learningMetrics']) => void;
  updateLearningMetrics: (metrics: Partial<IndiraState['learningMetrics']>) => void;
  
  // UI Actions
  setInitialized: (initialized: boolean) => void;
  setLoading: (loading: boolean) => void;
  setError: (error: string | null) => void;
  reset: () => void;
}

type IndiraStore = IndiraState & IndiraActions;

// ============================================================================
// INDIRA Store Implementation
// ============================================================================

export const useIndiraStore = create<IndiraStore>()(
  devtools(
    persist(
      (set) => ({
        // Initial State
        currentRegime: null,
        marketTrend: 'neutral',
        marketVolatility: 0.25,
        marketMomentum: 0.5,
        
        traderProfile: null,
        
        portfolioMetrics: null,
        
        cognitiveLoad: 0.5,
        consciousnessLevel: null,
        
        learningMetrics: null,
        
        isInitialized: false,
        isLoading: false,
        error: null,
        
        // Market Intelligence Actions
        setCurrentRegime: (regime) => set({ currentRegime: regime }),
        setMarketData: (data) => set((state) => ({
          marketTrend: data.trend ?? state.marketTrend,
          marketVolatility: data.volatility ?? state.marketVolatility,
          marketMomentum: data.momentum ?? state.marketMomentum,
        })),
        
        // Trader Intelligence Actions
        setTraderProfile: (profile) => set({ traderProfile: profile }),
        updatePsychologicalFactors: (factors) => set((state) => ({
          traderProfile: state.traderProfile ? {
            ...state.traderProfile,
            psychologicalFactors: {
              ...state.traderProfile.psychologicalFactors,
              ...factors
            }
          } : null
        })),
        
        // Portfolio Intelligence Actions
        setPortfolioMetrics: (metrics) => set({ portfolioMetrics: metrics }),
        updatePortfolioMetrics: (metrics) => set((state) => ({
          portfolioMetrics: state.portfolioMetrics ? {
            ...state.portfolioMetrics,
            ...metrics
          } : null
        })),
        
        // Cognitive Metrics Actions
        setCognitiveLoad: (load) => set({ cognitiveLoad: load }),
        setConsciousnessLevel: (level) => set({ consciousnessLevel: level }),
        
        // Learning Metrics Actions
        setLearningMetrics: (metrics) => set({ learningMetrics: metrics }),
        updateLearningMetrics: (metrics) => set((state) => ({
          learningMetrics: state.learningMetrics ? {
            ...state.learningMetrics,
            ...metrics
          } : null
        })),
        
        // UI Actions
        setInitialized: (initialized) => set({ isInitialized: initialized }),
        setLoading: (loading) => set({ isLoading: loading }),
        setError: (error) => set({ error }),
        reset: () => set({
          currentRegime: null,
          marketTrend: 'neutral',
          marketVolatility: 0.25,
          marketMomentum: 0.5,
          traderProfile: null,
          portfolioMetrics: null,
          cognitiveLoad: 0.5,
          consciousnessLevel: null,
          learningMetrics: null,
          isInitialized: false,
          isLoading: false,
          error: null,
        }),
      }),
      {
        name: 'indira-store',
        partialize: (state) => ({
          // Only persist critical state, not transient UI state
          traderProfile: state.traderProfile,
          portfolioMetrics: state.portfolioMetrics,
          learningMetrics: state.learningMetrics,
        }),
      }
    )
  )
);

// ============================================================================
// Selectors
// ============================================================================

export const useIndiraMarketIntelligence = () => {
  return useIndiraStore((state) => ({
    currentRegime: state.currentRegime,
    marketTrend: state.marketTrend,
    marketVolatility: state.marketVolatility,
    marketMomentum: state.marketMomentum,
    setCurrentRegime: state.setCurrentRegime,
    setMarketData: state.setMarketData,
  }));
};

export const useIndiraTraderIntelligence = () => {
  return useIndiraStore((state) => ({
    traderProfile: state.traderProfile,
    setTraderProfile: state.setTraderProfile,
    updatePsychologicalFactors: state.updatePsychologicalFactors,
  }));
};

export const useIndiraPortfolioIntelligence = () => {
  return useIndiraStore((state) => ({
    portfolioMetrics: state.portfolioMetrics,
    setPortfolioMetrics: state.setPortfolioMetrics,
    updatePortfolioMetrics: state.updatePortfolioMetrics,
  }));
};

export const useIndiraCognitiveState = () => {
  return useIndiraStore((state) => ({
    cognitiveLoad: state.cognitiveLoad,
    consciousnessLevel: state.consciousnessLevel,
    setCognitiveLoad: state.setCognitiveLoad,
    setConsciousnessLevel: state.setConsciousnessLevel,
  }));
};

export const useIndiraLearningState = () => {
  return useIndiraStore((state) => ({
    learningMetrics: state.learningMetrics,
    setLearningMetrics: state.setLearningMetrics,
    updateLearningMetrics: state.updateLearningMetrics,
  }));
};