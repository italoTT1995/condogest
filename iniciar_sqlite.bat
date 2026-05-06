@echo off
title Condo Manager - Local SQLite
color 0B

echo ---------------------------------------------------
echo    INICIANDO O SISTEMA (BANCO LOCAL SQLITE)
echo ---------------------------------------------------
echo.

:: Forca o uso do SQLite local
set DATABASE_URL=sqlite:///condominio.db

call venv\Scripts\activate.bat
python run_prod.py

pause
