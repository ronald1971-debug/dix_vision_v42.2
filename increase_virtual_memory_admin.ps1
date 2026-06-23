# Virtual Memory Increase Script - REQUIRES ADMINISTRATOR PRIVILEGES
# Run this script as Administrator to increase virtual memory

# Check if running as Administrator
$ isAdmin = ([Security.Principal.WindowsPrincipal] [Security.Principal.WindowsIdentity]::GetCurrent()).IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)

if (-not $isAdmin) {
    Write-Host "❌ This script requires Administrator privileges" -ForegroundColor Red
    Write-Host "Please right-click PowerShell and select 'Run as Administrator'" -ForegroundColor Yellow
    exit 1
}

Write-Host "=== Virtual Memory Increase Script ===" -ForegroundColor Cyan
Write-Host "Running with Administrator privileges" -ForegroundColor Green

# Disable automatic page file management
Write-Host "`nDisabling automatic page file management..." -ForegroundColor Yellow
try {
    $computerSystem = Get-WmiObject -Class Win32_ComputerSystem
    $computerSystem.AutomaticManagedPagefile = $false
    $computerSystem.Put()
    Write-Host "✅ Automatic page file management disabled" -ForegroundColor Green
} catch {
    Write-Host "❌ Failed to disable automatic page file management" -ForegroundColor Red
    Write-Host "Error: $($_.Exception.Message)" -ForegroundColor Gray
    exit 1
}

# Current configuration
$pageFile = Get-WmiObject -Class Win32_PageFileSetting
Write-Host "`nCurrent Page File Configuration:" -ForegroundColor Yellow
Write-Host "  Location: $($pageFile.Name)" -ForegroundColor White
Write-Host "  Initial Size: $($pageFile.InitialSize) MB ($([math]::Round($pageFile.InitialSize/1024,2)) GB)" -ForegroundColor White
Write-Host "  Maximum Size: $($pageFile.MaximumSize) MB ($([math]::Round($pageFile.MaximumSize/1024,2)) GB)" -ForegroundColor White

# Calculate optimal sizes based on physical RAM
$system = Get-WmiObject -Class Win32_ComputerSystem
$totalRAM = [math]::Round($system.TotalPhysicalMemory/1GB, 2)
Write-Host "`nSystem Physical RAM: $totalRAM GB" -ForegroundColor White

# Set optimal sizes for memory-intensive applications
$optimalInitialGB = [math]::Round($totalRAM * 2, 0)
$optimalMaximumGB = [math]::Round($totalRAM * 4, 0)
$optimalInitialMB = $optimalInitialGB * 1024
$optimalMaximumMB = $optimalMaximumGB * 1024

Write-Host "`nOptimal Page File Settings for Memory-Intensive Applications:" -ForegroundColor Green
Write-Host "  Initial Size: $optimalInitialGB GB ($optimalInitialMB MB)" -ForegroundColor White
Write-Host "  Maximum Size: $optimalMaximumGB GB ($optimalMaximumMB MB)" -ForegroundColor White

# Apply new settings
Write-Host "`nApplying new virtual memory settings..." -ForegroundColor Yellow
try {
    $pageFile.InitialSize = $optimalInitialMB
    $pageFile.MaximumSize = $optimalMaximumMB
    $pageFile.Put()
    
    Write-Host "✅ Virtual memory settings updated successfully!" -ForegroundColor Green
    Write-Host "   New Initial Size: $optimalInitialGB GB" -ForegroundColor White
    Write-Host "   New Maximum Size: $optimalMaximumGB GB" -ForegroundColor White
    
    # Display confirmation
    $updatedPageFile = Get-WmiObject -Class Win32_PageFileSetting
    Write-Host "`nVerification - New Settings:" -ForegroundColor Yellow
    Write-Host "  Initial Size: $($updatedPageFile.InitialSize) MB ($([math]::Round($updatedPageFile.InitialSize/1024,2)) GB)" -ForegroundColor White
    Write-Host "  Maximum Size: $($updatedPageFile.MaximumSize) MB ($([math]::Round($updatedPageFile.MaximumSize/1024,2)) GB)" -ForegroundColor White
    
} catch {
    Write-Host "❌ Failed to update virtual memory settings" -ForegroundColor Red
    Write-Host "Error: $($_.Exception.Message)" -ForegroundColor Gray
    
    # Provide manual instructions
    Write-Host "`nManual Configuration Instructions:" -ForegroundColor Yellow
    Write-Host "1. Press Win+R, type: sysdm.cpl" -ForegroundColor Gray
    Write-Host "2. Go to Advanced tab → Performance Settings" -ForegroundColor Gray
    Write-Host "3. Advanced tab → Virtual memory → Change" -ForegroundColor Gray
    Write-Host "4. Uncheck 'Automatically manage paging file size'" -ForegroundColor Gray
    Write-Host "5. Select C: drive" -ForegroundColor Gray
    Write-Host "6. Set Custom size:" -ForegroundColor Gray
    Write-Host "   Initial size (MB): $optimalInitialMB" -ForegroundColor White
    Write-Host "   Maximum size (MB): $optimalMaximumMB" -ForegroundColor White
    Write-Host "7. Click Set → OK → Apply" -ForegroundColor Gray
    Write-Host "8. Restart your computer" -ForegroundColor Gray
    exit 1
}

Write-Host "`n⚠️  SYSTEM RESTART REQUIRED to apply virtual memory changes" -ForegroundColor Yellow
Write-Host "Please restart your computer to activate the new virtual memory settings" -ForegroundColor Cyan

Write-Host "`n=== Virtual Memory Increase Complete ===" -ForegroundColor Green