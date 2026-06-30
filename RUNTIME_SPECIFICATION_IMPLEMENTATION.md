# DIX VISION Runtime Specification Implementation

## Overview

This document describes the implementation of the DIX VISION Runtime Specification as defined in the authoritative runtime specification. The system has been transformed from a collection of scripts into a formal service-based runtime with a single orchestrated lifecycle.

## Core Principle

The system is NOT a collection of scripts. It is a service-based runtime with a single orchestrated lifecycle.

**Lifecycle:** BOOT → REGISTER → INITIALIZE → RUN → MONITOR → RECOVER → SHUTDOWN

## Single Source of Truth (Boot Contract)

### Authoritative Entrypoint

**File:** `dix.py` - Runtime Orchestrator Kernel

This is the ONLY logical truth for system behavior. Even if multiple scripts exist, `dix.py` is the authoritative entry point.

**Role of dix.py:**
- Runtime Orchestrator Kernel (NOT a feature file)
- Load config
- Initialize runtime engine
- Register services
- Start event loop

**Invalid Entrypoint Behavior (Fixed):**
The following are NO LONGER allowed to define system behavior:
- ❌ .bat launch scripts (now wrappers only)
- ❌ .ps1 memory fixes (replaced by runtime memory manager)
- ❌ docker-compose startup order logic (now handled by orchestrator)
- ❌ dashboard startup scripts (now service-based)

## Service Model (New Unified Contract)

### Service Interface (MANDATORY)

Every subsystem conforms to:

```python
class Service:
    def init(self, event_bus: EventBus, config: Dict[str, Any]) -> bool:
        """Initialize the service with event bus and config"""
        
    def start(self) -> bool:
        """Start the service"""
        
    def stop(self) -> bool:
        """Stop the service"""
        
    def health(self) -> ServiceHealth:
        """Get service health information"""
```

### Service Types in System

**CORE SERVICES:**
- ConfigService - Configuration management
- MemoryService - Memory monitoring and management
- ValidationService - Contract validation (passive observer)

**INFRA SERVICES:**
- BackendService - Python backend server
- DashboardService - React dashboard
- DockerService - Docker container management

**SUPPORT SERVICES:**
- EventBus - Event communication system
- FailureHandler - Failure detection and recovery

### Service Rule

No module is allowed to run "freely" outside the service model. All components must conform to the Service interface.

## Event Bus (Formal Communication System)

### Event Bus Rule

All communication MUST pass through the EventBus.

### Event Structure

```python
{
    "source": "memory_monitor",
    "type": "MEMORY_WARNING",
    "payload": {},
    "timestamp": ""
}
```

### Event Types

**Memory Events:**
- MEMORY_WARNING - Memory pressure warning
- MEMORY_CRITICAL - Critical memory pressure
- MEMORY_RECOVERY - Memory recovery completed
- OOM_PREVENTION - OOM prevention action taken

**AI Runtime Events:**
- AI_INIT - AI engine initialization
- AI_START - AI engine started
- AI_STOP - AI engine stopped
- AI_STATE_UPDATE - AI state change
- AI_DECISION - AI decision made
- AI_ERROR - AI engine error

**Execution Events:**
- EXECUTION_START - Execution started
- EXECUTION_COMPLETE - Execution completed
- EXECUTION_ERROR - Execution error

**Dashboard Events:**
- DASHBOARD_READY - Dashboard ready for connections
- DASHBOARD_ERROR - Dashboard error

**System Events:**
- SYSTEM_BOOT - System boot completed
- SYSTEM_SHUTDOWN - System shutdown initiated
- SYSTEM_DEGRADED - System in degraded state
- SYSTEM_RECOVERING - System recovering

**Validation Events:**
- CONTRACT_VIOLATION - Contract violation detected
- VALIDATION_ERROR - Validation error

**Service Events:**
- SERVICE_START - Service started
- SERVICE_STOP - Service stopped
- SERVICE_CRASH - Service crashed
- SERVICE_HEALTH - Service health status

### Event Flows

**AI Runtime → Dashboard:**
- State updates
- Inference results
- Execution logs

**Memory System → Runtime:**
- Pressure alerts
- OOM prevention signals

**Validation System → All:**
- Contract violation signals

## AI Runtime Contract

### AI Lifecycle

INIT → LOAD MEMORY → RESTORE SESSION → RUN LOOP → UPDATE MEMORY → REPORT STATE

### AI Rules

- AI cannot bypass memory system
- AI cannot directly write to disk state
- AI must emit events for all decisions
- AI must be stateless at computation level, stateful via memory layer

