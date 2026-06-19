/**
 * dashboard2026/src/pages/memecoin/WhaleTrackingPage.tsx
 * Memecoin Whale Tracking & Smart Money Dashboard
 * 
 * Smart money tracking, copy trading, and whale activity monitoring
 * Inspired by GMGN.AI's smart money tracking and copy trading features
 */

import { useState } from 'react';
import { useQuery } from '@tanstack/react-query';
import { getMemecoinAPI, type Blockchain, type WhaleActivity, formatUSD, formatPercentage } from '@/api/memecoin';

export function WhaleTrackingPage() {
  const [selectedChain, setSelectedChain] = useState<Blockchain>('solana');
  const [walletAddress, setWalletAddress] = useState('');

  return (
    <div className="flex h-full flex-col bg-slate-900 text-slate-100">
      {/* Header */}
      <header className="border-b border-slate-700 bg-gradient-to-r from-slate-800 via-slate-800 to-slate-900 px-6 py-4">
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-2xl font-bold text-white flex items-center gap-2">
              <span className="bg-gradient-to-r from-green-500 to-blue-500 bg-clip-text text-transparent">
                Smart Money Tracking
              </span>
              <span className="text-xs px-2 py-1 bg-green-500/20 text-green-300 rounded-full border border-green-500/30">
                AI-Enhanced
              </span>
            </h1>
            <p className="text-slate-400 text-sm mt-1">
              Whale activity monitoring and copy trading dashboard
            </p>
          </div>
          <div className="flex items-center gap-4">
            <div className="flex items-center gap-2 px-3 py-2 bg-slate-700/50 rounded-lg border border-slate-600">
              <div className="w-2 h-2 bg-green-500 rounded-full animate-pulse"></div>
              <span className="text-xs text-slate-300">Live Tracking</span>
            </div>
            <select
              value={selectedChain}
              onChange={(e) => setSelectedChain(e.target.value as Blockchain)}
              className="bg-slate-700 border border-slate-600 rounded-lg px-3 py-2 text-sm focus:ring-2 focus:ring-green-500 focus:border-transparent transition-all"
            >
              <option value="solana">Solana</option>
              <option value="ethereum">Ethereum</option>
              <option value="bsc">BSC</option>
              <option value="base">Base</option>
            </select>
          </div>
        </div>
      </header>

      {/* Content */}
      <div className="flex-1 overflow-auto p-6">
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          {/* Wallet Tracking */}
          <WalletTracking walletAddress={walletAddress} setWalletAddress={setWalletAddress} selectedChain={selectedChain} />

          {/* Top Whales */}
          <TopWhales selectedChain={selectedChain} />

          {/* Copy Trading */}
          <CopyTrading selectedChain={selectedChain} />
        </div>
      </div>
    </div>
  );
}

