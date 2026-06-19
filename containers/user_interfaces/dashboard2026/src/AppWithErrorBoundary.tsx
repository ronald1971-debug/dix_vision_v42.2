import { useState, useEffect } from "react";
import { App as OriginalApp } from "./App";

export function App() {
  const [error, setError] = useState<Error | null>(null);
  const [hasError, setHasError] = useState(false);

  useEffect(() => {
    const handleError = (event: ErrorEvent) => {
      console.error('Global error caught:', event.error);
      setError(event.error instanceof Error ? event.error : new Error(String(event.error)));
      setHasError(true);
    };

    window.addEventListener('error', handleError);
    return () => window.removeEventListener('error', handleError);
  }, []);

  if (hasError && error) {
    return (
      <div className="flex h-screen items-center justify-center bg-red-900 text-white p-8">
        <div className="max-w-2xl">
          <h1 className="text-2xl font-bold mb-4">Dashboard Error</h1>
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
    return <OriginalApp />;
  } catch (err) {
    console.error('Component render error:', err);
    const errorObj = err instanceof Error ? err : new Error(String(err));
    return (
      <div className="flex h-screen items-center justify-center bg-red-900 text-white p-8">
        <div className="max-w-2xl">
          <h1 className="text-2xl font-bold mb-4">Render Error</h1>
          <p className="mb-2">{errorObj.message}</p>
          <pre className="text-xs overflow-auto bg-black/50 p-4 rounded">{errorObj.stack}</pre>
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