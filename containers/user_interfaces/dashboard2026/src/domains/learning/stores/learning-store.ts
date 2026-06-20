/**
 * LEARNING Domain Store
 * 
 * Manages LEARNING-specific state including learning systems, memory management,
 * adaptive intelligence, and knowledge accumulation.
 */

import { create } from 'zustand';
import { devtools, persist } from 'zustand/middleware';

// ============================================================================
// LEARNING Domain State Types
// ============================================================================

interface LearningState {
  // AI/ML State
  aiModelState: {
    modelType: string;
    accuracy: number;
    confidence: number;
    lastTraining: number;
    trainingData: any;
  } | null;
  
  // Research State
  researchState: {
    activeProjects: string[];
    completedProjects: string[];
    researchProgress: {
      [projectId: string]: {
        status: string;
        progress: number;
        findings: any;
      };
    };
  };
  
  // Knowledge Base
  knowledgeBase: {
    patterns: Array<{
      id: string;
      pattern: any;
      confidence: number;
      occurrences: number;
      lastUsed: number;
    }>;
    narratives: Array<{
      id: string;
      narrative: string;
      confidence: number;
      timestamp: number;
    }>;
  };
  
  // Learning Metrics
  learningMetrics: {
    totalPatternsLearned: number;
    accuracy: number;
    learningRate: number;
    adaptationSpeed: number;
  };
  
  // Memory Management
  memoryState: {
    shortTerm: any[];
    longTerm: any[];
    memoryCapacity: number;
    retentionRate: number;
  };
  
  // Learning Progress
  learningProgress: {
    currentPhase: string;
    milestones: Array<{
      phase: string;
      completed: boolean;
      timestamp: number;
    }>;
    overallProgress: number;
  };
  
  // UI State
  isLoading: boolean;
  error: string | null;
  selectedModel: string | null;
}

interface LearningActions {
  // AI/ML Actions
  setAiModelState: (state: LearningState['aiModelState']) => void;
  updateModelMetrics: (metrics: Partial<LearningState['aiModelState']>) => void;
  
  // Research Actions
  addResearchProject: (projectId: string) => void;
  completeResearchProject: (projectId: string, findings: any) => void;
  updateResearchProgress: (projectId: string, progress: number) => void;
  
  // Knowledge Base Actions
  addPattern: (pattern: Omit<LearningState['knowledgeBase']['patterns'][0], 'lastUsed'>) => void;
  addNarrative: (narrative: Omit<LearningState['knowledgeBase']['narratives'][0], 'timestamp'>) => void;
  updatePatternConfidence: (patternId: string, confidence: number) => void;
  
  // Learning Metrics Actions
  setLearningMetrics: (metrics: Partial<LearningState['learningMetrics']>) => void;
  
  // Memory Actions
  addToMemory: (memory: any, type: 'short' | 'long') => void;
  clearMemory: (type: 'short' | 'long') => void;
  updateMemoryCapacity: (capacity: number) => void;
  
  // Progress Actions
  setLearningPhase: (phase: string) => void;
  completeMilestone: (phase: string) => void;
  updateOverallProgress: (progress: number) => void;
  
  // UI Actions
  setLoading: (loading: boolean) => void;
  setError: (error: string | null) => void;
  setSelectedModel: (model: string | null) => void;
  reset: () => void;
}

type LearningStore = LearningState & LearningActions;

// ============================================================================
// LEARNING Store Implementation
// ============================================================================

