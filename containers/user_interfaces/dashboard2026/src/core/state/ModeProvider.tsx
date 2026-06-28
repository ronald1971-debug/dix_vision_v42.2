/**
 * Mode Provider
 * 
 * Centralized mode management for Manual/Semi-Auto/Full Auto trading modes.
 * Ensures mode consistency across all dashboards and domains.
 */

import React, { createContext, useContext, useState, useEffect } from 'react';
import { 
  fetchInitialState as fetchState,
  setTradingMode as setModeAPI,
  isStateProjectionConnected,
  type TradingMode,
  type ModeTransition
} from '@/core/state/StateProjectionBridge';

// ============================================================================
// Mode Context
// ============================================================================

interface ModeContextType {
  currentMode: TradingMode;
  modeHistory: ModeTransition[];
  isTransitioning: boolean;
  setMode: (mode: TradingMode, reason: string, authorizedBy: string) => Promise<boolean>;
  canTransitionTo: (mode: TradingMode) => boolean;
  getModeRestrictions: (mode: TradingMode) => ModeRestrictions;
  isConnected: boolean;
}

// Use ModeTransition from StateProjection for consistency
type ModeHistoryEntry = ModeTransition;

interface ModeRestrictions {
  allowedActions: string[];
  requiresApproval: boolean;
  maxPositionSize: number;
  riskMultiplier: number;
}

const ModeContext = createContext<ModeContextType | undefined>(undefined);

// ============================================================================
// Mode Provider
// ============================================================================

export function ModeProvider({ children }: { children: React.ReactNode }) {
  const [currentMode, setCurrentMode] = useState<TradingMode>('manual');
  const [modeHistory, setModeHistory] = useState<ModeHistoryEntry[]>([]);
  const [isTransitioning, setIsTransitioning] = useState(false);
  const [isConnected, setIsConnected] = useState(false);

  // Initialize mode from StateProjection
  useEffect(() => {
    const initializeMode = async () => {
      try {
        const state = await fetchState();
        if (state) {
          setCurrentMode(state.current_mode);
          setModeHistory(state.mode_transitions || []);
        }
      } catch (error) {
        console.error('[ModeProvider] Failed to initialize mode:', error);
      }
    };

    initializeMode();

    // Set up polling for connection status
    const connectionCheck = setInterval(() => {
      setIsConnected(isStateProjectionConnected());
    }, 5000);

    return () => clearInterval(connectionCheck);
  }, []);

  const setMode = async (mode: TradingMode, reason: string, authorizedBy: string): Promise<boolean> => {
    if (isTransitioning) {
      console.warn('[ModeProvider] Mode transition already in progress');
      return false;
    }

    // Validate mode transition
    if (!canTransitionTo(mode)) {
      console.warn(`[ModeProvider] Cannot transition from ${currentMode} to ${mode}`);
      return false;
    }

    setIsTransitioning(true);

    try {
      // Update local state optimistically
      const previousMode = currentMode;
      setCurrentMode(mode);

      // Update StateProjection bridge
      const success = await setModeAPI(mode, reason, authorizedBy);

      if (success) {
        // Add to history
        const historyEntry: ModeTransition = {
          timestamp: new Date().toISOString(),
          from_mode: previousMode,
          to_mode: mode,
          reason,
          authorized_by: authorizedBy,
        };
        setModeHistory(prev => [historyEntry, ...prev].slice(0, 10)); // Keep last 10
        return true;
      } else {
        // Revert on failure
        setCurrentMode(previousMode);
        return false;
      }
    } catch (error) {
      console.error('[ModeProvider] Failed to set mode:', error);
      return false;
    } finally {
      setIsTransitioning(false);
    }
  };

  const canTransitionTo = (targetMode: TradingMode): boolean => {
    // Define allowed transitions
    const allowedTransitions: Record<TradingMode, TradingMode[]> = {
      manual: ['manual', 'semi_auto'],
      semi_auto: ['manual', 'semi_auto', 'full_auto'],
      full_auto: ['semi_auto', 'manual'],
    };

    return allowedTransitions[currentMode]?.includes(targetMode) || false;
  };

  const getModeRestrictions = (mode: TradingMode): ModeRestrictions => {
    const restrictions: Record<TradingMode, ModeRestrictions> = {
      manual: {
        allowedActions: ['all'],
        requiresApproval: false,
        maxPositionSize: Number.POSITIVE_INFINITY,
        riskMultiplier: 1.0,
      },
      semi_auto: {
        allowedActions: ['operator_confirmed', 'suggestions'],
        requiresApproval: true,
        maxPositionSize: 100000,
        riskMultiplier: 1.5,
      },
      full_auto: {
        allowedActions: ['automated', 'governed'],
        requiresApproval: true,
        maxPositionSize: 50000,
        riskMultiplier: 2.0,
      },
    };

    return restrictions[mode];
  };

  const value: ModeContextType = {
    currentMode,
    modeHistory,
    isTransitioning,
    setMode,
    canTransitionTo,
    getModeRestrictions,
    isConnected,
  };

  return <ModeContext.Provider value={value}>{children}</ModeContext.Provider>;
}

// ============================================================================
// Hook
// ============================================================================

export function useMode(): ModeContextType {
  const context = useContext(ModeContext);
  if (!context) {
    throw new Error('useMode must be used within ModeProvider');
  }
  return context;
}

// ============================================================================
// Helper Functions
// ============================================================================

/**
 * Check if a specific action is allowed in the current mode
 */
export function isActionAllowed(action: string, currentMode: TradingMode): boolean {
  const restrictions = {
    manual: ['all'],
    semi_auto: ['operator_confirmed', 'suggestions', 'view'],
    full_auto: ['automated', 'governed', 'view'],
  };

  return restrictions[currentMode]?.includes(action) || false;
}

/**
 * Get mode display name
 */
export function getModeDisplayName(mode: TradingMode): string {
  const displayNames: Record<TradingMode, string> = {
    manual: 'Manual Mode',
    semi_auto: 'Semi-Automatic Mode',
    full_auto: 'Full Automatic Mode',
  };

  return displayNames[mode] || mode;
}

/**
 * Get mode description
 */
export function getModeDescription(mode: TradingMode): string {
  const descriptions: Record<TradingMode, string> = {
    manual: 'Operator has full control over all trading decisions. No automated actions.',
    semi_auto: 'System provides suggestions and requires operator confirmation before execution.',
    full_auto: 'System executes trades automatically within governance constraints and limits.',
  };

  return descriptions[mode] || '';
}