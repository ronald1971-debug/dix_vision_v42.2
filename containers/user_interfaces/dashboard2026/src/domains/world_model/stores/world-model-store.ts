/**
 * WORLD_MODEL Domain Store
 * 
 * Manages WORLD_MODEL-specific state including world state modeling,
 * regime tracking, market context analysis, and cognitive observatory.
 */

import { create } from 'zustand';
import { devtools, persist } from 'zustand/middleware';

// ============================================================================
// WORLD_MODEL Domain State Types
// ============================================================================

interface WorldModelState {
  // World State
  currentRegime: {
    name: string;
    confidence: number;
    stability: number;
    duration: number;
    characteristics: string[];
  } | null;
  
  // Regime History
  regimeHistory: {
    regime: string;
    startTimestamp: number;
    endTimestamp: number | null;
    duration: number | null;
  }[];
  
  // Market Context
  marketContext: {
    sentiment: 'bullish' | 'bearish' | 'neutral';
    volatility: number;
    liquidity: number;
    correlation: number;
  } | null;
  
  // Cognitive Observatory
  cognitiveObservatory: {
    coherenceLevel: number;
    systemComplexity: number;
    emergenceMetrics: {
      patterns: number;
      novelty: number;
      predictability: number;
    };
    lastObservation: number;
  } | null;
  
  // World Understanding
  worldUnderstanding: {
    domainsCovered: string[];
    domainAccuracy: Record<string, number>;
    overallConfidence: number;
    learningProgress: number;
  };
  
  // Coherence Tracking
  coherenceMetrics: {
    globalCoherence: number;
    domainCoherence: Record<string, number>;
    anomalies: string[];
  };
  
  // UI State
  isLoading: boolean;
  error: string | null;
  selectedRegime: string | null;
}

interface WorldModelActions {
  // Regime Actions
  setCurrentRegime: (regime: WorldModelState['currentRegime']) => void;
  addRegimeTransition: (regime: string) => void;
  endRegime: (regime: string) => void;
  
  // Market Context Actions
  setMarketContext: (context: WorldModelState['marketContext']) => void;
  updateMarketMetrics: (metrics: Partial<WorldModelState['marketContext']>) => void;
  
  // Cognitive Observatory Actions
  setCognitiveObservatory: (observatory: WorldModelState['cognitiveObservatory']) => void;
  updateObservatoryMetrics: (metrics: Partial<WorldModelState['cognitiveObservatory']>) => void;
  
  // World Understanding Actions
  setDomainAccuracy: (domain: string, accuracy: number) => void;
  updateWorldUnderstanding: (understanding: Partial<WorldModelState['worldUnderstanding']>) => void;
  
  // Coherence Actions
  setCoherenceMetrics: (metrics: WorldModelState['coherenceMetrics']) => void;
  detectAnomalies: () => void;
  
  // UI Actions
  setLoading: (loading: boolean) => void;
  setError: (error: string | null) => void;
  setSelectedRegime: (regime: string | null) => void;
  reset: () => void;
}

type WorldModelStore = WorldModelState & WorldModelActions;

// ============================================================================
// WORLD_MODEL Store Implementation
// ============================================================================

