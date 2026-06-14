/**
 * React hooks for Unified Markets API integration
 * 
 * Provides custom hooks for fetching and managing real-time data from
 * the Unified Markets API for all asset classes and chart types
 */

import { useQuery } from '@tanstack/react-query';
import { useCallback, useRef } from 'react';
import { getUnifiedMarketsAPI, type AssetClass, type ChartType, type IndicatorType } from '@/api/markets';

const api = getUnifiedMarketsAPI();

// ============================================================================
// MARKET DATA HOOKS
// ============================================================================

export function useQuote(symbol: string, enabled: boolean = true) {
  return useQuery({
    queryKey: ['markets', 'quote', symbol],
    queryFn: () => api.getQuote(symbol),
    enabled: enabled && !!symbol,
    refetchInterval: 2000, // Refresh every 2 seconds
    staleTime: 1000,
  });
}

export function useOHLCV(symbol: string, timeframe: string, chartType?: ChartType, enabled: boolean = true) {
  return useQuery({
    queryKey: ['markets', 'ohlcv', symbol, timeframe, chartType],
    queryFn: () => chartType 
      ? api.getOHLCVByChartType(symbol, timeframe, chartType)
      : api.getOHLCV(symbol, timeframe),
    enabled: enabled && !!symbol,
    refetchInterval: 5000,
    staleTime: 2500,
  });
}

export function useQuotesByAssetClass(assetClass: AssetClass, limit: number = 20) {
  return useQuery({
    queryKey: ['markets', 'quotes', assetClass, limit],
    queryFn: () => api.getQuotesByAssetClass(assetClass, limit),
    refetchInterval: 5000,
    staleTime: 2500,
  });
}

// ============================================================================
// INDICATOR HOOKS
// ============================================================================

export function useIndicator(
  symbol: string,
  indicator: IndicatorType,
  parameters: Record<string, number>,
  enabled: boolean = true
) {
  return useQuery({
    queryKey: ['markets', 'indicator', symbol, indicator, parameters],
    queryFn: () => api.getIndicator(symbol, indicator, parameters),
    enabled: enabled && !!symbol,
    refetchInterval: 10000,
    staleTime: 5000,
  });
}

export function useVWAP(symbol: string, enabled: boolean = true) {
  return useQuery({
    queryKey: ['markets', 'vwap', symbol],
    queryFn: () => api.getVWAP(symbol),
    enabled: enabled && !!symbol,
    refetchInterval: 10000,
    staleTime: 5000,
  });
}

export function useBollingerBands(
  symbol: string,
  period: number = 20,
  stdDev: number = 2,
  enabled: boolean = true
) {
  return useQuery({
    queryKey: ['markets', 'bollinger', symbol, period, stdDev],
    queryFn: () => api.getBollingerBands(symbol, period, stdDev),
    enabled: enabled && !!symbol,
    refetchInterval: 10000,
    staleTime: 5000,
  });
}

// ============================================================================
// ORDER FLOW HOOKS
// ============================================================================

export function useDOMLadder(symbol: string, depth: number = 20, enabled: boolean = true) {
  return useQuery({
    queryKey: ['markets', 'dom', symbol, depth],
    queryFn: () => api.getDOMLadder(symbol, depth),
    enabled: enabled && !!symbol,
    refetchInterval: 1000, // High frequency for order book
    staleTime: 500,
  });
}

export function useVolumeDelta(
  symbol: string,
  timeframe: string,
  limit: number = 100,
  enabled: boolean = true
) {
  return useQuery({
    queryKey: ['markets', 'volume-delta', symbol, timeframe, limit],
    queryFn: () => api.getVolumeDelta(symbol, timeframe, limit),
    enabled: enabled && !!symbol,
    refetchInterval: 2000,
    staleTime: 1000,
  });
}

export function useOrderBookHeatmap(symbol: string, levels: number = 20, enabled: boolean = true) {
  return useQuery({
    queryKey: ['markets', 'heatmap', symbol, levels],
    queryFn: () => api.getOrderBookHeatmap(symbol, levels),
    enabled: enabled && !!symbol,
    refetchInterval: 1000,
    staleTime: 500,
  });
}

export function useLiquidityHeatmap(symbol: string, levels: number = 20, enabled: boolean = true) {
  return useQuery({
    queryKey: ['markets', 'liquidity-heatmap', symbol, levels],
    queryFn: () => api.getLiquidityHeatmap(symbol, levels),
    enabled: enabled && !!symbol,
    refetchInterval: 2000,
    staleTime: 1000,
  });
}

