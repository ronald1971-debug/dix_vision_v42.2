import { useState } from "react";

import { AutonomyRibbon } from "@/components/AutonomyRibbon";
import { CommandPalette } from "@/components/CommandPalette";
import { ModeRibbon } from "@/components/ModeRibbon";
import { LiveStatusPill } from "@/components/LiveStatusPill";
import { MockDataBanner } from "@/components/MockDataBanner";
import { PadlockFloors } from "@/components/PadlockFloors";
import { PreferencesBar } from "@/components/PreferencesBar";
import { PromoteChain } from "@/components/PromoteChain";
import { Sidebar } from "@/components/Sidebar";
import { ToastHost } from "@/components/ToastHost";
import { WidgetTogglePanel } from "@/components/WidgetTogglePanel";
import { KillSwitchPill } from "@/components/KillSwitchPill";
import { DomainIndicator } from "@/components/DomainIndicator";
import { TradingStatusPill } from "@/components/TradingStatusPill";

// Meme-specific components
import { HotPairsTicker } from "@/components/HotPairsTicker";
import { TopBar } from "@/components/TopBar";

// Main dashboard pages
import { SignalsPage } from "@/pages/SignalsPage";
import { FormsPage } from "@/pages/FormsPage";
import { AdaptersPage } from "@/pages/AdaptersPage";
import { LedgerPage } from "@/pages/LedgerPage";
import { SecurityPage } from "@/pages/SecurityPage";
import { HazardsPage } from "@/pages/HazardsPage";
import { AIPage } from "@/pages/AIPage";
import { AlertsPage } from "@/pages/AlertsPage";
import { AuditPage } from "@/pages/AuditPage";
import { ChartingPage } from "@/pages/ChartingPage";
import { CognitiveChatPage } from "@/pages/CognitiveChatPage";
import { CredentialsPage } from "@/pages/CredentialsPage";
import { DyonLearningPage } from "@/pages/DyonLearningPage";
import { FabricPage } from "@/pages/FabricPage";
import { MemoryPage } from "@/pages/MemoryPage";
import { GovernancePage } from "@/pages/GovernancePage";
import { IndiraLearningPage } from "@/pages/IndiraLearningPage";
import { MarketContextPage } from "@/pages/MarketContextPage";
import { OnChainPage } from "@/pages/OnChainPage";
import { OperatorPage } from "@/pages/OperatorPage";
import { OrderFlowPage } from "@/pages/OrderFlowPage";
import { PluginsPage } from "@/pages/PluginsPage";
import { PositionsPage } from "@/pages/PositionsPage";
import { RiskPage } from "@/pages/RiskPage";
import { ScoutPage } from "@/pages/ScoutPage";
import { StrategiesPage } from "@/pages/StrategiesPage";
import { SystemHealthPage } from "@/pages/SystemHealthPage";
import { TestingPage } from "@/pages/TestingPage";
import { TradingPage } from "@/pages/TradingPage";
import { SimulationPage } from "@/pages/SimulationPage";
import { ObservatoryPage } from "@/pages/ObservatoryPage";
import { DexPage } from "@/pages/asset/DexPage";
import { ForexPage } from "@/pages/asset/ForexPage";
import { NftPage } from "@/pages/asset/NftPage";
import { PerpsPage } from "@/pages/asset/PerpsPage";
import { SpotPage } from "@/pages/asset/SpotPage";
import { StocksPage } from "@/pages/asset/StocksPage";

// Meme-specific pages
import { BigSwapPage } from "@/pages/BigSwapPage";
import { CopyTradingPage } from "@/pages/CopyTradingPage";
import { MultichartPage } from "@/pages/MultichartPage";
import { MultiswapPage } from "@/pages/MultiswapPage";
import { PairExplorerPage } from "@/pages/PairExplorerPage";
import { PoolExplorerPage } from "@/pages/PoolExplorerPage";
import { SniperPage } from "@/pages/SniperPage";
import { StatsPage } from "@/pages/StatsPage";
import { WalletInfoPage } from "@/pages/WalletInfoPage";

import { useApplyPreferences } from "@/preferences/store";
import { isPopoutRoute, useHashRoute, useIsPopout, type Route } from "@/router";
import { useGlobalHotkeys } from "@/state/hotkeys";
import { pushToast } from "@/state/toast";

