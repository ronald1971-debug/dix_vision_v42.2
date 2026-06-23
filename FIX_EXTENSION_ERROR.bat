@echo off
echo ========================================
echo FIXING CODEIUM EXTENSION ERROR
echo ========================================
echo.
echo This script will remove the broken Codeium extension reference.
echo.
echo IMPORTANT: You must close Windsurf IDE BEFORE running this script.
echo.
pause

echo.
echo Removing broken Codeium extension...
rmdir /s /q "c:\Users\prive\.devin\extensions\codeium.windsurfpyright-1.29.6-universal"

if %errorlevel% equ 0 (
    echo SUCCESS: Extension directory removed
) else (
    echo ERROR: Could not remove extension directory
    echo Possible causes:
    echo   - Windsurf IDE is still running (close it first)
    echo   - Another process is using the directory
    echo.
    pause
    exit /b 1
)

echo.
echo Clearing VS Code workspace state...
rmdir /s /q ".vscode\workspaceStorage"

echo.
echo ========================================
echo FIX COMPLETE
echo ========================================
echo.
echo Next steps:
echo 1. Start Windsurf IDE
echo 2. The broken extension should not load
echo 3. Try opening your archived session
echo.
pause
