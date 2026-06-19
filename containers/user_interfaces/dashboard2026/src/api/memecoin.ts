/**
 * dashboard2026/src/api/memecoin.ts
 * Memecoin Trading API Client
 * 
 * Real-time on-chain analytics, security analysis, and memecoin trading integration
 * Based on analysis of DexScreener, GMGN.AI, Pump.fun, and GeckoTerminal
 */

// ============================================================================
// TYPES
// ============================================================================

export type Blockchain = 'solana' | 'ethereum' | 'bsc' | 'base' | 'arbitrum' | 'polygon';

export interface TokenProfile {
  address: string;
  symbol: string;
  name: string;
  chain: Blockchain;
  description?: string;
  logo_url?: string;
  created_at: string;
  updated_at: string;
  metadata: {
    category?: string;
    tags?: string[];
    social_links?: {
      twitter?: string;
      telegram?: string;
      website?: string;
    };
  };
}

export interface PoolInfo {
  address: string;
  token_address: string;
  chain: Blockchain;
  dex: string;
  pair_address: string;
  liquidity_usd: number;
  volume_24h_usd: number;
  price_usd: number;
  price_change_24h: number;
  created_at: string;
  transactions_24h: {
    buys: number;
    sells: number;
  };
}

export interface SecurityScore {
  address: string;
  overall_score: number; // 0-100
  liquidity_locked: boolean;
  mint_authority_revoked: boolean;
  freeze_authority_revoked: boolean;
  rug_pull_risk: 'low' | 'medium' | 'high';
  honeypot_detected: boolean;
  tax_buy: number;
  tax_sell: number;
  holder_distribution: {
    top_10_holders_percentage: number;
    unique_holders: number;
  };
  transaction_patterns: {
    suspicious_activity: boolean;
    large_sells_24h: number;
    dev_wallet_sold: boolean;
  };
  analyzed_at: string;
}

export interface WhaleActivity {
  wallet_address: string;
  chain: Blockchain;
  tokens_tracked: string[];
  recent_activity: {
    token_address: string;
    action: 'buy' | 'sell';
    amount_usd: number;
    timestamp: string;
  }[];
  profit_score: number; // 0-100
  win_rate: number; // 0-100
}

export interface TokenBoost {
  token_address: string;
  chain: Blockchain;
  boost_amount: number;
  booster_address: string;
  timestamp: string;
  message?: string;
}

export interface CommunityTakeover {
  token_address: string;
  chain: Blockchain;
  previous_community: string;
  new_community: string;
  takeover_timestamp: string;
  confidence_score: number;
}

// ============================================================================
// API CLIENT
// ============================================================================

export class MemecoinAPI {
  private baseURL: string;
  private token: string | null = null;

  constructor(baseURL: string = '/api/memecoin') {
    this.baseURL = baseURL;
    this.loadToken();
  }

  private loadToken(): void {
    this.token = localStorage.getItem('dix_token') || null;
  }

  private async fetchAPI<T>(
    endpoint: string,
    options: RequestInit = {}
  ): Promise<T> {
    const url = `${this.baseURL}${endpoint}`;
    const headers = new Headers();
    headers.set('Content-Type', 'application/json');
    
    if (this.token) {
      headers.set('Authorization', `Bearer ${this.token}`);
    }
    
    if (options.headers) {
      const optionsHeaders = options.headers as Headers;
      optionsHeaders.forEach((value, key) => {
        headers.set(key, value);
      });
    }

    const response = await fetch(url, {
      ...options,
      headers,
    });

    if (!response.ok) {
      throw new Error(`Memecoin API error: ${response.status} ${response.statusText}`);
    }

    return response.json() as Promise<T>;
  }

  // ============================================================================
  // BLOCKCHAIN INDEXER
  // ============================================================================

  async startIndexer(chain: Blockchain): Promise<{ success: boolean; message?: string }> {
    return this.fetchAPI('/indexer/start', {
      method: 'POST',
      body: JSON.stringify({ chain }),
    });
  }

  async stopIndexer(chain: Blockchain): Promise<{ success: boolean }> {
    return this.fetchAPI('/indexer/stop', {
      method: 'POST',
      body: JSON.stringify({ chain }),
    });
  }

  async getIndexerStatus(chain: Blockchain): Promise<{
    running: boolean;
    last_block: number;
    pools_indexed: number;
    uptime_seconds: number;
  }> {
    return this.fetchAPI(`/indexer/status/${chain}`);
  }

  async getNewPools(chain: Blockchain, limit: number = 50): Promise<PoolInfo[]> {
    return this.fetchAPI(`/pools/new/${chain}?limit=${limit}`);
  }

  async getHotPools(chain: Blockchain, limit: number = 50): Promise<PoolInfo[]> {
    return this.fetchAPI(`/pools/hot/${chain}?limit=${limit}`);
  }

  // ============================================================================
  // SECURITY ANALYSIS
  // ============================================================================