function renderRoute(route: Route) {
  switch (route) {
    // Main dashboard routes
    case "spot":
      return <SpotPage />;
    case "perps":
      return <PerpsPage />;
    case "dex":
      return <DexPage />;
    case "forex":
      return <ForexPage />;
    case "stocks":
      return <StocksPage />;
    case "nft":
      return <NftPage />;
    case "operator":
      return <OperatorPage />;
    case "credentials":
      return <CredentialsPage />;
    case "chat":
      return <CognitiveChatPage />;
    case "indira":
      return <IndiraLearningPage />;
    case "dyon":
      return <DyonLearningPage />;
    case "observatory":
      return <ObservatoryPage />;
    case "testing":
      return <TestingPage />;
    case "onchain":
      return <OnChainPage />;
    case "ai":
      return <AIPage />;
    case "orderflow":
      return <OrderFlowPage />;
    case "governance":
      return <GovernancePage />;
    case "risk":
      return <RiskPage />;
    case "charting":
      return <ChartingPage />;
    case "market":
      return <MarketContextPage />;
    case "positions":
      return <PositionsPage />;
    case "trading":
      return <TradingPage />;
    case "plugins":
      return <PluginsPage />;
    case "syshealth":
      return <SystemHealthPage />;
    case "alerts":
      return <AlertsPage />;
    case "audit":
      return <AuditPage />;
    case "scout":
      return <ScoutPage />;
    case "strategies":
      return <StrategiesPage />;
    case "memory":
      return <MemoryPage />;
    case "fabric":
      return <FabricPage />;
    case "simulation":
      return <SimulationPage />;
    case "signals":
      return <SignalsPage />;
    case "forms":
      return <FormsPage />;
    case "adapters":
      return <AdaptersPage />;
    case "ledger":
      return <LedgerPage />;
    case "security":
      return <SecurityPage />;
    case "hazards":
      return <HazardsPage />;
    // Meme-specific routes
    case "explorer":
      return <PairExplorerPage />;
    case "pools":
      return <PoolExplorerPage />;
    case "bigswap":
      return <BigSwapPage />;
    case "multichart":
      return <MultichartPage />;
    case "trade":
      return <TradePage />;
    case "copy":
      return <CopyTradingPage />;
    case "sniper":
      return <SniperPage />;
    case "multiswap":
      return <MultiswapPage />;
    case "wallet":
      return <WalletInfoPage />;
    case "stats":
      return <StatsPage />;
    default:
      return <OperatorPage />;
  }
}

export function App() {
  const route = useHashRoute();
  const popout = useIsPopout();
  const [sidebarCollapsed, setSidebarCollapsed] = useState(false);
  const [paletteOpen, setPaletteOpen] = useState(false);
  useApplyPreferences();

  // Pop-out windows must keep the `#/popout/` prefix when the operator
  // navigates with hotkeys, otherwise `useIsPopout` flips back to chromed
  // mode and the second-monitor docking surface suddenly grows the full
  // sidebar + ribbons.
  const handleRouteChange = (newRoute: string) => {
    if (popout && !newRoute.startsWith("popout/")) {
      window.location.hash = `#popout/${newRoute}`;
    } else {
      window.location.hash = `#${newRoute}`;
    }
  };

  useGlobalHotkeys(
    {
      "Meta+k": () => pushToast({ title: "Command Palette", id: "cp" }),
      "Escape": () => {
        if (paletteOpen) setPaletteOpen(false);
      },
    },
  );

  return (
    <div
      className="flex h-screen w-screen flex-col overflow-hidden bg-bg text-text-primary"
      data-theme="default"
    >
      {popout ? (
        <MockDataBanner />
      ) : (
        <>
          <AutonomyRibbon />
          <ModeRibbon />
          <LiveStatusPill />
          <PadlockFloors />
          <PreferencesBar />
          <PromoteChain />
          <WidgetTogglePanel />
          <KillSwitchPill />
          <DomainIndicator />
          <TradingStatusPill />
          <HotPairsTicker />
        </>
      )}
      <div className="flex flex-1 overflow-hidden">
        <Sidebar active={route} collapsed={sidebarCollapsed} onRouteChange={handleRouteChange} />
        <div className="flex flex-1 flex-col overflow-hidden">
          {popout ? (
            <></>
          ) : (
            <TopBar
              sidebarCollapsed={sidebarCollapsed}
              onToggleSidebar={() => setSidebarCollapsed((c) => !c)}
            />
          )}
          <main className="flex-1 overflow-hidden">
            <CommandPalette open={paletteOpen} onClose={() => setPaletteOpen(false)} />
            {renderRoute(route)}
          </main>
        </div>
      </div>
      <ToastHost />
    </div>
  );
}