/**
 * Dashboard2026 Execution Page - Unified Execution Workspace
 * 
 * Consolidates scattered execution components into single unified EXECUTION workspace
 * per dashupdate1.txt plan requirements:
 * 
 * Panels:
 * - Order Ticket
 * - Positions
 * - Orders
 * - Risk
 * - Execution Feed
 * 
 * Actions:
 * - Buy, Sell, Quick Buy, Quick Sell
 * 
 * Order Types:
 * - Market, Limit, Stop, Stop Limit, Trailing Stop, OCO, Bracket Orders, TWAP, VWAP
 */

import { useState } from 'react';
import { Panel, PanelLayout, PanelSection } from '@/components/agent/Panel';
import { OrderForm, SLTPBuilder } from '@/domains/execution';
import { Activity, Target, Briefcase, Shield, Zap, CheckSquare } from 'lucide-react';

interface ExecutionPageProps {
  className?: string;
}

export function ExecutionPage({ className }: ExecutionPageProps) {
  const [selectedTab, setSelectedTab] = useState('orders');
  const [selectedOrderType, setSelectedOrderType] = useState('market');

  const executionTabs = [
    { id: 'orders', label: 'Orders & Fills', icon: Activity },
    { id: 'positions', label: 'Positions', icon: Briefcase },
    { id: 'risk', label: 'Risk', icon: Shield },
    { id: 'execution-feed', label: 'Execution Feed', icon: Zap },
  ];

  const orderTypes = [
    { id: 'market', label: 'Market' },
    { id: 'limit', label: 'Limit' },
    { id: 'stop', label: 'Stop' },
    { id: 'stop-limit', label: 'Stop Limit' },
    { id: 'trailing-stop', label: 'Trailing Stop' },
    { id: 'oco', label: 'OCO' },
    { id: 'bracket', label: 'Bracket Orders' },
    { id: 'twap', label: 'TWAP' },
    { id: 'vwap', label: 'VWAP' },
  ];

  return (
    <div className={`execution-workspace-page flex flex-col h-full ${className}`}>
      {/* Header */}
      <div className="execution-header flex items-center justify-between border-b border-border bg-muted/30 px-6 py-4">
        <div className="flex items-center gap-3">
          <Target className="w-6 h-6 text-blue-500" />
          <div>
            <h1 className="text-lg font-semibold">Execution Workspace</h1>
            <p className="text-xs text-muted-foreground">
              Execution engine workspace with advanced order management
            </p>
          </div>
        </div>
        
        {/* Quick Actions */}
        <div className="flex items-center gap-2">
          <button className="flex items-center gap-2 px-4 py-2 bg-green-500/10 text-green-500 border border-green-500/30 rounded text-sm hover:bg-green-500/20">
            <CheckSquare className="w-4 h-4" />
            Quick Buy
          </button>
          <button className="flex items-center gap-2 px-4 py-2 bg-red-500/10 text-red-500 border border-red-500/30 rounded text-sm hover:bg-red-500/20">
            <CheckSquare className="w-4 h-4" />
            Quick Sell
          </button>
        </div>
      </div>

      {/* Tab Navigation */}
      <div className="tab-navigation border-b border-border bg-muted/30 px-6">
        <div className="flex gap-2">
          {executionTabs.map((tab) => (
            <button
              key={tab.id}
              onClick={() => setSelectedTab(tab.id)}
              className={`flex items-center gap-2 px-4 py-2 text-sm transition-colors ${
                selectedTab === tab.id
                  ? 'bg-accent/10 text-accent border-b-2 border-accent'
                  : 'text-slate-400 hover:bg-bg hover:text-accent'
              }`}
            >
              <tab.icon className="w-4 h-4" />
              {tab.label}
            </button>
          ))}
        </div>
      </div>

      {/* Main Content */}
      <div className="flex-1 overflow-auto p-6">
        {selectedTab === 'orders' && (
          <PanelLayout columns={2} gap={6}>
            {/* Order Entry Panel */}
            <Panel>
              <PanelSection title="Order Entry" className="flex-1">
                {/* Order Type Selector */}
                <div className="mb-4">
                  <div className="text-xs text-muted-foreground mb-2">Order Type</div>
                  <div className="grid grid-cols-3 gap-2">
                    {orderTypes.map((type) => (
                      <button
                        key={type.id}
                        onClick={() => setSelectedOrderType(type.id)}
                        className={`px-3 py-2 text-xs rounded border transition-colors ${
                          selectedOrderType === type.id
                            ? 'bg-accent/10 text-accent border-accent/30'
                            : 'text-slate-400 border-border hover:border-accent/30'
                        }`}
                      >
                        {type.label}
                      </button>
                    ))}
                  </div>
                </div>

                {/* Order Form */}
                <OrderForm symbol="BTC/USD" />
              </PanelSection>
            </Panel>

            {/* SL/TP Builder */}
            <Panel>
              <PanelSection title="Stop Loss / Take Profit" className="flex-1">
                <SLTPBuilder form="spot" />
              </PanelSection>
            </Panel>

            {/* Active Orders */}
            <Panel className="col-span-2">
              <PanelSection title="Active Orders" className="flex-1">
                <div className="text-sm text-muted-foreground">
                  Active orders table - placeholder
                </div>
              </PanelSection>
            </Panel>
          </PanelLayout>
        )}

        {selectedTab === 'positions' && (
          <PanelLayout columns={1} gap={6}>
            <Panel>
              <PanelSection title="Open Positions" className="flex-1">
                <div className="text-sm text-muted-foreground">
                  Open positions table - placeholder
                </div>
              </PanelSection>
            </Panel>
          </PanelLayout>
        )}

        {selectedTab === 'risk' && (
          <PanelLayout columns={2} gap={6}>
            <Panel>
              <PanelSection title="Order Risk" className="flex-1">
                <div className="text-sm text-muted-foreground">
                  Order risk analysis - placeholder
                </div>
              </PanelSection>
            </Panel>
            <Panel>
              <PanelSection title="Position Risk" className="flex-1">
                <div className="text-sm text-muted-foreground">
                  Position risk analysis - placeholder
                </div>
              </PanelSection>
            </Panel>
          </PanelLayout>
        )}

        {selectedTab === 'execution-feed' && (
          <PanelLayout columns={1} gap={6}>
            <Panel>
              <PanelSection title="Execution Feed" className="flex-1">
                <div className="text-sm text-muted-foreground">
                  Real-time execution feed - placeholder
                </div>
              </PanelSection>
            </Panel>
          </PanelLayout>
        )}
      </div>
    </div>
  );
}