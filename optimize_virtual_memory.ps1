# Virtual Memory Optimization Script for DIX VISION
# Optimizes Windows page file for better OOM prevention

Write-Host "=== Virtual Memory Optimization ===" -ForegroundColor Cyan

# Step 1: Current Virtual Memory Analysis
Write-Host "`n1. Current Virtual Memory Configuration:" -ForegroundColor Yellow

$currentSettings = Get-WmiObject -Class Win32_PageFileUsage
Write-Host "Current Page File Usage:" -ForegroundColor Cyan
Write-Host "  Location: $($currentSettings.Name)" -ForegroundColor White
Write-Host "  Current Size: $([math]::Round($currentSettings.Size/1GB,2)) GB" -ForegroundColor White

$pagefileSettings = Get-WmiObject -Class Win32_PageFileSetting
Write-Host "`nPage File Settings:" -ForegroundColor Cyan
foreach ($setting in $pagefileSettings) {
    Write-Host "  Location: $($setting.Name)" -ForegroundColor White
    Write-Host "  Initial Size: $([math]::Round($setting.InitialSize/1MB,2)) GB" -ForegroundColor White
    Write-Host "  Maximum Size: $([math]::Round($setting.MaximumSize/1MB,2)) GB" -ForegroundColor White
}

# Step 2: System Memory Analysis
Write-Host "`n2. System Memory Analysis:" -ForegroundColor Yellow
$system = Get-WmiObject -Class Win32_ComputerSystem
$totalRAM = [math]::Round($system.TotalPhysicalMemory/1GB,2)
Write-Host "Total Physical RAM: $totalRAM GB" -ForegroundColor White

$os = Get-CimInstance Win32_OperatingSystem
$freeRAM = [math]::Round($os.FreePhysicalMemory/1MB,2)
$usedRAM = $totalRAM - $freeRAM
Write-Host "Used Physical RAM: $usedRAM GB" -ForegroundColor White
Write-Host "Free Physical RAM: $freeRAM GB" -ForegroundColor White

# Step 3: Calculate Optimal Page File Size
Write-Host "`n3. Optimal Page File Size Calculation:" -ForegroundColor Yellow

# Microsoft recommendation: 1.5x to 3x RAM size
$minRecommended = [math]::Round($totalRAM * 1.5, 0)
$maxRecommended = [math]::Round($totalRAM * 3, 0)

# For memory-intensive applications, use higher end
$optimalMin = [math]::Round($totalRAM * 2, 0)
$optimalMax = [math]::Round($totalRAM * 4, 0)

Write-Host "Microsoft Recommendation:" -ForegroundColor Cyan
Write-Host "  Minimum: $minRecommended GB" -ForegroundColor Gray
Write-Host "  Maximum: $maxRecommended GB" -ForegroundColor Gray

Write-Host "`nOptimal for Memory-Intensive Applications:" -ForegroundColor Green
Write-Host "  Initial Size: $optimalMin GB" -ForegroundColor White
Write-Host "  Maximum Size: $optimalMax GB" -ForegroundColor White

# Step 4: Check if optimization is needed
Write-Host "`n4. Optimization Analysis:" -ForegroundColor Yellow

$currentMaxMB = $pagefileSettings.MaximumSize
$currentMinMB = $pagefileSettings.InitialSize

$targetMinMB = $optimalMin * 1024
$targetMaxMB = $optimalMax * 1024

if ($currentMinMB -lt $targetMinMB -or $currentMaxMB -lt $targetMaxMB) {
    Write-Host "⚠️  Current settings are below optimal values" -ForegroundColor Red
    Write-Host "   Current Initial: $([math]::Round($currentMinMB/1MB,2)) GB, Target: $optimalMin GB" -ForegroundColor Gray
    Write-Host "   Current Maximum: $([math]::Round($currentMaxMB/1MB,2)) GB, Target: $optimalMax GB" -ForegroundColor Gray
    $needsOptimization = $true
} else {
    Write-Host "✅ Current settings meet or exceed optimal values" -ForegroundColor Green
    $needsOptimization = $false
}

