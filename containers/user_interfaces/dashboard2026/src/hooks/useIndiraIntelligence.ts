/**
 * React hooks for INDIRA Cognitive Center API integration
 * 
 * Provides custom hooks for fetching and managing real-time data from
 * the INDIRA intelligence API for all cognitive center tabs
 */

import { useQuery } from '@tanstack/react-query';
import { useCallback, useRef } from 'react';
import { getIndiraIntelligenceAPI } from '@/api/indiraIntelligence';

const api = getIndiraIntelligenceAPI();

// ============================================================================
// MARKET INTELLIGENCE HOOKS
// ============================================================================

export function useMarketRegimes() {
  return useQuery({
    queryKey: ['indira', 'market', 'regimes'],
    queryFn: () => api.getMarketRegimes(),
    refetchInterval: 30000, // Refresh every 30 seconds
    staleTime: 10000, // Consider data fresh for 10 seconds
  });
}

export function useMarketNarratives() {
  return useQuery({
    queryKey: ['indira', 'market', 'narratives'],
    queryFn: () => api.getMarketNarratives(),
    refetchInterval: 30000,
    staleTime: 10000,
  });
}

export function useLiquidityData() {
  return useQuery({
    queryKey: ['indira', 'market', 'liquidity'],
    queryFn: () => api.getLiquidityData(),
    refetchInterval: 15000, // Refresh every 15 seconds
    staleTime: 5000,
  });
}

export function useVolatilityData() {
  return useQuery({
    queryKey: ['indira', 'market', 'volatility'],
    queryFn: () => api.getVolatilityData(),
    refetchInterval: 30000,
    staleTime: 10000,
  });
}

export function useOrderFlowData() {
  return useQuery({
    queryKey: ['indira', 'market', 'orderflow'],
    queryFn: () => api.getOrderFlowData(),
    refetchInterval: 5000, // Refresh every 5 seconds (high frequency)
    staleTime: 2000,
  });
}

export function useCrossAssetData() {
  return useQuery({
    queryKey: ['indira', 'market', 'crossasset'],
    queryFn: () => api.getCrossAssetData(),
    refetchInterval: 60000, // Refresh every minute
    staleTime: 30000,
  });
}

// ============================================================================
// TRADER INTELLIGENCE HOOKS
// ============================================================================

export function useTopTraders(limit: number = 10) {
  return useQuery({
    queryKey: ['indira', 'traders', 'top', limit],
    queryFn: () => api.getTopTraders(limit),
    refetchInterval: 60000,
    staleTime: 30000,
  });
}

export function useTraderProfile(address: string) {
  return useQuery({
    queryKey: ['indira', 'traders', 'profile', address],
    queryFn: () => api.getTraderProfile(address),
    enabled: !!address,
    refetchInterval: 120000,
    staleTime: 60000,
  });
}

export function useTraderClusters() {
  return useQuery({
    queryKey: ['indira', 'traders', 'clusters'],
    queryFn: () => api.getTraderClusters(),
    refetchInterval: 300000, // Refresh every 5 minutes
    staleTime: 120000,
  });
}

export function useTraderRelationships() {
  return useQuery({
    queryKey: ['indira', 'traders', 'relationships'],
    queryFn: () => api.getTraderRelationships(),
    refetchInterval: 120000,
    staleTime: 60000,
  });
}

export function useTraderSimilarity(address: string) {
  return useQuery({
    queryKey: ['indira', 'traders', 'similarity', address],
    queryFn: () => api.getTraderSimilarity(address),
    enabled: !!address,
    refetchInterval: 180000,
    staleTime: 90000,
  });
}

export function useTraderPerformanceOverview() {
  return useQuery({
    queryKey: ['indira', 'traders', 'performance'],
    queryFn: () => api.getTraderPerformanceOverview(),
    refetchInterval: 120000,
    staleTime: 60000,
  });
}

export function useSearchTraders(query: string) {
  return useQuery({
    queryKey: ['indira', 'traders', 'search', query],
    queryFn: () => api.searchTraders(query),
    enabled: query.length > 2,
    refetchInterval: 60000,
    staleTime: 30000,
  });
}

// ============================================================================
// STRATEGY INTELLIGENCE HOOKS
// ============================================================================

export function useStrategyCreation() {
  return useQuery({
    queryKey: ['indira', 'strategy', 'creation'],
    queryFn: () => api.getStrategyCreation(),
    refetchInterval: 60000,
    staleTime: 30000,
  });
}

export function useStrategyEvolution() {
  return useQuery({
    queryKey: ['indira', 'strategy', 'evolution'],
    queryFn: () => api.getStrategyEvolution(),
    refetchInterval: 120000,
    staleTime: 60000,
  });
}

export function useStrategyOptimization() {
  return useQuery({
    queryKey: ['indira', 'strategy', 'optimization'],
    queryFn: () => api.getStrategyOptimization(),
    refetchInterval: 60000,
    staleTime: 30000,
  });
}

