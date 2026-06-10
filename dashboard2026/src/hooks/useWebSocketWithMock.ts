/**
 * WebSocket Hook with Mock/Real Toggle
 * 
 * Automatically switches between real and mock WebSocket manager
 * based on development configuration
 */

import { useEffect, useMemo } from 'react';
import { getWebSocketManager } from '@/lib/websocket/AgentWebSocketManager';
import { getMockWebSocketManager, resetMockWebSocketManager } from '@/lib/mock/mockAgentData';
import { DEV_CONFIG } from '@/config/dev';
import type { ConnectionState } from '@/types/agent';

export function useWebSocketWithMock() {
  const shouldUseMock = DEV_CONFIG.USE_MOCK_WEBSOCKET;
  
  const manager = useMemo(() => {
    return shouldUseMock ? getMockWebSocketManager() : getWebSocketManager();
  }, [shouldUseMock]);
  
  const [connectionState, setConnectionState] = useState<ConnectionState>('disconnected');
  const [isConnected, setIsConnected] = useState(false);

  useEffect(() => {
    // Subscribe to connection state changes
    const unsubscribeConnected = manager.subscribe('connection:connected', () => {
      setConnectionState('connected');
      setIsConnected(true);
    });

    const unsubscribeDisconnected = manager.subscribe('connection:disconnected', () => {
      setConnectionState('disconnected');
      setIsConnected(false);
    });

    const unsubscribeConnecting = manager.subscribe('connection:connecting', () => {
      setConnectionState('connecting');
      setIsConnected(false);
    });

    const unsubscribeError = manager.subscribe('connection:error', () => {
      setConnectionState('error');
      setIsConnected(false);
    });

    // Connect on mount
    manager.connect();

    // Cleanup on unmount
    return () => {
      unsubscribeConnected();
      unsubscribeDisconnected();
      unsubscribeConnecting();
      unsubscribeError();
      
      // Reset mock manager if using mock
      if (shouldUseMock) {
        resetMockWebSocketManager();
      }
    };
  }, [manager, shouldUseMock]);

  return {
    manager,
    connectionState,
    isConnected,
    connect: () => manager.connect(),
    disconnect: () => manager.disconnect(),
    isMockMode: shouldUseMock,
  };
}

// Add useState import
import { useState } from 'react';
