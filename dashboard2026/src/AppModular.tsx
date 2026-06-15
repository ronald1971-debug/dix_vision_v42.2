/**
 * Modular App Component
 * DIX VISION v42.2 - Phase 1: Architecture Optimization
 * 
 * Refactored App component using modular architecture with lazy loading,
 * resource monitoring, and user profile-based feature loading.
 * 
 * This replaces the eager-loading App.tsx while preserving all functionality.
 */

import { useState, useEffect } from "react";

import { GlobalSystemControlBar } from "@/components/GlobalSystemControlBar";
import { CommandPalette } from "@/components/CommandPalette";
import { LiveStatusPill } from "@/components/LiveStatusPill";
import { MockDataBanner } from "@/components/MockDataBanner";
import { PadlockFloors } from "@/components/PadlockFloors";
import { PreferencesBar } from "@/components/PreferencesBar";
import { PromoteChain } from "@/components/PromoteChain";
import { Sidebar } from "@/components/Sidebar";
import { ToastHost } from "@/components/ToastHost";
import { WidgetTogglePanel } from "@/components/WidgetTogglePanel";
import { DomainIndicator } from "@/components/DomainIndicator";
import { AgentOpsProvider } from "@/context/AgentOpsContext";
import { useApplyPreferences } from "@/preferences/store";
import { isPopoutRoute, useHashRoute, useIsPopout, type Route } from "@/router";
import { useGlobalHotkeys } from "@/state/hotkeys";
import { pushToast } from "@/state/toast";

// Modular Architecture Imports
import { 
  UserProfileProvider, 
  useUserProfile,
  renderLazyRoute,
  prefetchRoutes,
  resourceMonitor,
  useResourceMonitor
} from "@/core/modular-architecture";

function AppContent() {
  const route = useHashRoute();
  const popout = useIsPopout();
  const [sidebarCollapsed, setSidebarCollapsed] = useState(false);
  const [paletteOpen, setPaletteOpen] = useState(false);
  useApplyPreferences();
  
  // Resource monitoring
  useResourceMonitor(10000); // Monitor every 10 seconds
  
  // User profile context
  const { currentProfile, profileConfig } = useUserProfile();

  // Pop-out windows must keep the `#/popout/` prefix when the operator
  // navigates with hotkeys, otherwise `useIsPopout` flips back to chromed
  // mode and the second-monitor docking surface suddenly grows the full
  // sidebar + ribbons.
  const goRoute = (target: string) => {
    const prefix = isPopoutRoute(window.location.hash) ? "#/popout/" : "#/";
    window.location.hash = `${prefix}${target}`;
  };
  
  useGlobalHotkeys({
    "toggle-palette": () => setPaletteOpen((o) => !o),
    "toggle-sidebar": () => setSidebarCollapsed((c) => !c),
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

  // Prefetch routes based on user profile
  useEffect(() => {
    if (profileConfig.preloadRoutes.length > 0) {
      prefetchRoutes(profileConfig.preloadRoutes);
    }
  }, [profileConfig.preloadRoutes]);

  if (popout) {
    // J-track pop-out window: chromeless render — no sidebar, no
    // top ribbons, no command palette so the operator can dock the
    // route into a second monitor with maximum vertical real estate.
    // The mock-data banner still renders so the operator can never
    // mistake mock orderflow data for live data on a docked monitor.
    return (
      <div className="flex h-full flex-col">
        <MockDataBanner />
        <main className="flex-1 overflow-auto px-3 py-2">
          {renderLazyRoute(route)}
        </main>
      </div>
    );
  }

  return (
    <AgentOpsProvider>
      <div className="flex h-screen flex-col overflow-hidden bg-surface text-slate-100">
        {/* Mock Data Banner */}
        <MockDataBanner />

        {/* Top Ribbon */}
        <header className="flex items-center justify-between border-b border-border bg-surface-raised px-4 py-2 shrink-0">
          <div className="flex items-center gap-3">
            <PadlockFloors />
            <DomainIndicator />
          </div>
          <div className="flex items-center gap-3">
            <PromoteChain />
            <LiveStatusPill />
            <PreferencesBar />
            <GlobalSystemControlBar />
          </div>
        </header>

        {/* Main Content Area */}
        <div className="flex flex-1 overflow-hidden">
          {/* Sidebar */}
          <Sidebar collapsed={sidebarCollapsed} onToggle={() => setSidebarCollapsed(!sidebarCollapsed)} />

          {/* Route Content */}
          <main className="flex-1 overflow-auto">
            {renderLazyRoute(route)}
          </main>
        </div>

        {/* Command Palette */}
        <CommandPalette open={paletteOpen} onClose={() => setPaletteOpen(false)} />

        {/* Widget Toggle Panel */}
        <WidgetTogglePanel />

        {/* Toast Notifications */}
        <ToastHost />
        
        {/* Resource Monitor Indicator (development) */}
        {process.env.NODE_ENV === 'development' && (
          <ResourceMonitorIndicator currentProfile={currentProfile} />
        )}
      </div>
    </AgentOpsProvider>
  );
}

/**
 * Resource Monitor Indicator Component
 * Shows real-time resource metrics in development mode
 */
function ResourceMonitorIndicator({ currentProfile }: { currentProfile: string }) {
  const metrics = resourceMonitor.getCurrentMetrics();
  
  return (
    <div className="fixed bottom-4 right-4 bg-surface-raised border border-border rounded-lg p-3 text-xs space-y-1 z-50">
      <div className="font-semibold mb-2">Resource Monitor ({currentProfile})</div>
      <div>Bundle: {metrics.bundleSize} KB</div>
      <div>Memory: {metrics.memoryUsage.toFixed(1)} MB</div>
      <div>Modules: {metrics.activeModules}/{metrics.totalModules}</div>
      <div>Load Time: {metrics.loadTime.toFixed(0)} ms</div>
    </div>
  );
}

/**
 * Main App Component with User Profile Provider
 */
export function AppModular() {
  return (
    <UserProfileProvider>
      <AppContent />
    </UserProfileProvider>
  );
}