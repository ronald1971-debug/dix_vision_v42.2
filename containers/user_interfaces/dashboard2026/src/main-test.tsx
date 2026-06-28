import { StrictMode } from "react";
import { createRoot } from "react-dom/client";

console.log('🚀 TEST: Starting minimal dashboard...');

const TestApp = () => {
  return (
    <div style={{ padding: '20px', fontFamily: 'Arial' }}>
      <h1>Dashboard2026 Test</h1>
      <p>If you can see this, React is working!</p>
      <div style={{ color: 'green', fontSize: '24px' }}>
        ✅ Dashboard2026 Basic Render Successful
      </div>
    </div>
  );
};

const rootEl = document.getElementById("root");
if (!rootEl) {
  throw new Error("dashboard2026: #root element missing in index.html");
}

console.log('✅ Rendering Test Dashboard...');

createRoot(rootEl).render(
  <StrictMode>
    <TestApp />
  </StrictMode>,
);

console.log('✅ Test Dashboard Render Complete');