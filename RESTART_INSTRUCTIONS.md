# Devin IDE Restart Instructions

## Configuration Fixes Applied ✅
- Removed MCP Docker git server configuration
- Fixed path typo in permissions (dix_vision_vision_v42.2 → dix_vision_v42.2)
- Stopped Docker MCP container

## Current State
- 11 Devin processes still running (old processes)
- Configuration fixed but **not yet applied**

## Required Action: Complete IDE Restart

### Step 1: Close Devin IDE Completely
1. File → Exit
2. OR Click X in the top-right corner
3. OR Right-click Devin icon in taskbar → Close window

### Step 2: Verify All Processes Terminated
Run this command to confirm:
```powershell
tasklist | findstr Devin
```
Should show **0 processes** or only 1-2 processes.

### Step 3: Restart Devin IDE
1. Open Devin IDE
2. Open your project: `c:/dix_vision_v42.2`

### Step 4: Verify Fix
After restart, run:
```powershell
tasklist | findstr Devin
```
Should show **only 1-3 processes** (normal operation).

## Why Restart is Required
- Configuration changes only apply on IDE startup
- Running processes don't reload configuration dynamically
- MCP servers and background services start on launch

## Expected Result After Restart
- **1-3 Devin processes** (normal)
- **No OOM errors** when opening sessions
- **Reduced memory usage** (~500MB vs 2GB+)
