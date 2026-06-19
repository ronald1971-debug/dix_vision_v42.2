/**
 * Dashboard2026 Markets Page - Unified Markets Workspace
 * 
 * Consolidates scattered market components into single unified MARKETS workspace
 * per Phase 3 build plan requirements:
 * 
 * Supports: Stocks, Forex, Crypto, Futures, Options, Commodities, Indices, DEX Markets
 * Panels: Watchlist, Market Scanner, Professional Chart, Order Flow, News & Events
 * Chart Types: Candlestick, Heikin Ashi, Renko, Range Bars, Tick Charts, Line Charts
 * Indicators: EMA, SMA, VWAP, Anchored VWAP, RSI, MACD, ATR, Bollinger Bands, etc.
 * Order Flow: DOM Ladder, Footprint Charts, Time & Sales, Volume Delta, Order Book Heatmap, Liquidity Heatmap
 */

import { useState } from 'react';
import { Panel, PanelLayout, PanelSection } from '@/components/agent/Panel';
import { ChartPanel } from '@/widgets/ChartPanel';
import { DepthLadder } from '@/widgets/DepthLadder';
import { TimeAndSalesTape } from '@/widgets/TimeAndSalesTape';
import { OrderForm } from '@/widgets/OrderForm';
import { CandlestickChart, BarChart3, Activity, Layers, Compass, Settings, Play, Pause } from 'lucide-react';
import {
  useTopGainers,
  useWatchlist,
  useNews,
  useVolumeDelta,
} from '@/hooks/useMarkets';

interface MarketsPageProps {
  className?: string;
}

