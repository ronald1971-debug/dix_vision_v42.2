/**
 * dashboard2026/src/pages/memecoin/DiscoveryPage.tsx
 * Memecoin Discovery Page
 * 
 * Real-time new pool discovery, hot pool monitoring, and early opportunity detection
 * Inspired by DexScreener's discovery system and Pump.fun's new pair detection
 */

import { useState } from 'react';
import { useQuery, useQueryClient } from '@tanstack/react-query';
import { getMemecoinAPI, type Blockchain, type PoolInfo, formatTokenAddress, formatUSD, formatPercentage, getChainColor } from '@/api/memecoin';

export function DiscoveryPage() {
  const [selectedChain, setSelectedChain] = useState<Blockchain>('solana');
  const [activeTab, setActiveTab] = useState<'new' | 'hot' | 'movers'>('new');
  const [autoRefresh, setAutoRefresh] = useState(true);

  const memecoinAPI = getMemecoinAPI();
  const queryClient = useQueryClient();

  // Fetch new pools
  const { data: newPools, isLoading: newLoading } = useQuery({
    queryKey: ['memecoin', 'pools', 'new', selectedChain],
    queryFn: () => memecoinAPI.getNewPools(selectedChain, 50),
    refetchInterval: autoRefresh ? 5000 : false,
  });

  // Fetch hot pools
  const { data: hotPools, isLoading: hotLoading } = useQuery({
    queryKey: ['memecoin', 'pools', 'hot', selectedChain],
    queryFn: () => memecoinAPI.getHotPools(selectedChain, 50),
    refetchInterval: autoRefresh ? 5000 : false,
  });

  // Fetch movers
  const { data: movers, isLoading: moversLoading } = useQuery({
    queryKey: ['memecoin', 'movers', selectedChain],
    queryFn: () => memecoinAPI.getMovers(selectedChain),
    refetchInterval: autoRefresh ? 10000 : false,
  });

  const currentData = activeTab === 'new' ? newPools : activeTab === 'hot' ? hotPools : null;
  const currentLoading = activeTab === 'new' ? newLoading : activeTab === 'hot' ? hotLoading : activeTab === 'movers' ? moversLoading : false;

  const handleRefresh = () => {
    queryClient.invalidateQueries({ queryKey: ['memecoin'] });
  };

  return (
    <div className="flex h-full flex-col bg-slate-900 text-slate-100">
      {/* Header */}
      <header className="border-b border-slate-700 bg-slate-800 px-6 py-4">
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-2xl font-bold text-white">Memecoin Discovery</h1>
            <p className="text-slate-400 text-sm mt-1">
              Real-time new pool discovery and early opportunity detection
            </p>
          </div>
          <div className="flex items-center gap-4">
            <select
              value={selectedChain}
              onChange={(e) => setSelectedChain(e.target.value as Blockchain)}
              className="bg-slate-700 border border-slate-600 rounded px-3 py-2 text-sm"
            >
              <option value="solana">Solana</option>
              <option value="ethereum">Ethereum</option>
              <option value="bsc">BSC</option>
              <option value="base">Base</option>
              <option value="arbitrum">Arbitrum</option>
              <option value="polygon">Polygon</option>
            </select>
            <button
              onClick={handleRefresh}
              className="px-4 py-2 bg-slate-700 hover:bg-slate-600 rounded text-sm transition-colors"
            >
              Refresh
            </button>
            <label className="flex items-center gap-2 text-sm">
              <input
                type="checkbox"
                checked={autoRefresh}
                onChange={(e) => setAutoRefresh(e.target.checked)}
                className="rounded"
              />
              Auto-refresh
            </label>
          </div>
        </div>
      </header>

      {/* Tabs */}
      <div className="border-b border-slate-700 bg-slate-800/50 px-6">
        <div className="flex gap-1">
          <TabButton
            active={activeTab === 'new'}
            onClick={() => setActiveTab('new')}
            label="New Pools"
            count={newPools?.length}
          />
          <TabButton
            active={activeTab === 'hot'}
            onClick={() => setActiveTab('hot')}
            label="Hot Pools"
            count={hotPools?.length}
          />
          <TabButton
            active={activeTab === 'movers'}
            onClick={() => setActiveTab('movers')}
            label="Movers"
            count={movers?.length}
          />
        </div>
      </div>

      {/* Content */}
      <div className="flex-1 overflow-auto">
        {currentLoading ? (
          <div className="flex items-center justify-center h-full text-slate-500">
            <div className="text-center">
              <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-500 mx-auto mb-4"></div>
              <p>Loading pools...</p>
            </div>
          </div>
        ) : activeTab === 'movers' ? (
          <MoversTable movers={movers || []} chain={selectedChain} />
        ) : (
          <PoolsTable pools={currentData || []} chain={selectedChain} />
        )}
      </div>
    </div>
  );
}

function TabButton({ active, onClick, label, count }: { active: boolean; onClick: () => void; label: string; count?: number }) {
  return (
    <button
      onClick={onClick}
      className={`px-4 py-3 text-sm font-medium transition-colors ${
        active
          ? 'bg-slate-700 text-white border-b-2 border-blue-500'
          : 'text-slate-400 hover:text-white hover:bg-slate-700/50'
      }`}
    >
      {label}
      {count !== undefined && (
        <span className="ml-2 px-2 py-0.5 bg-slate-600 rounded-full text-xs">
          {count}
        </span>
      )}
    </button>
  );
}

