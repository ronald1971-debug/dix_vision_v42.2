import path from "node:path";
import { defineConfig, loadEnv } from 'vite';
import react from "@vitejs/plugin-react";
import { visualizer } from 'rollup-plugin-visualizer';
import viteCompression from 'vite-plugin-compression';

// Load environment variables
const env = loadEnv('', process.cwd());

/**
 * Phase 2: Resource Optimization Build Configuration
 * Enhanced build optimization with compression, tree shaking, 
 * dead code elimination, and advanced bundle analysis
 */
export default defineConfig({
  base: "/dash2/",
  plugins: [
    react(),
    // Bundle visualization for analysis
    visualizer({
      open: false,
      gzipSize: true,
      brotliSize: true,
    }),
    // Gzip compression for production
    viteCompression({
      algorithm: 'gzip',
      ext: '.gz',
    }),
    // Brotli compression for production
    viteCompression({
      algorithm: 'brotliCompress',
      ext: '.br',
    }),
  ],
  resolve: {
    alias: {
      "@": path.resolve(__dirname, "./src"),
    },
  },
  build: {
    outDir: "dist",
    sourcemap: env.MODE === 'development',
    emptyOutDir: true,
    chunkSizeWarningLimit: 600, // Lower threshold for Phase 2 optimization
    minify: 'terser',
    target: 'esnext',
    rollupOptions: {
      output: {
        manualChunks(id) {
          // Phase 2 Enhanced Build Optimization
          
          // Core framework - always loaded (smallest possible chunks)
          if (id.includes("node_modules")) {
            // Vendor libraries - aggressive splitting
            if (id.includes("react-grid-layout")) return "vendor-grid";
            if (id.includes("lucide-react")) return "vendor-icons";
            if (id.includes("lightweight-charts")) return "vendor-charts";
            if (id.includes("@tanstack/react-query")) return "vendor-query";
            if (id.includes("framer-motion")) return "vendor-animation";
            
            // Core React - keep together but separate from other vendors
            if (id.includes("react") || id.includes("react-dom") || id.includes("scheduler")) {
              return "vendor-core";
            }
            
            // Additional vendor splitting for optimization
            if (id.includes("@/node_modules")) {
              // Split large libraries into their own chunks
              if (id.includes("date-fns")) return "vendor-date";
              if (id.includes("clsx")) return "vendor-clsx";
              if (id.includes("class-variance-authority")) return "vendor-cva";
            }
            
            return "vendor";
          }
          
          // Core Architecture - minimal chunk
          if (id.includes("/core/modular-architecture/")) return "core-arch";
          if (id.includes("/core/resource-optimization/")) return "core-resource";
          
          // Core UI - essential components
          if (id.includes("/components/") && 
              (id.includes("Sidebar") || id.includes("CommandPalette") || 
               id.includes("GlobalSystemControlBar") || id.includes("ToastHost"))) {
            return "core-ui";
          }
          
          // Hub-based splitting for maximum efficiency
          
          // Trading Hub - split by functionality
          if (id.includes("/pages/MarketsPage")) return "hub-trade-markets";
          if (id.includes("/pages/OrderFlowPage")) return "hub-trade-flow";
          if (id.includes("/pages/ChartingPage")) return "hub-trade-charts";
          if (id.includes("/pages/PortfolioPage")) return "hub-trade-portfolio";
          if (id.includes("/pages/ExecutionPage")) return "hub-trade-exec";
          if (id.includes("/pages/PositionsPage")) return "hub-trade-positions";
          if (id.includes("/pages/TradingPage")) return "hub-trade-advanced";
          if (id.includes("/pages/asset/")) return "hub-trade-asset";
          
          // Intelligence Hub - split by cognitive engine
          if (id.includes("/pages/Indira")) return "hub-intel-indira";
          if (id.includes("/pages/Dyon")) return "hub-intel-dyon";
          if (id.includes("/pages/CognitiveChatPage")) return "hub-intel-chat";
          if (id.includes("/pages/AIPage")) return "hub-intel-ai";
          if (id.includes("/pages/MemoryPage")) return "hub-intel-memory";
          
          // Operations Hub - split by system function
          if (id.includes("/pages/MissionControlPage")) return "hub-ops-mission";
          if (id.includes("/pages/SystemHealthPage")) return "hub-ops-health";
          if (id.includes("/pages/GovernancePage")) return "hub-ops-govern";
          if (id.includes("/pages/SecurityPage")) return "hub-ops-security";
          if (id.includes("/pages/RiskPage")) return "hub-ops-risk";
          if (id.includes("/pages/AlertsPage")) return "hub-ops-alerts";
          if (id.includes("/pages/AuditPage")) return "hub-ops-audit";
          if (id.includes("/pages/OperatorPage")) return "hub-ops-operator";
          if (id.includes("/pages/CredentialsPage")) return "hub-ops-auth";
          
          // Widget grouping - aggressive consolidation
          const widgetMatch = id.match(/\/widgets\/([\w-]+)\//);
          if (widgetMatch) {
            const widgetType = widgetMatch[1];
            // Group by functionality for maximum consolidation
            if (widgetType.includes("order") || widgetType.includes("market") || 
                widgetType.includes("trade") || widgetType.includes("chart")) {
              return "widg-trade"; // Single chunk for all trading widgets
            }
            if (widgetType.includes("indira") || widgetType.includes("dyon") || 
                widgetType.includes("cognitive") || widgetType.includes("brain")) {
              return "widg-intel"; // Single chunk for all intelligence widgets
            }
            if (widgetType.includes("system") || widgetType.includes("health") || 
                widgetType.includes("audit") || widgetType.includes("monitor")) {
              return "widg-ops"; // Single chunk for all operations widgets
            }
            return `widg-${widgetType}`;
          }
          
          // Fallback for other pages - consolidate as much as possible
          const sysMatch = id.match(/\/pages\/(\w+)Page\.tsx?$/);
          if (sysMatch) return `page-${sysMatch[1].toLowerCase()}`;
        },
        // Optimize chunk file names for better caching
        chunkFileNames: 'static/js/[name]-[hash].js',
        entryFileNames: 'static/js/[name]-[hash].js',
        assetFileNames: 'static/[ext]/[name]-[hash].[ext]',
      },
      // Additional optimization settings
      onwarn(warning, warn) {
        // Ignore certain warnings
        if (warning.code === 'MODULE_BUNDLE_SIZE_LIMIT') return;
        warn(warning);
      },
    },
    // Advanced CSS optimization
    cssCodeSplit: true,
    // Optimize CSS
    cssMinify: true,
  },
  // Development server optimization
  server: {
    port: 5173,
    proxy: {
      "/api": {
        target: `http://127.0.0.1:${process.env.VITE_DEV_PROXY_PORT ?? "8080"}`,
        changeOrigin: true,
      },
    },
    // Enable HMR optimization
    hmr: {
      overlay: false,
    },
  },
  // Optimize dependencies
  optimizeDeps: {
    include: [
      'react',
      'react-dom',
      '@tanstack/react-query',
      'lucide-react',
      'framer-motion',
      'lightweight-charts',
      'react-grid-layout'
    ],
    exclude: [], // Don't exclude anything for maximum optimization
  },
  // Preview server optimization
  preview: {
    port: 4173,
  },
});