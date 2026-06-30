# Memory Management Unification Plan

## Overview
This document outlines the consolidation of the duplicated memory/OOM patch ecosystem as specified in P0 #2.

## Current State (Duplicated Memory Systems)

### Memory Management Files
1. **session_restore_safety_wrapper.py** - IDE session restoration safety wrapper
2. **memory_monitor.py** - Memory monitoring and leak detection utilities  
3. **optimize_wsl_docker_memory.ps1** - WSL/Docker memory optimization script
4. **VIRTUAL_MEMORY_REPORT.md** - Virtual memory analysis report

### Memory Modules Across Containers
- **containers/system_core/state/memory/** - State memory system
- **containers/system_core/state/memory_tensor/** - Tensor memory management
- **containers/user_interfaces/desktop_agent/memory/** - Desktop agent memory
- **containers/infrastructure/shared_infrastructure/unified_memory_framework.py** - Unified memory framework
- **Multiple development alternatives** - Various memory implementations

### Issues with Current State
- **Fragmented memory management**: 80+ memory-related files
- **Inconsistent OOM handling**: Different approaches across components
- **Duplicate functionality**: Multiple memory monitors and leak detectors
- **Platform-specific patches**: WSL/Docker specific scripts separate from core logic
- **No central coordination**: Each component manages memory independently

## Target State (Unified Memory Management)

### Central Memory Manager
**memory_manager.py** - Single source of truth for memory management

```python
class UnifiedMemoryManager:
    """Centralized memory management for DIX VISION system"""
    
    def __init__(self):
        self.monitors = []
        self.policies = {}
        self.emergency_handlers = []
        
    def register_monitor(self, monitor)
    def register_policy(self, policy)
    def handle_oom(self, emergency_handler)
    def get_memory_status(self)
    def force_cleanup(self)
```

### Unified Memory Policies
- **Memory monitoring**: Single monitoring system for all components
- **OOM prevention**: Consistent OOM handling across the system
- **Leak detection**: Unified leak detection and reporting
- **Resource allocation**: Centralized resource allocation policies
- **Platform abstraction**: WSL/Docker/native unified under single interface

## Migration Strategy

### Phase 1: Analysis (Current)
- [x] Identify all memory-related files
- [ ] Document current memory management approaches
- [ ] Identify duplicated functionality
- [ ] Map dependencies between memory systems

### Phase 2: Unification
- [ ] Create unified memory manager
- [ ] Consolidate monitoring utilities
- [ ] Implement platform abstraction layer
- [ ] Create unified OOM handling

### Phase 3: Integration
- [ ] Update containers to use unified manager
- [ ] Remove duplicate memory files
- [ ] Update platform-specific scripts
- [ ] Test memory management across modes

### Phase 4: Cleanup
- [ ] Remove old memory files
- [ ] Update documentation
- [ ] Archive removed code

## Unified Memory Manager Design

### Core Components

#### 1. Memory Monitor
```python
class MemoryMonitor:
    """Unified memory monitoring"""
    
    def __init__(self):
        self.process = psutil.Process()
        self.baseline = None
        self.peak = 0
        self.samples = []
        
    def start_monitoring(self)
    def check_memory(self) -> MemoryStatus
    def detect_leak(self) -> bool
    def get_summary(self) -> MemorySummary
```

#### 2. Memory Policy Engine
```python
class MemoryPolicyEngine:
    """Memory policy enforcement"""
    
    def __init__(self):
        self.policies = []
        self.emergency_handlers = []
        
    def register_policy(self, policy: MemoryPolicy)
    def enforce_policies(self) -> PolicyResult
    def trigger_emergency(self, handler: EmergencyHandler)
```

#### 3. Platform Abstraction
```python
class PlatformMemoryAdapter:
    """Platform-specific memory operations"""
    
    def __init__(self):
        self.platform = self.detect_platform()
        
    def detect_platform(self) -> Platform
    def get_memory_limits(self) -> MemoryLimits
    def set_memory_limits(self, limits: MemoryLimits)
    def optimize_memory(self) -> bool
```

#### 4. OOM Handler
```python
class OOMHandler:
    """Out-of-memory handling"""
    
    def __init__(self):
        self.emergency_procedures = []
        self.cleanup_handlers = []
        
    def detect_oom(self) -> bool
    def handle_oom(self) -> OOMResult
    def register_emergency_procedure(self, procedure)
    def register_cleanup_handler(self, handler)
```

### Memory Policies

#### Standard Policies
1. **Memory Warning Threshold**: 70% system memory
2. **Memory Critical Threshold**: 85% system memory
3. **Process Memory Limit**: 1GB per process
4. **Disk Space Warning**: 5GB free minimum
5. **Leak Detection Threshold**: 200MB increase

#### Emergency Procedures
1. **Force garbage collection**
2. **Clear Python caches**
3. **Terminate non-critical processes**
4. **Enable emergency memory mode**
5. **Trigger graceful shutdown**

## Platform Abstraction

### Windows/Native
```python
class WindowsMemoryAdapter(PlatformMemoryAdapter):
    def optimize_memory(self):
        # Windows-specific optimization
        # Empty working sets, etc.
```

### WSL/Docker
```python
class WSLMemoryAdapter(PlatformMemoryAdapter):
    def optimize_memory(self):
        # WSL-specific optimization
        # Update .wslconfig, etc.
```

### Linux/Native
```python
class LinuxMemoryAdapter(PlatformMemoryAdapter):
    def optimize_memory(self):
        # Linux-specific optimization
        # ulimit, cgroups, etc.
```

## Integration Points

### Container-Level Integration
- **Bootstrap System**: Initialize memory manager during system startup
- **State System**: Use unified memory manager for state operations
- **Desktop Agent**: Use unified memory manager for agent operations
- **Docker Stack**: Use unified memory manager for container operations

### Mode-Specific Integration
- **Desktop Mode**: Standard memory management
- **Portable Mode**: Per-user memory directory management
- **Docker Mode**: Container memory limit management
- **Development Mode**: Debug memory monitoring

## File Consolidation Map

### Files to Remove
- `session_restore_safety_wrapper.py` → Integrated into unified manager
- `memory_monitor.py` → Consolidated into unified monitor
- `optimize_wsl_dsl_docker_memory.ps1` → Platform adapter
- Duplicate memory modules in development alternatives
- Legacy memory files in system_core

### Files to Keep
- `containers/infrastructure/shared_infrastructure/unified_memory_framework.py` → Enhance and extend
- Core memory modules in system_core/state/memory/ → Standardize interface
- Core memory modules in system_core/state/memory_tensor/ → Standardize interface

## Testing Plan

### Unit Tests
- [ ] Memory monitor accuracy
- [ ] Policy enforcement correctness
- [ ] Platform adapter functionality
- [ ] OOM handler effectiveness

### Integration Tests
- [ ] Bootstrap integration
- [ ] Container memory management
- [ ] Platform-specific operations
- [ ] Emergency procedure execution

### Performance Tests
- [ ] Memory overhead of unified system
- [ ] Leak detection accuracy
- [ ] Cleanup effectiveness
- [ ] Cross-platform performance

## Benefits

### Technical Benefits
- **Single source of truth**: One memory management system
- **Consistent behavior**: All components use same memory policies
- **Better monitoring**: Unified view of system memory usage
- **Easier debugging**: Centralized memory logging and alerts
- **Simpler maintenance**: One system to update and maintain

### Operational Benefits
- **Predictable behavior**: Consistent memory handling across deployments
- **Better resource utilization**: Optimized memory allocation
- **Improved stability**: Centralized OOM prevention
- **Easier troubleshooting**: Single place to check memory issues
- **Platform independence**: Works consistently across platforms

## Migration Path

### Step 1: Create Unified Manager
- Implement core memory manager
- Implement platform adapters
- Implement policy engine
- Implement OOM handler

### Step 2: Integrate with Bootstrap
- Add memory manager initialization to bootstrap
- Add memory health checks to startup
- Add memory monitoring to runtime
- Add memory cleanup to shutdown

### Step 3: Update Containers
- Update state/memory modules to use unified manager
- Update desktop agent to use unified manager
- Update development alternatives to use unified manager
- Remove duplicate memory implementations

### Step 4: Remove Old Files
- Remove session_restore_safety_wrapper.py
- Remove memory_monitor.py
- Remove optimize_wsl_docker_memory.ps1
- Remove duplicate memory modules
- Update imports and references

### Step 5: Documentation
- Update memory management documentation
- Create unified memory manager guide
- Update troubleshooting guides
- Update development documentation

## Rollback Plan

If issues arise during migration:
1. Keep old memory files during Phase 1-2
2. Revert to old memory management by disabling unified manager
3. Restore duplicate memory files if needed
4. Document issues and fix before retrying migration

## Success Criteria

### Technical Criteria
- [ ] All memory management uses unified system
- [ ] No memory management functionality lost
- [ ] Memory overhead is minimal
- [ ] OOM handling improved or equivalent
- [ ] Platform-specific optimizations preserved

### Operational Criteria
- [ ] System stability maintained or improved
- [ ] Memory usage reduced or equivalent
- [ ] OOM errors reduced
- [ ] Platform consistency achieved
- [ ] Troubleshooting simplified

## Timeline

- **Phase 1**: 2-3 days (analysis and documentation)
- **Phase 2**: 3-4 days (unification and implementation)
- **Phase 3**: 3-4 days (integration and testing)
- **Phase 4**: 1-2 days (cleanup and documentation)

**Total**: 9-13 days for complete memory unification

## Next Steps

1. Complete analysis of current memory systems
2. Design unified memory manager architecture
3. Begin implementation of core components
4. Create platform abstraction layer
5. Integrate with bootstrap system