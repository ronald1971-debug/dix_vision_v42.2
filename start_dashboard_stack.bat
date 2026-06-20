@echo off
REM DIX VISION v42.2 - Complete Dashboard Stack Launcher
REM Starts all required services together: FastAPI Backend, React Dashboard

echo ========================================
echo 🚀 DIX VISION v42.2 Dashboard Stack
echo ========================================
echo.

cd c:\dix_vision_v42.2\containers\user_interfaces

echo 🔍 Checking if dashboard is already running...
netstat -ano | findstr :5175 >nul
if %errorlevel% == 0 (
    echo ⚠️  Dashboard appears to be running on port 5175
    echo    Stopping existing dashboard first...
    taskkill /F /IM node.exe >nul 2>&1
    timeout /t 2 >nul
)

echo ⚡ Starting FastAPI Backend on port 8000...
start "DIX Backend" cmd /k "cd /d c:\dix_vision_v42.2\containers\user_interfaces && set PYTHONPATH=c:\dix_vision_v42.2\containers\user_interfaces && python -m uvicorn ui.server:app --host 0.0.0.0 --port 8000 --reload"

echo ⏳ Waiting for backend to start...
timeout /t 5 >nul

echo 🎨 Starting React Dashboard on port 5173...
start "DIX Dashboard" cmd /k "cd /d c:\dix_vision_v42.2\containers\user_interfaces\dashboard2026 && npm run dev"

echo ⏳ Waiting for dashboard to start...
timeout /t 5 >nul

echo.
echo ========================================
echo 🎉 Dashboard Stack Started!
echo ========================================
echo 📊 Dashboard:  http://localhost:5173/dash2/
echo ⚡ Backend:    http://localhost:8000
echo ========================================
echo.
echo Backend and Dashboard are now running in separate windows.
echo Close those windows to stop the services.
echo.
pause