export function useStrategyBacktesting() {
  return useQuery({
    queryKey: ['indira', 'strategy', 'backtesting'],
    queryFn: () => api.getStrategyBacktesting(),
    refetchInterval: 120000,
    staleTime: 60000,
  });
}

export function useStrategyDeployment() {
  return useQuery({
    queryKey: ['indira', 'strategy', 'deployment'],
    queryFn: () => api.getStrategyDeployment(),
    refetchInterval: 30000,
    staleTime: 15000,
  });
}

// ============================================================================
// PORTFOLIO INTELLIGENCE HOOKS
// ============================================================================

export function usePortfolioAnalysis() {
  return useQuery({
    queryKey: ['indira', 'portfolio', 'analysis'],
    queryFn: () => api.getPortfolioAnalysis(),
    refetchInterval: 10000, // Refresh every 10 seconds (high frequency)
    staleTime: 5000,
  });
}

export function usePortfolioAllocation() {
  return useQuery({
    queryKey: ['indira', 'portfolio', 'allocation'],
    queryFn: () => api.getPortfolioAllocation(),
    refetchInterval: 30000,
    staleTime: 15000,
  });
}

export function usePortfolioRisk() {
  return useQuery({
    queryKey: ['indira', 'portfolio', 'risk'],
    queryFn: () => api.getPortfolioRisk(),
    refetchInterval: 15000, // Refresh every 15 seconds
    staleTime: 7500,
  });
}

export function usePortfolioPerformance() {
  return useQuery({
    queryKey: ['indira', 'portfolio', 'performance'],
    queryFn: () => api.getPortfolioPerformance(),
    refetchInterval: 60000,
    staleTime: 30000,
  });
}

export function usePortfolioAttribution() {
  return useQuery({
    queryKey: ['indira', 'portfolio', 'attribution'],
    queryFn: () => api.getPortfolioAttribution(),
    refetchInterval: 120000,
    staleTime: 60000,
  });
}

// ============================================================================
// RESEARCH INTELLIGENCE HOOKS
// ============================================================================

export function useResearchQueue() {
  return useQuery({
    queryKey: ['indira', 'research', 'queue'],
    queryFn: () => api.getResearchQueue(),
    refetchInterval: 30000,
    staleTime: 15000,
  });
}

export function useKnowledgeGraph() {
  return useQuery({
    queryKey: ['indira', 'research', 'knowledge-graph'],
    queryFn: () => api.getKnowledgeGraph(),
    refetchInterval: 120000,
    staleTime: 60000,
  });
}

export function useModelLearning() {
  return useQuery({
    queryKey: ['indira', 'research', 'learning'],
    queryFn: () => api.getModelLearning(),
    refetchInterval: 10000, // Refresh every 10 seconds
    staleTime: 5000,
  });
}

export function useResearchPublication() {
  return useQuery({
    queryKey: ['indira', 'research', 'publications'],
    queryFn: () => api.getResearchPublication(),
    refetchInterval: 120000,
    staleTime: 60000,
  });
}

export function useResearchCollaboration() {
  return useQuery({
    queryKey: ['indira', 'research', 'collaboration'],
    queryFn: () => api.getResearchCollaboration(),
    refetchInterval: 60000,
    staleTime: 30000,
  });
}

// ============================================================================
// WEBSOCKET HOOKS
// ============================================================================

export function useMarketWebSocket() {
  const wsRef = useRef<WebSocket | null>(null);
  const callbackRef = useRef<((data: any) => void) | null>(null);

  const connect = useCallback((callback: (data: any) => void) => {
    callbackRef.current = callback;
    
    if (wsRef.current?.readyState === WebSocket.OPEN) {
      return; // Already connected
    }

    wsRef.current = api.connectToMarketUpdates((data) => {
      if (callbackRef.current) {
        callbackRef.current(data);
      }
    });

    return () => {
      if (wsRef.current) {
        wsRef.current.close();
        wsRef.current = null;
      }
    };
  }, []);

  const disconnect = useCallback(() => {
    if (wsRef.current) {
      wsRef.current.close();
      wsRef.current = null;
    }
  }, []);

  return { connect, disconnect, isConnected: wsRef.current?.readyState === WebSocket.OPEN };
}

export function useTraderWebSocket() {
  const wsRef = useRef<WebSocket | null>(null);
  const callbackRef = useRef<((data: any) => void) | null>(null);

  const connect = useCallback((callback: (data: any) => void) => {
    callbackRef.current = callback;
    
    if (wsRef.current?.readyState === WebSocket.OPEN) {
      return; // Already connected
    }

    wsRef.current = api.connectToTraderUpdates((data) => {
      if (callbackRef.current) {
        callbackRef.current(data);
      }
    });

    return () => {
      if (wsRef.current) {
        wsRef.current.close();
        wsRef.current = null;
      }
    };
  }, []);

  const disconnect = useCallback(() => {
    if (wsRef.current) {
      wsRef.current.close();
      wsRef.current = null;
    }
  }, []);

  return { connect, disconnect, isConnected: wsRef.current?.readyState === WebSocket.OPEN };
}