export const useLearningStore = create<LearningStore>()(
  devtools(
    persist(
      (set) => ({
        // Initial State
        aiModelState: null,
        researchState: {
          activeProjects: [],
          completedProjects: [],
          researchProgress: {},
        },
        knowledgeBase: {
          patterns: [],
          narratives: [],
        },
        learningMetrics: {
          totalPatternsLearned: 0,
          accuracy: 0.5,
          learningRate: 0.5,
          adaptationSpeed: 0.5,
        },
        memoryState: {
          shortTerm: [],
          longTerm: [],
          memoryCapacity: 1000,
          retentionRate: 0.8,
        },
        learningProgress: {
          currentPhase: 'initialization',
          milestones: [],
          overallProgress: 0,
        },
        isLoading: false,
        error: null,
        selectedModel: null,
        
        // AI/ML Actions
        setAiModelState: (state) => set({ aiModelState: state }),
        updateModelMetrics: (metrics) => set((state) => ({
          aiModelState: state.aiModelState ? {
            ...state.aiModelState,
            ...metrics,
          } : null,
        })),
        
        // Research Actions
        addResearchProject: (projectId) => set((state) => ({
          researchState: {
            ...state.researchState,
            activeProjects: [...state.researchState.activeProjects, projectId],
            researchProgress: {
              ...state.researchState.researchProgress,
              [projectId]: {
                status: 'active',
                progress: 0,
                findings: null,
              },
            },
          },
        })),
        
        completeResearchProject: (projectId, findings) => set((state) => ({
          researchState: {
            activeProjects: state.researchState.activeProjects.filter(p => p !== projectId),
            completedProjects: [...state.researchState.completedProjects, projectId],
            researchProgress: {
              ...state.researchState.researchProgress,
              [projectId]: {
                ...state.researchState.researchProgress[projectId],
                status: 'completed',
                progress: 100,
                findings,
              },
            },
          },
        })),
        
        updateResearchProgress: (projectId, progress) => set((state) => ({
          researchState: {
            ...state.researchState,
            researchProgress: {
              ...state.researchState.researchProgress,
              [projectId]: state.researchState.researchProgress[projectId] ? {
                ...state.researchState.researchProgress[projectId],
                progress,
              } : {
                status: 'active',
                progress,
                findings: null,
              },
            },
          },
        })),
        
        // Knowledge Base Actions
        addPattern: (pattern) => set((state) => ({
          knowledgeBase: {
            ...state.knowledgeBase,
            patterns: [
              ...state.knowledgeBase.patterns,
              { ...pattern, lastUsed: Date.now() },
            ],
          },
        })),
        
        addNarrative: (narrative) => set((state) => ({
          knowledgeBase: {
            ...state.knowledgeBase,
            narratives: [
              ...state.knowledgeBase.narratives,
              { ...narrative, timestamp: Date.now() },
            ],
          },
        })),
        
        updatePatternConfidence: (patternId, confidence) => set((state) => ({
          knowledgeBase: {
            ...state.knowledgeBase,
            patterns: state.knowledgeBase.patterns.map(p =>
              p.id === patternId ? { ...p, confidence } : p
            ),
          },
        })),
        
        // Learning Metrics Actions
        setLearningMetrics: (metrics) => set((state) => ({
          learningMetrics: { ...state.learningMetrics, ...metrics },
        })),
        
        // Memory Actions
        addToMemory: (memory, type) => set((state) => {
          if (type === 'short') {
            return {
              memoryState: {
                ...state.memoryState,
                shortTerm: [...state.memoryState.shortTerm, memory].slice(-100),
              },
            };
          } else {
            return {
              memoryState: {
                ...state.memoryState,
                longTerm: [...state.memoryState.longTerm, memory].slice(-500),
              },
            };
          }
        }),
        
        clearMemory: (type) => set((state) => {
          if (type === 'short') {
            return { memoryState: { ...state.memoryState, shortTerm: [] } };
          } else {
            return { memoryState: { ...state.memoryState, longTerm: [] } };
          }
        }),
        
        updateMemoryCapacity: (capacity) => set((state) => ({
          memoryState: { ...state.memoryState, memoryCapacity: capacity },
        })),
        
        // Progress Actions
        setLearningPhase: (phase) => set((state) => ({
          learningProgress: { ...state.learningProgress, currentPhase: phase },
        })),
        
        completeMilestone: (phase) => set((state) => ({
          learningProgress: {
            ...state.learningProgress,
            milestones: [
              ...state.learningProgress.milestones,
              { phase, completed: true, timestamp: Date.now() },
            ],
          },
        })),
        
        updateOverallProgress: (progress) => set((state) => ({
          learningProgress: { ...state.learningProgress, overallProgress: progress },
        })),
        
        // UI Actions
        setLoading: (loading) => set({ isLoading: loading }),
        setError: (error) => set({ error }),
        setSelectedModel: (model) => set({ selectedModel: model }),
        
        reset: () => set({
          aiModelState: null,
          researchState: {
            activeProjects: [],
            completedProjects: [],
            researchProgress: {},
          },
          knowledgeBase: {
            patterns: [],
            narratives: [],
          },
          learningMetrics: {
            totalPatternsLearned: 0,
            accuracy: 0.5,
            learningRate: 0.5,
            adaptationSpeed: 0.5,
          },
          memoryState: {
            shortTerm: [],
            longTerm: [],
            memoryCapacity: 1000,
            retentionRate: 0.8,
          },
          learningProgress: {
            currentPhase: 'initialization',
            milestones: [],
            overallProgress: 0,
          },
          isLoading: false,
          error: null,
          selectedModel: null,
        }),
      }),
      {
        name: 'learning-store',
        partialize: (state) => ({
          // Persist critical learning data
          knowledgeBase: state.knowledgeBase,
          learningMetrics: state.learningMetrics,
          learningProgress: state.learningProgress,
        }),
      }
    )
  )
);

// ============================================================================
// Selectors
// ============================================================================

export const useLearningAI = () => {
  return useLearningStore((state) => ({
    aiModelState: state.aiModelState,
    selectedModel: state.selectedModel,
    setAiModelState: state.setAiModelState,
    updateModelMetrics: state.updateModelMetrics,
    setSelectedModel: state.setSelectedModel,
  }));
};

export const useLearningResearch = () => {
  return useLearningStore((state) => ({
    researchState: state.researchState,
    addResearchProject: state.addResearchProject,
    completeResearchProject: state.completeResearchProject,
    updateResearchProgress: state.updateResearchProgress,
  }));
};

export const useLearningKnowledge = () => {
  return useLearningStore((state) => ({
    knowledgeBase: state.knowledgeBase,
    addPattern: state.addPattern,
    addNarrative: state.addNarrative,
    updatePatternConfidence: state.updatePatternConfidence,
  }));
};

export const useLearningMetrics = () => {
  return useLearningStore((state) => ({
    learningMetrics: state.learningMetrics,
    setLearningMetrics: state.setLearningMetrics,
  }));
};

export const useLearningMemory = () => {
  return useLearningStore((state) => ({
    memoryState: state.memoryState,
    addToMemory: state.addToMemory,
    clearMemory: state.clearMemory,
    updateMemoryCapacity: state.updateMemoryCapacity,
  }));
};

export const useLearningProgress = () => {
  return useLearningStore((state) => ({
    learningProgress: state.learningProgress,
    setLearningPhase: state.setLearningPhase,
    completeMilestone: state.completeMilestone,
    updateOverallProgress: state.updateOverallProgress,
  }));
};