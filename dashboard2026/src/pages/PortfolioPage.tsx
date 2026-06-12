/**
 * Dashboard2026 Portfolio Page - Unified Portfolio Section
 * 
 * Consolidates scattered portfolio components into single unified PORTFOLIO section
 * per dashupdate1.txt plan requirements:
 * 
 * Panels:
 * - Allocation
 * - Exposure
 * - PnL
 * - Performance
 * - Attribution
 * - Risk
 * - Capital Distribution
 */

import { useState } from 'react';
import { Panel, PanelLayout, PanelSection } from '@/components/agent/Panel';
import { Briefcase, TrendingUp, Activity, PieChart, Gauge, Shield, BarChart3 } from 'lucide-react';

interface PortfolioPageProps {
  className?: string;
}

export function PortfolioPage({ className }: PortfolioPageProps) {
  const [selectedTab, setSelectedTab] = useState('allocation');

  const portfolioTabs = [
    { id: 'allocation', label: 'Allocation', icon: PieChart },
    { id: 'exposure', label: 'Exposure', icon: BarChart3 },
    { id: 'pnl', label: 'PnL', icon: TrendingUp },
    { id: 'performance', label: 'Performance', icon: Activity },
    { id: 'attribution', label: 'Attribution', icon: Briefcase },
    { id: 'risk', label: 'Risk', icon: Gauge },
    { id: 'capital', label: 'Capital Distribution', icon: Shield },
  ];

  return (
    <div className={`portfolio-section-page flex flex-col h-full ${className}`}>
      {/* Header */}
      <div className="portfolio-header flex items-center justify-between border-b border-border bg-muted/30 px-6 py-4">
        <div className="flex items-center gap-3">
          <Briefcase className="w-6 h-6 text-blue-500" />
          <div>
            <h1 className="text-lg font-semibold">Portfolio Section</h1>
            <p className="text-xs text-muted-foreground">
              Comprehensive portfolio management and analysis
            </p>
          </div>
        </div>
      </div>

      {/* Tab Navigation */}
      <div className="tab-navigation border-b border-border bg-muted/30 px-6">
        <div className="flex gap-2">
          {portfolioTabs.map((tab) => (
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
        {selectedTab === 'allocation' && (
          <PanelLayout columns={2} gap={6}>
            <Panel>
              <PanelSection title="Asset Allocation" className="flex-1">
                <div className="text-sm text-muted-foreground">
                  Asset allocation visualization - placeholder
                </div>
              </PanelSection>
            </Panel>
            <Panel>
              <PanelSection title="Sector Allocation" className="flex-1">
                <div className="text-sm text-muted-foreground">
                  Sector allocation breakdown - placeholder
                </div>
              </PanelSection>
            </Panel>
          </PanelLayout>
        )}

        {selectedTab === 'exposure' && (
          <PanelLayout columns={2} gap={6}>
            <Panel>
              <PanelSection title="Market Exposure" className="flex-1">
                <div className="text-sm text-muted-foreground">
                  Market exposure analysis - placeholder
                </div>
              </PanelSection>
            </Panel>
            <Panel>
              <PanelSection title="Currency Exposure" className="flex-1">
                <div className="text-sm text-muted-foreground">
                  Currency exposure breakdown - placeholder
                </div>
              </PanelSection>
            </Panel>
          </PanelLayout>
        )}

        {selectedTab === 'pnl' && (
          <PanelLayout columns={2} gap={6}>
            <Panel>
              <PanelSection title="Daily PnL" className="flex-1">
                <div className="text-sm text-muted-foreground">
                  Daily PnL breakdown - placeholder
                </div>
              </PanelSection>
            </Panel>
            <Panel>
              <PanelSection title="Realized vs Unrealized" className="flex-1">
                <div className="text-sm text-muted-foreground">
                  Realized vs unrealized PnL - placeholder
                </div>
              </PanelSection>
            </Panel>
          </PanelLayout>
        )}

        {selectedTab === 'performance' && (
          <PanelLayout columns={2} gap={6}>
            <Panel>
              <PanelSection title="Performance Metrics" className="flex-1">
                <div className="text-sm text-muted-foreground">
                  Performance metrics dashboard - placeholder
                </div>
              </PanelSection>
            </Panel>
            <Panel>
              <PanelSection title="Benchmark Comparison" className="flex-1">
                <div className="text-sm text-muted-foreground">
                  Benchmark comparison - placeholder
                </div>
              </PanelSection>
            </Panel>
          </PanelLayout>
        )}

        {selectedTab === 'attribution' && (
          <PanelLayout columns={2} gap={6}>
            <Panel>
              <PanelSection title="Strategy Attribution" className="flex-1">
                <div className="text-sm text-muted-foreground">
                  Strategy attribution analysis - placeholder
                </div>
              </PanelSection>
            </Panel>
            <Panel>
              <PanelSection title="Factor Attribution" className="flex-1">
                <div className="text-sm text-muted-foreground">
                  Factor attribution breakdown - placeholder
                </div>
              </PanelSection>
            </Panel>
          </PanelLayout>
        )}

        {selectedTab === 'risk' && (
          <PanelLayout columns={2} gap={6}>
            <Panel>
              <PanelSection title="Risk Analysis" className="flex-1">
                <div className="text-sm text-muted-foreground">
                  Risk analysis dashboard - placeholder
                </div>
              </PanelSection>
            </Panel>
            <Panel>
              <PanelSection title="Risk Budget" className="flex-1">
                <div className="text-sm text-muted-foreground">
                  Risk budget utilization - placeholder
                </div>
              </PanelSection>
            </Panel>
          </PanelLayout>
        )}

        {selectedTab === 'capital' && (
          <PanelLayout columns={2} gap={6}>
            <Panel>
              <PanelSection title="Capital Distribution" className="flex-1">
                <div className="text-sm text-muted-foreground">
                  Capital distribution analysis - placeholder
                </div>
              </PanelSection>
            </Panel>
            <Panel>
              <PanelSection title="Capital Efficiency" className="flex-1">
                <div className="text-sm text-muted-foreground">
                  Capital efficiency metrics - placeholder
                </div>
              </PanelSection>
            </Panel>
          </PanelLayout>
        )}
      </div>
    </div>
  );
}