  async analyzeSecurity(tokenAddress: string, chain: Blockchain): Promise<SecurityScore> {
    return this.fetchAPI(`/security/analyze`, {
      method: 'POST',
      body: JSON.stringify({ token_address: tokenAddress, chain }),
    });
  }

  async getSecurityScore(tokenAddress: string, chain: Blockchain): Promise<SecurityScore> {
    return this.fetchAPI(`/security/score/${chain}/${tokenAddress}`);
  }

  async batchSecurityAnalysis(tokenAddresses: string[], chain: Blockchain): Promise<SecurityScore[]> {
    return this.fetchAPI(`/security/batch`, {
      method: 'POST',
      body: JSON.stringify({ token_addresses: tokenAddresses, chain }),
    });
  }

  // ============================================================================
  // TOKEN PROFILES
  // ============================================================================

  async createTokenProfile(
    tokenAddress: string,
    chain: Blockchain,
    profile: Partial<TokenProfile>
  ): Promise<{ success: boolean; profile_id?: string }> {
    return this.fetchAPI('/profiles/create', {
      method: 'POST',
      body: JSON.stringify({
        token_address: tokenAddress,
        chain,
        ...profile,
      }),
    });
  }

  async getTokenProfile(tokenAddress: string, chain: Blockchain): Promise<TokenProfile> {
    return this.fetchAPI(`/profiles/${chain}/${tokenAddress}`);
  }

  async getLatestProfiles(chain?: Blockchain, limit: number = 20): Promise<TokenProfile[]> {
    const chainParam = chain ? `?chain=${chain}&limit=${limit}` : `?limit=${limit}`;
    return this.fetchAPI(`/profiles/latest${chainParam}`);
  }

  async getRecentUpdates(limit: number = 20): Promise<TokenProfile[]> {
    return this.fetchAPI(`/profiles/recent-updates?limit=${limit}`);
  }

  async searchProfiles(query: string, chain?: Blockchain): Promise<TokenProfile[]> {
    const chainParam = chain ? `&chain=${chain}` : '';
    return this.fetchAPI(`/profiles/search?q=${encodeURIComponent(query)}${chainParam}`);
  }

  // ============================================================================
  // WHALE & SMART MONEY TRACKING
  // ============================================================================

  async trackWallet(walletAddress: string, chain: Blockchain): Promise<{ success: boolean }> {
    return this.fetchAPI('/whales/track', {
      method: 'POST',
      body: JSON.stringify({ wallet_address: walletAddress, chain }),
    });
  }

  async untrackWallet(walletAddress: string, chain: Blockchain): Promise<{ success: boolean }> {
    return this.fetchAPI('/whales/untrack', {
      method: 'POST',
      body: JSON.stringify({ wallet_address: walletAddress, chain }),
    });
  }

  async getTrackedWhales(chain: Blockchain): Promise<WhaleActivity[]> {
    return this.fetchAPI(`/whales/tracked/${chain}`);
  }

  async getWhaleActivity(walletAddress: string, chain: Blockchain): Promise<WhaleActivity> {
    return this.fetchAPI(`/whales/activity/${chain}/${walletAddress}`);
  }

  async getTopWhales(chain: Blockchain, limit: number = 20): Promise<WhaleActivity[]> {
    return this.fetchAPI(`/whales/top/${chain}?limit=${limit}`);
  }

  // ============================================================================
  // LIQUIDITY ANALYSIS
  // ============================================================================

  async getLiquidityInfo(tokenAddress: string, chain: Blockchain): Promise<{
    total_liquidity_usd: number;
    liquidity_changes_24h: number;
    pool_count: number;
    largest_pool: PoolInfo;
    liquidity_providers: number;
  }> {
    return this.fetchAPI(`/liquidity/${chain}/${tokenAddress}`);
  }

  async getHolderDistribution(tokenAddress: string, chain: Blockchain): Promise<{
    total_holders: number;
    top_10_holders: Array<{ address: string; percentage: number }>;
    holder_growth_24h: number;
    average_hold_time: number;
  }> {
    return this.fetchAPI(`/holders/${chain}/${tokenAddress}`);
  }

  // ============================================================================
  // COMMUNITY & SOCIAL
  // ============================================================================

  async boostToken(tokenAddress: string, chain: Blockchain, amount: number, message?: string): Promise<{ success: boolean }> {
    return this.fetchAPI('/boosts/create', {
      method: 'POST',
      body: JSON.stringify({ token_address: tokenAddress, chain, amount, message }),
    });
  }

  async getLatestBoosts(chain?: Blockchain, limit: number = 20): Promise<TokenBoost[]> {
    const chainParam = chain ? `?chain=${chain}&limit=${limit}` : `?limit=${limit}`;
    return this.fetchAPI(`/boosts/latest${chainParam}`);
  }

