/**
 * Agent Operations Center Context
 * 
 * Provides global state management for the Agent Operations Center
 * 
 * COGNITIVE CONTROL CENTER INTEGRATION (FUTURE):
 * - Will connect to cognitive_control_center backend for real-time agent activities
 * - Will integrate with agent operations center activity feeds
 * - Will provide workspace-aware agent state management
 * 
 * NOTE: Integration planned for Dashboard2026 transformation Phase 1
 */

import { createContext, useContext, useState, useEffect, useCallback, useRef } from 'react';
import { useEnhancedWorldAwareWebSocket } from '@/hooks/useEnhancedWorldAwareWebSocket';
import { useEnhancedWorldAwareDataGenerator } from '@/lib/world/EnhancedWorldAwareDataGenerator';
import type {
  IndiraActivity,
  DyonActivity,
  Task,
  SystemEvent,
  ConnectionState,
} from '@/types/agent';

// ============================================================================
// Context Type Definition
// ============================================================================

interface AgentOpsContextType {
  // WebSocket
  websocket: ReturnType<typeof useEnhancedWorldAwareWebSocket>;
  connectionState: ConnectionState;
  isConnected: boolean;
  isWorldAware: boolean;

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
  children: any;
}

export function AgentOpsProvider({ children }: AgentOpsProviderProps) {
  // Enhanced world-aware WebSocket connection
  const websocket = useEnhancedWorldAwareWebSocket('ws://localhost:8080/api/dashboard/stream');
  const { generateAgentData, generateTaskData, generateSystemMetrics } = useEnhancedWorldAwareDataGenerator();

  // Activity data
  const [indiraActivities, setIndiraActivities] = useState<IndiraActivity[]>([]);
  const [dyonActivities, setDyonActivities] = useState<DyonActivity[]>([]);
  const [sharedTasks, setSharedTasks] = useState<Task[]>([]);
  const [globalEvents, setGlobalEvents] = useState<SystemEvent[]>([]);

  // ==========================================================================
  // WebSocket Connection Setup & World-Aware Data Initialization
  // ==========================================================================

  const initializedRef = useRef(false);

  useEffect(() => {
    // Initialize world-aware data if not connected to backend
    if (!websocket.isConnected && !initializedRef.current) {
      console.log('Initializing world-aware data for Agent Operations Center');
      initializedRef.current = true;
      
      // Use enhanced world-aware data generators
      for (let i = 0; i < 10; i++) {
        const agentData = generateAgentData() as any;
        setIndiraActivities((prev: any[]) => [{ ...agentData, id: `indira-${i}` }, ...prev]);
        setDyonActivities((prev: any[]) => [{ ...agentData, id: `dyon-${i}` }, ...prev]);
      }
      
      for (let i = 0; i < 15; i++) {
        const taskData = generateTaskData() as any;
        setSharedTasks((prev: any[]) => [{ ...taskData, id: `task-${i}` }, ...prev]);
      }
      
      for (let i = 0; i < 20; i++) {
        const metrics = generateSystemMetrics() as any;
        setGlobalEvents((prev: any[]) => [{ ...metrics, id: `event-${i}`, type: 'system-metric' }, ...prev]);
      }
    }
  }, [websocket.isConnected]);

  // ==========================================================================
  // WebSocket Message Handling
  // ==========================================================================

  useEffect(() => {
    if (!websocket.isConnected) return;

    // Simplified message handling - can be expanded later
    const handleMessages = () => {
      // Process WebSocket messages when available
      if (websocket.messages.length > 0) {
        const latestMessage = websocket.messages[websocket.messages.length - 1];
        console.log('Latest WebSocket message:', latestMessage);
      }
    };

    const interval = setInterval(handleMessages, 1000);

    return () => clearInterval(interval);
  }, [websocket.isConnected, websocket.messages]);

  // ==========================================================================
  // Activity Management Functions
  // ==========================================================================

  const addIndiraActivity = useCallback((activity: IndiraActivity) => {
    setIndiraActivities((prev: IndiraActivity[]) => {
      const filtered = prev.filter((a: IndiraActivity) => a.id !== activity.id);
      return [activity, ...filtered].slice(0, 1000);
    });
  }, []);

  const addDyonActivity = useCallback((activity: DyonActivity) => {
    setDyonActivities((prev: DyonActivity[]) => {
      const filtered = prev.filter((a: DyonActivity) => a.id !== activity.id);
      return [activity, ...filtered].slice(0, 1000);
    });
  }, []);

  const updateSharedTask = useCallback((task: Task) => {
    setSharedTasks((prev: Task[]) => {
      const index = prev.findIndex((t: Task) => t.id === task.id);
      if (index > -1) {
        const updated = [...prev];
        updated[index] = task;
        return updated;
      }
      return [task, ...prev].slice(0, 500);
    });
  }, []);

  const addGlobalEvent = useCallback((event: SystemEvent) => {
    setGlobalEvents((prev: SystemEvent[]) => {
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
  
  const connectionState: ConnectionState = websocket.isConnected ? 'connected' : 'disconnected';
  const isWorldAware = websocket.cognitiveLive;
  
  const value: AgentOpsContextType = {
    websocket,
    connectionState,
    isConnected: websocket.isConnected,
    isWorldAware,
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

export function useAgentOps() {
  const context = useContext(AgentOpsContext);
  if (!context) {
    throw new Error('useAgentOps must be used within AgentOpsProvider');
  }
  return context;
}