// ============================================================================
// WATCHLIST HOOKS
// ============================================================================

export function useWatchlist() {
  return useQuery({
    queryKey: ['markets', 'watchlist'],
    queryFn: () => api.getWatchlist(),
    refetchInterval: 10000,
    staleTime: 5000,
  });
}

// ============================================================================
// MARKET SCANNER HOOKS
// ============================================================================

export function useTopGainers(assetClass?: AssetClass, limit: number = 10) {
  return useQuery({
    queryKey: ['markets', 'scanner', 'gainers', assetClass, limit],
    queryFn: () => api.getTopGainers(assetClass, limit),
    refetchInterval: 30000,
    staleTime: 15000,
  });
}

export function useTopLosers(assetClass?: AssetClass, limit: number = 10) {
  return useQuery({
    queryKey: ['markets', 'scanner', 'losers', assetClass, limit],
    queryFn: () => api.getTopLosers(assetClass, limit),
    refetchInterval: 30000,
    staleTime: 15000,
  });
}

export function useHighVolume(assetClass?: AssetClass, limit: number = 10) {
  return useQuery({
    queryKey: ['markets', 'scanner', 'volume', assetClass, limit],
    queryFn: () => api.getHighVolume(assetClass, limit),
    refetchInterval: 30000,
    staleTime: 15000,
  });
}

export function useHighVolatility(assetClass?: AssetClass, limit: number = 10) {
  return useQuery({
    queryKey: ['markets', 'scanner', 'volatility', assetClass, limit],
    queryFn: () => api.getHighVolatility(assetClass, limit),
    refetchInterval: 30000,
    staleTime: 15000,
  });
}

// ============================================================================
// NEWS & EVENTS HOOKS
// ============================================================================

export function useNews(symbol?: string, limit: number = 20) {
  return useQuery({
    queryKey: ['markets', 'news', symbol, limit],
    queryFn: () => api.getNews(symbol, limit),
    refetchInterval: 120000,
    staleTime: 60000,
  });
}

export function useNewsByAssetClass(assetClass: AssetClass, limit: number = 20) {
  return useQuery({
    queryKey: ['markets', 'news', assetClass, limit],
    queryFn: () => api.getNewsByAssetClass(assetClass, limit),
    refetchInterval: 120000,
    staleTime: 60000,
  });
}

export function useUpcomingEvents(limit: number = 10) {
  return useQuery({
    queryKey: ['markets', 'events', limit],
    queryFn: () => api.getUpcomingEvents(limit),
    refetchInterval: 60000,
    staleTime: 30000,
  });
}

// ============================================================================
// WEBSOCKET HOOKS
// ============================================================================

export function useQuoteWebSocket() {
  const wsRef = useRef<WebSocket | null>(null);
  const callbackRef = useRef<((data: any) => void) | null>(null);

  const connect = useCallback((callback: (data: any) => void, symbols?: string[]) => {
    callbackRef.current = callback;
    
    if (wsRef.current?.readyState === WebSocket.OPEN) {
      return; // Already connected
    }

    wsRef.current = api.connectToQuoteUpdates((data) => {
      if (callbackRef.current) {
        callbackRef.current(data);
      }
    }, symbols);

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

export function useOrderFlowWebSocket() {
  const wsRef = useRef<WebSocket | null>(null);
  const callbackRef = useRef<((data: any) => void) | null>(null);

  const connect = useCallback((callback: (data: any) => void, symbol: string) => {
    callbackRef.current = callback;
    
    if (wsRef.current?.readyState === WebSocket.OPEN) {
      return; // Already connected
    }

    wsRef.current = api.connectToOrderFlowUpdates((data) => {
      if (callbackRef.current) {
        callbackRef.current(data);
      }
    }, symbol);

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

export function useScannerWebSocket() {
  const wsRef = useRef<WebSocket | null>(null);
  const callbackRef = useRef<((data: any) => void) | null>(null);

  const connect = useCallback((callback: (data: any) => void) => {
    callbackRef.current = callback;
    
    if (wsRef.current?.readyState === WebSocket.OPEN) {
      return; // Already connected
    }

    wsRef.current = api.connectToMarketScannerUpdates((data) => {
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
