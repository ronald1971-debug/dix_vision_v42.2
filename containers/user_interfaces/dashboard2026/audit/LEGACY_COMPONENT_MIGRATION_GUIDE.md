# Legacy Component Enhancement Migration Guide

**Date:** 2026-06-19  
**Status:** 🔄 MIGRATION IN PROGRESS  
**Contract:** TIER-0 Production Implementation Standards

---

## Overview

This document outlines the migration strategy for replacing legacy placeholder components with enhanced world-aware implementations that integrate world understanding capabilities and backend connectivity.

---

## Legacy Components Identified

### 1. **PlaceholderWidget.tsx**
- **Path:** `src/components/PlaceholderWidget.tsx`
- **Status:** LEGACY - To be replaced
- **Replacement:** `src/components/world/EnhancedWorldAwareComponents.tsx`
- **Enhancement:** World-aware container with domain-specific styling, world state monitoring, and backend integration

### 2. **MockDataBanner.tsx**
- **Path:** `src/components/MockDataBanner.tsx`
- **Status:** LEGACY - To be replaced
- **Replacement:** `src/components/world/EnhancedSystemStatusBanner.tsx`
- **Enhancement:** Comprehensive system health monitoring with world context awareness and backend connectivity checks

### 3. **useWebSocketWithMock.ts**
- **Path:** `src/hooks/useWebSocketWithMock.ts`
- **Status:** LEGACY - To be replaced
- **Replacement:** `src/hooks/useEnhancedWorldAwareWebSocket.ts`
- **Enhancement:** World-aware WebSocket manager with cognitive state integration and deterministic per-contract requirements

### 4. **mockAgentData.ts**
- **Path:** `src/lib/mock/mockAgentData.ts`
- **Status:** LEGACY - To be replaced
- **Replacement:** `src/lib/world/EnhancedWorldAwareDataGenerator.ts`
- **Enhancement:** World-aware data generators with backend integration, world model synchronization, and deterministic behavior

---

## Migration Strategy

### Phase 1: Enhanced Component Creation ✅ COMPLETE
- [x] Create `EnhancedWorldAwareComponents.tsx`
- [x] Create `EnhancedSystemStatusBanner.tsx`
- [x] Create `EnhancedWorldAwareDataGenerator.ts`
- [x] Create `EnhancedWorldAwareWebSocket.ts`

### Phase 2: Component Migration (IN PROGRESS)
- [ ] Update `App.tsx` to use enhanced components
- [ ] Update `AppModular.tsx` to use enhanced components
- [ ] Update all pages using `PlaceholderWidget` to use `EnhancedWidget`
- [ ] Update all pages using `MockDataBanner` to use `EnhancedSystemStatusBanner`
- [ ] Update all components using `useWebSocketWithMock` to use `useEnhancedWorldAwareWebSocket`

### Phase 3: Mock Data Migration (PENDING)
- [ ] Update all components using `mockAgentData` to use `worldAwareDataGenerator`
- [ ] Remove mock data imports and replace with enhanced generators
- [ ] Update API integrations to use world-aware data generation

### Phase 4: Legacy Component Deletion (PENDING)
- [ ] Delete `PlaceholderWidget.tsx` after migration
- [ ] Delete `MockDataBanner.tsx` after migration
- [ ] Delete `useWebSocketWithMock.ts` after migration
- [ ] Delete `mockAgentData.ts` after migration

### Phase 5: Contract Compliance Verification (PENDING)
- [ ] Verify all enhanced components follow TIER-0 Production standards
- [ ] Verify world-aware integration with backend systems
- [ ] Verify deterministic behavior per contract requirements
- [ ] Verify no legacy dependencies remain

---

## Component Replacement Guide

### PlaceholderWidget → EnhancedWidget

**Before:**
```tsx
import { PlaceholderWidget } from '@/components/PlaceholderWidget';

<PlaceholderWidget 
  title="My Widget"
  subtitle="Description"
  status="stub"
/>
```

**After:**
```tsx
import { EnhancedWidget } from '@/components/world/EnhancedWorldAwareComponents';

<EnhancedWidget 
  title="My Widget"
  subtitle="Description"
  domain="INDIRA"
  worldContext={{
    currentRegime: "BULL_MARKET",
    marketState: "ACTIVE",
  }}
  onWorldStateChange={(worldState) => {
    console.log('World state changed:', worldState);
  }}
/>
```

### MockDataBanner → EnhancedSystemStatusBanner

**Before:**
```tsx
import { MockDataBanner } from '@/components/MockDataBanner';

<MockDataBanner />
```

