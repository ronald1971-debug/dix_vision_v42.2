/**
 * Unified Markets API Integration
 * 
 * Provides live API integration for the Unified Markets Workspace:
 * - Market data across all asset classes (Crypto, Stocks, Forex, Futures, Options, Commodities, Indices, DEX)
 * - Chart data with multiple chart types (Candlestick, Heikin Ashi, Renko, Range Bars, Tick, Line)
 * - Technical indicators (EMA, SMA, VWAP, Anchored VWAP, RSI, MACD, ATR, Bollinger Bands)
 * - Order flow data (DOM Ladder, Footprint Charts, Volume Delta, Cumulative Delta, Order Book Heatmap, Liquidity Heatmap)
 * - Watchlist management
 * - Market scanner results
 * - News and events feed
 */

import { apiUrl } from '@/api/base';

// ============================================================================
// TYPE DEFINITIONS
// ============================================================================

// Asset Class Types
export type AssetClass = 'Crypto' | 'Stocks' | 'Forex' | 'Futures' | 'Options' | 'Commodities' | 'Indices' | 'DEX';

// Chart Types
export type ChartType = 'candlestick' | 'heikin_ashi' | 'renko' | 'range_bars' | 'tick' | 'line';

// Indicator Types
export type IndicatorType = 'ema' | 'sma' | 'vwap' | 'anchored_vwap' | 'rsi' | 'macd' | 'atr' | 'bollinger';

// Market Data Types
export interface MarketDataPoint {
  timestamp: number;
  open: number;
  high: number;
  low: number;
  close: number;
  volume: number;
}

export interface OHLCVData {
  symbol: string;
  timeframe: string;
  data: MarketDataPoint[];
}

export interface Quote {
  symbol: string;
  price: number;
  change: number;
  changePercent: number;
  volume: number;
  high24h: number;
  low24h: number;
  bid: number;
  ask: number;
  spread: number;
}

// Indicator Data Types
export interface IndicatorValue {
  timestamp: number;
  value: number;
  signal?: 'buy' | 'sell' | 'neutral';
}

export interface IndicatorData {
  type: IndicatorType;
  parameters: Record<string, number>;
  data: IndicatorValue[];
}

export interface VWAPData {
  timestamp: number;
  value: number;
  standardDeviation: number;
}

// Order Flow Data Types
export interface DOMLevel {
  price: number;
  size: number;
  orders: number;
}

export interface DOMLadderData {
  symbol: string;
  bids: DOMLevel[];
  asks: DOMLevel[];
  timestamp: number;
}

export interface FootprintData {
  timestamp: number;
  price: number;
  bidVolume: number;
  askVolume: number;
  delta: number;
}

export interface VolumeDeltaData {
  timestamp: number;
  buyVolume: number;
  sellVolume: number;
  delta: number;
  cumulativeDelta: number;
}

export interface OrderBookHeatmapData {
  symbol: string;
  priceLevels: number[];
  volumeLevels: number[];
  timestamp: number;
}

export interface LiquidityHeatmapData {
  symbol: string;
  priceLevels: number[];
  liquidityLevels: number[];
  timestamp: number;
}

// Watchlist Types
export interface WatchlistItem {
  symbol: string;
  assetClass: AssetClass;
  price: number;
  change: number;
  changePercent: number;
  volume: number;
  addedAt: string;
}

// Scanner Types
export interface ScannerResult {
  symbol: string;
  assetClass: AssetClass;
  price: number;
  changePercent: number;
  volume: number;
  volatility: 'Low' | 'Medium' | 'High';
  reason: string;
  timestamp: string;
}

export interface ScannerFilter {
  assetClass?: AssetClass;
  minVolume?: number;
  minChangePercent?: number;
  maxChangePercent?: number;
  volatility?: 'Low' | 'Medium' | 'High';
  limit?: number;
}

// News & Events Types
export interface NewsItem {
  title: string;
  summary: string;
  source: string;
  timestamp: string;
  url?: string;
  sentiment?: 'positive' | 'negative' | 'neutral';
  symbols: string[];
}

// ============================================================================
// API CLIENT
// ============================================================================

class UnifiedMarketsAPI {
  private baseURL: string;

  constructor(baseURL: string = '/api/markets') {
    this.baseURL = baseURL;
  }

  private async fetchAPI<T>(
    endpoint: string,
    options: RequestInit = {}
  ): Promise<T> {
    const url = apiUrl(`${this.baseURL}${endpoint}`);
    const headers = new Headers();
    headers.set('Content-Type', 'application/json');

    const response = await fetch(url, {
      ...options,
      headers,
    });

    if (!response.ok) {
      throw new Error(`Markets API error: ${response.status} ${response.statusText}`);
    }

    return response.json() as Promise<T>;
  }

  // ============================================================================
  // MARKET DATA ENDPOINTS
  // ============================================================================

  async getQuote(symbol: string): Promise<Quote> {
    return this.fetchAPI<Quote>(`/quote/${symbol}`);
  }

