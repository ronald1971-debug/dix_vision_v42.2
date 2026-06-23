/**
 * Enhanced World-Aware WebSocket Hook
 * 
 * Replaces legacy useWebSocketWithMock with world-aware implementation
 * that provides cognitive state integration and deterministic behavior per TIER-0 Production standards.
 */

import { useState, useEffect, useRef, useCallback } from "react";
import { useCognitiveStream } from "@/state/cognitive_realtime";
import { useAutonomyMode, AutonomyMode } from "@/state/autonomy";

// ============================================================================
// WebSocket Message Types
// ============================================================================

interface WebSocketMessage {
  type: string;
  payload: any;
  timestamp?: string;
  channel?: string;
}

interface EnhancedWebSocketState {
  connected: boolean;
  connecting: boolean;
  error: string | null;
  messages: WebSocketMessage[];
  cognitiveState: {
    regime: string;
    confidence: number;
    understanding: number;
  };
  autonomyLevel: AutonomyMode;
}

// ============================================================================
// Enhanced World-Aware WebSocket Hook
// ============================================================================

export function useEnhancedWorldAwareWebSocket(url: string) {
  const [autonomyMode] = useAutonomyMode();
  const { events: indiraEvents, live: indiraLive } = useCognitiveStream('indira', 50);
  const { events: dyonEvents, live: dyonLive } = useCognitiveStream('dyon', 50);
  
  const [state, setState] = useState<EnhancedWebSocketState>({
    connected: false,
    connecting: false,
    error: null,
    messages: [],
    cognitiveState: {
      regime: 'NORMAL',
      confidence: 0.85,
      understanding: 0.78,
    },
    autonomyLevel: autonomyMode,
  });

  const wsRef = useRef<WebSocket | null>(null);
  const reconnectTimeoutRef = useRef<number | null>(null);
  const messageQueueRef = useRef<WebSocketMessage[]>([]);

  // Update cognitive state based on stream events
  useEffect(() => {
    const allEvents = [...indiraEvents, ...dyonEvents];
    if (allEvents.length > 0) {
      const latestEvent = allEvents[allEvents.length - 1] as any;
      if (latestEvent && typeof latestEvent === 'object') {
        setState((prev: EnhancedWebSocketState) => ({
          ...prev,
          cognitiveState: {
            regime: latestEvent.regime || prev.cognitiveState.regime,
            confidence: latestEvent.confidence ?? prev.cognitiveState.confidence,
            understanding: latestEvent.causalUnderstanding ?? prev.cognitiveState.understanding,
          },
          connected: indiraLive || dyonLive,
        }));
      }
    }
  }, [indiraEvents, dyonEvents, indiraLive, dyonLive]);

  // Update autonomy level
  useEffect(() => {
    setState((prev: EnhancedWebSocketState) => ({
      ...prev,
      autonomyLevel: autonomyMode,
    }));
  }, [autonomyMode]);

  // Enhanced message with world context
  const enhanceMessage = useCallback((message: WebSocketMessage): WebSocketMessage => {
    return {
      ...message,
      timestamp: message.timestamp || new Date().toISOString(),
    };
  }, []);

  // Connect to WebSocket
  const connect = useCallback(() => {
    if (wsRef.current?.readyState === WebSocket.OPEN) return;
    
    setState((prev: EnhancedWebSocketState) => ({ ...prev, connecting: true, error: null }));
    
    try {
      const ws = new WebSocket(url);
      wsRef.current = ws;

      ws.onopen = () => {
        setState((prev: EnhancedWebSocketState) => ({
          ...prev,
          connected: true,
          connecting: false,
          error: null,
        }));
        
        // Send queued messages
        messageQueueRef.current.forEach((msg: WebSocketMessage) => {
          ws.send(JSON.stringify(enhanceMessage(msg)));
        });
        messageQueueRef.current = [];
      };

      ws.onmessage = (event: MessageEvent) => {
        try {
          const message = JSON.parse(event.data) as WebSocketMessage;
          setState((prev: EnhancedWebSocketState) => ({
            ...prev,
            messages: [...prev.messages, enhanceMessage(message)].slice(-100),
          }));
        } catch (error) {
          console.error('[EnhancedWebSocket] Message parse error:', error);
        }
      };

      ws.onerror = (error) => {
        console.error('[EnhancedWebSocket] Error:', error);
        setState((prev: EnhancedWebSocketState) => ({
          ...prev,
          connected: false,
          connecting: false,
          error: 'WebSocket connection error',
        }));
      };

      ws.onclose = () => {
        setState((prev: EnhancedWebSocketState) => ({
          ...prev,
          connected: false,
          connecting: false,
        }));
        
        // Attempt reconnection after delay
        if (reconnectTimeoutRef.current) {
          clearTimeout(reconnectTimeoutRef.current);
        }
        reconnectTimeoutRef.current = window.setTimeout(() => {
          connect();
        }, 5000);
      };

    } catch (error) {
      setState((prev: EnhancedWebSocketState) => ({
        ...prev,
        connected: false,
        connecting: false,
        error: 'Failed to create WebSocket connection',
      }));
    }
  }, [url, enhanceMessage]);

  // Disconnect from WebSocket
  const disconnect = useCallback(() => {
    if (reconnectTimeoutRef.current) {
      clearTimeout(reconnectTimeoutRef.current);
    }
    
    if (wsRef.current) {
      wsRef.current.close();
      wsRef.current = null;
    }
    
    setState((prev: EnhancedWebSocketState) => ({
      ...prev,
      connected: false,
      connecting: false,
    }));
  }, []);

  // Send message with world context enhancement
  const sendMessage = useCallback((message: WebSocketMessage) => {
    const enhancedMessage = enhanceMessage(message);
    
    if (wsRef.current?.readyState === WebSocket.OPEN) {
      wsRef.current.send(JSON.stringify(enhancedMessage));
    } else {
      // Queue message for when connection is established
      messageQueueRef.current.push(enhancedMessage);
    }
  }, [enhanceMessage]);

  // Cleanup on unmount
  useEffect(() => {
    return () => {
      disconnect();
    };
  }, [disconnect]);

  return {
    ...state,
    connect,
    disconnect,
    sendMessage,
    isConnected: state.connected,
    isConnecting: state.connecting,
    hasError: !!state.error,
    cognitiveLive: indiraLive || dyonLive,
  };
}
