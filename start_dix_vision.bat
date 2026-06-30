@echo off
REM DIX VISION Dashboard2026 - Docker Unified Startup Script
REM This script now uses the unified service manager

echo ============================================================
echo DIX VISION Dashboard2026 - Service Manager
echo ============================================================
echo.

REM Change to project directory
cd /d C:\dix_vision_v42.2

REM Check if Python is available
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python is not available
    pause
    exit /b 1
)

REM Use service manager to start services
echo Starting DIX VISION services using service manager...
python -c "from service_manager import get_service_manager; sm = get_service_manager(); sm.start_all()"

if errorlevel 1 (
    echo ERROR: Service manager failed to start services
    pause
    exit /b 1
)

echo.
echo Services started successfully
echo Run 'python -c \"from service_manager import get_service_manager; print(get_service_manager().get_all_status())\"' to check status
echo.
echo Press any key to stop services...
pause >nul

REM Stop services through service manager
echo.
echo Stopping DIX VISION services...
python -c "from service_manager import get_service_manager; sm = get_service_manager(); sm.stop_all()"

echo Services stopped.
pause