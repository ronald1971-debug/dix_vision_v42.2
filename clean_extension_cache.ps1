# Clean Extension Cache to Fix Missing Extension Errors
Write-Host "Cleaning VS Code/Windsurf Extension Cache..." -ForegroundColor Yellow

# Remove the missing extension reference from cache
$extensionCache = "c:\Users\prive\.devin\extensions"
if (Test-Path $extensionCache) {
    Write-Host "Extension cache directory exists: $extensionCache" -ForegroundColor Green
    
    # List current extensions
    Write-Host "`nCurrent extensions in cache:" -ForegroundColor Cyan
    Get-ChildItem $extensionCache -Directory | ForEach-Object {
        Write-Host "  - $($_.Name)" -ForegroundColor White
    }
    
    # Check for any broken links or references to windsurfpyright
    $brokenRef = Join-Path $extensionCache "codeium.windsurfpyright-1.29.6-universal"
    if (Test-Path $brokenRef) {
        Write-Host "`nRemoving broken extension reference..." -ForegroundColor Yellow
        Remove-Item -Path $brokenRef -Recurse -Force
        Write-Host "Removed: $brokenRef" -ForegroundColor Green
    } else {
        Write-Host "`nNo broken reference found (expected - already deleted)" -ForegroundColor Green
    }
} else {
    Write-Host "Extension cache directory not found: $extensionCache" -ForegroundColor Yellow
}

# Clear IDE workspace state
$workspaceState = ".vscode\workspaceStorage"
if (Test-Path $workspaceState) {
    Write-Host "`nClearing workspace storage..." -ForegroundColor Yellow
    # List workspace storage directories
    Get-ChildItem $workspaceState -Directory | ForEach-Object {
        Write-Host "  Workspace: $($_.Name)" -ForegroundColor Cyan
    }
    # Optional: Uncomment to clear all workspace storage
    # Remove-Item -Path "$workspaceState\*" -Recurse -Force
    Write-Host "Workspace storage cleared (if uncommented)" -ForegroundColor Green
}

Write-Host "`nExtension cache clean complete." -ForegroundColor Green
Write-Host "Please reload the IDE window (Ctrl+Shift+P -> 'Reload Window')" -ForegroundColor Yellow
