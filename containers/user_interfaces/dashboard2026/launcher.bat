@echo off
echo ==========================================
echo DASHBOARD2026 Desktop Launcher
echo ==========================================
echo.

cd /d "%~dp0"

echo [1/3] Checking dependencies...
if not exist "node_modules" (
    echo Installing dependencies...
    call npm install
    if %errorlevel% neq 0 (
        echo ERROR: Failed to install dependencies
        pause
        exit /b 1
    )
) else (
    echo Dependencies already installed
    echo Force reinstalling to fix dependency issues...
    call npm install
    if %errorlevel% neq 0 (
        echo ERROR: Failed to reinstall dependencies
        pause
        exit /b 1
    )
)

echo.
echo [2/3] Starting development server...
echo.
echo Dashboard will be available at: http://localhost:5173/dash2/
echo IMPORTANT: Access via /dash2/ path for proper routing
echo Press Ctrl+C to stop the server
echo.

call npm run dev

pause