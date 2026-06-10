@echo off
REM DIX VISION Desktop AgentOS Launcher
REM Launches the actual desktop application with backend

echo Starting DIX VISION Desktop AgentOS...
echo.

REM Change to project directory
cd /d "C:\dix_vision_v42.2"

REM Start Python backend in background
echo Starting Python backend...
start /B python LAUNCH_DIX_VISION_DESKTOP.py >nul 2>&1

REM Wait a moment for backend to initialize
timeout /t 2 /nobreak >nul

REM Launch Tauri desktop application
echo Launching DIX DESKTOP application...
cd dix_desktop
call npm run tauri dev

pause