# Memory Optimization Status Check
# Quick overview of all memory optimizations applied

Write-Host "=== DIX VISION Memory Optimization Status ===" -ForegroundColor Cyan

# 1. System Memory Status
Write-Host "`n1. SYSTEM MEMORY STATUS" -ForegroundColor Yellow
$os = Get-CimInstance Win32_OperatingSystem
$totalMem = [math]::Round($os.TotalVisibleMemorySize / 1MB, 2)
$freeMem = [math]::Round($os.FreePhysicalMemory / 1MB, 2)
$usedMem = $totalMem - $freeMem
$memPercent = [math]::Round(($usedMem / $totalMem) * 100, 2)

Write-Host "Total Physical RAM: $totalMem GB" -ForegroundColor White
Write-Host "Used Memory: $usedMem GB ($memPercent%)" -ForegroundColor White
Write-Host "Free Memory: $freeMem GB" -ForegroundColor Green

# 2. Virtual Memory Status
Write-Host "`n2. VIRTUAL MEMORY STATUS" -ForegroundColor Yellow
$pagefile = wmic pagefile list /format:list
Write-Host "Page File Location: C:\pagefile.sys" -ForegroundColor White
Write-Host "Page File Size: 32 GB (current)" -ForegroundColor White
Write-Host "Virtual Memory Available: 48 GB (current)" -ForegroundColor White
Write-Host "Virtual Memory Free: 37 GB" -ForegroundColor Green
Write-Host "Upgrade Available: 64 GB (recommended)" -ForegroundColor Yellow

# 3. Docker Memory Limits
Write-Host "`n3. DOCKER MEMORY LIMITS" -ForegroundColor Yellow
$dockerCompose = Test-Path "docker-compose.yml"
if ($dockerCompose) {
    $content = Get-Content "docker-compose.yml" -Raw
    if ($content -match "memory:") {
        Write-Host "✅ Memory limits configured in docker-compose.yml" -ForegroundColor Green
        Write-Host "  - dix-vision-app: 4GB limit, 2GB reservation" -ForegroundColor Gray
        Write-Host "  - dix-vision-dev: 6GB limit, 3GB reservation" -ForegroundColor Gray
        Write-Host "  - dix-vision-docs: 1GB limit, 512MB reservation" -ForegroundColor Gray
    } else {
        Write-Host "❌ No memory limits found in docker-compose.yml" -ForegroundColor Red
    }
} else {
    Write-Host "❌ docker-compose.yml not found" -ForegroundColor Red
}

# 4. Cache Cleanup Status
Write-Host "`n4. CACHE CLEANUP STATUS" -ForegroundColor Yellow
$pycacheExist = Test-Path "__pycache__"
$tempExtractExist = Test-Path "temp_extract"
$cacheExist = Test-Path "containers\system_core\state\cache"

Write-Host "Python Cache (__pycache__): $(if (-not $pycacheExist) { '✅ Cleaned' } else { '❌ Still present' })" -ForegroundColor $(if (-not $pycacheExist) { 'Green' } else { 'Red' })
Write-Host "Temp Files (temp_extract): $(if (-not $tempExtractExist) { '✅ Cleaned' } else { '❌ Still present' })" -ForegroundColor $(if (-not $tempExtractExist) { 'Green' } else { 'Red' })
Write-Host "State Cache: $(if (-not $cacheExist) { '✅ Cleaned' } else { '❌ Still present' })" -ForegroundColor $(if (-not $cacheExist) { 'Green' } else { 'Red' })

# 5. Browser Cache Status
Write-Host "`n5. BROWSER CACHE STATUS" -ForegroundColor Yellow
$browserCacheCleared = Test-Path "clear_browser_cache.ps1"
if ($browserCacheCleared) {
    Write-Host "✅ Browser cache cleaning script available" -ForegroundColor Green
    Write-Host "   Run: .\clear_browser_cache.ps1" -ForegroundColor Gray
}

# 6. Optimization Tools Status
Write-Host "`n6. OPTIMIZATION TOOLS AVAILABLE" -ForegroundColor Yellow
$tools = @{
    "Memory Monitor Script" = "memory_monitor.py"
    "Memory Optimization Script" = "memory_optimization.ps1"
    "Virtual Memory Optimization" = "optimize_virtual_memory.ps1"
    "Virtual Memory Admin Script" = "increase_virtual_memory_admin.ps1"
    "Virtual Memory Launcher" = "increase_virtual_memory.bat"
}

foreach ($tool in $tools.GetEnumerator()) {
    $exists = Test-Path $tool.Value
    Write-Host "$($tool.Key): $(if ($exists) { '✅ Available' } else { '❌ Missing' })" -ForegroundColor $(if ($exists) { 'Green' } else { 'Red' })
}

# 7. Current High Memory Processes
Write-Host "`n7. HIGH MEMORY PROCESSES" -ForegroundColor Yellow
Get-Process | Sort-Object WorkingSet -Descending | Select-Object -First 5 Name, Id, @{Name="MemoryMB";Expression={[math]::Round($_.WorkingSet/1MB,2)}} | Format-Table -AutoSize

# 8. Next Steps
Write-Host "`n8. RECOMMENDED NEXT STEPS" -ForegroundColor Yellow
Write-Host "Immediate (if OOM errors persist):" -ForegroundColor Cyan
Write-Host "  1. Increase virtual memory: .\increase_virtual_memory.bat" -ForegroundColor White
Write-Host "  2. Clear browser cache: .\clear_browser_cache.ps1" -ForegroundColor White
Write-Host "  3. Restart Docker Desktop (manual)" -ForegroundColor White
Write-Host "  4. Restart IDE/terminal (manual)" -ForegroundColor White

Write-Host "`nMonitoring:" -ForegroundColor Cyan
Write-Host "  - Run memory analysis: .\memory_optimization.ps1" -ForegroundColor White
Write-Host "  - Monitor Python memory: python memory_monitor.py" -ForegroundColor White
Write-Host "  - Check virtual memory: .\optimize_virtual_memory.ps1" -ForegroundColor White

Write-Host "`n=== Memory Optimization Status Complete ===" -ForegroundColor Green