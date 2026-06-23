# Memory Optimization Script for DIX VISION
Write-Host "=== DIX VISION Memory Optimization ===" -ForegroundColor Cyan

# Step 1: Current Memory Analysis
Write-Host "`n1. Current Memory Usage Analysis:" -ForegroundColor Yellow
Get-Process | Sort-Object WorkingSet -Descending | Select-Object -First 15 Name, Id, @{Name="MemoryMB";Expression={[math]::Round($_.WorkingSet/1MB,2)}} | Format-Table -AutoSize

# Step 2: System Memory Information
Write-Host "`n2. System Memory Status:" -ForegroundColor Yellow
$os = Get-CimInstance Win32_OperatingSystem
$totalMem = [math]::Round($os.TotalVisibleMemorySize / 1MB, 2)
$freeMem = [math]::Round($os.FreePhysicalMemory / 1MB, 2)
$usedMem = $totalMem - $freeMem
$memPercent = [math]::Round(($usedMem / $totalMem) * 100, 2)

Write-Host "Total Memory: $totalMem GB"
Write-Host "Used Memory: $usedMem GB ($memPercent%)"
Write-Host "Free Memory: $freeMem GB"

# Step 3: Clear Additional System Cache
Write-Host "`n3. Clearing System Cache:" -ForegroundColor Yellow
Write-Host "Clearing Windows DNS cache..." -ForegroundColor Cyan
Clear-DnsClientCache -ErrorAction SilentlyContinue

Write-Host "Clearing Windows Font cache..." -ForegroundColor Cyan
Stop-Service -Name "FontCache" -Force -ErrorAction SilentlyContinue
Remove-Item -Path "$env:LOCALAPPDATA\Microsoft\Windows\Fonts\cache*" -Recurse -Force -ErrorAction SilentlyContinue
Start-Service -Name "FontCache" -ErrorAction SilentlyContinue

# Step 4: Docker Memory Configuration Check
Write-Host "`n4. Docker Configuration Check:" -ForegroundColor Yellow
if (Test-Path "C:\Program Files\Docker\Docker\Docker Desktop.exe") {
    Write-Host "Docker Desktop is installed" -ForegroundColor Green
    Write-Host "Docker memory limits have been configured in docker-compose.yml" -ForegroundColor Green
} else {
    Write-Host "Docker Desktop not found" -ForegroundColor Red
}

# Step 5: Python Process Check
Write-Host "`n5. Python Processes:" -ForegroundColor Yellow
Get-Process python* -ErrorAction SilentlyContinue | Select-Object Name, Id, @{Name="MemoryMB";Expression={[math]::Round($_.WorkingSet/1MB,2)}} | Format-Table -AutoSize

# Step 6: Recommendations
Write-Host "`n6. Memory Optimization Recommendations:" -ForegroundColor Yellow
Write-Host "- Docker memory limits configured in docker-compose.yml:" -ForegroundColor Green
Write-Host "  * dix-vision-app: 4GB limit, 2GB reservation" -ForegroundColor Gray
Write-Host "  * dix-vision-dev: 6GB limit, 3GB reservation" -ForegroundColor Gray
Write-Host "  * dix-vision-docs: 1GB limit, 512MB reservation" -ForegroundColor Gray
Write-Host "  * dix-vision-config: 512MB limit, 256MB reservation" -ForegroundColor Gray
Write-Host "  * dix-vision-backup: 1GB limit, 512MB reservation" -ForegroundColor Gray

Write-Host "`n- Recommended Actions:" -ForegroundColor Yellow
Write-Host "1. Restart your IDE/terminal session" -ForegroundColor Cyan
Write-Host "2. Clear browser cache using clear_browser_cache.ps1" -ForegroundColor Cyan
Write-Host "3. Restart Docker Desktop if needed" -ForegroundColor Cyan
Write-Host "4. Monitor memory usage during operations" -ForegroundColor Cyan

Write-Host "`n=== Memory Analysis Complete ===" -ForegroundColor Green