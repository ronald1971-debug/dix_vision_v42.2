# Optimize WSL and Docker Desktop Memory Usage
Write-Host "=== WSL & Docker Memory Optimization ===" -ForegroundColor Yellow

# Check current WSL memory usage
Write-Host "`n1. Current WSL Memory Usage:" -ForegroundColor Cyan
Get-Process | Where-Object {$_.Name -like "*VMMem*"} | Select-Object Name, @{Name="MemoryMB";Expression={[math]::Round($_.WorkingSet/1MB,2)}}

# Create/Update .wslconfig to limit WSL memory
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

# Check Docker Desktop memory settings
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

# Restart WSL for changes to take effect
Write-Host "`n4. To apply WSL memory changes, restart WSL:" -ForegroundColor Yellow
Write-Host "   wsl --shutdown" -ForegroundColor White
Write-Host "   Then restart Docker Desktop" -ForegroundColor White

Write-Host "`n=== Optimization Complete ===" -ForegroundColor Green
Write-Host "Next steps:" -ForegroundColor Yellow
Write-Host "1. Run: wsl --shutdown" -ForegroundColor White  
Write-Host "2. Restart Docker Desktop" -ForegroundColor White
Write-Host "3. Restart WSL: wsl" -ForegroundColor White
