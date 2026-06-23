@echo off
echo ========================================
echo CLEANUP MULTIPLE DEVIN PROCESSES
echo ========================================
echo.
echo Found multiple Devin processes running.
echo These are likely zombie processes from previous sessions.
echo.
echo Current Devin processes:
tasklist /FI "IMAGENAME eq Devin.exe" /FO TABLE
echo.
tasklist /FI "IMAGENAME eq devin.exe" /FO TABLE
echo.

echo WARNING: This will kill all Devin processes except the main one.
echo The main Devin process is typically the one using the most memory.
echo.
pause

echo.
echo Killing zombie Devin processes...
taskkill /F /FI "IMAGENAME eq devin.exe" /FI "MEM lt 500000" 2>nul
taskkill /F /FI "IMAGENAME eq Devin.exe" /FI "MEM lt 500000" 2>nul

echo.
echo Checking remaining Devin processes...
tasklist /FI "IMAGENAME eq Devin.exe" /FO TABLE
echo.
tasklist /FI "IMAGENAME eq devin.exe" /FO TABLE
echo.

echo ========================================
echo PROCESS CLEANUP COMPLETE
echo ========================================
echo.
echo Zombie processes have been terminated.
echo The main Devin session should remain active.
echo Memory usage should be significantly reduced.
echo.
pause