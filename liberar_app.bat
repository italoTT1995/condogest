@echo off
cd /d "%~dp0"
powershell -NoProfile -ExecutionPolicy Bypass -File "liberar_python.ps1"
pause