function PoolsTable({ pools, chain }: { pools: PoolInfo[]; chain: Blockchain }) {
  const chainColor = getChainColor(chain);

  return (
    <div className="p-6">
      <div className="overflow-x-auto">
        <table className="w-full">
          <thead>
            <tr className="border-b border-slate-700">
              <th className="text-left py-3 px-4 text-sm font-medium text-slate-400">Token</th>
              <th className="text-right py-3 px-4 text-sm font-medium text-slate-400">Price</th>
              <th className="text-right py-3 px-4 text-sm font-medium text-slate-400">24h Change</th>
              <th className="text-right py-3 px-4 text-sm font-medium text-slate-400">Liquidity</th>
              <th className="text-right py-3 px-4 text-sm font-medium text-slate-400">Volume (24h)</th>
              <th className="text-right py-3 px-4 text-sm font-medium text-slate-400">Transactions</th>
              <th className="text-left py-3 px-4 text-sm font-medium text-slate-400">Age</th>
            </tr>
          </thead>
          <tbody>
            {pools.map((pool, index) => (
              <PoolRow key={index} pool={pool} chain={chain} chainColor={chainColor} />
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}

function PoolRow({ pool, chain, chainColor }: { pool: PoolInfo; chain: Blockchain; chainColor: string }) {
  const age = getPoolAge(pool.created_at);
  const buySellRatio = pool.transactions_24h.buys / (pool.transactions_24h.sells || 1);

  return (
    <tr className="border-b border-slate-800 hover:bg-slate-800/50 transition-colors">
      <td className="py-3 px-4">
        <div className="flex items-center gap-3">
          <div className="w-8 h-8 rounded-full bg-gradient-to-br from-blue-500 to-purple-500 flex items-center justify-center text-white text-xs font-bold">
            {pool.token_address.slice(0, 2)}
          </div>
          <div>
            <div className="font-medium text-white flex items-center gap-2">
              {formatTokenAddress(pool.token_address)}
              <span 
                className="text-xs px-2 py-0.5 rounded"
                style={{ backgroundColor: chainColor + '20', color: chainColor }}
              >
                {chain}
              </span>
            </div>
            <div className="text-xs text-slate-500">{pool.dex}</div>
          </div>
        </div>
      </td>
      <td className="text-right py-3 px-4 font-mono text-sm">
        {pool.price_usd < 0.01 ? `<$0.01` : formatUSD(pool.price_usd)}
      </td>
      <td className="text-right py-3 px-4">
        <span className={`font-mono text-sm ${pool.price_change_24h >= 0 ? 'text-green-400' : 'text-red-400'}`}>
          {formatPercentage(pool.price_change_24h)}
        </span>
      </td>
      <td className="text-right py-3 px-4 font-mono text-sm text-slate-300">
        {formatUSD(pool.liquidity_usd)}
      </td>
      <td className="text-right py-3 px-4 font-mono text-sm text-slate-300">
        {formatUSD(pool.volume_24h_usd)}
      </td>
      <td className="text-right py-3 px-4">
        <div className="flex items-center justify-end gap-2 text-xs">
          <span className="text-green-400">{pool.transactions_24h.buys} buys</span>
          <span className="text-red-400">{pool.transactions_24h.sells} sells</span>
        </div>
      </td>
      <td className="py-3 px-4 text-sm text-slate-400">
        {age}
      </td>
    </tr>
  );
}

function MoversTable({ movers, chain }: { movers: any[]; chain: Blockchain }) {
  const chainColor = getChainColor(chain);

  return (
    <div className="p-6">
      <div className="overflow-x-auto">
        <table className="w-full">
          <thead>
            <tr className="border-b border-slate-700">
              <th className="text-left py-3 px-4 text-sm font-medium text-slate-400">Token</th>
              <th className="text-right py-3 px-4 text-sm font-medium text-slate-400">Price Change</th>
              <th className="text-right py-3 px-4 text-sm font-medium text-slate-400">Volume (24h)</th>
            </tr>
          </thead>
          <tbody>
            {movers.map((mover, index) => (
              <tr key={index} className="border-b border-slate-800 hover:bg-slate-800/50 transition-colors">
                <td className="py-3 px-4">
                  <div className="flex items-center gap-3">
                    <div className="w-8 h-8 rounded-full bg-gradient-to-br from-green-500 to-emerald-500 flex items-center justify-center text-white text-xs font-bold">
                      #{index + 1}
                    </div>
                    <div>
                      <div className="font-medium text-white flex items-center gap-2">
                        {formatTokenAddress(mover.token_address)}
                        <span 
                          className="text-xs px-2 py-0.5 rounded"
                          style={{ backgroundColor: chainColor + '20', color: chainColor }}
                        >
                          {chain}
                        </span>
                      </div>
                      <div className="text-xs text-slate-500">{mover.symbol}</div>
                    </div>
                  </div>
                </td>
                <td className="text-right py-3 px-4">
                  <span className={`font-mono text-sm ${mover.price_change_percent >= 0 ? 'text-green-400' : 'text-red-400'}`}>
                    {formatPercentage(mover.price_change_percent)}
                  </span>
                </td>
                <td className="text-right py-3 px-4 font-mono text-sm text-slate-300">
                  {formatUSD(mover.volume_24h)}
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}

function getPoolAge(createdAt: string): string {
  const created = new Date(createdAt);
  const now = new Date();
  const diffMs = now.getTime() - created.getTime();
  const diffMins = Math.floor(diffMs / 60000);
  const diffHours = Math.floor(diffMs / 3600000);
  const diffDays = Math.floor(diffMs / 86400000);

  if (diffMins < 1) return '< 1 min';
  if (diffMins < 60) return `${diffMins} min`;
  if (diffHours < 24) return `${diffHours}h`;
  return `${diffDays}d`;
}