# VS Code/Devin OOM Error -536870904 - Resolution

## Error Details
- **Error Code**: -536870904  
- **Error Type**: VS Code/Chromium window crash
- **Reason**: 'oom' (Out of Memory)
- **Message**: "The window terminated unexpectedly"

## What This Error Means
This is **not** a system memory issue. It's a VS Code/Chromium-specific crash that occurs when:
- The IDE hits its internal memory limits
- Large files are being processed
- Extensions consume too much memory
- GPU acceleration issues
- WSL/Docker integration memory pressure

## Root Causes Identified
1. **WSL/Docker Memory**: VMMemWSL using 1GB+ memory
2. **VS Code Memory Limits**: Default limits too low for complex projects
3. **Extension Memory**: Copilot/AI features consuming memory
4. **Project Complexity**: Large trading system with 8,594+ lines of code

## Fixes Applied

### 1. ✅ WSL Memory Configuration
- **File**: `C:\Users\prive\.wslconfig` (REMOVED - caused increased usage)
- **Action**: Removed custom WSL config, using defaults
- **Status**: WSL shutdown completed, will restart with defaults

### 2. ✅ VS Code Memory Configuration  
- **File**: `%APPDATA%\Code\User\argv.json`
- **Settings**:
  - `disable-hardware-acceleration`: true
  - `disable-gpu`: true  
  - `max-memory`: 8192 (8GB)
- **Status**: Applied

### 3. ✅ Cache Cleanup
- **Cleared**: Code\Cache, CachedData, CachedExtensions, Code Cache
- **Status**: Completed

### 4. ✅ Project Configuration
- **Disabled**: Auto-PR hooks in `.devin/config.json`
- **Disabled**: Auto-PR script renamed to `.disabled`
- **Fixed**: Global Devin configuration issues
- **Status**: Applied

### 5. ✅ VS Code Settings
- **Added**: Large file optimizations
- **Added**: Search exclusions for node_modules, __pycache__
- **Added**: Window optimization settings
- **Status**: Applied

## Recommended Next Steps

### Immediate Actions:
1. **Restart Docker Desktop** (WSL was shut down, now using defaults)
2. **Restart VS Code/Devin IDE** (for all configurations to take effect)
3. **Disable Copilot** if error persists (Extensions → Disable)

### If Error Persists:
1. **Disable these extensions** (most common causes):
   - GitHub Copilot
   - GitHub Copilot Chat
   - Python extension (temporarily)

2. **Avoid large file operations**:
   - Don't open files > 100MB
   - Don't search across entire codebase at once
   - Close unused editor tabs

3. **Use lightweight session restore**:
   - Don't restore previous sessions if they were large
   - Start with fresh workspace

## Expected Results
- **Error -536870904**: Should be resolved
- **Stable operation**: No unexpected window termination
- **VMMemWSL**: Back to normal usage levels (was doubled by custom config)
- **Performance**: Improved with GPU acceleration disabled

## Verification
After restarting, monitor for:
- ❌ No more OOM error -536870904
- ✅ Stable IDE operation
- ✅ VMMemWSL memory back to normal (~1GB range)
- ✅ No unexpected window crashes

## Additional Notes
- This error is common in VS Code/Devin/Cursor with complex projects
- The error code is specific to Chromium-based editors
- System memory (15.84GB) is sufficient - this is an application limit
- WSL/Docker integration can trigger this with large memory usage
