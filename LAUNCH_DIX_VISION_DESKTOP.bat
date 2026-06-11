@echo off
REM DIX VISION Desktop AgentOS Launcher
REM Launches the actual desktop application with backend

echo Starting DIX VISION Desktop AgentOS...
echo.

REM Change to project directory
cd /d "C:\dix_vision_v42.2"

REM Change to dix_desktop directory
cd dix_desktop

REM Launch Tauri desktop application
echo Launching DIX DESKTOP application...
call npm run tauri dev

pause