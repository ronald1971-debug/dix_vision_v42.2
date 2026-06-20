/**
 * DYON Domain Store
 * 
 * Manages DYON-specific state including system architecture analysis,
 * code intelligence, drift monitoring, and engineering workspace state.
 */

import { create } from 'zustand';
import { devtools, persist } from 'zustand/middleware';

// ============================================================================
// DYON Domain State Types
// ============================================================================

interface DyonState {
  // Architecture Analysis
  architectureState: {
    totalModules: number;
    activeModules: number;
    complexityScore: number;
    architectureHealth: string;
    lastAnalysis: number;
  } | null;
  
  // Code Intelligence
  codeMetrics: {
    totalLines: number;
    codeQuality: number;
    technicalDebt: number;
    testCoverage: number;
    documentationCoverage: number;
  } | null;
  
  // Drift Monitoring
  driftMetrics: {
    driftDetected: boolean;
    driftSeverity: 'low' | 'medium' | 'high';
    affectedModules: string[];
    lastDriftCheck: number;
  } | null;
  
  // Engineering Workspace
  workspaceState: {
    currentView: string;
    activePanel: string;
    openPanels: string[];
    recentChanges: {
      file: string;
      change: string;
      timestamp: number;
    }[];
  };
  
  // Mutation Queue
  mutationQueue: {
    id: string;
    type: string;
    status: 'pending' | 'processing' | 'completed' | 'failed';
    priority: number;
    timestamp: number;
  }[];
  
  // Learning Progress
  learningProgress: {
    currentStage: string;
    completedTasks: number;
    totalTasks: number;
    learningRate: number;
  };
  
  // UI State
  isLoading: boolean;
  error: string | null;
}

interface DyonActions {
  // Architecture Actions
  setArchitectureState: (state: DyonState['architectureState']) => void;
  updateArchitectureMetrics: (metrics: Partial<DyonState['architectureState']>) => void;
  
  // Code Metrics Actions
  setCodeMetrics: (metrics: DyonState['codeMetrics']) => void;
  updateCodeMetrics: (metrics: Partial<DyonState['codeMetrics']>) => void;
  
  // Drift Actions
  setDriftMetrics: (metrics: DyonState['driftMetrics']) => void;
  clearDriftDetection: () => void;
  
  // Workspace Actions
  setWorkspaceView: (view: string) => void;
  setActivePanel: (panel: string) => void;
  addRecentChange: (change: DyonState['workspaceState']['recentChanges'][0]) => void;
  
  // Mutation Queue Actions
  addMutation: (mutation: Omit<DyonState['mutationQueue'][0], 'timestamp'>) => void;
  updateMutationStatus: (id: string, status: DyonState['mutationQueue'][0]['status']) => void;
  removeMutation: (id: string) => void;
  
  // Learning Actions
  setLearningStage: (stage: string) => void;
  updateLearningProgress: (progress: Partial<DyonState['learningProgress']>) => void;
  
  // UI Actions
  setLoading: (loading: boolean) => void;
  setError: (error: string | null) => void;
  reset: () => void;
}

type DyonStore = DyonState & DyonActions;

// ============================================================================
// DYON Store Implementation
// ============================================================================