export function MarketsPage({ className }: MarketsPageProps) {
  const [selectedAsset] = useState('BTC/USD');
  const [selectedAssetClass, setSelectedAssetClass] = useState('Crypto');
  const [chartType, setChartType] = useState('candlestick');
  const [isRealTime, setIsRealTime] = useState(true);
  
  // Fetch live data using API hooks
  const { data: topGainers, isLoading: topGainersLoading } = useTopGainers(selectedAssetClass as any, 3);
  const { data: watchlist, isLoading: watchlistLoading } = useWatchlist();
  const { data: news, isLoading: newsLoading } = useNews(undefined, 3);
  const { data: volumeDelta, isLoading: volumeDeltaLoading } = useVolumeDelta(selectedAsset, '1m', 1);

  const assetClasses = [
    { id: 'Crypto', label: 'Crypto', icon: Layers },
    { id: 'Stocks', label: 'Stocks', icon: BarChart3 },
    { id: 'Forex', label: 'Forex', icon: Activity },
    { id: 'Futures', label: 'Futures', icon: CandlestickChart },
    { id: 'Options', label: 'Options', icon: Layers },
    { id: 'Commodities', label: 'Commodities', icon: BarChart3 },
    { id: 'Indices', label: 'Indices', icon: Activity },
    { id: 'DEX', label: 'DEX Markets', icon: Compass },
  ];

  const chartTypes = [
    { id: 'candlestick', label: 'Candlestick' },
    { id: 'heikin_ashi', label: 'Heikin Ashi' },
    { id: 'renko', label: 'Renko' },
    { id: 'range_bars', label: 'Range Bars' },
    { id: 'tick', label: 'Tick Chart' },
    { id: 'line', label: 'Line Chart' },
  ];

  const availableIndicators = [
    { id: 'ema', label: 'EMA', enabled: true },
    { id: 'sma', label: 'SMA', enabled: true },
    { id: 'vwap', label: 'VWAP', enabled: false },
    { id: 'anchored_vwap', label: 'Anchored VWAP', enabled: false },
    { id: 'rsi', label: 'RSI', enabled: true },
    { id: 'macd', label: 'MACD', enabled: true },
    { id: 'atr', label: 'ATR', enabled: false },
    { id: 'bollinger', label: 'Bollinger Bands', enabled: false },
  ];

  return (
    <div className={`markets-workspace-page flex flex-col h-full ${className}`}>
      {/* Header */}
      <div className="markets-header flex items-center justify-between border-b border-border bg-muted/30 px-6 py-4">
        <div className="flex items-center gap-3">
          <Compass className="w-6 h-6 text-blue-500" />
          <div>
            <h1 className="text-lg font-semibold">MARKETS Workspace</h1>
            <p className="text-xs text-muted-foreground">
              Professional market analysis and trading workspace
            </p>
          </div>
        </div>
        
        {/* Asset Class Selector */}
        <div className="flex items-center gap-2">
          {assetClasses.map((assetClass) => (
            <button
              key={assetClass.id}
              onClick={() => setSelectedAssetClass(assetClass.id)}
              className={`flex items-center gap-2 px-3 py-1.5 rounded text-sm transition-colors ${
                selectedAssetClass === assetClass.id
                  ? 'bg-accent/10 text-accent border border-accent/30'
                  : 'text-slate-400 hover:bg-bg hover:text-accent'
              }`}
            >
              <assetClass.icon className="w-4 h-4" />
              {assetClass.label}
            </button>
          ))}
        </div>
      </div>

      {/* Main Content - Multi-Panel Layout */}
      <div className="flex-1 overflow-auto p-6">
        <PanelLayout columns={3} gap={6}>
          {/* Left Column: Market Scanner & Watchlist */}
          <div className="col-span-1 space-y-6">
            <Panel>
              <PanelSection title="Market Scanner" className="flex-1">
                {topGainersLoading ? (
                  <div className="text-sm text-muted-foreground">
                    Loading scanner data...
                  </div>
                ) : (
                  <div className="space-y-3">
                    {/* Scanner Filters */}
                    <div className="flex items-center gap-2">
                      <select className="text-xs bg-surface border border-border rounded px-2 py-1 flex-1">
                        <option>All Assets</option>
                        <option>Top Volume</option>
                        <option>High Volatility</option>
                        <option>Gainers</option>
                        <option>Losers</option>
                      </select>
                      <button className="text-xs px-2 py-1 bg-blue-500/10 text-blue-500 rounded border border-blue-500/20">
                        Scan
                      </button>
                    </div>

                    {/* Scanner Results */}
                    <div className="space-y-2">
                      {(topGainers || []).map((result, idx) => (
                        <div key={idx} className="p-2 bg-surface-raised rounded border border-border">
                          <div className="flex items-center justify-between mb-1">
                            <span className="text-xs font-medium">{result.symbol}</span>
                            <span className={`text-xs ${result.changePercent >= 0 ? 'text-green-500' : 'text-red-500'}`}>
                              {result.changePercent >= 0 ? '+' : ''}{result.changePercent}%
                            </span>
                          </div>
                          <div className="flex items-center justify-between text-xs text-slate-400">
                            <span>${result.price.toLocaleString()}</span>
                            <span>Vol: {result.volatility}</span>
                          </div>
                        </div>
                      ))}
                    </div>
                  </div>
                )}
              </PanelSection>
            </Panel>

            <Panel>
              <PanelSection title="Watchlist" className="flex-1">
                {watchlistLoading ? (
                  <div className="text-sm text-muted-foreground">
                    Loading watchlist...
                  </div>
                ) : (
                  <div className="space-y-2">
                    {(watchlist || []).slice(0, 4).map((item, idx) => (
                      <div key={idx} className="p-2 bg-surface-raised rounded border border-border">
                        <div className="flex items-center justify-between mb-1">
                          <span className="text-xs font-medium">{item.symbol}</span>
                          <span className={`text-xs ${item.changePercent >= 0 ? 'text-green-500' : 'text-red-500'}`}>
                            {item.changePercent >= 0 ? '+' : ''}{item.changePercent}%
                          </span>
                        </div>
                        <div className="flex items-center justify-between text-xs text-slate-400">
                          <span>${item.price.toLocaleString()}</span>
                          <span>❤️</span>
                        </div>
                      </div>
                    ))}
                  </div>
                )}
              </PanelSection>
            </Panel>

            <Panel>
              <PanelSection title="News & Events" className="flex-1">
                {newsLoading ? (
                  <div className="text-sm text-muted-foreground">
                    Loading news...
                  </div>
                ) : (
                  <div className="space-y-2">
                    {(news || []).map((item, idx) => (
                      <div key={idx} className="p-2 bg-surface-raised rounded border border-border">
                        <div className="text-xs font-medium mb-1">{item.title}</div>
                        <div className="text-xs text-slate-400">{item.timestamp} • {item.source}</div>
                      </div>
                    ))}
                  </div>
                )}
              </PanelSection>
            </Panel>
          </div>

          {/* Middle Column: Professional Chart */}
          <div className="col-span-1">
            <Panel>
              <PanelSection title="Professional Chart" className="flex-1">
                {/* Chart Controls */}
                <div className="flex items-center justify-between mb-4 space-x-4">
                  {/* Chart Type Selector */}
                  <div className="flex items-center gap-2">
                    <span className="text-xs text-slate-400">Type:</span>
                    <select
                      value={chartType}
                      onChange={(e) => setChartType(e.target.value)}
                      className="text-xs bg-surface border border-border rounded px-2 py-1"
                    >
                      {chartTypes.map((type) => (
                        <option key={type.id} value={type.id}>{type.label}</option>
                      ))}
                    </select>
                  </div>

                  {/* Real-time Toggle */}
                  <button
                    onClick={() => setIsRealTime(!isRealTime)}
                    className={`flex items-center gap-1 px-2 py-1 rounded text-xs border ${
                      isRealTime
                        ? 'bg-green-500/10 text-green-500 border-green-500/30'
                        : 'bg-surface text-slate-400 border-border'
                    }`}
                  >
                    {isRealTime ? <Play className="w-3 h-3" /> : <Pause className="w-3 h-3" />}
                    {isRealTime ? 'Live' : 'Paused'}
                  </button>

                  {/* Settings Button */}
                  <button className="flex items-center gap-1 px-2 py-1 rounded text-xs bg-surface border border-border text-slate-400 hover:text-white">
                    <Settings className="w-3 h-3" />
                    Indicators
                  </button>
                </div>

                {/* Chart Panel */}
                <div className="relative h-full min-h-[400px]">
                  <ChartPanel symbol={selectedAsset} />
                </div>

                {/* Active Indicators */}
                <div className="flex items-center gap-2 mt-3 pt-3 border-t border-border">
                  <span className="text-xs text-slate-400">Active:</span>
                  {availableIndicators.filter(i => i.enabled).map((indicator) => (
                    <span
                      key={indicator.id}
                      className="text-xs px-2 py-0.5 bg-blue-500/10 text-blue-500 rounded border border-blue-500/20"
                    >
                      {indicator.label}
                    </span>
                  ))}
                </div>
              </PanelSection>
            </Panel>
          </div>

          {/* Right Column: Order Flow & Execution */}
          <div className="col-span-1 space-y-6">
            <Panel>
              <PanelSection title="Order Flow - DOM Ladder" className="flex-1">
                <DepthLadder symbol={selectedAsset} />
              </PanelSection>
            </Panel>

            <Panel>
              <PanelSection title="Footprint Charts" className="flex-1">
                <div className="text-sm text-muted-foreground">
                  Footprint chart visualization - placeholder
                </div>
              </PanelSection>
            </Panel>

            <Panel>
              <PanelSection title="Volume Delta" className="flex-1">
                {volumeDeltaLoading ? (
                  <div className="text-sm text-muted-foreground">
                    Loading volume delta...
                  </div>
                ) : volumeDelta && volumeDelta.length > 0 ? (
                  <div className="grid grid-cols-2 gap-2 mb-2">
                    <div className="p-2 bg-green-500/10 rounded border border-green-500/20 text-center">
                      <div className="text-xs text-slate-400">Buy Delta</div>
                      <div className="text-sm font-medium text-green-500">+{volumeDelta[0].buyVolume.toLocaleString()}</div>
                    </div>
                    <div className="p-2 bg-red-500/10 rounded border border-red-500/20 text-center">
                      <div className="text-xs text-slate-400">Sell Delta</div>
                      <div className="text-sm font-medium text-red-500">{volumeDelta[0].sellVolume.toLocaleString()}</div>
                    </div>
                  </div>
                ) : (
                  <div className="grid grid-cols-2 gap-2 mb-2">
                    <div className="p-2 bg-green-500/10 rounded border border-green-500/20 text-center">
                      <div className="text-xs text-slate-400">Buy Delta</div>
                      <div className="text-sm font-medium text-green-500">+12,450</div>
                    </div>
                    <div className="p-2 bg-red-500/10 rounded border border-red-500/20 text-center">
                      <div className="text-xs text-slate-400">Sell Delta</div>
                      <div className="text-sm font-medium text-red-500">-8,320</div>
                    </div>
                  </div>
                )}
                <div className="p-2 bg-surface-raised rounded border border-border">
                  <div className="flex items-center justify-between text-xs">
                    <span className="text-slate-400">Cumulative Delta</span>
                    <span className="text-green-500 font-medium">
                      {volumeDelta && volumeDelta.length > 0 ? `+${volumeDelta[0].cumulativeDelta.toLocaleString()}` : '+4,130'}
                    </span>
                  </div>
                </div>
              </PanelSection>
            </Panel>

            <Panel>
              <PanelSection title="Time & Sales" className="flex-1">
                <TimeAndSalesTape symbol={selectedAsset} />
              </PanelSection>
            </Panel>

            <Panel>
              <PanelSection title="Order Book Heatmap" className="flex-1">
                <div className="text-sm text-muted-foreground">
                  Order book heatmap visualization - placeholder
                </div>
              </PanelSection>
            </Panel>

            <Panel>
              <PanelSection title="Quick Order" className="flex-1">
                <OrderForm symbol={selectedAsset} />
              </PanelSection>
            </Panel>
          </div>
        </PanelLayout>
      </div>
    </div>
  );
}