# Step 5: Apply Optimizations (if needed)
if ($needsOptimization) {
    Write-Host "`n5. Applying Virtual Memory Optimization:" -ForegroundColor Yellow
    
    try {
        # Set optimal page file sizes
        $pagefileSettings.InitialSize = $targetMinMB
        $pagefileSettings.MaximumSize = $targetMaxMB
        $pagefileSettings.Put()
        
        Write-Host "✅ Virtual memory settings updated successfully!" -ForegroundColor Green
        Write-Host "   New Initial Size: $optimalMin GB" -ForegroundColor White
        Write-Host "   New Maximum Size: $optimalMax GB" -ForegroundColor White
        Write-Host "`n⚠️  System restart required to apply changes" -ForegroundColor Yellow
        
    } catch {
        Write-Host "❌ Failed to update virtual memory settings" -ForegroundColor Red
        Write-Host "   Error: $($_.Exception.Message)" -ForegroundColor Gray
        Write-Host "`nManual configuration may be required:" -ForegroundColor Yellow
        Write-Host "   1. Right-click 'This PC' → Properties" -ForegroundColor Gray
        Write-Host "   2. Advanced system settings" -ForegroundColor Gray
        Write-Host "   3. Performance → Settings" -ForegroundColor Gray
        Write-Host "   4. Advanced → Virtual memory → Change" -ForegroundColor Gray
        Write-Host "   5. Set Initial size: $optimalMin GB" -ForegroundColor Gray
        Write-Host "   6. Set Maximum size: $optimalMax GB" -ForegroundColor Gray
    }
} else {
    Write-Host "`n5. No optimization needed - Current settings are optimal" -ForegroundColor Green
}

# Step 6: Additional Virtual Memory Optimizations
Write-Host "`n6. Additional Virtual Memory Optimizations:" -ForegroundColor Yellow

# Clear system standby list (unused memory cache)
Write-Host "Clearing system standby list..." -ForegroundColor Cyan
try {
    $emptyStandbyList = @{
        "EmptyStandbyList.exe" = "C:\Windows\System32\EmptyStandbyList.exe"
    }
    
    if (Test-Path $emptyStandbyList["EmptyStandbyList.exe"]) {
        & $emptyStandbyList["EmptyStandbyList.exe"] 0  # Clear standby list
        Write-Host "✅ System standby list cleared" -ForegroundColor Green
    } else {
        Write-Host "⚠️  EmptyStandbyList.exe not found (Windows 8+ feature)" -ForegroundColor Yellow
    }
} catch {
    Write-Host "⚠️  Could not clear standby list (may require admin rights)" -ForegroundColor Yellow
}

# Step 7: Memory Management Settings
Write-Host "`n7. Optimizing Memory Management:" -ForegroundColor Yellow

try {
    # Set system to favor performance over background services
    $registryPath = "HKLM:\SYSTEM\CurrentControlSet\Control\PriorityControl"
    if (Test-Path $registryPath) {
        $win32Priority = Get-ItemProperty -Path $registryPath -Name "Win32PrioritySeparation" -ErrorAction SilentlyContinue
        
        if ($win32Priority) {
            Write-Host "Current Win32 Priority Separation: $($win32Priority.Win32PrioritySeparation)" -ForegroundColor Gray
        }
        
        # Set to favor programs (value: 38)
        Set-ItemProperty -Path $registryPath -Name "Win32PrioritySeparation" -Value 38 -ErrorAction Stop
        Write-Host "✅ System set to favor foreground applications" -ForegroundColor Green
    }
} catch {
    Write-Host "⚠️  Could not modify memory management settings (may require admin rights)" -ForegroundColor Yellow
}

# Step 8: Final Summary
Write-Host "`n=== Virtual Memory Optimization Summary ===" -ForegroundColor Cyan
Write-Host "Total Physical RAM: $totalRAM GB" -ForegroundColor White
Write-Host "Virtual Memory Range: $optimalMin GB - $optimalMax GB" -ForegroundColor White

if ($needsOptimization) {
    Write-Host "`n⚠️  RESTART REQUIRED to apply virtual memory changes" -ForegroundColor Yellow
}

Write-Host "\n✅ Virtual memory optimization complete!" -ForegroundColor Green