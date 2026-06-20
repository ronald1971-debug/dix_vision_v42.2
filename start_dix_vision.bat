@echo off
REM DIX VISION Dashboard2026 - Docker Unified Startup Script
REM Launches Python backend and React dashboard as Docker containers

echo ============================================================
echo DIX VISION Dashboard2026 - Docker Unified Startup
echo ============================================================
echo.

REM Change to project directory
cd /d C:\dix_vision_v42.2

REM Check if Docker is running
echo Checking Docker status...
docker ps >nul 2>&1
if errorlevel 1 (
    echo Error: Docker is not running. Please start Docker Desktop.
    pause
    exit /b 1
)

echo Docker is running.

REM Start Docker containers
echo ============================================================
echo Starting DIX VISION Docker Containers
echo ============================================================
echo.

echo Starting backend, dashboard, and support services...
docker-compose -f docker-compose.main.yml up -d

REM Wait for services to start
echo Waiting for services to initialize...
timeout /t 10 /nobreak

REM Check container status
echo ============================================================
echo Container Status
echo ============================================================
docker-compose -f docker-compose.main.yml ps

REM Wait a moment for backend to be healthy
echo Waiting for backend health check...
timeout /t 5 /nobreak

REM Test backend connection
echo ============================================================
echo Testing Backend Connection
echo ============================================================
curl -s http://localhost:8080/api/health 2>nul
if errorlevel 1 (
    echo Warning: Backend health check failed, checking container logs...
    docker logs dix-vision-backend --tail 20
    echo.
    echo The dashboard may still function with limited functionality.
) else (
    echo Backend health check passed.
)

echo ============================================================
echo DIX VISION Dashboard2026 - System Started
echo ============================================================
echo.
echo System Components:
echo - Python Backend: http://localhost:8080
echo - React Dashboard: http://localhost:5173
echo - API Documentation: http://localhost:8080/docs
echo - Redis: localhost:6379
echo - PostgreSQL: localhost:5432
echo.
echo Opening browser to the dashboard...
start "" "http://localhost:5173/"

echo.
echo Press any key to stop the system...
pause >nul

REM Stop Docker containers
echo.
echo ============================================================
echo Stopping DIX VISION Dashboard2026
echo ============================================================
docker-compose -f docker-compose.main.yml down

echo System stopped.
pause