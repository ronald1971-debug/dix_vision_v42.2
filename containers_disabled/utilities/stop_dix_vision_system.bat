@echo off
REM DIX VISION v42.2+ System Stop Script
REM Stops Desktop Agent and Dashboard2026

echo Stopping DIX VISION services...
cd /d "C:\dix_vision_v42.2"
docker compose down
echo Services stopped.
pause