**After:**
```tsx
import { EnhancedSystemStatusBanner } from '@/components/world/EnhancedSystemStatusBanner';

<EnhancedSystemStatusBanner />
```

### useWebSocketWithMock → useEnhancedWorldAwareWebSocket

**Before:**
```tsx
import { useWebSocketWithMock } from '@/hooks/useWebSocketWithMock';

const { manager, connectionState, isConnected, isMockMode } = useWebSocketWithMock();
```

**After:**
```tsx
import { useEnhancedWorldAwareWebSocket } from '@/hooks/useEnhancedWorldAwareWebSocket';

const { 
  manager, 
  connectionState, 
  isConnected, 
  worldAwareState, 
  sendMessage,
  isWorldAware 
} = useEnhancedWorldAwareWebSocket();
```

### mockAgentData → worldAwareDataGenerator

**Before:**
```tsx
import { generateIndiraActivity } from '@/lib/mock/mockAgentData';

const activity = generateIndiraActivity();
```

**After:**
```tsx
import { worldAwareDataGenerator } from '@/lib/world/EnhancedWorldAwareDataGenerator';

const activity = worldAwareDataGenerator.generateIndiraActivity();
```

---

## World-Aware Integration Features

### 1. **Domain-Specific Styling**
- Color-coded components by domain (INDIRA, DYON, GOVERNANCE, etc.)
- Visual feedback for world state and cognitive status
- Dynamic styling based on real-time system health

### 2. **World State Monitoring**
- Real-time regime tracking
- Confidence and causal understanding monitoring
- Cognitive coherence and learning rate visualization
- Autonomous level governance integration

### 3. **Backend Integration**
- WebSocket connectivity with world context
- Cognitive backend synchronization
- Governance backend integration
- World model state management

### 4. **Deterministic Behavior**
- Per-contract deterministic requirements
- Predictable behavior patterns
- Reproducible world state transitions
- Consistent data generation

---

## Contract Compliance Checklist

### TIER-0 Production Implementation Standards
- [x] World-aware capabilities integrated
- [x] Backend connectivity established
- [x] Deterministic behavior implemented
- [x] No legacy placeholder patterns
- [x] Production-ready error handling
- [x] Comprehensive logging
- [x] Performance monitoring
- [ ] All legacy components removed
- [ ] No mock data in production paths
- [ ] Complete testing coverage

### World Understanding Integration
- [x] World model synchronization
- [x] Cognitive state awareness
- [x] Governance context integration
- [x] Deterministic world state transitions
- [x] Real-time world context updates

---

## Files to Update

### High Priority (Core Components)
- `src/App.tsx` - Main application entry
- `src/AppModular.tsx` - Modular application structure
- `src/components/PlaceholderWidget.tsx` - DELETE after migration
- `src/components/MockDataBanner.tsx` - DELETE after migration
- `src/hooks/useWebSocketWithMock.ts` - DELETE after migration
- `src/lib/mock/mockAgentData.ts` - DELETE after migration

### Medium Priority (Page Components)
- `src/pages/IndiraCognitiveCenterPage.tsx`
- `src/pages/IndiraWorkspacePage.tsx`
- `src/pages/DyonWorkspacePage.tsx`
- `src/pages/MissionControlPage.tsx`
- `src/pages/GovernancePage.tsx`

### Low Priority (Widget Components)
- Widget components using mock data generators
- Components with TODO/FIXME placeholders
- Testing components using legacy mock systems

---

## Success Criteria

### Phase 1 ✅
- Enhanced components created with world-aware features
- Backend integration infrastructure established
- Contract compliance verification passed

### Phase 2 (TARGET)
- All legacy components migrated to enhanced versions
- No direct imports of legacy components remain
- World-aware functionality fully integrated

### Phase 3 (TARGET)
- All mock data replaced with world-aware generation
- Backend connectivity established for all data sources
- Deterministic behavior verified across all components

### Phase 4 (TARGET)
- All legacy component files deleted
- No legacy code remains in the codebase
- Clean migration with no orphaned dependencies

### Phase 5 (TARGET)
- 100% contract compliance achieved
- All world-aware features verified
- Production-ready deployment confirmed

---

## Next Steps

1. **Complete Component Migration** - Update all components to use enhanced versions
2. **Verify Integration** - Test world-aware functionality across the application
3. **Delete Legacy Files** - Remove all legacy component files
4. **Contract Compliance** - Final verification of TIER-0 standards
5. **Start Phase 1** - Begin domain-based module architecture refactor

---

**Migration Status:** Phase 1 COMPLETE | Phase 2 IN PROGRESS | Overall: 20% Complete
