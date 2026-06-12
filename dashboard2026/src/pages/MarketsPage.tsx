/**
 * Dashboard2026 Markets Page - Unified Markets Workspace
 * 
 * Consolidates scattered market components into single unified MARKETS workspace
 * per dashupdate1.txt plan requirements:
 * 
 * Supports: Stocks, Forex, Crypto, Futures, Options, Commodities, Indices, DEX Markets
 * Panels: Watchlist, Market Scanner, Professional Chart, Order Flow, News & Events
 * Chart Types: Candlestick, Heikin Ashi, Renko, Range Bars, Tick Charts, Line Charts
 * Indicators: EMA, SMA, VWAP, RSI, MACD, ATR, Bollinger Bands, etc.
 * Order Flow: DOM Ladder, Footprint Charts, Time & Sales, Volume Delta, etc.
 */

import { useState } from 'react';
import { Panel, PanelLayout, PanelSection } from '@/components/agent/Panel';
import { ChartPanel } from '@/widgets/ChartPanel';
import { DepthLadder } from '@/widgets/DepthLadder';
import { TimeAndSalesTape } from '@/widgets/TimeAndSalesTape';
import { OrderForm } from '@/widgets/OrderForm';
import { CandlestickChart, BarChart3, Activity, Layers, Compass } from 'lucide-react';

interface MarketsPageProps {
  className?: string;
}

export function MarketsPage({ className }: MarketsPageProps) {
  const [selectedAsset, setSelectedAsset] = useState('BTC/USD');
  const [selectedAssetClass, setSelectedAssetClass] = useState('Crypto');

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
                <div className="text-sm text-muted-foreground">
                  Market scanner functionality - placeholder
                </div>
              </PanelSection>
            </Panel>

            <Panel>
              <PanelSection title="Watchlist" className="flex-1">
                <div className="text-sm text-muted-foreground">
                  Watchlist functionality - placeholder
                </div>
              </PanelSection>
            </Panel>

            <Panel>
              <PanelSection title="News & Events" className="flex-1">
                <div className="text-sm text-muted-foreground">
                  News and events feed - placeholder
                </div>
              </PanelSection>
            </Panel>
          </div>

          {/* Middle Column: Professional Chart */}
          <div className="col-span-1">
            <Panel>
              <PanelSection title="Professional Chart" className="flex-1">
                <ChartPanel symbol={selectedAsset} />
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
              <PanelSection title="Time & Sales" className="flex-1">
                <TimeAndSalesTape symbol={selectedAsset} />
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