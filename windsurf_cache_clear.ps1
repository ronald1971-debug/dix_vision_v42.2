# PowerShell script to clear Windsurf/VS Code caches aggressively
Write-Host "Aggressive Cache Clear for Language Server Error" -ForegroundColor Yellow
Write-Host ""

# Define paths to clear
$pathsToClear = @(
    "$env:APPDATA\Code\User\globalStorage",
    "$env:APPDATA\Code\User\workspaceStorage",
    "$env:APPDATA\Code\User\logs",
    "$env:APPDATA\Code\User\CachedData",
    "$env:APPDATA\Code\User\CachedExtensions",
    "$env:LOCALAPPDATA\Windsurf\User\globalStorage",
    "$env:LOCALAPPDATA\Windsurf\User\workspaceStorage",
    "$env:LOCALAPPDATA\Windsurf\User\logs",
    "$env:APPDATA\Windsurf\User\globalStorage",
    "$env:APPDATA\Windsurf\User\workspaceStorage"
)

Write-Host "Clearing IDE caches..." -ForegroundColor Cyan
foreach ($path in $pathsToClear) {
    if (Test-Path $path) {
        Write-Host "Clearing: $path"
        try {
            Remove-Item -Path $path -Recurse -Force -ErrorAction SilentlyContinue
            Write-Host "  Cleared successfully" -ForegroundColor Green
        } catch {
            Write-Host "  Failed to clear: $_" -ForegroundColor Red
        }
    } else {
        Write-Host "  Path not found: $path" -ForegroundColor Gray
    }
}

Write-Host ""
Write-Host "Checking for running IDE processes..." -ForegroundColor Cyan
$ideProcesses = Get-Process | Where-Object { $_.ProcessName -like "*code*" -or $_.ProcessName -like "*windsurf*" }
if ($ideProcesses) {
    Write-Host "Found running IDE processes:" -ForegroundColor Yellow
    $ideProcesses | ForEach-Object { Write-Host "  $($_.ProcessName) (PID: $($_.Id))" }
    Write-Host ""
    Write-Host "Please close all IDE instances before restarting!" -ForegroundColor Red
} else {
    Write-Host "No IDE processes found - safe to restart" -ForegroundColor Green
}

Write-Host ""
Write-Host "Creating clean workspace state..." -ForegroundColor Cyan
if (Test-Path ".vscode") {
    Write-Host "Backing up .vscode folder..."
    Copy-Item -Path ".vscode" -Destination ".vscode_backup_$(Get-Date -Format 'yyyyMMdd_HHmmss')" -Recurse -Force
}

Write-Host ""
Write-Host "============================================" -ForegroundColor Green
Write-Host "AGGRESSIVE CLEANUP COMPLETED" -ForegroundColor Green
Write-Host "============================================" -ForegroundColor Green
Write-Host ""
Write-Host "Next steps:" -ForegroundColor Yellow
Write-Host "1. Close ALL IDE instances completely" -ForegroundColor White
Write-Host "2. Wait 10 seconds" -ForegroundColor White
Write-Host "3. Restart your IDE" -ForegroundColor White
Write-Host "4. If error persists, try clean workspace:" -ForegroundColor White
Write-Host "   - Rename .vscode to .vscode_old" -ForegroundColor White
Write-Host "   - Restart IDE" -ForegroundColor White
Write-Host ""
Write-Host "If still failing, this may indicate:" -ForegroundColor Red
Write-Host "- Corrupted IDE installation" -ForegroundColor White
Write-Host "- System-level language server issue" -ForegroundColor White
Write-Host "- Requires IDE reinstall" -ForegroundColor White
Write-Host ""