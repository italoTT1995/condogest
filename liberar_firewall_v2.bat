@echo off
cd /d "%~dp0"
powershell -NoProfile -ExecutionPolicy Bypass -File "configurar_firewall.ps1"
pause
