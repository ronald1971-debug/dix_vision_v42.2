@echo off
REM DIX VISION v42.2 - Complete Dashboard Stack Launcher
REM Simple launcher for backend + frontend

echo ========================================
echo 🚀 DIX VISION v42.2 Complete Stack
echo ========================================
echo.

cd c:\dix_vision_v42.2\containers\user_interfaces

echo ⚡ Starting FastAPI Backend on port 8000...
start "DIX Backend" cmd /k "cd /d c:\dix_vision_v42.2\containers\user_interfaces && set PYTHONPATH=c:\dix_vision_v42.2\containers\user_interfaces && python -m uvicorn ui.server:app --host 0.0.0.0 --port 8000 --reload"

timeout /t 3

echo 🎨 Starting React Dashboard on port 5173...
cd c:\dix_vision_v42.2\containers\user_interfaces\dashboard2026
start "DIX Dashboard" cmd /k "cd /d c:\dix_vision_v42.2\containers\user_interfaces\dashboard2026 && npm run dev"

timeout /t 3

echo.
echo ========================================
echo 🎉 Complete Stack Started!
echo ========================================
echo 📊 Dashboard:  http://localhost:5173/dash2/
echo ⚡ Backend:    http://localhost:8000
echo ========================================
echo.
echo Services are running in separate windows.
echo Close those windows to stop the services.
echo.
