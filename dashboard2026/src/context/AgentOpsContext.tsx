/**
 * Agent Operations Center Context
 * 
 * Provides global state management for the Agent Operations Center
 */

import { createContext, useContext, useState, useEffect, useMemo, useCallback, ReactNode } from 'react';
import { useWebSocketWithMock } from '@/hooks/useWebSocketWithMock';
import { generateIndiraActivities, generateDyonActivities, generateTasks, generateSystemEvents } from '@/lib/mock/mockAgentData';
import { DEV_CONFIG } from '@/config/dev';
import type {
  IndiraActivity,
  DyonActivity,
  Task,
  SystemEvent,
  ConnectionState,
  WebSocketMessage,
} from '@/types/agent';

// ============================================================================
// Context Type Definition
// ============================================================================

interface AgentOpsContextType {
  // WebSocket
  websocket: ReturnType<typeof useWebSocketWithMock>['manager'];
  connectionState: ConnectionState;
  isConnected: boolean;
  isMockMode: boolean;

  // Data
  indiraActivities: IndiraActivity[];
  dyonActivities: DyonActivity[];
  sharedTasks: Task[];
  globalEvents: SystemEvent[];

  // Actions
  addIndiraActivity: (activity: IndiraActivity) => void;
  addDyonActivity: (activity: DyonActivity) => void;
  updateSharedTask: (task: Task) => void;
  addGlobalEvent: (event: SystemEvent) => void;
  
  // Utility
  clearIndiraActivities: () => void;
  clearDyonActivities: () => void;
  clearGlobalEvents: () => void;
}

const AgentOpsContext = createContext<AgentOpsContextType | null>(null);

// ============================================================================
// Provider Component
// ============================================================================

interface AgentOpsProviderProps {
  children: ReactNode;
}

export function AgentOpsProvider({ children }: AgentOpsProviderProps) {
  // WebSocket connection
  const { manager, connectionState, isConnected, isMockMode } = useWebSocketWithMock();

  // Activity data
  const [indiraActivities, setIndiraActivities] = useState<IndiraActivity[]>([]);
  const [dyonActivities, setDyonActivities] = useState<DyonActivity[]>([]);
  const [sharedTasks, setSharedTasks] = useState<Task[]>([]);
  const [globalEvents, setGlobalEvents] = useState<SystemEvent[]>([]);

  // ==========================================================================
  // WebSocket Connection Setup & Mock Data Initialization
  // ==========================================================================

  useEffect(() => {
    // Initialize mock data if in mock mode
    if (isMockMode) {
      console.log('Initializing mock data for Agent Operations Center');
      setIndiraActivities(generateIndiraActivities(10));
      setDyonActivities(generateDyonActivities(10));
      setSharedTasks(generateTasks(15));
      setGlobalEvents(generateSystemEvents(20));
    }

    // Subscribe to WebSocket events
    const unsubscribeIndiraActivity = manager.subscribe('indira:activity', (message: WebSocketMessage) => {
      setIndiraActivities(prev => {
        const activity = message.data as IndiraActivity;
        const filtered = prev.filter(a => a.id !== activity.id);
        return [activity, ...filtered].slice(0, DEV_CONFIG.MAX_ACTIVITIES);
      });
    });

    const unsubscribeDyonActivity = manager.subscribe('dyon:activity', (message: WebSocketMessage) => {
      setDyonActivities(prev => {
        const activity = message.data as DyonActivity;
        const filtered = prev.filter(a => a.id !== activity.id);
        return [activity, ...filtered].slice(0, DEV_CONFIG.MAX_ACTIVITIES);
      });
    });

    const unsubscribeTaskUpdate = manager.subscribe('task:update', (message: WebSocketMessage) => {
      setSharedTasks(prev => {
        const task = message.data as Task;
        const index = prev.findIndex(t => t.id === task.id);
        if (index > -1) {
          const updated = [...prev];
          updated[index] = task;
          return updated;
        }
        return [task, ...prev].slice(0, 500);
      });
    });

    const unsubscribeSystemEvent = manager.subscribe('system:event', (message: WebSocketMessage) => {
      setGlobalEvents(prev => {
        const event = message.data as SystemEvent;
        return [event, ...prev].slice(0, DEV_CONFIG.MAX_EVENTS);
      });
    });

    // Cleanup on unmount
    return () => {
      unsubscribeIndiraActivity();
      unsubscribeDyonActivity();
      unsubscribeTaskUpdate();
      unsubscribeSystemEvent();
    };
  }, [manager, isMockMode]);

  // ==========================================================================
  // Activity Management Functions
  // ==========================================================================

  const addIndiraActivity = useCallback((activity: IndiraActivity) => {
    setIndiraActivities(prev => {
      const filtered = prev.filter(a => a.id !== activity.id);
      return [activity, ...filtered].slice(0, 1000);
    });
  }, []);

  const addDyonActivity = useCallback((activity: DyonActivity) => {
    setDyonActivities(prev => {
      const filtered = prev.filter(a => a.id !== activity.id);
      return [activity, ...filtered].slice(0, 1000);
    });
  }, []);

  const updateSharedTask = useCallback((task: Task) => {
    setSharedTasks(prev => {
      const index = prev.findIndex(t => t.id === task.id);
      if (index > -1) {
        const updated = [...prev];
        updated[index] = task;
        return updated;
      }
      return [task, ...prev].slice(0, 500);
    });
  }, []);

  const addGlobalEvent = useCallback((event: SystemEvent) => {
    setGlobalEvents(prev => {
      return [event, ...prev].slice(0, 1000);
    });
  }, []);

  const clearIndiraActivities = useCallback(() => {
    setIndiraActivities([]);
  }, []);

  const clearDyonActivities = useCallback(() => {
    setDyonActivities([]);
  }, []);

  const clearGlobalEvents = useCallback(() => {
    setGlobalEvents([]);
  }, []);

  // ==========================================================================
  // Context Value
  // ==========================================================================

  const value: AgentOpsContextType = {
    websocket: manager,
    connectionState,
    isConnected,
    indiraActivities,
    dyonActivities,
    sharedTasks,
    globalEvents,
    addIndiraActivity,
    addDyonActivity,
    updateSharedTask,
    addGlobalEvent,
    clearIndiraActivities,
    clearDyonActivities,
    clearGlobalEvents,
    isMockMode,
  };

  return (
    <AgentOpsContext.Provider value={value}>
      {children}
    </AgentOpsContext.Provider>
  );
}

// ============================================================================
// Custom Hook
// ============================================================================

/**
 * Hook to use Agent Operations Center context
 */
export function useAgentOps(): AgentOpsContextType {
  const context = useContext(AgentOpsContext);
  if (!context) {
    throw new Error('useAgentOps must be used within AgentOpsProvider');
  }
  return context;
}

// ============================================================================
// Data Hooks
// ============================================================================

/**
 * Hook for INDIRA activities
 */
export function useIndiraActivities() {
  const { indiraActivities } = useAgentOps();
  return indiraActivities;
}

/**
 * Hook for DYON activities
 */
export function useDyonActivities() {
  const { dyonActivities } = useAgentOps();
  return dyonActivities;
}

/**
 * Hook for shared tasks
 */
export function useSharedTasks() {
  const { sharedTasks } = useAgentOps();
  return sharedTasks;
}

/**
 * Hook for global events
 */
export function useGlobalEvents() {
  const { globalEvents } = useAgentOps();
  return globalEvents;
}

/**
 * Hook for connection state
 */
export function useConnectionState() {
  const { connectionState, isConnected, isMockMode } = useAgentOps();
  return { connectionState, isConnected, isMockMode };
}
