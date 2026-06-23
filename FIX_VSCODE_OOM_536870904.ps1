# Fix VS Code/Devin OOM Error -536870904
Write-Host "=== Fixing VS Code OOM Error -536870904 ===" -ForegroundColor Yellow

Write-Host "`n1. Creating VS Code memory configuration..." -ForegroundColor Cyan

# Create VS Code arguments file to increase memory limits
$vscodeArgsPath = "$env:APPDATA\Code\User\argv.json"
$argvConfig = @{
    "disable-hardware-acceleration" = $true
    "disable-gpu" = $true
    "max-memory" = 8192  # 8GB limit
}

$argvConfig | ConvertTo-Json -Depth 10 | Set-Content $vscodeArgsPath
Write-Host "Created argv.json with memory optimizations" -ForegroundColor Green

Write-Host "`n2. Updating VS Code settings for large files..." -ForegroundColor Cyan

$settingsPath = ".vscode\settings.json"
if (Test-Path $settingsPath) {
    $settings = Get-Content $settingsPath -Raw | ConvertFrom-Json
    
    # Add memory optimization settings
    $settings | Add-Member -MemberType NoteProperty -Name "files.exclude" -Value @{
        "**/__pycache__" = $true
        "**/node_modules" = $true  
    } -Force
    
    $settings | Add-Member -MemberType NoteProperty -Name "search.exclude" -Value @{
        "**/__pycache__" = $true
        "**/node_modules" = $true
    } -Force
    
    $settings | Add-Member -MemberType NoteProperty -Name "editor.largeFileOptimizations" -Value $true -Force
    
    $settings | ConvertTo-Json -Depth 10 | Set-Content $settingsPath
    Write-Host "Updated VS Code settings" -ForegroundColor Green
} else {
    Write-Host "Settings file not found, skipping" -ForegroundColor Yellow
}

Write-Host "`n3. Disabling problematic extensions..." -ForegroundColor Cyan

# Create extension ignore list
$extensionsToDisable = @(
    "github.copilot"
    "github.copilot-chat"
    "ms-vscode.cpptools"
    "ms-python.python"
)

Write-Host "Recommended to disable these extensions temporarily:" -ForegroundColor Yellow
foreach ($ext in $extensionsToDisable) {
    Write-Host "  - $ext" -ForegroundColor White
}

Write-Host "`n4. Clearing VS Code cache..." -ForegroundColor Cyan

$cachePaths = @(
    "$env:APPDATA\Code\Cache"
    "$env:APPDATA\Code\CachedData"
    "$env:APPDATA\Code\CachedExtensions"
    "$env:APPDATA\Code\Code Cache"
)

foreach ($path in $cachePaths) {
    if (Test-Path $path) {
        Write-Host "Clearing: $path"
        Remove-Item "$path\*" -Recurse -Force -ErrorAction SilentlyContinue
    }
}

Write-Host "Cache cleared" -ForegroundColor Green

Write-Host "`n=== Fix Complete ===" -ForegroundColor Green
Write-Host "`nNext steps:" -ForegroundColor Yellow
Write-Host "1. Close VS Code/Devin completely" -ForegroundColor White
Write-Host "2. Restart VS Code/Devin" -ForegroundColor White
Write-Host "3. Disable Copilot if issue persists (Extensions → Disable)" -ForegroundColor White
Write-Host "4. Avoid opening very large files (>100MB)" -ForegroundColor White