export const useWorldModelStore = create<WorldModelStore>()(
  devtools(
    persist(
      (set) => ({
        // Initial State
        currentRegime: null,
        regimeHistory: [],
        marketContext: null,
        cognitiveObservatory: null,
        worldUnderstanding: {
          domainsCovered: [],
          domainAccuracy: {},
          overallConfidence: 0.5,
          learningProgress: 0,
        },
        coherenceMetrics: {
          globalCoherence: 0.7,
          domainCoherence: {},
          anomalies: [],
        },
        isLoading: false,
        error: null,
        selectedRegime: null,
        
        // Regime Actions
        setCurrentRegime: (regime) => set({ currentRegime: regime }),
        
        addRegimeTransition: (regime) => set((state) => {
          const now = Date.now();
          
          // End current regime if exists
          if (state.currentRegime) {
            const updatedHistory = state.regimeHistory.map(entry => {
              if (entry.endTimestamp === null) {
                return {
                  ...entry,
                  endTimestamp: now,
                  duration: now - entry.startTimestamp,
                };
              }
              return entry;
            });
            
            return {
              regimeHistory: [
                ...updatedHistory,
                {
                  regime,
                  startTimestamp: now,
                  endTimestamp: null,
                  duration: null,
                },
              ],
            };
          }
          
          // Start new regime
          return {
            regimeHistory: [
              ...state.regimeHistory,
              {
                regime,
                startTimestamp: now,
                endTimestamp: null,
                duration: null,
              },
            ],
          };
        }),
        
        endRegime: (regime) => set((state) => ({
          regimeHistory: state.regimeHistory.map(entry => {
            if (entry.regime === regime && entry.endTimestamp === null) {
              return {
                ...entry,
                endTimestamp: Date.now(),
                duration: Date.now() - entry.startTimestamp,
              };
            }
            return entry;
          }),
        })),
        
        // Market Context Actions
        setMarketContext: (context) => set({ marketContext: context }),
        updateMarketMetrics: (metrics) => set((state) => ({
          marketContext: state.marketContext ? {
            ...state.marketContext,
            ...metrics,
          } : null,
        })),
        
        // Cognitive Observatory Actions
        setCognitiveObservatory: (observatory) => set({ cognitiveObservatory: observatory }),
        updateObservatoryMetrics: (metrics) => set((state) => ({
          cognitiveObservatory: state.cognitiveObservatory ? {
            ...state.cognitiveObservatory,
            ...metrics,
          } : null,
        })),
        
        // World Understanding Actions
        setDomainAccuracy: (domain, accuracy) => set((state) => ({
          worldUnderstanding: {
            ...state.worldUnderstanding,
            domainAccuracy: {
              ...state.worldUnderstanding.domainAccuracy,
              [domain]: accuracy,
            },
          },
        })),
        
        updateWorldUnderstanding: (understanding) => set((state) => ({
          worldUnderstanding: {
            ...state.worldUnderstanding,
            ...understanding,
          },
        })),
        
        // Coherence Actions
        setCoherenceMetrics: (metrics) => set({ coherenceMetrics: metrics }),
        
        detectAnomalies: () => set((state) => {
          const anomalies: string[] = [];
          
          // Detect low coherence domains
          for (const [domain, coherence] of Object.entries(state.coherenceMetrics.domainCoherence)) {
            if (coherence < 0.5) {
              anomalies.push(`${domain}: Low coherence (${coherence.toFixed(2)})`);
            }
          }
          
          // Detect global coherence issues
          if (state.coherenceMetrics.globalCoherence < 0.6) {
            anomalies.push('Global: Low coherence detected');
          }
          
          return {
            coherenceMetrics: {
              ...state.coherenceMetrics,
              anomalies,
            },
          };
        }),
        
        // UI Actions
        setLoading: (loading) => set({ isLoading: loading }),
        setError: (error) => set({ error }),
        setSelectedRegime: (regime) => set({ selectedRegime: regime }),
        
        reset: () => set({
          currentRegime: null,
          regimeHistory: [],
          marketContext: null,
          cognitiveObservatory: null,
          worldUnderstanding: {
            domainsCovered: [],
            domainAccuracy: {},
            overallConfidence: 0.5,
            learningProgress: 0,
          },
          coherenceMetrics: {
            globalCoherence: 0.7,
            domainCoherence: {},
            anomalies: [],
          },
          isLoading: false,
          error: null,
          selectedRegime: null,
        }),
      }),
      {
        name: 'world-model-store',
        partialize: (state) => ({
          // Persist critical world model data
          currentRegime: state.currentRegime,
          regimeHistory: state.regimeHistory.slice(-50), // Keep last 50 transitions
          worldUnderstanding: state.worldUnderstanding,
          coherenceMetrics: state.coherenceMetrics,
        }),
      }
    )
  )
);

// ============================================================================
// Selectors
// ============================================================================

export const useWorldModelRegimes = () => {
  return useWorldModelStore((state) => ({
    currentRegime: state.currentRegime,
    regimeHistory: state.regimeHistory,
    selectedRegime: state.selectedRegime,
    setCurrentRegime: state.setCurrentRegime,
    addRegimeTransition: state.addRegimeTransition,
    endRegime: state.endRegime,
    setSelectedRegime: state.setSelectedRegime,
  }));
};

export const useWorldModelMarketContext = () => {
  return useWorldModelStore((state) => ({
    marketContext: state.marketContext,
    setMarketContext: state.setMarketContext,
    updateMarketMetrics: state.updateMarketMetrics,
  }));
};

export const useWorldModelObservatory = () => {
  return useWorldModelStore((state) => ({
    cognitiveObservatory: state.cognitiveObservatory,
    setCognitiveObservatory: state.setCognitiveObservatory,
    updateObservatoryMetrics: state.updateObservatoryMetrics,
  }));
};

export const useWorldModelUnderstanding = () => {
  return useWorldModelStore((state) => ({
    worldUnderstanding: state.worldUnderstanding,
    setDomainAccuracy: state.setDomainAccuracy,
    updateWorldUnderstanding: state.updateWorldUnderstanding,
  }));
};

export const useWorldModelCoherence = () => {
  return useWorldModelStore((state) => ({
    coherenceMetrics: state.coherenceMetrics,
    setCoherenceMetrics: state.setCoherenceMetrics,
    detectAnomalies: state.detectAnomalies,
  }));
};