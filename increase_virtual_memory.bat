@echo off
echo ========================================
echo Virtual Memory Increase Script
echo ========================================
echo.
echo This script requires Administrator privileges
echo.
powershell -Command "Start-Process powershell -ArgumentList '-ExecutionPolicy Bypass -File \"%~dp0increase_virtual_memory_admin.ps1\"' -Verb RunAs"
