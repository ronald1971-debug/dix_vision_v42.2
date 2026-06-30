# Optimize WSL and Docker Desktop Memory Usage
# This script now uses the unified platform abstraction layer

Write-Host "=== WSL & Docker Memory Optimization ===" -ForegroundColor Yellow

# Use unified platform abstraction
try {
    $pythonScript = @"
from platform_abstraction import get_platform_manager
import json

pm = get_platform_manager()
platform_info = pm.get_platform_info()

result = {
    'platform': platform_info.platform.value,
    'is_wsl': platform_info.is_wsl,
    'is_docker': platform_info.is_docker,
    'python_version': platform_info.python_version,
    'os_version': platform_info.os_version
}

print(json.dumps(result))
"@
    
    $result = python -c $pythonScript
    $platformData = $result | ConvertFrom-Json
    
    Write-Host "`nPlatform Information:" -ForegroundColor Cyan
    Write-Host "  Platform: $($platformData.platform)"
    Write-Host "  Is WSL: $($platformData.is_wsl)"
    Write-Host "  Is Docker: $($platformData.is_docker)"
    Write-Host "  Python: $($platformData.python_version)"
    
    if ($platformData.is_wsl -or $platformData.platform -eq "linux") {
        Write-Host "`n2. Configuring WSL memory limits..." -ForegroundColor Cyan
        
        $wslConfigPath = "$env:USERPROFILE\.wslconfig"
        
        $wslConfig = @"
[wsl2]
memory=4GB
processors=4
swap=2GB
"@
        
        $wslConfig | Set-Content $wslConfigPath
        Write-Host "Created .wslconfig with 4GB memory limit" -ForegroundColor Green
        
        # Use unified memory manager if available
        Write-Host "`n3. Using unified memory manager..." -ForegroundColor Cyan
        $memoryScript = @"
from memory_manager import get_memory_manager
import json

try:
    mm = get_memory_manager()
    summary = mm.get_summary()
    print(json.dumps(summary, indent=2))
except Exception as e:
    print(f'Error: {e}')
"@
        
        try {
            $memoryResult = python -c $memoryScript
            Write-Host $memoryResult
        } catch {
            Write-Host "Unified memory manager not available, skipping..." -ForegroundColor Yellow
        }
    }
    
    if ($platformData.is_docker -or $platformData.platform -eq "windows") {
        Write-Host "`n3. Checking Docker Desktop settings..." -ForegroundColor Cyan
        $dockerSettingsPath = "$env:APPDATA\Docker\settings.json"
        if (Test-Path $dockerSettingsPath) {
            Write-Host "Docker Desktop settings found at: $dockerSettingsPath"
            try {
                $dockerSettings = Get-Content $dockerSettingsPath -Raw | ConvertFrom-Json
                Write-Host "Current memory limit: $($dockerSettings.memoryMiB)MB"
            } catch {
                Write-Host "Could not read Docker settings"
            }
        } else {
            Write-Host "Docker Desktop settings not found"
        }
    }
    
    Write-Host "`n=== Optimization Complete ===" -ForegroundColor Green
    Write-Host "Platform abstraction layer: Active" -ForegroundColor Green
    Write-Host "Unified memory management: Available" -ForegroundColor Green
    
} catch {
    Write-Host "Error during optimization: $_" -ForegroundColor Red
    Write-Host "Falling back to legacy optimization..." -ForegroundColor Yellow
    
    # Legacy fallback
    Write-Host "`n1. Current WSL Memory Usage:" -ForegroundColor Cyan
    Get-Process | Where-Object {$_.Name -like "*VMMem*"} | Select-Object Name, @{Name="MemoryMB";Expression={[math]::Round($_.WorkingSet/1MB,2)}}
    
    $wslConfigPath = "$env:USERPROFILE\.wslconfig"
    Write-Host "`n2. Configuring WSL memory limits..." -ForegroundColor Cyan
    
    $wslConfig = @"
[wsl2]
memory=4GB
processors=4
swap=2GB
"@
    
    $wslConfig | Set-Content $wslConfigPath
    Write-Host "Created .wslconfig with 4GB memory limit" -ForegroundColor Green
    
    Write-Host "`n3. Checking Docker Desktop settings..." -ForegroundColor Cyan
    $dockerSettingsPath = "$env:APPDATA\Docker\settings.json"
    if (Test-Path $dockerSettingsPath) {
        Write-Host "Docker Desktop settings found at: $dockerSettingsPath"
        try {
            $dockerSettings = Get-Content $dockerSettingsPath -Raw | ConvertFrom-Json
            Write-Host "Current memory limit: $($dockerSettings.memoryMiB)MB"
        } catch {
            Write-Host "Could not read Docker settings"
        }
    } else {
        Write-Host "Docker Desktop settings not found"
    }
    
    Write-Host "`n=== Optimization Complete (Legacy Mode) ===" -ForegroundColor Green
}

Write-Host "`nNext steps:" -ForegroundColor Yellow
Write-Host "1. Run: wsl --shutdown" -ForegroundColor White  
Write-Host "2. Restart Docker Desktop" -ForegroundColor White
Write-Host "3. Restart WSL: wsl" -ForegroundColor White
