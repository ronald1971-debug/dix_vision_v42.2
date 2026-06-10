@echo off
REM DIX VISION Modular Architecture Setup Script
REM Run this script as Administrator to install all dependencies

echo ========================================
echo DIX VISION Modular Architecture Setup
echo ========================================
echo.

REM Check if running as Administrator
net session >nul 2>&1
if %errorLevel% neq 0 (
    echo ERROR: This script requires Administrator privileges
    echo Please right-click and run as Administrator
    pause
    exit /b 1
)

echo [1/5] Installing root dependencies...
call npm install
if %errorLevel% neq 0 (
    echo ERROR: Failed to install root dependencies
    pause
    exit /b 1
)

echo [2/5] Installing shared-types dependencies...
cd packages\shared-types
call npm install
if %errorLevel% neq 0 (
    echo ERROR: Failed to install shared-types dependencies
    cd ..\..
    pause
    exit /b 1
)
cd ..\..

echo [3/5] Installing shared-config dependencies...
cd packages\shared-config
call npm install
if %errorLevel% neq 0 (
    echo ERROR: Failed to install shared-config dependencies
    cd ..\..
    pause
    exit /b 1
)
cd ..\..

echo [4/5] Installing governance-core dependencies...
cd packages\governance-core
call npm install
if %errorLevel% neq 0 (
    echo ERROR: Failed to install governance-core dependencies
    cd ..\..
    pause
    exit /b 1
)
cd ..\..

echo [5/5] Installing observability dependencies...
cd packages\observability
call npm install
if %errorLevel% neq 0 (
    echo ERROR: Failed to install observability dependencies
    cd ..\..
    pause
    exit /b 1
)
cd ..\..

echo [6/9] Installing execution-engine dependencies...
cd packages\execution-engine
call npm install
if %errorLevel% neq 0 (
    echo ERROR: Failed to install execution-engine dependencies
    cd ..\..
    pause
    exit /b 1
)
cd ..\..

echo [7/9] Installing indira dependencies...
cd packages\indira
call npm install
if %errorLevel% neq 0 (
    echo ERROR: Failed to install indira dependencies
    cd ..\..
    pause
    exit /b 1
)
cd ..\..

echo [8/9] Installing dyon dependencies...
cd packages\dyon
call npm install
if %errorLevel% neq 0 (
    echo ERROR: Failed to install dyon dependencies
    cd ..\..
    pause
    exit /b 1
)
cd ..\..

echo [9/9] Installing agent-runtime dependencies...
cd apps\agent-runtime
call npm install
if %errorLevel% neq 0 (
    echo ERROR: Failed to install agent-runtime dependencies
    cd ..\..
    pause
    exit /b 1
)
cd ..\..

echo.
echo ========================================
echo Setup Complete!
echo ========================================
echo.
echo Next steps:
echo 1. Run validation: node scripts\validate-dependency-rules.js
echo 2. Run validation: node scripts\validate-boundary-rules.js
echo 3. Build packages: npm run build
echo 4. Test agent runtime: cd apps\agent-runtime && npm start
echo.
pause