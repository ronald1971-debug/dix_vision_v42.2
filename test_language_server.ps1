# Test to isolate language server error cause
Write-Host "Language Server Error Isolation Test" -ForegroundColor Yellow
Write-Host ""

# Create a test folder outside the project
$testPath = "$env:USERPROFILE\Desktop\test_workspace"
Write-Host "Creating test workspace at: $testPath" -ForegroundColor Cyan

if (Test-Path $testPath) {
    Remove-Item -Path $testPath -Recurse -Force
}

New-Item -Path $testPath -ItemType Directory -Force | Out-Null

# Create a simple test file
$testFile = Join-Path $testPath "test.py"
@"
# Simple test file
def hello():
    print("Hello, World")

if __name__ == "__main__":
    hello()
"@ | Out-File -FilePath $testFile -Encoding UTF8

Write-Host "Created test file: $testFile" -ForegroundColor Green
Write-Host ""
Write-Host "============================================" -ForegroundColor Yellow
Write-Host "TEST INSTRUCTIONS" -ForegroundColor Yellow
Write-Host "============================================" -ForegroundColor Yellow
Write-Host ""
Write-Host "1. Open VS Code" -ForegroundColor White
Write-Host "2. File -> Open Folder -> Select: $testPath" -ForegroundColor White
Write-Host "3. Open the test.py file" -ForegroundColor White
Write-Host "4. Check if the 'Protocol error (invalid_argument)' appears" -ForegroundColor White
Write-Host ""
Write-Host "RESULTS:" -ForegroundColor Yellow
Write-Host "- If NO error: The issue is project-specific (DIX VISION config)" -ForegroundColor Green
Write-Host "- If YES error: The issue is IDE installation/system-wide" -ForegroundColor Red
Write-Host ""
Write-Host "If error occurs in test workspace:" -ForegroundColor Yellow
Write-Host "1. VS Code installation may be corrupted" -ForegroundColor White
Write-Host "2. Try reinstalling VS Code" -ForegroundColor White
Write-Host "3. Check Windows Event Viewer for application errors" -ForegroundColor White
Write-Host ""