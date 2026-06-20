/**
 * OPERATOR Domain Store
 * 
 * Manages OPERATOR-specific state including system controls,
 * autonomy modes, permissions, and operational states.
 */

import { create } from 'zustand';
import { devtools, persist } from 'zustand/middleware';

// ============================================================================
// OPERATOR Domain State Types
// ============================================================================

interface OperatorState {
  // System Control State
  systemStatus: {
    isActive: boolean;
    health: 'excellent' | 'good' | 'degraded' | 'critical';
    uptime: number;
    lastRestart: number;
  };
  
  // Autonomy State
  autonomyMode: {
    currentMode: 'manual' | 'assisted' | 'autonomous';
    availableModes: string[];
    permissions: string[];
    overrideActive: boolean;
  };
  
  // Kill Switch State
  killSwitch: {
    isActive: boolean;
    triggeredBy: string | null;
    triggerReason: string | null;
    triggerTime: number | null;
  };
  
  // Learning Progress
  learningProgress: {
    currentPhase: string;
    completion: number;
    milestones: {
      phase: string;
      completed: boolean;
      timestamp: number;
    }[];
  };
  
  // Authority States
  authoritySwitches: {
    [switchId: string]: {
      enabled: boolean;
      level: number;
      lastToggle: number;
    };
  };
  
  // UI State
  isLoading: boolean;
  error: string | null;
  selectedAuthority: string | null;
}

interface OperatorActions {
  // System Control Actions
  setSystemActive: (isActive: boolean) => void;
  updateSystemHealth: (health: OperatorState['systemStatus']['health']) => void;
  recordRestart: () => void;
  
  // Autonomy Actions
  setAutonomyMode: (mode: OperatorState['autonomyMode']['currentMode']) => void;
  toggleOverride: (active: boolean) => void;
  updatePermissions: (permissions: string[]) => void;
  
  // Kill Switch Actions
  triggerKillSwitch: (triggeredBy: string, reason: string) => void;
  resetKillSwitch: () => void;
  
  // Learning Actions
  setLearningPhase: (phase: string) => void;
  updateLearningCompletion: (completion: number) => void;
  completeMilestone: (phase: string) => void;
  
  // Authority Actions
  toggleAuthority: (switchId: string, enabled: boolean, level: number) => void;
  setAuthorityLevel: (switchId: string, level: number) => void;
  
  // UI Actions
  setLoading: (loading: boolean) => void;
  setError: (error: string | null) => void;
  setSelectedAuthority: (id: string | null) => void;
  reset: () => void;
}

type OperatorStore = OperatorState & OperatorActions;

// ============================================================================
// OPERATOR Store Implementation
// ============================================================================

