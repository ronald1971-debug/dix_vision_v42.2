/**
 * EXECUTION Domain Store
 * 
 * Manages EXECUTION-specific state including orders, positions,
 * execution metrics, and order flow analysis.
 */

import { create } from 'zustand';
import { devtools, persist } from 'zustand/middleware';

// ============================================================================
// EXECUTION Domain State Types
// ============================================================================

interface ExecutionState {
  // Orders
  orders: {
    id: string;
    symbol: string;
    side: 'buy' | 'sell';
    type: string;
    quantity: number;
    price: number;
    status: 'pending' | 'open' | 'filled' | 'cancelled' | 'rejected';
    timestamp: number;
  }[];
  
  // Positions
  positions: {
    id: string;
    symbol: string;
    quantity: number;
    entryPrice: number;
    currentPrice: number;
    unrealizedPnL: number;
    side: 'long' | 'short';
  }[];
  
  // Order Flow Metrics
  orderFlowMetrics: {
    aggressorRatio: number;
    bidAskImbalance: number;
    tradeIntensity: number;
    volumeProfile: any;
  } | null;
  
  // Execution Performance
  executionMetrics: {
    fillRate: number;
    slippage: number;
    latency: number;
    successRate: number;
  } | null;
  
  // Trading State
  tradingStatus: {
    mode: 'manual' | 'automated' | 'hybrid';
    isActive: boolean;
    permissions: string[];
  };
  
  // UI State
  isLoading: boolean;
  error: string | null;
  selectedOrder: string | null;
  selectedPosition: string | null;
}

interface ExecutionActions {
  // Order Actions
  addOrder: (order: ExecutionState['orders'][0]) => void;
  updateOrder: (id: string, updates: Partial<ExecutionState['orders'][0]>) => void;
  cancelOrder: (id: string) => void;
  
  // Position Actions
  addPosition: (position: ExecutionState['positions'][0]) => void;
  updatePosition: (id: string, updates: Partial<ExecutionState['positions'][0]>) => void;
  closePosition: (id: string) => void;
  
  // Order Flow Actions
  setOrderFlowMetrics: (metrics: ExecutionState['orderFlowMetrics']) => void;
  updateOrderFlowMetrics: (updates: Partial<ExecutionState['orderFlowMetrics']>) => void;
  
  // Execution Actions
  setExecutionMetrics: (metrics: ExecutionState['executionMetrics']) => void;
  
  // Trading State Actions
  setTradingMode: (mode: ExecutionState['tradingStatus']['mode']) => void;
  setTradingActive: (isActive: boolean) => void;
  updatePermissions: (permissions: string[]) => void;
  
  // UI Actions
  setLoading: (loading: boolean) => void;
  setError: (error: string | null) => void;
  setSelectedOrder: (id: string | null) => void;
  setSelectedPosition: (id: string | null) => void;
  reset: () => void;
}

type ExecutionStore = ExecutionState & ExecutionActions;

// ============================================================================
// EXECUTION Store Implementation
// ============================================================================

export const useExecutionStore = create<ExecutionStore>()(
  devtools(
    persist(
      (set) => ({
        // Initial State
        orders: [],
        positions: [],
        orderFlowMetrics: null,
        executionMetrics: null,
        tradingStatus: {
          mode: 'manual',
          isActive: false,
          permissions: [],
        },
        isLoading: false,
        error: null,
        selectedOrder: null,
        selectedPosition: null,
        
        // Order Actions
        addOrder: (order) => set((state) => ({
          orders: [...state.orders, order],
        })),
        
        updateOrder: (id, updates) => set((state) => ({
          orders: state.orders.map(order =>
            order.id === id ? { ...order, ...updates, timestamp: Date.now() } : order
          ),
        })),
        
        cancelOrder: (id) => set((state) => ({
          orders: state.orders.map(order =>
            order.id === id ? { ...order, status: 'cancelled', timestamp: Date.now() } : order
          ),
        })),
        
        // Position Actions
        addPosition: (position) => set((state) => ({
          positions: [...state.positions, position],
        })),
        
        updatePosition: (id, updates) => set((state) => ({
          positions: state.positions.map(pos =>
            pos.id === id ? { ...pos, ...updates } : pos
          ),
        })),
        
        closePosition: (id) => set((state) => ({
          positions: state.positions.filter(pos => pos.id !== id),
        })),
        
        // Order Flow Actions
        setOrderFlowMetrics: (metrics) => set({ orderFlowMetrics: metrics }),
        updateOrderFlowMetrics: (updates) => set((state) => ({
          orderFlowMetrics: state.orderFlowMetrics ? {
            ...state.orderFlowMetrics,
            ...updates
          } : null
        })),
        
        // Execution Actions
        setExecutionMetrics: (metrics) => set({ executionMetrics: metrics }),
        
        // Trading State Actions
        setTradingMode: (mode) => set((state) => ({
          tradingStatus: { ...state.tradingStatus, mode },
        })),
        
        setTradingActive: (isActive) => set((state) => ({
          tradingStatus: { ...state.tradingStatus, isActive },
        })),
        
        updatePermissions: (permissions) => set((state) => ({
          tradingStatus: { ...state.tradingStatus, permissions },
        })),
        
        // UI Actions
        setLoading: (loading) => set({ isLoading: loading }),
        setError: (error) => set({ error }),
        setSelectedOrder: (id) => set({ selectedOrder: id }),
        setSelectedPosition: (id) => set({ selectedPosition: id }),
        
        reset: () => set({
          orders: [],
          positions: [],
          orderFlowMetrics: null,
          executionMetrics: null,
          tradingStatus: {
            mode: 'manual',
            isActive: false,
            permissions: [],
          },
          isLoading: false,
          error: null,
          selectedOrder: null,
          selectedPosition: null,
        }),
      }),
      {
        name: 'execution-store',
        partialize: (state) => ({
          // Persist critical execution data
          orders: state.orders.filter(o => o.status === 'open' || o.status === 'pending'),
          positions: state.positions,
          tradingStatus: state.tradingStatus,
        }),
      }
    )
  )
);

// ============================================================================
// Selectors
// ============================================================================

export const useExecutionOrders = () => {
  return useExecutionStore((state) => ({
    orders: state.orders,
    selectedOrder: state.selectedOrder,
    addOrder: state.addOrder,
    updateOrder: state.updateOrder,
    cancelOrder: state.cancelOrder,
    setSelectedOrder: state.setSelectedOrder,
  }));
};

export const useExecutionPositions = () => {
  return useExecutionStore((state) => ({
    positions: state.positions,
    selectedPosition: state.selectedPosition,
    addPosition: state.addPosition,
    updatePosition: state.updatePosition,
    closePosition: state.closePosition,
    setSelectedPosition: state.setSelectedPosition,
  }));
};

export const useExecutionMetrics = () => {
  return useExecutionStore((state) => ({
    orderFlowMetrics: state.orderFlowMetrics,
    executionMetrics: state.executionMetrics,
    setOrderFlowMetrics: state.setOrderFlowMetrics,
    setExecutionMetrics: state.setExecutionMetrics,
  }));
};

export const useExecutionStatus = () => {
  return useExecutionStore((state) => ({
    tradingStatus: state.tradingStatus,
    setTradingMode: state.setTradingMode,
    setTradingActive: state.setTradingActive,
    updatePermissions: state.updatePermissions,
  }));
};