@echo off
REM DIX VISION v42.2 - Real Backend Startup Script
REM Uses actual system dependencies as designed (no simplified stubs)

echo ========================================
echo 🚀 Starting DIX VISION Real Backend
echo ========================================
echo.

cd c:\dix_vision_v42.2\containers\user_interfaces

echo 🔧 Setting Python paths...
set PYTHONPATH=c:\dix_vision_v42.2\containers\infrastructure
set PYTHONPATH=%PYTHONPATH%;c:\dix_vision_v42.2\containers\system_core
set PYTHONPATH=%PYTHONPATH%;c:\dix_vision_v42.2\containers\user_interfaces
set PYTHONPATH=%PYTHONPATH%;c:\dix_vision_v42.2\containers\user_interfaces\dashboard_backend
set PYTHONPATH=%PYTHONPATH%;c:\dix_vision_v42.2\containers\system_core\evolution_engine
set PYTHONPATH=%PYTHONPATH%;c:\dix_vision_v42.2\containers\system_core\governance_unified
set PYTHONPATH=%PYTHONPATH%;c:\dix_vision_v42.2\containers\system_core\governance_unified\domains\cognitive
set PYTHONPATH=%PYTHONPATH%;c:\dix_vision_v42.2\containers\system_core\execution_unified
set PYTHONPATH=%PYTHONPATH%;c:\dix_vision_v42.2\containers\system_core\execution_unified\core
set PYTHONPATH=%PYTHONPATH%;c:\dix_vision_v42.2\containers\system_core\execution_unified\engine_archive
set PYTHONPATH=%PYTHONPATH%;c:\dix_vision_v42.2\containers\system_core\system
set PYTHONPATH=%PYTHONPATH%;c:\dix_vision_v42.2\containers\system_core\cognitive_control_center

echo 🔧 Setting locale to avoid Python 3.14 compatibility issues...
set LANG=en_US.UTF-8
set LC_ALL=en_US.UTF-8

echo ⚡ Starting FastAPI Backend on port 8000...
python -c "import sys; sys.path.insert(0, '.'); sys.path.insert(0, '..'); from ui.server import app; import uvicorn; uvicorn.run(app, host='0.0.0.0', port=8000, reload=True)"

echo.
echo ========================================
echo Backend stopped
echo ========================================