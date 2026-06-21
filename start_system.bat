@echo off
title DIX VISION System Launcher
echo Starting DIX VISION System...
echo.

REM Start the backend server in a new window
start "DIX VISION Backend" /min cmd /c "c:/dix_vision_v42.2/launch_real_backend.bat"

REM Wait a moment for the server to start
timeout /t 3 /nobreak >nul

REM Open the web browser
echo Launching web interface...
start http://localhost:8000

echo.
echo DIX VISION System started!
echo Backend server running in background window.
echo Web interface opened in browser.
echo.
echo Press any key to close this window (server will continue running)...
pause >nul