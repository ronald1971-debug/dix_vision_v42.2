@echo off
echo ========================================
echo FORCE CLEANUP OF DEVIN PROCESSES
echo ========================================
echo.
echo WARNING: This will kill ALL Devin processes.
echo You will need to restart Devin afterward.
echo.
pause

echo.
echo Killing all Devin processes...
taskkill /F /IM Devin.exe 2>nul
taskkill /F /IM devin.exe 2>nul

echo.
echo Waiting for processes to terminate...
timeout /t 3

echo.
echo Checking for remaining processes...
tasklist /FI "IMAGENAME eq Devin.exe" 2>nul
tasklist /FI "IMAGENAME eq devin.exe" 2>nul

echo.
echo ========================================
echo FORCE CLEANUP COMPLETE
echo ========================================
echo.
echo All Devin processes have been terminated.
echo Please restart the Devin IDE to continue.
echo.
pause