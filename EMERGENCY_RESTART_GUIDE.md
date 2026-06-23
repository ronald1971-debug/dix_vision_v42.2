# EMERGENCY RESTART GUIDE - OOM Error 536870904

## Current Status
- ❌ OOM error -536870904 **PERSISTS**
- ❌ WSL/VMMemWSL still running double even after Docker closed
- ❌ Previous fixes insufficient

## Root Cause Analysis
The issue is more complex than initially diagnosed:
1. **WSL memory management**: WSL processes cannot be force-terminated (protected system processes)
2. **Extension conflicts**: Devin extensions are locked while IDE is running
3. **VS Code memory limits**: Standard configuration insufficient for this project complexity

## Required Actions

### Step 1: Complete System Restart (RECOMMENDED)
1. **Save all work**
2. **Close ALL applications**: VS Code/Devin, Docker Desktop, any WSL terminals
3. **Restart Windows completely**
4. **After restart**, Docker should start with clean WSL state

### Step 2: Alternative: Manual Clean Restart
If system restart is not possible:

#### A. Stop Everything:
```powershell
# Stop Docker
taskkill /F /IM "Docker Desktop.exe"
taskkill /F /IM "com.docker.backend"

# Stop WSL  
wsl --shutdown

# Stop WSL service (requires admin)
net stop LxssManager
```

#### B. Clear Extension Cache:
```powershell
# After Devin is closed, rename extensions
Rename-Item -Path "$env:USERPROFILE\.devin\extensions" -NewName "$env:USERPROFILE\.devin\extensions.backup"
```

#### C. Clear VS Code Caches:
```powershell
Remove-Item -Path "$env:APPDATA\Code\Cache" -Recurse -Force
Remove-Item -Path "$env:APPDATA\Code\CachedData" -Recurse -Force
```

#### D. Restart:
1. Start Docker Desktop
2. Start VS Code/Devin
3. Open project: `c:/dix_vision_v42.2`

### Step 3: If OOM Persists After Restart
The project may be too complex for current system:

#### Options:
1. **Disable Copilot completely**: Extensions → Disable GitHub Copilot
2. **Use simpler editor**: Notepad++ or VS Code without AI features  
3. **Reduce project scope**: Work on smaller subdirectories
4. **System upgrade**: More RAM (currently 15.84GB may be insufficient)

## Project Complexity Analysis
This project is extremely complex:
- **8,594+ lines** of cognitive system implementations
- **159 cognitive components** across 17 systems  
- **Multiple Python runtimes** and Docker containers
- **Complex trading system** with real-time requirements

**This level of complexity may exceed VS Code/Devin memory limits.**

## Immediate Recommendation
**Complete Windows restart** is the most reliable solution to:
- Clear all WSL memory states
- Reset all protected processes
- Start with clean memory management
- Allow Docker to initialize properly

## After Restart Verification
Check if issues are resolved:
```powershell
# Check WSL memory
Get-Process | Where-Object {$_.Name -like "*VMMem*"}

# Check system memory  
Get-CimInstance Win32_OperatingSystem | Select-Object @{Name="FreeGB";Expression={[math]::Round($_.FreePhysicalMemory/1MB,2)}}

# Check Devin processes
Get-Process | Where-Object {$_.Name -like "*Devin*"}
```

## Expected Results After Clean Restart
- VMMemWSL: Normal ~1GB (not double)
- OOM error: Should be resolved
- IDE: Stable operation
- Memory: Manageable usage patterns

## If Still Failing
Contact Devin support at https://windsurf.com/support with:
- Error code: -536870904
- System specs: 15.84GB RAM, Windows
- Project complexity details
- All attempted fixes
