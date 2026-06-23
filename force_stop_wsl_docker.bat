@echo off
echo ========================================
echo FORCE STOP WSL AND DOCKER
echo ========================================
echo.
echo Stopping Docker Desktop...
taskkill /F /IM "Docker Desktop.exe" 2>nul
taskkill /F /IM "com.docker.backend" 2>nul
taskkill /F /IM "com.docker.service" 2>nul

echo.
echo Stopping WSL...
wsl --shutdown

echo.
echo Stopping WSL Service...
net stop LxssManager 2>nul

echo.
echo Waiting for processes to terminate...
timeout /t 5

echo.
echo Checking remaining processes...
tasklist | findstr "vmmemWSL"
tasklist | findstr "wsl"

echo.
echo ========================================
echo FORCE STOP COMPLETE
echo ========================================
echo.
echo To restart normally:
echo 1. Start Docker Desktop
echo 2. Wait for WSL to initialize
echo.
pause