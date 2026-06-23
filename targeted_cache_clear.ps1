# Targeted cache clear for VS Code/Code
Write-Host "Targeted Cache Clear for Language Server Error" -ForegroundColor Yellow
Write-Host ""

$basePath = "$env:APPDATA\Code"
$cachesToClear = @(
    "Cache",
    "Code Cache",
    "GPUCache",
    "DawnGraphiteCache",
    "DawnWebGPUCache",
    "Local Storage",
    "Session Storage",
    "Shared Dictionary",
    "Network",
    "CachedData",
    "CachedConfigurations",
    "CachedExtensionVSIXs",
    "CachedProfilesData",
    "logs"
)

Write-Host "Clearing VS Code caches..." -ForegroundColor Cyan
foreach ($cache in $cachesToClear) {
    $path = Join-Path $basePath $cache
    if (Test-Path $path) {
        Write-Host "Clearing: $cache"
        try {
            Remove-Item -Path $path -Recurse -Force -ErrorAction SilentlyContinue
            Write-Host "  Cleared successfully" -ForegroundColor Green
        } catch {
            Write-Host "  Failed to clear: $_" -ForegroundColor Red
        }
    }
}

Write-Host ""
Write-Host "Clearing User workspace state..." -ForegroundColor Cyan
$userPath = Join-Path $basePath "User"
if (Test-Path $userPath) {
    $userItems = Get-ChildItem $userPath -ErrorAction SilentlyContinue
    foreach ($item in $userItems) {
        if ($item.Name -eq "globalStorage" -or $item.Name -eq "workspaceStorage" -or $item.Name -eq "logs") {
            Write-Host "Clearing User\$($item.Name)"
            try {
                Remove-Item -Path $item.FullName -Recurse -Force -ErrorAction SilentlyContinue
                Write-Host "  Cleared successfully" -ForegroundColor Green
            } catch {
                Write-Host "  Failed to clear: $_" -ForegroundColor Red
            }
        }
    }
}

Write-Host ""
Write-Host "============================================" -ForegroundColor Green
Write-Host "TARGETED CLEANUP COMPLETED" -ForegroundColor Green
Write-Host "============================================" -ForegroundColor Green
Write-Host ""
Write-Host "CRITICAL: You must restart your IDE now!" -ForegroundColor Red
Write-Host ""
Write-Host "The language server protocol error should be resolved after restart." -ForegroundColor Yellow
Write-Host ""