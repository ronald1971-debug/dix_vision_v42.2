# Final test to determine if VS Code installation is corrupted
Write-Host "VS Code Installation Test" -ForegroundColor Yellow
Write-Host ""

# Create a completely empty folder at the same level
$emptyTestPath = "C:\Users\prive\Desktop\empty_test_workspace"
Write-Host "Creating empty test workspace at: $emptyTestPath" -ForegroundColor Cyan

if (Test-Path $emptyTestPath) {
    Remove-Item -Path $emptyTestPath -Recurse -Force
}

New-Item -Path $emptyTestPath -ItemType Directory -Force | Out-Null

# Create no files at all - completely empty
Write-Host "Created completely empty folder" -ForegroundColor Green
Write-Host ""
Write-Host "============================================" -ForegroundColor Yellow
Write-Host "FINAL TEST INSTRUCTIONS" -ForegroundColor Yellow
Write-Host "============================================" -ForegroundColor Yellow
Write-Host ""
Write-Host "1. Close VS Code completely" -ForegroundColor White
Write-Host "2. Open VS Code" -ForegroundColor White
Write-Host "3. File -> Open Folder -> Select: $emptyTestPath" -ForegroundColor White
Write-Host "4. Check if the 'Protocol error (invalid_argument)' appears" -ForegroundColor White
Write-Host ""
Write-Host "RESULTS:" -ForegroundColor Yellow
Write-Host "- If NO error: DIX VISION project location/path is the issue" -ForegroundColor Green
Write-Host "- If YES error: VS Code installation is corrupted" -ForegroundColor Red
Write-Host ""
Write-Host "If error occurs in empty workspace:" -ForegroundColor Yellow
Write-Host "1. VS Code installation is corrupted" -ForegroundColor White
Write-Host "2. Uninstall VS Code completely" -ForegroundColor White
Write-Host "3. Delete VS Code user data: %APPDATA%\Code" -ForegroundColor White
Write-Host "4. Reinstall VS Code from scratch" -ForegroundColor White
Write-Host "5. Or try a different IDE (Cursor, Windsurf, etc.)" -ForegroundColor White
Write-Host ""