## Memory System Contract

### Memory Rules

- Single memory authority module
- All memory reads go through API
- All writes are versioned
- Memory pressure must emit events

### Memory States

- NORMAL - Normal memory usage
- WARNING - Memory pressure warning
- CRITICAL - Critical memory pressure
- RECOVERY_MODE - Memory recovery in progress

### OOM Handling Rule

Instead of scripts:
- ❌ memory_optimization.ps1
- ❌ targeted_oom_fix.py

Now MemoryService handles:
- ✔ Pre-emptive cleanup
- ✔ Cache eviction
- ✔ State compression
- ✔ Service throttling

## Dashboard Contract

### Dashboard as Client

The dashboard becomes a client of the runtime, NOT a controller.

### Dashboard Rules

- Dashboard NEVER starts backend logic
- Dashboard ONLY subscribes to EventBus
- Dashboard NEVER modifies system state directly

### Data Flow

Runtime → EventBus → Dashboard UI

## Validation Layer

### Validation Rule

Validation is:
- ✔ A passive observer service

NOT:
- ❌ A controller
- ❌ A fixer
- ❌ A startup dependency

## Failure Handling Model

### Failure Pipeline

Detect → Classify → Emit Event → Recover → Verify

### Failure Types

- MEMORY_FAILURE - Memory-related failures
- SERVICE_CRASH - Service crashes
- CONTRACT_VIOLATION - Contract violations
- RUNTIME_DESYNC - Runtime state desynchronization

### Recovery Strategies

- MemoryRecoveryStrategy - Memory cleanup and optimization
- ServiceRestartStrategy - Automatic service restart
- ContractViolationStrategy - Manual intervention required
- RuntimeDesyncStrategy - State resynchronization

## System State Model

### System States

- BOOTING - System initializing
- RUNNING - System operational
- DEGRADED - System in degraded state
- RECOVERING - System recovering from failure
- STOPPED - System stopped

## Startup Sequence (Final Contract)

### Correct Order

1. Load Config
2. Initialize EventBus
3. Start MemoryService
4. Start Core Runtime
5. Restore Session
6. Start AI Engine
7. Start Execution Engine
8. Start Dashboard (last)
9. Start Monitoring

## Problems Eliminated

This specification removes:

- ❌ Random startup behavior
- ❌ Multiple entrypoints chaos
- ❌ OS-level memory hacks
- ❌ Dashboard coupling
- ❌ Unclear service boundaries
- ❌ Implicit communication

## What We Now Have

A formal runtime constitution for DIX Vision v42.2:

- ✔ Behavioral rules
- ✔ Execution order
- ✔ Service contracts
- ✔ System boundaries
- ✔ Failure model

## Implementation Files

### Core Runtime Files

- **dix.py** - Runtime Orchestrator Kernel (authoritative entry point)
- **event_bus.py** - Formal event communication system
- **service_manager.py** - Service lifecycle management
- **failure_handler.py** - Failure detection and recovery
- **memory_manager.py** - Unified memory management
- **config_manager.py** - Centralized configuration
- **platform_abstraction.py** - Cross-platform normalization

### Configuration

- **config/system_config.yaml** - System configuration

### Legacy Files (Updated)

- **bootstrap.py** - Updated to use new runtime (backward compatibility)
- **start_dix_vision.bat** - Updated to use service manager
- **memory_monitor.py** - Updated to use unified memory manager
- **session_restore_safety_wrapper.py** - Updated to use unified memory manager
- **optimize_wsl_docker_memory.ps1** - Updated to use platform abstraction

## Usage

### Authoritative Startup

```bash
# Use the Runtime Orchestrator Kernel
python dix.py
```

### Legacy Startup (Backward Compatible)

```bash
# Old scripts still work but call the new runtime
python bootstrap.py desktop
python bootstrap.py dashboard
```

### Service-Based Orchestration

```bash
# Use service manager for direct service control
python -c "from service_manager import get_service_manager; sm = get_service_manager(); sm.start_all()"
```

## Architecture Diagram

```
dix.py (Runtime Orchestrator Kernel)
    │
    ├── Config Manager
    │   └── config/system_config.yaml
    │
    ├── Event Bus
    │   ├── Memory Events
    │   ├── Service Events
    │   ├── System Events
    │   └── Validation Events
    │
    ├── Service Manager
    │   ├── ConfigService
    │   ├── MemoryService
    │   ├── ValidationService
    │   ├── BackendService
    │   ├── DashboardService
    │   └── DockerService
    │
    ├── Failure Handler
    │   ├── Memory Recovery Strategy
    │   ├── Service Restart Strategy
    │   ├── Contract Violation Strategy
    │   └── Runtime Desync Strategy
    │
    └── Platform Abstraction
        ├── Windows Adapter
        ├── Linux Adapter
        ├── WSL Adapter
        └── macOS Adapter
```

