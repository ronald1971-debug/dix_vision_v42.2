import path from "node:path";

import react from "@vitejs/plugin-react";
import { defineConfig } from "vite";

// Modular Architecture Build Configuration
// Phase 1: Architecture Optimization - Enhanced code splitting for lazy loading

export default defineConfig({
  base: "/dash2/",
  plugins: [react()],
  resolve: {
    alias: {
      "@": path.resolve(__dirname, "./src"),
    },
  },
  build: {
    outDir: "dist",
    sourcemap: true,
    emptyOutDir: true,
    chunkSizeWarningLimit: 700,
    rollupOptions: {
      output: {
        manualChunks(id) {
          // Phase 1 Modular Architecture: Enhanced code splitting for lazy loading
          
          // Core framework - always loaded
          if (id.includes("node_modules")) {
            // Vendor libraries splitting
            if (id.includes("react-grid-layout")) return "vendor-grid";
            if (id.includes("lucide-react")) return "vendor-icons";
            if (id.includes("lightweight-charts")) return "vendor-charts";
            if (id.includes("@tanstack/react-query")) return "vendor-query";
            if (id.includes("framer-motion")) return "vendor-animation";
            
            // Core React - keep together to avoid circular dependencies
            if (id.includes("react") || id.includes("react-dom") || id.includes("scheduler")) {
              return "vendor-core";
            }
            
            return "vendor";
          }
          
          // Modular Architecture Splitting
          
          // Core modules - always loaded
          if (id.includes("/core/modular-architecture/")) return "core-architecture";
          if (id.includes("/components/") && 
              (id.includes("Sidebar") || id.includes("CommandPalette") || 
               id.includes("GlobalSystemControlBar") || id.includes("ToastHost"))) {
            return "core-ui";
          }
          
          // Trading Hub modules
          if (id.includes("/pages/MarketsPage")) return "hub-trading-markets";
          if (id.includes("/pages/OrderFlowPage")) return "hub-trading-orderflow";
          if (id.includes("/pages/ChartingPage")) return "hub-trading-charting";
          if (id.includes("/pages/PortfolioPage")) return "hub-trading-portfolio";
          if (id.includes("/pages/ExecutionPage")) return "hub-trading-execution";
          if (id.includes("/pages/PositionsPage")) return "hub-trading-positions";
          if (id.includes("/pages/TradingPage")) return "hub-trading-advanced";
          if (id.includes("/pages/asset/")) return "hub-trading-asset";
          
          // Intelligence Hub modules
          if (id.includes("/pages/Indira")) return "hub-intelligence-indira";
          if (id.includes("/pages/Dyon")) return "hub-intelligence-dyon";
          if (id.includes("/pages/CognitiveChatPage")) return "hub-intelligence-chat";
          if (id.includes("/pages/AIPage")) return "hub-intelligence-ai";
          if (id.includes("/pages/MemoryPage")) return "hub-intelligence-memory";
          
          // Operations Hub modules
          if (id.includes("/pages/MissionControlPage")) return "hub-operations-mission";
          if (id.includes("/pages/SystemHealthPage")) return "hub-operations-health";
          if (id.includes("/pages/GovernancePage")) return "hub-operations-governance";
          if (id.includes("/pages/SecurityPage")) return "hub-operations-security";
          if (id.includes("/pages/RiskPage")) return "hub-operations-risk";
          if (id.includes("/pages/AlertsPage")) return "hub-operations-alerts";
          if (id.includes("/pages/AuditPage")) return "hub-operations-audit";
          if (id.includes("/pages/OperatorPage")) return "hub-operations-operator";
          if (id.includes("/pages/CredentialsPage")) return "hub-operations-auth";
          
          // Widget grouping - consolidate by functionality
          const widgetMatch = id.match(/\/widgets\/([\w-]+)\//);
          if (widgetMatch) {
            const widgetType = widgetMatch[1];
            // Group trading widgets
            if (widgetType.includes("order") || widgetType.includes("market") || widgetType.includes("trade")) {
              return "widgets-trading";
            }
            // Group intelligence widgets
            if (widgetType.includes("indira") || widgetType.includes("dyon") || widgetType.includes("cognitive")) {
              return "widgets-intelligence";
            }
            // Group operations widgets
            if (widgetType.includes("system") || widgetType.includes("health") || widgetType.includes("audit")) {
              return "widgets-operations";
            }
            return `widgets-${widgetType}`;
          }
          
          // Fallback for other pages
          const sysMatch = id.match(/\/pages\/(\w+)Page\.tsx?$/);
          if (sysMatch) return `page-${sysMatch[1].toLowerCase()}`;
        },
      },
    },
  },
  server: {
    port: 5173,
    proxy: {
      "/api": {
        target: `http://127.0.0.1:${process.env.VITE_DEV_PROXY_PORT ?? "8080"}`,
        changeOrigin: true,
      },
    },
  },
});