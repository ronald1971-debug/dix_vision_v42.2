/**
 * Refactored Systems Context Provider
 * Provides access to Phase 17, 18, 19 refactored systems throughout the dashboard
 */

import { createContext, useContext, ReactNode, useEffect, useState } from 'react';

// System imports
import { advancedRiskManagement, complianceManagement, portfolioGovernance } from '@/riskcompliance';
import { mobileOptimization, desktopApplication, apiIntegration } from '@/crossplatform';
import { stockTradingSystem, forexTradingSystem, futuresTradingSystem, optionsTradingSystem } from '@/assetclass/index';

interface RefactoredSystemsContextType {
  // Phase 18: Risk & Compliance
  riskCompliance: {
    advancedRiskManagement: typeof advancedRiskManagement;
    complianceManagement: typeof complianceManagement;
    portfolioGovernance: typeof portfolioGovernance;
  };
  
  // Phase 19: Cross-Platform
  crossPlatform: {
    mobileOptimization: typeof mobileOptimization;
    desktopApplication: typeof desktopApplication;
    apiIntegration: typeof apiIntegration;
  };
  
  // Phase 17: Asset Class
  assetClass: {
    stockTradingSystem: typeof stockTradingSystem;
    forexTradingSystem: typeof forexTradingSystem;
    futuresTradingSystem: typeof futuresTradingSystem;
    optionsTradingSystem: typeof optionsTradingSystem;
  };
  
  initialized: boolean;
  error: string | null;
}

const RefactoredSystemsContext = createContext<RefactoredSystemsContextType | undefined>(undefined);

export function RefactoredSystemsProvider({ children }: { children: ReactNode }) {
  const [initialized, setInitialized] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const initializeSystems = () => {
      try {
        console.log('� RefactoredSystemsContext: Initializing systems...');
        
        // Systems are already instantiated in their respective modules
        // We just need to make them available in the context
        console.log('✅ RefactoredSystemsContext: Systems ready');
        
        setInitialized(true);
        
        // Make systems available globally
        console.log('🔧 RefactoredSystemsContext: Setting global window access...');
        (window as any).__DASHBOARD2026_SYSTEMS__ = {
          riskCompliance: {
            advancedRiskManagement,
            complianceManagement,
            portfolioGovernance
          },
          crossPlatform: {
            mobileOptimization,
            desktopApplication,
            apiIntegration
          },
          assetClass: {
            stockTradingSystem,
            forexTradingSystem,
            futuresTradingSystem,
            optionsTradingSystem
          }
        };
        console.log('✅ RefactoredSystemsContext: Global access configured');
      } catch (err) {
        console.error('❌ RefactoredSystemsContext: Error initializing systems:', err);
        setError(err instanceof Error ? err.message : 'Unknown error');
      }
    };

    // Defer initialization to not block render
    const timeoutId = setTimeout(initializeSystems, 100);
    return () => clearTimeout(timeoutId);
  }, []);

  const value: RefactoredSystemsContextType = {
    riskCompliance: {
      advancedRiskManagement,
      complianceManagement,
      portfolioGovernance
    },
    crossPlatform: {
      mobileOptimization,
      desktopApplication,
      apiIntegration
    },
    assetClass: {
      stockTradingSystem,
      forexTradingSystem,
      futuresTradingSystem,
      optionsTradingSystem
    },
    initialized,
    error
  };

  return (
    <RefactoredSystemsContext.Provider value={value}>
      {children}
    </RefactoredSystemsContext.Provider>
  );
}

export function useRefactoredSystems(): RefactoredSystemsContextType {
  const context = useContext(RefactoredSystemsContext);
  if (context === undefined) {
    throw new Error('useRefactoredSystems must be used within a RefactoredSystemsProvider');
  }
  return context;
}

// Convenience hooks for each system module
export function useRiskCompliance() {
  const { riskCompliance } = useRefactoredSystems();
  return riskCompliance;
}

export function useCrossPlatform() {
  const { crossPlatform } = useRefactoredSystems();
  return crossPlatform;
}

export function useAssetClass() {
  const { assetClass } = useRefactoredSystems();
  return assetClass;
}