## Event Flow Examples

### Memory Pressure Event

```
MemoryService → EventBus → FailureHandler → MemoryRecoveryStrategy → EventBus → All Services
```

### Service Crash Event

```
Service → EventBus → FailureHandler → ServiceRestartStrategy → EventBus → Orchestrator
```

### Contract Violation Event

```
ValidationService → EventBus → FailureHandler → ContractViolationStrategy → EventBus → Manual Review
```

## Testing the Runtime

### Test Runtime Startup

```bash
python dix.py
```

### Test Event Bus

```python
from event_bus import get_event_bus, Event

bus = get_event_bus()
event = Event("test", "TEST_EVENT", {"message": "test"})
bus.publish(event)
```

### Test Service Manager

```python
from service_manager import get_service_manager

sm = get_service_manager()
sm.set_event_bus(get_event_bus())
sm.set_config(get_config().get_all())
sm.initialize_service("config_service")
sm.start_service("config_service")
health = sm.get_service_health("config_service")
```

### Test Failure Handler

```python
from failure_handler import get_failure_handler, FailureEvent, FailureType

fh = get_failure_handler()
fh.set_event_bus(get_event_bus())
failure = FailureEvent(FailureType.MEMORY_FAILURE, "test", "Test failure")
fh.handle_failure(failure)
```

## Migration Path

### For Existing Code

1. **Convert to Service Interface**: Implement init(), start(), stop(), health()
2. **Use Event Bus**: Replace direct calls with event emission
3. **Remove OS Hacks**: Use unified memory manager instead
4. **Follow Startup Sequence**: Ensure proper initialization order

### For New Code

1. **Always use Service Interface**: New components must be services
2. **Use Event Bus**: All communication through events
3. **Follow Runtime Contract**: Adhere to behavioral rules
4. **Use Platform Abstraction**: Cross-platform compatibility

## Benefits

### Technical Benefits

- **Single Source of Truth**: One authoritative entry point
- **Formal Contracts**: Clear interfaces and behavioral rules
- **Event-Driven**: Loose coupling between components
- **Failure Resilience**: Automated failure detection and recovery
- **Cross-Platform**: Consistent behavior across platforms

### Operational Benefits

- **Predictable Behavior**: Consistent startup and shutdown
- **Better Monitoring**: Comprehensive event logging
- **Easier Debugging**: Clear event flows and service states
- **Improved Reliability**: Automated failure recovery
- **Simplified Maintenance**: Clear architectural boundaries

## Compliance with Runtime Specification

### ✅ Core Principle
- Service-based runtime with orchestrated lifecycle
- BOOT → REGISTER → INITIALIZE → RUN → MONITOR → RECOVER → SHUTDOWN

### ✅ Single Source of Truth
- `dix.py` as authoritative entry point
- All other scripts are wrappers only

### ✅ Service Model
- All components conform to Service interface
- init(), start(), stop(), health() implemented

### ✅ Event Bus
- All communication through EventBus
- Standardized event structure
- Event types and flows defined

### ✅ AI Runtime Contract
- AI lifecycle defined
- AI rules enforced through event emission

### ✅ Memory System Contract
- Single memory authority
- API-based memory access
- Event-based memory pressure notifications

### ✅ Dashboard Contract
- Dashboard as client only
- No direct system state modification
- Event-based data flow

### ✅ Validation Layer
- Passive observer service
- No controller behavior
- Event-based violation reporting

### ✅ Failure Handling Model
- Detect → Classify → Emit → Recover → Verify pipeline
- Failure types defined
- Recovery strategies implemented

### ✅ System State Model
- BOOTING, RUNNING, DEGRADED, RECOVERING, STOPPED states
- State transitions managed by orchestrator

### ✅ Startup Sequence
- Formal 9-step startup sequence
- Proper dependency resolution
- Dashboard starts last

## Conclusion

The DIX VISION system now has a formal runtime constitution as specified. This is not just code changes, but:

- ✔ Behavioral rules
- ✔ Execution order
- ✔ Service contracts
- ✔ System boundaries
- ✔ Failure model

The system is now a proper service-based runtime with a single orchestrated lifecycle, replacing the previous collection of scripts with a unified, formal architecture.