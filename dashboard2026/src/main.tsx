import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { StrictMode } from "react";
import { createRoot } from "react-dom/client";

import { App } from "@/App";
import "@/index.css";

console.log('🚀 DASHBOARD2026 Starting...');
console.log('Step 1: Imports loaded');

console.log('Step 2: Creating QueryClient');
const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      refetchOnWindowFocus: true,
      staleTime: 5_000,
      retry: 1,
    },
  },
});
console.log('✅ QueryClient created');

const rootEl = document.getElementById("root");
if (!rootEl) {
  console.error('❌ Root element not found');
  throw new Error("dashboard2026: #root element missing in index.html");
}
console.log('✅ Root element found');

try {
  console.log('Step 3: Rendering App with providers');
  createRoot(rootEl).render(
    <StrictMode>
      <QueryClientProvider client={queryClient}>
        <App />
      </QueryClientProvider>
    </StrictMode>,
  );
  console.log('✅ Dashboard render initiated');
} catch (error) {
  console.error('❌ Error rendering dashboard:', error);
  // Render error message to screen
  rootEl.innerHTML = `
    <div style="padding: 20px; font-family: monospace; color: red; background: white;">
      <h1>Dashboard Error</h1>
      <p>${error instanceof Error ? error.message : 'Unknown error'}</p>
      <pre>${error instanceof Error ? error.stack : ''}</pre>
    </div>
  `;
}
