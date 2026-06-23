/**
 * GOVERNANCE Domain Store
 * 
 * Manages GOVERNANCE-specific state including approval workflows,
 * audit trails, policy compliance, and risk monitoring.
 */

import { create } from 'zustand';
import { devtools, persist } from 'zustand/middleware';

// ============================================================================
// GOVERNANCE Domain State Types
// ============================================================================

interface GovernanceState {
  // Approval Workflows
  approvalQueue: {
    id: string;
    type: string;
    status: 'pending' | 'approved' | 'rejected';
    requester: string;
    timestamp: number;
  }[];
  
  // Audit Trails
  auditLogs: {
    id: string;
    action: string;
    user: string;
    timestamp: number;
    details: any;
  }[];
  
  // Policy Compliance
  policyViolations: {
    id: string;
    policy: string;
    severity: 'low' | 'medium' | 'high' | 'critical';
    description: string;
    timestamp: number;
  }[];
  
  // Risk Monitoring
  riskMetrics: {
    overallRisk: number;
    complianceScore: number;
    activeAlerts: number;
    lastAssessment: number;
  } | null;
  
  // Strategy Registry
  strategyStates: {
    [strategyId: string]: {
      state: 'proposed' | 'canary' | 'live' | 'retired' | 'failed';
      promotionStage: string;
      lastUpdate: number;
    };
  };
  
  // UI State
  isLoading: boolean;
  error: string | null;
  selectedApproval: string | null;
}

interface GovernanceActions {
  // Approval Actions
  addApprovalItem: (item: GovernanceState['approvalQueue'][0]) => void;
  updateApprovalStatus: (id: string, status: GovernanceState['approvalQueue'][0]['status']) => void;
  removeApprovalItem: (id: string) => void;
  
  // Audit Actions
  addAuditLog: (log: GovernanceState['auditLogs'][0]) => void;
  updateAuditLog: (id: string, details: any) => void;
  
  // Compliance Actions
  addPolicyViolation: (violation: GovernanceState['policyViolations'][0]) => void;
  resolvePolicyViolation: (id: string) => void;
  
  // Risk Actions
  setRiskMetrics: (metrics: GovernanceState['riskMetrics']) => void;
  
  // Strategy Actions
  updateStrategyState: (strategyId: string, state: string) => void;
  setStrategyPromotionStage: (strategyId: string, stage: string) => void;
  
  // UI Actions
  setLoading: (loading: boolean) => void;
  setError: (error: string | null) => void;
  setSelectedApproval: (id: string | null) => void;
  reset: () => void;
}

type GovernanceStore = GovernanceState & GovernanceActions;

// ============================================================================
// GOVERNANCE Store Implementation
// ============================================================================

export const useGovernanceStore = create<GovernanceStore>()(
  devtools(
    persist(
      (set) => ({
        // Initial State
        approvalQueue: [],
        auditLogs: [],
        policyViolations: [],
        riskMetrics: null,
        strategyStates: {},
        isLoading: false,
        error: null,
        selectedApproval: null,
        
        // Approval Actions
        addApprovalItem: (item) => set((state) => ({
          approvalQueue: [...state.approvalQueue, item],
        })),
        
        updateApprovalStatus: (id, status) => set((state) => ({
          approvalQueue: state.approvalQueue.map(item =>
            item.id === id ? { ...item, status, timestamp: Date.now() } : item
          ),
        })),
        
        removeApprovalItem: (id) => set((state) => ({
          approvalQueue: state.approvalQueue.filter(item => item.id !== id),
        })),
        
        // Audit Actions
        addAuditLog: (log) => set((state) => ({
          auditLogs: [...state.auditLogs, log],
        })),
        
        updateAuditLog: (id, details) => set((state) => ({
          auditLogs: state.auditLogs.map(log =>
            log.id === id ? { ...log, details: { ...log.details, ...details } } : log
          ),
        })),
        
        // Compliance Actions
        addPolicyViolation: (violation) => set((state) => ({
          policyViolations: [...state.policyViolations, violation],
        })),
        
        resolvePolicyViolation: (id) => set((state) => ({
          policyViolations: state.policyViolations.filter(v => v.id !== id),
        })),
        
        // Risk Actions
        setRiskMetrics: (metrics) => set({ riskMetrics: metrics }),
        
        // Strategy Actions
        updateStrategyState: (strategyId, newState) => set((state) => ({
          strategyStates: {
            ...state.strategyStates,
            [strategyId]: {
              ...(state.strategyStates[strategyId] as any || {}),
              state: newState,
              lastUpdate: Date.now(),
            },
          },
        })),
        
        setStrategyPromotionStage: (strategyId, stage) => set((state) => ({
          strategyStates: {
            ...state.strategyStates,
            [strategyId]: {
              ...(state.strategyStates[strategyId] as any || {}),
              promotionStage: stage,
              lastUpdate: Date.now(),
            },
          },
        })),
        
        // UI Actions
        setLoading: (loading) => set({ isLoading: loading }),
        setError: (error) => set({ error }),
        setSelectedApproval: (id) => set({ selectedApproval: id }),
        
        reset: () => set({
          approvalQueue: [],
          auditLogs: [],
          policyViolations: [],
          riskMetrics: null,
          strategyStates: {},
          isLoading: false,
          error: null,
          selectedApproval: null,
        }),
      }),
      {
        name: 'governance-store',
        partialize: (state) => ({
          // Persist critical governance data
          approvalQueue: state.approvalQueue,
          auditLogs: state.auditLogs.slice(-100), // Keep last 100 logs
          policyViolations: state.policyViolations.slice(-50), // Keep last 50 violations
          strategyStates: state.strategyStates,
        }),
      }
    )
  )
);

// ============================================================================
// Selectors
// ============================================================================

export const useGovernanceApprovals = () => {
  return useGovernanceStore((state) => ({
    approvalQueue: state.approvalQueue,
    selectedApproval: state.selectedApproval,
    addApprovalItem: state.addApprovalItem,
    updateApprovalStatus: state.updateApprovalStatus,
    removeApprovalItem: state.removeApprovalItem,
    setSelectedApproval: state.setSelectedApproval,
  }));
};

export const useGovernanceAudit = () => {
  return useGovernanceStore((state) => ({
    auditLogs: state.auditLogs,
    addAuditLog: state.addAuditLog,
    updateAuditLog: state.updateAuditLog,
  }));
};

export const useGovernanceCompliance = () => {
  return useGovernanceStore((state) => ({
    policyViolations: state.policyViolations,
    riskMetrics: state.riskMetrics,
    addPolicyViolation: state.addPolicyViolation,
    resolvePolicyViolation: state.resolvePolicyViolation,
    setRiskMetrics: state.setRiskMetrics,
  }));
};

export const useGovernanceStrategies = () => {
  return useGovernanceStore((state) => ({
    strategyStates: state.strategyStates,
    updateStrategyState: state.updateStrategyState,
    setStrategyPromotionStage: state.setStrategyPromotionStage,
  }));
};