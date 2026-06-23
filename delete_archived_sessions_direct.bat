@echo off
echo ========================================
echo DELETE ARCHIVED SESSIONS
echo ========================================
echo.
echo This will delete all archived session files.
echo.
pause

echo.
echo Deleting development checkpoint sessions...
del /q "containers\development\checkpoints\*.json"

if %errorlevel% equ 0 (
    echo SUCCESS: Development checkpoints deleted
) else (
    echo WARNING: No development checkpoints found or error occurred
)

echo.
echo Deleting IDE global storage sessions...
if exist "C:\Users\prive\AppData\Roaming\Code\User\globalStorage\*.json" (
    del /q "C:\Users\prive\AppData\Roaming\Code\User\globalStorage\*.json"
    echo SUCCESS: IDE global storage sessions deleted
) else (
    echo WARNING: No IDE global storage sessions found
)

echo.
echo Deleting system_core cache...
rmdir /s /q "containers\system_core\state\cache" 2>nul
echo System_core cache cleared

echo.
echo ========================================
echo SESSION DELETION COMPLETE
echo ========================================
echo.
echo All archived sessions have been deleted.
echo Restart the IDE and the OOM error should be resolved.
echo.
pause