  async getTopBoosts(chain?: Blockchain, limit: number = 20): Promise<TokenBoost[]> {
    const chainParam = chain ? `?chain=${chain}&limit=${limit}` : `?limit=${limit}`;
    return this.fetchAPI(`/boosts/top${chainParam}`);
  }

  async getCommunityTakeovers(chain?: Blockchain, limit: number = 20): Promise<CommunityTakeover[]> {
    const chainParam = chain ? `?chain=${chain}&limit=${limit}` : `?limit=${limit}`;
    return this.fetchAPI(`/community/takeovers${chainParam}`);
  }

  // ============================================================================
  // DISCOVERY & SCREENING
  // ============================================================================

  async discoverNewPairs(chain: Blockchain, filters?: {
    min_liquidity?: number;
    min_volume?: number;
    age_hours?: number;
  }): Promise<PoolInfo[]> {
    const params = new URLSearchParams();
    if (filters?.min_liquidity) params.append('min_liquidity', filters.min_liquidity.toString());
    if (filters?.min_volume) params.append('min_volume', filters.min_volume.toString());
    if (filters?.age_hours) params.append('age_hours', filters.age_hours.toString());
    
    return this.fetchAPI(`/discovery/new/${chain}?${params.toString()}`);
  }

  async getTrendingCategories(chain?: Blockchain): Promise<Array<{
    category: string;
    volume_24h: number;
    pool_count: number;
    avg_price_change: number;
  }>> {
    const chainParam = chain ? `?chain=${chain}` : '';
    return this.fetchAPI(`/metas/trending${chainParam}`);
  }

  async getMovers(chain: Blockchain, period: '1h' | '6h' | '24h' = '24h'): Promise<Array<{
    token_address: string;
    symbol: string;
    price_change_percent: number;
    volume_24h: number;
  }>> {
    return this.fetchAPI(`/discovery/movers/${chain}?period=${period}`);
  }

  // ============================================================================
  // WEBSOCKET STREAMING
  // ============================================================================

  subscribeToNewPools(chain: Blockchain, callback: (pool: PoolInfo) => void): WebSocket {
    const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
    const host = window.location.host;
    const ws = new WebSocket(`${protocol}//${host}${this.baseURL}/ws/pools/new/${chain}`);

    ws.onopen = () => {
      console.log('[Memecoin API] New pools WebSocket connected');
    };

    ws.onmessage = (event) => {
      try {
        const data = JSON.parse(event.data);
        callback(data);
      } catch (error) {
        console.error('[Memecoin API] WebSocket parse error:', error);
      }
    };

    ws.onerror = (error) => {
      console.error('[Memecoin API] WebSocket error:', error);
    };

    ws.onclose = () => {
      console.log('[Memecoin API] WebSocket disconnected');
    };

    return ws;
  }

  subscribeToSecurityAlerts(callback: (alert: { token_address: string; chain: Blockchain; score: SecurityScore }) => void): WebSocket {
    const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
    const host = window.location.host;
    const ws = new WebSocket(`${protocol}//${host}${this.baseURL}/ws/security/alerts`);

    ws.onopen = () => {
      console.log('[Memecoin API] Security alerts WebSocket connected');
    };

    ws.onmessage = (event) => {
      try {
        const data = JSON.parse(event.data);
        callback(data);
      } catch (error) {
        console.error('[Memecoin API] WebSocket parse error:', error);
      }
    };

    ws.onerror = (error) => {
      console.error('[Memecoin API] WebSocket error:', error);
    };

    ws.onclose = () => {
      console.log('[Memecoin API] WebSocket disconnected');
    };

    return ws;
  }
}

// ============================================================================
// SINGLETON INSTANCE
// ============================================================================

let memecoinAPIInstance: MemecoinAPI | null = null;

export function getMemecoinAPI(): MemecoinAPI {
  if (!memecoinAPIInstance) {
    memecoinAPIInstance = new MemecoinAPI();
  }
  return memecoinAPIInstance;
}

// ============================================================================
// UTILITY FUNCTIONS
// ============================================================================

export function formatTokenAddress(address: string): string {
  return `${address.slice(0, 6)}...${address.slice(-4)}`;
}

export function formatUSD(amount: number): string {
  return new Intl.NumberFormat('en-US', {
    style: 'currency',
    currency: 'USD',
    minimumFractionDigits: 2,
    maximumFractionDigits: 2,
  }).format(amount);
}

export function formatPercentage(value: number): string {
  return `${value >= 0 ? '+' : ''}${value.toFixed(2)}%`;
}

export function getChainColor(chain: Blockchain): string {
  const colors = {
    solana: '#14F195',
    ethereum: '#627EEA',
    bsc: '#F3BA2F',
    base: '#0052FF',
    arbitrum: '#28A0F0',
    polygon: '#8247E5',
  };
  return colors[chain];
}

export function getSecurityColor(score: number): string {
  if (score >= 80) return '#22c55e'; // green
  if (score >= 50) return '#eab308'; // yellow
  return '#ef4444'; // red
}