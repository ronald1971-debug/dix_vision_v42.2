# Disable All VS Code Extensions to Fix OOM
Write-Host "=== Disabling All Extensions ===" -ForegroundColor Yellow

$extensionsPath = "$env:USERPROFILE\.vscode\extensions"
if (Test-Path $extensionsPath) {
    Write-Host "Found extensions directory: $extensionsPath"
    Write-Host "Temporarily renaming to disable all extensions..." -ForegroundColor Cyan
    
    $backupPath = "$extensionsPath.backup"
    if (Test-Path $backupPath) {
        Remove-Item -Path $backupPath -Recurse -Force
    }
    
    Rename-Item -Path $extensionsPath -Destination $backupPath -Force
    Write-Host "Extensions disabled (renamed to .backup)" -ForegroundColor Green
} else {
    Write-Host "Extensions directory not found" -ForegroundColor Yellow
}

Write-Host "`n=== Disabling Copilot Specifically ===" -ForegroundColor Yellow

# Create a settings file that disables Copilot
$vscodeSettings = "$env:APPDATA\Code\User\settings.json"
if (Test-Path $vscodeSettings) {
    try {
        $settings = Get-Content $vscodeSettings -Raw | ConvertFrom-Json
        $settings | Add-Member -MemberType NoteProperty -Name "github.copilot.enable" -Value $false -Force
        $settings | ConvertTo-Json -Depth 10 | Set-Content $vscodeSettings
        Write-Host "Copilot disabled in settings" -ForegroundColor Green
    } catch {
        Write-Host "Could not update VS Code settings" -ForegroundColor Yellow
    }
}

Write-Host "`n=== Complete ===" -ForegroundColor Green
Write-Host "Next steps:" -ForegroundColor Yellow
Write-Host "1. Restart VS Code/Devin" -ForegroundColor White
Write-Host "2. Test if OOM error persists" -ForegroundColor White
Write-Host "3. If fixed, re-enable extensions one by one" -ForegroundColor White
Write-Host "4. To restore extensions: Rename .backup back to extensions" -ForegroundColor White
