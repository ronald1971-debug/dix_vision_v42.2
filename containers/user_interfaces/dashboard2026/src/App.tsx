console.log('🔧 App.tsx: File loaded');
import { useState, useEffect } from "react";

import { GlobalSystemControlBar } from "@/domains/operator/components/GlobalSystemControlBar";
import { CommandPalette } from "@/components/CommandPalette";
import { LiveStatusPill } from "@/components/LiveStatusPill";
import { EnhancedSystemStatusBanner } from "@/components/world/EnhancedSystemStatusBanner";
import { PadlockFloors } from "@/components/PadlockFloors";
import { PreferencesBar } from "@/components/PreferencesBar";
import { PromoteChain } from "@/components/PromoteChain";
import { Sidebar } from "@/components/Sidebar";
import { ToastHost } from "@/components/ToastHost";
import { WidgetTogglePanel } from "@/components/WidgetTogglePanel";
import { DomainIndicator } from "@/components/DomainIndicator";

import { SignalsPage } from "@/pages/SignalsPage";
import { MissionControlPage } from "@/pages/MissionControlPage";
import { FormsPage } from "@/pages/FormsPage";
import { AdaptersPage } from "@/pages/AdaptersPage";
import { LedgerPage } from "@/pages/LedgerPage";
import { SecurityPage } from "@/pages/SecurityPage";
import { SecurityAnalysisPage } from "@/pages/memecoin/SecurityAnalysisPage";
import { DiscoveryPage } from "@/pages/memecoin/DiscoveryPage";
import { TradingAutomationPage } from "@/pages/memecoin/TradingAutomationPage";
import { WhaleTrackingPage } from "@/pages/memecoin/WhaleTrackingPage";
import { TokenProfilingPage } from "@/pages/memecoin/TokenProfilingPage";
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
import { MarketsPage } from "@/pages/MarketsPage";
import { PortfolioPage } from "@/pages/PortfolioPage";
import { ExecutionPage } from "@/pages/ExecutionPage";
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
import { AgentOpsPage } from "@/pages/AgentOpsPage";
import { IndiraWorkspacePage } from "@/pages/IndiraWorkspacePage";
import { IndiraCognitiveCenterPage } from "@/pages/IndiraCognitiveCenterPage";
import { DyonWorkspacePage } from "@/pages/DyonWorkspacePage";
import { OperatorWorkspacePage } from "@/pages/OperatorWorkspacePage";
import { AgentOpsProvider } from "@/context/AgentOpsContext";
import { useApplyPreferences } from "@/preferences/store";
import { isPopoutRoute, useHashRoute, useIsPopout, type Route } from "@/router";
import { useGlobalHotkeys } from "@/state/hotkeys";
import { pushToast } from "@/state/toast";

console.log('🔧 App.tsx: All imports loaded successfully');

function renderRoute(route: Route) {
  console.log('🔧 App.tsx: renderRoute called with:', route);
  // Phase 3: Redirect legacy asset routes to unified markets page
  if (["spot", "perps", "dex", "forex", "stocks", "nft"].includes(route)) {
    return <MarketsPage />;
  }

  switch (route) {
    case "mission-control":
      return <MissionControlPage />;
    case "markets":
      return <MarketsPage />;
    case "spot":
      return <MarketsPage />; // Redirect to unified markets
    case "perps":
      return <MarketsPage />; // Redirect to unified markets
    case "dex":
      return <MarketsPage />; // Redirect to unified markets
    case "forex":
      return <MarketsPage />; // Redirect to unified markets
    case "stocks":
      return <MarketsPage />; // Redirect to unified markets
    case "nft":
      return <MarketsPage />; // Redirect to unified markets
    case "operator":
      return <OperatorPage />;
    case "credentials":
      return <CredentialsPage />;
    case "chat":
      return <CognitiveChatPage />;
    case "indira":
      return <IndiraLearningPage />;
    case "indira-cognitive-center":
      return <IndiraCognitiveCenterPage />;
    case "dyon":
      return <DyonLearningPage />;
    case "agent-ops":
      return <AgentOpsPage />;
    case "indira-workspace":
      return <IndiraWorkspacePage />;
    case "dyon-workspace":
      return <DyonWorkspacePage />;
    case "operator-workspace":
      return <OperatorWorkspacePage />;
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
      return <MarketsPage />;
    case "portfolio":
      return <PortfolioPage />;
    case "execution":
      return <ExecutionPage />;
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
    case "memecoin-security":
      return <SecurityAnalysisPage />;
    case "hazards":
      return <HazardsPage />;

    case "memecoin-discovery":
      return <DiscoveryPage />;
    case "memecoin-trading":
      return <TradingAutomationPage />;
    case "memecoin-whales":
      return <WhaleTrackingPage />;
    case "memecoin-profiles":
      return <TokenProfilingPage />;











    default:
      return <OperatorPage />;
  }
}

console.log('🔧 App.tsx: renderRoute function defined');