function WalletTracking({ walletAddress, setWalletAddress, selectedChain: _selectedChain }: { walletAddress: string; setWalletAddress: (val: string) => void; selectedChain: Blockchain }) {
  const [tracking, setTracking] = useState(false);

  return (
    <div className="bg-slate-800 rounded-lg p-6 border border-slate-700">
      <h2 className="text-xl font-bold text-white mb-4">🐋 Wallet Tracking</h2>

      <div className="space-y-4">
        <div>
          <label className="block text-sm font-medium text-slate-300 mb-2">
            Wallet Address
          </label>
          <input
            type="text"
            value={walletAddress}
            onChange={(e) => setWalletAddress(e.target.value)}
            placeholder="Enter wallet address..."
            className="w-full bg-slate-700 border border-slate-600 rounded px-4 py-2 text-sm placeholder-slate-500"
          />
        </div>

        <div className="p-4 bg-slate-700/50 rounded-lg">
          <div className="flex items-center justify-between">
            <span className="text-sm text-slate-300">Track this wallet</span>
            <button
              onClick={() => setTracking(!tracking)}
              className={`px-4 py-2 rounded text-sm font-medium transition-colors ${tracking ? 'bg-green-500 text-white' : 'bg-slate-600 text-slate-300'}`}
            >
              {tracking ? 'Tracking' : 'Track'}
            </button>
          </div>
        </div>

        {walletAddress && (
          <div className="text-xs text-slate-400">
            <div className="mb-2">Monitoring:</div>
            <div className="space-y-1">
              <div className="flex items-center gap-2">
                <span className="text-green-400">✓</span>
                <span>Buy/Sell transactions</span>
              </div>
              <div className="flex items-center gap-2">
                <span className="text-green-400">✓</span>
                <span>Large transfers</span>
              </div>
              <div className="flex items-center gap-2">
                <span className="text-green-400">✓</span>
                <span>Token swaps</span>
              </div>
              <div className="flex items-center gap-2">
                <span className="text-green-400">✓</span>
                <span>Liquidity provision</span>
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}

function TopWhales({ selectedChain: _selectedChain }: { selectedChain: Blockchain }) {
  const { data: topWhales, isLoading } = useQuery({
    queryKey: ['memecoin', 'whales', 'top', _selectedChain],
    queryFn: () => getMemecoinAPI().getTopWhales(_selectedChain, 20),
    refetchInterval: 10000,
  });

  if (isLoading) {
    return (
      <div className="bg-slate-800 rounded-lg p-6 border border-slate-700">
        <h2 className="text-xl font-bold text-white mb-4">🏆 Top Whales</h2>
        <div className="text-center text-slate-500">Loading...</div>
      </div>
    );
  }

  return (
    <div className="bg-slate-800 rounded-lg p-6 border border-slate-700">
      <h2 className="text-xl font-bold text-white mb-4">🏆 Top Whales</h2>

      <div className="space-y-3">
        {topWhales?.slice(0, 10).map((whale, index) => (
          <WhaleCard key={index} whale={whale} rank={index + 1} />
        ))}
      </div>
    </div>
  );
}

function WhaleCard({ whale, rank }: { whale: WhaleActivity; rank: number }) {
  return (
    <div className="p-3 bg-slate-700/50 rounded-lg border border-slate-600 hover:border-slate-500 transition-colors">
      <div className="flex items-center gap-3">
        <div className="w-8 h-8 bg-gradient-to-br from-yellow-500 to-orange-500 rounded-full flex items-center justify-center text-white font-bold text-sm">
          {rank}
        </div>
        <div className="flex-1">
          <div className="font-mono text-xs text-white mb-1">
            {whale.wallet_address.slice(0, 6)}...{whale.wallet_address.slice(-4)}
          </div>
          <div className="flex items-center gap-2 text-xs">
            <span className="text-green-400">{formatPercentage(whale.win_rate)} win rate</span>
            <span className="text-blue-400">{formatUSD(whale.profit_score)} score</span>
          </div>
        </div>
      </div>
    </div>
  );
}

function CopyTrading({ selectedChain: _selectedChain }: { selectedChain: Blockchain }) {
  const [copyEnabled, setCopyEnabled] = useState(false);
  const [copyPercentage, setCopyPercentage] = useState(10);
  const [maxPositionSize, setMaxPositionSize] = useState(1000);
  const [selectedTraders, setSelectedTraders] = useState<string[]>([]);
  const [minProfitPercent, setMinProfitPercent] = useState(15);
  const [maxTradesPerDay, setMaxTradesPerDay] = useState(10);
  const [riskLevel, setRiskLevel] = useState<'low' | 'medium' | 'high'>('medium');
  const [enableAutoStopLoss, setEnableAutoStopLoss] = useState(true);
  const [stopLossPercent, setStopLossPercent] = useState(10);
  
  // Mock top performers data
  const topPerformers = [
    { address: '7xKXtg2CW87d97TXJSDpbD5jBkheTqA83TZRuJosgAsU', profit: 2500, winRate: 85, trades: 45 },
    { address: '9WzDXwBbmkg8ZTbNMqbU9hD8FjYzGNQwGt8iEh9sXp9s', profit: 1800, winRate: 78, trades: 38 },
    { address: '5Hd3x9qYf4zQcPbR9jQXeKqZcRx4h8z6NfGhTm5gD7wQ', profit: 1500, winRate: 72, trades: 52 },
    { address: '3kNTRpQcLxM8qYhXkQZkQpQqZcRx4h8z6NfGhTm5gD7wQ', profit: 1200, winRate: 68, trades: 29 },
  ];

  const toggleTraderSelection = (address: string) => {
    setSelectedTraders(prev =>
      prev.includes(address)
        ? prev.filter(a => a !== address)
        : [...prev, address]
    );
  };

  return (
    <div className="bg-gradient-to-br from-slate-800 to-slate-900 rounded-xl p-6 border border-slate-700 shadow-xl">
      <h2 className="text-xl font-bold text-white mb-4 flex items-center gap-2">
        <span className="bg-gradient-to-r from-blue-500 to-purple-500 bg-clip-text text-transparent">
          🔄 Copy Trading
        </span>
        <span className="text-xs px-2 py-1 bg-blue-500/20 text-blue-300 rounded-full border border-blue-500/30">
          Smart AI
        </span>
      </h2>

      <div className="space-y-6">
        {/* Enable Copy Trading */}
        <div className="p-4 bg-slate-700/50 rounded-lg">
          <div className="flex items-center justify-between mb-4">
            <div>
              <h3 className="font-semibold text-white">Enable Copy Trading</h3>
              <p className="text-xs text-slate-400 mt-1">Copy trades from top performers</p>
            </div>
            <button
              onClick={() => setCopyEnabled(!copyEnabled)}
              className={`px-4 py-2 rounded text-sm font-medium transition-colors ${copyEnabled ? 'bg-green-500 text-white' : 'bg-slate-600 text-slate-300'}`}
            >
              {copyEnabled ? 'Enabled' : 'Enable'}
            </button>
          </div>
          
          {copyEnabled && (
            <div className="mt-4 p-3 bg-green-500/10 border border-green-500/20 rounded">
              <div className="flex items-center gap-2 text-green-400 text-sm">
                <div className="w-2 h-2 bg-green-500 rounded-full animate-pulse"></div>
                <span className="font-medium">Copy Trading Active</span>
              </div>
              <p className="text-xs text-green-300 mt-1">
                Copying {selectedTraders.length} trader(s) • Last sync: Just now
              </p>
            </div>
          )}
        </div>

        {/* Top Performers Leaderboard */}
        <div className="p-4 bg-slate-700/50 rounded-lg">
          <h3 className="font-semibold text-white mb-3">🏆 Top Performers</h3>
          <div className="space-y-2">
            {topPerformers.map((performer, index) => (
              <div
                key={performer.address}
                className={`p-3 rounded border cursor-pointer transition-colors ${
                  selectedTraders.includes(performer.address)
                    ? 'bg-purple-500/20 border-purple-500/40'
                    : 'bg-slate-600/30 border-slate-600 hover:bg-slate-600/50'
                }`}
                onClick={() => toggleTraderSelection(performer.address)}
              >
                <div className="flex items-center justify-between">
                  <div className="flex items-center gap-3">
                    <div className={`w-6 h-6 rounded-full flex items-center justify-center text-xs font-bold ${
                      index === 0 ? 'bg-yellow-500 text-white' :
                      index === 1 ? 'bg-slate-400 text-white' :
                      index === 2 ? 'bg-orange-500 text-white' :
                      'bg-slate-600 text-slate-300'
                    }`}>
                      {index + 1}
                    </div>
                    <div>
                      <div className="text-sm font-medium text-white">
                        {performer.address.slice(0, 6)}...{performer.address.slice(-4)}
                      </div>
                      <div className="text-xs text-slate-400">
                        {performer.trades} trades
                      </div>
                    </div>
                  </div>
                  <div className="text-right">
                    <div className="text-sm font-bold text-green-400">
                      +${performer.profit.toLocaleString()}
                    </div>
                    <div className="text-xs text-purple-400">
                      {performer.winRate}% win rate
                    </div>
                  </div>
                </div>
                {selectedTraders.includes(performer.address) && (
                  <div className="mt-2 pt-2 border-t border-purple-500/20">
                    <div className="text-xs text-purple-300">✓ Selected for copying</div>
                  </div>
                )}
              </div>
            ))}
          </div>
        </div>

        {/* Copy Trading Settings */}
        <div className="p-4 bg-slate-700/50 rounded-lg">
          <h3 className="font-semibold text-white mb-4">⚙️ Copy Trading Settings</h3>
          
          <div className="space-y-4">
            {/* Copy Trade Size */}
            <div>
              <label className="block text-sm font-medium text-slate-300 mb-2">
                Copy Trade Size (% of wallet)
              </label>
              <div className="flex items-center gap-4">
                <input
                  type="range"
                  min="1"
                  max="50"
                  value={copyPercentage}
                  onChange={(e) => setCopyPercentage(parseInt(e.target.value))}
                  className="flex-1"
                  disabled={!copyEnabled}
                />
                <span className="text-sm font-mono text-white w-12">{copyPercentage}%</span>
              </div>
            </div>

            {/* Max Position Size */}
            <div>
              <label className="block text-sm font-medium text-slate-300 mb-2">
                Max Position Size (USD)
              </label>
              <input
                type="number"
                min="100"
                step="100"
                value={maxPositionSize}
                onChange={(e) => setMaxPositionSize(parseInt(e.target.value))}
                className="w-full bg-slate-600 border border-slate-500 rounded px-4 py-2 text-sm text-white"
                disabled={!copyEnabled}
              />
            </div>

            {/* Minimum Profit Percentage */}
            <div>
              <label className="block text-sm font-medium text-slate-300 mb-2">
                Min Profit Threshold (%)
              </label>
              <div className="flex items-center gap-4">
                <input
                  type="range"
                  min="5"
                  max="50"
                  value={minProfitPercent}
                  onChange={(e) => setMinProfitPercent(parseInt(e.target.value))}
                  className="flex-1"
                  disabled={!copyEnabled}
                />
                <span className="text-sm font-mono text-white w-12">{minProfitPercent}%</span>
              </div>
            </div>

            {/* Max Trades Per Day */}
            <div>
              <label className="block text-sm font-medium text-slate-300 mb-2">
                Max Trades Per Day
              </label>
              <input
                type="number"
                min="1"
                max="50"
                value={maxTradesPerDay}
                onChange={(e) => setMaxTradesPerDay(parseInt(e.target.value))}
                className="w-full bg-slate-600 border border-slate-500 rounded px-4 py-2 text-sm text-white"
                disabled={!copyEnabled}
              />
            </div>

            {/* Risk Level */}
            <div>
              <label className="block text-sm font-medium text-slate-300 mb-2">
                Risk Level
              </label>
              <div className="flex gap-2">
                {(['low', 'medium', 'high'] as const).map((level) => (
                  <button
                    key={level}
                    onClick={() => setRiskLevel(level)}
                    disabled={!copyEnabled}
                    className={`flex-1 py-2 px-3 rounded text-sm font-medium transition-colors ${
                      riskLevel === level
                        ? level === 'low' ? 'bg-green-500 text-white' :
                          level === 'medium' ? 'bg-yellow-500 text-white' :
                          'bg-red-500 text-white'
                        : 'bg-slate-600 text-slate-300 hover:bg-slate-500'
                    }`}
                  >
                    {level.charAt(0).toUpperCase() + level.slice(1)}
                  </button>
                ))}
              </div>
            </div>

            {/* Auto Stop Loss */}
            <div className="flex items-center justify-between p-3 bg-slate-600/30 rounded">
              <div>
                <div className="text-sm font-medium text-white">Auto Stop-Loss</div>
                <div className="text-xs text-slate-400">Automatic position exit when losing</div>
              </div>
              <button
                onClick={() => setEnableAutoStopLoss(!enableAutoStopLoss)}
                disabled={!copyEnabled}
                className={`px-3 py-1 rounded text-sm font-medium transition-colors ${
                  enableAutoStopLoss ? 'bg-green-500 text-white' : 'bg-slate-500 text-slate-300'
                }`}
              >
                {enableAutoStopLoss ? 'ON' : 'OFF'}
              </button>
            </div>

            {/* Stop Loss Percentage */}
            {enableAutoStopLoss && (
              <div>
                <label className="block text-sm font-medium text-slate-300 mb-2">
                  Stop-Loss Percentage (%)
                </label>
                <div className="flex items-center gap-4">
                  <input
                    type="range"
                    min="5"
                    max="30"
                    value={stopLossPercent}
                    onChange={(e) => setStopLossPercent(parseInt(e.target.value))}
                    className="flex-1"
                    disabled={!copyEnabled}
                  />
                  <span className="text-sm font-mono text-white w-12">{stopLossPercent}%</span>
                </div>
              </div>
            )}
          </div>
        </div>

        {/* Copy Trading Summary */}
        <div className="p-4 bg-gradient-to-r from-purple-900/30 to-blue-900/30 border border-purple-500/30 rounded-lg">
          <h3 className="font-semibold text-white mb-3">📊 Copy Trading Summary</h3>
          <div className="grid grid-cols-2 gap-3 text-sm">
            <div className="p-3 bg-slate-800/50 rounded">
              <div className="text-slate-400 text-xs">Selected Traders</div>
              <div className="text-white font-bold">{selectedTraders.length}</div>
            </div>
            <div className="p-3 bg-slate-800/50 rounded">
              <div className="text-slate-400 text-xs">Risk Level</div>
              <div className="text-white font-bold capitalize">{riskLevel}</div>
            </div>
            <div className="p-3 bg-slate-800/50 rounded">
              <div className="text-slate-400 text-xs">Position Size</div>
              <div className="text-white font-bold">{copyPercentage}%</div>
            </div>
            <div className="p-3 bg-slate-800/50 rounded">
              <div className="text-slate-400 text-xs">Daily Limit</div>
              <div className="text-white font-bold">{maxTradesPerDay} trades</div>
            </div>
          </div>
        </div>

        {/* Start/Stop Button */}
        <button
          className="w-full py-3 rounded-lg font-medium transition-colors ${
            copyEnabled && selectedTraders.length > 0
              ? 'bg-gradient-to-r from-green-500 to-emerald-600 text-white hover:from-green-600 hover:to-emerald-700'
              : 'bg-slate-600 text-slate-400 cursor-not-allowed'
          }`}
          disabled={!copyEnabled || selectedTraders.length === 0}
        >
          {copyEnabled && selectedTraders.length > 0
            ? 'Start Copy Trading'
            : selectedTraders.length === 0
            ? 'Select Traders to Copy'
            : 'Enable Copy Trading First'}
        </button>
      </div>
    </div>
  );
}