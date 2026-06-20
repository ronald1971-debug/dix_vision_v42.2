@echo off
REM DIX VISION Dashboard2026 - Docker Connection Test Script (Windows)
REM Tests the Docker container setup and connections

echo =============================================================
echo DIX VISION Dashboard2026 - Docker Connection Test
echo =============================================================
echo.

REM Change to project directory
cd /d C:\dix_vision_v42.2

REM Test Docker status
echo Testing Docker status...
docker ps >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Docker is not running. Please start Docker Desktop.
    pause
    exit /b 1
)
echo [OK] Docker is running

REM Test backend container
echo.
echo Testing backend container...
docker ps | findstr "dix-vision-backend" >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Backend container is not running
    echo Run: docker-compose -f docker-compose.main.yml up -d
    pause
    exit /b 1
)
echo [OK] Backend container is running

REM Test dashboard container
echo.
echo Testing dashboard container...
docker ps | findstr "dix-vision-dashboard" >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Dashboard container is not running
    echo Run: docker-compose -f docker-compose.main.yml up -d
    pause
    exit /b 1
)
echo [OK] Dashboard container is running

REM Test backend health
echo.
echo Testing backend health endpoint...
curl -s -o nul -w "%%{http_code}" http://localhost:8080/api/health >nul 2>&1
if errorlevel 1 (
    echo [WARNING] Backend health check failed, checking logs...
    docker logs dix-vision-backend --tail 20
    echo The system may still function with limited functionality.
) else (
    echo [OK] Backend health endpoint responding
    curl -s http://localhost:8080/api/health
)

REM Test dashboard accessibility
echo.
echo Testing dashboard accessibility...
curl -s -o nul -w "%%{http_code}" http://localhost:5173 >nul 2>&1
if errorlevel 1 (
    echo [WARNING] Dashboard endpoint test failed (may be normal for React dev server)
) else (
    echo [OK] Dashboard is accessible
)

REM Test container networking
echo.
echo Testing container networking...
docker exec dix-vision-dashboard ping -n 1 dix-vision-backend >nul 2>&1
if errorlevel 1 (
    echo [WARNING] Container networking test failed (may not be critical)
) else (
    echo [OK] Container networking working
)

REM Test Redis (optional)
echo.
echo Testing Redis connection...
docker ps | findstr "dix-redis-service" >nul 2>&1
if errorlevel 1 (
    echo [INFO] Redis container not running (optional)
) else (
    docker exec dix-redis-service redis-cli ping >nul 2>&1
    if errorlevel 1 (
        echo [ERROR] Redis is not responding
    ) else (
        echo [OK] Redis is responding
    )
)

REM Test PostgreSQL (optional)
echo.
echo Testing PostgreSQL connection...
docker ps | findstr "dix-postgresql-service" >nul 2>&1
if errorlevel 1 (
    echo [INFO] PostgreSQL container not running (optional)
) else (
    docker exec dix-postgresql-service pg_isready -U dixvision >nul 2>&1
    if errorlevel 1 (
        echo [ERROR] PostgreSQL is not responding
    ) else (
        echo [OK] PostgreSQL is responding
    )
)

echo =============================================================
echo Docker Connection Test Complete
echo =============================================================
echo.
echo Access Points:
echo - React Dashboard: http://localhost:5173
echo - Python Backend: http://localhost:8080
echo - API Documentation: http://localhost:8080/docs
echo - Redis: localhost:6379
echo - PostgreSQL: localhost:5432
echo.
echo To view logs:
echo - Backend: docker logs dix-vision-backend
echo - Dashboard: docker logs dix-vision-dashboard
echo.
echo To stop the system:
echo - docker-compose -f docker-compose.main.yml down
echo.
pause