export const useOperatorStore = create<OperatorStore>()(
  devtools(
    persist(
      (set) => ({
        // Initial State
        systemStatus: {
          isActive: true,
          health: 'excellent',
          uptime: 0,
          lastRestart: Date.now(),
        },
        autonomyMode: {
          currentMode: 'manual',
          availableModes: ['manual', 'assisted', 'autonomous'],
          permissions: [],
          overrideActive: false,
        },
        killSwitch: {
          isActive: false,
          triggeredBy: null,
          triggerReason: null,
          triggerTime: null,
        },
        learningProgress: {
          currentPhase: 'initialization',
          completion: 0,
          milestones: [],
        },
        authoritySwitches: {},
        isLoading: false,
        error: null,
        selectedAuthority: null,
        
        // System Control Actions
        setSystemActive: (isActive) => set((state) => ({
          systemStatus: { ...state.systemStatus, isActive },
        })),
        
        updateSystemHealth: (health) => set((state) => ({
          systemStatus: { ...state.systemStatus, health },
        })),
        
        recordRestart: () => set((state) => ({
          systemStatus: { ...state.systemStatus, lastRestart: Date.now() },
        })),
        
        // Autonomy Actions
        setAutonomyMode: (mode) => set((state) => ({
          autonomyMode: { ...state.autonomyMode, currentMode: mode },
        })),
        
        toggleOverride: (active) => set((state) => ({
          autonomyMode: { ...state.autonomyMode, overrideActive: active },
        })),
        
        updatePermissions: (permissions) => set((state) => ({
          autonomyMode: { ...state.autonomyMode, permissions },
        })),
        
        // Kill Switch Actions
        triggerKillSwitch: (triggeredBy, reason) => set({
          killSwitch: {
            isActive: true,
            triggeredBy,
            triggerReason: reason,
            triggerTime: Date.now(),
          },
        }),
        
        resetKillSwitch: () => set(() => ({
          killSwitch: {
            isActive: false,
            triggeredBy: null,
            triggerReason: null,
            triggerTime: null,
          },
        })),
        
        // Learning Actions
        setLearningPhase: (phase) => set((state) => ({
          learningProgress: { ...state.learningProgress, currentPhase: phase },
        })),
        
        updateLearningCompletion: (completion) => set((state) => ({
          learningProgress: { ...state.learningProgress, completion },
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
        
        // Authority Actions
        toggleAuthority: (switchId, enabled, level) => set((state) => ({
          authoritySwitches: {
            ...state.authoritySwitches,
            [switchId]: {
              enabled,
              level,
              lastToggle: Date.now(),
            },
          },
        })),
        
        setAuthorityLevel: (switchId, level) => set((state) => ({
          authoritySwitches: {
            ...state.authoritySwitches,
            [switchId]: {
              ...(state.authoritySwitches[switchId] || {}),
              level,
              lastToggle: Date.now(),
            },
          },
        })),
        
        // UI Actions
        setLoading: (loading) => set({ isLoading: loading }),
        setError: (error) => set({ error }),
        setSelectedAuthority: (id) => set({ selectedAuthority: id }),
        
        reset: () => set({
          systemStatus: {
            isActive: true,
            health: 'excellent',
            uptime: 0,
            lastRestart: Date.now(),
          },
          autonomyMode: {
            currentMode: 'manual',
            availableModes: ['manual', 'assisted', 'autonomous'],
            permissions: [],
            overrideActive: false,
          },
          killSwitch: {
            isActive: false,
            triggeredBy: null,
            triggerReason: null,
            triggerTime: null,
          },
          learningProgress: {
            currentPhase: 'initialization',
            completion: 0,
            milestones: [],
          },
          authoritySwitches: {},
          isLoading: false,
          error: null,
          selectedAuthority: null,
        }),
      }),
      {
        name: 'operator-store',
        partialize: (state) => ({
          // Persist critical operator data
          systemStatus: state.systemStatus,
          autonomyMode: state.autonomyMode,
          authoritySwitches: state.authoritySwitches,
          learningProgress: state.learningProgress,
        }),
      }
    )
  )
);

// ============================================================================
// Selectors
// ============================================================================

export const useOperatorSystemStatus = () => {
  return useOperatorStore((state) => ({
    systemStatus: state.systemStatus,
    setSystemActive: state.setSystemActive,
    updateSystemHealth: state.updateSystemHealth,
    recordRestart: state.recordRestart,
  }));
};

export const useOperatorAutonomy = () => {
  return useOperatorStore((state) => ({
    autonomyMode: state.autonomyMode,
    setAutonomyMode: state.setAutonomyMode,
    toggleOverride: state.toggleOverride,
    updatePermissions: state.updatePermissions,
  }));
};

export const useOperatorKillSwitch = () => {
  return useOperatorStore((state) => ({
    killSwitch: state.killSwitch,
    triggerKillSwitch: state.triggerKillSwitch,
    resetKillSwitch: state.resetKillSwitch,
  }));
};

export const useOperatorLearning = () => {
  return useOperatorStore((state) => ({
    learningProgress: state.learningProgress,
    setLearningPhase: state.setLearningPhase,
    updateLearningCompletion: state.updateLearningCompletion,
    completeMilestone: state.completeMilestone,
  }));
};

export const useOperatorAuthorities = () => {
  return useOperatorStore((state) => ({
    authoritySwitches: state.authoritySwitches,
    selectedAuthority: state.selectedAuthority,
    toggleAuthority: state.toggleAuthority,
    setAuthorityLevel: state.setAuthorityLevel,
    setSelectedAuthority: state.setSelectedAuthority,
  }));
};