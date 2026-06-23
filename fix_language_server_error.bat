@echo off
echo Fixing Language Server Protocol Error...
echo.

echo Step 1: Clearing VS Code/Windsurf cache...
if exist "%APPDATA%\Code\User\globalStorage" (
    echo Clearing global storage cache...
    del /f /q "%APPDATA%\Code\User\globalStorage\state.vscdb" 2>nul
    del /f /q "%APPDATA%\Code\User\globalStorage\state.vscdb.backup" 2>nul
)

if exist "%APPDATA%\Code\User\workspaceStorage" (
    echo Clearing workspace storage cache...
    for /d %%d in ("%APPDATA%\Code\User\workspaceStorage\*") do (
        rmdir /s /q "%%d" 2>nul
    )
)

echo.
echo Step 2: Restarting language servers...
echo Please restart your IDE (Windsurf/VS Code) to complete the fix.
echo.
echo If the error persists, try:
echo 1. Disable all extensions and re-enable them one by one
echo 2. Clear the IDE's output panel and restart
echo 3. Check for IDE updates
echo.
pause