  async getOHLCV(symbol: string, timeframe: string, limit: number = 100): Promise<OHLCVData> {
    return this.fetchAPI<OHLCVData>(`/ohlcv/${symbol}?timeframe=${timeframe}&limit=${limit}`);
  }

  async getOHLCVByChartType(
    symbol: string,
    timeframe: string,
    chartType: ChartType,
    limit: number = 100
  ): Promise<OHLCVData> {
    return this.fetchAPI<OHLCVData>(
      `/ohlcv/${symbol}?timeframe=${timeframe}&chartType=${chartType}&limit=${limit}`
    );
  }

  async getQuotesByAssetClass(assetClass: AssetClass, limit: number = 20): Promise<Quote[]> {
    return this.fetchAPI<Quote[]>(`/quotes/${assetClass}?limit=${limit}`);
  }

  // ============================================================================
  // INDICATOR ENDPOINTS
  // ============================================================================

  async getIndicator(
    symbol: string,
    indicator: IndicatorType,
    parameters: Record<string, number>
  ): Promise<IndicatorData> {
    const params = new URLSearchParams();
    Object.entries(parameters).forEach(([key, value]) => {
      params.append(key, value.toString());
    });
    return this.fetchAPI<IndicatorData>(`/indicators/${symbol}/${indicator}?${params}`);
  }

  async getVWAP(symbol: string): Promise<VWAPData[]> {
    return this.fetchAPI<VWAPData[]>(`/indicators/${symbol}/vwap`);
  }

  async getAnchoredVWAP(symbol: string, anchorTimestamp: number): Promise<VWAPData[]> {
    return this.fetchAPI<VWAPData[]>(`/indicators/${symbol}/anchored-vwap?anchor=${anchorTimestamp}`);
  }

  async getBollingerBands(
    symbol: string,
    period: number = 20,
    stdDev: number = 2
  ): Promise<{ upper: number[]; middle: number[]; lower: number[] }> {
    return this.fetchAPI(
      `/indicators/${symbol}/bollinger?period=${period}&stdDev=${stdDev}`
    );
  }

  // ============================================================================
  // ORDER FLOW ENDPOINTS
  // ============================================================================

  async getDOMLadder(symbol: string, depth: number = 20): Promise<DOMLadderData> {
    return this.fetchAPI<DOMLadderData>(`/orderflow/${String(symbol)}/dom?depth=${depth}`);
  }

  async getFootprintChart(
    symbol: string,
    timeframe: string,
    limit: number = 100
  ): Promise<FootprintData[]> {
    return this.fetchAPI<FootprintData[]>(
      `/orderflow/${symbol}/footprint?timeframe=${timeframe}&limit=${limit}`
    );
  }

  async getVolumeDelta(
    symbol: string,
    timeframe: string,
    limit: number = 100
  ): Promise<VolumeDeltaData[]> {
    return this.fetchAPI<VolumeDeltaData[]>(
      `/orderflow/${symbol}/volume-delta?timeframe=${timeframe}&limit=${limit}`
    );
  }

  async getOrderBookHeatmap(symbol: string, levels: number = 20): Promise<OrderBookHeatmapData> {
    return this.fetchAPI<OrderBookHeatmapData>(
      `/orderflow/${symbol}/heatmap?levels=${levels}`
    );
  }

  async getLiquidityHeatmap(symbol: string, levels: number = 20): Promise<LiquidityHeatmapData> {
    return this.fetchAPI<LiquidityHeatmapData>(
      `/orderflow/${symbol}/liquidity-heatmap?levels=${levels}`
    );
  }

  // ============================================================================
  // WATCHLIST ENDPOINTS
  // ============================================================================

  async getWatchlist(): Promise<WatchlistItem[]> {
    return this.fetchAPI<WatchlistItem[]>('/watchlist');
  }

  async addToWatchlist(symbol: string, assetClass: AssetClass): Promise<{ success: boolean }> {
    return this.fetchAPI('/watchlist', {
      method: 'POST',
      body: JSON.stringify({ symbol, assetClass }),
    });
  }

  async removeFromWatchlist(symbol: string): Promise<{ success: boolean }> {
    return this.fetchAPI(`/watchlist/${symbol}`, {
      method: 'DELETE',
    });
  }

  // ============================================================================
  // MARKET SCANNER ENDPOINTS
  // ============================================================================

  async scanMarkets(filter: ScannerFilter): Promise<ScannerResult[]> {
    const params = new URLSearchParams();
    if (filter.assetClass) params.append('assetClass', filter.assetClass);
    if (filter.minVolume) params.append('minVolume', filter.minVolume.toString());
    if (filter.minChangePercent) params.append('minChangePercent', filter.minChangePercent.toString());
    if (filter.maxChangePercent) params.append('maxChangePercent', filter.maxChangePercent.toString());
    if (filter.volatility) params.append('volatility', filter.volatility);
    if (filter.limit) params.append('limit', filter.limit.toString());
    
    return this.fetchAPI<ScannerResult[]>(`/scanner?${params}`);
  }

