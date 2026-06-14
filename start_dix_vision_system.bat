@echo off
REM DIX VISION v42.2+ Complete System Launcher
REM Starts Desktop Agent and Dashboard2026 Cognitive Control Center

echo DIX VISION v42.2+ Complete System Launcher
echo ========================================
echo.

cd /d "C:\dix_vision_v42.2"

echo [1/2] Starting Desktop Agent (Docker)...
docker compose up -d desktop-agent-service

echo Waiting for Desktop Agent to initialize...
ping 127.0.0.1 -n 10 > nul

echo [2/2] Starting Dashboard2026 dev server...
cd dashboard2026
start npm run dev

echo Waiting for Dashboard2026 to initialize...
ping 127.0.0.1 -n 8 > nul

echo Opening INDIRA Cognitive Center in browser...
start http://localhost:5173/dash2/#indira-cognitive-center

echo.
echo ========================================
echo DIX VISION v42.2+ Complete System Launcher
echo ========================================
echo Desktop Agent: Running (http://localhost:9186)
echo Dashboard2026: Running (http://localhost:5173)
echo Cognitive Center: http://localhost:5173/dash2/#indira-cognitive-center
echo ========================================
echo.
echo Complete system running in background.
echo To stop services, run: stop_dix_vision_system.bat
echo.
pause