export function App() {
  console.log('🔧 App component: Starting render');
  const [error, setError] = useState<Error | null>(null);
  const [sidebarCollapsed, setSidebarCollapsed] = useState(false);
  const [paletteOpen, setPaletteOpen] = useState(false);
  
  useEffect(() => {
    const handleError = (e: ErrorEvent) => {
      console.error('🔧 App component: Global error caught:', e.error);
      setError(e.error instanceof Error ? e.error : new Error(String(e.error)));
    };
    window.addEventListener('error', handleError);
    return () => window.removeEventListener('error', handleError);
  }, []);

  if (error) {
    console.error('🔧 App component: Rendering error state:', error);
    return (
      <div className="flex h-screen items-center justify-center bg-red-900 text-white p-8">
        <div className="max-w-2xl">
          <h1 className="text-2xl font-bold mb-4">App Component Error</h1>
          <p className="mb-2">{error.message}</p>
          <pre className="text-xs overflow-auto bg-black/50 p-4 rounded">{error.stack}</pre>
          <button 
            onClick={() => window.location.reload()}
            className="mt-4 px-4 py-2 bg-white text-red-900 rounded font-bold"
          >
            Reload Dashboard
          </button>
        </div>
      </div>
    );
  }

  try {
    console.log('🔧 App component: Getting route and popout');
    const route = useHashRoute();
    const popout = useIsPopout();
    console.log('🔧 App component: Route:', route, 'Popout:', popout);

    try {
      console.log('🔧 App component: Calling useApplyPreferences');
      useApplyPreferences();
      console.log('🔧 App component: useApplyPreferences succeeded');
    } catch (err) {
      console.error('❌ App component: useApplyPreferences failed:', err);
      setError(err instanceof Error ? err : new Error(String(err)));
      return null;
    }

    const goRoute = (target: string) => {
      const prefix = isPopoutRoute(window.location.hash) ? "#/popout/" : "#/";
      window.location.hash = `${prefix}${target}`;
    };

    try {
      console.log('🔧 App component: Setting up hotkeys');
      useGlobalHotkeys({
        "toggle-palette": () => setPaletteOpen((o: boolean) => !o),
        "toggle-sidebar": () => setSidebarCollapsed((c: boolean) => !c),
        "go-operator": () => goRoute("operator"),
        "go-mission-control": () => goRoute("mission-control"),
        "go-governance": () => goRoute("governance"),
        "go-testing": () => goRoute("testing"),
        "go-ai": () => goRoute("ai"),
        "go-signals": () => goRoute("signals"),
        "go-forms": () => goRoute("forms"),
        "go-adapters": () => goRoute("adapters"),
        "go-ledger": () => goRoute("ledger"),
        "go-security": () => goRoute("security"),
        "go-hazards": () => goRoute("hazards"),
        "kill-switch": () => {
          pushToast("Kill switch armed", {
            tone: "danger",
            hint: "release ctrl+shift+k to abort all autonomous activity",
          });
        },
      });
      console.log('🔧 App component: Hotkeys set up successfully');
    } catch (err) {
      console.error('❌ App component: useGlobalHotkeys failed:', err);
      setError(err instanceof Error ? err : new Error(String(err)));
      return null;
    }

    console.log('🔧 App component: About to render JSX');

    if (popout) {
      console.log('🔧 App component: Rendering popout mode');
      return (
        <div className="flex h-full flex-col">
          <EnhancedSystemStatusBanner />
          <main className="flex-1 overflow-auto px-3 py-2">
            {renderRoute(route)}
          </main>
          <ToastHost />

        </div>
      );
    }

    console.log('🔧 App component: Rendering main mode');
    return (
      <AgentOpsProvider>
        <div className="flex h-full flex-col">
          <EnhancedSystemStatusBanner />
          <header
            data-layout-glow
            className="flex flex-col gap-2 border-b border-border bg-surface px-4 py-2"
          >
            <div className="flex items-center gap-3">
              <span className="text-base font-semibold tracking-tight">
                DIX VISION
              </span>
              <span className="font-mono text-[10px] uppercase tracking-widest text-slate-500">
                /{route}
              </span>
              <div className="ml-4 flex items-center gap-2">
                <LiveStatusPill />
                <DomainIndicator />
              </div>
            </div>
            <div className="flex items-center gap-2">
              <GlobalSystemControlBar />
              <PadlockFloors />
            </div>
          </header>
          <div className="flex flex-1 overflow-hidden">
            <Sidebar active={route} collapsed={sidebarCollapsed} onToggle={() => setSidebarCollapsed(!sidebarCollapsed)} />
            <main className="flex-1 overflow-auto">
              {paletteOpen && (
                <CommandPalette open={paletteOpen}
                  onClose={() => setPaletteOpen(false)}
                  onNavigate={(navigateRoute: Route) => {
                    goRoute(navigateRoute);
                    setPaletteOpen(false);
                  }}
                />
              )}
              {renderRoute(route)}
            </main>
            <aside className="flex w-12 flex-col border-l border-border bg-surface px-1 py-2">
              <PreferencesBar />
              <PromoteChain />
              <WidgetTogglePanel />
            </aside>
          </div>
          <ToastHost />

        </div>
      </AgentOpsProvider>
    );
  } catch (err) {
    console.error('❌ App component: Render error:', err);
    setError(err instanceof Error ? err : new Error(String(err)));
    return (
      <div className="flex h-screen items-center justify-center bg-red-900 text-white p-8">
        <div className="max-w-2xl">
          <h1 className="text-2xl font-bold mb-4">Render Error</h1>
          <p className="mb-2">{err instanceof Error ? err.message : String(err)}</p>
          <pre className="text-xs overflow-auto bg-black/50 p-4 rounded">{err instanceof Error ? err.stack : ''}</pre>
          <button 
            onClick={() => window.location.reload()}
            className="mt-4 px-4 py-2 bg-white text-red-900 rounded font-bold"
          >
            Reload Dashboard
          </button>
        </div>
      </div>
    );
  }
}

console.log('🔧 App.tsx: App component defined');