  async getTopGainers(assetClass?: AssetClass, limit: number = 10): Promise<ScannerResult[]> {
    const params = new URLSearchParams();
    if (assetClass) params.append('assetClass', assetClass);
    params.append('limit', limit.toString());
    return this.fetchAPI<ScannerResult[]>(`/scanner/gainers?${params}`);
  }

  async getTopLosers(assetClass?: AssetClass, limit: number = 10): Promise<ScannerResult[]> {
    const params = new URLSearchParams();
    if (assetClass) params.append('assetClass', assetClass);
    params.append('limit', limit.toString());
    return this.fetchAPI<ScannerResult[]>(`/scanner/losers?${params}`);
  }

  async getHighVolume(assetClass?: AssetClass, limit: number = 10): Promise<ScannerResult[]> {
    const params = new URLSearchParams();
    if (assetClass) params.append('assetClass', assetClass);
    params.append('limit', limit.toString());
    return this.fetchAPI<ScannerResult[]>(`/scanner/volume?${params}`);
  }

  async getHighVolatility(assetClass?: AssetClass, limit: number = 10): Promise<ScannerResult[]> {
    const params = new URLSearchParams();
    if (assetClass) params.append('assetClass', assetClass);
    params.append('limit', limit.toString());
    return this.fetchAPI<ScannerResult[]>(`/scanner/volatility?${params}`);
  }

  // ============================================================================
  // NEWS & EVENTS ENDPOINTS
  // ============================================================================

  async getNews(symbol?: string, limit: number = 20): Promise<NewsItem[]> {
    const params = new URLSearchParams();
    if (symbol) params.append('symbol', symbol);
    params.append('limit', limit.toString());
    return this.fetchAPI<NewsItem[]>(`/news?${params}`);
  }

  async getNewsByAssetClass(assetClass: AssetClass, limit: number = 20): Promise<NewsItem[]> {
    return this.fetchAPI<NewsItem[]>(`/news/${assetClass}?limit=${limit}`);
  }

  async getUpcomingEvents(limit: number = 10): Promise<NewsItem[]> {
    return this.fetchAPI<NewsItem[]>(`/events?limit=${limit}`);
  }

  // ============================================================================
  // WEBSOCKET CONNECTIONS
  // ============================================================================

  connectToQuoteUpdates(callback: (data: any) => void, symbols?: string[]): WebSocket {
    const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
    const host = window.location.host;
    const symbolsParam = symbols ? `?symbols=${symbols.join(',')}` : '';
    const ws = new WebSocket(`${protocol}//${host}${this.baseURL}/ws/quotes${symbolsParam}`);

    ws.onopen = () => {
      console.log('[Markets API] Quotes WebSocket connected');
    };

    ws.onmessage = (event) => {
      try {
        const data = JSON.parse(event.data);
        callback(data);
      } catch (error) {
        console.error('[Markets API] WebSocket parse error:', error);
      }
    };

    ws.onerror = (error) => {
      console.error('[Markets API] WebSocket error:', error);
    };

    ws.onclose = () => {
      console.log('[Markets API] WebSocket disconnected');
    };

    return ws;
  }

  connectToOrderFlowUpdates(callback: (data: any) => void, symbol: string): WebSocket {
    const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
    const host = window.location.host;
    const ws = new WebSocket(`${protocol}//${host}${this.baseURL}/ws/orderflow/${symbol}`);

    ws.onopen = () => {
      console.log('[Markets API] Order flow WebSocket connected');
    };

    ws.onmessage = (event) => {
      try {
        const data = JSON.parse(event.data);
        callback(data);
      } catch (error) {
        console.error('[Markets API] WebSocket parse error:', error);
      }
    };

    ws.onerror = (error) => {
      console.error('[Markets API] WebSocket error:', error);
    };

    ws.onclose = () => {
      console.log('[Markets API] WebSocket disconnected');
    };

    return ws;
  }

  connectToMarketScannerUpdates(callback: (data: any) => void): WebSocket {
    const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
    const host = window.location.host;
    const ws = new WebSocket(`${protocol}//${host}${this.baseURL}/ws/scanner`);

    ws.onopen = () => {
      console.log('[Markets API] Scanner WebSocket connected');
    };

    ws.onmessage = (event) => {
      try {
        const data = JSON.parse(event.data);
        callback(data);
      } catch (error) {
        console.error('[Markets API] WebSocket parse error:', error);
      }
    };

    ws.onerror = (error) => {
      console.error('[Markets API] WebSocket error:', error);
    };

    ws.onclose = () => {
      console.log('[Markets API] WebSocket disconnected');
    };

    return ws;
  }
}

// Singleton instance
let unifiedMarketsAPIInstance: UnifiedMarketsAPI | null = null;

export function getUnifiedMarketsAPI(): UnifiedMarketsAPI {
  if (!unifiedMarketsAPIInstance) {
    unifiedMarketsAPIInstance = new UnifiedMarketsAPI();
  }
  return unifiedMarketsAPIInstance;
}