export const useDyonStore = create<DyonStore>()(
  devtools(
    persist(
      (set) => ({
        // Initial State
        architectureState: null,
        codeMetrics: null,
        driftMetrics: null,
        workspaceState: {
          currentView: 'overview',
          activePanel: 'architecture',
          openPanels: ['architecture', 'drift'],
          recentChanges: [],
        },
        mutationQueue: [],
        learningProgress: {
          currentStage: 'initialization',
          completedTasks: 0,
          totalTasks: 100,
          learningRate: 0.5,
        },
        isLoading: false,
        error: null,
        
        // Architecture Actions
        setArchitectureState: (state) => set({ architectureState: state }),
        updateArchitectureMetrics: (metrics) => set((state) => ({
          architectureState: state.architectureState ? {
            ...state.architectureState,
            ...metrics,
          } : null,
        })),
        
        // Code Metrics Actions
        setCodeMetrics: (metrics) => set({ codeMetrics: metrics }),
        updateCodeMetrics: (metrics) => set((state) => ({
          codeMetrics: state.codeMetrics ? {
            ...state.codeMetrics,
            ...metrics,
          } : null,
        })),
        
        // Drift Actions
        setDriftMetrics: (metrics) => set({ driftMetrics: metrics }),
        clearDriftDetection: () => set({
          driftMetrics: {
            driftDetected: false,
            driftSeverity: 'low',
            affectedModules: [],
            lastDriftCheck: Date.now(),
          },
        }),
        
        // Workspace Actions
        setWorkspaceView: (view) => set((state) => ({
          workspaceState: { ...state.workspaceState, currentView: view },
        })),
        
        setActivePanel: (panel) => set((state) => ({
          workspaceState: { ...state.workspaceState, activePanel: panel },
        })),
        
        addRecentChange: (change) => set((state) => ({
          workspaceState: {
            ...state.workspaceState,
            recentChanges: [
              { ...change, timestamp: Date.now() },
              ...state.workspaceState.recentChanges.slice(0, 9),
            ],
          },
        })),
        
        // Mutation Queue Actions
        addMutation: (mutation) => set((state) => ({
          mutationQueue: [
            ...state.mutationQueue,
            { ...mutation, timestamp: Date.now() },
          ],
        })),
        
        updateMutationStatus: (id, status) => set((state) => ({
          mutationQueue: state.mutationQueue.map(m =>
            m.id === id ? { ...m, status, timestamp: Date.now() } : m
          ),
        })),
        
        removeMutation: (id) => set((state) => ({
          mutationQueue: state.mutationQueue.filter(m => m.id !== id),
        })),
        
        // Learning Actions
        setLearningStage: (stage) => set((state) => ({
          learningProgress: { ...state.learningProgress, currentStage: stage },
        })),
        
        updateLearningProgress: (progress) => set((state) => ({
          learningProgress: { ...state.learningProgress, ...progress },
        })),
        
        // UI Actions
        setLoading: (loading) => set({ isLoading: loading }),
        setError: (error) => set({ error }),
        
        reset: () => set({
          architectureState: null,
          codeMetrics: null,
          driftMetrics: null,
          workspaceState: {
            currentView: 'overview',
            activePanel: 'architecture',
            openPanels: ['architecture', 'drift'],
            recentChanges: [],
          },
          mutationQueue: [],
          learningProgress: {
            currentStage: 'initialization',
            completedTasks: 0,
            totalTasks: 100,
            learningRate: 0.5,
          },
          isLoading: false,
          error: null,
        }),
      }),
      {
        name: 'dyon-store',
        partialize: (state) => ({
          // Persist critical DYON data
          workspaceState: state.workspaceState,
          learningProgress: state.learningProgress,
        }),
      }
    )
  )
);

// ============================================================================
// Selectors
// ============================================================================

export const useDyonArchitecture = () => {
  return useDyonStore((state) => ({
    architectureState: state.architectureState,
    setArchitectureState: state.setArchitectureState,
    updateArchitectureMetrics: state.updateArchitectureMetrics,
  }));
};

export const useDyonCodeMetrics = () => {
  return useDyonStore((state) => ({
    codeMetrics: state.codeMetrics,
    setCodeMetrics: state.setCodeMetrics,
    updateCodeMetrics: state.updateCodeMetrics,
  }));
};

export const useDyonDrift = () => {
  return useDyonStore((state) => ({
    driftMetrics: state.driftMetrics,
    setDriftMetrics: state.setDriftMetrics,
    clearDriftDetection: state.clearDriftDetection,
  }));
};

export const useDyonWorkspace = () => {
  return useDyonStore((state) => ({
    workspaceState: state.workspaceState,
    setWorkspaceView: state.setWorkspaceView,
    setActivePanel: state.setActivePanel,
    addRecentChange: state.addRecentChange,
  }));
};

export const useDyonMutations = () => {
  return useDyonStore((state) => ({
    mutationQueue: state.mutationQueue,
    addMutation: state.addMutation,
    updateMutationStatus: state.updateMutationStatus,
    removeMutation: state.removeMutation,
  }));
};

export const useDyonLearning = () => {
  return useDyonStore((state) => ({
    learningProgress: state.learningProgress,
    setLearningStage: state.setLearningStage,
    updateLearningProgress: state.updateLearningProgress,
  }));
};